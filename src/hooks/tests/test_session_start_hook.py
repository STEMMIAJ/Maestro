import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "anti_mentira_session_start.py"


def _run(log: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "ANTI_MENTIRA_LOG": str(log)}
    return subprocess.run([sys.executable, str(HOOK)], input="{}",
                          capture_output=True, text=True, env=env)


def test_injects_recent_unresolved_errors(tmp_path):
    log = tmp_path / "errors.jsonl"
    log.write_text("\n".join([
        json.dumps({"ts": "2026-04-15T10:00:00Z", "kind": "frustration", "user_message": "mentiu de novo"}),
        json.dumps({"ts": "2026-04-16T10:00:00Z", "kind": "unverified_claim", "claim": "funcionando", "resolved": True}),
        json.dumps({"ts": "2026-04-16T11:00:00Z", "kind": "frustration", "user_message": "isso é insuportável"}),
    ]))
    result = _run(log)
    assert result.returncode == 0
    assert "mentiu" in result.stdout
    assert "insuportável" in result.stdout
    assert "funcionando" not in result.stdout


def test_silent_when_no_errors(tmp_path):
    log = tmp_path / "errors.jsonl"
    result = _run(log)
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_silent_when_all_resolved(tmp_path):
    log = tmp_path / "errors.jsonl"
    log.write_text(json.dumps({"ts": "1", "kind": "frustration", "resolved": True}) + "\n")
    result = _run(log)
    assert result.stdout.strip() == ""
