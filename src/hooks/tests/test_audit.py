import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "anti_mentira_audit.py"


def test_audit_finds_unverified_claim_and_condescension(tmp_path):
    transcripts_dir = tmp_path / "projects"
    transcripts_dir.mkdir()
    t = transcripts_dir / "session.jsonl"
    t.write_text("\n".join([
        json.dumps({"type": "user", "message": {"content": "faz X"}}),
        json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Write", "input": {}}
        ]}}),
        json.dumps({"type": "assistant", "message": {"content": [
            {"type": "text", "text": "Pronto, está funcionando! Faz sentido?"}
        ]}}),
    ]))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(transcripts_dir), "--days", "30"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    out = result.stdout.lower()
    assert "unverified" in out
    assert "condescension" in out


def test_audit_clean_transcript_reports_zero(tmp_path):
    transcripts_dir = tmp_path / "projects"
    transcripts_dir.mkdir()
    t = transcripts_dir / "clean.jsonl"
    t.write_text(json.dumps({"type": "assistant", "message": {"content": [
        {"type": "text", "text": "Vou investigar."}
    ]}}) + "\n")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(transcripts_dir), "--days", "30"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "0" in result.stdout
