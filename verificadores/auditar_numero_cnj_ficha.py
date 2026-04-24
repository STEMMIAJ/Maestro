#!/usr/bin/env python3
"""
auditar_numero_cnj_ficha.py — Onda 2.5 do Maestro.

Varre todas as pastas de processo em ~/Desktop/ANALISADOR FINAL/processos/
que tenham FICHA.json, compara o numero_cnj da FICHA com o CNJ extraído
do nome da pasta e reporta discrepâncias.

Uso:
    python3 auditar_numero_cnj_ficha.py [--fix] [--processos <pasta>]

Flags:
    --fix       corrige automaticamente o numero_cnj na FICHA.json
    --processos pasta raiz (default: ~/Desktop/ANALISADOR FINAL/processos)

Exit code:
    0   sem discrepâncias
    1   discrepâncias encontradas (sem --fix) ou corrigidas (com --fix)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CNJ_PASTA_RE = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")
PROCESSOS_DEFAULT = Path.home() / "Desktop" / "ANALISADOR FINAL" / "processos"


def extrair_cnj_da_pasta(pasta: Path) -> str | None:
    m = CNJ_PASTA_RE.search(pasta.name)
    return m.group(0) if m else None


def auditar(processos_root: Path, fix: bool) -> int:
    """Retorna número de discrepâncias encontradas."""
    fichas = sorted(processos_root.glob("*/FICHA.json"))
    if not fichas:
        print(f"Nenhuma FICHA.json encontrada em {processos_root}")
        return 0

    discrepancias = 0
    for ficha_path in fichas:
        pasta = ficha_path.parent
        cnj_pasta = extrair_cnj_da_pasta(pasta)
        if not cnj_pasta:
            print(f"[SKIP] {pasta.name} — sem CNJ no nome da pasta")
            continue

        try:
            ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"[ERRO] {ficha_path}: {e}")
            continue

        cnj_ficha = ficha.get("numero_cnj", "").strip()

        if cnj_ficha == cnj_pasta:
            print(f"[OK]   {cnj_pasta}")
            continue

        discrepancias += 1
        if not fix:
            print(
                f"[BUG]  Pasta:  {cnj_pasta}\n"
                f"       FICHA:  {cnj_ficha or '(vazio)'}\n"
                f"       Arquivo: {ficha_path}"
            )
        else:
            ficha["numero_cnj"] = cnj_pasta
            ficha_path.write_text(
                json.dumps(ficha, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(
                f"[FIX]  {cnj_pasta} <- era '{cnj_ficha or '(vazio)'}'"
                f"\n       {ficha_path}"
            )

    print(f"\nTotal FICHA.json: {len(fichas)} | Discrepâncias: {discrepancias}")
    return discrepancias


def main() -> None:
    ap = argparse.ArgumentParser(description="Auditar numero_cnj nas FICHAs dos processos")
    ap.add_argument(
        "--processos",
        default=str(PROCESSOS_DEFAULT),
        help=f"Pasta raiz dos processos (default: {PROCESSOS_DEFAULT})",
    )
    ap.add_argument(
        "--fix",
        action="store_true",
        help="Corrigir automaticamente o numero_cnj divergente",
    )
    args = ap.parse_args()

    processos_root = Path(args.processos).expanduser().resolve()
    if not processos_root.is_dir():
        print(f"Pasta nao encontrada: {processos_root}", file=sys.stderr)
        sys.exit(2)

    n = auditar(processos_root, fix=args.fix)
    sys.exit(1 if n > 0 else 0)


if __name__ == "__main__":
    main()
