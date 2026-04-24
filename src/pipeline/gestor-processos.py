#!/usr/bin/env python3
"""
Gestor de Processos Periciais — Sistema Unificado
Unifica processos do organizador e analisador numa estrutura padronizada.

Uso:
    python3 gestor-processos.py listar           # Lista todos com status
    python3 gestor-processos.py status           # Dashboard resumido
    python3 gestor-processos.py migrar           # Migra do organizador para cá
    python3 gestor-processos.py organizar        # Padroniza nomes e estrutura
    python3 gestor-processos.py ficha CNJ        # Mostra ficha de um processo
"""

import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent
ORGANIZADOR_DIR = Path.home() / "Desktop" / "organizador" / "processos"
PROCESSOS_DIR = BASE_DIR / "processos"

# Cores para terminal
class C:
    R = "\033[0m"    # Reset
    B = "\033[1m"    # Bold
    G = "\033[32m"   # Green
    Y = "\033[33m"   # Yellow
    RE = "\033[31m"  # Red
    CY = "\033[36m"  # Cyan
    DIM = "\033[2m"  # Dim


def abreviar_cidade(cidade):
    """Abrevia nomes de cidades longas."""
    abreviacoes = {
        "Governador Valadares": "Gov Valadares",
        "GV": "Gov Valadares",
        "Conselheiro Pena": "Cons Pena",
        "JF João Monlevade": "João Monlevade",
        "João Monlevade": "João Monlevade",
        "Bom Despacho": "Bom Despacho",
        "Ribeirão das Neves": "Rib Neves",
        "Santa Luzia": "Santa Luzia",
        "Uberlândia": "Uberlândia",
    }
    return abreviacoes.get(cidade, cidade)


def ler_ficha_md(caminho):
    """Lê FICHA.md do organizador e extrai dados."""
    texto = Path(caminho).read_text(encoding="utf-8")
    dados = {}

    # Título
    titulo = re.search(r"^# (.+)", texto, re.MULTILINE)
    if titulo:
        dados["titulo"] = titulo.group(1).strip()

    # Número CNJ
    m = re.search(r"\*\*Número:\*\*\s*(.+)", texto)
    if m:
        dados["numero_cnj"] = m.group(1).strip()

    # Comarca
    m = re.search(r"\*\*Comarca:\*\*\s*(.+)", texto)
    if m:
        dados["comarca"] = m.group(1).strip()

    # Vara
    m = re.search(r"\*\*Vara:\*\*\s*(.+)", texto)
    if m:
        dados["vara"] = m.group(1).strip()

    # Área
    m = re.search(r"\*\*Área:\*\*\s*(.+)", texto)
    if m:
        dados["area"] = m.group(1).strip()

    # Tipo
    m = re.search(r"\*\*Tipo:\*\*\s*(.+)", texto)
    if m:
        dados["tipo_pericia"] = m.group(1).strip()

    # Objeto
    m = re.search(r"## Objeto\n(.+?)(?:\n\n|\n##)", texto, re.DOTALL)
    if m:
        dados["objeto"] = m.group(1).strip()

    # Áreas Médicas
    areas = re.findall(r"- (.+)", texto.split("## Áreas Médicas")[-1].split("## Status")[0]) if "## Áreas Médicas" in texto else []
    dados["areas_medicas"] = [a.strip() for a in areas]

    # Status (checkboxes)
    status_items = re.findall(r"- \[([xX ])\] (.+)", texto)
    dados["checklist"] = {item.strip(): (mark.lower() == "x") for mark, item in status_items}

    # Número da perícia (do nome da pasta)
    m = re.search(r"pericia-(\d+)", str(caminho))
    if m:
        dados["numero_pericia_original"] = int(m.group(1))

    # Sufixo JF
    dados["justica_federal"] = "-jf" in str(caminho)

    return dados


