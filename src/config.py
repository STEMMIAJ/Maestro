"""
Configuração centralizada do STEMMIA Dexter.
Hub de perícia médica judicial — Governador Valadares/MG.
"""

import os
from pathlib import Path

# ============================================================
# CHAVES / CREDENCIAIS
# ============================================================
# DataJud CNJ — chave PÚBLICA documentada pelo CNJ.
# Mesmo sendo pública, lemos do ambiente para manter o código-fonte
# livre de segredos e permitir rotação sem editar arquivos.
#
# Para setar, carregue o .env do projeto:
#   set -a; source "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/.env"; set +a
# Ou exporte manualmente em ~/.zshrc:
#   export DATAJUD_API_KEY="<chave-publica-datajud>"
#
# Fonte oficial da chave: https://datajud-wiki.cnj.jus.br/api-publica/acesso
DATAJUD_API_KEY = os.getenv("DATAJUD_API_KEY", "")


def exigir_datajud_key() -> str:
    """Retorna DATAJUD_API_KEY ou falha com instrução clara de export."""
    key = os.getenv("DATAJUD_API_KEY", "")
    if not key:
        raise RuntimeError(
            "DATAJUD_API_KEY não está setada no ambiente.\n"
            "Execute:\n"
            '  export DATAJUD_API_KEY="<chave-publica-datajud>"\n'
            "Ou adicione em ~/.zshrc / ~/Desktop/STEMMIA Dexter/00-CONTROLE/.env\n"
            "Chave pública documentada em: https://datajud-wiki.cnj.jus.br/api-publica/acesso"
        )
    return key


# ============================================================
# DIRETÓRIOS BASE
# ============================================================

DEXTER_ROOT = Path.home() / "Desktop" / "STEMMIA Dexter"
PROCESSOS_DIR = Path.home() / "Desktop" / "ANALISADOR FINAL" / "processos"
PJE_DOWNLOADS = Path.home() / "Desktop" / "processos-pje-windows"
PERICIAS_DIR = Path.home() / "Desktop" / "PERÍCIA"
SCRIPTS_DIR = Path.home() / "Desktop" / "ANALISADOR FINAL" / "scripts"

# ============================================================
# SUBDIRETÓRIOS DEXTER
# ============================================================

SRC_DIR = DEXTER_ROOT / "src"
MEMORIA_DIR = DEXTER_ROOT / "memoria"
TEMPLATES_DIR = DEXTER_ROOT / "templates"
REFERENCIAS_DIR = DEXTER_ROOT / "referencias"
DATA_DIR = DEXTER_ROOT / "data"
PAINEL_DIR = DEXTER_ROOT / "painel"

# Subdiretórios de templates
TEMPLATES_LAUDO = TEMPLATES_DIR / "laudo"
TEMPLATES_PETICAO = TEMPLATES_DIR / "peticao"
TEMPLATES_ROTEIRO = TEMPLATES_DIR / "roteiro"
TEMPLATES_RELATORIO = TEMPLATES_DIR / "relatorio"

# Subdiretórios de referências
REF_CHECKLIST = REFERENCIAS_DIR / "checklist"
REF_ESCALAS = REFERENCIAS_DIR / "escalas"

# ============================================================
# SAÍDA
# ============================================================

SAIDA_PETICOES = Path.home() / "Desktop" / "ANALISADOR FINAL" / "saida" / "peticoes-claude"
SAIDA_LAUDOS = PERICIAS_DIR

# ============================================================
# SITE
# ============================================================

SITE_URL = "https://stemmiapericia.com"
FTP_HOST = "ftp.stemmiapericia.com"

# ============================================================
# TELEGRAM
# ============================================================

TELEGRAM_BOT = "@stemmiapericia_bot"
TELEGRAM_CHAT_ID = "8397602236"

# ============================================================
# N8N
# ============================================================

N8N_URL = "https://n8n.srv19105.nvhm.cloud"

# ============================================================
# HELPERS
# ============================================================


def garantir_diretorios():
    """Cria todos os diretórios configurados se não existirem."""
    diretorios = [
        SRC_DIR,
        MEMORIA_DIR,
        TEMPLATES_DIR,
        TEMPLATES_LAUDO,
        TEMPLATES_PETICAO,
        TEMPLATES_ROTEIRO,
        TEMPLATES_RELATORIO,
        REFERENCIAS_DIR,
        REF_CHECKLIST,
        REF_ESCALAS,
        DATA_DIR,
        PAINEL_DIR,
        SAIDA_PETICOES,
    ]
    for d in diretorios:
        d.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    garantir_diretorios()
    print(f"DEXTER_ROOT: {DEXTER_ROOT}")
    print(f"Diretórios verificados/criados.")
