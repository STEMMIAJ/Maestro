#!/usr/bin/env python3
"""Automação PJe/AJ/AJG com Playwright standalone (sem Chrome em modo debug).

Abre Chromium próprio, faz login VidaaS (manual), depois automatiza tudo.

Refatorado: aplica padrões de pje.common e captura_falha estruturada.
ref: PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json + 07-PESQUISA-AGENTES/auditoria-pje/REFACTOR-PLAN.md

Uso:
  python3 pje_standalone.py --aj              # Lista nomeações AJ TJMG
  python3 pje_standalone.py --ajg             # Lista nomeações AJG Federal
  python3 pje_standalone.py --baixar CNJ...   # Baixa PDFs do PJe
  python3 pje_standalone.py --tudo            # AJ + AJG + baixar pendentes

Variáveis de ambiente (ver .env.example):
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID  — notificação opcional
  TJMG_JANELA_INICIO, TJMG_JANELA_FIM   — janela horário PJe (13-19)
  PROCESSOS_DIR                          — destino dos PDFs
  PJE_FORCAR_HORARIO                     — bypass guarda janela TJMG

IMPORTANTE: NUNCA clica em Aceitar ou Rejeitar. Somente leitura + download.
"""

from __future__ import annotations
import argparse
import asyncio
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("pip install playwright && playwright install chromium")
    sys.exit(1)

# Common helpers do próprio repo
sys.path.insert(0, str(Path(__file__).parent.parent))
from pje.common.config import SETTINGS, telegram_configurado
from pje.common.cnj import RE_CNJ, validar_cnj, limpar_cnj, safe_filename_cnj  # noqa: F401
from pje.common.paths import processos_dir, quarentena_dir, safe_move
from pje.common.logger import get_logger
from pje.common.pdf import pdf_valido, cnj_no_pdf
from pje.common.janela import dentro_janela_tjmg, msg_janela
from pje.common.pje_session import sessao_ativa, salvar_diagnostico
from pje.common.richfaces import setar_select_jsf
from pje.common.download import clicar_e_salvar_download

# Compat com scripts legados (consultar_aj.py / consultar_ajg.py do iCloud)
ICLOUD_SCRIPTS = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/Stemmia/ANALISADOR FINAL"
sys.path.insert(0, str(ICLOUD_SCRIPTS / "analisador de processos"))
sys.path.insert(0, str(ICLOUD_SCRIPTS / "scripts"))

logger = get_logger("pje_standalone")

# ============================================================
# CONFIGURAÇÃO
# ============================================================

AJ_URL = "https://aj.tjmg.jus.br/aj/internet/consultarNomeacoes.jsf"
AJG_URL = "https://ajg.cjf.jus.br/ajg2/internet/nomeacoes/consultanomeacoes.jsf"
PJE_PAINEL = "https://pje.tjmg.jus.br/pje/Painel/painel_usuario/Usuario.seam"

DOWNLOAD_TIMEOUT = 300_000  # 5 min
USER_DATA = Path.home() / ".pje-browser-data"  # cookies entre sessões (Mac, sem cert A3)


def log(msg: str, level: str = "INFO") -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "i", "OK": "v", "ERRO": "x", "AVISO": "!"}.get(level, "·")
    print(f"  [{ts}] {prefix} {msg}")


# ============================================================
# BROWSER — persistência de cookies
# ============================================================

