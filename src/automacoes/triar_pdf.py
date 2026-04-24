#!/usr/bin/env python3
"""
triar_pdf.py — Triagem e enriquecimento de processos do PJe.

DOIS MODOS:

  TRIAR (padrão) — Pega PDFs crus, extrai texto, identifica CNJ real,
  cidade, vara, data de nomeação, partes, valor. Cria pasta organizada
  com FICHA.json completa.

  ENRIQUECER — Varre pastas de processos que já existem e completa o que
  falta: extrai texto se não tem, enriquece FICHA.json esqueleto com
  dados reais do texto, lista o que ainda falta (PDF, texto, etc).

Uso:
    # TRIAR PDFs novos
    python3 triar_pdf.py triar arquivo.pdf                     # Tria 1 PDF
    python3 triar_pdf.py triar ~/Desktop/processos-pje-windows/   # Tria todos
    python3 triar_pdf.py triar arquivo.pdf --dry-run            # Só mostra

    # ENRIQUECER pastas existentes
    python3 triar_pdf.py enriquecer                            # Todas as pastas
    python3 triar_pdf.py enriquecer --dry-run                  # Só mostra
    python3 triar_pdf.py enriquecer --pasta CNJ-ou-nome        # Uma pasta só

    # DIAGNOSTICO — mostra o estado geral
    python3 triar_pdf.py diagnostico
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# === CONFIGURAÇÃO ===
DESTINO_PADRAO = Path.home() / "Desktop" / "ANALISADOR FINAL" / "processos"

# === REGEX ===
RE_CNJ = re.compile(r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})")
RE_VALOR = re.compile(r"Valor da causa:\s*R\$\s*([\d.,]+)")
RE_CLASSE = re.compile(r"Classe:\s*(?:\[[^\]]*\]\s*)?(.+)")
RE_ORGAO = re.compile(r"Órgão julgador:\s*(.+)")
RE_ASSUNTO = re.compile(r"Assuntos?:\s*(.+)")
RE_JG = re.compile(r"Justiça gratuita\?\s*(SIM|NÃO)", re.IGNORECASE)
RE_SEGREDO = re.compile(r"Segredo de justiça\?\s*(SIM|NÃO)", re.IGNORECASE)
RE_LIMINAR = re.compile(r"liminar.*?\?\s*(SIM|NÃO)", re.IGNORECASE)

# Para datas no formato PJe: "10643225593 12/03/2026 18:15"
RE_DATA_ID = re.compile(r"(\d{10,13})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})")

# Para nomeação
RE_NOMEACAO = re.compile(
    r"(\d{10,13})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})\s*\n\s*(?:Sem movimento\s*\n\s*)?Nomea",
    re.IGNORECASE | re.MULTILINE
)
# Fallback: "Nomeado perito" próximo de uma data
RE_NOMEACAO_SIMPLES = re.compile(r"Nomea(?:do|ção).*(?:perito|expert)", re.IGNORECASE)

# Designação de perícia
RE_DESIGNACAO = re.compile(
    r"[Dd]esigno a perícia para (?:o dia )?(\d{2}/\d{2}/\d{4})(?:,?\s*às?\s*(\d{2}[h:]\d{2}))?",
)

# Partes do PJe
RE_PARTE = re.compile(
    r"^([A-ZÀ-Ü\s\-\.]+?)\s*\((AUTOR|AUTORA|RÉU|RÉ|RÉU/RÉ|REQUERENTE|REQUERIDO|REQUERIDA|"
    r"REQUERIDO\(A\)|REQUERIDA\(A\)|"
    r"RECLAMANTE|RECLAMADO|RECLAMADO\(A\)|RECLAMADA|"
    r"PERITO\(A\)|PERITO|ADVOGADO|ADVOGADO\(A\)|ADVOGADA)\)",
    re.MULTILINE
)

# Nomeação via Sistema AJ-TJMG (formato alternativo)
RE_NOMEACAO_AJ = re.compile(
    r"Nomeação Perito\s*-\s*Sistema AJ-TJMG\s+.*?(JESUS|JÉSUS).*?(NOLETO|NOLÊTO)",
    re.IGNORECASE
)

# Comarca a partir do órgão julgador
RE_COMARCA = re.compile(r"[Cc]omarca de\s+(.+?)(?:\s*$|\s*-)", re.MULTILINE)
RE_CIDADE_ORGAO = re.compile(r"(?:Comarca|Foro|Fórum)\s+(?:de|do|da)\s+(.+?)(?:\s*$|\s*-)", re.MULTILINE)


class Cores:
    R = "\033[0m"
    B = "\033[1m"
    G = "\033[32m"
    Y = "\033[33m"
    RE = "\033[31m"
    CY = "\033[36m"


def extrair_texto(pdf_path: Path) -> str:
    """Extrai texto do PDF via pdftotext."""
    try:
        result = subprocess.run(
            ["pdftotext", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return ""


def extrair_dados(texto: str, nome_arquivo: str = "") -> dict:
    """Extrai todos os dados estruturados do texto do PJe."""
    dados = {
        "cnj_real": "",
        "cnj_arquivo": "",
        "classe": "",
        "orgao_julgador": "",
        "cidade": "",
        "vara": "",
        "valor_causa": "",
        "assunto": "",
        "justica_gratuita": "",
        "segredo_justica": "",
        "liminar": "",
        "data_nomeacao": "",
        "hora_nomeacao": "",
        "id_nomeacao": "",
        "data_pericia": "",
        "hora_pericia": "",
        "partes": [],
        "autor": "",
        "reu": "",
        "perito": "",
        "advogados": [],
    }

    # CNJ do nome do arquivo
    m = RE_CNJ.search(nome_arquivo)
    if m:
        dados["cnj_arquivo"] = m.group(1)

    # CNJ real (primeiro encontrado no texto, geralmente no cabeçalho)
    cnjs = RE_CNJ.findall(texto[:3000])  # só no começo
    if cnjs:
        dados["cnj_real"] = cnjs[0]

    # Classe processual
    m = RE_CLASSE.search(texto[:2000])
    if m:
        dados["classe"] = m.group(1).strip()

    # Órgão julgador (pode quebrar linha no meio do nome da cidade)
    m = RE_ORGAO.search(texto[:2000])
    if m:
        orgao = m.group(1).strip()
        # Juntar próxima linha se é continuação do nome da cidade
        pos_fim = m.end()
        proximas = texto[pos_fim:pos_fim+100].split('\n')
        for prox in proximas[1:3]:  # até 2 linhas depois
            prox = prox.strip()
            if prox and not prox.startswith(('Última', 'Valor', 'Assunto', 'Segredo', 'Justiça', 'Pedido', 'Partes')):
                orgao = orgao + " " + prox
            else:
                break
        dados["orgao_julgador"] = orgao
        # Extrair cidade
        mc = re.search(r"[Cc]omarca de\s+(.+?)(?:\s*$)", orgao)
        if mc:
            dados["cidade"] = mc.group(1).strip()
        else:
            mc = re.search(r"(?:Comarca|Foro|Fórum)\s+(?:de|do|da)\s+(.+?)(?:\s*$)", orgao)
            if mc:
                dados["cidade"] = mc.group(1).strip()
        # Extrair vara
        vara_match = re.match(r"(\d+ª?\s*Vara[^,]*)", orgao)
        if vara_match:
            dados["vara"] = vara_match.group(1).strip()

    # Valor da causa
    m = RE_VALOR.search(texto[:3000])
    if m:
        dados["valor_causa"] = m.group(1).strip()

    # Assunto
    m = RE_ASSUNTO.search(texto[:3000])
    if m:
        dados["assunto"] = m.group(1).strip()

    # Justiça gratuita
    m = RE_JG.search(texto[:3000])
    if m:
        dados["justica_gratuita"] = m.group(1).upper()

    # Segredo de justiça
    m = RE_SEGREDO.search(texto[:3000])
    if m:
        dados["segredo_justica"] = m.group(1).upper()

    # Liminar
    m = RE_LIMINAR.search(texto[:3000])
    if m:
        dados["liminar"] = m.group(1).upper()

    # Data de nomeação (padrão PJe: ID + data + "Nomeado perito")
    m = RE_NOMEACAO.search(texto)
    if m:
        dados["id_nomeacao"] = m.group(1)
        dados["data_nomeacao"] = m.group(2)
        dados["hora_nomeacao"] = m.group(3)
    else:
        # Fallback 1: buscar "Nomeado perito" e pegar data mais próxima acima
        encontrou = False
        for match in RE_NOMEACAO_SIMPLES.finditer(texto):
            pos = match.start()
            trecho_antes = texto[max(0, pos-200):pos]
            datas = RE_DATA_ID.findall(trecho_antes)
            if datas:
                ultima = datas[-1]
                dados["id_nomeacao"] = ultima[0]
                dados["data_nomeacao"] = ultima[1]
                dados["hora_nomeacao"] = ultima[2]
                encontrou = True
                break
        # Fallback 2: formato AJ-TJMG — datas e tipos em blocos separados
        if not encontrou:
            m_aj = RE_NOMEACAO_AJ.search(texto)
            if m_aj:
                # Pegar todas as datas do bloco antes
                pos = m_aj.start()
                # Voltar até encontrar o bloco de datas (IDs com datas)
                trecho = texto[max(0, pos-3000):pos]
                datas = RE_DATA_ID.findall(trecho)
                if datas:
                    # Contar quantos tipos de documento existem entre datas e a nomeação AJ
                    bloco_tipos = texto[texto.rfind('\n\n', max(0, pos-3000), pos):pos]
                    linhas_tipo = [l.strip() for l in bloco_tipos.split('\n') if l.strip() and not RE_DATA_ID.match(l.strip())]
                    # A última data corresponde ao último tipo antes da nomeação AJ
                    # Precisamos contar a posição relativa
                    if datas:
                        ultima = datas[-1]
                        dados["id_nomeacao"] = ultima[0]
                        dados["data_nomeacao"] = ultima[1]
                        dados["hora_nomeacao"] = ultima[2]

    # Data da perícia designada
    m = RE_DESIGNACAO.search(texto)
    if m:
        dados["data_pericia"] = m.group(1)
        if m.group(2):
            dados["hora_pericia"] = m.group(2).replace("h", ":")

    # Partes
    for m in RE_PARTE.finditer(texto[:5000]):
        nome = m.group(1).strip()
        papel = m.group(2).strip()
        dados["partes"].append({"nome": nome, "papel": papel})

        papel_limpo = re.sub(r'\(A\)', '', papel.upper()).replace("/RÉ", "").strip()
        if papel_limpo in ("AUTOR", "AUTORA", "REQUERENTE", "RECLAMANTE"):
            if not dados["autor"]:
                dados["autor"] = nome
        elif papel_limpo in ("RÉU", "RÉ", "REQUERIDO", "REQUERIDA", "RECLAMADO", "RECLAMADA"):
            if not dados["reu"]:
                dados["reu"] = nome
        elif "PERITO" in papel_limpo:
            dados["perito"] = nome
        elif "ADVOGAD" in papel_limpo:
            dados["advogados"].append(nome)

    return dados


def gerar_nome_pasta(dados: dict) -> str:
    """Gera nome da pasta: Cidade - Vara - CNJ."""
    partes = []
    if dados["cidade"]:
        partes.append(dados["cidade"])
    if dados["vara"]:
        # Simplificar: "2ª Vara Cível, Criminal..." → "2a Vara"
        vara = re.sub(r"ª", "a", dados["vara"])
        vara_curta = re.match(r"(\d+a?\s*Vara)", vara)
        if vara_curta:
            partes.append(vara_curta.group(1))
        else:
            partes.append(vara[:30])
    cnj = dados["cnj_real"] or dados["cnj_arquivo"]
    if cnj:
        partes.append(cnj)
    return " - ".join(partes) if partes else "SEM-IDENTIFICACAO"


def criar_ficha_json(dados: dict) -> dict:
    """Cria FICHA.json estruturada."""
    return {
        "numero_cnj": dados["cnj_real"] or dados["cnj_arquivo"],
        "cnj_arquivo_original": dados["cnj_arquivo"],
        "classe": dados["classe"],
        "orgao_julgador": dados["orgao_julgador"],
        "cidade": dados["cidade"],
        "vara": dados["vara"],
        "valor_causa": dados["valor_causa"],
        "assunto": dados["assunto"],
        "justica_gratuita": dados["justica_gratuita"],
        "segredo_justica": dados["segredo_justica"],
        "liminar": dados["liminar"],
        "data_nomeacao": dados["data_nomeacao"],
        "hora_nomeacao": dados["hora_nomeacao"],
        "id_nomeacao_pje": dados["id_nomeacao"],
        "data_pericia_designada": dados["data_pericia"],
        "hora_pericia_designada": dados["hora_pericia"],
        "autor": dados["autor"],
        "reu": dados["reu"],
        "perito": dados["perito"],
        "advogados": dados["advogados"],
        "partes": dados["partes"],
        "status": "triado",
        "etapa_atual": "pendente-aceite",
        "extraido_em": datetime.now().isoformat(),
        "origem_pdf": dados.get("arquivo_original", ""),
    }


def triar_um_pdf(pdf_path: Path, destino: Path, dry_run: bool = False) -> dict:
    """Tria um único PDF. Retorna dados extraídos."""
    nome_arquivo = pdf_path.name

    print(f"\n{Cores.CY}{'='*60}{Cores.R}")
    print(f"{Cores.B}Triando:{Cores.R} {nome_arquivo}")

    # 1. Extrair texto
    texto = extrair_texto(pdf_path)
    if not texto:
        print(f"  {Cores.RE}✗ Falha na extração de texto{Cores.R}")
        return {"erro": "falha_extracao", "arquivo": nome_arquivo}

    print(f"  {Cores.G}✓{Cores.R} Texto extraído ({len(texto)} chars, ~{texto.count(chr(10))} linhas)")

    # 2. Extrair dados
    dados = extrair_dados(texto, nome_arquivo)
    dados["arquivo_original"] = nome_arquivo

    # 3. Mostrar resultado
    cnj = dados["cnj_real"] or dados["cnj_arquivo"]
    diverge = dados["cnj_real"] and dados["cnj_arquivo"] and dados["cnj_real"] != dados["cnj_arquivo"]

    print(f"  CNJ real:     {Cores.B}{dados['cnj_real'] or '???'}{Cores.R}")
    if diverge:
        print(f"  {Cores.Y}⚠ CNJ do arquivo: {dados['cnj_arquivo']} (DIVERGE!){Cores.R}")
    print(f"  Cidade:       {dados['cidade'] or '???'}")
    print(f"  Vara:         {dados['vara'] or '???'}")
    print(f"  Nomeação:     {dados['data_nomeacao'] or '???'}")
    print(f"  Perícia:      {dados['data_pericia'] or 'não designada'} {dados['hora_pericia'] or ''}")
    print(f"  Valor:        R$ {dados['valor_causa'] or '???'}")
    print(f"  Assunto:      {dados['assunto'] or '???'}")
    print(f"  JG:           {dados['justica_gratuita'] or '???'}")
    print(f"  Autor:        {dados['autor'] or '???'}")
    print(f"  Réu:          {dados['reu'] or '???'}")
    print(f"  Perito:       {dados['perito'] or '???'}")

    # 4. Gerar nome da pasta
    nome_pasta = gerar_nome_pasta(dados)
    pasta_destino = destino / nome_pasta
    print(f"  Pasta:        {Cores.CY}{nome_pasta}{Cores.R}")

    if dry_run:
        print(f"  {Cores.Y}[DRY RUN] Não criou pasta nem moveu arquivos{Cores.R}")
        return dados

    # 5. Criar pasta e estrutura
    pasta_destino.mkdir(parents=True, exist_ok=True)
    (pasta_destino / "PDFs").mkdir(exist_ok=True)

    # 6. Copiar PDF
    pdf_destino = pasta_destino / "PDFs" / pdf_path.name
    if not pdf_destino.exists():
        shutil.copy2(pdf_path, pdf_destino)
        print(f"  {Cores.G}✓{Cores.R} PDF copiado")
    else:
        print(f"  {Cores.Y}• PDF já existe no destino{Cores.R}")

    # 7. Salvar TEXTO-EXTRAIDO.txt
    texto_path = pasta_destino / "TEXTO-EXTRAIDO.txt"
    texto_path.write_text(texto, encoding="utf-8")
    print(f"  {Cores.G}✓{Cores.R} TEXTO-EXTRAIDO.txt ({texto.count(chr(10))} linhas)")

    # 8. Salvar FICHA.json
    ficha = criar_ficha_json(dados)
    ficha_path = pasta_destino / "FICHA.json"
    ficha_path.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  {Cores.G}✓{Cores.R} FICHA.json")

    return dados


def enriquecer_pasta(pasta: Path, dry_run: bool = False) -> dict:
    """Enriquece uma pasta de processo existente. Retorna diagnóstico."""
    nome = pasta.name
    resultado = {
        "pasta": nome,
        "tinha_pdf": False,
        "tinha_texto": False,
        "tinha_ficha": False,
        "ficha_esqueleto": False,
        "acoes": [],
    }

    # Verificar o que já existe
    texto_path = pasta / "TEXTO-EXTRAIDO.txt"
    ficha_path = pasta / "FICHA.json"

    # Achar PDFs (na raiz ou em PDFs/)
    pdfs = list(pasta.glob("*.pdf")) + list((pasta / "PDFs").glob("*.pdf")) if (pasta / "PDFs").exists() else list(pasta.glob("*.pdf"))
    resultado["tinha_pdf"] = len(pdfs) > 0
    resultado["tinha_texto"] = texto_path.exists() and texto_path.stat().st_size > 100
    resultado["tinha_ficha"] = ficha_path.exists()

    # Verificar se FICHA.json é esqueleto (< 300 bytes ou sem cidade)
    if resultado["tinha_ficha"]:
        try:
            ficha_atual = json.loads(ficha_path.read_text(encoding="utf-8"))
            campos_ricos = ["cidade", "autor", "reu", "data_nomeacao", "assunto"]
            preenchidos = sum(1 for c in campos_ricos if ficha_atual.get(c))
            resultado["ficha_esqueleto"] = preenchidos < 2
        except (json.JSONDecodeError, KeyError):
            resultado["ficha_esqueleto"] = True

    # Se não tem PDF nem texto, não tem o que fazer
    if not resultado["tinha_pdf"] and not resultado["tinha_texto"]:
        resultado["acoes"].append("SEM_PDF_E_SEM_TEXTO")
        print(f"  {Cores.RE}✗{Cores.R} {nome}: sem PDF e sem texto — nada a fazer")
        return resultado

    # AÇÃO 1: Extrair texto se falta
    texto = ""
    if not resultado["tinha_texto"] and pdfs:
        pdf = pdfs[0]
        texto = extrair_texto(pdf)
        if texto:
            if not dry_run:
                texto_path.write_text(texto, encoding="utf-8")
            resultado["acoes"].append("TEXTO_EXTRAIDO")
            print(f"  {Cores.G}+{Cores.R} {nome}: texto extraído ({texto.count(chr(10))} linhas)")
        else:
            resultado["acoes"].append("FALHA_EXTRACAO")
            print(f"  {Cores.RE}✗{Cores.R} {nome}: falha ao extrair texto do PDF")
            return resultado
    elif resultado["tinha_texto"]:
        texto = texto_path.read_text(encoding="utf-8")

    # AÇÃO 2: Enriquecer FICHA.json se é esqueleto ou não existe
    if texto and (resultado["ficha_esqueleto"] or not resultado["tinha_ficha"]):
        dados = extrair_dados(texto, nome)
        ficha_nova = criar_ficha_json(dados)

        # Se já existia, preservar campos manuais (status, etapa, honorarios, numero_pericia)
        if resultado["tinha_ficha"]:
            try:
                ficha_atual = json.loads(ficha_path.read_text(encoding="utf-8"))
                for campo in ["status", "etapa_atual", "etapa_atual_id", "numero_pericia",
                              "honorarios", "data_aceite", "origem", "pasta_original",
                              "tipo_pericia", "objeto", "areas_medicas", "prazos"]:
                    if campo in ficha_atual and ficha_atual[campo]:
                        ficha_nova[campo] = ficha_atual[campo]
            except (json.JSONDecodeError, KeyError):
                pass

        if not dry_run:
            ficha_path.write_text(json.dumps(ficha_nova, ensure_ascii=False, indent=2), encoding="utf-8")
        resultado["acoes"].append("FICHA_ENRIQUECIDA")
        cnj = ficha_nova.get("numero_cnj", "?")
        cidade = ficha_nova.get("cidade", "?")
        nomeacao = ficha_nova.get("data_nomeacao", "?")
        print(f"  {Cores.G}+{Cores.R} {nome}: FICHA enriquecida (CNJ={cnj}, {cidade}, nomeação={nomeacao})")
    elif resultado["tinha_ficha"] and not resultado["ficha_esqueleto"]:
        resultado["acoes"].append("FICHA_OK")

    return resultado


def cmd_enriquecer(args):
    """Modo enriquecer: varre pastas existentes e completa o que falta."""
    destino = Path(args.destino).expanduser()

    if not destino.exists():
        print(f"{Cores.RE}Erro: {destino} não existe{Cores.R}")
        sys.exit(1)

    # Coletar pastas de processos (ignorar arquivos soltos)
    if args.pasta:
        # Uma pasta específica
        candidatas = [destino / args.pasta]
        if not candidatas[0].exists():
            # Buscar por CNJ parcial
            candidatas = [p for p in destino.iterdir() if p.is_dir() and args.pasta in p.name]
    else:
        candidatas = sorted([p for p in destino.iterdir() if p.is_dir()])

    if not candidatas:
        print(f"{Cores.Y}Nenhuma pasta encontrada{Cores.R}")
        sys.exit(0)

    print(f"{Cores.B}Enriquecendo {len(candidatas)} pasta(s){Cores.R}")
    print(f"Base: {destino}")
    if args.dry_run:
        print(f"{Cores.Y}[MODO DRY RUN — nada será alterado]{Cores.R}")

    stats = {"texto_extraido": 0, "ficha_enriquecida": 0, "sem_pdf": 0, "ja_ok": 0, "erros": 0}

    for pasta in candidatas:
        try:
            r = enriquecer_pasta(pasta, args.dry_run)
            for acao in r["acoes"]:
                if acao == "TEXTO_EXTRAIDO":
                    stats["texto_extraido"] += 1
                elif acao == "FICHA_ENRIQUECIDA":
                    stats["ficha_enriquecida"] += 1
                elif acao == "SEM_PDF_E_SEM_TEXTO":
                    stats["sem_pdf"] += 1
                elif acao == "FICHA_OK":
                    stats["ja_ok"] += 1
                elif "FALHA" in acao:
                    stats["erros"] += 1
        except Exception as e:
            print(f"  {Cores.RE}✗ {pasta.name}: {e}{Cores.R}")
            stats["erros"] += 1

    # Resumo
    print(f"\n{Cores.CY}{'='*60}{Cores.R}")
    print(f"{Cores.B}Resumo do enriquecimento:{Cores.R}")
    print(f"  Textos extraídos:    {stats['texto_extraido']}")
    print(f"  Fichas enriquecidas: {stats['ficha_enriquecida']}")
    print(f"  Já completas:        {stats['ja_ok']}")
    print(f"  Sem PDF (pendente):  {stats['sem_pdf']}")
    print(f"  Erros:               {stats['erros']}")


def cmd_diagnostico(args):
    """Modo diagnóstico: mostra estado geral das pastas."""
    destino = Path(args.destino).expanduser()

    if not destino.exists():
        print(f"{Cores.RE}Erro: {destino} não existe{Cores.R}")
        sys.exit(1)

    pastas = sorted([p for p in destino.iterdir() if p.is_dir()])

    total = len(pastas)
    com_pdf = 0
    com_texto = 0
    com_ficha = 0
    ficha_esqueleto = 0
    com_urgencia = 0
    completas = 0  # tem PDF + texto + ficha rica

    for pasta in pastas:
        tem_pdf = any(pasta.glob("*.pdf")) or (pasta / "PDFs").exists() and any((pasta / "PDFs").glob("*.pdf"))
        tem_texto = (pasta / "TEXTO-EXTRAIDO.txt").exists()
        tem_ficha = (pasta / "FICHA.json").exists()
        tem_urgencia = (pasta / "URGENCIA.json").exists()

        if tem_pdf:
            com_pdf += 1
        if tem_texto:
            com_texto += 1
        if tem_ficha:
            com_ficha += 1
            try:
                f = json.loads((pasta / "FICHA.json").read_text(encoding="utf-8"))
                campos = ["cidade", "autor", "reu", "data_nomeacao", "assunto"]
                if sum(1 for c in campos if f.get(c)) < 2:
                    ficha_esqueleto += 1
                else:
                    if tem_pdf and tem_texto:
                        completas += 1
            except Exception:
                ficha_esqueleto += 1
        if tem_urgencia:
            com_urgencia += 1

    print(f"\n{Cores.CY}{'='*60}{Cores.R}")
    print(f"{Cores.B}DIAGNÓSTICO — {destino.name}/{Cores.R}")
    print(f"{Cores.CY}{'='*60}{Cores.R}")
    print(f"  Pastas totais:         {total}")
    print(f"  Com PDF:               {Cores.G}{com_pdf}{Cores.R}")
    print(f"  Com TEXTO-EXTRAIDO:    {Cores.G}{com_texto}{Cores.R}")
    print(f"  Com FICHA.json:        {com_ficha} ({Cores.Y}{ficha_esqueleto} esqueleto{Cores.R})")
    print(f"  Com URGENCIA.json:     {com_urgencia}")
    print(f"  {Cores.G}Completas (PDF+texto+ficha rica): {completas}{Cores.R}")
    print(f"  {Cores.RE}Faltam PDF:              {total - com_pdf}{Cores.R}")
    print(f"  {Cores.Y}Faltam texto:            {total - com_texto}{Cores.R}")
    print(f"  {Cores.Y}Fichas a enriquecer:     {ficha_esqueleto + (total - com_ficha)}{Cores.R}")


def cmd_triar(args):
    """Modo triar: pega PDFs novos e cria pastas."""
    entrada = Path(args.entrada).expanduser()
    destino = Path(args.destino).expanduser()

    if not entrada.exists():
        print(f"{Cores.RE}Erro: {entrada} não existe{Cores.R}")
        sys.exit(1)

    # Coletar PDFs
    if entrada.is_file() and entrada.suffix.lower() == ".pdf":
        pdfs = [entrada]
    elif entrada.is_dir():
        pdfs = sorted(entrada.glob("*.pdf"))
        for sub in ["_chrome_downloads"]:
            subdir = entrada / sub
            if subdir.exists():
                pdfs.extend(sorted(subdir.glob("*.pdf")))
    else:
        print(f"{Cores.RE}Erro: {entrada} não é PDF nem pasta{Cores.R}")
        sys.exit(1)

    if not pdfs:
        print(f"{Cores.Y}Nenhum PDF encontrado{Cores.R}")
        sys.exit(0)

    print(f"{Cores.B}Triagem de {len(pdfs)} PDF(s){Cores.R}")
    print(f"Destino: {destino}")
    if args.dry_run:
        print(f"{Cores.Y}[MODO DRY RUN — nada será criado]{Cores.R}")

    resultados = []
    erros = 0

    for pdf in pdfs:
        try:
            dados = triar_um_pdf(pdf, destino, args.dry_run)
            resultados.append(dados)
            if "erro" in dados:
                erros += 1
        except Exception as e:
            print(f"  {Cores.RE}✗ Erro: {e}{Cores.R}")
            erros += 1

    # Resumo
    print(f"\n{Cores.CY}{'='*60}{Cores.R}")
    print(f"{Cores.B}Resumo:{Cores.R} {len(resultados)} processados, {erros} erros")

    divergencias = [r for r in resultados if r.get("cnj_real") and r.get("cnj_arquivo") and r["cnj_real"] != r["cnj_arquivo"]]
    if divergencias:
        print(f"\n{Cores.Y}⚠ {len(divergencias)} PDFs com CNJ divergente (arquivo ≠ conteúdo):{Cores.R}")
        for d in divergencias:
            print(f"  {d['cnj_arquivo']} → {d['cnj_real']}")

    # Salvar índice
    if not args.dry_run and resultados:
        indice_path = destino / f"TRIAGEM-{datetime.now().strftime('%Y-%m-%d')}.json"
        indice = []
        for r in resultados:
            if "erro" not in r:
                indice.append({
                    "cnj_real": r.get("cnj_real", ""),
                    "cnj_arquivo": r.get("cnj_arquivo", ""),
                    "cidade": r.get("cidade", ""),
                    "vara": r.get("vara", ""),
                    "data_nomeacao": r.get("data_nomeacao", ""),
                    "nome_pasta": gerar_nome_pasta(r),
                })
        indice_path.write_text(json.dumps(indice, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n{Cores.G}✓{Cores.R} Índice salvo: {indice_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Triagem e enriquecimento de processos do PJe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python3 triar_pdf.py diagnostico                        # Ver estado geral
  python3 triar_pdf.py triar ~/Desktop/processos-pje-windows/  # Triar PDFs novos
  python3 triar_pdf.py enriquecer                          # Completar pastas
  python3 triar_pdf.py enriquecer --dry-run                # Só mostrar o que faria
"""
    )
    sub = parser.add_subparsers(dest="comando")

    # Subcomando: triar
    p_triar = sub.add_parser("triar", help="Tria PDFs novos e cria pastas")
    p_triar.add_argument("entrada", help="PDF ou pasta com PDFs")
    p_triar.add_argument("--destino", default=str(DESTINO_PADRAO))
    p_triar.add_argument("--dry-run", action="store_true")

    # Subcomando: enriquecer
    p_enriquecer = sub.add_parser("enriquecer", help="Completa pastas existentes")
    p_enriquecer.add_argument("--destino", default=str(DESTINO_PADRAO))
    p_enriquecer.add_argument("--pasta", default=None, help="Nome ou CNJ de uma pasta específica")
    p_enriquecer.add_argument("--dry-run", action="store_true")

    # Subcomando: diagnostico
    p_diag = sub.add_parser("diagnostico", help="Mostra estado geral das pastas")
    p_diag.add_argument("--destino", default=str(DESTINO_PADRAO))

    args = parser.parse_args()

    if args.comando == "triar":
        cmd_triar(args)
    elif args.comando == "enriquecer":
        cmd_enriquecer(args)
    elif args.comando == "diagnostico":
        cmd_diagnostico(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
