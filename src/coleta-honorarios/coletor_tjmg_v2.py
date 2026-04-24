#!/usr/bin/env python3
"""Coletor TJMG v2 — pausa manual para captcha de 5 digitos.

Fluxo:
1. Abre browser visivel com perfil persistente _perfil_tjmg/
2. Navega form, preenche busca, submete
3. PAUSA: usuario digita captcha na janela
4. Apos captcha validado e resultados aparecerem, usuario aperta Enter no terminal
5. Script extrai acordaos da pagina atual
6. Para cada acordao: abre em nova tab, PAUSA p/ captcha de inteiroTeor, salva trinity

Refs PYTHON-BASE/03-FALHAS-SOLUCOES:
- PW-010 stealth
- PW-012 launch_persistent_context
- PW-026 perfil persistente aumenta score
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
    digits = re.sub(r"\D", "", cnj or "")
    return digits[-13:] if len(digits) >= 13 else digits or "sem-cnj"


def extract_valor(texto: str) -> int | None:
    m = re.search(r"R\$\s*([\d\.]+,\d{2})", texto)
    if not m:
        return None
    raw = m.group(1).replace(".", "").replace(",", ".")
    try:
        return int(float(raw) * 100)
    except ValueError:
        return None


def classificar_comarca(texto: str) -> str:
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


def wait_user(msg: str):
    print(f"\n>>> {msg}")
    print(">>> Aperte ENTER aqui no terminal para continuar...")
    sys.stdin.readline()


async def extrair_links(page):
    """Extrai links de acordaos da pagina atual de resultados TJMG."""
    return await page.evaluate(
        """() => {
            const out = [];
            // Varredura ampla
            document.querySelectorAll('a').forEach(a => {
                const href = a.href || '';
                const txt = (a.textContent || '').trim();
                const lower = href.toLowerCase();
                if (lower.includes('inteiroteor') ||
                    lower.includes('espelhoacordao') ||
                    lower.includes('numeroregistro') ||
                    txt.match(/\\d{7}-?\\d{2}\\.?\\d{4}\\.?8?\\.?13/)) {
                    out.push({href, txt});
                }
            });
            return out;
        }"""
    )


async def coletar(busca: str, max_resultados: int):
    print(f"[v2] busca='{busca}' max={max_resultados}")
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
            print("[v2] stealth aplicado")
        except Exception as e:
            print(f"[v2] aviso: stealth falhou ({e})")

        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_navigation_timeout(60_000)

        print(f"[v2] navegando {TJMG_URL}")
        await page.goto(TJMG_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        campo = await page.wait_for_selector('input[name="palavras"]', timeout=10000)
        await campo.fill(busca)
        print(f"[v2] busca preenchida: {busca}")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(3000)

        # PAUSA 1: captcha inicial
        wait_user("DIGITE O CAPTCHA de 5 digitos na JANELA DO BROWSER e espere aparecer os resultados.")

        # Snapshot pos-captcha
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        (RAW_DIR / f"pos-captcha-{ts}.html").write_text(await page.content(), encoding="utf-8")
        await page.screenshot(path=str(RAW_DIR / f"pos-captcha-{ts}.png"), full_page=True)

        links = await extrair_links(page)
        print(f"[v2] {len(links)} links candidatos encontrados")

        if not links:
            print("[v2] Zero links. HTML salvo em _raw_html/pos-captcha-*.html")
            print("[v2] Possivel: pagina de lista usa iframe ou JS dinamico. Investigar HTML.")
            await context.close()
            return

        # Paginacao: se houver mais paginas, coletar tambem
        paginas_vistas = 1
        todos_links = list(links)
        while len(todos_links) < max_resultados * 2 and paginas_vistas < 5:
            # Procurar link "Proximo"
            prox = await page.query_selector('a:has-text("Próximo"), a:has-text("Proximo"), a:has-text(">>")')
            if not prox:
                break
            try:
                await prox.click()
                await page.wait_for_timeout(3000)
                # Pode re-trigger captcha
                content = await page.content()
                if 'captcha_image' in content or 'Digite os números' in content:
                    wait_user(f"Captcha de paginacao apareceu (pag {paginas_vistas+1}). Digite no browser.")
                mais = await extrair_links(page)
                novos = [l for l in mais if l['href'] not in {x['href'] for x in todos_links}]
                todos_links.extend(novos)
                paginas_vistas += 1
                print(f"[v2] pag {paginas_vistas}: +{len(novos)} links (total {len(todos_links)})")
            except Exception as e:
                print(f"[v2] erro paginacao: {e}")
                break

        salvos = 0
        for i, ln in enumerate(todos_links[:max_resultados]):
            print(f"\n[{i+1}/{min(len(todos_links), max_resultados)}] {ln['txt'][:80]}")
            try:
                novo = await context.new_page()
                await novo.goto(ln["href"], wait_until="domcontentloaded", timeout=30000)
                await novo.wait_for_timeout(2000)

                # TJMG pode pedir captcha de novo no inteiroTeor
                content = await novo.content()
                if 'captcha_image' in content or 'Digite os números' in content:
                    wait_user(f"Captcha no acordao {i+1}. Digite no browser.")
                    await novo.wait_for_timeout(1500)

                texto = await novo.inner_text("body")
                cnj = re.search(r"\d{7}-?\d{2}\.?\d{4}\.?8?\.?13\.?\d{4}", texto)
                valor = extract_valor(texto)

                if cnj and valor:
                    cnj_str = cnj.group(0)
                    slug = f"tjmg-{slugify_cnj(cnj_str)}-v{valor//100}"
                    regiao = classificar_comarca(texto)
                    destino = OUTPUT_DIR / regiao
                    destino.mkdir(parents=True, exist_ok=True)

                    pdf_path = destino / f"{slug}.pdf"
                    await novo.emulate_media(media="screen")
                    await novo.pdf(path=str(pdf_path), format="A4", print_background=True)

                    md_path = destino / f"{slug}.md"
                    md_path.write_text(
                        f"# Acordao TJMG — {slug}\n\n"
                        f"- CNJ: {cnj_str}\n"
                        f"- Valor fixado: R$ {valor/100:.2f}\n"
                        f"- Fonte: {ln['href']}\n"
                        f"- Coletado: {datetime.now().isoformat()}\n\n"
                        f"## Trecho relevante\n\n{texto[:3000]}\n",
                        encoding="utf-8",
                    )
                    ficha = {
                        "cnj": cnj_str,
                        "tribunal": "TJMG",
                        "comarca": regiao,
                        "valor_fixado_reais": valor / 100,
                        "data_coleta": datetime.now().isoformat(),
                        "fonte_url": ln["href"],
                        "classificacao": "REAL_COM_CNJ",
                        "busca_origem": busca,
                    }
                    (destino / f"{slug}.FICHA.json").write_text(
                        json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                    salvos += 1
                    print(f"  OK -> {regiao}/{slug} R$ {valor/100:.2f}")
                else:
                    print(f"  SKIP (cnj={bool(cnj)} valor={valor})")
                await novo.close()
            except Exception as e:
                print(f"  ERRO: {e}")

        print(f"\n[v2] FIM. Salvos: {salvos}/{min(len(todos_links), max_resultados)}")
        wait_user("Aperte Enter para fechar o browser (ou Ctrl+C).")
        await context.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--busca", required=True)
    parser.add_argument("--max", type=int, default=10)
    args = parser.parse_args()
    asyncio.run(coletar(args.busca, args.max))


if __name__ == "__main__":
    main()
