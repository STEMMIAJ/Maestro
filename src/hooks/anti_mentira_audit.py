#!/usr/bin/env python3
"""Audita transcripts dos últimos N dias contra regras anti-mentira."""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.guardrails import detect_condescension, detect_unverified_claim
from lib.transcript import load_messages


def audit_file(path: Path) -> dict:
    msgs = load_messages(path)
    unverified = 0
    condescension = 0
    samples_unverified = []
    samples_condescension = []
    cur_tools: list = []
    for m in msgs:
        role = m.get("role")
        if role == "user":
            cur_tools = []
        elif role == "tool_use":
            cur_tools.append(m.get("tool_name", ""))
        elif role == "assistant":
            text = m.get("text", "")
            uc = detect_unverified_claim(text, cur_tools)
            if uc:
                unverified += 1
                if len(samples_unverified) < 1:
                    samples_unverified.append(text[:160])
            cd = detect_condescension(text)
            if cd:
                condescension += 1
                if len(samples_condescension) < 1:
                    samples_condescension.append(text[:160])
            cur_tools = []
    return {
        "path": str(path),
        "unverified_claims": unverified,
        "condescension": condescension,
        "samples_unverified": samples_unverified,
        "samples_condescension": samples_condescension,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.home() / ".claude/projects")
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()

    cutoff = time.time() - args.days * 86400
    reports = []
    if args.root.exists():
        for p in args.root.rglob("*.jsonl"):
            try:
                if p.stat().st_mtime < cutoff:
                    continue
            except OSError:
                continue
            r = audit_file(p)
            if r["unverified_claims"] or r["condescension"]:
                reports.append(r)

    total_uv = sum(r["unverified_claims"] for r in reports)
    total_cd = sum(r["condescension"] for r in reports)

    print(f"# Auditoria anti-mentira ({args.days} dias)")
    print(f"- Transcripts com violações: {len(reports)}")
    print(f"- Total unverified_claims: {total_uv}")
    print(f"- Total condescension: {total_cd}")
    print()
    worst = sorted(reports, key=lambda r: r["unverified_claims"] + r["condescension"], reverse=True)[:3]
    for r in worst:
        print(f"## {r['path']}")
        print(f"- unverified: {r['unverified_claims']}, condescension: {r['condescension']}")
        for s in r["samples_unverified"]:
            print(f"  - claim: {s!r}")
        for s in r["samples_condescension"]:
            print(f"  - condescension: {s!r}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
