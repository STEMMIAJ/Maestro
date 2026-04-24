"""Config centralizada via env (.env opcional).

Endereça:
- BUGS.md §8 CRÍTICO: IP 10.211.55.3 hardcoded em atualizar-pje.py
- BUGS.md §19 CRÍTICO: chat_id 8397602236 + token Telegram hardcoded em pje_standalone.py
- REFACTOR-PLAN §1.2 — remover hardcodes sensíveis

Base: ~/Desktop/_MESA/01-ATIVO/PYTHON-BASE/06-TEMPLATES/script-cli-typer-com-logging.py
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path


def _env(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key, default)
    return v.strip() if isinstance(v, str) and v.strip() else default


@dataclass(frozen=True)
class Settings:
    # Chrome debug (Parallels Windows ou Mac local)
    chrome_debug_ip: str = field(default_factory=lambda: _env("CHROME_DEBUG_IP", "10.211.55.3") or "10.211.55.3")
    chrome_debug_porta: int = field(default_factory=lambda: int(_env("CHROME_DEBUG_PORTA", "9223") or 9223))

    # Pastas
    processos_dir: Path = field(default_factory=lambda: Path(
        _env("PROCESSOS_DIR", str(Path.home() / "Desktop/ANALISADOR FINAL/processos"))
        or str(Path.home() / "Desktop/ANALISADOR FINAL/processos")
    ))

    # Telegram (opcional — se faltar, notificações silenciam, NÃO quebram script)
    telegram_token: str | None = field(default_factory=lambda: _env("TELEGRAM_TOKEN") or _env("TELEGRAM_BOT_TOKEN"))
    telegram_chat_id: str | None = field(default_factory=lambda: _env("TELEGRAM_CHAT_ID"))

    # Janela TJMG (PJE-009)
    janela_inicio: int = field(default_factory=lambda: int(_env("TJMG_JANELA_INICIO", "13") or 13))
    janela_fim: int = field(default_factory=lambda: int(_env("TJMG_JANELA_FIM", "19") or 19))

    # Motor browser default — 'local' (Chromium Mac) ou 'remoto' (CDP Windows)
    motor: str = field(default_factory=lambda: (_env("PJE_MOTOR", "local") or "local").lower())


SETTINGS = Settings()


def telegram_configurado() -> bool:
    return bool(SETTINGS.telegram_token and SETTINGS.telegram_chat_id)
