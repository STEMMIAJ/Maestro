#!/usr/bin/env python3
"""
baixar_push_pje.py - Download automatico processos PJe PUSH (TJMG)
v2: Perfil isolado, sem conflito com Chrome do usuario.

Uso:
  python baixar_push_pje.py                          # Baixa todos
  python baixar_push_pje.py --limite 1               # Teste com 1
  python baixar_push_pje.py --download-dir C:\pdfs   # Pasta customizada
  python baixar_push_pje.py --pagina 3               # Comeca na pagina 3

Requisitos: pip install selenium
"""

import argparse
import json
import os
import platform
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# Importar módulo de verificação/Telegram/janela (mesmo diretório)
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from pje_verificacao import (
        verificar_conteudo, slug_comarca, notificar_telegram,
        janela_disponivel, esperar_janela_liberar,
        ordenar_por_comarca, mover_para_quarentena,
    )
    _VERIF_OK = True
except Exception as _e:
    _VERIF_OK = False
    print(f"[aviso] pje_verificacao não disponível: {_e}", file=sys.stderr)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    ElementClickInterceptedException, UnexpectedAlertPresentException,
)

# Polimento 2026-04-19 (plano binary-gliding-pine): tqdm, rich. Opcionais.
# NOTA: tenacity NÃO aplicado aqui — aguardar_download já possui retry manual
# por loop de polling + reconfirmação de hash (fix dedup de 2026-04-19). Não
# duplicar para não mascarar o sinal de falha.
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

# Validação do config em runtime (fail-soft)
try:
    _cfg_path = Path(__file__).resolve().parent.parent / "config"
    if str(_cfg_path) not in sys.path:
        sys.path.insert(0, str(_cfg_path))
    from config_validacao import validar_config as _validar_config
    _res = _validar_config()
    if not _res.get("ok", True):
        rprint(f"[yellow][config-validacao] avisos: {_res}[/yellow]")
except Exception as _e:
    print(f"[config-validacao] skip: {_e}", file=sys.stderr)

# ── CONFIG ────────────────────────────────────────────────────
PJE_BASE = "https://pje.tjmg.jus.br"
PJE_LOGIN = f"{PJE_BASE}/pje/login.seam"
PJE_PAINEL = f"{PJE_BASE}/pje/Painel/painel_usuario/advogado.seam"

if platform.system() == "Windows":
    HOME = Path(os.environ.get("USERPROFILE", "C:\\Users\\jesus"))
else:
    HOME = Path.home()

DEFAULT_DOWNLOAD_DIR = HOME / "Desktop" / "processos-pje"
ORDEM_COMARCA_DEFAULT = ["0680", "0627", "0105", "0396"]  # Taiobeiras→GV→Mantena
SLEEP_ENTRE_PROCESSOS = 20       # segundos de pausa entre downloads
PAUSA_LONGA_A_CADA = 10          # a cada N OK, pausa longa
SLEEP_PAUSA_LONGA = 180          # 3 min
NOTIFICAR_A_CADA = 10            # Telegram a cada N OK confirmados

# Perfil FIXO e PERSISTENTE — cookies/sessao sobrevivem entre execucoes.
# NUNCA e temporario, NUNCA e recriado. Diretorio fica no Desktop para visibilidade.
if platform.system() == "Windows":
    AUTOMATION_PROFILE = Path(r"C:\Users\jesus\Desktop\chrome-pje-profile")
else:
    AUTOMATION_PROFILE = HOME / "Desktop" / "chrome-pje-profile"

WAIT_LOGIN = 300     # 5 min para login manual
WAIT_DOWNLOAD = 180  # 3 min para download de PDF
TIMEOUT_PROCESSO = 300  # 5 min por processo — PDFs grandes precisam de tempo
CNJ_RE = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")


# ── DEDUP PERSISTENTE ─────────────────────────────────────────
# Fix 2026-04-19: loop infinito baixando 7x o mesmo CNJ.
# Causa: arquivos salvos com hash do PJe (sem CNJ no nome) nunca batiam
# com "if num in f" em _encontrar_valido_existente. Solução: índice
# JSON mapeando CNJ -> caminho real, consultado ANTES de tentar baixar.

_DEDUP_INDEX_PATH = None            # set pelo main() com download_dir
_DEDUP_INDEX = {}                   # {cnj: {"path": str, "kb": int, "ts": str, "comarca": str}}
_CNJS_BAIXADOS_SESSAO = set()       # dedup adicional na execução corrente


def _carregar_dedup_index(download_dir):
    global _DEDUP_INDEX_PATH, _DEDUP_INDEX
    _DEDUP_INDEX_PATH = Path(download_dir) / "_downloads_feitos.json"
    if _DEDUP_INDEX_PATH.exists():
        try:
            _DEDUP_INDEX = json.loads(_DEDUP_INDEX_PATH.read_text(encoding="utf-8"))
        except Exception:
            _DEDUP_INDEX = {}
    else:
        _DEDUP_INDEX = {}
    return _DEDUP_INDEX


