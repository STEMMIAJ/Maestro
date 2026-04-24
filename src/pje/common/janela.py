"""Janela de horário do TJMG.

Endereça:
- PJE-009 (PJe pico 17h-20h: timeouts + 504/503)

REGISTRO.md histórico (2026-04-14): script rodou fora da janela e
caiu com 503/504. Fix sugerido: guarda no topo do main.

Janela útil: 13h-19h (configurável via env TJMG_JANELA_INICIO/FIM).
"""
from __future__ import annotations
from datetime import datetime
from .config import SETTINGS


def dentro_janela_tjmg(agora: datetime | None = None) -> bool:
    h = (agora or datetime.now()).hour
    return SETTINGS.janela_inicio <= h < SETTINGS.janela_fim


def msg_janela() -> str:
    return (
        f"Fora da janela TJMG ({SETTINGS.janela_inicio}h-{SETTINGS.janela_fim}h). "
        f"PJe instável fora desse horário (ref: PJE-009)."
    )
