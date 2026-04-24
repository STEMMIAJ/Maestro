#!/bin/bash
# Hook PostToolUse (Write) — Copia .md APENAS para Plan Mode (organizado por data)
# NÃO copia para a Mesa — a Mesa deve ficar limpa.
# Atualizado: 2026-03-17 — removida cópia para ~/Desktop/

LOG="$HOME/stemmia-forense/logs/copias-md.log"
PLAN_MODE="$HOME/Desktop/Projetos - Plan Mode/documentos-criados"
MAX_SIZE=52428800  # 50 MB

# Lê JSON do stdin
INPUT=$(cat)

# Extrai o file_path do tool_input
FILE_PATH=$(echo "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"//' | sed 's/"$//')

# Se não conseguiu extrair → sai
[ -z "$FILE_PATH" ] && exit 0

# Se não termina em .md → sai silencioso
[[ "$FILE_PATH" != *.md ]] && exit 0

# Se o arquivo não existe → sai
[ ! -f "$FILE_PATH" ] && exit 0

# Ignorar arquivos de sistema e temporários
case "$FILE_PATH" in
    */plans/*|*/.claude/*|*/node_modules/*|*/tmp/*|*/.cache/*|*/.git/*|*/memory/*)
        exit 0
        ;;
esac

# Ignorar se o destino já é o Plan Mode (evitar loop)
FILE_DIR=$(dirname "$FILE_PATH")
if [[ "$FILE_DIR" == "$PLAN_MODE"* ]]; then
    exit 0
fi

# Verificar tamanho (máximo 50 MB)
FILE_SIZE=$(stat -f%z "$FILE_PATH" 2>/dev/null || echo 0)
if [ "$FILE_SIZE" -gt "$MAX_SIZE" ]; then
    exit 0
fi

# Nome base do arquivo
BASENAME=$(basename "$FILE_PATH")
DATA_HOJE=$(date +%Y-%m-%d)

# --- Cópia APENAS para Plan Mode (organizado por data) ---
DEST_DIR="$PLAN_MODE/$DATA_HOJE"
mkdir -p "$DEST_DIR"
DEST_PLAN="$DEST_DIR/$BASENAME"
if [ -f "$DEST_PLAN" ]; then
    NAME="${BASENAME%.md}"
    N=2
    while [ -f "$DEST_DIR/${NAME}-v${N}.md" ]; do
        N=$((N + 1))
    done
    DEST_PLAN="$DEST_DIR/${NAME}-v${N}.md"
fi
cp "$FILE_PATH" "$DEST_PLAN" 2>/dev/null

# --- Log ---
echo "[$(date '+%Y-%m-%d %H:%M:%S')] BACKUP: $FILE_PATH → $DEST_PLAN" >> "$LOG"

exit 0
