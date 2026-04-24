#!/usr/bin/env python3
"""Stop hook: bloqueia término se assistant declarou sucesso sem verificação."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.error_log import append as log_append
from lib.guardrails import detect_unverified_claim
from lib.transcript import last_assistant_text, load_messages, tools_used_since_last_user

DEFAULT_LOG = Path.home() / ".claude/projects/-Users-jesus/memory/errors.jsonl"


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0

    transcript_path = payload.get("transcript_path")
    if not transcript_path:
        return 0
    messages = load_messages(Path(transcript_path))
    text = last_assistant_text(messages)
    tools = tools_used_since_last_user(messages)

    finding = detect_unverified_claim(text, tools)
    if not finding:
        return 0

    log_path = Path(os.environ.get("ANTI_MENTIRA_LOG", DEFAULT_LOG))
    log_append(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "kind": "unverified_claim",
            "claim": finding["claim"],
            "context": text[:1000],
            "tools_used": tools,
            "session_id": payload.get("session_id", ""),
            "resolved": False,
        },
        log_path,
    )

    sys.stderr.write(
        f"BLOQUEADO: você declarou '{finding['claim']}' sem verificar. "
        f"Rode Bash/Read/Grep/Glob para confirmar antes de finalizar.\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
