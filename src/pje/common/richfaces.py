"""Helpers para RichFaces/PrimeFaces (PJe usa ambos).

Endereça:
- PW-008 (IDs com ':' quebram querySelector)
- PW-009 (select_option falha em PrimeFaces)
- PJE-004 ('Incluir expediente=Sim' não seleciona)
- PJE-024 (selects populados via Ajax demoram)
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Page


def escapar_id(jsf_id: str) -> str:
    """form:situacao_input → form\\:situacao_input. ref: PW-008."""
    return jsf_id.replace(":", r"\:")


async def setar_select_jsf(page: "Page", input_id: str, valor: str) -> bool:
    """Define value + dispara change manualmente.

    PrimeFaces esconde <select> nativo; select_option oficial não dispara
    onchange AJAX. Padrão consultar_aj.py:233 (citado em falhas.json PW-009).
    """
    js = (
        "(args) => {"
        " var el = document.getElementById(args.id);"
        " if (!el) return false;"
        " el.value = args.v;"
        " el.dispatchEvent(new Event('change', {bubbles: true}));"
        " el.dispatchEvent(new Event('input', {bubbles: true}));"
        " return true;"
        "}"
    )
    try:
        ok = await page.evaluate(js, {"id": input_id, "v": valor})
        return bool(ok)
    except Exception:
        return False


async def aguardar_select_populado(page: "Page", input_id: str, timeout_ms: int = 10000) -> bool:
    """Espera <select id=...> ter pelo menos 2 options. ref: PJE-024."""
    js = (
        "(id) => { var el = document.getElementById(id);"
        " return !!el && el.options && el.options.length > 1; }"
    )
    try:
        await page.wait_for_function(js, arg=input_id, timeout=timeout_ms)
        return True
    except Exception:
        return False
