#!/usr/bin/env python3
"""
Utilitários compartilhados — PJe TJMG no Mac (Chrome Selenium)
Extraídos e adaptados de baixar_direto_selenium.py (Windows).

Diferença crítica:
  - Mac usa porta 9223 (perfil isolado, sem cert A3)
  - Windows usa porta 9222 (Chrome com VidaaS A3)
  - Login manual no Chrome (não no Safari)

ref: SE-001, SE-002, SE-003, SE-007, SE-009, SE-011
"""

import re
import time
import unicodedata
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("ERRO: pip install selenium")
    import sys; sys.exit(1)

# ============================================================
# CONFIG
# ============================================================

PJE_BASE      = "https://pje.tjmg.jus.br/pje"
PAINEL_URL    = f"{PJE_BASE}/Painel/painel_usuario/advogado.seam"
PUSH_URL      = f"{PJE_BASE}/Push/listView.seam"

# Mac: porta 9223. Windows: 9222 (não usar aqui)
PORTAS_DEBUG_MAC = [9223, 9224]
CDP_TIMEOUT      = 3
LOCK_FILES       = ["SingletonLock", "SingletonSocket", "SingletonCookie"]

# Perfil isolado — não toca no Chrome do usuário (ref: SE-007)
AUTOMATION_PROFILE = Path.home() / "stemmia-forense" / "tools" / "chrome-cdp-profile"

# Regex CNJ padrão nacional
PUSH_CNJ_RE = re.compile(r'(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})')

# Mapa foro → comarca (mesmo do baixar_direto_selenium.py)
COMARCAS = {
    "0005": "Acucena",
    "0024": "Belo Horizonte",
    "0042": "Arcos",
    "0059": "Barroso",
    "0089": "Bracopolis",
    "0105": "Governador Valadares",
    "0112": "Campo Belo",
    "0134": "Governador Valadares",
    "0184": "Conselheiro Pena",
    "0194": "Coronel Fabriciano",
    "0231": "Ribeirao das Neves",
    "0245": "Santa Luzia",
    "0309": "Ibiapim",
    "0329": "Itamogi",
    "0344": "Ituiutaba",
    "0362": "Joao Monlevade",
    "0396": "Mantena",
    "0471": "Para de Minas",
    "0627": "Taiobeiras",
    "0674": "Bom Despacho",
    "0680": "Taiobeiras",
    "0694": "Tres Pontas",
    "0701": "Uberaba",
    "0702": "Uberlandia",
}

# ============================================================
# LOG
# ============================================================

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "i", "OK": "+", "ERRO": "X", "AVISO": "!", "PROG": ">"}.get(level, ".")
    print(f"  [{ts}] {prefix} {msg}", flush=True)

# ============================================================
# CONEXÃO CHROME — Mac (porta 9223)
# ref: SE-007, SE-001
# ============================================================

def _cdp_vivo(host, porta):
    try:
        req = urllib.request.urlopen(f"http://{host}:{porta}/json/version", timeout=CDP_TIMEOUT)
        return "Browser" in req.read().decode("utf-8", errors="ignore")
    except Exception:
        return False


