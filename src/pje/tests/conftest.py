"""Adiciona raiz de src/pje ao sys.path para os testes importarem modulos locais."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for sub in ("", "config", "descoberta", "descoberta/core", "descoberta/fontes"):
    p = ROOT / sub if sub else ROOT
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)
