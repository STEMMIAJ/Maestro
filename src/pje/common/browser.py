"""Dispatcher de motor de browser — local (Mac) ou remoto (Chrome debug Windows).

Endereça:
- REFACTOR-PLAN §1.3: extrair launch_persistent_context de pje_standalone.py
- BUGS.md §8: connect_over_cdp inline em atualizar-pje.py
- PJE-014: validar /json/version antes de connect_over_cdp
- PW-002: anti-detect (--disable-blink-features=AutomationControlled)

Padrão de uso:
    from pje.common.browser import abrir_browser
    pw, ctx, page = await abrir_browser(motor="local")
    pw, ctx, page = await abrir_browser(motor="remoto", ip="10.211.55.3", porta=9223)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .cdp import cdp_url, chrome_debug_vivo
from .config import SETTINGS

# Perfil persistente local (cookies VidaaS reaproveitados entre sessões)
USER_DATA_LOCAL = Path.home() / ".pje-browser-data"


class BrowserError(RuntimeError):
    """Falha ao abrir/conectar browser. Inclui ref_falhas_json para logger."""

    def __init__(self, msg: str, ref: str | None = None) -> None:
        super().__init__(msg)
        self.ref_falhas_json = ref


async def abrir_browser_local(
    headless: bool = False,
    slow_mo: int = 100,
) -> tuple[Any, Any, Any]:
    """Lança Chromium local Mac com perfil persistente em ~/.pje-browser-data.

    Mesmo padrão de pje_standalone.py:abrir_browser. Login VidaaS feito 1x e cookies
    permanecem entre execuções. Sem cert A3 — para download que exige A3, usar
    motor='remoto' (Windows).

    ref: PW-002 (anti-detect), PJE-002 (sessão), PJE-NEW (A3 obrigatório).
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError as e:
        raise BrowserError(
            "Playwright não instalado (pip install playwright && playwright install chromium)",
            ref="PW-001",
        ) from e

    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_LOCAL),
        headless=headless,
        slow_mo=slow_mo,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
        ],
        viewport={"width": 1280, "height": 900},
        accept_downloads=True,
    )
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    return pw, ctx, page


async def conectar_browser_remoto(
    ip: str,
    porta: int,
) -> tuple[Any, Any, Any]:
    """Conecta via CDP no Chrome debug Windows (Parallels). Valida /json/version antes.

    ref: PJE-014 (CDP fora do ar), CDP-001 (connection refused), PW-019 (connect_over_cdp).
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError as e:
        raise BrowserError(
            "Playwright não instalado (pip install playwright && playwright install chromium)",
            ref="PW-001",
        ) from e

    if not chrome_debug_vivo(ip, porta):
        raise BrowserError(
            f"Chrome debug indisponível em {ip}:{porta} — abra .bat no Windows",
            ref="PJE-014",
        )

    pw = await async_playwright().start()
    try:
        browser = await pw.chromium.connect_over_cdp(cdp_url(ip, porta))
    except Exception as e:
        await pw.stop()
        raise BrowserError(
            f"connect_over_cdp falhou em {ip}:{porta}: {e}",
            ref="PW-019",
        ) from e

    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    return pw, ctx, page


async def abrir_browser(
    motor: str = "local",
    ip: str | None = None,
    porta: int | None = None,
    **kwargs: Any,
) -> tuple[Any, Any, Any]:
    """Dispatcher. motor in {'local','remoto'}. Default lê SETTINGS.motor.

    motor='local'  → abrir_browser_local()
    motor='remoto' → conectar_browser_remoto(ip, porta) (defaults: SETTINGS.chrome_debug_ip/porta)
    """
    motor = (motor or SETTINGS.motor or "local").lower()

    if motor == "local":
        return await abrir_browser_local(
            headless=kwargs.get("headless", False),
            slow_mo=kwargs.get("slow_mo", 100),
        )

    if motor == "remoto":
        return await conectar_browser_remoto(
            ip=ip or SETTINGS.chrome_debug_ip,
            porta=porta or SETTINGS.chrome_debug_porta,
        )

    raise BrowserError(f"motor inválido: {motor!r} (use 'local' ou 'remoto')", ref="GL-001")
