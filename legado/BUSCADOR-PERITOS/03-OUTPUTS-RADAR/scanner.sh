#!/bin/bash
# Radar Scanner — Varre diretórios e gera snapshot JSON
# Uso: ./scanner.sh [horas]  (padrão: 24h)

RADAR_DIR="$HOME/Desktop/Radar"
DADOS_DIR="$RADAR_DIR/dados"
HORAS="${1:-24}"
TIMESTAMP=$(date "+%Y-%m-%d-%H")
SNAPSHOT="$DADOS_DIR/snapshot-$TIMESTAMP.json"
DATA_HOJE=$(date "+%Y-%m-%d")

# Diretórios a monitorar
DIRS=(
    "$HOME/Desktop"
    "$HOME/Documentos"
    "$HOME/Sites"
    "$HOME/.claude/plugins"
)

# Padrões a ignorar (para find -not -path)
IGNORE_PATHS=(
    "*/node_modules/*"
    "*/.git/*"
    "*/__pycache__/*"
    "*/.venv/*"
    "*/venv/*"
    "*/.tox/*"
    "*/build/*"
    "*/dist/*"
    "*/.egg-info/*"
    "*/Radar/dados/*"
    "*/Radar/logs/*"
)

IGNORE_NAMES=(
    ".DS_Store"
    "Thumbs.db"
    ".gitignore"
    ".gitkeep"
    "*.pyc"
    "*.pyo"
    "*.tmp"
    "*.swp"
    "*.swo"
)

# Montar argumentos de exclusão
EXCLUDE_ARGS=""
for p in "${IGNORE_PATHS[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS -not -path \"$p\""
done
for n in "${IGNORE_NAMES[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS -not -name \"$n\""
done

# Função para categorizar arquivo
categorizar() {
    local caminho="$1"
    local ext="${caminho##*.}"
    ext=".$ext"

    if echo "$caminho" | grep -qi "analisador de processos\|processos\|pericia\|perícia"; then
        echo "pericia"
    elif echo "$caminho" | grep -qi "Sites\|webdev"; then
        echo "web"
    elif echo "$caminho" | grep -qi "scripts\|Radar\|imoveis-gv" || [[ "$ext" == ".sh" || "$ext" == ".command" ]]; then
        echo "automacao"
    elif echo "$caminho" | grep -qi ".claude\|.openclaw\|.config" || [[ "$ext" == ".plist" || "$ext" == ".conf" ]]; then
        echo "config"
    elif [[ "$ext" == ".md" || "$ext" == ".txt" || "$ext" == ".pdf" ]]; then
        echo "documentacao"
    elif [[ "$ext" == ".py" ]]; then
        echo "automacao"
    elif [[ "$ext" == ".html" || "$ext" == ".css" || "$ext" == ".js" ]]; then
        echo "web"
    elif [[ "$ext" == ".json" ]]; then
        echo "config"
    else
        echo "outro"
    fi
}

# Iniciar JSON
echo "{" > "$SNAPSHOT"
echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"," >> "$SNAPSHOT"
echo "  \"periodo_horas\": $HORAS," >> "$SNAPSHOT"
echo "  \"arquivos\": [" >> "$SNAPSHOT"

PRIMEIRO=1
TOTAL=0

for DIR in "${DIRS[@]}"; do
    if [ ! -d "$DIR" ]; then
        continue
    fi

    # Usar find com eval para os argumentos de exclusão
    while IFS= read -r arquivo; do
        [ -z "$arquivo" ] && continue
        [ -d "$arquivo" ] && continue

        nome=$(basename "$arquivo")
        tamanho=$(stat -f%z "$arquivo" 2>/dev/null || echo "0")
        data_mod=$(stat -f%Sm -t "%Y-%m-%dT%H:%M:%S" "$arquivo" 2>/dev/null || echo "")
        data_cria=$(stat -f%SB -t "%Y-%m-%dT%H:%M:%S" "$arquivo" 2>/dev/null || echo "")
        ext="${nome##*.}"
        [ "$ext" = "$nome" ] && ext=""
        [ -n "$ext" ] && ext=".$ext"
        categoria=$(categorizar "$arquivo")

        if [ $PRIMEIRO -eq 0 ]; then
            echo "," >> "$SNAPSHOT"
        fi
        PRIMEIRO=0
        TOTAL=$((TOTAL + 1))

        # Escapar aspas no caminho e nome
        arquivo_esc=$(echo "$arquivo" | sed 's/"/\\"/g')
        nome_esc=$(echo "$nome" | sed 's/"/\\"/g')

        cat >> "$SNAPSHOT" << ENTRY
    {
      "nome": "$nome_esc",
      "caminho": "$arquivo_esc",
      "tamanho": $tamanho,
      "extensao": "$ext",
      "data_modificacao": "$data_mod",
      "data_criacao": "$data_cria",
      "categoria": "$categoria"
    }
ENTRY

    done < <(eval "find \"$DIR\" -maxdepth 8 -type f -mmin -$((HORAS * 60)) $EXCLUDE_ARGS 2>/dev/null")
done

echo "" >> "$SNAPSHOT"
echo "  ]," >> "$SNAPSHOT"
echo "  \"total\": $TOTAL" >> "$SNAPSHOT"
echo "}" >> "$SNAPSHOT"

echo "Radar: $TOTAL arquivos encontrados (últimas ${HORAS}h) → $SNAPSHOT"
