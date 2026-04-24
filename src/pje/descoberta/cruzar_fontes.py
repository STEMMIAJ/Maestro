"""
cruzar_fontes.py — Cruza 3 fontes: PJe Push + AJ/AJG + downloads locais.

Entradas:
    _input/pje-push-*.md          (lista do PJe Push, 141 CNJs em 2026-04-20)
    _input/nomeacoes-*.md         (lista AJ + AJG, 125 CNJs em 2026-04-19)

Saídas em consolidado/:
    CONSOLIDADO_FONTES_{data}.csv        (cnj, em_pje, em_aj_ajg, baixado, comarca, acao)
    FALTA_CADASTRAR_PUSH_{data}.txt      (só no AJ/AJG → precisa entrar no Push)
    FALTA_BAIXAR_{data}.txt              (em qualquer fonte + não baixado, na ordem Taiobeiras→GV→Mantena→outras)

Observação: alguns CNJs do Push vêm truncados (6 dígitos na 1ª parte em vez de 7).
O normalizador_flex aceita 19 dígitos e pad-zero no começo — sem isso, 4 CNJs do PJe
virariam "inválidos" e o cruzamento ficaria errado.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

from conferir_nomeacoes import CONSOLIDADO, HOME, INPUT_DIR, localizar
from ordenar_nomeacoes import NOME_COMARCA, PRIORIDADE_COMARCAS, chave_ordem, comarca_do

# ─────────────────────────────────────────────
# Regex flex (aceita 6-7 dígitos antes do hífen para cobrir truncamentos do Push)
# ─────────────────────────────────────────────
RE_CNJ_FMT_FLEX = re.compile(r"\d{6,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")
RE_CNJ_CRU = re.compile(r"\b\d{20}\b")


def _formatar(d20: str) -> str:
    return f"{d20[:7]}-{d20[7:9]}.{d20[9:13]}.{d20[13]}.{d20[14:16]}.{d20[16:20]}"


def normalizar20(s: str) -> str | None:
    """Normaliza CNJ com exatamente 20 dígitos."""
    d = "".join(c for c in s if c.isdigit())
    return _formatar(d) if len(d) == 20 else None


def _variantes19(d19: str) -> List[str]:
    """
    Para CNJ com 19 dígitos (truncado no Push), gera as 7 variantes possíveis
    inserindo '0' em cada posição do número sequencial (primeiros 6/7 dígitos).
    Mantém intactas as partes fixas (ano, J, TR, comarca = últimos 11 dígitos).
    """
    if len(d19) != 19:
        return []
    seq = d19[:6]      # 6 dígitos do número sequencial
    resto = d19[6:]    # 13 dígitos: 2 dv + 4 ano + 1 J + 2 TR + 4 OOOO
    variantes = []
    for i in range(7):
        # insere '0' na posição i do sequencial (7 opções total, i=0..6)
        novo_seq = seq[:i] + "0" + seq[i:]
        variantes.append(_formatar(novo_seq + resto))
    return variantes


def extrair(texto: str, referencia: Set[str] | None = None) -> Set[str]:
    """
    Extrai CNJs únicos. Se houver 19 dígitos (truncamento comum do Push),
    tenta as 7 variantes de insert-zero no sequencial — escolhe a que está
    na 'referencia' (outra fonte já normalizada). Se nenhuma bater, usa a
    variante padrão (zero na posição 0 do sequencial, i.e. pad-left).
    """
    out: Set[str] = set()
    ref = referencia or set()

    # Regex único cobre 19 e 20 dígitos
    for m in RE_CNJ_FMT_FLEX.finditer(texto):
        d = "".join(c for c in m.group() if c.isdigit())
        if len(d) == 20:
            out.add(_formatar(d))
        elif len(d) == 19:
            variantes = _variantes19(d)
            escolhida = next((v for v in variantes if v in ref), variantes[0])
            out.add(escolhida)

    for m in RE_CNJ_CRU.finditer(texto):
        d = m.group()
        if len(d) == 20:
            out.add(_formatar(d))

    return out


def achar_mais_recente(prefixo: str) -> Path | None:
    if not INPUT_DIR.exists():
        return None
    cand = sorted(INPUT_DIR.glob(f"{prefixo}*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return cand[0] if cand else None


def acao_recomendada(em_pje: bool, em_ajajg: bool, baixado: bool) -> str:
    if baixado:
        return "OK_BAIXADO"
    if em_pje:
        return "BAIXAR"  # já está no Push, só precisa baixar PDF
    # Só no AJ/AJG = precisa cadastrar no Push antes pra receber intimação
    return "CADASTRAR_PUSH"


def main() -> int:
    arq_pje = achar_mais_recente("pje-push-")
    arq_aj = achar_mais_recente("nomeacoes-")

    if not arq_pje:
        print("ERRO: _input/pje-push-*.md não encontrado", file=sys.stderr)
        return 2
    if not arq_aj:
        print("ERRO: _input/nomeacoes-*.md não encontrado", file=sys.stderr)
        return 2

    print(f"[PJe Push]   {arq_pje.name}")
    print(f"[AJ/AJG ]   {arq_aj.name}")

    # AJ/AJG primeiro (fonte "limpa", só 20 dígitos) — vira referência para resolver truncamentos do Push
    cnjs_aj = extrair(arq_aj.read_text(encoding="utf-8"))
    cnjs_pje = extrair(arq_pje.read_text(encoding="utf-8"), referencia=cnjs_aj)

    todos = sorted(cnjs_pje | cnjs_aj, key=chave_ordem)

    ja_tenho, _ = localizar(todos)
    baixados = set(ja_tenho.keys())

    # Conjuntos
    so_pje = cnjs_pje - cnjs_aj
    so_aj = cnjs_aj - cnjs_pje
    ambas = cnjs_pje & cnjs_aj

    # CSV consolidado
    data = datetime.now().strftime("%d%m%Y")
    csv_path = CONSOLIDADO / f"CONSOLIDADO_FONTES_{data}.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ordem", "cnj", "comarca_cod", "comarca_nome", "em_pje", "em_aj_ajg", "baixado", "acao"])
        for i, cnj in enumerate(todos, 1):
            cod = comarca_do(cnj)
            nome = NOME_COMARCA.get(cod, "?")
            em_pje = cnj in cnjs_pje
            em_aj = cnj in cnjs_aj
            baix = cnj in baixados
            w.writerow([
                i, cnj, cod, nome,
                "S" if em_pje else "N",
                "S" if em_aj else "N",
                "S" if baix else "N",
                acao_recomendada(em_pje, em_aj, baix),
            ])

    # TXT: só AJ (precisa cadastrar no Push)
    falta_push = sorted(so_aj, key=chave_ordem)
    txt_push = CONSOLIDADO / f"FALTA_CADASTRAR_PUSH_{data}.txt"
    txt_push.write_text("\n".join(falta_push) + ("\n" if falta_push else ""), encoding="utf-8")

    # TXT: tudo que precisa baixar (qualquer fonte, não baixado)
    falta_baix = sorted([c for c in todos if c not in baixados], key=chave_ordem)
    txt_baix = CONSOLIDADO / f"FALTA_BAIXAR_{data}.txt"
    txt_baix.write_text("\n".join(falta_baix) + ("\n" if falta_baix else ""), encoding="utf-8")

    # ─────── RELATÓRIO ───────
    print()
    print("═" * 60)
    print(" TOTAIS POR FONTE")
    print("═" * 60)
    print(f"  PJe Push         : {len(cnjs_pje):4d} CNJs únicos")
    print(f"  AJ + AJG         : {len(cnjs_aj):4d} CNJs únicos")
    print(f"  UNIÃO (tudo)     : {len(todos):4d} CNJs únicos")
    print()
    print(f"  Em ambas fontes  : {len(ambas):4d}")
    print(f"  Só no PJe Push   : {len(so_pje):4d}  ← recebo intimação mas não foi nomeação formal")
    print(f"  Só no AJ/AJG     : {len(so_aj):4d}  ← FALTA CADASTRAR NO PUSH")
    print()
    print(f"  Baixados local   : {len(baixados):4d}")
    print(f"  FALTA BAIXAR     : {len(falta_baix):4d}")
    print()

    # Taiobeiras total na união
    tai_pje = sum(1 for c in cnjs_pje if comarca_do(c) in ("0680", "0627"))
    tai_aj = sum(1 for c in cnjs_aj if comarca_do(c) in ("0680", "0627"))
    tai_uniao = sum(1 for c in todos if comarca_do(c) in ("0680", "0627"))
    print(f"  Taiobeiras PJe   : {tai_pje}")
    print(f"  Taiobeiras AJ    : {tai_aj}")
    print(f"  Taiobeiras UNIÃO : {tai_uniao}")
    print()

    # Por comarca (união, ordenada pela prioridade)
    print("═" * 60)
    print(" POR COMARCA (união das 2 fontes)")
    print("═" * 60)
    por_comarca = Counter(comarca_do(c) for c in todos)
    falta_por_comarca = Counter(comarca_do(c) for c in falta_baix)
    vistas = set()
    for cod in PRIORIDADE_COMARCAS:
        if cod in por_comarca:
            print(f"  {cod} {NOME_COMARCA.get(cod, '?'):28s} total={por_comarca[cod]:3d}  falta={falta_por_comarca[cod]:3d}")
            vistas.add(cod)
    for cod in sorted(c for c in por_comarca if c not in vistas):
        print(f"  {cod} {NOME_COMARCA.get(cod, '?'):28s} total={por_comarca[cod]:3d}  falta={falta_por_comarca[cod]:3d}")

    print()
    print("═" * 60)
    print(" ARQUIVOS GERADOS")
    print("═" * 60)
    print(f"  {csv_path.relative_to(HOME)}")
    print(f"  {txt_push.relative_to(HOME)}  ({len(falta_push)} CNJs)")
    print(f"  {txt_baix.relative_to(HOME)}  ({len(falta_baix)} CNJs)")

    if falta_push:
        print()
        print("SÓ NO AJ/AJG (cadastrar no Push pra receber intimação):")
        for c in falta_push[:20]:
            print(f"  {c}   ({comarca_do(c)} {NOME_COMARCA.get(comarca_do(c), '?')})")
        if len(falta_push) > 20:
            print(f"  ... +{len(falta_push) - 20}")

    if falta_baix:
        print()
        print("FALTA BAIXAR (ordem Taiobeiras → GV → Mantena → outras):")
        for c in falta_baix[:20]:
            print(f"  {c}   ({comarca_do(c)} {NOME_COMARCA.get(comarca_do(c), '?')})")
        if len(falta_baix) > 20:
            print(f"  ... +{len(falta_baix) - 20}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
