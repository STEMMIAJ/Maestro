#!/usr/bin/env python3
"""
python_base_indexer.py — enfileira scripts Python alterados para indexação.

Uso:
  1. Como hook PostToolUse (matcher Write|Edit, glob *.py) — lê arquivo do stdin/argv e adiciona à fila.
  2. Standalone: `python3 python_base_indexer.py --process-queue` — processa fila pendente.

Fila: ~/Desktop/STEMMIA Dexter/PYTHON-BASE/.queue/pending.txt (1 path por linha).
Dedup por hash SHA256.
"""
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(os.path.expanduser("~/Desktop/STEMMIA Dexter/PYTHON-BASE"))
QUEUE_DIR = BASE / ".queue"
QUEUE_FILE = QUEUE_DIR / "pending.txt"
LOGS_DIR = BASE / "99-LOGS"
INDICE = BASE / "_INDICE-CONSULTAVEL.md"
FALHAS_JSON = BASE / "03-FALHAS-SOLUCOES" / "db" / "falhas.json"

IGNORE_PATTERNS = [r"/\.venv/", r"/__pycache__/", r"/\.queue/", r"/_[^/]*\.py$"]


def should_ignore(path: str) -> bool:
    return any(re.search(p, path) for p in IGNORE_PATTERNS)


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:12]


def extract_libs(content: str) -> list:
    libs = set()
    for line in content.splitlines():
        m = re.match(r"^\s*(?:from\s+(\S+?)(?:\s|\.)|import\s+(\S+?)(?:\s|$|,))", line)
        if m:
            lib = (m.group(1) or m.group(2) or "").split(".")[0]
            if lib and not lib.startswith("_"):
                libs.add(lib)
    return sorted(libs)


def extract_tags(content: str, libs: list) -> list:
    tags = set(libs[:3])
    keywords = {
        "selenium", "playwright", "requests", "bs4", "pandas", "pdfplumber",
        "pje", "retry", "download", "scraping", "ocr", "cdp", "debug", "async"
    }
    text_lower = content.lower()
    for kw in keywords:
        if kw in text_lower:
            tags.add(kw)
    return sorted(tags)[:6]


def extract_pattern(path: Path, content: str) -> str:
    # primeira docstring ou primeiro comentário não-shebang
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('"""') or line.startswith("'''"):
            end = i + 1
            while end < len(lines) and '"""' not in lines[end] and "'''" not in lines[end]:
                end += 1
            return " ".join(lines[i : end + 1])[:200].replace('"""', "").replace("'''", "").strip()
        if line.startswith("#") and not line.startswith("#!"):
            return line.lstrip("# ").strip()[:150]
    return f"Script: {path.name}"


def enqueue(path: str):
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    if should_ignore(path):
        return
    existing = QUEUE_FILE.read_text().splitlines() if QUEUE_FILE.exists() else []
    if path not in existing:
        with QUEUE_FILE.open("a") as f:
            f.write(path + "\n")


def process_queue():
    if not QUEUE_FILE.exists():
        print(json.dumps({"processados": 0, "motivo": "fila vazia"}))
        return

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    INDICE.parent.mkdir(parents=True, exist_ok=True)
    if not INDICE.exists():
        INDICE.write_text("# Índice consultável PYTHON-BASE\n\n| Arquivo | Padrão | Bibs | Tags | Hash | Data |\n|---|---|---|---|---|---|\n")

    pending = [l.strip() for l in QUEUE_FILE.read_text().splitlines() if l.strip()]
    processados, pulados, erros = 0, 0, []
    log_file = LOGS_DIR / f"indexer-{datetime.now():%Y%m%d}.log"

    # carregar hashes já indexados
    existing_hashes = set()
    if INDICE.exists():
        for line in INDICE.read_text().splitlines():
            m = re.search(r"\|\s*([a-f0-9]{12})\s*\|", line)
            if m:
                existing_hashes.add(m.group(1))

    new_rows = []
    for p in pending:
        path = Path(p)
        if not path.exists() or not path.suffix == ".py":
            pulados += 1
            continue
        if should_ignore(str(path)):
            pulados += 1
            continue
        try:
            content = path.read_text(errors="ignore")
            h = file_hash(path)
            if h in existing_hashes:
                pulados += 1
                continue
            libs = extract_libs(content)
            tags = extract_tags(content, libs)
            pattern = extract_pattern(path, content)
            row = f"| `{path.name}` | {pattern[:80]} | {', '.join(libs[:3])} | {', '.join(tags)} | {h} | {datetime.now():%Y-%m-%d} |"
            new_rows.append(row)
            existing_hashes.add(h)
            processados += 1
            with log_file.open("a") as lf:
                lf.write(f"{datetime.now().isoformat()} OK {path} hash={h}\n")
        except Exception as e:
            erros.append(f"{path}: {e}")

    if new_rows:
        with INDICE.open("a") as f:
            f.write("\n".join(new_rows) + "\n")

    # mover fila para done
    done_file = QUEUE_DIR / f"done-{datetime.now():%Y%m%d}.txt"
    with done_file.open("a") as f:
        f.write("\n".join(pending) + "\n")
    QUEUE_FILE.write_text("")

    print(json.dumps({
        "processados": processados,
        "pulados": pulados,
        "novos_registros_indice": len(new_rows),
        "erros": erros,
    }, ensure_ascii=False))


def main():
    if "--process-queue" in sys.argv:
        process_queue()
        return

    # modo hook: espera JSON via stdin OR path via argv
    path = None
    if len(sys.argv) > 1 and sys.argv[1] not in ("--process-queue",):
        path = sys.argv[1]
    else:
        try:
            data = json.load(sys.stdin)
            path = data.get("tool_input", {}).get("file_path") or data.get("file_path")
        except Exception:
            pass

    if path and path.endswith(".py"):
        enqueue(path)
        print(json.dumps({"enqueued": path}))
    else:
        print(json.dumps({"skipped": True}))


if __name__ == "__main__":
    main()