def ler_ficha_json(caminho):
    """Lê FICHA.json se existir."""
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def criar_ficha_json(dados, numero_pericia):
    """Cria estrutura FICHA.json a partir dos dados extraídos."""
    comarca = dados.get("comarca", "Desconhecida")
    cidade = abreviar_cidade(comarca)

    return {
        "numero_cnj": dados.get("numero_cnj", ""),
        "numero_pericia": numero_pericia,
        "cidade": cidade,
        "comarca": comarca,
        "vara": dados.get("vara", ""),
        "tribunal": "TRF6" if dados.get("justica_federal") else "TJMG",
        "area": dados.get("area", ""),
        "tipo_pericia": dados.get("tipo_pericia", ""),
        "objeto": dados.get("objeto", ""),
        "areas_medicas": dados.get("areas_medicas", []),
        "data_nomeacao": "",
        "data_aceite": "",
        "status": determinar_status(dados.get("checklist", {})),
        "etapa_atual": determinar_etapa(dados.get("checklist", {})),
        "partes": {"autor": "", "reu": ""},
        "prazos": {"proximo": "", "tipo": ""},
        "honorarios": {"valor": 0, "status": "pendente"},
        "origem": "organizador",
        "pasta_original": dados.get("pasta_original", ""),
        "atualizado_em": datetime.now().isoformat()
    }


def determinar_status(checklist):
    """Determina status baseado no checklist."""
    if not checklist:
        return "novo"
    concluidos = sum(1 for v in checklist.values() if v)
    total = len(checklist)
    if concluidos == total:
        return "concluido"
    if concluidos > 0:
        return "em_andamento"
    return "pendente"


def determinar_etapa(checklist):
    """Determina etapa atual baseado no checklist."""
    etapas_ordem = [
        "Aceite de nomeação",
        "Proposta de honorários",
        "Agendamento da perícia",
        "Análise dos autos",
        "Laudo pericial"
    ]
    for etapa in etapas_ordem:
        for key, done in checklist.items():
            if etapa.lower() in key.lower() and not done:
                return etapa
    return "concluído" if all(checklist.values()) else "aceite"