def conectar_chrome():
    """
    1) Tenta reusar Chrome com debug port 9223/9224 (Mac).
    2) Se não tiver, abre Chrome novo em perfil isolado + porta 9223.

    NÃO usa porta 9222 (Windows/Parallels).
    NÃO mexe no Chrome nem Safari do usuário.
    ref: SE-001, SE-007
    """
    # Tenta reusar sessão existente
    for host in ("127.0.0.1", "localhost"):
        for porta in PORTAS_DEBUG_MAC:
            if _cdp_vivo(host, porta):
                log(f"Chrome debug ativo em {host}:{porta} — reusando sessão", "OK")
                opts = Options()
                opts.debugger_address = f"{host}:{porta}"
                driver = webdriver.Chrome(options=opts)
                driver.implicitly_wait(5)
                return driver

    # Abre Chrome novo em perfil isolado
    log("Nenhum CDP respondeu — abrindo Chrome em perfil dedicado (Mac)...")
    AUTOMATION_PROFILE.mkdir(parents=True, exist_ok=True)
    for lf in LOCK_FILES:
        p = AUTOMATION_PROFILE / lf
        try:
            if p.exists():
                p.unlink()
        except Exception:
            pass

    opts = Options()
    opts.add_argument(f"--user-data-dir={AUTOMATION_PROFILE}")
    opts.add_argument("--profile-directory=Default")
    opts.add_argument("--remote-debugging-port=9223")
    opts.add_argument("--start-maximized")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--disable-session-crashed-bubble")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)
    # Aceita alerts automáticamente (PJe spamma "Ocorreu um erro tente novamente")
    opts.set_capability("unhandledPromptBehavior", "accept")

    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(5)
    log("Chrome aberto em perfil dedicado (Mac)", "OK")

    try:
        driver.get("https://pje.tjmg.jus.br")
    except Exception:
        pass
    for _ in range(3):
        try:
            alerta = driver.switch_to.alert
            log(f"Alert dismissado: {alerta.text[:80]}", "AVISO")
            alerta.accept()
            time.sleep(1)
        except Exception:
            break
    return driver

# ============================================================
# ALERTS — crítico para PJe JSF/RichFaces
# ============================================================

def dismiss_alerts_loop(driver, max_iter=8, sleep_between=0.3):
    """
    Aceita TODOS os alerts pendentes em loop.
    PJe dispara alerts JavaScript aleatórios (CNJ 121, sessão expirada, etc).
    ref: SE-003
    """
    aceitos = 0
    for _ in range(max_iter):
        try:
            alerta = driver.switch_to.alert
            texto = (alerta.text or "")[:100].replace("\n", " ")
            alerta.accept()
            aceitos += 1
            log(f"Alert aceito: {texto}", "AVISO")
            time.sleep(sleep_between)
        except Exception:
            break
    return aceitos

# ============================================================
# HELPERS DE ELEMENTO
# ref: SE-002, SE-003, SE-009
# ============================================================

def find_element_multi(driver, seletores, timeout=5):
    """
    Tenta múltiplos seletores CSS/XPath. Retorna primeiro encontrado.
    Tolerante a is_displayed quebrado (jQuery antigo do PJe).
    ref: SE-009
    """
    for seletor in seletores:
        try:
            if seletor.startswith("//"):
                elems = driver.find_elements(By.XPATH, seletor)
            else:
                elems = driver.find_elements(By.CSS_SELECTOR, seletor)
            for elem in elems:
                try:
                    if elem.is_displayed():
                        return elem
                except Exception:
                    return elem  # jQuery PJe quebra is_displayed — aceita mesmo assim
        except Exception:
            continue
    return None


def find_element_multi_com_alert(driver, seletores, timeout=10):
    """find_element_multi + dismiss de alerts em loop. ref: SE-002, SE-003"""
    fim = time.time() + timeout
    while time.time() < fim:
        dismiss_alerts_loop(driver, max_iter=3, sleep_between=0.2)
        elem = find_element_multi(driver, seletores, timeout=1)
        if elem:
            return elem
        time.sleep(0.5)
    return None


def wait_element(driver, by, value, timeout=10):
    """Espera elemento ficar visível. ref: SE-002"""
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )
    except Exception:
        return None

# ============================================================
# SESSÃO / AUTENTICAÇÃO
# ============================================================

def is_authenticated(driver):
    """True se está em pje.tjmg.jus.br e não na tela de login SSO."""
    try:
        url = driver.current_url.lower()
        if "pje.tjmg.jus.br" not in url:
            return False
        if "sso.cloud.pje.jus.br" in url or "cas/login" in url:
            return False
        return True
    except Exception:
        return False


def page_requires_login(driver):
    try:
        url = driver.current_url.lower()
        return "sso.cloud.pje.jus.br" in url or "cas/login" in url
    except Exception:
        return True


def verificar_sessao(driver):
    try:
        return is_authenticated(driver) and not page_requires_login(driver)
    except Exception:
        return False


