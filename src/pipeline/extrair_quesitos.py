#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extrair_quesitos.py — Parser de quesitos de processos judiciais.

Extrai quesitos de diferentes origens (autor, réu, juízo, MP, litisconsorte),
classifica por origem, e salva como JSON + MD na pasta do processo.

Uso:
    python3 extrair_quesitos.py --cnj 5015391-72
    python3 extrair_quesitos.py --cnj 5017700-42.2020.8.13.0105
    python3 extrair_quesitos.py --arquivo /caminho/TEXTO-EXTRAIDO.txt
    python3 extrair_quesitos.py /caminho/para/pasta/do/processo

Autor: Sistema Stemmia
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════════

BASE = Path.home() / "Desktop" / "ANALISADOR FINAL" / "processos"

RE_CNJ = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")

# Cores ANSI
class C:
    R = "\033[0m"
    B = "\033[1m"
    G = "\033[32m"
    Y = "\033[33m"
    RE = "\033[31m"
    CY = "\033[36m"
    DIM = "\033[2m"


# ═══════════════════════════════════════════════════════════════════════════════
# PADRÕES DE CABEÇALHO DE QUESITOS
# ═══════════════════════════════════════════════════════════════════════════════

# Cada entrada: (regex compilado, chave de origem)
# Ordem importa: padrões mais específicos primeiro
PADROES_ORIGEM = [
    # --- Suplementares (de qualquer origem) ---
    # Só matcha como título (linha curta, não no meio de uma frase longa)
    (re.compile(
        r"^\s*[Qq]uesitos?\s+[Ss]uplementar(?:es)?\s*(?:[-–:]|$)",
        re.IGNORECASE
    ), "suplementares"),

    # --- Ministério Público ---
    (re.compile(
        r"[Qq]uesitos?\s+(?:d[oa]s?\s+)?(?:Minist[eé]rio\s+P[uú]blico|M\.?\s*P\.?)",
        re.IGNORECASE
    ), "mp"),

    # --- Denunciado / Litisconsorte ---
    (re.compile(
        r"[Qq]uesitos?\s+(?:d[oa]s?\s+)?(?:parte\s+)?(?:denunciad[oa]|litisconsorte|terceiro|chamad[oa]|assistente\s+(?:simples|litisconsorcial))",
        re.IGNORECASE
    ), "litisconsorte"),

    # --- Juízo ---
    (re.compile(
        r"[Qq]uesitos?\s+(?:d[oa]s?\s+)?(?:Ju[ií]z[oa]?|MM\.?\s*Ju[ií]z|Meritíssim[oa]|periciais\s+d[oa]\s+Ju[ií]z)",
        re.IGNORECASE
    ), "juizo"),

    # --- Réu (vários padrões, incluindo "QUESITOS DA PARTE RÉ – ID ...") ---
    (re.compile(
        r"[Qq]uesitos?\s+(?:d[oa]s?\s+)?(?:parte\s+)?(?:[Rr][eé](?:u|quer)?id[oa]?|[Rr][eé](?:u)?(?:\s|$)|[Rr]eclamad[oa]|[Ee]xecutad[oa]|[Ii]mpetrad[oa])",
        re.IGNORECASE
    ), "reu"),

    # --- Autor (vários padrões, incluindo "QUESITOS DA PARTE AUTORA – ID ...") ---
    (re.compile(
        r"[Qq]uesitos?\s+(?:d[oa]s?\s+)?(?:parte\s+)?(?:[Aa]utor[a]?|[Rr]equerente|[Rr]eclamante|[Ee]xequente|[Ii]mpetrante)",
        re.IGNORECASE
    ), "autor"),

    # --- Padrão genérico "QUESITOS MÉDICOS" (normalmente da ré) ---
    # Só matcha se a linha é APENAS "QUESITOS MÉDICOS" (com ou sem espaços)
    (re.compile(
        r"^\s*QUESITOS\s+M[EÉ]DICOS\s*$",
        re.IGNORECASE
    ), "reu"),

    # --- "QUESITOS PERICIAIS" como título de petição de quesitos ---
    # Só matcha linhas longas o suficiente para serem um título real,
    # NÃO itens de índice de documentos (que são curtos e misturados)
    # Requer que a próxima palavra não seja vazia (deve ter conteúdo após)
    (re.compile(
        r"^\s*QUESITOS\s+PERICIAIS\s*[,:]",
        re.IGNORECASE
    ), "autor"),

    # --- Padrões indiretos: "apresenta ... os seguintes quesitos" ---
    # Comuns quando a parte introduz quesitos em petição sem título específico
    (re.compile(
        r"(?:apresenta|formula|propõe)\s+.*(?:os\s+)?(?:seguintes\s+)?quesitos\b",
        re.IGNORECASE
    ), "_contexto"),

    # --- "os QUESITOS a serem respondidos" ---
    (re.compile(
        r"\bos\s+QUESITOS\s+a\s+serem\s+respondidos",
    ), "_contexto"),
]