def coletar_todos_processos():
    """Coleta processos de ambas as fontes."""
    processos = {}

    # 1. Organizador (FICHA.md)
    if ORGANIZADOR_DIR.exists():
        for pasta in sorted(ORGANIZADOR_DIR.iterdir()):
            ficha_path = pasta / "FICHA.md"
            if ficha_path.exists():
                dados = ler_ficha_md(ficha_path)
                cnj = dados.get("numero_cnj", "")
                if cnj:
                    dados["pasta_original"] = str(pasta)
                    dados["fonte"] = "organizador"
                    processos[cnj] = dados

    # 2. Analisador (pastas CNJ existentes)
    for pasta in sorted(BASE_DIR.iterdir()):
        if pasta.is_dir() and re.match(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", pasta.name):
            cnj = pasta.name
            if cnj in processos:
                # Já veio do organizador — mesclar dados
                processos[cnj]["pasta_analisador"] = str(pasta)
                processos[cnj]["tem_pdf"] = any(pasta.glob("*.pdf"))
                processos[cnj]["tem_texto"] = (pasta / "TEXTO-EXTRAIDO.txt").exists()
                processos[cnj]["tem_analise"] = (pasta / "ANALISE.md").exists()
            else:
                # Só existe no analisador
                processos[cnj] = {
                    "numero_cnj": cnj,
                    "fonte": "analisador",
                    "pasta_analisador": str(pasta),
                    "tem_pdf": any(pasta.glob("*.pdf")),
                    "tem_texto": (pasta / "TEXTO-EXTRAIDO.txt").exists(),
                    "tem_analise": (pasta / "ANALISE.md").exists(),
                    "comarca": "",
                    "vara": "",
                    "area": "",
                }

    # 3. Processos já organizados (pasta processos/)
    if PROCESSOS_DIR.exists():
        for pasta in sorted(PROCESSOS_DIR.iterdir()):
            ficha_json = pasta / "FICHA.json"
            if ficha_json.exists():
                dados = ler_ficha_json(ficha_json)
                if dados:
                    cnj = dados.get("numero_cnj", "")
                    if cnj and cnj not in processos:
                        dados["fonte"] = "processos"
                        processos[cnj] = dados

    return processos


def cmd_listar():
    """Lista todos os processos com detalhes."""
    processos = coletar_todos_processos()

    print(f"\n{C.B}{'='*80}{C.R}")
    print(f"{C.B}  PROCESSOS PERICIAIS — {len(processos)} processos{C.R}")
    print(f"{C.B}{'='*80}{C.R}\n")

    # Ordenar por número da perícia (se tiver) ou CNJ
    items = sorted(processos.items(), key=lambda x: x[1].get("numero_pericia_original", 99))

    for i, (cnj, dados) in enumerate(items, 1):
        num_orig = dados.get("numero_pericia_original", "?")
        comarca = abreviar_cidade(dados.get("comarca", "?"))
        vara = dados.get("vara", "?")
        area = dados.get("area", "?")
        fonte = dados.get("fonte", "?")
        jf = " (JF)" if dados.get("justica_federal") else ""

        # Status visual
        status = dados.get("status", determinar_status(dados.get("checklist", {})))
        status_icon = {"concluido": f"{C.G}OK{C.R}", "em_andamento": f"{C.Y}>>>{C.R}", "pendente": f"{C.RE}---{C.R}", "novo": f"{C.CY}NEW{C.R}"}.get(status, "?")

        # Arquivos
        tem_pdf = "PDF" if dados.get("tem_pdf") else ""
        tem_txt = "TXT" if dados.get("tem_texto") else ""
        tem_ana = "ANA" if dados.get("tem_analise") else ""
        arquivos = " ".join(filter(None, [tem_pdf, tem_txt, tem_ana]))

        print(f"  {C.B}{num_orig:>3}{C.R}{jf:<4} {C.CY}{cnj}{C.R}")
        print(f"       {comarca} — {vara} | {area}")
        print(f"       [{status_icon}] Fonte: {fonte} {C.DIM}{arquivos}{C.R}")
        print()

    # Resumo
    por_fonte = {}
    for d in processos.values():
        f = d.get("fonte", "?")
        por_fonte[f] = por_fonte.get(f, 0) + 1

    print(f"{C.B}{'─'*80}{C.R}")
    print(f"  Total: {C.B}{len(processos)}{C.R} processos")
    for fonte, count in por_fonte.items():
        print(f"  — {fonte}: {count}")
    print()


def cmd_status():
    """Dashboard resumido."""
    processos = coletar_todos_processos()

    print(f"\n{C.B}  DASHBOARD — PERÍCIAS{C.R}")
    print(f"{'─'*50}")

    # Contadores
    total = len(processos)
    com_ficha = sum(1 for d in processos.values() if d.get("fonte") == "organizador")
    com_pdf = sum(1 for d in processos.values() if d.get("tem_pdf"))
    com_texto = sum(1 for d in processos.values() if d.get("tem_texto"))
    com_analise = sum(1 for d in processos.values() if d.get("tem_analise"))
    so_analisador = sum(1 for d in processos.values() if d.get("fonte") == "analisador")

    print(f"  Total de processos:    {C.B}{total}{C.R}")
    print(f"  Com ficha (organizador): {com_ficha}")
    print(f"  Só no analisador:      {so_analisador}")
    print(f"  Com PDF:               {com_pdf}")
    print(f"  Com texto extraído:    {com_texto}")
    print(f"  Com análise:           {com_analise}")
    print()

    # Por área
    areas = {}
    for d in processos.values():
        a = d.get("area", "Sem área")
        areas[a] = areas.get(a, 0) + 1

    print(f"  {C.B}Por área:{C.R}")
    for area, count in sorted(areas.items(), key=lambda x: -x[1]):
        print(f"    {count:>2}× {area}")
    print()

    # Por comarca
    comarcas = {}
    for d in processos.values():
        c = abreviar_cidade(d.get("comarca", "?"))
        comarcas[c] = comarcas.get(c, 0) + 1

    print(f"  {C.B}Por comarca:{C.R}")
    for com, count in sorted(comarcas.items(), key=lambda x: -x[1]):
        print(f"    {count:>2}× {com}")
    print()


def cmd_migrar():
    """Migra processos do organizador para a pasta processos/ no analisador."""
    processos = coletar_todos_processos()
    PROCESSOS_DIR.mkdir(exist_ok=True)

    migrados = 0
    erros = 0

    for cnj, dados in sorted(processos.items()):
        if dados.get("fonte") != "organizador":
            continue

        num_orig = dados.get("numero_pericia_original", 0)
        comarca = abreviar_cidade(dados.get("comarca", "Desconhecida"))
        vara = dados.get("vara", "Vara")

        # Nome padronizado
        jf = " JF" if dados.get("justica_federal") else ""
        nome_pasta = f"Perícia {num_orig:02d} - {comarca} - {vara}{jf}"

        destino = PROCESSOS_DIR / nome_pasta

        if destino.exists():
            print(f"  {C.Y}EXISTE{C.R} {nome_pasta}")
            continue

        try:
            destino.mkdir(parents=True)

            # Criar FICHA.json
            ficha = criar_ficha_json(dados, num_orig)
            (destino / "FICHA.json").write_text(
                json.dumps(ficha, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            # Copiar FICHA.md original
            pasta_orig = dados.get("pasta_original", "")
            if pasta_orig:
                ficha_md_orig = Path(pasta_orig) / "FICHA.md"
                if ficha_md_orig.exists():
                    shutil.copy2(ficha_md_orig, destino / "FICHA.md")

            # Se tem pasta no analisador, copiar PDFs e textos
            pasta_anal = dados.get("pasta_analisador", "")
            if pasta_anal:
                pasta_anal = Path(pasta_anal)
                for arq in pasta_anal.iterdir():
                    if arq.is_file():
                        shutil.copy2(arq, destino / arq.name)

            # Criar subpastas
            (destino / "petições").mkdir(exist_ok=True)
            (destino / "verificações").mkdir(exist_ok=True)
            (destino / "anexos").mkdir(exist_ok=True)

            # Criar link simbólico com CNJ
            link_cnj = PROCESSOS_DIR / cnj
            if not link_cnj.exists():
                link_cnj.symlink_to(destino.name)

            migrados += 1
            print(f"  {C.G}OK{C.R} {nome_pasta} ({cnj})")

        except Exception as e:
            erros += 1
            print(f"  {C.RE}ERRO{C.R} {cnj}: {e}")

    # Migrar processos que só existem no analisador (sem FICHA.md)
    for cnj, dados in sorted(processos.items()):
        if dados.get("fonte") != "analisador":
            continue

        nome_pasta = f"Perícia ?? - Desconhecida - {cnj}"
        destino = PROCESSOS_DIR / nome_pasta

        if destino.exists():
            print(f"  {C.Y}EXISTE{C.R} {nome_pasta}")
            continue

        try:
            destino.mkdir(parents=True)

            ficha = {
                "numero_cnj": cnj,
                "numero_pericia": 0,
                "cidade": "",
                "comarca": "",
                "vara": "",
                "tribunal": "TJMG",
                "area": "",
                "tipo_pericia": "",
                "status": "novo",
                "etapa_atual": "identificar",
                "partes": {"autor": "", "reu": ""},
                "prazos": {"proximo": "", "tipo": ""},
                "honorarios": {"valor": 0, "status": "pendente"},
                "origem": "analisador",
                "pasta_analisador": str(dados.get("pasta_analisador", "")),
                "atualizado_em": datetime.now().isoformat()
            }

            (destino / "FICHA.json").write_text(
                json.dumps(ficha, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            # Copiar arquivos do analisador
            pasta_anal = dados.get("pasta_analisador", "")
            if pasta_anal:
                for arq in Path(pasta_anal).iterdir():
                    if arq.is_file():
                        shutil.copy2(arq, destino / arq.name)

            (destino / "petições").mkdir(exist_ok=True)
            (destino / "verificações").mkdir(exist_ok=True)
            (destino / "anexos").mkdir(exist_ok=True)

            link_cnj = PROCESSOS_DIR / cnj
            if not link_cnj.exists():
                link_cnj.symlink_to(destino.name)

            migrados += 1
            print(f"  {C.G}OK{C.R} {nome_pasta} (só analisador)")

        except Exception as e:
            erros += 1
            print(f"  {C.RE}ERRO{C.R} {cnj}: {e}")

    print(f"\n  {C.B}Migrados: {migrados} | Erros: {erros}{C.R}\n")


def cmd_organizar(confirmar=False):
    """Verifica e padroniza a estrutura de todas as pastas em processos/.
    Com --confirmar, renomeia de verdade. Sem, apenas lista."""
    if not PROCESSOS_DIR.exists():
        print(f"  {C.RE}Pasta processos/ não existe. Rode 'migrar' primeiro.{C.R}")
        return

    ajustados = 0
    renomeados = 0
    pendentes_renomear = []
    for pasta in sorted(PROCESSOS_DIR.iterdir()):
        if not pasta.is_dir() or pasta.is_symlink():
            continue

        ficha_json = pasta / "FICHA.json"
        if not ficha_json.exists():
            print(f"  {C.Y}SEM FICHA{C.R} {pasta.name}")
            continue

        # Garantir subpastas
        for sub in ["petições", "verificações", "anexos"]:
            (pasta / sub).mkdir(exist_ok=True)

        # Verificar se nome está padronizado
        ficha = ler_ficha_json(ficha_json)
        if ficha:
            num = ficha.get("numero_pericia", 0)
            cidade = abreviar_cidade(ficha.get("cidade", "?"))
            vara = ficha.get("vara", "?")
            tribunal = ficha.get("tribunal", "")
            jf = " JF" if tribunal.startswith("TRF") else ""
            nome_esperado = f"Perícia {num:02d} - {cidade} - {vara}{jf}"

            if pasta.name != nome_esperado and num > 0:
                print(f"  {C.Y}RENOMEAR{C.R} {pasta.name}")
                print(f"       → {nome_esperado}")
                ajustados += 1

                if confirmar:
                    pendentes_renomear.append((pasta, nome_esperado, ficha))

    # Renomeação em 2 fases para evitar conflitos
    if confirmar and pendentes_renomear:
        print(f"\n  Renomeando em 2 fases ({len(pendentes_renomear)} pastas)...")

        # Fase 1: renomear para nomes temporários
        temp_map = []
        for pasta, nome_final, ficha in pendentes_renomear:
            cnj = ficha.get("numero_cnj", "")
            temp_nome = f"_TEMP_{cnj or pasta.name}"
            temp_dest = PROCESSOS_DIR / temp_nome
            try:
                if cnj:
                    link = PROCESSOS_DIR / cnj
                    if link.is_symlink():
                        link.unlink()
                pasta.rename(temp_dest)
                temp_map.append((temp_dest, nome_final, cnj))
            except Exception as e:
                print(f"  {C.RE}ERRO fase 1{C.R} {pasta.name}: {e}")

        # Fase 2: renomear de temporário para final
        for temp_dest, nome_final, cnj in temp_map:
            destino = PROCESSOS_DIR / nome_final
            try:
                if destino.exists():
                    print(f"  {C.RE}CONFLITO{C.R} {nome_final} já existe")
                    continue
                temp_dest.rename(destino)
                if cnj:
                    link = PROCESSOS_DIR / cnj
                    if not link.exists():
                        link.symlink_to(nome_final)
                renomeados += 1
                print(f"  {C.G}FEITO{C.R} {nome_final}")
            except Exception as e:
                print(f"  {C.RE}ERRO fase 2{C.R} {nome_final}: {e}")

    if ajustados == 0:
        print(f"  {C.G}Tudo organizado.{C.R}")
    elif not confirmar:
        print(f"\n  {ajustados} pastas precisam de renomeação.")
        print(f"  Use: python3 gestor-processos.py organizar --confirmar")
    else:
        print(f"\n  {renomeados}/{ajustados} pastas renomeadas.")


def cmd_ficha(cnj):
    """Mostra ficha de um processo específico."""
    processos = coletar_todos_processos()

    # Busca por CNJ parcial
    matches = [(k, v) for k, v in processos.items() if cnj in k]

    if not matches:
        print(f"  {C.RE}Processo não encontrado: {cnj}{C.R}")
        return

    if len(matches) > 1:
        print(f"  Múltiplos resultados:")
        for k, _ in matches:
            print(f"    {k}")
        return

    cnj_full, dados = matches[0]
    print(f"\n{C.B}  FICHA — {cnj_full}{C.R}")
    print(f"{'─'*60}")

    campos = [
        ("Comarca", "comarca"), ("Vara", "vara"), ("Área", "area"),
        ("Tipo", "tipo_pericia"), ("Objeto", "objeto"),
        ("Fonte", "fonte"),
    ]
    for label, key in campos:
        val = dados.get(key, "")
        if val:
            print(f"  {label}: {val}")

    areas_med = dados.get("areas_medicas", [])
    if areas_med:
        print(f"  Áreas médicas: {', '.join(areas_med)}")

    checklist = dados.get("checklist", {})
    if checklist:
        print(f"\n  {C.B}Checklist:{C.R}")
        for item, done in checklist.items():
            icon = f"{C.G}[x]{C.R}" if done else f"{C.RE}[ ]{C.R}"
            print(f"    {icon} {item}")

    print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()
    confirmar = "--confirmar" in sys.argv

    if cmd == "listar":
        cmd_listar()
    elif cmd == "status":
        cmd_status()
    elif cmd == "migrar":
        cmd_migrar()
    elif cmd == "organizar":
        cmd_organizar(confirmar=confirmar)
    elif cmd == "cronologia":
        # Roda o script de sequência cronológica
        import subprocess
        args_extra = ["--aplicar"] if confirmar else []
        subprocess.run([sys.executable, str(BASE_DIR / "sequencia_cronologica.py")] + args_extra)
    elif cmd == "ficha" and len(sys.argv) > 2:
        cmd_ficha(sys.argv[2])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
