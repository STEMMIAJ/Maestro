#!/usr/bin/env python3
"""
DOWNLOAD DIRETO — 157 processos PJe TJMG (SELENIUM)
Roda NO WINDOWS. Sem greenlet. Sem Playwright. Funciona em ARM64.

  1. pip install selenium webdriver-manager
  2. python baixar_direto_selenium.py

Flags:
  --teste          Baixa so 1 processo (para validar)
  --sem-retomar    Forca re-download de tudo
  --so-comarca X   Baixa so processos da comarca X
  --listar         Mostra lista ordenada sem baixar
  --retries N      Tentativas por processo (default: 3)
"""

import argparse
import glob as glob_mod
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("ERRO: Selenium nao instalado. Rode:")
    print("  pip install selenium webdriver-manager")
    sys.exit(1)

# pypdf para extrair vara do PDF baixado (herda logica do espelho antigo)
try:
    import pypdf
    PYPDF_OK = True
except ImportError:
    PYPDF_OK = False
    print("AVISO: pypdf ausente — extracao de vara desabilitada")
    print("  Recomendado: pip install pypdf")

# ============================================================
# CONFIGURACAO
# ============================================================

PJE_BASE = "https://pje.tjmg.jus.br/pje"
PAINEL_URL = f"{PJE_BASE}/Painel/painel_usuario/advogado.seam"
CONSULTA_URL = f"{PJE_BASE}/Processo/ConsultaProcesso/listView.seam"
PUSH_URL = f"{PJE_BASE}/Push/listView.seam"
DOWNLOAD_TIMEOUT = 600  # 10 min (em segundos)
MAX_RETRIES = 3
TIMEOUT_PROCESSO = 300  # hard timeout por CNJ
IFRAME_TIMEOUT = 15
CDP_TIMEOUT = 3
PORTAS_DEBUG = [9222, 9223]
LOCK_FILES = ["SingletonLock", "SingletonSocket", "SingletonCookie"]

# Perfil DEDICADO (nao mexe no Chrome do usuario) - resolve DevToolsActivePort no ARM64
AUTOMATION_PROFILE = Path.home() / "Desktop" / "chrome-pje-profile"

# STAGING local — Chrome baixa aqui (NUNCA direto em UNC, corrompe. ref PJE-015, PJE-025)
PASTA_STAGING = Path.home() / "Desktop" / "processos-pje" / "downloads"
PASTA_SAIDA = PASTA_STAGING  # alias compat

# FINAL — pasta compartilhada Mac via Parallels Shared Folders (UNC)
# \\psf\Home\* mapeia /Users/jesus/* do Mac (host)
PASTA_FINAL = Path(r"\\psf\Home\Desktop\STEMMIA Dexter\Processos Atualizados")

# Pasta temp interna do Chrome (subpasta de STAGING)
DOWNLOAD_TEMP = Path.home() / "Desktop" / "processos-pje" / "_chrome_downloads"

PROGRESSO_FILE = PASTA_STAGING / "_progresso_lote.json"
LOG_FILE = PASTA_STAGING / "_log_download.txt"
CONTROLE_ESPELHO = PASTA_FINAL / "_controle_espelho.json"

# Telegram
_token_paths = [
    Path("Z:/Desktop/ANALISADOR FINAL/scripts/.telegram-token"),
    Path.home() / "Desktop" / "ANALISADOR FINAL" / "scripts" / ".telegram-token",
]
TELEGRAM_CHAT_ID = "8397602236"

