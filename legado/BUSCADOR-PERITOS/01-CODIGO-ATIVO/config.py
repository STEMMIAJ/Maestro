"""Configurações do Buscador de Oportunidades para Perito."""

import os
from datetime import datetime, timedelta

# Caminhos
PROJECT_DIR = os.path.expanduser("~/Desktop/Projetos - Plan Mode/buscador-peritos")
DATA_DIR = os.path.join(PROJECT_DIR, "data")
LOG_DIR = os.path.join(PROJECT_DIR, "logs")
DB_PATH = os.path.join(DATA_DIR, "oportunidades.db")

# Dashboard
DASHBOARD_PORT = 8889

# Browser
TIMEOUT_PAGINA = 30
TIMEOUT_BUSCA = 120

# Agendamento
BUSCA_INTERVALO_HORAS = 12

# User-agents
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]

# Estado foco
ESTADO_FOCO = "MG"

# Recência: só resultados dos últimos 12 meses
MESES_RECENCIA = 12
DATA_CORTE = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

# Comarcas dentro de 200km de Governador Valadares
COMARCAS_200KM = [
    # Até 100km
    "Governador Valadares",
    "Itanhomi",
    "Galileia",
    "Tarumirim",
    "Conselheiro Pena",
    "Inhapim",
    "Açucena",
    # 100-150km
    "Ipatinga",
    "Peçanha",
    "Itambacuri",
    "Coronel Fabriciano",
    "Virginópolis",
    "Caratinga",
    "Timóteo",
    "Resplendor",
    "São João Evangelista",
    "Santa Maria do Suaçuí",
    "Mantena",
    "Teófilo Otoni",
    "Capelinha",
    "Guanhães",
    # 150-200km
    "Aimorés",
    "Sabinópolis",
    "Nova Era",
    "São Domingos do Prata",
    "Ipanema",
    "Raul Soares",
    "Mutum",
    "Novo Cruzeiro",
    "Ferros",
    "Lajinha",
    "Manhuaçu",
]

# Termos otimizados (os que retornaram resultados na v1)
# Combinados com comarcas geram buscas focadas
TERMOS_COMARCA = [
    ("escassez_direta", '"falta de perito"'),
    ("escassez_direta", '"escassez de perito"'),
    ("escassez_direta", '"sem perito"'),
    ("escassez_direta", '"ausência de perito"'),
    ("dificuldade_nomeacao", '"nomeação de perito"'),
    ("dificuldade_nomeacao", '"perito não encontrado"'),
    ("mutirao", '"mutirão" "perícia"'),
    ("mutirao", '"mutirão pericial"'),
    ("mutirao", '"aguardando" "perícia"'),
    ("cadastro_aberto", '"cadastro de perito"'),
    ("cadastro_aberto", '"inscrição de perito"'),
]

# Termos genéricos com DJMG (sem comarca específica)
TERMOS_DJMG = [
    ("escassez_direta", '"falta de perito" DJMG'),
    ("escassez_direta", '"escassez de perito" DJMG'),
    ("escassez_direta", '"sem perito" DJMG'),
    ("escassez_direta", '"ausência de perito" DJMG'),
    ("dificuldade_nomeacao", '"nomeação de perito" DJMG'),
    ("dificuldade_nomeacao", '"perito não encontrado" DJMG'),
    ("mutirao", '"mutirão" "perícia" DJMG'),
    ("mutirao", '"mutirão pericial" DJMG'),
    ("mutirao", '"aguardando" "perícia" DJMG'),
    ("mutirao", '"aguardar mutirão" DJMG'),
    ("cadastro_aberto", '"cadastro de perito" DJMG'),
    ("cadastro_aberto", '"inscrição de perito" DJMG'),
]
