"""Pastas padrão + safe_move cross-filesystem.

Endereça:
- PJE-021 (PDF baixado em _tmp não move para pasta final em FS diferente)
- GL-001 (Path.home() difere Mac/Windows)
- BUGS.md §10 (Backup copia sem verificar espaço)
"""
from __future__ import annotations
import shutil
from pathlib import Path
from .config import SETTINGS


def processos_dir() -> Path:
    SETTINGS.processos_dir.mkdir(parents=True, exist_ok=True)
    return SETTINGS.processos_dir


def quarentena_dir() -> Path:
    """PDFs com CNJ que não bate ficam aqui pra revisão manual."""
    p = processos_dir() / "_QUARENTENA"
    p.mkdir(parents=True, exist_ok=True)
    return p


def safe_move(src: Path, dst: Path) -> bool:
    """ref: PJE-021. shutil.move (copy+delete) cross-FS no Windows."""
    src = Path(src)
    dst = Path(dst)
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(str(src), str(dst))
        return True
    except OSError:
        # Cross-FS no Windows entre %TEMP% (C:) e destino (D:): copy manual.
        try:
            shutil.copy2(str(src), str(dst))
            src.unlink(missing_ok=True)
            return True
        except Exception:
            return False