# Chrome user data (perfil real com certificado digital)
CHROME_USER_DATA = str(Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data")

# ============================================================
# MAPEAMENTO FORO -> COMARCA
# ============================================================

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

PRIORIDADE = {
    "Taiobeiras": 1,
    "Governador Valadares": 2,
    "Mantena": 3,
    "Conselheiro Pena": 4,
}

# ============================================================
# 157 CNJs — LISTA REAL (20/abr/2026)
# ============================================================

PROCESSOS = [
    # --- Taiobeiras (24) --- prioridade 1
    "5000038-13.2025.8.13.0680",
    "5000154-81.2025.8.13.0627",
    "5000416-08.2021.8.13.0680",
    "5000510-14.2025.8.13.0680",
    "5000792-52.2025.8.13.0680",
    "5001309-57.2025.8.13.0680",
    "5001543-78.2021.8.13.0680",
    "5001565-97.2025.8.13.0680",
    "5001566-19.2024.8.13.0680",
    "5001994-69.2022.8.13.0680",
    "5002175-65.2025.8.13.0680",
    "5002387-57.2023.8.13.0680",
    "5002406-92.2025.8.13.0680",
    "5002670-46.2024.8.13.0680",
    "5003080-41.2023.8.13.0680",
    "5003293-13.2024.8.13.0680",
    "5003575-85.2023.8.13.0680",
    "5003685-50.2024.8.13.0680",
    "5003799-23.2023.8.13.0680",
    "5003880-69.2023.8.13.0680",
    "5004052-40.2025.8.13.0680",
    "5004205-10.2024.8.13.0680",
    "5004301-88.2025.8.13.0680",
    "5004594-92.2024.8.13.0680",
    # --- Governador Valadares (32) --- prioridade 2
    "0443639-15.2018.8.13.0105",
    "0607708-35.2016.8.13.0105",
    "1000435-22.2025.8.13.0105",
    "5001140-30.2017.8.13.0105",
    "5004172-72.2019.8.13.0105",
    "5005267-30.2025.8.13.0105",
    "5007127-08.2021.8.13.0105",
    "5007830-31.2024.8.13.0105",
    "5008297-73.2025.8.13.0105",
    "5008504-19.2018.8.13.0105",
    "5008789-02.2024.8.13.0105",
    "5009261-08.2021.8.13.0105",
    "5011001-35.2020.8.13.0105",
    "5013218-75.2025.8.13.0105",
    "5014017-55.2024.8.13.0105",
    "5015391-72.2025.8.13.0105",
    "5016366-70.2020.8.13.0105",
    "5017700-42.2020.8.13.0105",
    "5018356-57.2024.8.13.0105",
    "5018431-96.2024.8.13.0105",
    "5022119-66.2024.8.13.0105",
    "5022941-21.2025.8.13.0105",
    "5022952-60.2019.8.13.0105",
    "5024581-59.2025.8.13.0105",
    "5027170-29.2022.8.13.0105",
    "5028174-33.2024.8.13.0105",
    "5030880-86.2024.8.13.0105",
    "5031069-64.2024.8.13.0105",
    "5034347-39.2025.8.13.0105",
    "5035510-54.2025.8.13.0105",
    "5035541-11.2024.8.13.0105",
    "5039279-07.2024.8.13.0105",
    # --- Mantena (68) --- prioridade 3
    "0022707-76.2015.8.13.0396",
    "0038122-07.2012.8.13.0396",
    "0056651-98.2017.8.13.0396",
    "0057334-43.2014.8.13.0396",
    "0102935-58.2003.8.13.0396",
    "5000029-93.2026.8.13.0396",
    "5000162-72.2025.8.13.0396",
    "5000232-55.2026.8.13.0396",
    "5000237-19.2022.8.13.0396",
    "5000247-58.2025.8.13.0396",
    "5000447-65.2025.8.13.0396",
    "5000691-57.2026.8.13.0396",
    "5000692-76.2025.8.13.0396",
    "5000914-44.2025.8.13.0396",
    "5000920-17.2026.8.13.0396",
    "5000926-24.2026.8.13.0396",
    "5000966-40.2025.8.13.0396",
    "5001473-64.2026.8.13.0396",
    "5001486-97.2025.8.13.0396",
    "5001604-73.2025.8.13.0396",
    "5001606-43.2025.8.13.0396",
    "5001625-49.2025.8.13.0396",
    "5001634-11.2025.8.13.0396",
    "5001662-13.2024.8.13.0396",
    "5001797-88.2025.8.13.0396",
    "5002156-38.2025.8.13.0396",
    "5002188-43.2025.8.13.0396",
    "5002205-16.2024.8.13.0396",
    "5002388-50.2025.8.13.0396",
    "5002392-87.2025.8.13.0396",
    "5002456-97.2025.8.13.0396",
    "5002587-72.2025.8.13.0396",
    "5002637-35.2024.8.13.0396",
    "5002785-22.2019.8.13.0396",
    "5002966-13.2025.8.13.0396",
    "5002973-39.2024.8.13.0396",
    "5003064-32.2024.8.13.0396",
    "5003087-41.2025.8.13.0396",
    "5003154-06.2025.8.13.0396",
    "5003178-68.2024.8.13.0396",
    "5003213-91.2025.8.13.0396",
    "5003247-66.2025.8.13.0396",
    "5003351-58.2025.8.13.0396",
    "5003396-62.2025.8.13.0396",
    "5003403-88.2024.8.13.0396",
    "5003730-96.2025.8.13.0396",
    "5003806-23.2025.8.13.0396",
    "5003853-94.2025.8.13.0396",
    "5003873-85.2025.8.13.0396",
    "5003935-62.2024.8.13.0396",
    "5003988-09.2025.8.13.0396",
    "5003994-50.2024.8.13.0396",
    "5004027-06.2025.8.13.0396",
    "5004041-87.2025.8.13.0396",
    "5004143-12.2025.8.13.0396",
    "5004251-41.2025.8.13.0396",
    "5004266-44.2024.8.13.0396",
    "5004401-56.2024.8.13.0396",
    "5004407-29.2025.8.13.0396",
    "5004580-53.2025.8.13.0396",
    "5004692-22.2025.8.13.0396",
    "5004725-12.2025.8.13.0396",
    "5004737-26.2025.8.13.0396",
    "5004786-67.2025.8.13.0396",
    "5004952-02.2025.8.13.0396",
    "5005249-09.2025.8.13.0396",
    "5005297-65.2025.8.13.0396",
    "5005376-49.2022.8.13.0396",
    # --- Conselheiro Pena (8) --- prioridade 4
    "5000047-81.2020.8.13.0184",
    "5000048-32.2021.8.13.0184",
    "5000412-28.2026.8.13.0184",
    "5000506-10.2025.8.13.0184",
    "5001702-49.2024.8.13.0184",
    "5001710-89.2025.8.13.0184",
    "5002831-26.2023.8.13.0184",
    "5003107-57.2023.8.13.0184",
    # --- Outras comarcas (25) --- prioridade 5
    "0012022-56.2012.8.13.0059",
    "0159720-82.2003.8.13.0188",
    "5000162-62.2026.8.13.0194",
    "5000162-82.2022.8.13.0362",
    "5000181-85.2025.8.13.0329",
    "5000628-46.2019.8.13.0309",
    "5001356-58.2025.8.13.0089",
    "5001360-54.2025.8.13.0329",
    "5001615-98.2025.8.13.0074",
    "5001875-14.2024.8.13.0042",
    "5002424-62.2025.8.13.0309",
    "5002526-60.2024.8.13.0005",
    "5003133-79.2021.8.13.0231",
    "5004032-07.2025.8.13.0694",
    "5004462-81.2024.8.13.0309",
    "5004860-37.2024.8.13.0112",
    "5004904-79.2017.8.13.0313",
    "5005009-79.2025.8.13.0344",
    "5005547-25.2025.8.13.0194",
    "5007409-48.2020.8.13.0245",
    "5010234-65.2024.8.13.0134",
    "5011972-13.2025.8.13.0471",
    "5016125-49.2023.8.13.0701",
    "5065815-44.2023.8.13.0702",
    "5202056-90.2021.8.13.0024",
]


# ============================================================
# FUNCOES AUXILIARES
# ============================================================

def get_comarca(cnj):
    foro = cnj[-4:]
    return COMARCAS.get(foro, f"Foro {foro}")

def get_prioridade(comarca):
    return PRIORIDADE.get(comarca, 5)

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "i", "OK": "+", "ERRO": "X", "AVISO": "!", "PROG": ">"}.get(level, ".")
    line = f"  [{ts}] {prefix} {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def sanitize_folder(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()


# ============================================================
# EXTRACAO DE VARA + VALIDACAO + MOVE PRA PASTA FINAL
# ============================================================

