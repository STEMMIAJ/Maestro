"""Verificar Chrome debug ANTES de connect_over_cdp.

Endereça:
- PJE-014 (Chrome debug Windows Parallels fecha ao suspender Mac)
- CDP-001 (curl /json/version retorna Connection refused)
- CDP-007 (Parallels: Mac não alcança Chrome via IP da VM)

Padrão de uso:
    from .cdp import chrome_debug_vivo
    if not chrome_debug_vivo(ip, porta):
        logger.captura_falha(..., ref_falhas_json='PJE-014')
        sys.exit(1)
"""
from __future__ import annotations
import json
import urllib.error
import urllib.request


def chrome_debug_vivo(ip: str, porta: int, timeout: float = 3.0) -> bool:
    """True se http://{ip}:{porta}/json/version responde."""
    url = f"http://{ip}:{porta}/json/version"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8", errors="replace"))
            return "Browser" in data
    except (urllib.error.URLError, ConnectionResetError, TimeoutError, json.JSONDecodeError):
        return False


def cdp_url(ip: str, porta: int) -> str:
    return f"http://{ip}:{porta}"
