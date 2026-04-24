"""Validação de PDF + extração de texto + checagem de CNJ na 1ª página.

Endereça:
- PJE-007 (PDF baixado não corresponde ao CNJ esperado)
- PW-028 (download chega vazio/truncado)

Padrão real do baixar_push_pje_playwright.py linha 536:
    def pdf_valido(path):
        if path.stat().st_size < 1024: return False
        with path.open("rb") as f: return f.read(4) == b"%PDF"

Ref: ~/Desktop/_MESA/01-ATIVO/PYTHON-BASE/07-PESQUISA-AGENTES/browser/CASOS-PJE.md
"""
from __future__ import annotations
import re
import subprocess
from pathlib import Path

from .cnj import limpar_cnj


def pdf_valido(path: Path, min_bytes: int = 1024) -> bool:
    """True se arquivo existe, >min_bytes e header é %PDF. ref: PW-028."""
    p = Path(path)
    try:
        if not p.is_file() or p.stat().st_size < min_bytes:
            return False
        with p.open("rb") as f:
            return f.read(4) == b"%PDF"
    except OSError:
        return False


def extrair_texto(pdf: Path, timeout: int = 120) -> str | None:
    """Roda pdftotext -layout. None se falhar."""
    p = Path(pdf)
    if not p.exists():
        return None
    try:
        r = subprocess.run(
            ["pdftotext", "-layout", str(p), "-"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if r.returncode == 0:
            return r.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return None


def cnj_no_pdf(pdf: Path, cnj: str, primeiras_paginas_chars: int = 8000) -> bool:
    """True se CNJ aparece nas primeiras páginas do PDF.

    Aceita formato CNJ formatado OU 20 dígitos contínuos.
    ref: PJE-007.
    """
    txt = extrair_texto(pdf)
    if txt is None:
        return False
    head = txt[:primeiras_paginas_chars]
    head_norm = re.sub(r"\s+", "", head)
    digitos = limpar_cnj(cnj)
    if not digitos:
        return False
    # busca o CNJ formatado e a versão só-dígitos (com e sem pontuação)
    return cnj in head or digitos in head_norm
