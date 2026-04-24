#!/usr/bin/env python3
"""Upgrade das FICHAs PARCIAL_COM_CNJ_SEM_VALOR_NA_EMENTA abrindo o inteiro teor no TJMG.

Fluxo:
1. Varre Casos-Reais/<regiao>/*.FICHA.json com classificacao PARCIAL_COM_CNJ_SEM_VALOR_NA_EMENTA
2. Abre browser persistente (_perfil_tjmg/ — sessao validada) em cada url_ementa_semformato
3. Se aparecer captcha: pausa pro usuario digitar no browser
4. Extrai texto do inteiro teor (inner_text body)
5. Re-roda extract_valor com whitelist pericial rigorosa (mesma do parser v2)
6. Se valor achado: promove FICHA -> REAL_COM_CNJ_E_VALOR, salva PDF, reescreve MD com trecho
7. Se nao: marca necessita_inteiro_teor=false e adiciona nota 'valor nao citado no inteiro teor'

Uso:
  python3 upgrade_parciais_inteiroteor.py                # roda em todas as regioes
  python3 upgrade_parciais_inteiroteor.py --regiao GV-e-regiao

Nao criar/modificar arquivo fora da propria pasta do caso.
"""
from __future__ import annotations
import argparse
import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).resolve().parent
PROFILE_DIR = BASE_DIR / "_perfil_tjmg"
OUTPUT_DIR = Path("/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/Banco-Transversal/Honorarios-Periciais/Casos-Reais")


def wait_user(msg: str):
    print(f"\n>>> {msg}")
    print(">>> ENTER aqui para continuar...")
    sys.stdin.readline()


def extract_valor_pericial(texto: str) -> tuple[int | None, str | None]:
    """Mesma whitelist/blacklist do parser v2."""
    whitelist = re.compile(
        r"honor[aá]rios?\s+(pericia[li]|do\s+perito|ao\s+perito)|"
        r"verba\s+pericial|"
        r"remunera[cç][aã]o\s+do\s+perito|"
        r"honor[aá]rios?\s+arbitrad[oa]s?\s+(ao|em\s+favor\s+do)\s+perito|"
        r"perito.{0,40}honor[aá]rios?|"
        r"honor[aá]rios?.{0,40}perito",
        re.IGNORECASE,
    )
    blacklist = re.compile(
        r"honor[aá]rios?\s+(advocat[ií]cios?|sucumbencia[li]s?|contratua[li]s?)|"
        r"danos?\s+morais|"
        r"indeniza[cç][aã]o",
        re.IGNORECASE,
    )
    for m in re.finditer(r"R\$\s*([\d\.]+,\d{2})", texto):
        start = max(0, m.start() - 200)
        end = min(len(texto), m.end() + 200)
        janela = texto[start:end]
        if not whitelist.search(janela):
            continue
        if blacklist.search(janela):
            continue
        raw = m.group(1).replace(".", "").replace(",", ".")
        try:
            centavos = int(float(raw) * 100)
        except ValueError:
            continue
        if centavos > 5_000_000 or centavos < 5_000:
            continue
        return centavos, janela.strip()
    return None, None


TIPOS_FORA_DE_ESCOPO = {"engenharia-civil", "contabil", "grafotecnica"}


def listar_parciais(regiao_filtro: str | None, incluir_fora_escopo: bool = False):
    """Retorna lista de (path_ficha, dict_ficha) que precisam upgrade.
    Filtra tipos NAO medicos por padrao (engenharia-civil, contabil, grafotecnica)."""
    resultado = []
    fora_escopo = []
    if not OUTPUT_DIR.exists():
        return resultado
    for regiao_dir in OUTPUT_DIR.iterdir():
        if not regiao_dir.is_dir():
            continue
        if regiao_filtro and regiao_dir.name != regiao_filtro:
            continue
        for ficha_path in regiao_dir.glob("*.FICHA.json"):
            try:
                data = json.loads(ficha_path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"[skip] {ficha_path.name}: json invalido ({e})")
                continue
            classif = data.get("classificacao", "")
            if classif != "PARCIAL_COM_CNJ_SEM_VALOR_NA_EMENTA":
                continue
            tipo = data.get("tipo_pericia_heuristica", "")
            if tipo in TIPOS_FORA_DE_ESCOPO and not incluir_fora_escopo:
                fora_escopo.append((ficha_path, tipo))
                continue
            resultado.append((ficha_path, data))
    if fora_escopo:
        print(f"[filtro] {len(fora_escopo)} ficha(s) excluidas (perícia nao-medica):")
        for fp, t in fora_escopo:
            print(f"  - {fp.parent.name}/{fp.name} [tipo={t}]")
    return resultado


