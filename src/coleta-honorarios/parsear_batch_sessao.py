#!/usr/bin/env python3
"""Parsea TODOS os HTMLs brutos de uma sessao do v3 em batch.

Uso:
  python3 parsear_batch_sessao.py 20260421-0540
  python3 parsear_batch_sessao.py 20260421-0540 --apenas-slug Muriae

Le _raw_html/<ts_sessao>_*.html, chama parsear_resultados_tjmg.main por baixo.
Imprime resumo agregado.
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "_raw_html"
PARSER = BASE_DIR / "parsear_resultados_tjmg.py"


def slug_para_busca(slug: str) -> str:
    mapa = {
        "muriae": "honorarios periciais medico Muriae",
        "uberlandia": "honorarios periciais medico Uberlandia",
        "belo-horizonte": "honorarios pericia medica Belo Horizonte",
        "montes-claros": "honorarios periciais medico Montes Claros",
    }
    return mapa.get(slug.lower(), f"honorarios periciais medico {slug}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ts_sessao", help="Timestamp da sessao v3, ex: 20260421-0540")
    ap.add_argument("--apenas-slug", default=None)
    args = ap.parse_args()

    padrao = f"{args.ts_sessao}_*.html"
    htmls = sorted(RAW_DIR.glob(padrao))
    if not htmls:
        print(f"[batch] nenhum HTML em {RAW_DIR} com padrao {padrao}")
        sys.exit(1)

    print(f"[batch] {len(htmls)} HTMLs encontrados")
    for h in htmls:
        print(f"  - {h.name} ({h.stat().st_size} bytes)")

    for h in htmls:
        slug = h.stem.replace(f"{args.ts_sessao}_", "")
        if args.apenas_slug and slug.lower() != args.apenas_slug.lower():
            continue
        busca = slug_para_busca(slug)
        print(f"\n[batch] parseando {h.name} (busca={busca})")
        result = subprocess.run(
            [sys.executable, str(PARSER), str(h), "--busca", busca],
            cwd=str(BASE_DIR.parent.parent),
        )
        if result.returncode != 0:
            print(f"  [erro] parser retornou {result.returncode}")


if __name__ == "__main__":
    main()
