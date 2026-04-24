"""
ordenar_nomeacoes.py — Ordena nomeações por comarca (prioridade) e marca faltantes.

Prioridade de download (regra explícita do Dr. Jesus em 2026-04-20):
    1º Taiobeiras (0680)
    2º Governador Valadares (0105)
    3º Mantena (0396)
    4º Demais comarcas (ordem alfabética do código)

Reusa lógica de `conferir_nomeacoes.py` (mesmo diretório).

Saídas em consolidado/:
    NOMEACOES_ORDEM_TODAS_{data}.csv   (125 linhas: ordem, cnj, comarca, ja_tenho, locais)
    NOMEACOES_ORDEM_FALTAM_{data}.txt  (só faltantes, 1 por linha, pronto pro baixar_push_pje.py)

Uso:
    python3 ordenar_nomeacoes.py              # usa _input/ mais recente
    python3 ordenar_nomeacoes.py arquivo.md   # arquivo específico
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Importa do irmão (mesmo dir)
from conferir_nomeacoes import (
    CONSOLIDADO,
    HOME,
    INPUT_DIR,
    arquivo_mais_recente,
    extrair_cnjs,
    localizar,
)

# ─────────────────────────────────────────────
# Ordem de comarcas (editar aqui pra mudar prioridade)
# ─────────────────────────────────────────────
PRIORIDADE_COMARCAS: List[str] = ["0680", "0105", "0396"]

NOME_COMARCA: Dict[str, str] = {
    "0680": "Taiobeiras",
    "0105": "Governador Valadares",
    "0396": "Mantena",
    "0184": "Conselheiro Pena",
    "0309": "Inhapim",
    "0194": "Coronel Fabriciano",
    "0329": "Itamogi",
    "0362": "João Monlevade",
    "0231": "Ribeirão das Neves",
    "0702": "Uberlândia",
    "0005": "Açucena",
    "0024": "Belo Horizonte",
    "0042": "Arcos",
    "0059": "Barroso",
    "0074": "Bom Despacho",
    "0089": "Brazópolis",
    "0112": "Campo Belo",
    "0134": "Governador Valadares",  # subseção
    "0188": "Nova Lima",
    "0245": "Santa Luzia",
    "0461": "Lagoa da Prata",
    "0471": "Pará de Minas",
    "0627": "Taiobeiras (subseção)",
    "0694": "Três Pontas",
    "0701": "Uberaba",
}


def comarca_do(cnj: str) -> str:
    """Extrai o código de 4 dígitos da comarca (últimos 4)."""
    return cnj[-4:]


def chave_ordem(cnj: str) -> tuple:
    """
    Chave de ordenação. Menor tupla = vem primeiro.
    - índice na lista de prioridade (999 se não está na lista)
    - código da comarca (para demais, alfabético)
    - cnj (desempate)
    """
    c = comarca_do(cnj)
    if c in PRIORIDADE_COMARCAS:
        return (PRIORIDADE_COMARCAS.index(c), c, cnj)
    return (999, c, cnj)


def salvar_csv_todas(
    cnjs_ordenados: List[str],
    ja_tenho: Dict[str, List[str]],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ordem", "cnj", "comarca_codigo", "comarca_nome", "ja_tenho", "locais"])
        for i, cnj in enumerate(cnjs_ordenados, 1):
            cod = comarca_do(cnj)
            nome = NOME_COMARCA.get(cod, "?")
            presente = cnj in ja_tenho
            locais = " | ".join(ja_tenho.get(cnj, []))
            w.writerow([i, cnj, cod, nome, "S" if presente else "N", locais])


def salvar_txt_faltam(cnjs_ordenados: List[str], ja_tenho: Dict[str, List[str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    faltam = [c for c in cnjs_ordenados if c not in ja_tenho]
    path.write_text("\n".join(faltam) + ("\n" if faltam else ""), encoding="utf-8")


def main(argv: List[str]) -> int:
    if len(argv) > 1:
        entrada = Path(argv[1]).expanduser().resolve()
    else:
        entrada = arquivo_mais_recente()
        if not entrada:
            print(f"ERRO: nenhum arquivo em {INPUT_DIR}", file=sys.stderr)
            return 2

    if not entrada.exists():
        print(f"ERRO: não encontrado: {entrada}", file=sys.stderr)
        return 2

    print(f"[entrada]    {entrada.name}")
    texto = entrada.read_text(encoding="utf-8")
    cnjs = extrair_cnjs(texto)
    print(f"[CNJs únicos] {len(cnjs)}")

    if not cnjs:
        return 1

    ja_tenho, falta = localizar(cnjs)
    ordenados = sorted(cnjs, key=chave_ordem)

    data = datetime.now().strftime("%d%m%Y")
    csv_path = CONSOLIDADO / f"NOMEACOES_ORDEM_TODAS_{data}.csv"
    txt_path = CONSOLIDADO / f"NOMEACOES_ORDEM_FALTAM_{data}.txt"

    salvar_csv_todas(ordenados, ja_tenho, csv_path)
    salvar_txt_faltam(ordenados, ja_tenho, txt_path)

    # Resumo por comarca (na ordem de prioridade)
    por_comarca = Counter(comarca_do(c) for c in cnjs)
    falta_por_comarca = Counter(comarca_do(c) for c in falta)

    print()
    print("  ORDEM DE DOWNLOAD — por comarca:")
    ja_listadas = set()
    for cod in PRIORIDADE_COMARCAS:
        if cod in por_comarca:
            nome = NOME_COMARCA.get(cod, "?")
            print(f"    {cod} {nome:25s} total={por_comarca[cod]:3d}  falta={falta_por_comarca[cod]:3d}")
            ja_listadas.add(cod)
    # demais
    demais = sorted(cod for cod in por_comarca if cod not in ja_listadas)
    for cod in demais:
        nome = NOME_COMARCA.get(cod, "?")
        print(f"    {cod} {nome:25s} total={por_comarca[cod]:3d}  falta={falta_por_comarca[cod]:3d}")

    print()
    print(f"  Total      : {len(cnjs)}")
    print(f"  Já tenho   : {len(ja_tenho)}")
    print(f"  Faltam     : {len(falta)}")
    print()
    print(f"[csv ok]  {csv_path.relative_to(HOME)}")
    print(f"[txt ok]  {txt_path.relative_to(HOME)}")

    if falta:
        print()
        print("FALTAM BAIXAR (na ordem de prioridade):")
        faltam_ord = [c for c in ordenados if c not in ja_tenho]
        for c in faltam_ord:
            cod = comarca_do(c)
            nome = NOME_COMARCA.get(cod, "?")
            print(f"  {c}   ({cod} {nome})")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
