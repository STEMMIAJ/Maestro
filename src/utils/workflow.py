#!/usr/bin/env python3
"""
Workflow de Perícia — Pipeline padronizado por processo.

Etapas do pipeline:
  1. nomeacao    — Nomeação recebida (triagem de complexidade)
  2. aceite      — Aceite + proposta de honorários
  3. analise     — Análise documental completa
  4. preparo     — Preparo do ato pericial (agendamento, quesitos)
  5. pericia     — Realização da perícia
  6. laudo       — Elaboração do laudo
  7. entrega     — Entrega e acompanhamento
  8. concluido   — Processo encerrado

Uso:
  python3 workflow.py status                  # Dashboard de todos os processos
  python3 workflow.py listar                  # Lista com etapa atual
  python3 workflow.py ver CNJ                 # Detalhes de um processo
  python3 workflow.py avancar CNJ             # Avança para próxima etapa
  python3 workflow.py avancar CNJ --etapa X   # Define etapa específica
  python3 workflow.py pendencias              # O que precisa de atenção
  python3 workflow.py dashboard               # Gera DASHBOARD.html com dados atuais
"""

import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
PROCESSOS_DIR = BASE_DIR / "processos"

# Cores
class C:
    R = "\033[0m"
    B = "\033[1m"
    G = "\033[32m"
    Y = "\033[33m"
    RE = "\033[31m"
    CY = "\033[36m"
    DIM = "\033[2m"
    MAG = "\033[35m"


# Pipeline de etapas
ETAPAS = [
    {
        "id": "nomeacao",
        "nome": "Nomeação Recebida",
        "descricao": "Triagem de complexidade, decisão aceitar/recusar",
        "checklist": [
            "Ler despacho/decisão de nomeação",
            "Identificar tipo de perícia",
            "Avaliar complexidade (50 fatores)",
            "Decidir: aceitar ou recusar",
        ],
    },
    {
        "id": "aceite",
        "nome": "Aceite + Proposta",
        "descricao": "Petição de aceite e proposta de honorários",
        "checklist": [
            "Gerar petição de aceite",
            "Calcular honorários (fórmula + tabela TJMG)",
            "Gerar proposta de honorários",
            "Protocolar no PJe",
        ],
    },
    {
        "id": "analise",
        "nome": "Análise Documental",
        "descricao": "Leitura completa dos autos, extração de dados",
        "checklist": [
            "Extrair texto do PDF (pdftotext)",
            "Verificar erros materiais (CIDs, datas, nomes)",
            "Identificar partes, advogados, assistentes",
            "Mapear documentos médicos anexados",
            "Gerar ANALISE.md",
        ],
    },
    {
        "id": "preparo",
        "nome": "Preparo do Ato Pericial",
        "descricao": "Agendamento, análise de quesitos, preparação",
        "checklist": [
            "Analisar quesitos das partes",
            "Identificar vícios nos quesitos",
            "Agendar perícia (petição + contato)",
            "Preparar roteiro de exame",
        ],
    },
    {
        "id": "pericia",
        "nome": "Realização da Perícia",
        "descricao": "Exame pericial presencial ou documental",
        "checklist": [
            "Realizar exame pericial",
            "Fotografar/documentar achados",
            "Registrar anamnese e exame físico",
            "Coletar documentos adicionais",
        ],
    },
    {
        "id": "laudo",
        "nome": "Elaboração do Laudo",
        "descricao": "Redação, revisão e formatação do laudo",
        "checklist": [
            "Redigir laudo (usar template por tipo)",
            "Responder todos os quesitos",
            "Revisar (checklist de qualidade)",
            "Formatar e gerar PDF final",
        ],
    },
    {
        "id": "entrega",
        "nome": "Entrega",
        "descricao": "Upload no PJe e acompanhamento",
        "checklist": [
            "Upload do laudo no PJe",
            "Confirmar recebimento",
            "Aguardar manifestação das partes",
            "Responder esclarecimentos (se houver)",
        ],
    },
    {
        "id": "concluido",
        "nome": "Concluído",
        "descricao": "Processo encerrado",
        "checklist": [
            "Honorários recebidos",
            "Arquivo finalizado",
        ],
    },
]

ETAPA_IDS = [e["id"] for e in ETAPAS]