# Padrões de sub-seção DENTRO de quesitos (não iniciam nova seção)
# Ex: "Quesitos sobre a Dinâmica do Acidente e Responsabilidade"
RE_SUBSECAO_QUESITOS = re.compile(
    r"^\s*[Qq]uesitos?\s+sobre\s+",
    re.IGNORECASE
)

# Padrões de ausência — só matcham linhas INTEIRAS que indicam ausência
# (evita falso positivo com "Prejudicado" dentro de respostas a quesitos)
PADROES_AUSENCIA = [
    re.compile(r"[Nn][aã]o\s+(?:constam?|h[aá]|foram?\s+(?:apresentad|formulad))", re.IGNORECASE),
    re.compile(r"[Nn][aã]o\s+(?:houve|apresent)", re.IGNORECASE),
    re.compile(r"[Ss]em\s+quesitos", re.IGNORECASE),
    # "Prejudicado" só quando é a linha inteira (sem numeração de quesito)
    re.compile(r"^\s*[Pp]rejudicad[oa]\.?\s*$", re.IGNORECASE),
]

# Padrão de quesito numerado
RE_QUESITO_NUM = re.compile(
    r"^\s*(\d{1,3})\s*[-).:\s]\s*(.+)",
)

# Padrão de subquesito (ex: "3.1-", "5.2)", "a)", "b)")
RE_SUBQUESITO = re.compile(
    r"^\s*(?:\d{1,3}\.\d{1,2}|[a-z]\))\s*[-)\s]\s*(.+)",
    re.IGNORECASE,
)

# Linhas que indicam fim de seção de quesitos
RE_FIM_SECAO = [
    re.compile(r"^N[uú]mero do documento:", re.IGNORECASE),
    re.compile(r"^https?://pje\.tjmg", re.IGNORECASE),
    re.compile(r"^Assinado eletronicamente por:", re.IGNORECASE),
    re.compile(r"^Num\.\s+\d+\s*-\s*P[aá]g", re.IGNORECASE),
    re.compile(r"^\s*Nestes\s+termos", re.IGNORECASE),
    re.compile(r"^\s*Termos\s+em\s+que", re.IGNORECASE),
    re.compile(r"^\s*Pede\s+deferimento", re.IGNORECASE),
    re.compile(r"^\s*Protesta\s+por\s+apresentar\s+novos", re.IGNORECASE),
    re.compile(r"^\s*DAS\s+PUBLICA[ÇC][OÕ]ES", re.IGNORECASE),
    re.compile(r"^\s*Termo\s+de\s+encerramento", re.IGNORECASE),
    re.compile(r"^\s*Conclus[aã]o\b", re.IGNORECASE),
    re.compile(r"^_{10,}$"),  # Linhas de separação
]

# Linhas de transição PJe que devem ser ignoradas mas não terminam seção
RE_LINHA_PJE = re.compile(
    r"^(?:N[uú]mero do documento:|https?://pje|Assinado eletronicamente|Num\.\s+\d+\s*-\s*P[aá]g)",
    re.IGNORECASE,
)


# ═══════════════════════════════════════════════════════════════════════════════
# BUSCA DE PROCESSO
# ═══════════════════════════════════════════════════════════════════════════════

