#!/usr/bin/env python3
"""
Automação PJe/AJ/AJG com Playwright standalone (sem Chrome em modo debug).
Abre Chromium próprio, faz login VidaaS (manual), depois automatiza tudo.

Uso:
  python3 pje_standalone.py --aj              # Lista nomeações AJ TJMG
  python3 pje_standalone.py --ajg             # Lista nomeações AJG Federal
  python3 pje_standalone.py --baixar CNJ...   # Baixa PDFs do PJe
  python3 pje_standalone.py --tudo            # AJ + AJG + baixar pendentes

Login VidaaS:
  O script abre o browser e espera você autenticar (~30s).
  Após login, tudo é automático.

IMPORTANTE: NUNCA clica em Aceitar ou Rejeitar. Somente leitura + download.
"""

import asyncio
import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("pip install playwright && playwright install chromium")
    sys.exit(1)

# Importar funções dos scripts existentes (diretório do próprio script)
_LOCAL_DIR = str(Path(__file__).parent)
if _LOCAL_DIR not in sys.path:
    sys.path.insert(0, _LOCAL_DIR)

# ============================================================
# CONFIGURAÇÃO
# ============================================================

AJ_URL = "https://aj.tjmg.jus.br/aj/internet/consultarNomeacoes.jsf"
AJG_URL = "https://ajg.cjf.jus.br/ajg2/internet/nomeacoes/consultanomeacoes.jsf"
PJE_URL = "https://pje.tjmg.jus.br/pje/login.seam"
PJE_PAINEL = "https://pje.tjmg.jus.br/pje/Painel/painel_usuario/Usuario.seam"

PROCESSOS_DIR = Path.home() / "stemmia-forense/data/processos"
DOWNLOAD_TIMEOUT = 300_000  # 5 min
USER_DATA = Path.home() / ".pje-browser-data"  # Salva cookies entre sessões

RE_CNJ = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ", "OK": "✓", "ERRO": "✗", "AVISO": "⚠"}.get(level, "·")
    print(f"  [{ts}] {prefix} {msg}")


# ============================================================
# BROWSER — Abrir com persistência de cookies
# ============================================================

async def abrir_browser():
    """Abre Chromium com dados persistentes (cookies salvos entre sessões)."""
    pw = await async_playwright().start()
    browser = await pw.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA),
        headless=False,  # Precisa ver para login VidaaS
        slow_mo=100,     # Mais estável em sites Java (PJe)
        args=[
            "--no-first-run",
            "--no-default-browser-check",
        ],
        viewport={"width": 1280, "height": 900},
        accept_downloads=True,
    )
    page = browser.pages[0] if browser.pages else await browser.new_page()
    return pw, browser, page


# ============================================================
# LOGIN — VidaaS (espera manual)
# ============================================================