def wait_for_login(driver, timeout_min=6):
    """Poll passivo aguardando login manual. Não clica nada."""
    print()
    print("  " + "=" * 60)
    print("  FAÇA LOGIN NO PJe NO CHROME (não no Safari):")
    print(f"  {PAINEL_URL}")
    print()
    print("  O script detecta automaticamente quando você logar.")
    print("  " + "=" * 60)
    print()
    for _ in range(timeout_min * 20):  # 3s por tentativa
        try:
            if is_authenticated(driver):
                log("Login detectado!", "OK")
                return True
        except Exception:
            pass
        time.sleep(3)
    log(f"Timeout aguardando login ({timeout_min} min)", "ERRO")
    return False

# ============================================================
# PUSH — extrair CNJs paginados
# (copiado de baixar_direto_selenium.py — validado em produção)
# ============================================================

def extrair_cnjs_pagina_push(driver):
    """Retorna lista de CNJs na página atual da tabela PUSH."""
    try:
        cnjs = driver.execute_script("""
            const out = [];
            document.querySelectorAll('table[id*="dataTableProcessosCadastrados"] tbody tr').forEach(tr => {
                const cells = tr.querySelectorAll('td');
                if (cells.length >= 2) {
                    const t = (cells[1].innerText || '').trim();
                    const m = t.match(/\\d{7}-\\d{2}\\.\\d{4}\\.\\d\\.\\d{2}\\.\\d{4}/);
                    if (m) out.push(m[0]);
                }
            });
            return out;
        """)
        return cnjs or []
    except Exception as e:
        log(f"Erro extraindo CNJs: {e}", "ERRO")
        return []


def proxima_pagina_push(driver):
    """Clica na página atual+1 do datascroller RichFaces. True se avançou."""
    try:
        result = driver.execute_script("""
            const ds = document.querySelector(
                'div[id*="scrollerListaProcessosCadastrados"], div.rich-datascr'
            );
            if (!ds) return {ok: false};
            const act = ds.querySelector('td.rich-datascr-act');
            if (!act) return {ok: false};
            const current = parseInt((act.innerText||'').trim());
            if (isNaN(current)) return {ok: false};
            const next = current + 1;
            const inacts = ds.querySelectorAll('td.rich-datascr-inact');
            for (const td of inacts) {
                const n = parseInt((td.innerText||'').trim());
                if (n === next) { td.click(); return {ok: true}; }
            }
            return {ok: false, at_end: true};
        """)
        if result and result.get("ok"):
            time.sleep(3)
            return True
        return False
    except Exception as e:
        log(f"Erro próxima página: {e}", "ERRO")
        return False


def coletar_push_completo(driver, max_paginas=60):
    """Percorre todas as páginas da PUSH. Retorna {cnj: pagina_idx} (1-based)."""
    log("Coletando mapa da aba PUSH...")
    driver.get(PUSH_URL)
    time.sleep(4)
    dismiss_alerts_loop(driver, max_iter=3, sleep_between=0.3)

    mapa = {}
    pag = 1
    while pag <= max_paginas:
        cnjs = extrair_cnjs_pagina_push(driver)
        novos = sum(1 for c in cnjs if c not in mapa)
        for c in cnjs:
            if c not in mapa:
                mapa[c] = pag
        log(f"  Página {pag}: {len(cnjs)} CNJs ({novos} novos, total {len(mapa)})")
        if not cnjs:
            break
        if not proxima_pagina_push(driver):
            break
        pag += 1
    log(f"PUSH mapeada: {len(mapa)} processos em {pag} páginas", "OK")
    return mapa

# ============================================================
# NORMALIZAÇÃO CNJ
# ============================================================

def normalizar_cnj(cnj: str) -> str:
    """Remove espaços, garante formato NNNNNNN-DD.AAAA.J.TT.OOOO."""
    cnj = cnj.strip()
    # Remove caracteres fora do padrão
    match = PUSH_CNJ_RE.search(cnj)
    return match.group(1) if match else cnj


def extrair_cnjs_do_texto(texto: str) -> list[str]:
    """Extrai todos os CNJs de um bloco de texto (page_source, innerText)."""
    return list(set(PUSH_CNJ_RE.findall(texto)))


def get_comarca(cnj: str) -> str:
    foro = cnj[-4:] if len(cnj) >= 4 else "????"
    return COMARCAS.get(foro, f"Foro {foro}")