def encontrar_pasta(cnj: str) -> Optional[Path]:
    """Busca pasta do processo pelo número CNJ (completo ou parcial)."""
    if not BASE.exists():
        return None
    # Busca exata
    d = BASE / cnj
    if d.is_dir():
        return d
    # Busca parcial
    for p in sorted(BASE.iterdir()):
        if p.is_dir() and cnj in p.name:
            return p
    return None


def encontrar_texto(pasta: Path) -> Optional[Path]:
    """Encontra TEXTO-EXTRAIDO.txt na pasta do processo."""
    candidatos = [
        pasta / "TEXTO-EXTRAIDO.txt",
        pasta / "texto-extraido.txt",
        pasta / "TEXTO_EXTRAIDO.txt",
    ]
    for c in candidatos:
        if c.exists():
            return c
    # Fallback: maior .txt
    txts = sorted(pasta.glob("*.txt"), key=lambda f: f.stat().st_size, reverse=True)
    return txts[0] if txts else None


def extrair_cnj_do_texto(texto: str) -> str:
    """Extrai número CNJ das primeiras linhas do texto."""
    for linha in texto.split("\n")[:30]:
        m = RE_CNJ.search(linha)
        if m:
            return m.group()
    return ""


# ═══════════════════════════════════════════════════════════════════════════════
# PARSER DE QUESITOS
# ═══════════════════════════════════════════════════════════════════════════════

def classificar_origem(linha: str) -> Optional[tuple[str, bool]]:
    """Verifica se a linha é um cabeçalho de seção de quesitos.

    Retorna (chave_origem, eh_generico) ou None.
    eh_generico é True para cabeçalhos como "QUESITOS MÉDICOS" / "QUESITOS PERICIAIS"
    que precisam de refinamento por contexto.
    """
    texto = linha.strip()
    if not texto:
        return None

    # Sub-seções como "Quesitos sobre a Dinâmica..." não são novos cabeçalhos
    if RE_SUBSECAO_QUESITOS.match(texto):
        return None

    for idx, (padrao, origem) in enumerate(PADROES_ORIGEM):
        if padrao.search(texto):
            # Os dois últimos padrões são genéricos
            eh_generico = idx >= len(PADROES_ORIGEM) - 2
            return (origem, eh_generico)

    return None


def eh_ausencia(linhas: list[str], inicio: int, limite: int = 3) -> Optional[str]:
    """Verifica se as próximas linhas não-vazias indicam ausência de quesitos.

    Só verifica as primeiras linhas com conteúdo (default: 3).
    Se a primeira linha com conteúdo for um quesito numerado, retorna None.
    Retorna o motivo (ex: 'Não constam nos autos') ou None.
    """
    fim = min(inicio + 10, len(linhas))  # Janela de busca
    linhas_checadas = 0
    for i in range(inicio, fim):
        texto = linhas[i].strip()
        if not texto:
            continue
        # Se a primeira linha com conteúdo é um quesito numerado, não é ausência
        if RE_QUESITO_NUM.match(texto):
            return None
        for padrao in PADROES_AUSENCIA:
            if padrao.search(texto):
                return texto
        linhas_checadas += 1
        if linhas_checadas >= limite:
            break
    return None


def eh_fim_secao(linha: str) -> bool:
    """Verifica se a linha indica fim de seção de quesitos."""
    texto = linha.strip()
    if not texto:
        return False
    for padrao in RE_FIM_SECAO:
        if padrao.search(texto):
            return True
    return False


def eh_linha_pje(linha: str) -> bool:
    """Verifica se a linha é cabeçalho/rodapé PJe (ignorar mas continuar)."""
    return bool(RE_LINHA_PJE.search(linha.strip()))


def eh_novo_cabecalho_quesitos(linha: str) -> bool:
    """Verifica se a linha é cabeçalho de nova seção de quesitos.

    Retorna False para sub-seções como 'Quesitos sobre a Dinâmica...'
    que são divisões DENTRO de uma seção, não nova seção.
    """
    texto = linha.strip()
    # Sub-seções não contam como novo cabeçalho
    if RE_SUBSECAO_QUESITOS.match(texto):
        return False
    resultado = classificar_origem(linha)
    return resultado is not None


