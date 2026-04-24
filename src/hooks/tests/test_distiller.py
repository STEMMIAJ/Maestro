import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "anti_mentira_distiller.py"


def _run(log: Path, mem_dir: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--log", str(log), "--memory-dir", str(mem_dir), *args],
        capture_output=True, text=True,
    )


def test_creates_memory_when_pattern_repeats_3_times(tmp_path):
    log = tmp_path / "errors.jsonl"
    mem = tmp_path / "memory"
    mem.mkdir()
    (mem / "MEMORY.md").write_text("# Memory\n")
    for i in range(3):
        with log.open("a") as f:
            f.write(json.dumps({
                "ts": f"2026-04-{i+10:02d}T10:00:00Z",
                "kind": "frustration",
                "signals": ["mentiu", "não funciona"],
                "user_message": "mentiu de novo, não funciona"
            }) + "\n")

    result = _run(log, mem)
    assert result.returncode == 0, f"stderr={result.stderr}"
    created = list(mem.glob("feedback_*.md"))
    assert created, f"nenhum feedback criado. stdout={result.stdout}"
    assert "feedback_" in (mem / "MEMORY.md").read_text()


def test_below_threshold_creates_nothing(tmp_path):
    log = tmp_path / "errors.jsonl"
    mem = tmp_path / "memory"
    mem.mkdir()
    (mem / "MEMORY.md").write_text("# Memory\n")
    log.write_text(json.dumps({"ts": "1", "kind": "frustration", "signals": ["único"]}) + "\n")
    result = _run(log, mem)
    assert result.returncode == 0
    assert not list(mem.glob("feedback_*.md"))


def test_dry_run_writes_nothing(tmp_path):
    log = tmp_path / "errors.jsonl"
    mem = tmp_path / "memory"
    mem.mkdir()
    (mem / "MEMORY.md").write_text("# Memory\n")
    for i in range(3):
        with log.open("a") as f:
            f.write(json.dumps({"ts": f"2026-04-{i+10:02d}T10:00:00Z", "kind": "frustration", "signals": ["mentiu"]}) + "\n")
    result = _run(log, mem, "--dry-run")
    assert result.returncode == 0
    assert not list(mem.glob("feedback_*.md"))
    assert "would create" in result.stdout.lower() or "criaria" in result.stdout.lower()


def test_marks_clustered_events_as_resolved(tmp_path):
    log = tmp_path / "errors.jsonl"
    mem = tmp_path / "memory"
    mem.mkdir()
    (mem / "MEMORY.md").write_text("# Memory\n")
    for i in range(3):
        with log.open("a") as f:
            f.write(json.dumps({"ts": f"2026-04-{i+10:02d}T10:00:00Z", "kind": "frustration", "signals": ["mentiu"]}) + "\n")
    _run(log, mem)
    after = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
    assert all(e.get("resolved") is True for e in after)
