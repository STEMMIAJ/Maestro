"""Append-only JSONL log de eventos de frustração e enforcement."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def append(event: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def _read_all(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            out.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return out


def read_recent(path: Path, n: int = 5) -> list[dict[str, Any]]:
    events = _read_all(path)
    return list(reversed(events[-n:]))


def read_unresolved(path: Path, n: int = 3) -> list[dict[str, Any]]:
    events = [e for e in _read_all(path) if not e.get("resolved")]
    return list(reversed(events[-n:]))
