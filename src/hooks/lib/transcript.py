"""Lê transcripts JSONL do Claude Code e normaliza para uso interno."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "\n".join(parts)
    return ""


def load_messages(transcript_path: Path) -> list[dict[str, Any]]:
    if not transcript_path.exists():
        return []
    out: list[dict[str, Any]] = []
    for raw in transcript_path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            continue
        etype = entry.get("type")
        msg = entry.get("message") or {}
        if etype == "user":
            content = msg.get("content") if isinstance(msg, dict) else entry.get("content")
            if isinstance(content, str):
                out.append({"role": "user", "text": content})
            else:
                out.append({"role": "user", "text": _extract_text(content)})
        elif etype == "assistant":
            content = msg.get("content", []) if isinstance(msg, dict) else []
            text = _extract_text(content)
            if text:
                out.append({"role": "assistant", "text": text})
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "tool_use":
                        out.append({
                            "role": "tool_use",
                            "text": "",
                            "tool_name": item.get("name", ""),
                        })
    return out


def last_assistant_text(messages: list[dict[str, Any]]) -> str:
    for m in reversed(messages):
        if m.get("role") == "assistant":
            return m.get("text", "")
    return ""


def tools_used_since_last_user(messages: list[dict[str, Any]]) -> list[str]:
    last_user_idx = -1
    for i, m in enumerate(messages):
        if m.get("role") == "user":
            last_user_idx = i
    return [m["tool_name"] for m in messages[last_user_idx + 1:] if m.get("role") == "tool_use"]
