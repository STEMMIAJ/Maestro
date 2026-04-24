#!/usr/bin/env python3
"""
migrar_taiobeiras.py — Move os PDFs Taiobeiras flat para Taiobeiras/Vara Única/

Contexto: sessao 2026-04-23. Pasta "Processos Atualizados/Taiobeiras/" tinha
24 PDFs jogados na raiz, sem subpasta. O novo script baixar_e_organizar.py
salva em Comarca/VaraCurta/, entao precisamos alinhar o historico com o novo layout.

Roda NO MAC. Uso:
    python3 migrar_taiobeiras.py --dry-run   # so mostra o que faria
    python3 migrar_taiobeiras.py             # executa
"""

from __future__ import annotations
import argparse
import re
import shutil
import sys
from pathlib import Path

PASTA_TAIOBEIRAS = (
    Path.home()
    / "Desktop"
    / "STEMMIA Dexter"
    / "Processos Atualizados"
    / "Taiobeiras"
)
SUBPASTA_DESTINO = PASTA_TAIOBEIRAS / "Vara Única"

# CNJ do TJMG (validacao simples)
CNJ_RE = re.compile(r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")


def coletar_pdfs_flat() -> list[Path]:
    """Retorna PDFs que estao direto em Taiobeiras/ (nao em subpasta)."""
    if not PASTA_TAIOBEIRAS.exists():
        print(f"ERRO: pasta nao existe: {PASTA_TAIOBEIRAS}")
        sys.exit(1)
    pdfs: list[Path] = []
    for p in PASTA_TAIOBEIRAS.iterdir():
        if p.is_file() and p.suffix.lower() == ".pdf":
            # aceita tanto "<CNJ>..." quanto "<CNJ> - Taiobeiras - Vara Unica..."
            if CNJ_RE.match(p.name):
                pdfs.append(p)
    return sorted(pdfs)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="apenas mostra as acoes")
    args = ap.parse_args()

    pdfs = coletar_pdfs_flat()
    print(f"\nEncontrados {len(pdfs)} PDFs flat em {PASTA_TAIOBEIRAS.name}/\n")

    if not pdfs:
        print("Nada a migrar — ja esta organizado.")
        return 0

    if not args.dry_run:
        SUBPASTA_DESTINO.mkdir(parents=True, exist_ok=True)

    movidos = 0
    pulados = 0
    erros = 0

    for pdf in pdfs:
        destino = SUBPASTA_DESTINO / pdf.name
        if destino.exists():
            print(f"  [PULA] ja existe no destino: {pdf.name}")
            pulados += 1
            continue
        print(f"  [MOVE] {pdf.name}")
        if args.dry_run:
            continue
        try:
            shutil.move(str(pdf), str(destino))
            movidos += 1
        except Exception as e:
            print(f"         ERRO: {e}")
            erros += 1

    print()
    print("=" * 60)
    if args.dry_run:
        print(f"  DRY-RUN — rode sem --dry-run para executar")
        print(f"  Seriam movidos: {len(pdfs) - pulados}")
    else:
        print(f"  Movidos: {movidos}  |  Pulados: {pulados}  |  Erros: {erros}")
    print(f"  Destino: {SUBPASTA_DESTINO}")
    print("=" * 60)
    return 0 if erros == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
