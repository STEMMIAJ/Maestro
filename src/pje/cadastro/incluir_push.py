#!/usr/bin/env python3
"""
Inclusão automática de processos no PUSH do PJe TJMG.
Abre Chromium, espera login VidaaS manual, depois inclui processos automaticamente.

Uso:
  python3 incluir_push.py                     # Inclui todos
  python3 incluir_push.py --limite 3          # Inclui apenas 3 (teste)
  python3 incluir_push.py --dry-run           # Mostra o que faria sem executar
  python3 incluir_push.py --cnj 5022119-66... # Inclui um específico
  python3 incluir_push.py --descobrir         # Navega ao PUSH, screenshot, mostra seletores

Login VidaaS:
  O script abre o browser e espera você autenticar (~30s).
  Após login, tudo é automático.
"""

import asyncio
import argparse
import hashlib
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

# Polimento 2026-04-19 (plano binary-gliding-pine): tqdm, rich, tenacity.
try:
    from tqdm import tqdm as _tqdm
    def tqdm(it, **kw):
        kw.setdefault("leave", False)
        return _tqdm(it, **kw)
except Exception:
    def tqdm(it, **kw):
        return it

try:
    from rich import print as rprint
except Exception:
    def rprint(*a, **kw):
        print(*a, **kw)

try:
    from tenacity import (
        AsyncRetrying,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
    )
    _TENACITY_OK = True
except Exception:
    _TENACITY_OK = False


# ============================================================
# CONFIGURAÇÃO
# ============================================================

PJE_LOGIN = "https://pje.tjmg.jus.br/pje/login.seam"
PJE_PUSH = "https://pje.tjmg.jus.br/pje/Push/listView.seam"
PJE_PUSH_ALT = "https://pje.tjmg.jus.br/pje/Push/push.seam"

USER_DATA = Path.home() / ".pje-browser-data"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
MAPA_DIR = Path(__file__).parent / "_mapa"
ANALISE_ERROS_DIR = Path(__file__).parent / "_analise-erros"

# Config central (lazy — não falha se ausente)
_THIS_DIR = Path(__file__).parent
_ROOT = _THIS_DIR.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
try:
    from config.config_pje import PUSH_MAPA_FILE as _CFG_PUSH_MAPA_FILE  # noqa
    PUSH_MAPA_FILE = _CFG_PUSH_MAPA_FILE
except Exception:
    PUSH_MAPA_FILE = "push_atual_{data}.json"

# Validação do config em runtime (fail-soft)
try:
    _cfg_path = _ROOT / "config"
    if str(_cfg_path) not in sys.path:
        sys.path.insert(0, str(_cfg_path))
    from config_validacao import validar_config as _validar_config
    _res = _validar_config()
    if not _res.get("ok", True):
        rprint(f"[yellow][config-validacao] avisos: {_res}[/yellow]")
except Exception as _e:
    print(f"[config-validacao] skip: {_e}", file=sys.stderr)

# Observações — variações determinísticas (evita duplicata exata no PJe)
OBS_VARIACOES_POR_CIDADE = {
    "CONSELHEIRO PENA": [
        "CONSELHEIRO PENA - GV",
        "Cons. Pena/GV",
        "Cons.Pena-GV",
        "Conselheiro Pena/GV",
        "CONS PENA - GV",
    ],
    "GOVERNADOR VALADARES": [
        "GOVERNADOR VALADARES",
        "Gov. Valadares",
        "Gov.Valadares",
        "GV",
        "Governador Valadares",
    ],
    "MANTENA": [
        "MANTENA",
        "Mantena/MG",
        "Mantena-MG",
    ],
    "RIO PARDO": [
        "RIO PARDO DE MINAS",
        "Rio Pardo/MG",
        "Rio Pardo-MG",
    ],
}

# Caminhos da lista de processos (ordem de prioridade)
LISTA_JSON = Path.home() / "Desktop/STEMMIA Dexter/LISTA-COMPLETA-PUSH.json"
LISTA_TXT = Path.home() / "Desktop/STEMMIA Dexter/AUTOMAÇÃO/lista-inclusao-push.txt"

# Seletores candidatos — o PJe varia entre versões
SELETORES_CNJ = [
    "input[id*='numeroProcesso']",
    "input[id*='numProcesso']",
    "input[id*='numero']",
    "input[name*='numeroProcesso']",
    "input[name*='numero']",
    "input.numeroCNJ",
    "input[id*='push'][id*='numero']",
    "#numProcessoPush",
]