def carregar_processos():
    """Carrega todos os processos com FICHA.json."""
    processos = []
    if not PROCESSOS_DIR.exists():
        return processos

    for pasta in sorted(PROCESSOS_DIR.iterdir()):
        if not pasta.is_dir() or pasta.is_symlink():
            continue
        ficha_path = pasta / "FICHA.json"
        if not ficha_path.exists():
            continue
        try:
            ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
            ficha["_pasta"] = pasta
            ficha["_ficha_path"] = ficha_path
            processos.append(ficha)
        except (json.JSONDecodeError, OSError):
            continue

    return processos


def get_etapa_info(etapa_id):
    """Retorna info da etapa pelo ID."""
    for e in ETAPAS:
        if e["id"] == etapa_id:
            return e
    return None


def get_etapa_index(etapa_id):
    """Retorna índice da etapa (0-based)."""
    try:
        return ETAPA_IDS.index(etapa_id)
    except ValueError:
        return -1


def etapa_cor(etapa_id):
    """Retorna cor ANSI baseada na etapa."""
    cores = {
        "nomeacao": C.MAG,
        "aceite": C.Y,
        "analise": C.CY,
        "preparo": C.CY,
        "pericia": C.B,
        "laudo": C.B,
        "entrega": C.G,
        "concluido": C.DIM,
    }
    return cores.get(etapa_id, C.R)


def barra_progresso(etapa_id, largura=20):
    """Gera barra de progresso visual."""
    idx = get_etapa_index(etapa_id)
    if idx < 0:
        idx = 0
    total = len(ETAPAS) - 1  # concluído = 100%
    preenchido = int((idx / total) * largura) if total > 0 else 0
    barra = "█" * preenchido + "░" * (largura - preenchido)
    pct = int((idx / total) * 100) if total > 0 else 0
    return f"[{barra}] {pct}%"


# ============================================================
# COMANDOS
# ============================================================

def cmd_status():
    """Dashboard resumido de todos os processos."""
    processos = carregar_processos()

    if not processos:
        print(f"\n  {C.DIM}Nenhum processo encontrado.{C.R}\n")
        return

    # Contar por etapa
    contagem = {}
    for e in ETAPAS:
        contagem[e["id"]] = 0

    for p in processos:
        etapa = p.get("etapa_atual_id", "nomeacao")
        if etapa not in contagem:
            etapa = "nomeacao"
        contagem[etapa] += 1

    total = len(processos)
    ativos = total - contagem.get("concluido", 0)

    print(f"\n{C.B}  WORKFLOW DE PERÍCIAS — {total} processos ({ativos} ativos){C.R}")
    print(f"{'─' * 65}")

    for e in ETAPAS:
        n = contagem[e["id"]]
        if n == 0:
            indicador = f"{C.DIM}  0{C.R}"
        else:
            cor = etapa_cor(e["id"])
            indicador = f"{cor}{C.B}{n:>3}{C.R}"

        barra = ""
        if n > 0:
            barra = " " + "●" * min(n, 20)

        print(f"  {indicador}  {e['nome']:<28}{C.DIM}{barra}{C.R}")

    print(f"{'─' * 65}")

    # Processos que precisam de ação (não concluídos)
    pendentes = [p for p in processos if p.get("etapa_atual_id", "nomeacao") != "concluido"]
    if pendentes:
        print(f"\n{C.B}  PRÓXIMAS AÇÕES{C.R}")
        print(f"{'─' * 65}")

        # Ordenar por etapa (mais avançados primeiro)
        pendentes.sort(key=lambda p: get_etapa_index(p.get("etapa_atual_id", "nomeacao")), reverse=True)

        for p in pendentes[:10]:  # Top 10
            etapa_id = p.get("etapa_atual_id", "nomeacao")
            etapa = get_etapa_info(etapa_id)
            cor = etapa_cor(etapa_id)
            num = p.get("numero_pericia", "?")
            cidade = p.get("cidade", "?")
            nome_etapa = etapa["nome"] if etapa else etapa_id

            print(f"  {cor}● {nome_etapa:<22}{C.R}  Perícia {num} — {cidade}")

        if len(pendentes) > 10:
            print(f"  {C.DIM}... e mais {len(pendentes) - 10} processos{C.R}")

    print()


