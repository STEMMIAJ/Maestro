#!/usr/bin/env python3
"""Coletor TJMG jurisprudencia — honorarios periciais.

Uso:
  # Primeira execucao (browser visivel, resolve captcha manual):
  python3 coletor_tjmg_jurisprudencia.py --busca "honorarios periciais Governador Valadares"

  # Re-uso com sessao salva:
  python3 coletor_tjmg_jurisprudencia.py --busca "honorarios periciais Ipatinga" --headless

Refs (PYTHON-BASE/03-FALHAS-SOLUCOES):
- PW-010: stealth + --disable-blink-features=AutomationControlled
- PW-012: launch_persistent_context para manter sessao
- PW-026: perfil persistente aumenta score reCAPTCHA
"""
from __future__ import annotations
import argparse
import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

BASE_DIR = Path(__file__).resolve().parent
PROFILE_DIR = BASE_DIR / "_perfil_tjmg"
OUTPUT_DIR = Path("/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/Banco-Transversal/Honorarios-Periciais/Casos-Reais")
RAW_DIR = BASE_DIR / "_raw_html"
TJMG_URL = "https://www5.tjmg.jus.br/jurisprudencia/formEspelhoAcordao.do"

PROFILE_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)


def slugify_cnj(cnj: str) -> str:
    """CNJ completo (20 digitos+) -> slug curto sem pontuacao."""
    digits = re.sub(r"\D", "", cnj or "")
    return digits[-13:] if len(digits) >= 13 else digits or "sem-cnj"


def extract_valor(texto: str) -> int | None:
    """Procura valor R$ no texto do acordao."""
    m = re.search(r"R\$\s*([\d\.]+,\d{2})", texto)
    if not m:
        return None
    raw = m.group(1).replace(".", "").replace(",", ".")
    try:
        return int(float(raw) * 100)  # centavos
    except ValueError:
        return None


def classificar_comarca(texto: str) -> str:
    """Heuristica de comarca -> pasta de destino."""
    lower = texto.lower()
    if any(c in lower for c in ["governador valadares", "ipatinga", "coronel fabriciano",
                                 "timoteo", "caratinga", "aimores", "mantena",
                                 "teofilo otoni", "nanuque"]):
        return "GV-e-regiao"
    if any(c in lower for c in ["juiz de fora", "barbacena", "muriae", "manhuacu",
                                 "ponte nova", "santos dumont"]):
        return "Zona-Mata-Sul"
    if any(c in lower for c in ["uberlandia", "uberaba", "ituiutaba", "araxa", "patos de minas"]):
        return "Triangulo-Alto-Paranaiba"
    if any(c in lower for c in ["belo horizonte", "contagem", "betim", "santa luzia",
                                 "ribeirao das neves", "nova lima", "lagoa santa", "sete lagoas"]):
        return "BH-metropolitana"
    if any(c in lower for c in ["montes claros", "pirapora", "januaria", "janauba", "salinas"]):
        return "Norte-Mineiro"
    return "Outros-regiao-MG"