SELETORES_OBS = [
    "input[id*='observacao']",
    "textarea[id*='observacao']",
    "input[id*='descricao']",
    "textarea[id*='descricao']",
    "input[name*='observacao']",
    "input[id*='push'][id*='obs']",
]

SELETORES_BTN = [
    "input[value='Incluir']",
    "button:has-text('Incluir')",
    "a:has-text('Incluir')",
    "input[value='Adicionar']",
    "button:has-text('Adicionar')",
    "input[value='Salvar']",
    "button:has-text('Salvar')",
]

RE_CNJ = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "\u2139", "OK": "\u2713", "ERRO": "\u2717", "AVISO": "\u26a0", "PUSH": "\u25b6"}.get(level, "\u00b7")
    print(f"  [{ts}] {prefix} {msg}")


# ============================================================
# OBSERVAÇÃO — variações determinísticas
# ============================================================

def gerar_observacao(cnj: str, cidade_base: str) -> str:
    """
    Retorna uma observação com variação determinística por CNJ.

    O PJe detecta duplicata EXATA em alguns contextos; rotacionar por hash(cnj)
    gera strings diferentes (mesma semântica) para cada CNJ, mantendo
    idempotência — o mesmo CNJ sempre recebe a mesma variação.
    """
    if not cidade_base:
        return ""
    chave = cidade_base.strip().upper()
    variacoes = OBS_VARIACOES_POR_CIDADE.get(chave)
    if not variacoes:
        # Cidade desconhecida — retorna a string original, sem variação
        return cidade_base
    h = hashlib.md5(cnj.encode("utf-8")).hexdigest()
    idx = int(h[:8], 16) % len(variacoes)
    return variacoes[idx]


# ============================================================
# MAPA PRÉVIO — carregamento (verificação PROATIVA)
# ============================================================

def carregar_mapa_push(data_str=None):
    """
    Lê o JSON gerado por mapear_paginas_push.py.
    Retorna dict com chaves 'cnjs' (set) e 'observacoes_por_cnj'.
    Se não existir, retorna estrutura vazia.
    """
    if data_str is None:
        data_str = datetime.now().strftime("%Y-%m-%d")
    nome = PUSH_MAPA_FILE.format(data=data_str) if "{data}" in PUSH_MAPA_FILE else f"push_atual_{data_str}.json"
    path = MAPA_DIR / nome
    if not path.exists():
        # Tenta pegar o mais recente disponível
        if MAPA_DIR.exists():
            cands = sorted(MAPA_DIR.glob("push_atual_*.json"))
            if cands:
                path = cands[-1]
                log(f"Mapa de hoje não achado — usando o mais recente: {path.name}", "AVISO")
            else:
                log("Nenhum mapa PUSH encontrado — rode mapear_paginas_push.py primeiro", "AVISO")
                return {"cnjs": set(), "observacoes_por_cnj": {}, "path": None}
        else:
            return {"cnjs": set(), "observacoes_por_cnj": {}, "path": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"Erro lendo mapa {path}: {e}", "ERRO")
        return {"cnjs": set(), "observacoes_por_cnj": {}, "path": None}
    cnjs = set(data.get("cnjs") or [])
    obs = data.get("observacoes_por_cnj") or {}
    log(f"Mapa PUSH carregado: {len(cnjs)} CNJs já cadastrados ({path.name})", "OK")
    return {"cnjs": cnjs, "observacoes_por_cnj": obs, "path": path}


def registrar_duplicata_runtime(cnj: str, contexto: str = ""):
    """Registra no _analise-erros que o PJe respondeu 'já cadastrado' em runtime."""
    ANALISE_ERROS_DIR.mkdir(parents=True, exist_ok=True)
    hoje = datetime.now().strftime("%Y-%m-%d")
    path = ANALISE_ERROS_DIR / f"duplicatas-runtime-{hoje}.jsonl"
    entrada = {
        "tipo": "duplicata_runtime",
        "cnj": cnj,
        "timestamp": datetime.now().isoformat(),
        "contexto": contexto,
    }
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ============================================================
# CARREGAR LISTA DE PROCESSOS
# ============================================================

