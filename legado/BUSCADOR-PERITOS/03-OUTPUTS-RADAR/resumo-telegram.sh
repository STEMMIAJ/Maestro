#!/bin/bash
# Radar — Resumo para Telegram (texto puro)
# Uso: ./resumo-telegram.sh [dia|semana|mes] [--lista]

RADAR_DIR="$HOME/Desktop/Radar"
DADOS_DIR="$RADAR_DIR/dados"
MODO="${1:-dia}"
LISTA="${2:-}"
DATA_HOJE=$(date "+%Y-%m-%d")
SEMANA_NUM=$(date "+%V")
MES_NUM=$(date "+%Y-%m")

# Encontrar snapshot mais recente
encontrar_snapshot() {
    local padrao="$1"
    ls -t "$DADOS_DIR"/snapshot-${padrao}*.json 2>/dev/null | head -1
}

# Se não há snapshot recente, rodar scanner
SNAPSHOT=""
case "$MODO" in
    dia)
        SNAPSHOT=$(encontrar_snapshot "$DATA_HOJE")
        if [ -z "$SNAPSHOT" ]; then
            bash "$RADAR_DIR/scanner.sh" 24 >/dev/null 2>&1
            SNAPSHOT=$(encontrar_snapshot "$DATA_HOJE")
        fi
        ;;
    semana)
        # Buscar todos os snapshots da semana
        SNAPSHOT=$(ls -t "$DADOS_DIR"/snapshot-*.json 2>/dev/null | head -1)
        if [ -z "$SNAPSHOT" ]; then
            bash "$RADAR_DIR/scanner.sh" 168 >/dev/null 2>&1
            SNAPSHOT=$(ls -t "$DADOS_DIR"/snapshot-*.json 2>/dev/null | head -1)
        fi
        ;;
    mes)
        SNAPSHOT=$(ls -t "$DADOS_DIR"/snapshot-*.json 2>/dev/null | head -1)
        if [ -z "$SNAPSHOT" ]; then
            bash "$RADAR_DIR/scanner.sh" 720 >/dev/null 2>&1
            SNAPSHOT=$(ls -t "$DADOS_DIR"/snapshot-*.json 2>/dev/null | head -1)
        fi
        ;;
esac

if [ -z "$SNAPSHOT" ] || [ ! -f "$SNAPSHOT" ]; then
    echo "Nenhum dado encontrado. Rode: bash ~/Desktop/Radar/scanner.sh"
    exit 1
fi

# Extrair dados com python (disponível no macOS)
python3 - "$SNAPSHOT" "$MODO" "$LISTA" << 'PYTHON_SCRIPT'
import json
import sys
from datetime import datetime, timedelta
from collections import Counter

snapshot_path = sys.argv[1]
modo = sys.argv[2]
lista = sys.argv[3] if len(sys.argv) > 3 else ""

with open(snapshot_path) as f:
    data = json.load(f)

arquivos = data.get("arquivos", [])
total = data.get("total", len(arquivos))

if total == 0:
    if modo == "dia":
        print("Nenhum arquivo novo hoje.")
    elif modo == "semana":
        print("Nenhum arquivo novo esta semana.")
    else:
        print("Nenhum arquivo novo este mês.")
    sys.exit(0)

# Contar por categoria
cats = Counter(a.get("categoria", "outro") for a in arquivos)

# Nomes bonitos das categorias
CAT_NOMES = {
    "pericia": "Perícia",
    "web": "Web/Sites",
    "automacao": "Automação",
    "config": "Configuração",
    "documentacao": "Documentação",
    "outro": "Outros"
}

# Cabeçalho
if modo == "dia":
    hoje = datetime.now().strftime("%d/%m/%Y")
    print(f"RADAR — {hoje}")
    print(f"{total} arquivos criados/modificados hoje")
elif modo == "semana":
    sem = datetime.now().strftime("%V")
    print(f"RADAR — Semana {sem}")
    print(f"{total} arquivos no período")
else:
    mes = datetime.now().strftime("%m/%Y")
    print(f"RADAR — {mes}")
    print(f"{total} arquivos no período")

print("")

# Por categoria
print("Por categoria:")
for cat, n in cats.most_common():
    nome = CAT_NOMES.get(cat, cat.title())
    print(f"  {nome}: {n}")

print("")

# Ordenar por data de modificação (mais recente primeiro)
arquivos_ord = sorted(arquivos, key=lambda a: a.get("data_modificacao", ""), reverse=True)

if lista == "--lista":
    # Lista completa
    print("Todos os arquivos:")
    for a in arquivos_ord:
        nome = a["nome"]
        caminho = a["caminho"]
        cat = CAT_NOMES.get(a.get("categoria", ""), "")
        print(f"  [{cat}] {nome}")
        print(f"    {caminho}")
else:
    # Top 10 mais recentes
    print("Mais recentes:")
    for a in arquivos_ord[:10]:
        nome = a["nome"]
        hora = ""
        dm = a.get("data_modificacao", "")
        if dm:
            try:
                dt = datetime.strptime(dm, "%Y-%m-%dT%H:%M:%S")
                hora = dt.strftime("%H:%M")
            except:
                hora = ""
        cat = CAT_NOMES.get(a.get("categoria", ""), "")
        print(f"  {hora} [{cat}] {nome}")

PYTHON_SCRIPT
