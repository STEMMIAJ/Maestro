#!/usr/bin/env python3
"""Clusteriza errors.jsonl em padrões recorrentes e gera feedback_*.md."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

THRESHOLD = 3
MAX_SLUG_TOKENS = 3

FEEDBACK_TEMPLATE = """\
---
name: {name}
description: Padrão recorrente detectado pelo destilador anti-mentira: {signals}
type: feedback
---

Padrão detectado automaticamente após {count} ocorrências entre {first_date} e {last_date}.

**Sinais:** {signals}

**Exemplos do que o usuário disse:**
{examples}

**Why:** O destilador identificou que esse problema recorre. Cada repetição custa tempo e confiança.

**How to apply:** Antes de declarar sucesso, verificar com Bash/Read/Grep/Glob. Antes de assumir que entendeu, reler o pedido. Se reconhecer um sinal listado em mensagem do usuário, parar e revisar a última ação.
"""


def _normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9áéíóúâêôãõçñ ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _signature(event: dict) -> tuple:
    signals = event.get("signals") or []
    if not signals:
        msg = event.get("user_message") or event.get("claim") or ""
        signals = _normalize(msg).split()[:MAX_SLUG_TOKENS]
    norm = [_normalize(s).split()[0] for s in signals if s and _normalize(s).split()]
    norm = [s for s in norm if s]
    return tuple(sorted(set(norm))[:MAX_SLUG_TOKENS])


def _slug(sig: tuple) -> str:
    return "_".join(sig) if sig else "geral"


def cluster(events: list) -> dict:
    buckets: dict = defaultdict(list)
    for e in events:
        if e.get("resolved"):
            continue
        sig = _signature(e)
        if not sig:
            continue
        buckets[sig].append(e)
    return buckets


def render_feedback(sig: tuple, events: list) -> str:
    examples_lines = []
    for e in events[:3]:
        msg = (e.get("user_message") or e.get("claim") or "").replace("\n", " ").strip()[:200]
        if msg:
            examples_lines.append(f'- "{msg}"')
    examples = "\n".join(examples_lines) or "- (sem exemplo de mensagem)"
    dates = sorted(e.get("ts", "") for e in events)
    return FEEDBACK_TEMPLATE.format(
        name=f"feedback_{_slug(sig)}",
        signals=", ".join(sig),
        count=len(events),
        first_date=dates[0][:10] if dates else "?",
        last_date=dates[-1][:10] if dates else "?",
        examples=examples,
    )


def update_index(memory_dir: Path, slug: str, signals: tuple) -> None:
    index = memory_dir / "MEMORY.md"
    line = f"- [feedback_{slug}](feedback_{slug}.md) — Auto-destilado: {', '.join(signals)}\n"
    content = index.read_text(encoding="utf-8") if index.exists() else "# Memory\n"
    if f"feedback_{slug}.md" in content:
        return
    index.write_text(content.rstrip() + "\n" + line, encoding="utf-8")


def rewrite_log_with_resolved(log_path: Path, resolved_signatures: set) -> None:
    if not log_path.exists():
        return
    new_lines = []
    for raw in log_path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            e = json.loads(raw)
        except json.JSONDecodeError:
            new_lines.append(raw)
            continue
        if not e.get("resolved") and _signature(e) in resolved_signatures:
            e["resolved"] = True
            e["resolved_at"] = datetime.now(timezone.utc).isoformat()
        new_lines.append(json.dumps(e, ensure_ascii=False))
    log_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--memory-dir", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.log.exists():
        print("log não existe, nada a fazer")
        return 0
    events = []
    for raw in args.log.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            events.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    buckets = cluster(events)
    resolved: set = set()
    for sig, evs in buckets.items():
        if len(evs) < THRESHOLD:
            continue
        slug = _slug(sig)
        target = args.memory_dir / f"feedback_{slug}.md"
        if target.exists():
            continue
        if args.dry_run:
            print(f"would create / criaria: {target}")
            continue
        target.write_text(render_feedback(sig, evs), encoding="utf-8")
        update_index(args.memory_dir, slug, sig)
        resolved.add(sig)
        print(f"criado: {target}")
    if resolved and not args.dry_run:
        rewrite_log_with_resolved(args.log, resolved)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
