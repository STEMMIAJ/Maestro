#!/usr/bin/env python3
"""SessionStart hook: injeta últimos erros não-resolvidos como contexto inicial."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.error_log import read_unresolved

DEFAULT_LOG = Path.home() / ".claude/projects/-Users-jesus/memory/errors.jsonl"


def _format(events: list) -> str:
    if not events:
        return ""
    lines = ["[ANTI-MENTIRA] Últimos erros do usuário não-resolvidos (evite repetir):"]
    for e in events:
        ts = e.get("ts", "?")[:10]
        kind = e.get("kind", "?")
        snippet = e.get("user_message") or e.get("claim") or e.get("context") or ""
        snippet = snippet.replace("\n", " ")[:140]
        lines.append(f"  - [{ts}] {kind}: {snippet}")
    return "\n".join(lines) + "\n"


def main() -> int:
    log_path = Path(os.environ.get("ANTI_MENTIRA_LOG", DEFAULT_LOG))
    events = read_unresolved(log_path, n=3)
    out = _format(events)
    if out:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
