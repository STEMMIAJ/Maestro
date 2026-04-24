#!/usr/bin/env python3
"""
Comparador de Versões de PDFs — Stemmia Forense
Compara hashes MD5 de PDFs em processos/, detecta mudanças e versiona.

Uso:
  python3 comparar_versoes.py                # Varredura completa
  python3 comparar_versoes.py --cnj XXXXXXX  # Verifica 1 processo
  python3 comparar_versoes.py --json         # Saída JSON
  python3 comparar_versoes.py --relatorio    # Lista todas as versões
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(os.path.expanduser("~/Desktop/ANALISADOR FINAL"))
PROCESSOS_DIR = BASE_DIR / "processos"
HASHES_FILE = BASE_DIR / "scripts" / "_hashes_pdfs.json"


def md5_arquivo(caminho):
    """Calcula MD5 de um arquivo."""
    h = hashlib.md5()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(8192), b""):
            h.update(bloco)
    return h.hexdigest()


def carregar_hashes():
    """Carrega registro de hashes anteriores."""
    if HASHES_FILE.exists():
        try:
            return json.loads(HASHES_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def salvar_hashes(hashes):
    """Salva registro de hashes."""
    HASHES_FILE.write_text(
        json.dumps(hashes, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def ler_ficha(pasta):
    """Lê FICHA.json de uma pasta."""
    ficha_path = Path(pasta) / "FICHA.json"
    if ficha_path.exists():
        try:
            return json.loads(ficha_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def salvar_ficha(pasta, ficha):
    """Salva FICHA.json."""
    ficha_path = Path(pasta) / "FICHA.json"
    ficha_path.write_text(
        json.dumps(ficha, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def comparar_processo(pasta, hashes_anteriores):
    """Compara PDFs de um processo com hashes salvos."""
    resultado = {
        "pasta": str(pasta),
        "cnj": "",
        "mudancas": [],
        "versoes": []
    }

    ficha = ler_ficha(pasta)
    cnj_match = re.search(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", pasta.name)
    cnj = ficha.get("cnj") or (cnj_match.group(0) if cnj_match else pasta.name)
    resultado["cnj"] = cnj

    # Verificar todos os PDFs
    for pdf in sorted(pasta.glob("*.pdf")):
        hash_atual = md5_arquivo(str(pdf))
        chave = f"{cnj}:{pdf.name}"
        hash_anterior = hashes_anteriores.get(chave, {}).get("hash", "")

        if hash_anterior and hash_anterior != hash_atual:
            # PDF mudou — versionar
            data_anterior = datetime.fromtimestamp(pdf.stat().st_mtime)
            backup_nome = f"{pdf.stem}-{data_anterior.strftime('%Y-%m-%d')}{pdf.suffix}"
            backup_path = pasta / backup_nome

            # Não sobrescrever backup existente
            if not backup_path.exists():
                try:
                    shutil.copy2(str(pdf), str(backup_path))
                except Exception:
                    pass

            resultado["mudancas"].append({
                "arquivo": pdf.name,
                "hash_anterior": hash_anterior,
                "hash_atual": hash_atual,
                "tamanho_mb": round(pdf.stat().st_size / 1048576, 1),
                "backup": backup_nome
            })

            # Registrar versão na FICHA
            versoes = ficha.get("versoes", [])
            versoes.append({
                "data": datetime.now().isoformat(),
                "hash": hash_atual,
                "hash_anterior": hash_anterior,
                "tamanho_mb": round(pdf.stat().st_size / 1048576, 1),
                "arquivo": pdf.name
            })
            ficha["versoes"] = versoes
            salvar_ficha(pasta, ficha)

        # Atualizar registro de hash
        hashes_anteriores[chave] = {
            "hash": hash_atual,
            "tamanho": pdf.stat().st_size,
            "data_verificacao": datetime.now().isoformat()
        }

    # Listar versões existentes
    resultado["versoes"] = ficha.get("versoes", [])

    return resultado


def main():
    parser = argparse.ArgumentParser(description="Comparador de Versões de PDFs")
    parser.add_argument("--cnj", help="CNJ específico para verificar")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    parser.add_argument("--relatorio", action="store_true", help="Lista todas as versões")

    args = parser.parse_args()
    hashes = carregar_hashes()
    resultados = []

    if not PROCESSOS_DIR.is_dir():
        print("Pasta processos/ não encontrada", file=sys.stderr)
        sys.exit(1)

    for pasta in sorted(PROCESSOS_DIR.iterdir()):
        if not pasta.is_dir() or pasta.name.startswith("."):
            continue

        # Filtrar por CNJ se especificado
        if args.cnj and args.cnj not in pasta.name:
            continue

        # Só processar pastas com PDF
        if not any(pasta.glob("*.pdf")):
            continue

        r = comparar_processo(pasta, hashes)
        if args.relatorio or r["mudancas"]:
            resultados.append(r)

    salvar_hashes(hashes)

    if args.json:
        saida = {
            "data": datetime.now().isoformat(),
            "total_verificados": len(resultados),
            "total_mudancas": sum(len(r["mudancas"]) for r in resultados),
            "processos": resultados
        }
        print(json.dumps(saida, indent=2, ensure_ascii=False))
    else:
        mudancas = [r for r in resultados if r["mudancas"]]
        if mudancas:
            print(f"\n{'='*60}")
            print(f"MUDANÇAS DETECTADAS: {len(mudancas)} processos")
            print(f"{'='*60}")
            for r in mudancas:
                print(f"\n  {r['cnj']}:")
                for m in r["mudancas"]:
                    print(f"    ↻ {m['arquivo']} ({m['tamanho_mb']} MB)")
                    print(f"      Backup: {m['backup']}")
        else:
            print("Nenhuma mudança detectada.")

        if args.relatorio:
            versionados = [r for r in resultados if r["versoes"]]
            if versionados:
                print(f"\n{'='*60}")
                print(f"PROCESSOS COM VERSÕES: {len(versionados)}")
                print(f"{'='*60}")
                for r in versionados:
                    print(f"\n  {r['cnj']}: {len(r['versoes'])} versões")
                    for v in r["versoes"]:
                        print(f"    - {v.get('data', '?')[:10]} | {v.get('tamanho_mb', '?')} MB")


if __name__ == "__main__":
    main()