async def upgrade_um(page, ficha_path: Path, ficha: dict) -> str:
    """Abre url_ementa_semformato, re-extrai valor, atualiza trinity.
    Retorna status: 'UPGRADE', 'NO_VALOR', 'ERRO'."""
    url = ficha.get("fonte_url")
    if not url:
        return "ERRO"

    slug = ficha_path.stem.replace(".FICHA", "")
    regiao_dir = ficha_path.parent

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
        await page.wait_for_timeout(2000)

        content = await page.content()
        if 'captcha_image' in content or 'Digite os números' in content or 'captcha.svl' in content:
            wait_user(f"Captcha em {slug}. Digite no browser e aperte ENTER aqui.")
            await page.wait_for_timeout(1500)

        texto = await page.inner_text("body")
        valor, trecho = extract_valor_pericial(texto)

        if valor is None:
            ficha["necessita_inteiro_teor"] = False
            ficha["nota_upgrade"] = f"inteiro_teor aberto em {datetime.now().isoformat()} — valor NAO citado"
            ficha_path.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
            return "NO_VALOR"

        # UPGRADE
        ficha["valor_fixado_reais"] = valor / 100
        ficha["valor_fonte"] = "inteiro_teor_tjmg"
        ficha["valor_trecho_contexto"] = trecho
        ficha["classificacao"] = "REAL_COM_CNJ_E_VALOR"
        ficha["data_upgrade"] = datetime.now().isoformat()
        ficha["necessita_inteiro_teor"] = False
        ficha_path.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")

        # PDF
        pdf_path = regiao_dir / f"{slug}.pdf"
        try:
            await page.emulate_media(media="screen")
            await page.pdf(path=str(pdf_path), format="A4", print_background=True)
        except Exception as e:
            print(f"  [aviso PDF falhou] {e}")

        # MD append trecho
        md_path = regiao_dir / f"{slug}.md"
        if md_path.exists():
            old = md_path.read_text(encoding="utf-8")
            adendo = (
                f"\n\n## UPGRADE inteiro_teor ({datetime.now().isoformat()})\n\n"
                f"- Valor fixado: **R$ {valor/100:.2f}**\n"
                f"- Trecho:\n\n> {trecho}\n"
                f"- Classificacao agora: REAL_COM_CNJ_E_VALOR\n"
            )
            md_path.write_text(old + adendo, encoding="utf-8")

        return "UPGRADE"
    except Exception as e:
        print(f"  ERRO upgrade {slug}: {e}")
        return "ERRO"


async def executar(regiao_filtro: str | None, dry_run: bool):
    parciais = listar_parciais(regiao_filtro)
    print(f"[upgrader] {len(parciais)} fichas PARCIAL_COM_CNJ_SEM_VALOR_NA_EMENTA encontradas")
    for fp, _ in parciais:
        print(f"  - {fp.parent.name}/{fp.name}")
    if dry_run:
        return
    if not parciais:
        return

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
            args=["--disable-blink-features=AutomationControlled"],
        )
        try:
            from playwright_stealth import Stealth
            await Stealth().apply_stealth_async(context)
        except Exception:
            pass

        page = context.pages[0] if context.pages else await context.new_page()

        stats = {"UPGRADE": 0, "NO_VALOR": 0, "ERRO": 0}
        for i, (fp, ficha) in enumerate(parciais, 1):
            slug = fp.stem.replace(".FICHA", "")
            print(f"\n[{i}/{len(parciais)}] {slug}")
            status = await upgrade_um(page, fp, ficha)
            stats[status] += 1
            print(f"  -> {status}")
            await page.wait_for_timeout(1500)

        print("\n=== RESUMO UPGRADE ===")
        for k, v in stats.items():
            print(f"  {k}: {v}")

        wait_user("Fim. ENTER pra fechar browser.")
        await context.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regiao", default=None, help="Filtra por nome de subpasta, ex: GV-e-regiao")
    ap.add_argument("--dry-run", action="store_true", help="Lista sem executar")
    args = ap.parse_args()
    asyncio.run(executar(args.regiao, args.dry_run))


if __name__ == "__main__":
    main()