def sanitize_vara_curta(vara_longa):
    """'3ª Vara Civel da Comarca de GV' -> '3ª Vara Cível'. Trata Única, Família, multi-especialidade."""
    if not vara_longa:
        return "_Sem_Vara"
    vara = re.split(r'\s+da\s+Comarca\s+de\s+', vara_longa, maxsplit=1)[0].strip()
    # Multi-especialidade: "Vara Cível, Criminal e de Execuções" -> "Vara Cível-Criminal"
    if "Criminal" in vara and ("Civel" in vara or "Cível" in vara):
        vara = re.sub(r'(C[ií]vel),?\s+Criminal.*', r'\1-Criminal', vara)
    # "Vara de Família, Sucessões e Ausência" -> "Vara de Família"
    if "Família" in vara or "Familia" in vara:
        vara = re.split(r',', vara)[0].strip()
    # Infância: preserva se aparecer depois do Cível
    if "Infância" in vara_longa and "Cível" in vara:
        if "-Infância" not in vara and "-Infancia" not in vara:
            vara = vara.split(",")[0].strip() + "-Infância"
    # Ref PJE-019: chars invalidos Windows
    vara = re.sub(r'[<>:"/\\|?*\r\n\t]', '_', vara).strip()
    return vara or "_Sem_Vara"


def extrair_vara_do_pdf(pdf_path, max_paginas=3):
    """Le primeiras paginas via pypdf, regex extrai vara LONGA. Retorna str ou None."""
    if not PYPDF_OK:
        return None
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        texto = ""
        for i in range(min(max_paginas, len(reader.pages))):
            try:
                texto += (reader.pages[i].extract_text() or "") + "\n"
            except Exception:
                continue
        if not texto:
            return None
        padroes = [
            r'(\d+ª\s+Vara\s+[^,\n\r]{2,120}?\s+da\s+Comarca\s+de\s+[^,\n\r]{2,80})',
            r'(Vara\s+Única\s+da\s+Comarca\s+de\s+[^,\n\r]{2,80})',
            r'(Vara\s+Unica\s+da\s+Comarca\s+de\s+[^,\n\r]{2,80})',
            r'(Vara\s+de\s+[^,\n\r]{2,120}?\s+da\s+Comarca\s+de\s+[^,\n\r]{2,80})',
        ]
        for pat in padroes:
            m = re.search(pat, texto, flags=re.IGNORECASE)
            if m:
                return re.sub(r'\s+', ' ', m.group(1).strip())
        return None
    except Exception as e:
        log(f"Erro extraindo vara: {e}", "AVISO")
        return None


def validar_cnj_no_pdf(pdf_path, cnj_esperado, max_paginas=3):
    """Valida CNJ presente no PDF. Ref PJE-007 (evita baixar processo errado)."""
    if not PYPDF_OK:
        return True  # sem pypdf, aceita sem validacao
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        for i in range(min(max_paginas, len(reader.pages))):
            try:
                t = reader.pages[i].extract_text() or ""
                if cnj_esperado in t:
                    return True
            except Exception:
                continue
        return False
    except Exception:
        return True


def pdf_ja_baixado_final(cnj):
    """Retorna Path do PDF se existe em qualquer subpasta de PASTA_FINAL, senao None."""
    try:
        if not PASTA_FINAL.exists():
            return None
        for pdf in PASTA_FINAL.rglob(f"*{cnj}*.pdf"):
            try:
                if pdf.stat().st_size > 10000:
                    return pdf
            except Exception:
                continue
    except Exception:
        pass
    return None


