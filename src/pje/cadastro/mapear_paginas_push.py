#!/usr/bin/env python3
"""
mapear_paginas_push.py — Varre TODAS as páginas do PUSH do PJe TJMG
e extrai CNJs já cadastrados (verificação PROATIVA antes de tentar incluir).

Saída: _mapa/push_atual_{YYYY-MM-DD}.json

Uso:
    python3 mapear_paginas_push.py
    python3 mapear_paginas_push.py --porta 9222
    python3 mapear_paginas_push.py --standalone

Ref-falhas: PW-012 (selectors PJe variam entre versões),
            PW-019 (paginação pode ser JS async — esperar render),
            PW-031 (sessão expira meio de varredura — re-login).
"""

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("pip install playwright && playwright install chromium")
    sys.exit(1)

# Config central
THIS_DIR = Path(__file__).parent
ROOT = THIS_DIR.parent
sys.path.insert(0, str(ROOT))
try:
    from config.config_pje import PUSH_MAPA_FILE, CADASTRO_DIR  # noqa
except Exception:
    PUSH_MAPA_FILE = "push_atual_{data}.json"
    CADASTRO_DIR = THIS_DIR


# ============================================================
# CONFIGURAÇÃO (espelhada de incluir_push.py — COPIADA)
# ============================================================

PJE_LOGIN = "https://pje.tjmg.jus.br/pje/login.seam"
PJE_PUSH = "https://pje.tjmg.jus.br/pje/Push/listView.seam"
PJE_PUSH_ALT = "https://pje.tjmg.jus.br/pje/Push/push.seam"

USER_DATA = Path.home() / ".pje-browser-data"
MAPA_DIR = THIS_DIR / "_mapa"

RE_CNJ = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')

# Seletores da TABELA de processos já cadastrados no PUSH
SELETORES_TABELA = [
    "table[id*='pushTable']",
    "table[id*='processos']",
    "table.rich-table",
    "table[id*='listView']",
    "table",
]

# Seletores do botão "próxima página" (paginação)
SELETORES_NEXT = [
    "a[title='Próxima página']",
    "a[title='Próxima']",
    "a[title='Next']",
    ".rich-datascr-button:has-text('»')",
    ".rich-datascr-button:has-text('>')",
    "td.rich-datascr-button[onclick*='next']",
    "a:has-text('Próxima')",
    "a:has-text('>>')",
]


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {
        "INFO": "\u2139",
        "OK": "\u2713",
        "ERRO": "\u2717",
        "AVISO": "\u26a0",
        "MAPA": "\u25b6",
    }.get(level, "\u00b7")
    print(f"  [{ts}] {prefix} {msg}")


# ============================================================
# BROWSER — CDP ou standalone (COPIADO de incluir_push.py)
# ============================================================

async def conectar_cdp(porta=9222):
    cdp_url = f"http://127.0.0.1:{porta}"
    log(f"Conectando ao Chrome via CDP em {cdp_url}...")
    pw = await async_playwright().start()
    try:
        browser = await pw.chromium.connect_over_cdp(cdp_url)
    except Exception as e:
        log(f"CDP não disponível na porta {porta}: {e}", "ERRO")
        log("Tentando abrir Chromium standalone...", "AVISO")
        return await abrir_browser_standalone()

    log("Conectado ao Chrome via CDP!", "OK")
    contexts = browser.contexts
    if not contexts:
        context = await browser.new_context()
    else:
        context = contexts[0]

    pages = context.pages
    page = None
    for p in pages:
        if "blank" not in p.url:
            page = p
            break
    if not page:
        page = pages[0] if pages else await context.new_page()

    return pw, browser, page


async def abrir_browser_standalone():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA),
        headless=False,
        slow_mo=400,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
        ],
        viewport={"width": 1280, "height": 900},
    )
    page = browser.pages[0] if browser.pages else await browser.new_page()
    return pw, browser, page


# ============================================================
# LOGIN VIDAAS (COPIADO de incluir_push.py)
# ============================================================

async def aguardar_login(page):
    log("Abrindo PJe...")
    await page.goto(PJE_LOGIN, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(2000)

    url = page.url.lower()
    if "login" not in url and "sso" not in url and "gov.br" not in url:
        log("Já autenticado (cookies salvos)", "OK")
        return True

    log("AGUARDANDO LOGIN VIDAAS — autentique no browser", "AVISO")
    print()
    print("  >>> Faça login no PJe via VidaaS (gov.br) <<<")
    print()

    for i in range(300):
        await page.wait_for_timeout(1000)
        url = page.url.lower()
        if "login" not in url and "sso" not in url and "gov.br" not in url:
            log("Login detectado!", "OK")
            await page.wait_for_timeout(3000)
            return True
        if i > 0 and i % 30 == 0:
            log(f"Ainda aguardando login... ({i}s)", "AVISO")

    log("Timeout esperando login (5 min)", "ERRO")
    return False


# ============================================================
# NAVEGAR AO PUSH (listagem)
# ============================================================

async def navegar_listagem_push(page):
    """Abre a listagem do PUSH (não o form de inclusão)."""
    log("Navegando à listagem do PUSH...")
    for url in [PJE_PUSH, PJE_PUSH_ALT]:
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2500)

            url_atual = page.url.lower()
            if "login" in url_atual or "sso" in url_atual:
                log("Sessão expirou — refaça login", "ERRO")
                return False

            # Busca indício de tabela OU link "listar/consultar"
            for sel in SELETORES_TABELA:
                try:
                    el = page.locator(sel).first
                    if await el.is_visible(timeout=2000):
                        log(f"Listagem PUSH carregada ({url})", "OK")
                        return True
                except Exception:
                    continue

            # Se não tem tabela visível, tenta clicar em links que levam à listagem
            for texto in ["Consultar", "Listar", "Pesquisar"]:
                try:
                    link = page.locator(f"a:has-text('{texto}')").first
                    if await link.is_visible(timeout=1500):
                        await link.click()
                        await page.wait_for_timeout(2500)
                        log(f"Clicou em '{texto}'", "OK")
                        return True
                except Exception:
                    continue
        except Exception as e:
            log(f"Erro ao navegar {url}: {e}", "AVISO")
            continue

    log("Não encontrei a listagem do PUSH", "ERRO")
    return False