async def abrir_browser():
    """Abre Chromium persistente. ref: PW-002 (anti-detect), PJE-002 (cookies)."""
    pw = await async_playwright().start()
    browser = await pw.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA),
        headless=False,
        slow_mo=100,
        args=[
            "--disable-blink-features=AutomationControlled",
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

async def login_vidaas(page, url_destino: str) -> bool:
    """Navega e aguarda login se necessário. ref: PJE-002 (sessão), CASOS-PJE Caso 3."""
    log(f"Abrindo {url_destino}...")
    try:
        await page.goto(url_destino, wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        logger.captura_falha(
            tecnologia="playwright",
            categoria="navegacao",
            sintoma=f"goto {url_destino} falhou: {e}",
            ref_falhas_json="PW-001",
            severidade="alta",
            exc=e,
        )
        return False

    await page.wait_for_timeout(2000)

    if await sessao_ativa(page):
        log("Já autenticado (cookies salvos)", "OK")
        return True

    log("AGUARDANDO LOGIN VIDAAS — autentique no browser", "AVISO")
    print("\n  >>> Faça login no browser que abriu <<<\n")

    # Espera até sair da tela de login (máx 5 min)
    for i in range(300):
        await page.wait_for_timeout(1000)
        if await sessao_ativa(page):
            log("Login detectado", "OK")
            await page.wait_for_timeout(2000)
            return True
        if i > 0 and i % 30 == 0:
            log(f"Ainda aguardando login... ({i}s)", "AVISO")

    logger.captura_falha(
        tecnologia="pje",
        categoria="autenticacao",
        sintoma="timeout 5min aguardando login VidaaS",
        ref_falhas_json="PJE-002",
        severidade="alta",
    )
    return False


# ============================================================
# AJ TJMG
# ============================================================

SITUACAO_VALUES = {
    "TODAS": "0", "AGUARDANDO ACEITE": "1", "RECUSADA": "2",
    "CANCELADA PELO JUIZ": "3", "PERDA DE PRAZO": "4",
    "ACEITA": "5", "SERVIÇO PRESTADO": "7",
}


async def listar_aj(page, situacao: str = "AGUARDANDO ACEITE") -> list[dict]:
    """Lista nomeações AJ TJMG. Reutiliza consultar_aj.py se disponível."""
    if not await login_vidaas(page, AJ_URL):
        return []

    try:
        from consultar_aj import navegar_consulta, listar_nomeacoes  # type: ignore
        await navegar_consulta(page)
        return await listar_nomeacoes(page, situacao=situacao)
    except ImportError:
        log("consultar_aj.py não encontrado, usando lógica inline", "AVISO")
        return await _listar_aj_inline(page, situacao)


async def _listar_aj_inline(page, situacao: str) -> list[dict]:
    """Fallback se consultar_aj não estiver no path. ref: PW-009 (PrimeFaces)."""
    if "consultarNomeacoes" not in page.url:
        try:
            await page.goto(AJ_URL, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            logger.captura_falha(
                tecnologia="playwright", categoria="navegacao",
                sintoma=f"goto AJ_URL falhou: {e}",
                ref_falhas_json="PW-001", exc=e,
            )
            return []
        await page.wait_for_timeout(2000)

    valor = SITUACAO_VALUES.get(situacao.upper(), "0")

    # Setar dropdown via helper que dispara onchange AJAX (não dá pra usar select_option em PrimeFaces)
    ok = await setar_select_jsf(page, "form:situacao_input", valor)
    if not ok:
        logger.captura_falha(
            tecnologia="primefaces", categoria="select",
            sintoma="setar_select_jsf form:situacao_input retornou False",
            ref_falhas_json="PW-009",
            contexto={"valor": valor, "situacao": situacao},
            severidade="media",
        )
    await page.wait_for_timeout(500)

    # Clica Consultar
    clicado = False
    for sel in ["input[value='Consultar']", "button:has-text('Consultar')"]:
        try:
            btn = page.locator(sel).first
            if await btn.is_visible(timeout=3000):
                await btn.click()
                await page.wait_for_timeout(3000)
                clicado = True
                break
        except Exception:
            continue
    if not clicado:
        logger.captura_falha(
            tecnologia="playwright", categoria="locator",
            sintoma="botão Consultar AJ não encontrado",
            ref_falhas_json="PJE-016",
            severidade="alta",
        )
        return []

    nomeacoes: list[dict] = []
    try:
        tabela = page.locator("//table[.//th[contains(text(), 'mero')]]").first
        rows = await tabela.locator("tr").all()
        for row in rows:
            cells = await row.locator("td").all()
            if len(cells) < 7:
                continue
            textos = [(await c.inner_text()).strip() for c in cells]

            num_raw = textos[1]
            num_limpo = re.sub(r"[^0-9]", "", num_raw)
            m = re.match(r"^(\d{7})(\d{2})(\d{4})(\d)(\d{2})(\d{4})$", num_limpo)
            cnj = (
                f"{m.group(1)}-{m.group(2)}.{m.group(3)}.{m.group(4)}.{m.group(5)}.{m.group(6)}"
                if m else num_raw
            )

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
        logger.captura_falha(
            tecnologia="playwright", categoria="extracao_tabela",
            sintoma=f"erro extraindo tabela AJ: {e}",
            ref_falhas_json="PJE-005", exc=e,
        )
        log(f"Erro ao extrair tabela AJ: {e}", "ERRO")

    log(f"AJ TJMG: {len(nomeacoes)} nomeações", "OK")
    return nomeacoes


# ============================================================
# AJG Federal
# ============================================================

async def listar_ajg(page, situacao: str = "AGUARDANDO ACEITE") -> list[dict]:
    """Lista AJG Federal. ref: PJE-014 (CJF pode estar offline)."""
    if not await login_vidaas(page, AJG_URL):
        return []

    try:
        from consultar_ajg import navegar_consulta, listar_nomeacoes  # type: ignore
        await navegar_consulta(page)
        return await listar_nomeacoes(page, situacao=situacao)
    except ImportError:
        log("consultar_ajg.py não encontrado — sem fallback inline", "AVISO")
        logger.captura_falha(
            tecnologia="geral", categoria="dependencia_ausente",
            sintoma="consultar_ajg.py não encontrado no PYTHONPATH",
            ref_falhas_json="GL-001",
            severidade="media",
        )
        return []


# ============================================================
# PJe — Baixar PDFs
# ============================================================

async def _localizar_botao_download(page):
    """Procura botão de download por múltiplos seletores. ref: PJE-016."""
    for sel in [
        "a[title*='Download']",
        "a[id*='downloadAutos']",
        "//span[contains(@class, 'fa-download')]/parent::a",
        "//i[contains(@class, 'fa-download')]/parent::a",
    ]:
        try:
            elem = page.locator(sel).first
            if await elem.is_visible(timeout=3000):
                return elem
        except Exception:
            continue
    return None


async def _localizar_botao_dl_final(page):
    """Botão DOWNLOAD final dentro do dialog de opções. ref: PJE-016."""
    for sel in [
        "input[value='DOWNLOAD']",
        "button:has-text('DOWNLOAD')",
        "input[type='submit'][value*='DOWNLOAD']",
    ]:
        try:
            btn = page.locator(sel).first
            if await btn.is_visible(timeout=2000):
                return btn
        except Exception:
            continue
    return None


async def baixar_pdfs(page, cnjs: list[str], pasta_saida: Path | None = None) -> dict:
    """Baixa PDFs de uma lista de CNJs do PJe TJMG.

    Aplica:
    - clicar_e_salvar_download (PW-013/PJE-003: fallback nova aba)
    - pdf_valido + cnj_no_pdf (PW-028/PJE-007)
    - safe_move para quarentena se CNJ não bater (PJE-021)
    - setar_select_jsf para dropdowns PrimeFaces (PW-009/PJE-004)
    """
    pasta_saida = Path(pasta_saida) if pasta_saida else processos_dir()

    if not await login_vidaas(page, PJE_PAINEL):
        return {"sucesso": 0, "falha": len(cnjs), "resultados": []}

    resultados: list[dict] = []
    sucesso = 0
    falha = 0

    for i, cnj in enumerate(cnjs, 1):
        if not validar_cnj(cnj):
            log(f"CNJ inválido ignorado: {cnj}", "ERRO")
            logger.captura_falha(
                tecnologia="geral", categoria="validacao",
                sintoma=f"CNJ inválido na lista de download: {cnj}",
                ref_falhas_json="GL-002",
                severidade="baixa",
            )
            falha += 1
            resultados.append({"cnj": cnj, "status": "ERRO", "motivo": "CNJ inválido"})
            continue

        log(f"[{i}/{len(cnjs)}] Baixando {cnj}...")

        pasta_cnj = pasta_saida / cnj
        pasta_cnj.mkdir(parents=True, exist_ok=True)

        try:
            try:
                await page.goto(PJE_PAINEL, wait_until="domcontentloaded", timeout=30000)
            except Exception as e:
                logger.captura_falha(
                    tecnologia="playwright", categoria="navegacao",
                    sintoma=f"goto PJE_PAINEL falhou: {e}",
                    ref_falhas_json="PW-001", exc=e,
                )
                raise
            await page.wait_for_timeout(2000)

            num_limpo = limpar_cnj(cnj)

            # Campo de busca
            campo = None
            for sel in [
                "input[id*='pesquisaProcesso']",
                "input[id*='numeroProcesso']",
                "input[placeholder*='processo']",
                "#fPP\\:dnp\\:numeroProcesso\\:numeroSequencial",
            ]:
                try:
                    elem = page.locator(sel).first
                    if await elem.is_visible(timeout=2000):
                        campo = elem
                        break
                except Exception:
                    continue

            if not campo:
                logger.captura_falha(
                    tecnologia="playwright", categoria="locator",
                    sintoma=f"campo de busca de processo não encontrado para {cnj}",
                    ref_falhas_json="PJE-016",
                    contexto={"cnj": cnj},
                    severidade="alta",
                )
                await salvar_diagnostico(page, pasta_cnj, prefix="erro_busca")
                falha += 1
                resultados.append({"cnj": cnj, "status": "ERRO", "motivo": "campo busca não encontrado"})
                continue

            await campo.click()
            await campo.fill("")
            await campo.fill(num_limpo)
            await campo.press("Enter")
            await page.wait_for_timeout(3000)

            # Link do processo
            try:
                link = page.locator(f"//a[contains(text(), '{cnj}')]").first
                if await link.is_visible(timeout=5000):
                    await link.click()
                    await page.wait_for_timeout(3000)
            except Exception:
                pass

            # Botão de download (abre dialog)
            btn_download = await _localizar_botao_download(page)
            if not btn_download:
                logger.captura_falha(
                    tecnologia="playwright", categoria="locator",
                    sintoma=f"botão download não encontrado para {cnj}",
                    ref_falhas_json="PJE-016",
                    contexto={"cnj": cnj},
                    severidade="alta",
                )
                await salvar_diagnostico(page, pasta_cnj, prefix="erro_btn_download")
                falha += 1
                resultados.append({"cnj": cnj, "status": "ERRO", "motivo": "botão download não encontrado"})
                continue

            await btn_download.click()
            await page.wait_for_timeout(2000)

            # Configura opções via setar_select_jsf (PW-009)
            for sel_id, valor in [
                ("cronologia", "Crescente"),
                ("expediente", "Sim"),
                ("movimento", "Sim"),
                ("qrCode", "Não"),
            ]:
                # Tenta primeiro via id real (sem prefixo de form), depois com prefixo
                ok = False
                for tentativa in (sel_id, f"form:{sel_id}", f"form:{sel_id}_input"):
                    if await setar_select_jsf(page, tentativa, valor):
                        ok = True
                        break
                if not ok:
                    # Fallback ao select_option original (não fatal — algumas opções nem aparecem)
                    try:
                        elem = page.locator(f"select[id*='{sel_id}']").first
                        if await elem.is_visible(timeout=1000):
                            await elem.select_option(label=valor)
                    except Exception:
                        pass

            # Botão DOWNLOAD final
            dl_btn = await _localizar_botao_dl_final(page)
            if not dl_btn:
                logger.captura_falha(
                    tecnologia="playwright", categoria="locator",
                    sintoma=f"botão DOWNLOAD final não encontrado para {cnj}",
                    ref_falhas_json="PJE-016",
                    severidade="alta",
                )
                await salvar_diagnostico(page, pasta_cnj, prefix="erro_dl_final")
                falha += 1
                resultados.append({"cnj": cnj, "status": "ERRO", "motivo": "botão DOWNLOAD final não encontrado"})
                continue

            # Download com fallback nova aba (PW-013/PJE-003)
            dest = pasta_cnj / "autos-completos.pdf"
            res_dl = await clicar_e_salvar_download(page, dl_btn, dest, timeout_ms=DOWNLOAD_TIMEOUT)

            if res_dl["tipo"] == "falha":
                logger.captura_falha(
                    tecnologia="playwright", categoria="download",
                    sintoma=f"download falhou para {cnj}: {res_dl.get('motivo')}",
                    ref_falhas_json="PW-013",
                    contexto={"cnj": cnj, "motivo": res_dl.get("motivo")},
                    severidade="alta",
                )
                await salvar_diagnostico(page, pasta_cnj, prefix="erro_download")
                falha += 1
                resultados.append({"cnj": cnj, "status": "ERRO", "motivo": res_dl.get("motivo")})
                continue

            # Validação 1: PDF válido (PW-028)
            if not pdf_valido(dest):
                logger.captura_falha(
                    tecnologia="pdf", categoria="validacao",
                    sintoma=f"arquivo baixado não é PDF válido: {dest.name}",
                    ref_falhas_json="PW-028",
                    contexto={"cnj": cnj, "path": str(dest)},
                    severidade="alta",
                )
                # Move para quarentena
                qdest = quarentena_dir() / f"{safe_filename_cnj(cnj, '_invalido.pdf')}"
                safe_move(dest, qdest)
                falha += 1
                resultados.append({"cnj": cnj, "status": "ERRO", "motivo": "PDF inválido", "quarentena": str(qdest)})
                continue

            # Validação 2: CNJ no PDF (PJE-007)
            if not cnj_no_pdf(dest, cnj):
                logger.captura_falha(
                    tecnologia="pdf", categoria="validacao_cnj",
                    sintoma=f"CNJ {cnj} não encontrado no PDF baixado",
                    ref_falhas_json="PJE-007",
                    contexto={"cnj": cnj, "path": str(dest)},
                    severidade="alta",
                )
                qdest = quarentena_dir() / f"{safe_filename_cnj(cnj, '_cnj_divergente.pdf')}"
                safe_move(dest, qdest)
                falha += 1
                resultados.append({"cnj": cnj, "status": "ERRO", "motivo": "CNJ divergente no PDF", "quarentena": str(qdest)})
                continue

            tamanho_mb = dest.stat().st_size / (1024 * 1024)
            log(f"OK: {cnj} ({tamanho_mb:.1f} MB) [{res_dl['tipo']}]", "OK")
            sucesso += 1
            resultados.append({
                "cnj": cnj, "status": "OK",
                "tamanho_mb": round(tamanho_mb, 1),
                "tipo_captura": res_dl["tipo"],
            })

        except Exception as e:
            logger.captura_falha(
                tecnologia="playwright", categoria="download_loop",
                sintoma=f"exceção não tratada baixando {cnj}: {e}",
                ref_falhas_json="GL-003",
                contexto={"cnj": cnj},
                exc=e,
                severidade="alta",
            )
            log(f"ERRO: {cnj} — {e}", "ERRO")
            falha += 1
            resultados.append({"cnj": cnj, "status": "ERRO", "motivo": str(e)})
            try:
                await salvar_diagnostico(page, pasta_cnj, prefix="erro_excecao")
            except Exception:
                pass

        if i < len(cnjs):
            await page.wait_for_timeout(2000)

    return {"sucesso": sucesso, "falha": falha, "resultados": resultados}


# ============================================================
# TELEGRAM
# ============================================================

async def notificar_telegram(msg: str) -> None:
    """Envia notificação via bot Telegram. Token via env (BUGS.md §19)."""
    if not telegram_configurado():
        log("Telegram não configurado (TELEGRAM_BOT_TOKEN/CHAT_ID ausentes)", "AVISO")
        return

    url = f"https://api.telegram.org/bot{SETTINGS.telegram_token}/sendMessage"
    data = json.dumps({
        "chat_id": SETTINGS.telegram_chat_id,
        "text": msg,
        "parse_mode": "Markdown",
    }).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        log("Telegram notificado", "OK")
    except Exception as e:
        logger.captura_falha(
            tecnologia="telegram", categoria="notificacao",
            sintoma=f"erro envio Telegram: {e}",
            ref_falhas_json="GL-004",
            exc=e,
            severidade="baixa",
        )
        log(f"Erro Telegram: {e}", "AVISO")


# ============================================================
# MAIN
# ============================================================

async def main() -> int:
    parser = argparse.ArgumentParser(
        description="Automação PJe/AJ/AJG standalone com Playwright",
        epilog="NUNCA aceita ou rejeita nomeações. Somente leitura + download.",
    )
    parser.add_argument("--aj", action="store_true", help="Lista nomeações AJ TJMG")
    parser.add_argument("--ajg", action="store_true", help="Lista nomeações AJG Federal")
    parser.add_argument("--baixar", nargs="*", metavar="CNJ", help="Baixa PDFs (lista de CNJs)")
    parser.add_argument("--tudo", action="store_true", help="AJ + AJG + baixar pendentes")
    parser.add_argument("--pendentes", action="store_true", help="Só AGUARDANDO ACEITE")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    parser.add_argument("--saida", default=None, help="Pasta de saída para PDFs")
    parser.add_argument("--situacao", default="AGUARDANDO ACEITE", help="Filtro de situação")
    parser.add_argument("--forcar-horario", action="store_true",
                        help="Bypass guarda janela TJMG 13-19h (PJE-009)")
    args = parser.parse_args()

    if not (args.aj or args.ajg or args.baixar is not None or args.tudo):
        args.aj = True
        args.pendentes = True

    # Guarda janela TJMG (PJE-009) — só relevante se for baixar PDF
    vai_baixar = args.baixar is not None or args.tudo
    forcar = args.forcar_horario or os.environ.get("PJE_FORCAR_HORARIO") == "1"
    if vai_baixar and not forcar and not dentro_janela_tjmg():
        log(msg_janela(), "AVISO")
        log("Use --forcar-horario para ignorar (ref: PJE-009)", "INFO")
        logger.captura_falha(
            tecnologia="pje", categoria="janela_horario",
            sintoma="execução fora da janela TJMG 13-19h sem --forcar-horario",
            ref_falhas_json="PJE-009",
            severidade="media",
        )
        return 2

    pw, browser, page = await abrir_browser()
    resultados_totais: dict = {}

    try:
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
                    sit_n = n.get("situacao", "?")
                    data = n.get("data_nomeacao", "?")
                    print(f"  {cnj:<25} {sit_n:<22} {data}")
                print(f"\n  Total: {len(nomeacoes_aj)}")

        # --- AJG ---
        if args.ajg or args.tudo:
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
                    sit_n = n.get("situacao", "?")
                    data = n.get("data_nomeacao", "?")
                    print(f"  {cnj:<25} {sit_n:<22} {data}")
                print(f"\n  Total: {len(nomeacoes_ajg)}")

        # --- BAIXAR ---
        if vai_baixar:
            cnjs: list[str] = list(args.baixar) if args.baixar else []

            if args.tudo:
                for fonte in ("aj", "ajg"):
                    for n in resultados_totais.get(fonte, []):
                        if "AGUARDANDO" in n.get("situacao", "").upper():
                            cnj = n.get("numero_processo_cnj")
                            if cnj and cnj not in cnjs:
                                cnjs.append(cnj)

            if cnjs:
                pasta = Path(args.saida) if args.saida else processos_dir()
                page_pje = await browser.new_page()
                resultado_download = await baixar_pdfs(page_pje, cnjs, pasta)
                await page_pje.close()

                print()
                print("=" * 60)
                s = resultado_download["sucesso"]
                f = resultado_download["falha"]
                print(f"  DOWNLOADS: {s} OK / {f} ERRO / {len(cnjs)} total")
                print("=" * 60)

                msg = f"*PJe Download*\n{s} OK / {f} erro de {len(cnjs)} processos"
                await notificar_telegram(msg)
            else:
                log("Nenhum CNJ para baixar", "INFO")

        if args.tudo:
            n_aj = len(resultados_totais.get("aj", []))
            n_ajg = len(resultados_totais.get("ajg", []))
            await notificar_telegram(
                f"*Sincronização PJe*\nAJ: {n_aj} nomeações\nAJG: {n_ajg} nomeações"
            )

        # Persiste sumário
        try:
            json_path = processos_dir() / "ultima-sincronizacao.json"
            json_path.parent.mkdir(parents=True, exist_ok=True)
            json_path.write_text(json.dumps({
                "data": datetime.now().isoformat(),
                "aj": len(resultados_totais.get("aj", [])),
                "ajg": len(resultados_totais.get("ajg", [])),
            }, ensure_ascii=False, indent=2))
        except Exception as e:
            logger.captura_falha(
                tecnologia="geral", categoria="io",
                sintoma=f"erro salvando ultima-sincronizacao.json: {e}",
                ref_falhas_json="GL-005",
                exc=e,
                severidade="baixa",
            )

    finally:
        try:
            await browser.close()
        finally:
            await pw.stop()

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