def atualizar_controle_espelho(destino, cnj, comarca, vara_longa, origem=""):
    """Atualiza _controle_espelho.json. Chave = SHA-256 ou fallback."""
    import hashlib
    try:
        CONTROLE_ESPELHO.parent.mkdir(parents=True, exist_ok=True)
        controle = {}
        if CONTROLE_ESPELHO.exists():
            try:
                controle = json.loads(CONTROLE_ESPELHO.read_text(encoding="utf-8"))
            except Exception:
                controle = {}
        try:
            if destino.stat().st_size < 50 * 1024 * 1024:
                sha = hashlib.sha256(destino.read_bytes()).hexdigest()
            else:
                sha = f"big_{cnj}_{destino.stat().st_size}"
        except Exception:
            sha = f"sem_sha_{cnj}_{int(time.time())}"
        controle[sha] = {
            "bytes": destino.stat().st_size,
            "cidade": comarca,
            "cnj": cnj,
            "copiado_em": datetime.now().isoformat(timespec="seconds"),
            "destino": str(destino),
            "origem": origem,
            "vara": vara_longa or "SEM VARA",
        }
        CONTROLE_ESPELHO.write_text(
            json.dumps(controle, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        log(f"Controle espelho falhou: {e}", "AVISO")


def mover_pra_final(pdf_staging, cnj):
    """Extrai vara, valida CNJ, move pra PASTA_FINAL/Comarca/VaraCurta/. Retorna Path ou None."""
    import shutil
    comarca = get_comarca(cnj)

    # PJE-007: valida CNJ no PDF
    if not validar_cnj_no_pdf(pdf_staging, cnj):
        log(f"CNJ {cnj} NAO consta no PDF — PDF de processo errado?", "ERRO")
        return None

    vara_longa = extrair_vara_do_pdf(pdf_staging) or ""
    vara_curta = sanitize_vara_curta(vara_longa)

    # Nome final (PJE-019: chars invalidos Windows)
    if vara_longa:
        nome = f"{cnj} - {comarca} - {vara_longa}.pdf"
    else:
        nome = f"{cnj} - {comarca}.pdf"
    nome = re.sub(r'[<>:"/\\|?*\r\n\t]', '_', nome)

    destino_dir = PASTA_FINAL / sanitize_folder(comarca) / vara_curta
    try:
        destino_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        log(f"PASTA_FINAL inacessivel ({destino_dir}): {e}", "ERRO")
        log("Verifique: VM ligada + Parallels Shared Folders habilitado (\\\\psf\\Home\\)", "ERRO")
        return None

    destino = destino_dir / nome

    # Dedupe por tamanho
    try:
        if destino.exists() and destino.stat().st_size == pdf_staging.stat().st_size:
            log(f"Destino ja identico: {destino.name}", "INFO")
            pdf_staging.unlink()
            return destino
    except Exception:
        pass

    # PJE-021: shutil.move funciona cross-filesystem local -> UNC
    try:
        shutil.move(str(pdf_staging), str(destino))
    except Exception as e:
        log(f"shutil.move falhou (local->UNC): {e}", "ERRO")
        return None

    atualizar_controle_espelho(destino, cnj, comarca, vara_longa, str(pdf_staging))
    return destino

def carregar_progresso():
    if PROGRESSO_FILE.exists():
        try:
            return json.loads(PROGRESSO_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"baixados": [], "falhas": [], "inicio": None}

def salvar_progresso(progresso):
    progresso["ultima_atualizacao"] = datetime.now().isoformat()
    PROGRESSO_FILE.write_text(json.dumps(progresso, ensure_ascii=False, indent=2), encoding="utf-8")

def notificar_telegram(msg):
    try:
        token = None
        for p in _token_paths:
            if p.exists():
                token = p.read_text().strip()
                break
        if not token:
            return
        import urllib.request
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass

def mostrar_progresso(i, total, comarca_atual, sucesso, falha, inicio):
    elapsed = time.time() - inicio
    pct = (i / total) * 100
    if i > 0:
        tempo_por_proc = elapsed / i
        restante = tempo_por_proc * (total - i)
        eta = str(timedelta(seconds=int(restante)))
    else:
        eta = "calculando..."
    bar_len = 30
    filled = int(bar_len * i / total)
    bar = "#" * filled + "-" * (bar_len - filled)
    print(f"\r  [{bar}] {pct:5.1f}% [{i}/{total}] OK:{sucesso} FALHA:{falha} | {comarca_atual} | ETA: {eta}  ", end="", flush=True)


# ============================================================
# KILL CHROME
# ============================================================

def _cdp_vivo(host, porta):
    try:
        req = urllib.request.urlopen(f"http://{host}:{porta}/json/version", timeout=CDP_TIMEOUT)
        return "Browser" in req.read().decode("utf-8", errors="ignore")
    except Exception:
        return False


def conectar_chrome():
    """
    Conecta ao Chrome de 2 formas, na ordem:
      1) CDP existente (portas 9222/9223, tentando IPv4 e IPv6/localhost)
      2) Chrome NOVO em perfil DEDICADO isolado + porta 9223
    Nao mexe no Chrome do usuario. Nao depende de taskkill.
    """
    # 1) Tenta reusar Chrome existente com debug port aberto (IPv4 e IPv6)
    for host in ("127.0.0.1", "localhost", "[::1]"):
        for porta in PORTAS_DEBUG:
            if _cdp_vivo(host, porta):
                log(f"Chrome debug ativo em {host}:{porta} - reusando sessao", "OK")
                opts = Options()
                opts.debugger_address = f"{host}:{porta}" if not host.startswith("[") else f"localhost:{porta}"
                driver = webdriver.Chrome(options=opts)
                driver.implicitly_wait(5)
                return driver

    # 2) Abre Chrome novo em perfil isolado
    log("Nenhum CDP respondeu - abrindo Chrome em perfil dedicado...")
    AUTOMATION_PROFILE.mkdir(parents=True, exist_ok=True)
    for lf in LOCK_FILES:
        p = AUTOMATION_PROFILE / lf
        try:
            if p.exists():
                p.unlink()
        except Exception:
            pass

    # Flags minimas - ARM64 crasha com --no-sandbox, --disable-gpu, detach=True
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
    # Aceita alertas JS automaticamente (PJe spamma "Ocorreu um erro tente novamente")
    opts.set_capability("unhandledPromptBehavior", "accept")
    opts.add_experimental_option("prefs", {
        "download.default_directory": str(DOWNLOAD_TEMP),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,
    })

    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(5)
    log("Chrome aberto em perfil dedicado", "OK")

    # Navega limpo e dismissa qualquer alerta de sessao anterior
    try:
        driver.get("https://pje.tjmg.jus.br")
    except Exception:
        pass
    for _ in range(3):
        try:
            alerta = driver.switch_to.alert
            log(f"Alerta dismissado: {alerta.text[:80]}", "AVISO")
            alerta.accept()
            time.sleep(1)
        except Exception:
            break
    return driver


# ============================================================
# AGUARDAR DOWNLOAD (monitorar pasta)
# ============================================================

def aguardar_download(pasta_download, timeout=DOWNLOAD_TIMEOUT):
    """Aguarda um arquivo novo aparecer na pasta de download e o .crdownload sumir."""
    inicio = time.time()
    arquivos_antes = set(os.listdir(pasta_download)) if pasta_download.exists() else set()

    while time.time() - inicio < timeout:
        time.sleep(2)
        if not pasta_download.exists():
            continue
        arquivos_agora = set(os.listdir(pasta_download))
        novos = arquivos_agora - arquivos_antes

        # Verifica se tem arquivo novo que NAO eh .crdownload/.tmp
        for arq in novos:
            if arq.endswith(".crdownload") or arq.endswith(".tmp"):
                continue
            caminho = pasta_download / arq
            if caminho.stat().st_size > 1000:
                return caminho

        # Verifica se tem .crdownload (download em progresso)
        tem_crdownload = any(a.endswith(".crdownload") for a in arquivos_agora)
        if tem_crdownload:
            continue  # ainda baixando

        # Sem crdownload e sem arquivo novo — talvez nao iniciou ainda
        if time.time() - inicio > 30 and not tem_crdownload and not novos:
            return None  # provavel que nao iniciou

    return None


# ============================================================
# SELENIUM HELPERS
# ============================================================

def find_element_multi(driver, seletores, timeout=5):
    """Tenta multiplos seletores CSS/XPath. Retorna o primeiro achado (is_displayed tolerante - PJe tem jQuery velho que quebra o check)."""
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
                    # is_displayed quebrou (conflito jQuery PJe) - aceita o elemento mesmo assim
                    return elem
        except Exception:
            continue
    return None


def wait_element(driver, by, value, timeout=10):
    """Espera elemento ficar visivel."""
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )
    except Exception:
        return None


def is_authenticated(driver):
    """Detecta se usuario esta autenticado no PJe 1o grau.
    Regra: esta em pje.tjmg.jus.br e NAO esta na tela de login do SSO.
    (A lista estrita de tokens quebrava depois de fechar a aba do processo,
    pois a aba PUSH fica em /pje/Push/listView.seam que nao casava com nada.)
    """
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
    """Detecta se esta na pagina de login SSO (ESTRITO: host do SSO)."""
    try:
        url = driver.current_url.lower()
        return "sso.cloud.pje.jus.br" in url or "cas/login" in url
    except Exception:
        return True


def acionar_login_certificado(driver):
    """Tenta clicar no botao/link de login com certificado, se existir."""
    seletores = [
        "//a[contains(translate(normalize-space(.), 'CERTIFICADO', 'certificado'), 'certificado')]",
        "//button[contains(translate(normalize-space(.), 'CERTIFICADO', 'certificado'), 'certificado')]",
        "//input[contains(translate(@value, 'CERTIFICADO', 'certificado'), 'certificado')]",
        "a[title*='Certificado']",
        "button[title*='Certificado']",
        "input[value*='Certificado']",
        "a[href*='certificado']",
        "button[id*='certificado']",
        "a[id*='certificado']",
    ]
    botao = find_element_multi(driver, seletores, timeout=3)
    if not botao:
        return False

    try:
        driver.execute_script("arguments[0].click();", botao)
    except Exception:
        try:
            botao.click()
        except Exception:
            return False

    log("Acionado login com certificado digital.", "INFO")
    return True


# ============================================================
# AGUARDAR LOGIN
# ============================================================

def wait_for_login(driver):
    """Poll passivo aguardando o usuario logar - sem auto-click."""
    print()
    print("  " + "=" * 60)
    print("  LOGUE NO PJe 1o GRAU (advogado):")
    print("  https://pje.tjmg.jus.br/pje/Painel/painel_usuario/advogado.seam")
    print("  ")
    print("  O script detecta automaticamente quando voce estiver")
    print("  no painel (URL com 'advogado.seam' ou 'painel_usuario').")
    print("  " + "=" * 60)
    print()

    for tentativa in range(120):  # ate 6 minutos
        try:
            if is_authenticated(driver):
                log("Login detectado no PJe 1o grau!", "OK")
                return True
        except Exception:
            pass
        time.sleep(3)

    log("Timeout aguardando login (6 min)", "ERRO")
    return False


# ============================================================
# VERIFICACAO DE SESSAO
# ============================================================

def verificar_sessao(driver):
    """Verifica se a sessao do PJe ainda esta ativa."""
    try:
        return is_authenticated(driver) and not page_requires_login(driver)
    except Exception:
        return False


def aguardar_relogin(driver):
    """Poll passivo aguardando o usuario logar. Nao clica nada - so observa."""
    log("SESSAO EXPIRADA! Logue novamente no PJe 1o grau (advogado.seam).", "ERRO")
    notificar_telegram(
        "<b>SESSAO PJe EXPIRADA</b>\n"
        "Logue novamente com certificado digital no PJe 1o grau."
    )
    print()
    print("  === AGUARDANDO LOGIN MANUAL ===")
    print("  1) Na janela do Chrome (perfil dedicado), navegue pra:")
    print("     https://pje.tjmg.jus.br/pje/Painel/painel_usuario/advogado.seam")
    print("  2) Logue com certificado/VidaaS")
    print("  3) Confirme que ve o painel do advogado")
    print("  4) O script detecta automaticamente (ate 20 min)")
    print()

    for tentativa in range(120):  # 20 minutos, poll passivo
        try:
            if is_authenticated(driver):
                log("Sessao restaurada! Continuando...", "OK")
                notificar_telegram("Sessao PJe restaurada. Download continuando.")
                return True
        except Exception:
            pass
        time.sleep(10)

    log("Timeout aguardando re-login (20 min). Abortando.", "ERRO")
    return False


# ============================================================
# FLUXO PUSH (aba Push do PJe)
# ============================================================

PUSH_CNJ_RE = re.compile(r'(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})')

def extrair_cnjs_pagina_push(driver):
    """Retorna lista de CNJs na pagina atual da tabela PUSH."""
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
    """Clica na pagina atual+1 do datascroller RichFaces. Retorna True se avancou."""
    try:
        result = driver.execute_script("""
            const ds = document.querySelector('div[id*="scrollerListaProcessosCadastrados"], div.rich-datascr');
            if (!ds) return {ok: false};
            const act = ds.querySelector('td.rich-datascr-act');
            if (!act) return {ok: false};
            const current = parseInt((act.innerText||'').trim());
            if (isNaN(current)) return {ok: false};
            const next = current + 1;
            const inacts = ds.querySelectorAll('td.rich-datascr-inact');
            for (const td of inacts) {
                const n = parseInt((td.innerText||'').trim());
                if (n === next) {
                    td.click();
                    return {ok: true, current: current, next: next};
                }
            }
            return {ok: false, current: current, at_end: true};
        """)
        if result and result.get("ok"):
            time.sleep(3)
            return True
        return False
    except Exception as e:
        log(f"Erro proxima pagina: {e}", "ERRO")
        return False


def coletar_push_completo(driver, max_paginas=30):
    """Percorre todas as paginas da PUSH, retorna dict {cnj: pagina_idx} (1-based)."""
    log("Coletando mapa da aba PUSH...")
    driver.get(PUSH_URL)
    time.sleep(4)

    mapa = {}
    pag = 1
    while pag <= max_paginas:
        cnjs = extrair_cnjs_pagina_push(driver)
        novos = 0
        for c in cnjs:
            if c not in mapa:
                mapa[c] = pag
                novos += 1
        log(f"  Pagina {pag}: {len(cnjs)} CNJs ({novos} novos, total {len(mapa)})")
        if not cnjs:
            break
        if not proxima_pagina_push(driver):
            break
        pag += 1
    log(f"PUSH mapeada: {len(mapa)} processos em {pag} paginas", "OK")
    return mapa


def ir_para_pagina_push(driver, pagina_alvo):
    """Navega pra PUSH e avanca ate a pagina alvo."""
    driver.get(PUSH_URL)
    time.sleep(4)
    for _ in range(pagina_alvo - 1):
        if not proxima_pagina_push(driver):
            return False
    return True


def abrir_via_push(driver, numero):
    """
    Clica no link 'Autos Digitais' da row do CNJ na pagina atual da PUSH.
    Switch pra nova aba se abrir. Retorna o handle da aba PUSH (pra voltar).
    """
    aba_original = driver.current_window_handle
    abas_antes = set(driver.window_handles)

    ok = driver.execute_script("""
        const rows = document.querySelectorAll('table[id*="dataTableProcessosCadastrados"] tbody tr');
        for (const tr of rows) {
            const cells = tr.querySelectorAll('td');
            if (cells.length >= 2) {
                const t = (cells[1].innerText || '').trim();
                if (t === arguments[0]) {
                    const link = tr.querySelector('a[title="Autos Digitais"]');
                    if (link) { link.click(); return true; }
                }
            }
        }
        return false;
    """, numero)

    if not ok:
        return None

    # Aguarda aba nova ou navegacao
    time.sleep(4)
    novas = set(driver.window_handles) - abas_antes
    if novas:
        driver.switch_to.window(next(iter(novas)))
        try:
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass
    return aba_original


# ============================================================
# DOWNLOAD DE UM PROCESSO
# ============================================================

def baixar_processo(driver, numero, mapa_push=None):
    aba_push = None
    """Baixa autos completos de um processo. Retorna True/False."""
    # 1) Checa PASTA_FINAL (qualquer subpasta) — evita re-baixar
    ja_final = pdf_ja_baixado_final(numero)
    if ja_final:
        tam = ja_final.stat().st_size / 1024 / 1024
        log(f"Ja existe em final: {numero} ({tam:.1f}MB) [{ja_final.parent.name}/]", "OK")
        return True

    # 2) Pasta staging local (Chrome baixa aqui, depois move pra final)
    pasta = PASTA_STAGING / sanitize_folder(numero)
    pasta.mkdir(parents=True, exist_ok=True)
    pdf_path = pasta / "autos-completos.pdf"

    # 3) Staging tem PDF valido mas nao chegou na final: tenta so mover
    if pdf_path.exists() and pdf_path.stat().st_size > 10000:
        log(f"Existe em staging: {numero} - tentando mover pra final", "INFO")
        destino = mover_pra_final(pdf_path, numero)
        if destino:
            log(f"Recuperado: {numero} -> {destino.parent.name}/", "OK")
            return True
        log(f"Move falhou, re-baixando", "AVISO")

    try:
        # 1. Verifica sessao antes de cada processo
        if not verificar_sessao(driver):
            ok = aguardar_relogin(driver)
            if not ok:
                return False

        # 2. Abre via PUSH (search por CNJ bloqueada por reCAPTCHA invisivel do PJe)
        if not mapa_push or numero not in mapa_push:
            log(f"CNJ nao esta na aba PUSH: {numero}", "ERRO")
            return False

        if not ir_para_pagina_push(driver, mapa_push[numero]):
            log(f"Falha ao ir pra pagina {mapa_push[numero]} da PUSH: {numero}", "ERRO")
            return False

        aba_push = abrir_via_push(driver, numero)
        if not aba_push:
            log(f"Falha ao abrir processo via PUSH: {numero}", "ERRO")
            return False
        # Agora estamos na aba do processo aberto

        # 5. Botao de download dos autos
        download_btn_seletores = [
            "a[id*='downloadAutos']",
            "a[title*='Download']",
            "a[title*='download']",
            "//a[contains(@id, 'download')]",
            "//a[contains(@title, 'Download')]",
            "//span[contains(@class, 'fa-download')]/parent::a",
            "//i[contains(@class, 'fa-download')]/parent::a",
            ".download-autos",
            "a.icon-download",
            "a.btn-download",
            "[id*='btnDown']",
        ]

        btn_download = find_element_multi(driver, download_btn_seletores, timeout=5)

        if not btn_download:
            log(f"Botao download nao encontrado: {numero}", "ERRO")
            driver.save_screenshot(str(pasta / "erro_botao.png"))
            return False

        btn_download.click()
        time.sleep(2)

        # 6. Configura opcoes do dialogo de download
        for sel_id, val in [("cronologia", "Crescente"), ("expediente", "Sim"), ("movimento", "Sim")]:
            try:
                sels = driver.find_elements(By.CSS_SELECTOR, f"select[id*='{sel_id}']")
                if not sels:
                    sels = driver.find_elements(By.CSS_SELECTOR, f"select[id*='{sel_id.capitalize()}']")
                for s in sels:
                    if s.is_displayed():
                        Select(s).select_by_visible_text(val)
                        break
            except Exception:
                pass

        try:
            for qr_id in ['qrCode', 'qrcode', 'QrCode']:
                sels = driver.find_elements(By.CSS_SELECTOR, f"select[id*='{qr_id}']")
                for s in sels:
                    if s.is_displayed():
                        Select(s).select_by_visible_text("Nao")
                        break
        except Exception:
            pass

        # 7. Limpa pasta temporaria antes do download
        DOWNLOAD_TEMP.mkdir(parents=True, exist_ok=True)
        for f in DOWNLOAD_TEMP.iterdir():
            try:
                f.unlink()
            except Exception:
                pass

        # 8. Clica DOWNLOAD (tenta default content + iframes)
        dl_btn_seletores = [
            "input[value='DOWNLOAD']",
            "input[value='Download']",
            "//button[contains(text(), 'DOWNLOAD')]",
            "//button[contains(text(), 'Download')]",
            "//a[contains(text(), 'DOWNLOAD')]",
            "//a[contains(text(), 'Download')]",
        ]

        dl_btn = find_element_multi(driver, dl_btn_seletores, timeout=3)

        # Se nao achou no default content, entra em cada iframe
        if not dl_btn:
            driver.switch_to.default_content()
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                try:
                    driver.switch_to.frame(iframe)
                    dl_btn = find_element_multi(driver, dl_btn_seletores, timeout=2)
                    if dl_btn:
                        break
                    driver.switch_to.default_content()
                except Exception:
                    try:
                        driver.switch_to.default_content()
                    except Exception:
                        pass

        if not dl_btn:
            log(f"Botao DOWNLOAD final nao encontrado: {numero}", "ERRO")
            driver.save_screenshot(str(pasta / "erro_download_btn.png"))
            return False

        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", dl_btn)
        except Exception:
            dl_btn.click()
        driver.switch_to.default_content()

        # 9. Aguarda arquivo na pasta temporaria
        arquivo_baixado = aguardar_download(DOWNLOAD_TEMP, timeout=DOWNLOAD_TIMEOUT)

        if arquivo_baixado and arquivo_baixado.exists():
            # STAGING: move do temp do Chrome pra pasta do CNJ em staging local
            import shutil
            shutil.move(str(arquivo_baixado), str(pdf_path))

            if pdf_path.exists() and pdf_path.stat().st_size > 1000:
                # FINAL: extrai vara, valida CNJ, move pra PASTA_FINAL / Comarca / VaraCurta /
                destino = mover_pra_final(pdf_path, numero)
                if destino is None:
                    log(f"Baixou em staging mas falhou mover pra final: {numero}", "ERRO")
                    return False
                tam = destino.stat().st_size / (1024 * 1024)
                log(f"Baixado+organizado: {numero} ({tam:.1f} MB) -> {destino.parent.name}/", "OK")
                return True
            else:
                log(f"PDF vazio ou muito pequeno: {numero}", "ERRO")
                return False
        else:
            log(f"Download direto falhou, tentando Area de Download: {numero}...", "AVISO")
            return verificar_area_download(driver, numero, pasta)

    except Exception as e:
        log(f"Erro: {numero}: {e}", "ERRO")
        try:
            driver.save_screenshot(str(pasta / "erro_geral.png"))
        except Exception:
            pass
        return False
    finally:
        # Fecha aba do processo e volta pra aba da PUSH
        try:
            abas = driver.window_handles
            if len(abas) > 1 and aba_push in abas:
                atual = driver.current_window_handle
                if atual != aba_push:
                    driver.close()
                    driver.switch_to.window(aba_push)
        except Exception:
            pass


def verificar_area_download(driver, numero, pasta):
    """Verifica se o PDF esta na Area de Download do PJe (processos > 50MB vao pra fila)."""
    try:
        area_url = f"{PJE_BASE}/AreaDeDownload/listView.seam"
        driver.get(area_url)
        time.sleep(3)

        for tentativa in range(18):  # ~3 min
            content = driver.page_source
            if numero in content:
                try:
                    row_xpath = f"//tr[contains(., '{numero}')]//a[contains(@href, 'download')]"
                    links = driver.find_elements(By.XPATH, row_xpath)
                    if links:
                        # Limpa temp antes
                        for f in DOWNLOAD_TEMP.iterdir():
                            try:
                                f.unlink()
                            except Exception:
                                pass

                        links[0].click()
                        arquivo = aguardar_download(DOWNLOAD_TEMP, timeout=DOWNLOAD_TIMEOUT)

                        if arquivo and arquivo.exists():
                            import shutil
                            pdf_local = pasta / "autos-completos.pdf"
                            shutil.move(str(arquivo), str(pdf_local))
                            if pdf_local.exists():
                                destino = mover_pra_final(pdf_local, numero)
                                if destino:
                                    log(f"Baixado da fila + organizado: {numero} -> {destino.parent.name}/", "OK")
                                    return True
                except Exception:
                    pass

            log(f"  Fila... ({tentativa+1}/18)", "INFO")
            time.sleep(10)
            driver.refresh()

    except Exception as e:
        log(f"Erro Area Download: {e}", "ERRO")
    return False


def baixar_com_retry(driver, cnj, max_retries, mapa_push=None):
    """Tenta baixar um processo com retries."""
    for tentativa in range(max_retries):
        ok = baixar_processo(driver, cnj, mapa_push=mapa_push)
        if ok:
            return True
        if tentativa < max_retries - 1:
            log(f"Tentativa {tentativa+1}/{max_retries} falhou. Retentando em 5s...", "AVISO")
            time.sleep(5)
    return False


# ============================================================
# LISTAR
# ============================================================

def cmd_listar():
    por_grupo = {}
    for cnj in PROCESSOS:
        comarca = get_comarca(cnj)
        prio = get_prioridade(comarca)
        key = (prio, comarca)
        por_grupo.setdefault(key, []).append(cnj)

    print()
    print("=" * 65)
    print(f"  LISTA DE DOWNLOAD -- {len(PROCESSOS)} processos")
    print("=" * 65)
    print()

    for (prio, comarca) in sorted(por_grupo.keys()):
        cnjs = por_grupo[(prio, comarca)]
        marca = "*" if prio <= 2 else ("-" if prio >= 98 else ".")
        print(f"  {marca} [{prio}] {comarca}: {len(cnjs)} processos")
        for cnj in cnjs[:3]:
            print(f"        {cnj}")
        if len(cnjs) > 3:
            print(f"        ... (+{len(cnjs)-3} mais)")
        print()


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Download direto -- PJe TJMG -- 157 processos (Selenium)")
    parser.add_argument("--teste", action="store_true", help="Baixa so 1 processo")
    parser.add_argument("--sem-retomar", action="store_true", help="Ignora progresso anterior")
    parser.add_argument("--so-comarca", default=None, help="Filtra por comarca")
    parser.add_argument("--listar", action="store_true", help="Mostra lista sem baixar")
    parser.add_argument("--retries", type=int, default=MAX_RETRIES, help="Tentativas por processo")
    args = parser.parse_args()

    if args.listar:
        cmd_listar()
        return

    PASTA_STAGING.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_TEMP.mkdir(parents=True, exist_ok=True)
    # Checa PASTA_FINAL (UNC Parallels) — falha explicita se nao acessivel
    try:
        PASTA_FINAL.mkdir(parents=True, exist_ok=True)
        _probe = PASTA_FINAL / ".__probe__"
        _probe.write_text("ok", encoding="utf-8")
        _probe.unlink()
    except Exception as e:
        print(f"\n  [ERRO CRITICO] PASTA_FINAL inacessivel: {e}")
        print(f"  Path: {PASTA_FINAL}")
        print(f"  Checar: (1) VM Parallels ligada? (2) Shared Folders habilitado?")
        print(f"  (3) A pasta existe no Mac em ~/Desktop/STEMMIA Dexter/Processos Atualizados/?")
        sys.exit(1)

    # Filtra lista
    processos = list(PROCESSOS)
    if args.so_comarca:
        processos = [p for p in processos if args.so_comarca.lower() in get_comarca(p).lower()]

    # Ordena: Taiobeiras primeiro, Governador Valadares depois, resto por ultimo
    processos.sort(key=lambda p: get_prioridade(get_comarca(p)))

    # Progresso (resume de onde parou)
    progresso = carregar_progresso()
    if not args.sem_retomar:
        ja_baixados = set(progresso.get("baixados", []))
        processos = [p for p in processos if p not in ja_baixados]
    else:
        progresso = {"baixados": [], "falhas": [], "inicio": None}

    if not processos:
        print("\n  Todos os processos ja foram baixados!\n")
        return

    # Resumo
    por_comarca = {}
    for cnj in processos:
        c = get_comarca(cnj)
        por_comarca.setdefault(c, []).append(cnj)

    print()
    print("=" * 65)
    print("  DOWNLOAD DIRETO -- PJe TJMG (SELENIUM)")
    print("=" * 65)
    print(f"\n  Total pendente: {len(processos)} processos")
    print(f"  Ja baixados: {len(progresso.get('baixados', []))}")
    print(f"  Retries: {args.retries} por processo")
    print(f"  Staging (local): {PASTA_STAGING}")
    print(f"  Final (Mac UNC): {PASTA_FINAL}")
    print(f"  Download temp:   {DOWNLOAD_TEMP}")
    print("\n  ORDEM:")
    for comarca in sorted(por_comarca.keys(), key=lambda c: get_prioridade(c)):
        qtd = len(por_comarca[comarca])
        prio = get_prioridade(comarca)
        marca = "*" if prio <= 2 else ("-" if prio >= 98 else ".")
        print(f"    {marca} {comarca}: {qtd}")
    print()

    if args.teste:
        processos = processos[:1]
        print("  *** MODO TESTE: 1 processo ***\n")

    # Conecta ao Chrome (CDP existente ou abre perfil dedicado isolado)
    try:
        driver = conectar_chrome()
    except Exception as e:
        log(f"FALHA ao conectar no Chrome: {e}", "ERRO")
        print("\n  Se quiser reusar sua sessao, abra o Chrome antes com:")
        print('  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
        sys.exit(1)

    try:
        # Navega ao PJe e aguarda login
        driver.get("https://pje.tjmg.jus.br")
        time.sleep(5)

        # Verifica se ja esta logado
        url = driver.current_url.lower()
        if "painel_usuario" in url or "tasklist" in url or "advogado" in url:
            log("Ja esta logado no PJe!", "OK")
        else:
            logged_in = wait_for_login(driver)
            if not logged_in:
                log("Nao foi possivel detectar login. Abortando.", "ERRO")
                driver.quit()
                sys.exit(1)

        if not progresso.get("inicio"):
            progresso["inicio"] = datetime.now().isoformat()

        # Coleta mapa da PUSH (cnj -> pagina_idx)
        mapa_push = coletar_push_completo(driver)
        fora_push_cnjs = [c for c in processos if c not in mapa_push]
        na_push = len(processos) - len(fora_push_cnjs)
        log(f"Da sua lista: {na_push} na PUSH, {len(fora_push_cnjs)} FORA (pulados)", "PROG")
        for c in fora_push_cnjs:
            log(f"  FORA PUSH: {c} ({get_comarca(c)})", "AVISO")
        # Filtra: so processa os que estao na PUSH
        processos = [c for c in processos if c in mapa_push]
        if not processos:
            log("Nenhum processo da lista esta na PUSH. Abortando.", "ERRO")
            return

        inicio = time.time()
        sucesso = 0
        falha = 0
        comarca_anterior = ""

        notificar_telegram(
            f"<b>Download PJe iniciado (Selenium + PUSH)</b>\n"
            f"Na PUSH: {na_push}/{len(processos)}\n"
            f"Primeira comarca: {get_comarca(processos[0])}"
        )

        for i, cnj in enumerate(processos):
            comarca = get_comarca(cnj)

            if comarca != comarca_anterior and comarca_anterior:
                notificar_telegram(
                    f"<b>{comarca_anterior}</b> concluida\n"
                    f"Proxima: {comarca}\n"
                    f"Progresso: {i}/{len(processos)} ({100*i/len(processos):.0f}%)"
                )
                print()
                log(f"=== {comarca} ===", "PROG")

            comarca_anterior = comarca
            mostrar_progresso(i, len(processos), comarca, sucesso, falha, inicio)

            ok = baixar_com_retry(driver, cnj, args.retries, mapa_push=mapa_push)

            if ok:
                sucesso += 1
                progresso["baixados"].append(cnj)
            else:
                falha += 1
                if cnj not in progresso.get("falhas", []):
                    progresso["falhas"].append(cnj)

            salvar_progresso(progresso)

            # Notifica a cada 10 processos
            if (i + 1) % 10 == 0:
                elapsed = timedelta(seconds=int(time.time() - inicio))
                notificar_telegram(
                    f"<b>Progresso</b>: {i+1}/{len(processos)}\n"
                    f"OK: {sucesso} | FALHA: {falha}\n"
                    f"Comarca: {comarca}\n"
                    f"Tempo: {elapsed}"
                )

            if i < len(processos) - 1:
                time.sleep(2)

        # 2a passagem: re-escaneia a PUSH e tenta FORA_PUSH que agora podem estar visiveis
        pendentes_fora = [c for c in fora_push_cnjs if c not in progresso.get("baixados", [])]
        if pendentes_fora:
            print()
            log(f"2a passagem: re-escaneando PUSH para {len(pendentes_fora)} nao encontrados...", "PROG")
            try:
                mapa_push2 = coletar_push_completo(driver)
            except Exception as e:
                log(f"Falha na 2a coleta PUSH: {e}", "ERRO")
                mapa_push2 = {}
            agora_na_push = [c for c in pendentes_fora if c in mapa_push2]
            ainda_fora = [c for c in pendentes_fora if c not in mapa_push2]
            log(f"Encontrados: {len(agora_na_push)} / Ainda fora: {len(ainda_fora)}", "PROG")
            for c in ainda_fora:
                if c not in progresso.get("falhas", []):
                    progresso["falhas"].append(c)
            for cnj in agora_na_push:
                log(f"Retentando (2a passagem): {cnj}", "PROG")
                ok = baixar_com_retry(driver, cnj, args.retries, mapa_push=mapa_push2)
                if ok:
                    sucesso += 1
                    progresso["baixados"].append(cnj)
                    if cnj in progresso.get("falhas", []):
                        progresso["falhas"].remove(cnj)
                else:
                    falha += 1
                    if cnj not in progresso.get("falhas", []):
                        progresso["falhas"].append(cnj)
                salvar_progresso(progresso)

        print()
        print()
        elapsed = timedelta(seconds=int(time.time() - inicio))
        print("=" * 65)
        print(f"  CONCLUIDO em {elapsed}")
        print(f"  OK: {sucesso}  |  FALHA: {falha}  |  Total: {len(processos)}")
        print(f"  Pasta: {PASTA_FINAL}")
        print("=" * 65)

        if progresso.get("falhas"):
            print(f"\n  Falhas ({len(progresso['falhas'])}):")
            for f_cnj in progresso["falhas"]:
                print(f"    - {f_cnj} ({get_comarca(f_cnj)})")
            print(f"\n  Para retentar falhas:")
            print(f"    python baixar_direto_selenium.py --sem-retomar")

        notificar_telegram(
            f"<b>Download concluido!</b>\n"
            f"OK: {sucesso} | FALHA: {falha}\n"
            f"Tempo: {elapsed}\n"
            f"Pasta: {PASTA_FINAL}"
        )

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
