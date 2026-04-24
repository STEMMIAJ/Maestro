#!/usr/bin/env python3
"""
Configuração central do Hub de Automações — Stemmia Forense.

Caminhos, definição de fontes, filtros anti-ruído, FTP.
"""

from pathlib import Path

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path.home() / "stemmia-forense"
AUTOMACOES_DIR = PROJECT_ROOT / "automacoes"
ESTADO_PATH = AUTOMACOES_DIR / "estado_hub.json"
DASHBOARD_PATH = AUTOMACOES_DIR / "DASHBOARD-HUB.html"
LOGS_DIR = AUTOMACOES_DIR / "logs"

DATA_DIR = PROJECT_ROOT / "data"
CONSOLIDADO_JSON = DATA_DIR / "PROCESSOS-CONSOLIDADO.json"
LISTA_MESTRE = DATA_DIR / "LISTA-MESTRE-PROCESSOS.json"

PIPELINE_DIR = PROJECT_ROOT / "src" / "pipeline"
PJE_DIR = PROJECT_ROOT / "src" / "pje"
UTILIDADES_DIR = PROJECT_ROOT / "src" / "utilidades"

FONTES_DIR = PIPELINE_DIR / "fontes"
PROCESSOS_DIR = PROJECT_ROOT / "processos"

# ============================================================
# PERITO
# ============================================================

PERITO_CPF = "12785885660"
PERITO_CPF_FMT = "127.858.856-60"
PERITO_NOME = "NOLETO"
PERITO_NOME_COMPLETO = "JESUS EDUARDO NOLETO"
PERITO_CRM = "92148"

# ============================================================
# FONTES DE DADOS
# ============================================================

FONTES = [
    {
        "id": "dje_tjmg",
        "nome": "DJe TJMG",
        "descricao": "Diário Eletrônico — 20 comarcas",
        "cor": "#3b82f6",
        "ativa": True,
    },
    {
        "id": "datajud",
        "nome": "DataJud API",
        "descricao": "API pública CNJ — movimentações",
        "cor": "#8b5cf6",
        "ativa": True,
    },
    {
        "id": "pje_consulta",
        "nome": "PJe Consulta",
        "descricao": "Consulta pública TJMG por CPF",
        "cor": "#f59e0b",
        "ativa": True,
    },
    {
        "id": "comunica_pje",
        "nome": "Comunica PJe",
        "descricao": "API pública CNJ — comunicações processuais (3 layers)",
        "cor": "#10b981",
        "ativa": True,
    },
]

# ============================================================
# FILTRO ANTI-RUÍDO (PJe Consulta Pública)
# ============================================================

CLASSES_EXCLUIR_PJE = [
    "Auto de Prisão em Flagrante",
    "Alimentos",
    "Alimentos - Prestação",
    "Termo Circunstanciado",
    "Despejo",
    "Carta Precatória Criminal",
    "Comunicado de Mandado de Prisão",
    "Execução de Pena",
    "Ação Penal",
    "Medida Protetiva",
    "Habeas Corpus",
    "Busca e Apreensão",
    "Divórcio",
    "Guarda",
    "Regulamentação de Visitas",
    "Inventário",
]

# ============================================================
# FTP DEPLOY
# ============================================================

FTP_HOST = "alvorada.nuvemidc.com"
FTP_USER = "deploy@stemmia.com.br"
FTP_REMOTE_DIR = "/webdev/teste/"
FTP_DASHBOARD_FILENAME = "dashboard-hub.html"

# ============================================================
# TELEGRAM
# ============================================================

TELEGRAM_CHAT_ID = "8397602236"

# ============================================================
# EXECUÇÃO
# ============================================================

DJE_DIAS_PADRAO = 3
DATAJUD_DIAS_MOVIMENTACAO = 30
HISTORICO_MAX_DIAS = 30