def _salvar_dedup_index():
    if _DEDUP_INDEX_PATH:
        try:
            _DEDUP_INDEX_PATH.write_text(
                json.dumps(_DEDUP_INDEX, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            print(f"[aviso] falha ao salvar dedup_index: {e}", file=sys.stderr)


def _marcar_baixado(cnj, destino_path, kb, comarca=""):
    _DEDUP_INDEX[cnj] = {
        "path": str(Path(destino_path).resolve()),
        "kb": int(kb),
        "ts": datetime.now().isoformat(timespec="seconds"),
        "comarca": comarca or "",
    }
    _CNJS_BAIXADOS_SESSAO.add(cnj)
    _salvar_dedup_index()


def _ja_baixado_idx(cnj):
    """Retorna entry do índice se CNJ já foi baixado e arquivo ainda existe."""
    entry = _DEDUP_INDEX.get(cnj)
    if not entry:
        return None
    p = Path(entry.get("path", ""))
    if p.exists() and p.stat().st_size > 0:
        return entry
    # Arquivo sumiu — limpar entry fantasma
    _DEDUP_INDEX.pop(cnj, None)
    _salvar_dedup_index()
    return None


# ── OBSERVABILIDADE ───────────────────────────────────────────
_log_entries = []


def log(msg, level="INFO", selector=None, elapsed=None, arquivo=None, erro=None):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    prefix = {"INFO": "  ", "OK": " [OK]", "ERR": " [ERRO]", "WAIT": " [...]", "DL": " [DL]"}
    entry = {"timestamp": datetime.now().isoformat(), "level": level, "msg": msg}
    if selector:
        entry["selector"] = selector
    if elapsed is not None:
        entry["elapsed_s"] = round(elapsed, 2)
    if arquivo:
        entry["arquivo"] = str(arquivo)
    if erro:
        entry["erro"] = str(erro)
    _log_entries.append(entry)

    line = f"[{ts}]{prefix.get(level, '  ')} {msg}"
    if elapsed is not None:
        line += f" ({elapsed:.1f}s)"
    if arquivo:
        line += f" -> {arquivo}"
    print(line)


# ── BROWSER ISOLADO ───────────────────────────────────────────

def limpar_locks():
    """Remove APENAS locks de processo (nao cookies/sessao).
    Necessario quando Chrome da automacao crashou e deixou lock orfao."""
    for f in ["SingletonLock", "SingletonSocket", "SingletonCookie"]:
        lock = AUTOMATION_PROFILE / f
        try:
            if lock.exists():
                lock.unlink()
        except Exception:
            pass


def criar_browser(download_dir):
    """Conecta ao Chrome JA ABERTO ou abre novo.
    Estrategia: Chrome ja rodando > abrir novo com perfil isolado."""
    download_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # === MODO 1: Conectar ao Chrome existente via debuggerAddress ===
    # Tenta primeiro a porta usada pelos executores PJe atuais.
    for porta in [9223, 9222]:
        try:
            import urllib.request
            resp = urllib.request.urlopen(f"http://127.0.0.1:{porta}/json/version", timeout=3)
            data = resp.read().decode()
            if "Browser" in data:
                log(f"Chrome debug ativo na porta {porta}!", "OK")
                opts = Options()
                opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{porta}")
                driver = webdriver.Chrome(options=opts)
                driver.implicitly_wait(5)
                log(f"Conectado ao Chrome existente (porta {porta})", "OK", elapsed=time.time() - t0)
                return driver
        except Exception:
            pass

    # === MODO 2: Abrir Chrome novo com perfil isolado ===
    log("Nenhum Chrome debug encontrado. Abrindo Chrome novo...")
    AUTOMATION_PROFILE.mkdir(parents=True, exist_ok=True)
    limpar_locks()
    log(f"Perfil: {AUTOMATION_PROFILE}")

    opts = Options()
    opts.add_argument(f"--user-data-dir={AUTOMATION_PROFILE}")
    opts.add_argument("--remote-debugging-port=9223")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--disable-session-crashed-bubble")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_experimental_option("detach", True)

    prefs = {
        "download.default_directory": str(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,
    }
    opts.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(5)
    log(f"Chrome novo aberto com perfil isolado", "OK", elapsed=time.time() - t0)
    return driver


# ── AUTENTICACAO ──────────────────────────────────────────────

def esperar_login(driver):
    """Espera autenticacao manual VidaaS. Timeout: 5 min."""
    log("Aguardando login manual VidaaS/gov.br...", "WAIT")
    log("Faca login na janela do Chrome. O script detecta automaticamente.")
    t0 = time.time()
    try:
        WebDriverWait(driver, WAIT_LOGIN).until(
            lambda d: sessao_ativa(d)
        )
        log("Login detectado!", "OK", elapsed=time.time() - t0)
        return True
    except TimeoutException:
        log("Timeout de login (5 min)", "ERR", elapsed=time.time() - t0)
        return False


# ── SESSAO ───────────────────────────────────────────────────

def sessao_ativa(driver):
    """Verifica se ainda esta logado no PJe."""
    try:
        url = (driver.current_url or "").lower()
        if "login" in url or "auth" in url or "sso.cloud" in url:
            return False
        titulo = driver.title or ""
        src = driver.page_source[:6000]
        src_n = src.lower()
        if "cpf/cnpj" in src_n and "senha" in src_n:
            return False
        return any(
            [
                "painel_usuario" in url,
                "push/listview" in url,
                "painel" in titulo.lower(),
                "quadro de avisos" in src_n,
                "painel do usuario" in src_n,
                "painel do usuário" in src_n,
                "processos cadastrados" in src_n,
                bool(CNJ_RE.search(src)),
            ]
        )
    except Exception:
        return False


def relogar(driver):
    """Navega para login e espera autenticacao manual."""
    log("Sessao expirou! Redirecionando para login...", "WAIT")
    driver.get(PJE_LOGIN)
    time.sleep(3)
    return esperar_login(driver)


# ── NAVEGACAO PUSH ────────────────────────────────────────────

def navegar_para_push(driver):
    """Navega para aba PUSH do Painel do Advogado."""
    t0 = time.time()
    log("Navegando para Painel do Advogado...")
    driver.get(PJE_PAINEL)

    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
    except TimeoutException:
        pass
    time.sleep(3)

    seletores = [
        (By.LINK_TEXT, "PUSH"),
        (By.PARTIAL_LINK_TEXT, "PUSH"),
        (By.XPATH, "//a[normalize-space(text())='PUSH']"),
        (By.XPATH, "//span[normalize-space(text())='PUSH']"),
        (By.CSS_SELECTOR, "a[href*='Push'], a[href*='push']"),
    ]

    for by, sel in seletores:
        try:
            els = driver.find_elements(by, sel)
            for el in els:
                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", el
                    )
                    time.sleep(3)
                    log("Na aba PUSH!", "OK", selector=f"{by}={sel}", elapsed=time.time() - t0)
                    return True
                except Exception:
                    continue
        except Exception:
            continue

    # Fallback: URL direta
    try:
        driver.get(f"{PJE_BASE}/pje/Push/listView.seam?iframe=true")
        time.sleep(3)
        if "push" in driver.current_url.lower():
            log("Na aba PUSH (URL direta)!", "OK", elapsed=time.time() - t0)
            return True
    except Exception:
        pass

    log("Falha ao navegar para PUSH", "ERR", elapsed=time.time() - t0)
    return False


# ── EXTRACAO DE PROCESSOS ─────────────────────────────────────

def extrair_processos(driver):
    """Extrai CNJs da tabela PUSH."""
    t0 = time.time()
    processos = []
    cnjs_vistos = set()

    rows = []
    sel_usado = ""
    for selector in ["table tbody tr", "table tr", ".rich-table-row", ".rf-dt-r", "tr"]:
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, selector)
            tem_cnj = False
            for row in rows:
                texto = row.text or ""
                html = row.get_attribute("innerHTML") or ""
                if CNJ_RE.search(f"{texto} {html}"):
                    tem_cnj = True
                    break
            if tem_cnj:
                sel_usado = selector
                break
        except Exception:
            continue

    log(f"{len(rows)} linhas na tabela", selector=sel_usado)

    for i, row in enumerate(rows):
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 2:
            continue

        num = ""
        for cell in cells:
            try:
                m = CNJ_RE.search(cell.text.strip())
                if m:
                    num = m.group()
                    break
            except Exception:
                continue

        if not num:
            for cell in cells:
                try:
                    html = cell.get_attribute("innerHTML") or ""
                    m = CNJ_RE.search(html)
                    if m:
                        num = m.group()
                        break
                except Exception:
                    continue

        if num and num not in cnjs_vistos:
            cnjs_vistos.add(num)
            processos.append({"index": i, "numero": num})

    log(f"{len(processos)} processos extraidos", "OK", elapsed=time.time() - t0)
    return processos


# ── DOWNLOAD ──────────────────────────────────────────────────

def aceitar_alert(driver):
    try:
        alert = driver.switch_to.alert
        log(f"Alert: {alert.text[:60]}")
        alert.accept()
        time.sleep(1)
        return True
    except Exception:
        return False


def js_click(driver, el):
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", el
    )