def extrair_quesitos_secao(linhas: list[str], inicio: int) -> tuple[list[str], int]:
    """Extrai a lista de quesitos a partir de uma posição.

    Retorna (lista_quesitos, próxima_linha_após_seção).
    Concatena linhas de continuação ao quesito anterior.
    """
    quesitos = []
    quesito_atual = []
    i = inicio
    total = len(linhas)
    linhas_vazias_consecutivas = 0
    ultimo_num = 0

    while i < total:
        texto = linhas[i].strip()

        # Ignorar linhas PJe (paginação) sem quebrar a seção
        if eh_linha_pje(texto):
            i += 1
            continue

        # Checar se é um novo cabeçalho de quesitos (nova seção)
        if texto and eh_novo_cabecalho_quesitos(texto):
            break

        # Checar fim de seção (assinatura, termos, etc.)
        if eh_fim_secao(texto):
            # Verificar se é só uma linha de paginação PJe no meio
            # Se for Conclusão ou Termo de encerramento, é fim definitivo
            break

        # Linha vazia
        if not texto:
            linhas_vazias_consecutivas += 1
            # Muitas linhas vazias seguidas = possível fim de seção
            if linhas_vazias_consecutivas >= 6:
                # Verificar se há mais quesitos à frente (em até 10 linhas)
                encontrou_mais = False
                for j in range(i + 1, min(i + 10, total)):
                    prox = linhas[j].strip()
                    if RE_QUESITO_NUM.match(prox):
                        encontrou_mais = True
                        break
                    if prox and not eh_linha_pje(prox):
                        break
                if not encontrou_mais:
                    break
            i += 1
            continue

        linhas_vazias_consecutivas = 0

        # Pular sub-seções (ex: "Quesitos sobre a Dinâmica do Acidente")
        # Elas são títulos internos e não devem ser incluídas como texto de quesito
        if RE_SUBSECAO_QUESITOS.match(texto):
            # Salvar quesito anterior antes de pular
            if quesito_atual:
                quesitos.append(" ".join(quesito_atual))
                quesito_atual = []
            i += 1
            continue

        # Tentar match de quesito numerado
        m = RE_QUESITO_NUM.match(texto)
        if m:
            # Salvar quesito anterior
            if quesito_atual:
                quesitos.append(" ".join(quesito_atual))
                quesito_atual = []
            num = int(m.group(1))
            # Se o número é sequencial ou razoável, é quesito
            if num <= ultimo_num + 5 or ultimo_num == 0:
                ultimo_num = num
                quesito_atual = [texto]
            else:
                # Número muito fora de sequência — pode ser outro conteúdo
                # Mas incluir mesmo assim (pode ser numeração não sequencial)
                quesito_atual = [texto]
            i += 1
            continue

        # Subquesito ou continuação
        if quesito_atual:
            # Linha de continuação
            quesito_atual.append(texto)
        else:
            # Texto sem quesito anterior e sem numeração — pode ser quesito sem número
            # Incluir se parece ser uma pergunta ou instrução
            if texto.endswith("?") or texto.startswith("Queira") or texto.startswith("Poderá"):
                quesito_atual = [texto]

        i += 1

    # Salvar último quesito
    if quesito_atual:
        quesitos.append(" ".join(quesito_atual))

    return quesitos, i


