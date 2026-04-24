#!/usr/bin/env python3
"""Coletor TJMG v3 — 1 browser, 1 captcha inicial, N comarcas em abas.

Diferenças do v2:
- Sem page.screenshot (evita timeout de fontes)
- Sem wait_user a cada acordao — só 1 captcha inicial
- wait_for_selector da tabela de resultados antes de page.content()
- linhasPorPagina=50 via URL (em vez de 10 default)
- Sessao TJMG validada uma vez serve pra todas as buscas em ordem
- Salva 1 HTML bruto por comarca em _raw_html/<ts>_<slug>.html
- Parser roda depois em batch (nao faz parsing aqui)

Uso:
  python3 baixar_tjmg_v3.py
  python3 baixar_tjmg_v3.py --comarcas "Muriae,Uberlandia,Belo Horizonte,Montes Claros"

Refs PYTHON-BASE:
- PW-012 launch_persistent_context
- PW-026 perfil persistente aumenta score anti-bot
- TJ-001 captcha numerico 5 digitos (nova falha, catalogar)
- TJ-006 cache stale em page.content() antes de DOM novo carregar (falha nova)
"""
from __future__ import annotations
import argparse
import asyncio
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

BASE_DIR = Path(__file__).resolve().parent
PROFILE_DIR = BASE_DIR / "_perfil_tjmg_v3"
RAW_DIR = BASE_DIR / "_raw_html"
TJMG_FORM_URL = "https://www5.tjmg.jus.br/jurisprudencia/formEspelhoAcordao.do"
TJMG_SEARCH_URL = "https://www5.tjmg.jus.br/jurisprudencia/pesquisaPalavrasEspelhoAcordao.do"

PROFILE_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

COMARCAS_PADRAO = [
    ("honorarios periciais medico Muriae", "Muriae"),
    ("honorarios periciais medico Uberlandia", "Uberlandia"),
    ("honorarios pericia medica Belo Horizonte", "Belo-Horizonte"),
    ("honorarios periciais medico Montes Claros", "Montes-Claros"),
]


def slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-")
    return s.lower()


def wait_user(msg: str):
    print(f"\n>>> {msg}")
    print(">>> ENTER aqui no terminal para continuar...")
    sys.stdin.readline()


async def aguardar_lista_carregada(page, timeout_ms: int = 60_000) -> str:
    """Espera DOM da lista aparecer. Retorna motivo da conclusao."""
    # Seletor primario — link de acordao na lista
    try:
        await page.wait_for_selector(
            'a.linkListaEspelhoAcordaos, a[href*="ementaSemFormatacao.do"]',
            timeout=timeout_ms,
        )
        return "selector_lista_ok"
    except PWTimeout:
        pass
    # Seletor alternativo — mensagem "nenhum resultado"
    try:
        await page.wait_for_selector('text=/nenhum.{0,20}resultado|sem.{0,20}resultados/i', timeout=5_000)
        return "sem_resultados"
    except PWTimeout:
        pass
    # Seletor de captcha persistente
    try:
        await page.wait_for_selector('img[src*="captcha"]', timeout=5_000)
        return "captcha_ainda_presente"
    except PWTimeout:
        pass
    return "timeout_desconhecido"


async def submeter_busca_e_aguardar(page, termo: str) -> str:
    """Preenche o form, submete, aguarda resposta. Retorna motivo."""
    await page.goto(TJMG_FORM_URL, wait_until="domcontentloaded", timeout=30_000)
    await page.wait_for_timeout(1500)

    # preenche campo palavras e seta linhasPorPagina=50 antes de submeter
    campo = await page.wait_for_selector('input[name="palavras"]', timeout=10_000)
    await campo.fill(termo)

    # tenta setar linhasPorPagina=50 (se existir input oculto ou select)
    try:
        await page.evaluate("""
            () => {
                const sel = document.querySelector('select[name="linhasPorPagina"]');
                if (sel) { sel.value = '50'; }
                const inp = document.querySelector('input[name="linhasPorPagina"]');
                if (inp) { inp.value = '50'; }
            }
        """)
    except Exception:
        pass

    # submete
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(2000)

    motivo = await aguardar_lista_carregada(page, timeout_ms=60_000)
    return motivo


