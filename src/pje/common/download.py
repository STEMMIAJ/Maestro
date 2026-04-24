"""Download robusto de PDF do PJe — captura via 'download' OU via nova aba.

Endereça:
- PW-013 (wait_for_event('download') não resolve em window.open)
- PJE-003 (botão DOWNLOAD abre nova aba com PDF embed em vez de baixar)
- PJE-016 (botão DOWNLOAD não encontrado por texto)

Padrão real: baixar_push_pje_playwright.py:665 (CASOS-PJE.md Caso 4).
"""
from __future__ import annotations
import asyncio
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Locator, Page


async def clicar_e_salvar_download(
    page: "Page",
    botao: "Locator",
    destino: Path,
    timeout_ms: int = 300_000,
) -> dict:
    """Clica botão e captura PDF, com fallback para PDF servido em nova aba.

    Returns:
        {"tipo": "download" | "url-pdf" | "falha", "path": str|None, "motivo": str|None}
    """
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    contexto = page.context
    pages_antes = list(contexto.pages)

    # Tarefa do download nativo (pode resolver, pode não)
    download_task = asyncio.create_task(
        page.wait_for_event("download", timeout=timeout_ms)
    )

    try:
        await botao.click(timeout=15000)
    except Exception as e:
        download_task.cancel()
        return {"tipo": "falha", "path": None, "motivo": f"click falhou: {e}"}

    deadline = time.monotonic() + (timeout_ms / 1000.0)

    while time.monotonic() < deadline:
        # 1. Download capturado
        if download_task.done() and not download_task.cancelled():
            try:
                download = download_task.result()
                await download.save_as(str(destino))
                return {"tipo": "download", "path": str(destino), "motivo": None}
            except Exception as e:
                return {"tipo": "falha", "path": None, "motivo": f"save_as: {e}"}

        # 2. Nova aba com PDF embed
        novas = [p for p in contexto.pages if p not in pages_antes]
        for nova in novas:
            try:
                await nova.wait_for_load_state("domcontentloaded", timeout=5000)
                if ".pdf" in (nova.url or "").lower():
                    response = await contexto.request.get(nova.url)
                    body = await response.body()
                    destino.write_bytes(body)
                    download_task.cancel()
                    try:
                        await nova.close()
                    except Exception:
                        pass
                    return {"tipo": "url-pdf", "path": str(destino), "motivo": None}
            except Exception:
                continue

        await asyncio.sleep(0.5)

    download_task.cancel()
    return {"tipo": "falha", "path": None, "motivo": "timeout"}