def cmd_listar():
    """Lista todos os processos com etapa atual e progresso."""
    processos = carregar_processos()

    if not processos:
        print(f"\n  {C.DIM}Nenhum processo encontrado.{C.R}\n")
        return

    print(f"\n{C.B}  PROCESSOS — PIPELINE{C.R}")
    print(f"{'─' * 80}")
    print(f"  {'Perícia':<12} {'Cidade':<20} {'Etapa':<24} {'Progresso'}")
    print(f"{'─' * 80}")

    for p in processos:
        num = p.get("numero_pericia", "?")
        cidade = p.get("cidade", "?")[:18]
        etapa_id = p.get("etapa_atual_id", "nomeacao")
        etapa = get_etapa_info(etapa_id)
        cor = etapa_cor(etapa_id)
        nome_etapa = etapa["nome"] if etapa else etapa_id
        barra = barra_progresso(etapa_id, 15)

        print(f"  {C.B}{str(num):>4}{C.R}        {cidade:<20} {cor}{nome_etapa:<24}{C.R} {barra}")

    print(f"{'─' * 80}")
    print()


def cmd_ver(cnj_ou_num):
    """Mostra detalhes de um processo específico."""
    processos = carregar_processos()

    # Buscar por CNJ ou número de perícia
    encontrado = None
    for p in processos:
        if str(cnj_ou_num) in str(p.get("numero_cnj", "")):
            encontrado = p
            break
        if str(cnj_ou_num) == str(p.get("numero_pericia", "")):
            encontrado = p
            break

    if not encontrado:
        print(f"\n  {C.RE}Processo não encontrado: {cnj_ou_num}{C.R}\n")
        return

    p = encontrado
    etapa_id = p.get("etapa_atual_id", "nomeacao")
    etapa = get_etapa_info(etapa_id)
    idx = get_etapa_index(etapa_id)

    print(f"\n{C.B}  PERÍCIA {p.get('numero_pericia', '?')} — {p.get('cidade', '?')} — {p.get('vara', '?')}{C.R}")
    print(f"{'─' * 65}")
    print(f"  CNJ: {p.get('numero_cnj', '?')}")
    print(f"  Tipo: {p.get('tipo_pericia', '?')}")
    print(f"  Área: {p.get('area', '?')}")
    print(f"  Status: {p.get('status', '?')}")
    print(f"  Progresso: {barra_progresso(etapa_id, 25)}")
    print()

    # Mostrar pipeline visual
    print(f"  {C.B}PIPELINE:{C.R}")
    for i, e in enumerate(ETAPAS):
        if i < idx:
            marca = f"{C.G}✓{C.R}"
        elif i == idx:
            marca = f"{C.Y}▶{C.R}"
        else:
            marca = f"{C.DIM}○{C.R}"

        nome = e["nome"]
        if i == idx:
            nome = f"{C.B}{nome}{C.R}"
        elif i < idx:
            nome = f"{C.DIM}{nome}{C.R}"

        print(f"    {marca} {i + 1}. {nome}")

    # Checklist da etapa atual
    if etapa:
        print(f"\n  {C.B}CHECKLIST — {etapa['nome']}:{C.R}")
        for item in etapa["checklist"]:
            print(f"    □ {item}")

    # Datas relevantes
    datas = []
    for campo in ["data_nomeacao", "data_aceite", "data_pericia", "data_prazo_laudo"]:
        val = p.get(campo, "")
        if val:
            label = campo.replace("data_", "").replace("_", " ").title()
            datas.append((label, val))

    if datas:
        print(f"\n  {C.B}DATAS:{C.R}")
        for label, val in datas:
            print(f"    {label}: {val}")

    print()