async def coletar(comarcas, timeout_captcha_s: int = 600):
    ts_sessao = datetime.now().strftime("%Y%m%d-%H%M")
    print(f"[v3] sessao {ts_sessao} | {len(comarcas)} comarca(s)")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        try:
            from playwright_stealth import Stealth
            await Stealth().apply_stealth_async(context)
            print("[v3] stealth aplicado")
        except Exception as e:
            print(f"[v3] aviso stealth: {e}")

        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_navigation_timeout(45_000)

        # === CAPTCHA INICIAL ===
        # Submete primeira busca pra trigger do captcha
        termo0, slug0 = comarcas[0]
        print(f"\n[v3] submetendo 1a busca: {termo0}")
        motivo = await submeter_busca_e_aguardar(page, termo0)
        print(f"[v3] motivo pos-submit: {motivo}")

        if motivo in ("captcha_ainda_presente", "timeout_desconhecido"):
            wait_user(f"CAPTCHA INICIAL: digite no browser os 5 digitos. NAO APERTE ENTER AQUI ATE a LISTA estar VISIVEL no browser (ementa, CNJ, titulo 'Espelhos de Acordaos').")
            # re-espera lista carregar
            motivo = await aguardar_lista_carregada(page, timeout_ms=60_000)
            print(f"[v3] motivo pos-captcha: {motivo}")

        # Salva HTML da primeira busca
        if motivo == "selector_lista_ok":
            html_path = RAW_DIR / f"{ts_sessao}_{slug0}.html"
            html_path.write_text(await page.content(), encoding="utf-8")
            print(f"  SALVO: {html_path.name} ({html_path.stat().st_size} bytes)")
        else:
            print(f"  SKIP: {slug0} ({motivo})")

        # === DEMAIS BUSCAS ===
        for termo, slug in comarcas[1:]:
            print(f"\n[v3] busca: {termo}")
            motivo = await submeter_busca_e_aguardar(page, termo)
            print(f"[v3] motivo: {motivo}")

            # Se pedir captcha de novo (sessao expirou), pausa
            if motivo == "captcha_ainda_presente":
                wait_user(f"Captcha pediu de novo para '{termo}'. Digite no browser, espera lista, depois ENTER aqui.")
                motivo = await aguardar_lista_carregada(page, timeout_ms=60_000)

            if motivo == "selector_lista_ok":
                html_path = RAW_DIR / f"{ts_sessao}_{slug}.html"
                html_path.write_text(await page.content(), encoding="utf-8")
                print(f"  SALVO: {html_path.name} ({html_path.stat().st_size} bytes)")
            elif motivo == "sem_resultados":
                print(f"  SEM RESULTADOS TJMG para '{termo}'")
            else:
                print(f"  SKIP: {slug} ({motivo})")

            await page.wait_for_timeout(2000)

        print(f"\n[v3] FIM. HTMLs em {RAW_DIR}/{ts_sessao}_*.html")
        print("[v3] Rode agora o parser em batch:")
        print(f"     python3 parsear_resultados_tjmg.py <cada html> --busca '<termo>'")
        print("[v3] Ou o consolidador (parser_batch) que varre todos os HTMLs da sessao.")

        wait_user("ENTER pra fechar o browser (ou Ctrl+C)")
        await context.close()


def parse_lista_arg(s: str):
    items = [x.strip() for x in s.split(",") if x.strip()]
    return [(f"honorarios periciais medico {x}", slugify(x)) for x in items]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--comarcas", default=None,
                    help="Lista vigulada de comarcas, ex: 'Muriae,Uberlandia,BH'")
    args = ap.parse_args()
    comarcas = parse_lista_arg(args.comarcas) if args.comarcas else COMARCAS_PADRAO
    asyncio.run(coletar(comarcas))


if __name__ == "__main__":
    main()
