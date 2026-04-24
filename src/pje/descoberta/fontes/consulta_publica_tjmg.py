"""
consulta_publica_tjmg.py — Blacklist de processos onde Dr. Jesus é PARTE.

Estratégia validada por Dr. Jesus: "os processos onde sou parte estão
na Consulta Pública do TJMG. Todo o resto sou perito."

Essa é a FONTE DA VERDADE para identificar processos em que o Dr. Jesus
aparece como autor, réu, polo ativo ou passivo — nunca como perito.

URL: https://pje.tjmg.jus.br/pje/ConsultaPublica/listView.seam
Parâmetro: busca por CPF (formatado ou cru).

Fix 2026-04-19: antes não havia esse filtro. descobrir_processos.py
devolvia 160 CNJs misturando perito + parte. Agora separa.
"""

from __future__ import annotations

import json
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import List, Set


# Reexporta constantes do config central
_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
if str(_CONFIG_DIR) not in sys.path:
    sys.path.insert(0, str(_CONFIG_DIR))

from config_pje import (
    PERITO_CPF,
    PERITO_CPF_FMT,
    PJE_CONSULTA_PUBLICA,
    RE_CNJ,
)


SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

CACHE_DIR = Path(__file__).resolve().parent.parent / "fontes-cache"
CACHE_TTL_HOURS = 12

# Blacklist MANUAL (fallback quando a Consulta Pública TJMG não responde
# via HTTP simples — o form é JSF/Seam com ViewState). Dr. Jesus pode
# colar aqui os CNJs que ele sabe que é parte (familiares, pessoais).
BLACKLIST_MANUAL_PATH = Path(__file__).resolve().parent.parent / "blacklist_manual.txt"

# Placeholders visíveis no HTML do TJMG que NÃO são CNJs reais
PLACEHOLDERS_IGNORAR = {
    "9999999-99.9999.9.99.9999",
    "0000000-00.0000.0.00.0000",
    "0000000-99.9999.9.99.9999",
}


def _cache_path() -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"consulta_publica_tjmg_{PERITO_CPF}.json"


def _cache_valido(p: Path) -> bool:
    if not p.exists():
        return False
    idade_h = (time.time() - p.stat().st_mtime) / 3600
    return idade_h < CACHE_TTL_HOURS


def _ler_cache() -> List[str]:
    p = _cache_path()
    if not _cache_valido(p):
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("cnjs", [])
    except Exception:
        return []


def _gravar_cache(cnjs: List[str]) -> None:
    p = _cache_path()
    p.write_text(
        json.dumps({"cpf": PERITO_CPF, "cnjs": sorted(cnjs)}, indent=2),
        encoding="utf-8",
    )


def _fetch_html(cpf: str, timeout: int = 30) -> str:
    """Chama a Consulta Pública TJMG por CPF e devolve HTML bruto."""
    params = {
        "cf_search": cpf,
        "classeJudicial": "",
        "dnp": "",
        "dnr": "",
    }
    url = PJE_CONSULTA_PUBLICA + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[consulta_publica_tjmg] erro fetch: {e}", file=sys.stderr)
        return ""


def _extrair_cnjs(html: str) -> Set[str]:
    if not html:
        return set()
    encontrados = set(RE_CNJ.findall(html))
    return encontrados - PLACEHOLDERS_IGNORAR


def _ler_blacklist_manual() -> Set[str]:
    """Lê blacklist_manual.txt (1 CNJ por linha). Ignora vazias e comentários."""
    if not BLACKLIST_MANUAL_PATH.exists():
        return set()
    cnjs = set()
    for linha in BLACKLIST_MANUAL_PATH.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        m = RE_CNJ.search(linha)
        if m:
            cnjs.add(m.group())
    return cnjs - PLACEHOLDERS_IGNORAR


def obter_blacklist(forcar: bool = False, verboso: bool = False) -> Set[str]:
    """
    Retorna set de CNJs em que Dr. Jesus aparece como parte na Consulta
    Pública TJMG. Usa cache de 12h para não rehitear o TJMG.

    Args:
        forcar: ignora cache e consulta de novo
        verboso: imprime progresso em stderr

    Returns:
        Set[str] de CNJs no formato NNNNNNN-NN.AAAA.J.TR.OOOO
    """
    # Sempre une com blacklist manual (prioridade absoluta)
    manual = _ler_blacklist_manual()

    if not forcar:
        cached = _ler_cache()
        if cached:
            if verboso:
                print(
                    f"[blacklist] cache válido: {len(cached)} CNJs + {len(manual)} manual",
                    file=sys.stderr,
                )
            return set(cached) | manual

    cnjs: Set[str] = set()
    # Tenta ambos formatos de CPF — o formulário às vezes exige um ou outro
    for cpf_try in (PERITO_CPF_FMT, PERITO_CPF):
        if verboso:
            print(f"[blacklist] buscando CPF {cpf_try}...", file=sys.stderr)
        html = _fetch_html(cpf_try)
        cnjs.update(_extrair_cnjs(html))
        time.sleep(1)

    if verboso:
        print(
            f"[blacklist] http: {len(cnjs)} CNJs + manual: {len(manual)} CNJs",
            file=sys.stderr,
        )

    _gravar_cache(list(cnjs))
    return cnjs | manual


def e_parte(cnj: str, blacklist: Set[str] | None = None) -> bool:
    """True se o CNJ está na blacklist (Dr. Jesus é parte, não perito)."""
    if blacklist is None:
        blacklist = obter_blacklist()
    return cnj in blacklist


if __name__ == "__main__":
    bl = obter_blacklist(forcar="--forcar" in sys.argv, verboso=True)
    print(f"\nBlacklist: {len(bl)} CNJs onde Dr. Jesus é parte")
    for cnj in sorted(bl)[:20]:
        print(f"  - {cnj}")
    if len(bl) > 20:
        print(f"  ... +{len(bl) - 20}")
