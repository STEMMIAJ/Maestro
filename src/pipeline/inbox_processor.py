#!/usr/bin/env python3
"""
inbox_processor.py — Processador Automático de INBOX
Detecta PDFs na INBOX, extrai CNJ, cria pasta, extrai texto, roda pipeline.

Uso:
    python3 inbox_processor.py              # Processa todos os PDFs da INBOX
    python3 inbox_processor.py --dry-run    # Mostra o que faria sem executar
    python3 inbox_processor.py --json       # Saída JSON
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(os.path.expanduser("~/Desktop/ANALISADOR FINAL"))
INBOX_DIR = BASE_DIR / "INBOX"
PROCESSOS_DIR = BASE_DIR / "processos"
SCRIPTS_DIR = BASE_DIR / "scripts"

CNJ_PATTERN = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')


def extrair_cnj_do_nome(nome):
    """Extrai CNJ do nome do arquivo."""
    match = CNJ_PATTERN.search(nome)
    return match.group(0) if match else None


def extrair_cnj_do_conteudo(pdf_path):
    """Extrai CNJ das primeiras páginas do PDF."""
    try:
        result = subprocess.run(
            ["pdftotext", "-l", "3", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            match = CNJ_PATTERN.search(result.stdout)
            if match:
                return match.group(0)
    except (subprocess.TimeoutExpired, OSError):
        pass
    return None


def criar_pasta_processo(cnj):
    """Cria pasta do processo se não existir."""
    pasta = PROCESSOS_DIR / cnj
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def extrair_texto(pdf_path, pasta_destino):
    """Extrai texto completo do PDF."""
    txt_path = pasta_destino / "TEXTO-EXTRAIDO.txt"

    try:
        # Verificar tamanho
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True, text=True, timeout=10,
        )
        paginas = 0
        for line in result.stdout.splitlines():
            if line.startswith("Pages:"):
                paginas = int(line.split(":")[1].strip())

        # Extrair texto
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), str(txt_path)],
            capture_output=True, text=True, timeout=120,
        )

        if result.returncode == 0 and txt_path.exists():
            tamanho = txt_path.stat().st_size
            return {"ok": True, "paginas": paginas, "tamanho_txt": tamanho}

    except (subprocess.TimeoutExpired, OSError) as e:
        return {"ok": False, "erro": str(e)}

    return {"ok": False, "erro": "pdftotext falhou"}


def rodar_pipeline(pasta):
    """Roda pipeline_analise.py no processo."""
    pipeline_script = SCRIPTS_DIR / "pipeline_analise.py"
    if not pipeline_script.exists():
        return {"ok": False, "erro": "pipeline_analise.py não encontrado"}

    try:
        result = subprocess.run(
            [sys.executable, str(pipeline_script), str(pasta), "--silencioso"],
            capture_output=True, text=True, timeout=120,
        )
        return {"ok": result.returncode == 0, "saida": result.stdout[-200:]}
    except (subprocess.TimeoutExpired, OSError) as e:
        return {"ok": False, "erro": str(e)}


def atualizar_status():
    """Atualiza STATUS-PROCESSOS.json."""
    scanner = SCRIPTS_DIR / "scanner_processos.py"
    if scanner.exists():
        try:
            subprocess.run(
                [sys.executable, str(scanner), "--json-only"],
                capture_output=True, timeout=30,
            )
        except (subprocess.TimeoutExpired, OSError):
            pass


def processar_inbox(dry_run=False):
    """Processa todos os PDFs da INBOX."""
    if not INBOX_DIR.exists():
        INBOX_DIR.mkdir(parents=True, exist_ok=True)
        return []

    resultados = []
    pdfs = [f for f in INBOX_DIR.iterdir() if f.suffix.lower() == ".pdf" and not f.name.startswith('.')]

    if not pdfs:
        return []

    for pdf in sorted(pdfs):
        registro = {
            "arquivo": pdf.name,
            "cnj": None,
            "pasta_criada": None,
            "texto_extraido": False,
            "pipeline": False,
            "erro": None,
        }

        # 1. Extrair CNJ
        cnj = extrair_cnj_do_nome(pdf.name)
        if not cnj:
            cnj = extrair_cnj_do_conteudo(pdf)
        if not cnj:
            registro["erro"] = "CNJ não encontrado no nome nem no conteúdo"
            resultados.append(registro)
            continue

        registro["cnj"] = cnj

        if dry_run:
            registro["pasta_criada"] = str(PROCESSOS_DIR / cnj)
            registro["texto_extraido"] = True
            registro["pipeline"] = True
            resultados.append(registro)
            continue

        # 2. Criar pasta
        pasta = criar_pasta_processo(cnj)
        registro["pasta_criada"] = str(pasta)

        # 3. Mover PDF
        pdf_destino = pasta / f"PROCESSO-ORIGINAL.pdf"
        if not pdf_destino.exists():
            shutil.copy2(str(pdf), str(pdf_destino))

        # 4. Extrair texto
        txt_result = extrair_texto(pdf_destino, pasta)
        registro["texto_extraido"] = txt_result.get("ok", False)

        if not registro["texto_extraido"]:
            registro["erro"] = txt_result.get("erro", "Falha na extração")
            resultados.append(registro)
            continue

        # 5. Rodar pipeline
        pipe_result = rodar_pipeline(pasta)
        registro["pipeline"] = pipe_result.get("ok", False)

        # 6. Mover PDF da INBOX para processados (manter cópia na INBOX/processados/)
        processados_dir = INBOX_DIR / "processados"
        processados_dir.mkdir(exist_ok=True)
        try:
            shutil.move(str(pdf), str(processados_dir / pdf.name))
        except OSError:
            pass

        resultados.append(registro)

    # 7. Atualizar STATUS-PROCESSOS.json
    if not dry_run and any(r["texto_extraido"] for r in resultados):
        atualizar_status()

    return resultados


def formato_terminal(resultados):
    """Formata para terminal."""
    if not resultados:
        print("INBOX vazia — nenhum PDF para processar.")
        return

    print("=" * 60)
    print("INBOX PROCESSOR — STEMMIA FORENSE")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)

    for r in resultados:
        status = "OK" if r["pipeline"] else "PARCIAL" if r["texto_extraido"] else "ERRO"
        icone = {"OK": "✅", "PARCIAL": "⚠️", "ERRO": "❌"}.get(status, "")
        print(f"\n  {icone} {r['arquivo']}")
        if r["cnj"]:
            print(f"    CNJ: {r['cnj']}")
        if r["pasta_criada"]:
            print(f"    Pasta: {r['pasta_criada']}")
        if r["erro"]:
            print(f"    Erro: {r['erro']}")

    ok = sum(1 for r in resultados if r["pipeline"])
    print(f"\nTotal: {len(resultados)} PDFs | {ok} processados com sucesso")


def formato_telegram(resultados):
    """Formata para Telegram."""
    if not resultados:
        print("INBOX vazia.")
        return

    linhas = [f"*INBOX:* {len(resultados)} PDF(s) processados\n"]
    for r in resultados:
        emoji = "✅" if r["pipeline"] else "⚠️" if r["texto_extraido"] else "❌"
        cnj_short = r["cnj"][:20] if r["cnj"] else "sem CNJ"
        linhas.append(f"{emoji} {cnj_short}")

    ok = sum(1 for r in resultados if r["pipeline"])
    linhas.append(f"\n{ok}/{len(resultados)} processados OK")
    print("\n".join(linhas))


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv

    resultados = processar_inbox(dry_run=dry_run)

    if "--json" in sys.argv:
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
    elif "--telegram" in sys.argv:
        formato_telegram(resultados)
    else:
        formato_terminal(resultados)