def detectar_contexto_generico(linhas: list[str], pos_cabecalho: int) -> Optional[str]:
    """Para cabeçalhos genéricos como 'QUESITOS MÉDICOS', tenta detectar quem formulou.

    Busca nas linhas anteriores indícios de autoria (petição de quem, advogado de quem).
    Usa janela maior para contextuais (até 60 linhas) e menor para genéricos (30 linhas).
    """
    inicio_busca = max(0, pos_cabecalho - 60)
    bloco = "\n".join(linhas[inicio_busca:pos_cabecalho])
    bloco_lower = bloco.lower()

    # Indicadores de réu (mais específicos primeiro)
    indicadores_reu = [
        "parte ré", "requerido", "requerida", "reclamado", "reclamada",
        "executado", "executada", "impetrado",
        "em defesa", "contestação", "contende com",
        "polo passivo",
    ]
    # Indicadores de autor (mais específicos primeiro)
    indicadores_autor = [
        "parte autora", "requerente", "reclamante", "exequente", "impetrante",
        "petição inicial", "polo ativo",
        "já devidamente qualificad",  # "já devidamente qualificada nos autos"
    ]

    # Contar indicadores de cada lado (mais robusto que primeiro match)
    score_reu = sum(1 for t in indicadores_reu if t in bloco_lower)
    score_autor = sum(1 for t in indicadores_autor if t in bloco_lower)

    if score_reu > score_autor:
        return "reu"
    if score_autor > score_reu:
        return "autor"

    # Empate ou zero: tentar com janela menor (últimas 15 linhas, mais próximas do cabeçalho)
    inicio_curto = max(0, pos_cabecalho - 15)
    bloco_curto = "\n".join(linhas[inicio_curto:pos_cabecalho]).lower()

    for t in indicadores_reu:
        if t in bloco_curto:
            return "reu"
    for t in indicadores_autor:
        if t in bloco_curto:
            return "autor"

    return None


def extrair_todos_quesitos(texto: str) -> dict:
    """Pipeline principal: extrai todos os quesitos do texto.

    Retorna dicionário com origens e quesitos.
    """
    linhas = texto.split("\n")
    total = len(linhas)
    cnj = extrair_cnj_do_texto(texto)

    origens = {
        "autor": {"quantidade": 0, "quesitos": [], "ausente": True},
        "reu": {"quantidade": 0, "quesitos": [], "ausente": True},
        "juizo": {"quantidade": 0, "quesitos": [], "ausente": True},
        "mp": {"quantidade": 0, "quesitos": [], "ausente": True},
        "litisconsorte": {"quantidade": 0, "quesitos": [], "ausente": True},
        "suplementares": {"quantidade": 0, "quesitos": [], "ausente": True},
    }

    i = 0
    secoes_encontradas = 0

    while i < total:
        resultado = classificar_origem(linhas[i])

        if resultado is None:
            i += 1
            continue

        origem, eh_generico = resultado
        secoes_encontradas += 1
        pos_cabecalho = i
        i += 1  # Avançar além do cabeçalho

        # Para cabeçalhos genéricos ou contextuais, tentar refinar pelo contexto
        if eh_generico or origem == "_contexto":
            ctx = detectar_contexto_generico(linhas, pos_cabecalho)
            if ctx:
                origem = ctx
            elif origem == "_contexto":
                # Não conseguiu determinar a origem — pular
                i += 1
                secoes_encontradas -= 1
                continue

        # Pular linhas vazias após cabeçalho
        while i < total and not linhas[i].strip():
            i += 1

        # Checar se é ausência
        motivo = eh_ausencia(linhas, i)
        if motivo:
            origens[origem]["ausente"] = True
            origens[origem]["motivo"] = motivo
            # Avançar além da linha de ausência
            while i < total and not linhas[i].strip():
                i += 1
            if i < total:
                i += 1  # Pular a linha de ausência em si
            continue

        # Extrair quesitos
        quesitos, prox = extrair_quesitos_secao(linhas, i)

        if quesitos:
            # Se já havia quesitos nessa origem (ex: quesitos do réu em dois documentos),
            # adicionar, não substituir
            origens[origem]["quesitos"].extend(quesitos)
            origens[origem]["quantidade"] = len(origens[origem]["quesitos"])
            origens[origem]["ausente"] = False
            if "motivo" in origens[origem]:
                del origens[origem]["motivo"]

        i = prox

    # Calcular total
    total_quesitos = sum(o["quantidade"] for o in origens.values())

    resultado = {
        "cnj": cnj,
        "total_quesitos": total_quesitos,
        "secoes_encontradas": secoes_encontradas,
        "origens": origens,
        "extraido_em": datetime.now().isoformat(),
        "script": "extrair_quesitos.py",
    }

    return resultado


# ═══════════════════════════════════════════════════════════════════════════════
# GERAÇÃO DE MARKDOWN
# ═══════════════════════════════════════════════════════════════════════════════

