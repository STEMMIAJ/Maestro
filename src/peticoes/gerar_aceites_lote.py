#!/usr/bin/env python3
"""
gerar_aceites_lote.py — Gera múltiplos aceites de uma vez
==========================================================
Autor: Jésus Eduardo Nolêto da Penha (CRM-MG 92.148)
Versão: 1.0 — 22/03/2026

USO:
    python3 gerar_aceites_lote.py --cnjs 5000123-45.2025.8.13.0680 5000456-78.2025.8.13.0680
    python3 gerar_aceites_lote.py --cnjs-arquivo lista.txt
    python3 gerar_aceites_lote.py --cnjs-arquivo lista.txt --pdf
    python3 gerar_aceites_lote.py --todos-pendentes
    python3 gerar_aceites_lote.py --comarca Taiobeiras

Gera aceite para cada processo usando FICHA.json.
Opcionalmente gera PDF com timbrado para todos.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple

BASE_PROCESSOS = Path.home() / "Desktop" / "ANALISADOR FINAL" / "analisador de processos" / "processos"
SCRIPTS_DIR = Path.home() / "Desktop" / "ANALISADOR FINAL" / "scripts"
GERAR_ACEITE = SCRIPTS_DIR / "gerar_aceite_rapido.py"


def listar_processos_sem_aceite() -> List[Tuple[str, Path]]:
    """Lista processos que têm FICHA.json mas não têm PETICAO-ACEITE.md."""
    pendentes = []
    for pasta in sorted(BASE_PROCESSOS.iterdir()):
        if not pasta.is_dir():
            continue
        ficha = pasta / "FICHA.json"
        aceite = pasta / "PETICAO-ACEITE.md"
        if ficha.exists() and not aceite.exists():
            try:
                with open(ficha, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                cnj = dados.get("numero_cnj", "")
                if cnj:
                    pendentes.append((cnj, pasta))
            except (json.JSONDecodeError, KeyError):
                continue
    return pendentes


def listar_processos_por_comarca(comarca: str) -> List[Tuple[str, Path]]:
    """Lista processos de uma comarca específica."""
    processos = []
    for pasta in sorted(BASE_PROCESSOS.iterdir()):
        if not pasta.is_dir():
            continue
        ficha = pasta / "FICHA.json"
        if ficha.exists():
            try:
                with open(ficha, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                cnj = dados.get("numero_cnj", "")
                com = dados.get("comarca", "")
                if cnj and comarca.lower() in com.lower():
                    processos.append((cnj, pasta))
            except (json.JSONDecodeError, KeyError):
                continue
    return processos


def gerar_aceite_individual(cnj: str, pdf: bool = False) -> bool:
    """Gera aceite para um processo individual."""
    cmd = ["python3", str(GERAR_ACEITE), cnj]
    if pdf:
        cmd.append("--pdf")

    resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if resultado.returncode == 0:
        return True
    else:
        print("  [ERRO] {}: {}".format(cnj, resultado.stderr.strip()), file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Gera múltiplos aceites de uma vez"
    )
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--cnjs", nargs="+", help="Lista de CNJs")
    grupo.add_argument("--cnjs-arquivo", help="Arquivo com CNJs (um por linha)")
    grupo.add_argument("--todos-pendentes", action="store_true",
                       help="Gerar para todos que têm FICHA mas não têm aceite")
    grupo.add_argument("--comarca", help="Gerar para todos de uma comarca")

    parser.add_argument("--pdf", action="store_true", help="Gerar PDF com timbrado")
    parser.add_argument("--listar", action="store_true",
                        help="Apenas listar, não gerar")

    args = parser.parse_args()

    # Coletar CNJs
    cnjs = []
    if args.cnjs:
        cnjs = args.cnjs
    elif args.cnjs_arquivo:
        with open(args.cnjs_arquivo, "r") as f:
            cnjs = [linha.strip() for linha in f if linha.strip()]
    elif args.todos_pendentes:
        pendentes = listar_processos_sem_aceite()
        if not pendentes:
            print("[INFO] Todos os processos já têm aceite!")
            return
        print("[INFO] {} processos sem aceite:".format(len(pendentes)))
        for cnj, pasta in pendentes:
            print("  {} — {}".format(cnj, pasta.name))
        if args.listar:
            return
        cnjs = [cnj for cnj, _ in pendentes]
    elif args.comarca:
        processos = listar_processos_por_comarca(args.comarca)
        if not processos:
            print("[INFO] Nenhum processo encontrado para comarca '{}'".format(args.comarca))
            return
        print("[INFO] {} processos em {}:".format(len(processos), args.comarca))
        for cnj, pasta in processos:
            print("  {} — {}".format(cnj, pasta.name))
        if args.listar:
            return
        cnjs = [cnj for cnj, _ in processos]

    if args.listar:
        return

    # Gerar aceites
    print("\n[INFO] Gerando {} aceites{}...".format(
        len(cnjs), " com PDF" if args.pdf else ""
    ))

    sucesso = 0
    falha = 0
    for i, cnj in enumerate(cnjs, 1):
        print("\n[{}/{}] {}".format(i, len(cnjs), cnj))
        if gerar_aceite_individual(cnj, args.pdf):
            sucesso += 1
        else:
            falha += 1

    # Resumo
    print()
    print("=" * 60)
    print("LOTE DE ACEITES — RESUMO")
    print("=" * 60)
    print("  Total:    {}".format(len(cnjs)))
    print("  Sucesso:  {}".format(sucesso))
    print("  Falha:    {}".format(falha))
    print("=" * 60)


if __name__ == "__main__":
    main()