def carregar_lista(arquivo=None):
    """Carrega lista de processos do JSON ou TXT."""
    # Path customizado
    if arquivo:
        p = Path(arquivo)
        if not p.exists():
            log(f"Arquivo não encontrado: {arquivo}", "ERRO")
            sys.exit(1)
        if p.suffix == ".json":
            return _carregar_json(p)
        return _carregar_txt(p)

    # JSON primeiro
    if LISTA_JSON.exists():
        return _carregar_json(LISTA_JSON)

    # Fallback TXT
    if LISTA_TXT.exists():
        return _carregar_txt(LISTA_TXT)

    log("Nenhuma lista de processos encontrada!", "ERRO")
    log(f"  Esperado: {LISTA_JSON}")
    log(f"  Ou: {LISTA_TXT}")
    sys.exit(1)


def _carregar_json(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    processos = data.get("processos", data) if isinstance(data, dict) else data
    resultado = []
    for p in processos:
        cnj = p.get("cnj", "")
        # observacao_push tratado como CIDADE_BASE; gerar_observacao cria variação
        cidade_base = p.get("observacao_push", "") or p.get("cidade", "")
        if cnj and RE_CNJ.match(cnj):
            obs = gerar_observacao(cnj, cidade_base)
            resultado.append({"cnj": cnj, "observacao": obs, "cidade_base": cidade_base})
    log(f"Carregados {len(resultado)} processos de {path.name}", "OK")
    return resultado


def _carregar_txt(path):
    resultado = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            partes = linha.split("|", 1)
            cnj = partes[0].strip()
            cidade_base = partes[1].strip() if len(partes) > 1 else ""
            if RE_CNJ.match(cnj):
                obs = gerar_observacao(cnj, cidade_base)
                resultado.append({"cnj": cnj, "observacao": obs, "cidade_base": cidade_base})
    log(f"Carregados {len(resultado)} processos de {path.name}", "OK")
    return resultado


# ============================================================
# BROWSER — CDP ou standalone
# ============================================================

async def conectar_cdp(porta=9222):
    """Conecta ao Chrome já aberto via CDP."""
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
        log("Nenhum contexto — criando...", "AVISO")
        context = await browser.new_context()
    else:
        try:
            from pje_cdp import pick_context_by_url, PJE_URL_HINTS
            context = pick_context_by_url(browser, PJE_URL_HINTS) or contexts[0]
        except ImportError:
            context = contexts[0]

    pages = context.pages
    # Usar primeira aba não-blank ou criar nova
    page = None
    for p in pages:
        if "blank" not in p.url:
            page = p
            break
    if not page:
        page = pages[0] if pages else await context.new_page()

    return pw, browser, page


async def abrir_browser_standalone():
    """Abre Chromium próprio com dados persistentes (fallback)."""
    pw = await async_playwright().start()
    browser = await pw.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA),
        headless=False,
        slow_mo=500,
        args=[
            "--no-first-run",
            "--no-default-browser-check",
        ],
        viewport={"width": 1280, "height": 900},
    )
    page = browser.pages[0] if browser.pages else await browser.new_page()
    return pw, browser, page


# ============================================================
# LOGIN VIDAAS
# ============================================================

async def aguardar_login(page):
    """Navega ao PJe e espera login VidaaS manual."""
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

    for i in range(300):  # 5 min max
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
# NAVEGAR AO PUSH
# ============================================================

async def navegar_push(page):
    """Navega até a página de inclusão no PUSH."""
    log("Navegando ao PUSH...")

    for url in [PJE_PUSH, PJE_PUSH_ALT]:
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)

            # Verifica se a página carregou (não redirecionou para login)
            url_atual = page.url.lower()
            if "login" in url_atual or "sso" in url_atual:
                log("Sessão expirou — refaça login", "ERRO")
                return False

            # Procura algum campo de inclusão
            for sel in SELETORES_CNJ:
                try:
                    el = page.locator(sel).first
                    if await el.is_visible(timeout=2000):
                        log(f"Página PUSH carregada ({url})", "OK")
                        return True
                except Exception:
                    continue

            # Se não achou campo, tenta link "Incluir" ou "Novo"
            for texto in ["Incluir", "Novo", "Adicionar", "Cadastrar"]:
                try:
                    link = page.locator(f"a:has-text('{texto}')").first
                    if await link.is_visible(timeout=2000):
                        await link.click()
                        await page.wait_for_timeout(2000)
                        log(f"Clicou em '{texto}'", "OK")
                        return True
                except Exception:
                    continue

        except Exception as e:
            log(f"Erro ao navegar {url}: {e}", "AVISO")
            continue

    log("Não encontrei a página do PUSH — use --descobrir para investigar", "ERRO")
    return False