NOMES_ORIGEM = {
    "autor": "Parte Autora",
    "reu": "Parte Ré",
    "juizo": "Juízo",
    "mp": "Ministério Público",
    "litisconsorte": "Denunciado/Litisconsorte",
    "suplementares": "Quesitos Suplementares",
}


def gerar_markdown(dados: dict) -> str:
    """Gera quesitos.md a partir dos dados extraídos."""
    md = []
    cnj = dados.get("cnj", "")
    total = dados.get("total_quesitos", 0)

    md.append("# Quesitos do Processo\n")
    if cnj:
        md.append(f"**Processo:** {cnj}")
    md.append(f"**Total de quesitos:** {total}")
    md.append(f"**Seções identificadas:** {dados.get('secoes_encontradas', 0)}")
    md.append("")

    origens = dados.get("origens", {})
    for chave in ("autor", "reu", "juizo", "mp", "litisconsorte", "suplementares"):
        info = origens.get(chave, {})
        nome = NOMES_ORIGEM.get(chave, chave)

        md.append(f"## {nome}\n")

        if info.get("ausente", True):
            motivo = info.get("motivo", "Não identificado no texto")
            md.append(f"*{motivo}*\n")
            continue

        qtd = info.get("quantidade", 0)
        md.append(f"**Quantidade:** {qtd}\n")

        for idx, q in enumerate(info.get("quesitos", []), 1):
            md.append(f"{idx}. {q}")

        md.append("")

    # Resumo
    md.append("---")
    md.append(f"\n| Origem | Quantidade |")
    md.append(f"|--------|-----------|")
    for chave in ("autor", "reu", "juizo", "mp", "litisconsorte", "suplementares"):
        info = origens.get(chave, {})
        nome = NOMES_ORIGEM.get(chave, chave)
        qtd = info.get("quantidade", 0)
        status = f"{qtd}" if not info.get("ausente") else "Ausente"
        md.append(f"| {nome} | {status} |")
    md.append(f"| **TOTAL** | **{total}** |")
    md.append("")

    md.append(f"\n*Extraído em {dados.get('extraido_em', '')} por extrair_quesitos.py*")

    return "\n".join(md)


# ═══════════════════════════════════════════════════════════════════════════════
# SAÍDA NO TERMINAL
# ═══════════════════════════════════════════════════════════════════════════════