async def login_vidaas(page, url_destino):
    """
    Navega para URL e detecta se precisa login.
    Se precisar, espera o usuário autenticar via VidaaS.
    Retorna True se logou com sucesso.
    """
    log(f"Abrindo {url_destino}...")
    await page.goto(url_destino, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(2000)

    url_atual = page.url.lower()

    # Já logado?
    if "login" not in url_atual and "sso" not in url_atual and "gov.br" not in url_atual:
        log("Já autenticado (cookies salvos)", "OK")
        return True

    # Precisa login — espera o usuário
    log("AGUARDANDO LOGIN VIDAAS — autentique no browser", "AVISO")
    log("(face, biometria ou código gov.br)")
    print()
    print("  >>> Faça login no browser que abriu <<<")
    print()

    # Espera até sair da tela de login (máx 5 min)
    for i in range(300):  # 300 x 1s = 5 min
        await page.wait_for_timeout(1000)
        url_atual = page.url.lower()

        # Detecta que saiu do login
        if "login" not in url_atual and "sso" not in url_atual and "gov.br" not in url_atual:
            log("Login detectado!", "OK")
            await page.wait_for_timeout(2000)  # Espera página carregar
            return True

        # A cada 30s lembra o usuário
        if i > 0 and i % 30 == 0:
            log(f"Ainda aguardando login... ({i}s)", "AVISO")

    log("Timeout esperando login (5 min)", "ERRO")
    return False


# ============================================================
# AJ TJMG — Lista nomeações
# ============================================================

async def listar_aj(page, situacao="AGUARDANDO ACEITE"):
    """Lista nomeações do AJ TJMG. Reutiliza lógica do consultar_aj.py."""
    if not await login_vidaas(page, AJ_URL):
        return []

    # Importar funções do script existente
    try:
        from consultar_aj import navegar_consulta, listar_nomeacoes
        await navegar_consulta(page)
        return await listar_nomeacoes(page, situacao=situacao)
    except ImportError:
        log("consultar_aj.py não encontrado, usando lógica inline", "AVISO")
        return await _listar_aj_inline(page, situacao)


async def _listar_aj_inline(page, situacao):
    """Fallback caso consultar_aj.py não esteja no path."""
    # Navega para consulta
    if "consultarNomeacoes" not in page.url:
        await page.goto(AJ_URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

    # Mapeia situação → valor do dropdown
    SITUACAO_VALUES = {
        "TODAS": "0", "AGUARDANDO ACEITE": "1", "RECUSADA": "2",
        "CANCELADA PELO JUIZ": "3", "PERDA DE PRAZO": "4",
        "ACEITA": "5", "SERVIÇO PRESTADO": "7",
    }
    valor = SITUACAO_VALUES.get(situacao.upper(), "0")

    # Altera dropdown via JS (PrimeFaces esconde o select nativo)
    await page.evaluate(f"""() => {{
        var el = document.getElementById('form:situacao_input');
        if (el) {{ el.value = '{valor}'; el.dispatchEvent(new Event('change', {{bubbles: true}})); }}
    }}""")
    await page.wait_for_timeout(500)

    # Clica Consultar
    for sel in ["input[value='Consultar']", "button:has-text('Consultar')"]:
        try:
            btn = page.locator(sel).first
            if await btn.is_visible(timeout=3000):
                await btn.click()
                await page.wait_for_timeout(3000)
                break
        except Exception:
            continue

    # Extrai tabela
    nomeacoes = []
    tabela = page.locator("//table[.//th[contains(text(), 'mero')]]").first
    try:
        rows = await tabela.locator("tr").all()
        for row in rows:
            cells = await row.locator("td").all()
            if len(cells) >= 7:
                textos = [await c.inner_text() for c in cells]
                textos = [t.strip() for t in textos]

                # Converte número para CNJ
                num_raw = textos[1]
                num_limpo = re.sub(r'[^0-9]', '', num_raw)
                m = re.match(r'^(\d{7})(\d{2})(\d{4})(\d)(\d{2})(\d{4})$', num_limpo)
                cnj = f"{m.group(1)}-{m.group(2)}.{m.group(3)}.{m.group(4)}.{m.group(5)}.{m.group(6)}" if m else num_raw

                nomeacoes.append({
                    "numero_nomeacao": textos[0],
                    "numero_processo_cnj": cnj,
                    "unidade": textos[2],
                    "data_nomeacao": textos[3],
                    "dias_aceite": textos[4],
                    "valor_honorario": textos[5],
                    "situacao": textos[6],
                    "sistema": "AJ",
                })
    except Exception as e:
        log(f"Erro ao extrair tabela AJ: {e}", "ERRO")

    log(f"AJ TJMG: {len(nomeacoes)} nomeações", "OK")
    return nomeacoes


# ============================================================
# AJG Federal — Lista nomeações
# ============================================================

async def listar_ajg(page, situacao="AGUARDANDO ACEITE"):
    """Lista nomeações do AJG Federal."""
    # AJG é outro site, precisa navegar
    if not await login_vidaas(page, AJG_URL):
        return []

    try:
        from consultar_ajg import navegar_consulta, listar_nomeacoes
        await navegar_consulta(page)
        return await listar_nomeacoes(page, situacao=situacao)
    except ImportError:
        log("consultar_ajg.py não encontrado — implemente fallback se necessário", "AVISO")
        return []


# ============================================================
# PJe — Baixar PDFs
# ============================================================

async def baixar_pdfs(page, cnjs, pasta_saida=None):
    """Baixa PDFs de uma lista de CNJs do PJe TJMG."""
    if not pasta_saida:
        pasta_saida = PROCESSOS_DIR

    if not await login_vidaas(page, PJE_PAINEL):
        return {"sucesso": 0, "falha": len(cnjs), "resultados": []}

    resultados = []
    sucesso = 0
    falha = 0

    for i, cnj in enumerate(cnjs, 1):
        log(f"[{i}/{len(cnjs)}] Baixando {cnj}...")

        pasta_processo = pasta_saida / cnj.replace(".", "").replace("-", "")
        # Usa formato CNJ como nome de pasta
        pasta_cnj = pasta_saida / cnj
        pasta_cnj.mkdir(parents=True, exist_ok=True)

        try:
            # Navega ao painel
            await page.goto(PJE_PAINEL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)

            # Busca o processo
            num_limpo = re.sub(r'[^0-9]', '', cnj)

            # Tenta campo de busca
            campo = None
            for sel in ["input[id*='pesquisaProcesso']", "input[id*='numeroProcesso']",
                        "input[placeholder*='processo']", "#fPP\\:dnp\\:numeroProcesso\\:numeroSequencial"]:
                try:
                    elem = page.locator(sel).first
                    if await elem.is_visible(timeout=2000):
                        campo = elem
                        break
                except Exception:
                    continue

            if campo:
                await campo.click()
                await campo.fill("")
                await campo.fill(num_limpo)
                await campo.press("Enter")
                await page.wait_for_timeout(3000)

                # Clica no link do processo
                try:
                    link = page.locator(f"//a[contains(text(), '{cnj}')]").first
                    if await link.is_visible(timeout=5000):
                        await link.click()
                        await page.wait_for_timeout(3000)
                except Exception:
                    pass

            # Procura botão de download
            btn_download = None
            for sel in ["a[title*='Download']", "a[id*='downloadAutos']",
                        "//span[contains(@class, 'fa-download')]/parent::a",
                        "//i[contains(@class, 'fa-download')]/parent::a"]:
                try:
                    elem = page.locator(sel).first
                    if await elem.is_visible(timeout=3000):
                        btn_download = elem
                        break
                except Exception:
                    continue

            if not btn_download:
                log(f"Botão de download não encontrado para {cnj}", "ERRO")
                await page.screenshot(path=str(pasta_cnj / "erro_screenshot.png"))
                falha += 1
                resultados.append({"cnj": cnj, "status": "ERRO", "motivo": "botão não encontrado"})
                continue

            await btn_download.click()
            await page.wait_for_timeout(2000)

            # Configura opções do download
            for sel_id, valor in [("cronologia", "Crescente"), ("expediente", "Sim"),
                                   ("movimento", "Sim"), ("qrCode", "Não")]:
                try:
                    elem = page.locator(f"select[id*='{sel_id}']").first
                    if await elem.is_visible(timeout=1000):
                        await elem.select_option(label=valor)
                except Exception:
                    pass

            # Clica DOWNLOAD
            async with page.expect_download(timeout=DOWNLOAD_TIMEOUT) as dl_info:
                dl_btn = page.locator("input[value='DOWNLOAD'], button:has-text('DOWNLOAD')").first
                await dl_btn.click()

            download = await dl_info.value
            dest = pasta_cnj / "autos-completos.pdf"
            await download.save_as(str(dest))

            tamanho_mb = dest.stat().st_size / (1024 * 1024)
            log(f"OK: {cnj} ({tamanho_mb:.1f} MB)", "OK")
            sucesso += 1
            resultados.append({"cnj": cnj, "status": "OK", "tamanho_mb": round(tamanho_mb, 1)})

        except Exception as e:
            log(f"ERRO: {cnj} — {e}", "ERRO")
            falha += 1
            resultados.append({"cnj": cnj, "status": "ERRO", "motivo": str(e)})
            try:
                await page.screenshot(path=str(pasta_cnj / "erro_screenshot.png"))
            except Exception:
                pass

        # Pausa entre downloads
        if i < len(cnjs):
            await page.wait_for_timeout(2000)

    return {"sucesso": sucesso, "falha": falha, "resultados": resultados}


# ============================================================
# NOTIFICAR TELEGRAM
# ============================================================

async def notificar_telegram(msg):
    """Envia notificação via bot Telegram."""
    import urllib.request
    try:
        from src.config import TELEGRAM_BOT_TOKEN as _tg_token, TELEGRAM_CHAT_ID as _tg_chat
        token = _tg_token
        chat_id = _tg_chat
    except ImportError:
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "8397602236")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        log("Telegram notificado", "OK")
    except Exception as e:
        log(f"Erro Telegram: {e}", "AVISO")


# ============================================================
# MAIN
# ============================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Automação PJe/AJ/AJG standalone com Playwright",
        epilog="NUNCA aceita ou rejeita nomeações. Somente leitura + download."
    )
    parser.add_argument("--aj", action="store_true", help="Lista nomeações AJ TJMG")
    parser.add_argument("--ajg", action="store_true", help="Lista nomeações AJG Federal")
    parser.add_argument("--baixar", nargs="*", metavar="CNJ", help="Baixa PDFs (lista de CNJs)")
    parser.add_argument("--tudo", action="store_true", help="AJ + AJG + baixar pendentes")
    parser.add_argument("--pendentes", action="store_true", help="Só AGUARDANDO ACEITE")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    parser.add_argument("--saida", default=None, help="Pasta de saída para PDFs")
    parser.add_argument("--situacao", default="AGUARDANDO ACEITE", help="Filtro de situação")
    args = parser.parse_args()

    if not (args.aj or args.ajg or args.baixar is not None or args.tudo):
        args.aj = True
        args.pendentes = True

    pw, browser, page = await abrir_browser()

    try:
        resultados_totais = {}

        # --- AJ ---
        if args.aj or args.tudo:
            sit = "AGUARDANDO ACEITE" if args.pendentes else args.situacao
            nomeacoes_aj = await listar_aj(page, situacao=sit)
            resultados_totais["aj"] = nomeacoes_aj

            if args.json:
                print(json.dumps(nomeacoes_aj, ensure_ascii=False, indent=2))
            else:
                print()
                print("=" * 100)
                print("  NOMEAÇÕES - AJ TJMG")
                print("=" * 100)
                for n in nomeacoes_aj:
                    cnj = n.get("numero_processo_cnj", "?")
                    sit = n.get("situacao", "?")
                    data = n.get("data_nomeacao", "?")
                    print(f"  {cnj:<25} {sit:<22} {data}")
                print(f"\n  Total: {len(nomeacoes_aj)}")

        # --- AJG ---
        if args.ajg or args.tudo:
            # AJG é outro site — abre nova aba
            page_ajg = await browser.new_page()
            sit = "AGUARDANDO ACEITE" if args.pendentes else args.situacao
            nomeacoes_ajg = await listar_ajg(page_ajg, situacao=sit)
            resultados_totais["ajg"] = nomeacoes_ajg
            await page_ajg.close()

            if args.json:
                print(json.dumps(nomeacoes_ajg, ensure_ascii=False, indent=2))
            else:
                print()
                print("=" * 100)
                print("  NOMEAÇÕES - AJG FEDERAL")
                print("=" * 100)
                for n in nomeacoes_ajg:
                    cnj = n.get("numero_processo_cnj", "?")
                    sit = n.get("situacao", "?")
                    data = n.get("data_nomeacao", "?")
                    print(f"  {cnj:<25} {sit:<22} {data}")
                print(f"\n  Total: {len(nomeacoes_ajg)}")

        # --- BAIXAR ---
        if args.baixar is not None or args.tudo:
            cnjs = args.baixar if args.baixar else []

            # Se --tudo, pega CNJs pendentes do AJ + AJG
            if args.tudo:
                for n in resultados_totais.get("aj", []):
                    if "AGUARDANDO" in n.get("situacao", "").upper():
                        cnj = n.get("numero_processo_cnj")
                        if cnj:
                            cnjs.append(cnj)
                for n in resultados_totais.get("ajg", []):
                    if "AGUARDANDO" in n.get("situacao", "").upper():
                        cnj = n.get("numero_processo_cnj")
                        if cnj:
                            cnjs.append(cnj)

            if cnjs:
                pasta = Path(args.saida) if args.saida else PROCESSOS_DIR
                # Abre nova aba para PJe (diferente do AJ)
                page_pje = await browser.new_page()
                resultado_download = await baixar_pdfs(page_pje, cnjs, pasta)
                await page_pje.close()

                print()
                print("=" * 60)
                s = resultado_download["sucesso"]
                f = resultado_download["falha"]
                print(f"  DOWNLOADS: {s} OK / {f} ERRO / {len(cnjs)} total")
                print("=" * 60)

                # Notifica Telegram
                msg = f"*PJe Download*\n{s} OK / {f} erro de {len(cnjs)} processos"
                await notificar_telegram(msg)
            else:
                log("Nenhum CNJ para baixar", "INFO")

        # Notifica resumo geral
        if args.tudo:
            n_aj = len(resultados_totais.get("aj", []))
            n_ajg = len(resultados_totais.get("ajg", []))
            msg = f"*Sincronização PJe*\nAJ: {n_aj} nomeações\nAJG: {n_ajg} nomeações"
            await notificar_telegram(msg)

        # Salva resultado em JSON
        json_path = PROCESSOS_DIR / "ultima-sincronizacao.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps({
            "data": datetime.now().isoformat(),
            "aj": len(resultados_totais.get("aj", [])),
            "ajg": len(resultados_totais.get("ajg", [])),
        }, ensure_ascii=False, indent=2))

    finally:
        await browser.close()
        await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())