# ============================================================
# ENCONTRAR SELETORES
# ============================================================

async def encontrar_elemento(page, seletores, nome):
    """Tenta cada seletor da lista até encontrar um visível."""
    for sel in seletores:
        try:
            el = page.locator(sel).first
            if await el.is_visible(timeout=1000):
                return el
        except Exception:
            continue
    return None


# ============================================================
# INCLUIR UM PROCESSO
# ============================================================

async def incluir_processo(page, cnj, observacao, dry_run=False):
    """Inclui um processo no PUSH. Retorna: 'ok', 'duplicata', 'erro'."""
    if dry_run:
        log(f"[DRY-RUN] {cnj} | {observacao}", "PUSH")
        return "ok"

    # Encontrar campo CNJ
    campo_cnj = await encontrar_elemento(page, SELETORES_CNJ, "CNJ")
    if not campo_cnj:
        log(f"Campo CNJ não encontrado para {cnj}", "ERRO")
        await _screenshot_erro(page, cnj)
        return "erro"

    # Limpar e preencher CNJ
    await campo_cnj.click()
    await campo_cnj.fill("")
    await campo_cnj.fill(cnj)
    await page.wait_for_timeout(500)

    # Encontrar campo observação (opcional — pode não existir)
    if observacao:
        campo_obs = await encontrar_elemento(page, SELETORES_OBS, "observação")
        if campo_obs:
            await campo_obs.click()
            await campo_obs.fill("")
            await campo_obs.fill(observacao)
            await page.wait_for_timeout(300)

    # Clicar Incluir
    btn = await encontrar_elemento(page, SELETORES_BTN, "Incluir")
    if not btn:
        log(f"Botão Incluir não encontrado para {cnj}", "ERRO")
        await _screenshot_erro(page, cnj)
        return "erro"

    # Retry no click do botão Salvar/Incluir (transiente: elemento interceptado,
    # timeout de rede durante POST do JSF). 3 tentativas, backoff exponencial 2-10s.
    if _TENACITY_OK:
        from playwright.async_api import Error as _PWError, TimeoutError as _PWTimeout
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((_PWError, _PWTimeout, ConnectionError, TimeoutError)),
            reraise=True,
        ):
            with attempt:
                await btn.click()
    else:
        await btn.click()
    await page.wait_for_timeout(2000)

    # Verificar resultado
    body_text = await page.inner_text("body")
    body_lower = body_text.lower()

    # Detectar duplicata em runtime — NÃO abortar o loop, só registrar e seguir
    if any(t in body_lower for t in ["já cadastrado", "já existe", "duplicado", "já incluído", "já incluido"]):
        log(f"Duplicata em runtime (já no PUSH): {cnj} — registrado e seguindo", "AVISO")
        registrar_duplicata_runtime(cnj, contexto="resposta PJe após submit")
        return "duplicata"

    # Detectar erro
    if any(t in body_lower for t in ["erro", "inválido", "invalido", "não encontrado", "nao encontrado"]):
        msg_erro = _extrair_mensagem(body_text)
        log(f"Erro ao incluir {cnj}: {msg_erro}", "ERRO")
        await _screenshot_erro(page, cnj)
        return "erro"

    # Detectar sucesso
    if any(t in body_lower for t in ["sucesso", "incluído", "incluido", "adicionado", "cadastrado"]):
        log(f"Incluído: {cnj} | {observacao}", "OK")
        return "ok"

    # Não detectou nada específico — assume sucesso se não houve erro
    log(f"Incluído (sem confirmação explícita): {cnj}", "OK")
    return "ok"


def _extrair_mensagem(body_text):
    """Extrai primeira mensagem de erro/aviso do body."""
    for linha in body_text.split("\n"):
        linha = linha.strip()
        if any(t in linha.lower() for t in ["erro", "inválido", "não encontrado"]):
            return linha[:100]
    return "(mensagem não identificada)"