def cmd_avancar(cnj_ou_num, etapa_alvo=None):
    """Avança um processo para a próxima etapa (ou etapa específica)."""
    processos = carregar_processos()

    encontrado = None
    for p in processos:
        if str(cnj_ou_num) in str(p.get("numero_cnj", "")):
            encontrado = p
            break
        if str(cnj_ou_num) == str(p.get("numero_pericia", "")):
            encontrado = p
            break

    if not encontrado:
        print(f"\n  {C.RE}Processo não encontrado: {cnj_ou_num}{C.R}\n")
        return

    etapa_atual = encontrado.get("etapa_atual_id", "nomeacao")
    idx_atual = get_etapa_index(etapa_atual)

    if etapa_alvo:
        if etapa_alvo not in ETAPA_IDS:
            print(f"\n  {C.RE}Etapa inválida: {etapa_alvo}{C.R}")
            print(f"  Etapas válidas: {', '.join(ETAPA_IDS)}\n")
            return
        nova_etapa = etapa_alvo
    else:
        if idx_atual >= len(ETAPAS) - 1:
            print(f"\n  {C.DIM}Processo já está concluído.{C.R}\n")
            return
        nova_etapa = ETAPA_IDS[idx_atual + 1]

    # Atualizar FICHA.json
    encontrado["etapa_atual_id"] = nova_etapa
    etapa_info = get_etapa_info(nova_etapa)
    encontrado["etapa_atual"] = etapa_info["nome"] if etapa_info else nova_etapa
    encontrado["atualizado_em"] = datetime.now().isoformat()

    # Salvar
    ficha_path = encontrado["_ficha_path"]
    dados = {k: v for k, v in encontrado.items() if not k.startswith("_")}
    ficha_path.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    etapa_anterior = get_etapa_info(etapa_atual)
    nome_anterior = etapa_anterior["nome"] if etapa_anterior else etapa_atual
    nome_nova = etapa_info["nome"] if etapa_info else nova_etapa

    print(f"\n  {C.G}✓{C.R} Perícia {encontrado.get('numero_pericia', '?')}: {nome_anterior} → {C.B}{nome_nova}{C.R}")
    print(f"  {barra_progresso(nova_etapa, 25)}\n")


def cmd_pendencias():
    """Mostra processos que precisam de atenção imediata."""
    processos = carregar_processos()

    if not processos:
        print(f"\n  {C.DIM}Nenhum processo encontrado.{C.R}\n")
        return

    # Filtrar não-concluídos
    ativos = [p for p in processos if p.get("etapa_atual_id", "nomeacao") != "concluido"]

    if not ativos:
        print(f"\n  {C.G}Todos os processos estão concluídos!{C.R}\n")
        return

    print(f"\n{C.B}  PENDÊNCIAS — {len(ativos)} processos ativos{C.R}")
    print(f"{'─' * 65}")

    # Agrupar por etapa
    por_etapa = {}
    for p in ativos:
        etapa = p.get("etapa_atual_id", "nomeacao")
        if etapa not in por_etapa:
            por_etapa[etapa] = []
        por_etapa[etapa].append(p)

    for etapa_id in ETAPA_IDS:
        if etapa_id not in por_etapa:
            continue

        etapa = get_etapa_info(etapa_id)
        cor = etapa_cor(etapa_id)
        procs = por_etapa[etapa_id]

        print(f"\n  {cor}{C.B}{etapa['nome']}{C.R} ({len(procs)} processos)")

        for p in procs:
            num = p.get("numero_pericia", "?")
            cidade = p.get("cidade", "?")
            tipo = p.get("tipo_pericia", "")[:30]
            print(f"    Perícia {num} — {cidade} — {tipo}")

        # Mostrar próxima ação
        if etapa and etapa["checklist"]:
            print(f"    {C.DIM}→ Próximo: {etapa['checklist'][0]}{C.R}")

    print()


# ============================================================
# INICIALIZAÇÃO: Garantir que todas as FICHAs têm etapa_atual_id
# ============================================================

