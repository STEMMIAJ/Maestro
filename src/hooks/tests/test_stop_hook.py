import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "anti_mentira_stop.py"


def _make_transcript(tmp_path: Path, entries: list) -> Path:
    p = tmp_path / "transcript.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in entries), encoding="utf-8")
    return p


def _run_hook(stdin_payload: dict, env_overrides: dict) -> subprocess.CompletedProcess:
    env = {**os.environ, **env_overrides}
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(stdin_payload),
        capture_output=True,
        text=True,
        env=env,
    )


def test_blocks_when_claim_without_verification(tmp_path):
    transcript = _make_transcript(tmp_path, [
        {"type": "user", "message": {"content": "implementa X"}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Write", "input": {}}
        ]}},
        {"type": "assistant", "message": {"content": [
            {"type": "text", "text": "Pronto, está funcionando."}
        ]}},
    ])
    log = tmp_path / "errors.jsonl"
    result = _run_hook(
        {"session_id": "s1", "transcript_path": str(transcript)},
        {"ANTI_MENTIRA_LOG": str(log)},
    )
    assert result.returncode == 2, f"esperava 2, veio {result.returncode}, stderr={result.stderr}"
    assert "verific" in result.stderr.lower()
    assert log.exists() and "unverified_claim" in log.read_text()


def test_allows_when_verification_present(tmp_path):
    transcript = _make_transcript(tmp_path, [
        {"type": "user", "message": {"content": "implementa X"}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Write", "input": {}},
            {"type": "tool_use", "name": "Bash", "input": {}}
        ]}},
        {"type": "assistant", "message": {"content": [
            {"type": "text", "text": "Pronto, testes passaram."}
        ]}},
    ])
    log = tmp_path / "errors.jsonl"
    result = _run_hook(
        {"session_id": "s1", "transcript_path": str(transcript)},
        {"ANTI_MENTIRA_LOG": str(log)},
    )
    assert result.returncode == 0
    assert not log.exists() or "unverified_claim" not in log.read_text()


def test_silent_when_no_claim(tmp_path):
    transcript = _make_transcript(tmp_path, [
        {"type": "user", "message": {"content": "?"}},
        {"type": "assistant", "message": {"content": [
            {"type": "text", "text": "Vou ler o arquivo primeiro."}
        ]}},
    ])
    log = tmp_path / "errors.jsonl"
    result = _run_hook(
        {"session_id": "s1", "transcript_path": str(transcript)},
        {"ANTI_MENTIRA_LOG": str(log)},
    )
    assert result.returncode == 0
