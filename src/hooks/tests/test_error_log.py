import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.error_log import append, read_recent, read_unresolved


def test_append_creates_file_and_writes_json_line(tmp_path):
    log = tmp_path / "errors.jsonl"
    event = {"ts": "2026-04-17T10:00:00Z", "kind": "frustration", "user_message": "mentiu"}
    append(event, log)
    assert log.exists()
    line = log.read_text().strip()
    assert json.loads(line) == event


def test_append_is_append_only(tmp_path):
    log = tmp_path / "errors.jsonl"
    append({"ts": "2026-04-17T10:00:00Z", "kind": "a"}, log)
    append({"ts": "2026-04-17T11:00:00Z", "kind": "b"}, log)
    lines = log.read_text().strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0])["kind"] == "a"
    assert json.loads(lines[1])["kind"] == "b"


def test_read_recent_returns_last_n_reversed(tmp_path):
    log = tmp_path / "errors.jsonl"
    for i in range(10):
        append({"ts": f"2026-04-17T{i:02d}:00:00Z", "kind": "x", "i": i}, log)
    recent = read_recent(log, n=3)
    assert len(recent) == 3
    assert [e["i"] for e in recent] == [9, 8, 7]


def test_read_recent_handles_missing_file(tmp_path):
    log = tmp_path / "missing.jsonl"
    assert read_recent(log) == []


def test_read_unresolved_filters_resolved(tmp_path):
    log = tmp_path / "errors.jsonl"
    append({"ts": "1", "kind": "a", "resolved": True}, log)
    append({"ts": "2", "kind": "b", "resolved": False}, log)
    append({"ts": "3", "kind": "c"}, log)
    unresolved = read_unresolved(log, n=10)
    kinds = [e["kind"] for e in unresolved]
    assert "a" not in kinds
    assert "b" in kinds and "c" in kinds


def test_append_corrupt_event_does_not_crash_subsequent_reads(tmp_path):
    log = tmp_path / "errors.jsonl"
    log.write_text("not valid json\n")
    append({"ts": "1", "kind": "ok"}, log)
    recent = read_recent(log, n=10)
    assert any(e.get("kind") == "ok" for e in recent)
