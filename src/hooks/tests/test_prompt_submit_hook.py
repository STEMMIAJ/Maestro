import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "anti_mentira_prompt_submit.py"


def _run(payload: dict, log: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "ANTI_MENTIRA_LOG": str(log)}
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True, text=True, env=env,
    )


def test_frustration_logs_and_injects_reminder(tmp_path):
    log = tmp_path / "errors.jsonl"
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(json.dumps({"type": "assistant", "message": {"content": [
        {"type": "text", "text": "achei que tinha funcionado"}
    ]}}) + "\n")

    result = _run({
        "session_id": "s1",
        "prompt": "você mentiu de novo, isso é insuportável",
        "transcript_path": str(transcript),
    }, log)

    assert result.returncode == 0
    assert log.exists()
    assert "frustration" in log.read_text()
    assert "mentir" in result.stdout.lower() or "verifi" in result.stdout.lower()


def test_neutral_prompt_is_silent(tmp_path):
    log = tmp_path / "errors.jsonl"
    result = _run({"session_id": "s1", "prompt": "ok, segue", "transcript_path": ""}, log)
    assert result.returncode == 0
    assert result.stdout.strip() == ""
    assert not log.exists()
