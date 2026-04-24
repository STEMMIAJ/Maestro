"""
config_pje.py — Configuração centralizada dos fluxos PJe.

Consolida paths, credenciais públicas e constantes usadas por
descoberta, download e cadastro. 1 lugar só.

Fix 2026-04-19: antes havia APIKey hardcoded em descobrir_processos.py
linha 64. Agora vive aqui. Secret do Dr. Jesus (senha PJe) fica fora
deste arquivo — usa ~/.credenciais-cnj.json (ainda não criado).
"""

from pathlib import Path
import platform


# ── IDENTIDADE DO PERITO ──────────────────────────────────────
# Dr. Jesus Eduardo Noleto de Souza — perito médico judicial (CRM MG)
PERITO_CPF = "12785885660"
PERITO_CPF_FMT = "127.858.856-60"
PERITO_NOME = "NOLETO"
PERITO_NOME_COMPLETO = "JESUS EDUARDO NOLETO DE SOUZA"


# ── APIs PÚBLICAS ─────────────────────────────────────────────
# APIKey DataJud CNJ — chave PÚBLICA documentada em:
# https://datajud-wiki.cnj.jus.br/api-publica/acesso
# Mesmo sendo pública, lemos do ambiente (DATAJUD_API_KEY) para manter
# o código-fonte sem credenciais. Export em ~/.zshrc ou .env do projeto.
import os as _os
DATAJUD_KEY = _os.getenv("DATAJUD_API_KEY", "")
if not DATAJUD_KEY:
    import warnings as _w
    _w.warn(
        "DATAJUD_API_KEY não setada. Consultas ao DataJud falharão. "
        'Execute: export DATAJUD_API_KEY="<chave>" '
        "(ver https://datajud-wiki.cnj.jus.br/api-publica/acesso)",
        RuntimeWarning,
        stacklevel=2,
    )
DATAJUD_ENDPOINTS = {
    "tjmg": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search",
    "trf6": "https://api-publica.datajud.cnj.jus.br/api_publica_trf6/_search",
    "trt3": "https://api-publica.datajud.cnj.jus.br/api_publica_trt3/_search",
}

PJE_TJMG_BASE = "https://pje.tjmg.jus.br"
PJE_CONSULTA_PUBLICA = f"{PJE_TJMG_BASE}/pje/ConsultaPublica/listView.seam"

DJE_TJMG_BASE = "https://www8.tjmg.jus.br/juridico/diariojudicial/djem/publicacoes.jsp"
DJEN_API = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"


# ── PATHS ─────────────────────────────────────────────────────
if platform.system() == "Windows":
    import os
    HOME = Path(os.environ.get("USERPROFILE", "C:\\Users\\jesus"))
else:
    HOME = Path.home()

DESKTOP = HOME / "Desktop"
DEXTER_ROOT = DESKTOP / "STEMMIA Dexter"
MAESTRO_ROOT = DEXTER_ROOT / "Maestro"
PJE_ROOT = MAESTRO_ROOT / "src" / "pje"

# Subpastas canônicas
DESCOBERTA_DIR = PJE_ROOT / "descoberta"
DOWNLOAD_DIR = PJE_ROOT / "download"
CADASTRO_DIR = PJE_ROOT / "cadastro"
LOGS_DIR = PJE_ROOT / "_logs"
SESSOES_DIR = PJE_ROOT / "_sessoes"

# Pastas externas usadas pelos fluxos
PROCESSOS_DIR = DESKTOP / "ANALISADOR FINAL" / "processos"
PDFS_PJE_WINDOWS = DESKTOP / "processos-pje-windows"
FALHAS_JSON = DESKTOP / "_MESA" / "01-ATIVO" / "PYTHON-BASE" / "03-FALHAS-SOLUCOES" / "db" / "falhas.json"

# Banco de dados central de processos
# ÚNICO local autorizado para persistir processos descobertos.
MAESTRO_DB = MAESTRO_ROOT / "banco-local" / "maestro.db"

# Download padrão do baixar_push_pje (Windows/Parallels)
DEFAULT_DOWNLOAD_DIR = DESKTOP / "processos-novos"


# ── DEDUP/CACHE ───────────────────────────────────────────────
DEDUP_INDEX_FILE = "_downloads_feitos.json"     # criado em DEFAULT_DOWNLOAD_DIR
PUSH_MAPA_FILE = "push_atual_{data}.json"       # em cadastro/_mapa/
ERROS_FLUXO_JSONL = LOGS_DIR / "erros_fluxo.jsonl"


# ── CREDENCIAIS PRIVADAS (lazy load) ──────────────────────────
CREDENCIAIS_PATH = HOME / ".credenciais-cnj.json"


def carregar_credenciais():
    """Carrega credenciais privadas se arquivo existir. Não falha se ausente."""
    import json
    if not CREDENCIAIS_PATH.exists():
        return {}
    try:
        return json.loads(CREDENCIAIS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ── FILTROS/REGEX ─────────────────────────────────────────────
import re
RE_CNJ = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')

# DJEN — filtro de ementa para reconhecer nomeação pericial
DJEN_FILTRO_PERITO = re.compile(r"PERIT|NOMEADO|LAUDO|EXPERT", re.IGNORECASE)

# Ordem de prioridade de comarcas para download
# 0627 = Governador Valadares, 0680 = Conselheiro Pena, 0396 = Mantena, 0105 = Rio Pardo
ORDEM_COMARCA_DEFAULT = ["0680", "0627", "0105", "0396"]


# ── TIMEOUTS ──────────────────────────────────────────────────
WAIT_LOGIN = 300          # 5 min para login manual
WAIT_DOWNLOAD = 180       # 3 min para download PDF
TIMEOUT_PROCESSO = 300    # 5 min por processo (PDFs grandes)
SLEEP_ENTRE_PROCESSOS = 20


# ── VALIDAÇÃO EM RUNTIME ──────────────────────────────────────
def validar():
    """Checa que paths críticos existem. Retorna dict de problemas."""
    problemas = {}
    for nome, p in [
        ("DEXTER_ROOT", DEXTER_ROOT),
        ("PJE_ROOT", PJE_ROOT),
        ("DESCOBERTA_DIR", DESCOBERTA_DIR),
        ("DOWNLOAD_DIR", DOWNLOAD_DIR),
        ("CADASTRO_DIR", CADASTRO_DIR),
    ]:
        if not p.exists():
            problemas[nome] = f"não existe: {p}"
    return problemas


if __name__ == "__main__":
    print(f"PERITO: {PERITO_NOME_COMPLETO} ({PERITO_CPF_FMT})")
    print(f"DEXTER_ROOT: {DEXTER_ROOT}")
    print(f"PJE_ROOT: {PJE_ROOT}")
    prob = validar()
    if prob:
        print("PROBLEMAS:")
        for k, v in prob.items():
            print(f"  - {k}: {v}")
    else:
        print("OK: todos os paths existem")