async def coletar(busca: str, headless: bool, max_resultados: int):
    print(f"[coletor] busca='{busca}' headless={headless} max={max_resultados}")
    async with async_playwright() as p:
        # launch_persistent_context para manter sessao entre execucoes (PW-012)
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            viewport={"width": 1400, "height": 900},
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
            args=[
                "--disable-blink-features=AutomationControlled",  # PW-010
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        # Stealth (PW-010)
        try:
            from playwright_stealth import Stealth
            stealth = Stealth()
            await stealth.apply_stealth_async(context)
        except Exception as e:
            print(f"[coletor] aviso: stealth falhou ({e}), prosseguindo sem")

        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_navigation_timeout(60_000)  # PJE-009

        print(f"[coletor] navegando {TJMG_URL}")
        await page.goto(TJMG_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Snapshot inicial para debug
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        (RAW_DIR / f"form-{ts}.html").write_text(await page.content(), encoding="utf-8")
        await page.screenshot(path=str(RAW_DIR / f"form-{ts}.png"), full_page=True)

        # Detectar campo de busca
        seletores_candidatos = [
            'input[name="palavras"]',
            'input[id="palavras"]',
            'textarea[name="palavras"]',
            'input[type="text"][name*="palavra"]',
        ]
        campo = None
        for sel in seletores_candidatos:
            try:
                campo = await page.wait_for_selector(sel, timeout=3000)
                if campo:
                    print(f"[coletor] campo busca encontrado: {sel}")
                    break
            except PWTimeout:
                continue

        if not campo:
            print("[coletor] CAMPO DE BUSCA NAO ENCONTRADO. Verifique HTML salvo em _raw_html/")
            print("[coletor] Se viu reCAPTCHA/Cloudflare, resolva manualmente na janela e aperte Enter")
            if not headless:
                input("Pressione Enter apos resolver captcha e carregar o formulario...")
                # re-tentar
                for sel in seletores_candidatos:
                    try:
                        campo = await page.wait_for_selector(sel, timeout=3000)
                        if campo:
                            break
                    except PWTimeout:
                        continue
            if not campo:
                await context.close()
                return

        await campo.fill(busca)
        await page.keyboard.press("Enter")
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(3000)

        # Salvar resultado
        ts2 = datetime.now().strftime("%Y%m%d-%H%M%S")
        html_result = await page.content()
        (RAW_DIR / f"result-{ts2}.html").write_text(html_result, encoding="utf-8")
        await page.screenshot(path=str(RAW_DIR / f"result-{ts2}.png"), full_page=True)
        print(f"[coletor] resultado salvo em _raw_html/result-{ts2}.html")

        # Extrair links de acordaos (heuristica generica)
        links = await page.evaluate(
            """() => {
                const links = [];
                document.querySelectorAll('a').forEach(a => {
                    const href = a.href || '';
                    const txt = (a.textContent || '').trim();
                    if (href.includes('inteiroTeor') || href.includes('espelhoAcordao') || txt.match(/\\d{7}-\\d{2}\\.\\d{4}/)) {
                        links.push({href, txt});
                    }
                });
                return links;
            }"""
        )
        print(f"[coletor] {len(links)} links candidatos encontrados")

        for i, ln in enumerate(links[:max_resultados]):
            print(f"[{i+1}/{min(len(links), max_resultados)}] {ln['txt'][:60]}")
            try:
                novo = await context.new_page()
                await novo.goto(ln["href"], wait_until="domcontentloaded", timeout=30000)
                await novo.wait_for_timeout(2000)
                texto = await novo.inner_text("body")

                cnj = re.search(r"\d{7}-?\d{2}\.?\d{4}\.?\d{1}\.?\d{2}\.?\d{4}", texto)
                valor = extract_valor(texto)
                if cnj and valor:
                    cnj_str = cnj.group(0)
                    slug = f"tjmg-{slugify_cnj(cnj_str)}-v{valor//100}"
                    regiao = classificar_comarca(texto)
                    destino = OUTPUT_DIR / regiao
                    destino.mkdir(parents=True, exist_ok=True)

                    # Salvar PDF via print
                    pdf_path = destino / f"{slug}.pdf"
                    await novo.emulate_media(media="screen")
                    await novo.pdf(path=str(pdf_path), format="A4", print_background=True)

                    # Salvar MD
                    md_path = destino / f"{slug}.md"
                    md_path.write_text(
                        f"# Acordao TJMG — {slug}\n\n"
                        f"- CNJ: {cnj_str}\n"
                        f"- Valor fixado: R$ {valor/100:.2f}\n"
                        f"- Fonte: {ln['href']}\n\n"
                        f"## Trecho relevante\n\n{texto[:3000]}\n",
                        encoding="utf-8",
                    )

                    # Salvar FICHA
                    ficha = {
                        "cnj": cnj_str,
                        "tribunal": "TJMG",
                        "comarca": regiao,
                        "valor_fixado_reais": valor / 100,
                        "data_coleta": datetime.now().isoformat(),
                        "fonte_url": ln["href"],
                        "classificacao": "REAL_COM_CNJ",
                    }
                    (destino / f"{slug}.FICHA.json").write_text(
                        json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                    print(f"  -> {destino.name}/{slug} R$ {valor/100:.2f}")
                else:
                    print(f"  (sem CNJ={bool(cnj)} ou valor={valor})")
                await novo.close()
            except Exception as e:
                print(f"  ERRO: {e}")

        await context.close()
        print("[coletor] fim")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--busca", required=True, help='Ex: "honorarios periciais Governador Valadares"')
    parser.add_argument("--headless", action="store_true", help="Sem browser visivel (so apos 1a execucao com sessao salva)")
    parser.add_argument("--max", type=int, default=20, help="Max de resultados a baixar")
    args = parser.parse_args()
    asyncio.run(coletar(args.busca, args.headless, args.max))


if __name__ == "__main__":
    main()
