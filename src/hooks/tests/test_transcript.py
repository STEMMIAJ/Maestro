import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.transcript import load_messages, last_assistant_text, tools_used_since_last_user


def _write_transcript(path: Path, entries: list) -> None:
    path.write_text("\n".join(json.dumps(e) for e in entries), encoding="utf-8")


def test_load_messages_normalizes_user_assistant(tmp_path):
    t = tmp_path / "t.jsonl"
    _write_transcript(t, [
        {"type": "user", "message": {"content": "oi"}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "olá"}]}},
    ])
    msgs = load_messages(t)
    assert msgs[0]["role"] == "user"
    assert msgs[0]["text"] == "oi"
    assert msgs[1]["role"] == "assistant"
    assert msgs[1]["text"] == "olá"


def test_load_messages_extracts_tool_use(tmp_path):
    t = tmp_path / "t.jsonl"
    _write_transcript(t, [
        {"type": "assistant", "message": {"content": [
            {"type": "text", "text": "vou rodar"},
            {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}
        ]}},
    ])
    msgs = load_messages(t)
    text_msgs = [m for m in msgs if m["role"] == "assistant"]
    tool_msgs = [m for m in msgs if m["role"] == "tool_use"]
    assert text_msgs and "vou rodar" in text_msgs[0]["text"]
    assert tool_msgs and tool_msgs[0]["tool_name"] == "Bash"


def test_last_assistant_text_returns_most_recent(tmp_path):
    t = tmp_path / "t.jsonl"
    _write_transcript(t, [
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "antigo"}]}},
        {"type": "user", "message": {"content": "ok"}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "novo"}]}},
    ])
    msgs = load_messages(t)
    assert last_assistant_text(msgs) == "novo"


def test_tools_used_since_last_user(tmp_path):
    t = tmp_path / "t.jsonl"
    _write_transcript(t, [
        {"type": "user", "message": {"content": "primeiro"}},
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": {}}]}},
        {"type": "user", "message": {"content": "segundo"}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {}},
            {"type": "tool_use", "name": "Grep", "input": {}}
        ]}},
    ])
    msgs = load_messages(t)
    tools = tools_used_since_last_user(msgs)
    assert tools == ["Bash", "Grep"]


def test_load_messages_handles_missing_file(tmp_path):
    assert load_messages(tmp_path / "nope.jsonl") == []


def test_load_messages_skips_malformed_lines(tmp_path):
    t = tmp_path / "t.jsonl"
    t.write_text("garbage\n" + json.dumps({"type": "user", "message": {"content": "ok"}}) + "\n")
    msgs = load_messages(t)
    assert len(msgs) == 1 and msgs[0]["text"] == "ok"