# ============================================================
# EXTRAÇÃO — CNJs + observações da página atual
# ============================================================

async def extrair_pagina_atual(page):
    """Varre a página atual e retorna lista de tuplas (cnj, observacao)."""
    resultados = []

    # 1) Tenta via linhas de tabela
    try:
        linhas = await page.locator("tr").all()
        for tr in linhas:
            try:
                texto = (await tr.inner_text()).strip()
                if not texto:
                    continue
                matches = RE_CNJ.findall(texto)
                if not matches:
                    continue
                cnj = matches[0]
                # Heurística simples para observação: resto do texto sem o CNJ
                resto = texto.replace(cnj, "").strip()
                # Remove tabs/quebras
                resto = re.sub(r"\s+", " ", resto)[:120]
                resultados.append((cnj, resto))
            except Exception:
                continue
    except Exception:
        pass

    # 2) Fallback: varrer body todo
    if not resultados:
        try:
            body = await page.inner_text("body")
            for cnj in set(RE_CNJ.findall(body)):
                resultados.append((cnj, ""))
        except Exception:
            pass

    # Dedup preservando ordem
    vistos = set()
    dedup = []
    for cnj, obs in resultados:
        if cnj in vistos:
            continue
        vistos.add(cnj)
        dedup.append((cnj, obs))
    return dedup


async def tentar_proxima_pagina(page):
    """Retorna True se conseguiu avançar para a próxima página."""
    for sel in SELETORES_NEXT:
        try:
            btn = page.locator(sel).first
            if not await btn.is_visible(timeout=1500):
                continue
            # Verifica se botão está desabilitado (última página)
            classe = (await btn.get_attribute("class") or "").lower()
            disabled = await btn.get_attribute("disabled")
            if "disabled" in classe or disabled:
                return False
            await btn.click()
            await page.wait_for_timeout(2500)
            return True
        except Exception:
            continue
    return False


# ============================================================
# VARREDURA COMPLETA
# ============================================================

async def mapear_todas_paginas(page, max_paginas=200):
    """Itera por todas as páginas e retorna dict {cnj: observacao}."""
    mapa = {}
    pagina = 1

    while pagina <= max_paginas:
        log(f"Lendo página {pagina}...", "MAPA")
        resultados = await extrair_pagina_atual(page)
        novos = 0
        for cnj, obs in resultados:
            if cnj not in mapa:
                mapa[cnj] = obs
                novos += 1
        log(f"  Página {pagina}: {len(resultados)} linhas, {novos} CNJs novos (total {len(mapa)})", "INFO")

        if not resultados:
            log("Página sem CNJs — parando", "AVISO")
            break

        avancou = await tentar_proxima_pagina(page)
        if not avancou:
            log(f"Fim da paginação na página {pagina}", "OK")
            break

        # Se avançou mas sessão expirou, aborta
        url_atual = page.url.lower()
        if "login" in url_atual or "sso" in url_atual:
            log("Sessão expirou durante varredura", "ERRO")
            break

        pagina += 1

    return mapa


# ============================================================
# SALVAR JSON
# ============================================================

def salvar_mapa(mapa):
    MAPA_DIR.mkdir(parents=True, exist_ok=True)
    hoje = datetime.now().strftime("%Y-%m-%d")
    nome = PUSH_MAPA_FILE.format(data=hoje) if "{data}" in PUSH_MAPA_FILE else f"push_atual_{hoje}.json"
    path = MAPA_DIR / nome

    cnjs = sorted(mapa.keys())
    payload = {
        "data": hoje,
        "gerado_em": datetime.now().isoformat(),
        "total": len(cnjs),
        "cnjs": cnjs,
        "observacoes_por_cnj": {k: v for k, v in mapa.items() if v},
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    log(f"Mapa salvo: {path}", "OK")
    return path


# ============================================================
# MAIN
# ============================================================

async def main():
    parser = argparse.ArgumentParser(description="Mapear CNJs já cadastrados no PUSH do PJe TJMG")
    parser.add_argument("--porta", type=int, default=9222, help="Porta CDP (padrão 9222)")
    parser.add_argument("--standalone", action="store_true", help="Chromium próprio em vez de CDP")
    parser.add_argument("--max-paginas", type=int, default=200, help="Limite de páginas (safety)")
    args = parser.parse_args()

    if args.standalone:
        pw, browser, page = await abrir_browser_standalone()
    else:
        pw, browser, page = await conectar_cdp(args.porta)

    try:
        if not await aguardar_login(page):
            log("Login falhou — encerrando", "ERRO")
            return

        if not await navegar_listagem_push(page):
            log("Não consegui acessar listagem PUSH", "ERRO")
            return

        mapa = await mapear_todas_paginas(page, max_paginas=args.max_paginas)
        salvar_mapa(mapa)
        print(f"Mapeou {len(mapa)} CNJs")

    finally:
        try:
            if args.standalone:
                await browser.close()
        except Exception:
            pass
        try:
            await pw.stop()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