async def _screenshot_erro(page, cnj):
    """Salva screenshot em caso de erro."""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    cnj_limpo = re.sub(r'[^0-9]', '', cnj)
    path = SCREENSHOTS_DIR / f"erro_push_{cnj_limpo}_{ts}.png"
    try:
        await page.screenshot(path=str(path))
        log(f"Screenshot salvo: {path.name}", "INFO")
    except Exception:
        pass


# ============================================================
# MODO DESCOBRIR — investiga página do PUSH
# ============================================================

async def modo_descobrir(page):
    """Navega ao PUSH, faz screenshot, lista seletores encontrados."""
    log("=== MODO DESCOBRIR ===", "INFO")

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOTS_DIR / f"push_descobrir_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    await page.screenshot(path=str(path), full_page=True)
    log(f"Screenshot salvo: {path}", "OK")

    log("Seletores encontrados na página:", "INFO")
    inputs = await page.locator("input").all()
    for inp in inputs:
        try:
            id_attr = await inp.get_attribute("id") or ""
            name_attr = await inp.get_attribute("name") or ""
            type_attr = await inp.get_attribute("type") or ""
            value_attr = await inp.get_attribute("value") or ""
            visible = await inp.is_visible()
            if visible:
                print(f"    <input id='{id_attr}' name='{name_attr}' type='{type_attr}' value='{value_attr}'>")
        except Exception:
            continue

    textareas = await page.locator("textarea").all()
    for ta in textareas:
        try:
            id_attr = await ta.get_attribute("id") or ""
            name_attr = await ta.get_attribute("name") or ""
            visible = await ta.is_visible()
            if visible:
                print(f"    <textarea id='{id_attr}' name='{name_attr}'>")
        except Exception:
            continue

    buttons = await page.locator("button, input[type='submit'], input[type='button'], a.btn").all()
    for btn in buttons:
        try:
            text = (await btn.inner_text()).strip()[:50] if await btn.is_visible() else ""
            id_attr = await btn.get_attribute("id") or ""
            if text or id_attr:
                print(f"    <button id='{id_attr}'>{text}</button>")
        except Exception:
            continue

    log("URL atual: " + page.url, "INFO")
    log(f"Analise o screenshot em {path} para identificar os campos corretos", "INFO")


# ============================================================
# MAIN
# ============================================================