def imprimir_resumo(dados: dict, pasta: Path):
    """Imprime resumo formatado no terminal."""
    cnj = dados.get("cnj", "?")
    total = dados.get("total_quesitos", 0)
    secoes = dados.get("secoes_encontradas", 0)
    origens = dados.get("origens", {})

    print()
    print(f"{'=' * 60}")
    print(f"  {C.B}QUESITOS EXTRAÍDOS{C.R}")
    print(f"{'=' * 60}")
    if cnj:
        print(f"  CNJ: {cnj}")
    print(f"  Seções encontradas: {secoes}")
    print()

    for chave in ("autor", "reu", "juizo", "mp", "litisconsorte", "suplementares"):
        info = origens.get(chave, {})
        nome = NOMES_ORIGEM.get(chave, chave)
        qtd = info.get("quantidade", 0)
        ausente = info.get("ausente", True)

        if ausente:
            motivo = info.get("motivo", "")
            if motivo:
                print(f"  {nome:.<30s} {C.Y}Ausente{C.R} ({motivo})")
            else:
                print(f"  {nome:.<30s} {C.DIM}Não identificado{C.R}")
        else:
            print(f"  {nome:.<30s} {C.G}{qtd}{C.R} quesito(s)")

    print()
    if total > 0:
        print(f"  {C.B}TOTAL: {total} quesitos{C.R}")
    else:
        print(f"  {C.RE}Nenhum quesito encontrado no texto.{C.R}")

    print()
    print(f"  {C.DIM}Salvos em: {pasta}{C.R}")
    print(f"  {C.DIM}  → quesitos.json{C.R}")
    print(f"  {C.DIM}  → quesitos.md{C.R}")
    print(f"{'=' * 60}")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# FLUXO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Extrai quesitos de processos judiciais — Stemmia Forense",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python3 extrair_quesitos.py --cnj 5017700-42.2020.8.13.0105
  python3 extrair_quesitos.py --cnj 5015391-72
  python3 extrair_quesitos.py --arquivo ~/Desktop/ANALISADOR\\ FINAL/processos/Perícia\\ 31/TEXTO-EXTRAIDO.txt
  python3 extrair_quesitos.py /caminho/para/pasta/do/processo
        """,
    )
    parser.add_argument(
        "processo",
        nargs="?",
        help="Caminho da pasta do processo (alternativa ao --cnj)",
    )
    parser.add_argument(
        "--cnj",
        type=str,
        help="Número CNJ do processo (completo ou parcial)",
    )
    parser.add_argument(
        "--arquivo", "-a",
        type=str,
        help="Caminho direto para TEXTO-EXTRAIDO.txt",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Imprimir JSON no stdout e sair (sem salvar arquivos)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Pasta de saída (default: pasta do processo)",
    )

    args = parser.parse_args()

    arquivo = None
    pasta = None

    # ─── Resolver arquivo de entrada ──────────────────────────────────────
    if args.arquivo:
        arquivo = Path(args.arquivo).expanduser().resolve()
        pasta = arquivo.parent
        if not arquivo.exists():
            print(f"{C.RE}ERRO: Arquivo não encontrado: {arquivo}{C.R}")
            sys.exit(1)

    elif args.cnj:
        pasta = encontrar_pasta(args.cnj)
        if not pasta:
            print(f"{C.RE}ERRO: Processo não encontrado para CNJ '{args.cnj}' em {BASE}{C.R}")
            sys.exit(1)
        arquivo = encontrar_texto(pasta)
        if not arquivo:
            print(f"{C.RE}ERRO: TEXTO-EXTRAIDO.txt não encontrado em {pasta}{C.R}")
            sys.exit(1)

    elif args.processo:
        p = Path(args.processo).expanduser().resolve()
        if p.is_dir():
            pasta = p
            arquivo = encontrar_texto(pasta)
        elif p.is_file():
            arquivo = p
            pasta = p.parent
        else:
            # Tentar como CNJ
            pasta = encontrar_pasta(args.processo)
            if pasta:
                arquivo = encontrar_texto(pasta)

        if not arquivo or not arquivo.exists():
            print(f"{C.RE}ERRO: Não foi possível localizar o texto do processo '{args.processo}'{C.R}")
            sys.exit(1)

    else:
        # Verificar se há TEXTO-EXTRAIDO.txt no diretório atual
        local = Path.cwd() / "TEXTO-EXTRAIDO.txt"
        if local.exists():
            arquivo = local
            pasta = local.parent
        else:
            parser.print_help()
            print(f"\n{C.RE}ERRO: Informe --cnj, --arquivo ou passe a pasta do processo.{C.R}")
            sys.exit(1)

    # ─── Ler texto ────────────────────────────────────────────────────────
    print(f"  Arquivo: {arquivo.name} ({arquivo.stat().st_size // 1024} KB)")
    texto = arquivo.read_text(encoding="utf-8", errors="replace")

    # ─── Extrair quesitos ─────────────────────────────────────────────────
    dados = extrair_todos_quesitos(texto)

    # ─── Saída JSON no stdout ─────────────────────────────────────────────
    if args.json_only:
        print(json.dumps(dados, ensure_ascii=False, indent=2))
        sys.exit(0)

    # ─── Pasta de saída ───────────────────────────────────────────────────
    output_dir = Path(args.output).expanduser().resolve() if args.output else pasta
    output_dir.mkdir(parents=True, exist_ok=True)

    # ─── Salvar JSON ──────────────────────────────────────────────────────
    json_path = output_dir / "quesitos.json"
    json_path.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # ─── Salvar Markdown ──────────────────────────────────────────────────
    md_path = output_dir / "quesitos.md"
    md_path.write_text(gerar_markdown(dados), encoding="utf-8")

    # ─── Resumo no terminal ───────────────────────────────────────────────
    imprimir_resumo(dados, output_dir)


if __name__ == "__main__":
    main()