def cmd_dashboard():
    """Gera DASHBOARD.html com dados atualizados dos processos."""
    processos = carregar_processos()
    dashboard_path = BASE_DIR / "DASHBOARD.html"

    if not dashboard_path.exists():
        print(f"  {C.RE}DASHBOARD.html não encontrado em {BASE_DIR}{C.R}")
        return

    # Preparar dados para o JSON
    dados = []
    for p in processos:
        pasta = p.get("_pasta")
        tem_pdf = False
        if pasta:
            tem_pdf = any(pasta.glob("autos-completos*.pdf")) or (pasta / "PROCESSO-ORIGINAL.pdf").exists()

        dados.append({
            "numero_pericia": p.get("numero_pericia", "?"),
            "numero_cnj": p.get("numero_cnj", ""),
            "cidade": p.get("cidade", "?"),
            "vara": p.get("vara", ""),
            "comarca": p.get("comarca", ""),
            "area": p.get("area", ""),
            "tipo_pericia": p.get("tipo_pericia", ""),
            "status": p.get("status", ""),
            "etapa_atual_id": p.get("etapa_atual_id", "nomeacao"),
            "etapa_atual": p.get("etapa_atual", ""),
            "data_nomeacao": p.get("data_nomeacao", ""),
            "data_aceite": p.get("data_aceite", ""),
            "data_prazo_laudo": p.get("data_prazo_laudo", ""),
            "tem_pdf": tem_pdf,
        })

    json_str = json.dumps(dados, ensure_ascii=False, indent=2)

    # Ler HTML e substituir o bloco de dados
    html = dashboard_path.read_text(encoding="utf-8")
    marcador = '<script id="dados-json" type="application/json">'
    fim_marcador = '</script>'

    idx_inicio = html.find(marcador)
    if idx_inicio < 0:
        print(f"  {C.RE}Marcador de dados não encontrado no DASHBOARD.html{C.R}")
        return

    idx_inicio += len(marcador)
    idx_fim = html.find(fim_marcador, idx_inicio)

    novo_html = html[:idx_inicio] + json_str + html[idx_fim:]
    dashboard_path.write_text(novo_html, encoding="utf-8")

    print(f"  {C.G}✓{C.R} DASHBOARD.html atualizado com {len(dados)} processos")
    print(f"  Abrir: open \"{dashboard_path}\"\n")


def garantir_etapas():
    """Adiciona etapa_atual_id nas FICHAs que não têm."""
    processos = carregar_processos()
    atualizados = 0

    for p in processos:
        if "etapa_atual_id" not in p:
            # Mapear etapa_atual (texto) para etapa_atual_id
            etapa_texto = p.get("etapa_atual", "").lower()
            etapa_id = "nomeacao"  # default

            mapa = {
                "aceite": "aceite",
                "nomeação": "nomeacao",
                "nomeacao": "nomeacao",
                "análise": "analise",
                "analise": "analise",
                "preparo": "preparo",
                "agendamento": "preparo",
                "perícia": "pericia",
                "pericia": "pericia",
                "laudo": "laudo",
                "entrega": "entrega",
                "concluído": "concluido",
                "concluido": "concluido",
            }

            for chave, valor in mapa.items():
                if chave in etapa_texto:
                    etapa_id = valor
                    break

            # Verificar status para inferir etapa
            status = p.get("status", "").lower()
            if "conclu" in status:
                etapa_id = "concluido"
            elif "laudo" in status:
                etapa_id = "laudo"
            elif "andamento" in status or "ativo" in status:
                if p.get("data_aceite"):
                    etapa_id = "analise"

            p["etapa_atual_id"] = etapa_id
            etapa_info = get_etapa_info(etapa_id)
            p["etapa_atual"] = etapa_info["nome"] if etapa_info else etapa_id
            p["atualizado_em"] = datetime.now().isoformat()

            ficha_path = p["_ficha_path"]
            dados = {k: v for k, v in p.items() if not k.startswith("_")}
            ficha_path.write_text(
                json.dumps(dados, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            atualizados += 1

    if atualizados > 0:
        print(f"  {C.DIM}Inicializado etapa_atual_id em {atualizados} processos{C.R}")


# ============================================================
# MAIN
# ============================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()

    # Garantir que todas as FICHAs têm etapa_atual_id
    garantir_etapas()

    if cmd == "status":
        cmd_status()
    elif cmd == "listar":
        cmd_listar()
    elif cmd == "ver":
        if len(sys.argv) < 3:
            print("  Uso: python3 workflow.py ver <CNJ ou número>")
            return
        cmd_ver(sys.argv[2])
    elif cmd == "avancar":
        if len(sys.argv) < 3:
            print("  Uso: python3 workflow.py avancar <CNJ ou número> [--etapa ETAPA]")
            return
        etapa = None
        if "--etapa" in sys.argv:
            idx = sys.argv.index("--etapa")
            if idx + 1 < len(sys.argv):
                etapa = sys.argv[idx + 1]
        cmd_avancar(sys.argv[2], etapa)
    elif cmd == "pendencias":
        cmd_pendencias()
    elif cmd == "dashboard":
        cmd_dashboard()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