async def main():
    parser = argparse.ArgumentParser(description="Incluir processos no PUSH do PJe TJMG")
    parser.add_argument("--limite", type=int, help="Processar apenas os N primeiros")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem executar no browser")
    parser.add_argument("--cnj", help="Incluir apenas este CNJ")
    parser.add_argument("--descobrir", action="store_true", help="Investigar página do PUSH (screenshot + seletores)")
    parser.add_argument("--arquivo", help="Path alternativo para lista de processos")
    parser.add_argument("--porta", type=int, default=9222, help="Porta CDP do Chrome (padrão: 9222)")
    parser.add_argument("--standalone", action="store_true", help="Abrir Chromium próprio em vez de CDP")
    parser.add_argument("--sem-mapa", action="store_true", help="Não filtrar pelo mapa prévio de CNJs cadastrados")
    parser.add_argument("--sem-confirmacao", action="store_true", help="Não pedir confirmação antes (use com cuidado)")
    args = parser.parse_args()

    # Carregar lista
    processos = carregar_lista(args.arquivo)

    # Filtrar por CNJ específico
    if args.cnj:
        cnj_limpo = args.cnj.strip()
        processos = [p for p in processos if p["cnj"] == cnj_limpo]
        if not processos:
            log(f"CNJ {cnj_limpo} não encontrado na lista", "ERRO")
            sys.exit(1)

    # Aplicar limite
    if args.limite:
        processos = processos[:args.limite]

    # Verificação PROATIVA — remove CNJs já cadastrados antes de qualquer processamento
    if not args.sem_mapa:
        mapa = carregar_mapa_push()
        ja_cadastrados = mapa["cnjs"]
        if ja_cadastrados:
            antes = len(processos)
            processos = [p for p in processos if p["cnj"] not in ja_cadastrados]
            ignorados = antes - len(processos)
            if ignorados:
                log(f"Ignorando {ignorados} CNJs já cadastrados (via mapa)", "AVISO")

    log(f"Total de processos a incluir: {len(processos)}", "INFO")

    if not processos:
        log("Nada a incluir — todos os CNJs já estão no PUSH", "OK")
        return

    # Dry run sem browser
    if args.dry_run:
        log("=== DRY RUN ===", "INFO")
        for i, p in enumerate(processos, 1):
            log(f"[{i}/{len(processos)}] {p['cnj']} | {p['observacao']}", "PUSH")
        log(f"Total: {len(processos)} processos seriam incluídos", "OK")
        return

    # Confirmação obrigatória
    if not args.sem_confirmacao:
        print()
        print(f"  Vou incluir {len(processos)} CNJs:")
        for p in processos:
            print(f"    - {p['cnj']} | {p['observacao']}")
        print()
        try:
            resposta = input(f"  Confirma inclusão de {len(processos)} CNJs? (s/n): ").strip().lower()
        except EOFError:
            resposta = ""
        if resposta != "s":
            log("Abortado pelo usuário", "AVISO")
            return

    # Abrir browser (CDP por padrão, standalone com --standalone)
    if args.standalone:
        pw, browser, page = await abrir_browser_standalone()
    else:
        pw, browser, page = await conectar_cdp(args.porta)

    try:
        # Login
        if not await aguardar_login(page):
            log("Login falhou — encerrando", "ERRO")
            return

        # Navegar ao PUSH
        if not await navegar_push(page):
            log("Não consegui acessar o PUSH", "ERRO")
            return

        # Modo descobrir
        if args.descobrir:
            await modo_descobrir(page)
            return

        # Incluir processos
        resultados = {"ok": 0, "duplicata": 0, "erro": 0, "detalhes": []}
        total = len(processos)
        rprint(f"[cyan]Incluindo {total} CNJs no PUSH...[/cyan]")

        _iter = tqdm(list(enumerate(processos, 1)), desc="PUSH", unit="cnj", total=total)
        for i, p in _iter:
            log(f"[{i}/{total}] Incluindo {p['cnj']}...", "PUSH")
            resultado = await incluir_processo(page, p["cnj"], p["observacao"])
            resultados[resultado] += 1
            resultados["detalhes"].append({"cnj": p["cnj"], "resultado": resultado})

            # Detectar se sessão expirou
            url_atual = page.url.lower()
            if "login" in url_atual or "sso" in url_atual:
                log("Sessão expirou! Aguardando re-login...", "AVISO")
                if not await aguardar_login(page):
                    log("Re-login falhou — encerrando", "ERRO")
                    break
                if not await navegar_push(page):
                    log("Não consegui retornar ao PUSH após re-login", "ERRO")
                    break

            # Rate limiting
            await page.wait_for_timeout(2000)

        # Relatório
        print()
        log("=" * 50, "INFO")
        log(f"RESULTADO FINAL", "INFO")
        log(f"  Incluídos com sucesso: {resultados['ok']}", "OK")
        log(f"  Duplicatas (já no PUSH): {resultados['duplicata']}", "AVISO")
        log(f"  Erros: {resultados['erro']}", "ERRO" if resultados['erro'] > 0 else "INFO")
        log(f"  Total processado: {total}", "INFO")
        log("=" * 50, "INFO")

        # Salvar relatório
        relatorio_path = Path(__file__).parent / f"resultado-push-{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(relatorio_path, "w", encoding="utf-8") as f:
            json.dump({
                "data": datetime.now().isoformat(),
                "total": total,
                **{k: v for k, v in resultados.items() if k != "detalhes"},
                "detalhes": resultados["detalhes"],
            }, f, indent=2, ensure_ascii=False)
        log(f"Relatório salvo: {relatorio_path.name}", "OK")
        if resultados["erro"] > 0:
            rprint(f"[red]Inclusão finalizada com {resultados['erro']} erros[/red]")
        else:
            rprint(f"[green]Inclusão finalizada — {resultados['ok']} OK, {resultados['duplicata']} duplicatas[/green]")

    finally:
        if args.standalone:
            await browser.close()
        await pw.stop()


def _main_cli():
    try:
        from pje_lock import acquire_lock, LockBusy
    except ImportError:
        asyncio.run(main())
        return 0
    try:
        with acquire_lock("pje-chrome-profile", timeout=0):  # ref: PJE-020
            asyncio.run(main())
        return 0
    except LockBusy as exc:
        print(f"[BLOQUEADO] {exc} — evite rodar scripts PJe concorrentes no mesmo perfil.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(_main_cli())