def aguardar_download(download_dir, arquivos_antes, timeout=WAIT_DOWNLOAD):
    """Aguarda download real: arquivo novo sem .crdownload pendente."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(3)
        agora = set(os.listdir(str(download_dir)))
        novos = agora - arquivos_antes
        completos = [f for f in novos if not f.endswith((".crdownload", ".tmp"))]
        pendentes = [f for f in novos if f.endswith(".crdownload")]

        if completos:
            return completos[0], time.time() - t0

        if pendentes and time.time() - t0 > 10:
            log(f"Download em progresso: {pendentes[0]}", "DL")

    return None, time.time() - t0


def _timeout_check(t0, label=""):
    """Retorna True se excedeu TIMEOUT_PROCESSO."""
    if time.time() - t0 > TIMEOUT_PROCESSO:
        log(f"TIMEOUT {TIMEOUT_PROCESSO}s atingido{' — ' + label if label else ''}", "ERR")
        return True
    return False


def _encontrar_botao_download_final(driver):
    """Busca agressiva do botao DOWNLOAD/GERAR dentro da pagina/iframe atual."""
    # 1. Texto exato em botoes e links
    for btn in driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit'], input[type='button'], a"):
        txt = (btn.text.strip() or btn.get_attribute("value") or "").upper()
        if txt in ("DOWNLOAD", "BAIXAR", "GERAR PDF", "GERAR", "OK"):
            return btn, f"texto='{txt}'"

    # 2. Title parcial
    for btn in driver.find_elements(By.CSS_SELECTOR, "[title*='ownload'], [title*='aixar'], [title*='erar']"):
        return btn, f"title='{btn.get_attribute('title')}'"

    # 3. XPATH contendo texto parcial (pega botoes com spans internos)
    for xpath in [
        "//button[contains(translate(., 'download', 'DOWNLOAD'), 'DOWNLOAD')]",
        "//button[contains(translate(., 'baixar', 'BAIXAR'), 'BAIXAR')]",
        "//input[translate(@value, 'download', 'DOWNLOAD')='DOWNLOAD']",
        "//a[contains(translate(., 'download', 'DOWNLOAD'), 'DOWNLOAD')]",
    ]:
        els = driver.find_elements(By.XPATH, xpath)
        if els:
            return els[0], f"xpath={xpath[:40]}"

    # 4. Classes tipicas PJe/RichFaces
    for btn in driver.find_elements(By.CSS_SELECTOR, ".btn-primary, .btn-info, .btn-success, .rf-bt, .rich-btn"):
        txt = (btn.text.strip() or btn.get_attribute("value") or "")
        if txt:
            return btn, f"class='{btn.get_attribute('class')[:30]}' texto='{txt}'"

    # 5. Qualquer input[type=submit] visivel
    for btn in driver.find_elements(By.CSS_SELECTOR, "input[type='submit']"):
        if btn.is_displayed():
            return btn, f"submit-visivel value='{btn.get_attribute('value')}'"

    return None, ""


def baixar_processo(driver, idx, num, download_dir):
    """Baixa autos completos de um processo. Timeout hard de {TIMEOUT_PROCESSO}s."""
    t0 = time.time()
    log(f"Processo: {num}")

    # ★ Dedup por índice persistente (fix 2026-04-19: loop infinito 7x)
    # Consulta JSON antes de tentar qualquer coisa — evita re-download
    # quando arquivo foi salvo com hash do PJe (sem CNJ no filename)
    if num in _CNJS_BAIXADOS_SESSAO:
        log(f"Ja baixado nesta execucao (dedup sessao): {num}", "OK")
        return {"numero": num, "status": "ja-baixado-sessao", "tempo_s": 0}

    entry_idx = _ja_baixado_idx(num)
    if entry_idx:
        log(f"Ja baixado (indice): {Path(entry_idx['path']).name} "
            f"({entry_idx['kb']} KB, {entry_idx['ts']})", "OK",
            arquivo=entry_idx["path"])
        _CNJS_BAIXADOS_SESSAO.add(num)
        return {"numero": num, "status": "ja-baixado-idx",
                "arquivo": entry_idx["path"], "kb": entry_idx["kb"]}

    safe = re.sub(r"[/\\: ]", "_", num)
    destino = download_dir / f"{safe}.pdf"
    # Dedup ROBUSTO: verifica CONTEÚDO antes de confiar no filename (fix 17/abr)
    # Bug antigo: arquivos quebrados (conteúdo de outro processo) passavam como "já baixado"
    def _encontrar_valido_existente():
        candidatos = [destino] if destino.exists() else []
        for f in os.listdir(str(download_dir)):
            if num in f and f.endswith(".pdf"):
                candidatos.append(download_dir / f)
        # Verificar conteúdo de cada candidato
        if _VERIF_OK:
            for c in candidatos:
                try:
                    ok, _cnj, _com, _raz = verificar_conteudo(c, num)
                    if ok:
                        return c
                except Exception:
                    continue
            return None
        # Sem módulo de verificação, comportamento antigo
        return candidatos[0] if candidatos else None

    valido = _encontrar_valido_existente()
    if valido:
        sz = valido.stat().st_size
        log(f"Ja baixado (conteudo conferido): {valido.name} ({sz // 1024} KB)", "OK",
            arquivo=str(valido.resolve()))
        # Importar pro índice — evita re-verificar conteúdo em próximas execuções
        _marcar_baixado(num, valido, sz // 1024)
        return {"numero": num, "status": "ja-baixado",
                "arquivo": str(valido.resolve()), "kb": sz // 1024}

    aba_push = driver.current_window_handle
    opened_same_tab = False

    try:
        # 1. Encontrar linha por CNJ
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        row = None
        for r in rows:
            try:
                if num in r.text:
                    row = r
                    break
            except Exception:
                continue
            try:
                html = r.get_attribute("innerHTML") or ""
                if num in html:
                    row = r
                    break
            except Exception:
                continue

        if not row:
            log(f"CNJ {num} nao encontrado na tabela (total linhas: {len(rows)})", "ERR")
            return {"numero": num, "status": "erro", "erro": "CNJ nao encontrado na tabela"}

        # Achar botao Autos Digitais na linha
        autos_btn = None
        sel_usado = ""
        for link in row.find_elements(By.TAG_NAME, "a"):
            title = (link.get_attribute("title") or "").lower()
            href = (link.get_attribute("href") or "").lower()
            if any(k in title for k in ["auto", "digital", "visualizar", "abrir"]):
                autos_btn = link
                sel_usado = f"title={link.get_attribute('title')}"
                break
            if any(k in href for k in ["autos", "processo", "visualiz"]):
                autos_btn = link
                sel_usado = f"href(parcial)"
                break

        if not autos_btn:
            for link in row.find_elements(By.TAG_NAME, "a"):
                title = (link.get_attribute("title") or "").lower()
                if any(k in title for k in ["editar", "excluir", "remover", "deletar"]):
                    continue
                autos_btn = link
                sel_usado = "primeiro-link-nao-destrutivo"
                break

        if not autos_btn:
            log("Botao Autos nao encontrado na linha", "ERR")
            return {"numero": num, "status": "erro", "erro": "Botao Autos nao encontrado"}

        log("Clicando Autos Digitais", selector=sel_usado)
        abas_antes = set(driver.window_handles)
        js_click(driver, autos_btn)
        time.sleep(2)
        aceitar_alert(driver)
        time.sleep(2)

        if _timeout_check(t0, "apos clicar Autos"):
            fechar_abas_extras(driver, aba_push)
            return {"numero": num, "status": "timeout", "tempo_s": round(time.time() - t0, 1)}

        # 2. Trocar para nova aba
        opened_same_tab = False
        novas = set(driver.window_handles) - abas_antes
        if novas:
            driver.switch_to.window(novas.pop())
            log("Autos abertos (nova aba)")
        else:
            opened_same_tab = True
            log("Autos abertos (mesma aba)")

        # 3. Clicar icone "Download autos do processo"
        dl_btn = None
        sel_dl = ""
        for el in driver.find_elements(By.CSS_SELECTOR, "a[title], button[title], span[title]"):
            title = el.get_attribute("title") or ""
            if "download autos" in title.lower():
                dl_btn = el
                sel_dl = f"title={title}"
                break

        if not dl_btn:
            for el in driver.find_elements(By.CSS_SELECTOR, ".fa-download, [class*='download']"):
                dl_btn = el
                sel_dl = "class=fa-download"
                break

        if not dl_btn:
            log("Icone download nao encontrado", "ERR")
            fechar_abas_extras(driver, aba_push)
            return {"numero": num, "status": "erro", "erro": "Icone download nao encontrado"}

        log("Clicando icone download autos", selector=sel_dl)
        js_click(driver, dl_btn)
        time.sleep(3)

        if _timeout_check(t0, "apos clicar download icon"):
            fechar_abas_extras(driver, aba_push)
            return {"numero": num, "status": "timeout", "tempo_s": round(time.time() - t0, 1)}

        # 4. Iframe — esperar ate 15s com checagem agressiva
        in_iframe = False
        iframe_deadline = time.time() + 15
        while time.time() < iframe_deadline and not _timeout_check(t0):
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if not iframes:
                time.sleep(2)
                continue

            for iframe in iframes:
                try:
                    driver.switch_to.frame(iframe)
                    in_iframe = True
                    # Checar se tem conteudo util
                    test = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit'], a, select")
                    if test:
                        log(f"Iframe com {len(test)} elementos", "OK")
                        break
                    driver.switch_to.default_content()
                    in_iframe = False
                except Exception:
                    try:
                        driver.switch_to.default_content()
                    except Exception:
                        pass
                    in_iframe = False

            if in_iframe:
                break
            time.sleep(2)

        # 5. Configurar dropdowns: expediente/movimentos -> Sim
        selects = driver.find_elements(By.TAG_NAME, "select")
        for sel in selects:
            try:
                s = Select(sel)
                if s.first_selected_option.text.strip() == "N\u00e3o":
                    s.select_by_visible_text("Sim")
                    time.sleep(0.3)
            except Exception:
                continue

        # 6. Botao DOWNLOAD final — busca agressiva
        dl_final, sel_info = _encontrar_botao_download_final(driver)

        # Se nao achou no iframe, tenta fora dele
        if not dl_final and in_iframe:
            driver.switch_to.default_content()
            in_iframe = False
            dl_final, sel_info = _encontrar_botao_download_final(driver)

        if not dl_final:
            log("Botao DOWNLOAD nao encontrado — SKIP", "ERR")
            if in_iframe:
                driver.switch_to.default_content()
            fechar_abas_extras(driver, aba_push)
            return {"numero": num, "status": "erro", "erro": "Botao DOWNLOAD nao encontrado"}

        log(f"Botao DOWNLOAD: {sel_info}")
        arquivos_antes = set(os.listdir(str(download_dir)))
        abas_antes_dl = set(driver.window_handles)

        log("Clicando DOWNLOAD...", "DL")
        js_click(driver, dl_final)

        # 7. Esperar aba PDF ou download direto (com timeout do processo)
        aba_pdf = None
        while not _timeout_check(t0, "esperando PDF"):
            time.sleep(3)
            novas_pdf = set(driver.window_handles) - abas_antes_dl
            if novas_pdf:
                aba_pdf = novas_pdf.pop()
                break
            agora = set(os.listdir(str(download_dir)))
            novos = agora - arquivos_antes
            completos = [f for f in novos if not f.endswith((".crdownload", ".tmp"))]
            if completos:
                break

        if aba_pdf:
            driver.switch_to.window(aba_pdf)
            time.sleep(2)
            try:
                from selenium.webdriver.common.keys import Keys
                mod = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
                driver.find_element(By.TAG_NAME, "body").send_keys(mod + "s")
                time.sleep(2)
            except Exception:
                pass

        # 8. Aguardar download real (respeitando timeout global do processo)
        restante = max(10, TIMEOUT_PROCESSO - (time.time() - t0))
        novo_arquivo, tempo_dl = aguardar_download(download_dir, arquivos_antes, timeout=restante)

        if in_iframe:
            try:
                driver.switch_to.default_content()
            except Exception:
                pass

        if novo_arquivo:
            caminho = download_dir / novo_arquivo
            sz = caminho.stat().st_size if caminho.exists() else 0

            # ★ VERIFICAÇÃO PÓS-DOWNLOAD (fix 17/abr) — core do fix do bug do cache
            cnj_real = ""
            comarca = ""
            conferido = False
            razao_verif = "verificacao_indisponivel"
            if _VERIF_OK:
                try:
                    conferido, cnj_real, comarca, razao_verif = verificar_conteudo(caminho, num)
                except Exception as _verr:
                    log(f"Falha ao verificar conteudo: {_verr}", "ERR")

            if _VERIF_OK and not conferido:
                # PDF baixado com conteúdo ERRADO (bug do cache de sessão do PJe)
                try:
                    novo_nome = f"{safe}__CONTEM_{cnj_real or 'desconhecido'}__{razao_verif}.pdf"
                    destino_inv = mover_para_quarentena(caminho, "_invalidos", novo_nome)
                    log(f"INVALIDO: conteudo != esperado ({razao_verif}) -> {destino_inv.name}", "ERR",
                        arquivo=str(destino_inv.resolve()), elapsed=time.time() - t0)
                    result = {
                        "numero": num, "status": "conteudo-divergente",
                        "cnj_real_encontrado": cnj_real, "razao": razao_verif,
                        "arquivo": str(destino_inv.resolve()), "tempo_s": round(time.time() - t0, 1),
                    }
                except Exception as _merr:
                    log(f"Erro ao mover invalido: {_merr}", "ERR")
                    result = {"numero": num, "status": "conteudo-divergente",
                              "erro_mover": str(_merr), "tempo_s": round(time.time() - t0, 1)}
            else:
                # Conteúdo OK (ou verificação desabilitada). Renomear com padrão seguro.
                try:
                    if _VERIF_OK and comarca:
                        novo_stem = f"{safe}__{slug_comarca(comarca)}"
                    else:
                        novo_stem = safe
                    destino = download_dir / f"{novo_stem}.pdf"
                    if destino.exists() and destino != caminho:
                        destino = download_dir / f"{novo_stem}_{datetime.now().strftime('%H%M%S')}.pdf"
                    if caminho != destino:
                        caminho.rename(destino)
                    status_tag = "OK-CONFERIDO" if conferido else "SALVO"
                    log(f"{status_tag}: {destino.name} ({sz // 1024} KB)", "OK",
                        arquivo=str(destino.resolve()), elapsed=time.time() - t0)
                except Exception:
                    destino = caminho
                    log(f"Salvo (sem renomear): {novo_arquivo} ({sz // 1024} KB)", "OK",
                        arquivo=str(caminho.resolve()), elapsed=time.time() - t0)

                # ★ Registrar no índice de dedup (fix loop infinito)
                try:
                    _marcar_baixado(num, destino, sz // 1024, comarca=comarca)
                except Exception as _ierr:
                    log(f"Aviso: falha ao atualizar indice dedup: {_ierr}", "ERR")

                result = {
                    "numero": num, "status": "ok",
                    "arquivo": str(destino.resolve()), "nome": destino.name,
                    "kb": sz // 1024, "tempo_s": round(time.time() - t0, 1),
                    "conferido": conferido, "comarca": comarca,
                }
        else:
            log("Download nao concluiu no timeout", "ERR", elapsed=time.time() - t0)
            result = {"numero": num, "status": "download-timeout", "tempo_s": round(time.time() - t0, 1)}

    except Exception as e:
        log(f"Erro: {e}", "ERR", erro=str(e), elapsed=time.time() - t0)
        result = {"numero": num, "status": "erro", "erro": str(e), "tempo_s": round(time.time() - t0, 1)}

    fechar_abas_extras(driver, aba_push)

    # Se Autos abriu na mesma aba, a aba PUSH agora mostra a pagina do processo.
    # Precisamos voltar para o PUSH para que o proximo processo encontre a tabela.
    if opened_same_tab:
        log("Voltando para PUSH (mesma aba)...")
        navegar_para_push(driver)

    return result


def fechar_abas_extras(driver, aba_principal):
    try:
        for handle in driver.window_handles:
            if handle != aba_principal:
                driver.switch_to.window(handle)
                driver.close()
        driver.switch_to.window(aba_principal)
        time.sleep(1)
    except Exception:
        try:
            driver.switch_to.window(aba_principal)
        except Exception:
            if driver.window_handles:
                driver.switch_to.window(driver.window_handles[0])


def detectar_total_paginas(driver):
    """Detecta total de paginas via RichFaces DataScroller (spans, nao links)."""
    max_pag = 1
    # RichFaces: <span class="rf-ds-nmb">N</span>
    for sel in [".rf-ds-nmb", ".rf-ds span", "[class*='ds-nmb']", "[class*='datascr'] span"]:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in els:
                txt = el.text.strip()
                if txt.isdigit() and 1 <= int(txt) <= 200:
                    max_pag = max(max_pag, int(txt))
        except Exception:
            continue
    # Fallback JS: varrer todo o DOM
    if max_pag <= 1:
        try:
            max_pag = driver.execute_script("""
                var spans = document.querySelectorAll('span, a, td');
                var mx = 1;
                for (var i = 0; i < spans.length; i++) {
                    var t = spans[i].textContent.trim();
                    var cls = (spans[i].className || '').toLowerCase();
                    if (/^\\d+$/.test(t) && (cls.indexOf('ds') >= 0 || cls.indexOf('pag') >= 0 || cls.indexOf('scr') >= 0)) {
                        var n = parseInt(t);
                        if (n > mx && n <= 200) mx = n;
                    }
                }
                return mx;
            """) or 1
        except Exception:
            pass
    log(f"Paginacao detectada: {max_pag} paginas", "OK")
    return max_pag


def proxima_pagina(driver, pag_atual=0):
    """Avanca para proxima pagina. PJe usa <span> RichFaces, nao <a>."""
    prox = pag_atual + 1

    # Debug: listar elementos de paginacao (spans RichFaces + qualquer <a>)
    pag_txts = []
    try:
        els = driver.find_elements(By.CSS_SELECTOR, ".rf-ds span, .rf-ds a, [class*='ds-nmb'], [class*='ds-btn']")
        for el in els:
            t = el.text.strip()
            if t:
                cls = el.get_attribute("class") or ""
                pag_txts.append(f"{t}({cls[:15]})")
    except Exception:
        pass
    log(f"Paginacao visivel: {pag_txts}")

    # 1. RichFaces: span.rf-ds-nmb com texto = proxima pagina
    try:
        els = driver.find_elements(By.CSS_SELECTOR, ".rf-ds-nmb")
        for el in els:
            if el.text.strip() == str(prox):
                cls = (el.get_attribute("class") or "").lower()
                if "rf-ds-dis" not in cls and "disabled" not in cls:
                    driver.execute_script("arguments[0].click();", el)
                    time.sleep(3)
                    log(f"Pagina {prox} (rf-ds-nmb)", "OK")
                    return True
    except Exception:
        pass

    # 2. RichFaces: span.rf-ds-btn-next (botao ›)
    try:
        els = driver.find_elements(By.CSS_SELECTOR, ".rf-ds-btn-next")
        for el in els:
            cls = (el.get_attribute("class") or "").lower()
            if "rf-ds-dis" not in cls and "disabled" not in cls:
                driver.execute_script("arguments[0].click();", el)
                time.sleep(3)
                log(f"Pagina {prox} (rf-ds-btn-next)", "OK")
                return True
    except Exception:
        pass

    # 3. Qualquer span/a/td com texto = numero da proxima pagina
    try:
        els = driver.find_elements(By.XPATH, f"//*[normalize-space(text())='{prox}']")
        for el in els:
            cls = (el.get_attribute("class") or "").lower()
            tag = el.tag_name.lower()
            # Ignorar celulas de tabela com dados (td de processos)
            if tag in ("span", "a", "button") and "disabled" not in cls and "rf-ds-dis" not in cls:
                driver.execute_script("arguments[0].click();", el)
                time.sleep(3)
                log(f"Pagina {prox} (xpath {tag})", "OK")
                return True
    except Exception:
        pass

    # 4. Qualquer elemento com texto » ou › (proximo)
    for simbolo in ["\u203a", "\u00bb", ">"]:
        try:
            els = driver.find_elements(By.XPATH, f"//*[normalize-space(text())='{simbolo}']")
            for el in els:
                cls = (el.get_attribute("class") or "").lower()
                if "disabled" not in cls and "rf-ds-dis" not in cls:
                    txt = el.text.strip()
                    # Ignorar »» (ultima pagina)
                    if txt in ("\u00bb\u00bb", ">>"):
                        continue
                    driver.execute_script("arguments[0].click();", el)
                    time.sleep(3)
                    log(f"Pagina {prox} (simbolo '{simbolo}')", "OK")
                    return True
        except Exception:
            continue

    # 5. Nuclear: JavaScript puro — busca no DOM inteiro
    try:
        result = driver.execute_script(f"""
            // Tentar rf-ds-nmb primeiro
            var nmbs = document.querySelectorAll('.rf-ds-nmb');
            for (var i = 0; i < nmbs.length; i++) {{
                if (nmbs[i].textContent.trim() === '{prox}') {{
                    nmbs[i].click();
                    return 'nmb';
                }}
            }}
            // Tentar rf-ds-btn-next
            var btns = document.querySelectorAll('.rf-ds-btn-next');
            for (var i = 0; i < btns.length; i++) {{
                if (btns[i].className.indexOf('rf-ds-dis') < 0) {{
                    btns[i].click();
                    return 'btn-next';
                }}
            }}
            // Ultimo recurso: qualquer span com o numero
            var all = document.querySelectorAll('span, a');
            for (var i = 0; i < all.length; i++) {{
                if (all[i].textContent.trim() === '{prox}' && all[i].offsetParent !== null) {{
                    all[i].click();
                    return 'any';
                }}
            }}
            return false;
        """)
        if result:
            time.sleep(3)
            log(f"Pagina {prox} (JS: {result})", "OK")
            return True
    except Exception:
        pass

    log(f"FALHOU avancar da pagina {pag_atual}. Elementos visiveis: {pag_txts}", "ERR")
    return False


def ir_pagina_direta(driver, numero):
    """Clica diretamente no numero da pagina."""
    # RichFaces span
    try:
        els = driver.find_elements(By.CSS_SELECTOR, ".rf-ds-nmb")
        for el in els:
            if el.text.strip() == str(numero):
                driver.execute_script("arguments[0].click();", el)
                time.sleep(3)
                log(f"Pagina {numero} (rf-ds-nmb direto)", "OK")
                return True
    except Exception:
        pass
    # Fallback
    return proxima_pagina(driver, numero - 1)


def ir_pagina(driver, alvo):
    if alvo <= 1:
        return
    for p in range(2, alvo + 1):
        if not ir_pagina_direta(driver, p):
            log(f"Nao foi para pagina {p}", "ERR")


# ── MAIN ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Download PJe PUSH (perfil isolado)")
    parser.add_argument("--pagina", type=int, default=1)
    parser.add_argument("--limite", type=int, default=0)
    parser.add_argument("--download-dir", type=str, default=str(DEFAULT_DOWNLOAD_DIR))
    parser.add_argument("--retry", action="store_true", help="Retenta apenas processos com erro do ultimo relatorio")
    parser.add_argument("--excluir-comarca", nargs="+", default=[], help="Codigos de comarca a excluir (4 digitos finais do CNJ). Ex: --excluir-comarca 0396")
    parser.add_argument("--ordem-comarca", type=str, default=",".join(ORDEM_COMARCA_DEFAULT),
                        help="Codigos de comarca em ordem de prioridade, separados por virgula. Default: 0680,0627,0105,0396 (Taiobeiras, Rio Pardo, GV, Mantena)")
    parser.add_argument("--telegram", action="store_true", help="Envia notificacoes no Telegram a cada 10 OK confirmados")
    parser.add_argument("--telegram-primeiros", type=int, default=0, help="Envia Telegram quando atingir N processos OK nesta execucao")
    parser.add_argument("--ignorar-janela", action="store_true", help="Ignora janela TJMG 13h-19h (indisponivel)")
    parser.add_argument("--sleep", type=int, default=SLEEP_ENTRE_PROCESSOS, help=f"Pausa entre processos em segundos (default {SLEEP_ENTRE_PROCESSOS})")
    args = parser.parse_args()

    ordem_comarca = [c.strip() for c in args.ordem_comarca.split(",") if c.strip()]

    dl_dir = Path(args.download_dir)
    dl_dir.mkdir(parents=True, exist_ok=True)

    # ★ Carregar índice de dedup persistente (fix 2026-04-19: loop infinito)
    _carregar_dedup_index(dl_dir)
    log(f"Indice dedup: {len(_DEDUP_INDEX)} CNJs ja baixados", "OK")
    rprint(f"[cyan]Download PJe — {len(_DEDUP_INDEX)} já baixados previamente[/cyan]")

    # ── JANELA TJMG (13h-19h indisponivel) ──
    if _VERIF_OK and not args.ignorar_janela:
        disp, msg_janela = janela_disponivel()
        if not disp:
            log(msg_janela, "WAIT")
            if args.telegram:
                notificar_telegram(f"⏸ PJe aguardando janela TJMG: {msg_janela}", silent=True, log_fn=log)
            esperar_janela_liberar(log_fn=lambda m: log(m, "WAIT"))
            log("Janela liberada — iniciando.", "OK")

    # ── MODO RETRY: le ultimo relatorio, filtra so os que falharam ──
    retry_cnjs = None
    if args.retry:
        import glob
        relatorios = sorted(glob.glob(str(dl_dir / "relatorio-*.json")))
        if not relatorios:
            print("Nenhum relatorio encontrado para retry.")
            return
        with open(relatorios[-1], encoding="utf-8") as f:
            ultimo = json.load(f)
        retry_cnjs = [
            p["numero"] for p in ultimo.get("processos", [])
            if p.get("status") not in ("ok", "ja-baixado", "ja-baixado-idx", "ja-baixado-sessao")
        ]
        if not retry_cnjs:
            print("Nenhum processo com erro no ultimo relatorio. Nada a retentar.")
            return
        print(f"  RETRY: {len(retry_cnjs)} processos com erro no ultimo relatorio")
        for c in retry_cnjs:
            print(f"    - {c}")
        print()

    print("=" * 60)
    print("  PJe PUSH - Download Automatico (v2 isolado)")
    print("  Perito Jesus Penna - TJMG")
    print("=" * 60)
    print(f"  Destino:  {dl_dir}")
    print(f"  Perfil:   {AUTOMATION_PROFILE}")
    print(f"  Pagina:   {args.pagina}")
    print(f"  Limite:   {'todos' if args.limite == 0 else args.limite}")
    if args.excluir_comarca:
        print(f"  Excluir:  comarcas {', '.join(args.excluir_comarca)}")
    if retry_cnjs:
        print(f"  Modo:     RETRY ({len(retry_cnjs)} processos)")
    print("=" * 60)
    print()

    report = {
        "inicio": datetime.now().isoformat(),
        "config": {
            "download_dir": str(dl_dir),
            "perfil": str(AUTOMATION_PROFILE),
            "limite": args.limite,
            "pagina_inicial": args.pagina,
            "retry": args.retry,
        },
        "processos": [],
    }

    driver = criar_browser(dl_dir)

    try:
        # 1. Login
        driver.get(PJE_LOGIN)
        time.sleep(3)

        logged = False
        if "painel_usuario" in driver.current_url or "Quadro" in driver.title:
            log("Ja logado (sessao anterior)!", "OK")
            logged = True
        else:
            try:
                src = driver.page_source
                if "Jesus Penna" in src or "Painel do Advogado" in src:
                    log("Ja logado!", "OK")
                    logged = True
            except Exception:
                pass

        if not logged:
            logged = esperar_login(driver)

        if not logged:
            log("Login falhou. Encerrando.", "ERR")
            return

        # 2. Navegar para PUSH
        if not navegar_para_push(driver):
            return

        if args.pagina > 1:
            ir_pagina(driver, args.pagina)

        # 3. Detectar total de paginas e PDFs ja baixados
        total_paginas = detectar_total_paginas(driver)

        ja_baixados = set()
        for f in os.listdir(str(dl_dir)):
            if f.endswith(".pdf") and not f.startswith("relatorio"):
                ja_baixados.add(f)
        if ja_baixados:
            log(f"{len(ja_baixados)} PDFs ja existem em {dl_dir}", "OK")

        # Notificacao de inicio
        if args.telegram and _VERIF_OK:
            notificar_telegram(
                f"🚀 PJe download iniciado\n"
                f"Pasta: <code>{dl_dir}</code>\n"
                f"Ordem: {' → '.join(ordem_comarca)}\n"
                f"Paginas: {total_paginas} | Limite: {'todos' if args.limite == 0 else args.limite}",
                log_fn=log,
            )

        # 4. Loop de download
        pag = args.pagina
        total_ok = 0
        total_ok_conferido = 0  # OK com conteudo verificado pag 1
        total_err = 0
        total_invalidos = 0
        cnjs_processados = set()  # Evita reprocessar CNJs apos volta ao PUSH

        while True:
            print(f"\n{'=' * 50}")
            log(f"PAGINA {pag} de {total_paginas}")
            print(f"{'=' * 50}")

            procs = extrair_processos(driver)

            # Ordenar por comarca (prioridade: Taiobeiras, Rio Pardo, GV, Mantena)
            if _VERIF_OK and procs and ordem_comarca:
                procs = ordenar_por_comarca(procs, ordem_comarca)

            if not procs:
                # Verificar se e sessao expirada ou realmente sem processos
                if not sessao_ativa(driver):
                    log("Tabela vazia — sessao expirou!", "WAIT")
                    if relogar(driver) and navegar_para_push(driver):
                        log("Re-logado! Reextraindo...", "OK")
                        if pag > 1:
                            ir_pagina_direta(driver, pag)
                        continue  # Volta ao while sem avancar pagina
                    else:
                        log("Re-login falhou. Encerrando.", "ERR")
                        break
                # Pagina vazia NAO significa fim — pode ser problema de carregamento
                if pag < total_paginas:
                    log(f"Pagina {pag} vazia, mas ainda ha {total_paginas} paginas. Tentando proxima...", "WAIT")
                else:
                    log("Nenhum processo nesta pagina. Fim.", "OK")
                    break

            # Em modo retry, filtrar so os CNJs que falharam
            if retry_cnjs is not None:
                procs = [p for p in procs if p["numero"] in retry_cnjs]
                if not procs:
                    log(f"Nenhum CNJ de retry nesta pagina, avancando...")

            # Filtrar comarcas excluidas (4 digitos finais do CNJ)
            if args.excluir_comarca:
                antes = len(procs)
                procs = [p for p in procs if p["numero"][-4:] not in args.excluir_comarca]
                excluidos = antes - len(procs)
                if excluidos:
                    log(f"{excluidos} processos excluidos por comarca", "INFO")

            for proc in tqdm(procs, desc=f"Pag {pag}/{total_paginas}", unit="proc"):
                if 0 < args.limite <= total_ok:
                    log(f"Limite {args.limite} atingido!", "OK")
                    break

                # Checar sessao antes de cada processo
                if not sessao_ativa(driver):
                    if not relogar(driver):
                        log("Re-login falhou. Encerrando.", "ERR")
                        break
                    if not navegar_para_push(driver):
                        log("Falha ao voltar para PUSH apos re-login.", "ERR")
                        break
                    if pag > 1:
                        ir_pagina_direta(driver, pag)
                    # Pular para proximo ciclo — tabela foi recarregada
                    log("Sessao restaurada! Reextraindo processos...", "OK")
                    break  # Sai do for, volta ao while que re-extrai

                # Skip se ja processado nesta execucao (evita loop infinito)
                if proc["numero"] in cnjs_processados:
                    continue

                print(f"\n  --- [{total_ok + total_err + 1}] ---")
                cnjs_processados.add(proc["numero"])
                r = baixar_processo(driver, proc["index"], proc["numero"], dl_dir)
                report["processos"].append(r)

                if r["status"] in ("ok", "ja-baixado", "ja-baixado-idx", "ja-baixado-sessao"):
                    total_ok += 1
                    if args.telegram and _VERIF_OK and args.telegram_primeiros and total_ok == args.telegram_primeiros:
                        notificar_telegram(
                            f"✅ PJe: {total_ok} primeiros processos OK\n"
                            f"Último: <code>{proc['numero']}</code>\n"
                            f"Pasta: <code>{dl_dir}</code>\n"
                            f"Continuando execução.",
                            log_fn=log,
                        )
                    # conferido=True = verificacao pag 1 bate com esperado
                    if r.get("conferido"):
                        total_ok_conferido += 1

                        # Telegram: a cada NOTIFICAR_A_CADA confirmados
                        if args.telegram and _VERIF_OK and total_ok_conferido % NOTIFICAR_A_CADA == 0:
                            last_cnj = r.get("numero") or proc["numero"]
                            last_com = r.get("comarca") or "?"
                            notificar_telegram(
                                f"✅ {total_ok_conferido} baixados e conferidos\n"
                                f"Último: <code>{last_cnj}</code> ({last_com})\n"
                                f"Pasta: {total_ok} OK | {total_invalidos} inválidos | {total_err} erros",
                                silent=True, log_fn=log,
                            )

                        # Pausa longa a cada PAUSA_LONGA_A_CADA confirmados
                        if total_ok_conferido > 0 and total_ok_conferido % PAUSA_LONGA_A_CADA == 0:
                            log(f"Pausa longa ({SLEEP_PAUSA_LONGA}s) apos {total_ok_conferido} OK confirmados", "WAIT")
                            time.sleep(SLEEP_PAUSA_LONGA)

                    # Pausa curta entre processos
                    time.sleep(max(1, args.sleep))
                elif r.get("status") == "conteudo-divergente":
                    total_invalidos += 1
                    if args.telegram and _VERIF_OK and total_invalidos % 5 == 0:
                        notificar_telegram(
                            f"⚠️ {total_invalidos} PDFs com conteúdo divergente (quarentena _invalidos/)\n"
                            f"Último: <code>{proc['numero']}</code>",
                            silent=True, log_fn=log,
                        )
                    # Pausa curta tambem
                    time.sleep(max(1, args.sleep))
                else:
                    total_err += 1
                    # Se 5 erros consecutivos, checar sessao
                    recent = report["processos"][-5:]
                    if len(recent) >= 5 and all(p["status"] == "erro" for p in recent):
                        log("5 erros consecutivos — verificando sessao...", "WAIT")
                        if not sessao_ativa(driver):
                            if not relogar(driver):
                                log("Re-login falhou. Encerrando.", "ERR")
                                break
                            if not navegar_para_push(driver):
                                break
                            if pag > 1:
                                ir_pagina_direta(driver, pag)
                            log("Sessao restaurada!", "OK")
                            break

            if 0 < args.limite <= total_ok:
                break

            # Avancar pagina — click direto no numero, depois »
            avancou = proxima_pagina(driver, pag)
            if not avancou and pag < total_paginas:
                log(f"proxima_pagina falhou, tentando ir direto para pagina {pag + 1}...", "WAIT")
                avancou = ir_pagina_direta(driver, pag + 1)
            if not avancou:
                if pag >= total_paginas:
                    log(f"Todas as {total_paginas} paginas processadas. Fim!", "OK")
                else:
                    log(f"Nao conseguiu avancar alem da pagina {pag}.", "ERR")
                break
            pag += 1

        # 4. Relatorio
        report["fim"] = datetime.now().isoformat()
        report["baixados"] = total_ok
        report["conferidos"] = total_ok_conferido
        report["invalidos"] = total_invalidos
        report["erros"] = total_err
        report["log"] = _log_entries

        rpath = dl_dir / f"relatorio-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(rpath, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n{'=' * 60}")
        print(f"  CONCLUIDO!")
        print(f"  Baixados: {total_ok} | Conferidos: {total_ok_conferido}")
        print(f"  Invalidos: {total_invalidos} | Erros: {total_err}")
        print(f"  Pasta:    {dl_dir}")
        print(f"  Relatorio: {rpath}")
        print(f"{'=' * 60}")

        # Notificacao final
        if args.telegram and _VERIF_OK:
            notificar_telegram(
                f"🏁 PJe download CONCLUÍDO\n"
                f"Total baixados: {total_ok}\n"
                f"Conferidos (CNJ pag 1 OK): {total_ok_conferido}\n"
                f"Inválidos (quarentena): {total_invalidos}\n"
                f"Erros: {total_err}\n"
                f"Relatório: <code>{rpath.name}</code>",
                log_fn=log,
            )

        # NAO fecha o navegador
        print("\n  Chrome permanece aberto para inspecao.")

    except Exception as e:
        log(f"Erro fatal: {e}", "ERR", erro=str(e))
        rprint(f"[red]Erro fatal no download: {e}[/red]")

    # Salvar relatorio mesmo em caso de erro
    report["fim"] = datetime.now().isoformat()
    report["log"] = _log_entries
    try:
        rpath = dl_dir / f"relatorio-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(rpath, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        _ok = report.get("baixados", 0)
        _er = report.get("erros", 0)
        if _er:
            rprint(f"[yellow]Download finalizado — {_ok} OK, {_er} erros[/yellow]")
        else:
            rprint(f"[green]Download finalizado — {_ok} OK[/green]")
    except Exception:
        pass


if __name__ == "__main__":
    main()
