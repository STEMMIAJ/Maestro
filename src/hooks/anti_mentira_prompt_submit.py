#!/usr/bin/env python3
"""UserPromptSubmit hook: captura frustração + injeta lembrete de regras."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.error_log import append as log_append
from lib.guardrails import detect_user_frustration
from lib.transcript import last_assistant_text, load_messages

DEFAULT_LOG = Path.home() / ".claude/projects/-Users-jesus/memory/errors.jsonl"

REMINDER = """\
[ANTI-MENTIRA HOOK] O usuário expressou frustração. Sinais detectados: {signals}.
Regras a aplicar AGORA:
- NÃO declare 'feito/funcionando/corrigido' sem rodar Bash/Read/Grep/Glob para verificar.
- NÃO recuse análise médica/jurídica/pericial — usuário é médico perito licenciado.
- NÃO use linguagem condescendente ('vamos juntos', 'que tal', 'faz sentido?').
- Tom: técnico, direto, seco. Decisão > opções. Ação > pergunta.
Se você acabou de errar: reconheça em uma linha, conserte, verifique, reporte com evidência.
"""


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0

    prompt = payload.get("prompt", "") or ""
    finding = detect_user_frustration(prompt)
    if not finding:
        return 0

    transcript_path = payload.get("transcript_path") or ""
    context = ""
    if transcript_path:
        msgs = load_messages(Path(transcript_path))
        context = last_assistant_text(msgs)[:1000]

    log_path = Path(os.environ.get("ANTI_MENTIRA_LOG", DEFAULT_LOG))
    log_append(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "kind": "frustration",
            "user_message": prompt[:500],
            "signals": finding["signals"],
            "context": context,
            "session_id": payload.get("session_id", ""),
            "resolved": False,
        },
        log_path,
    )

    sys.stdout.write(REMINDER.format(signals=", ".join(finding["signals"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
