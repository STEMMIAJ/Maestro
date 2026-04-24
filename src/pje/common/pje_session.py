"""Detecção de sessão PJe ativa + diagnóstico de erro.

Endereça:
- PJE-002 (sessão PJe expira em ~30 min)
- PJE-008 (PJe tela branca: body vazio)
- PJE-023 (requests pós-Playwright dá 302 -> login.seam)

Padrão real do baixar_push_pje_playwright.py:282 (CASOS-PJE.md Caso 3).
"""
from __future__ import annotations
import unicodedata
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Page

_TERMS_LOGIN = ("login", "sso", "gov.br", "auth", "saml")


def _normalizar(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


async def sessao_ativa(page: "Page") -> bool:
    """True se logado no PJe. ref: PJE-002.

    Critério (igual ao baixar_push_pje_playwright.py:282):
    1. URL não contém termos de login
    2. body não tem CPF/CNPJ + Senha próximos
    3. domínio é PJe TJMG
    """
    try:
        url = _normalizar(page.url)
        if any(t in url for t in _TERMS_LOGIN):
            return False
        body = await page.locator("body").inner_text(timeout=3000)
        body_norm = _normalizar(body[:4000])
        if "cpf/cnpj" in body_norm and "senha" in body_norm:
            return False
        return "pje.tjmg.jus.br" in url or "tjmg.jus.br" in url
    except Exception:
        return False


async def salvar_diagnostico(page: "Page", pasta: Path, prefix: str = "erro") -> dict:
    """Salva PNG + HTML + URL atual. Retorna dict com paths gerados."""
    pasta.mkdir(parents=True, exist_ok=True)
    out = {}
    try:
        png = pasta / f"{prefix}_screenshot.png"
        await page.screenshot(path=str(png), full_page=True)
        out["png"] = str(png)
    except Exception:
        pass
    try:
        html = pasta / f"{prefix}_page.html"
        html.write_text(await page.content(), encoding="utf-8")
        out["html"] = str(html)
    except Exception:
        pass
    try:
        url = pasta / f"{prefix}_url.txt"
        url.write_text(page.url or "", encoding="utf-8")
        out["url"] = str(url)
    except Exception:
        pass
    return out
