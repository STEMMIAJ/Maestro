#!/bin/bash
# Script executado automaticamente após criar arquivo com ferramenta Write
# Hook: PostToolUse (matcher: Write)

PLAN_MODE_DIR="$HOME/Desktop/Projetos - Plan Mode"
SESSAO_ATUAL_FILE="$PLAN_MODE_DIR/.sessao_atual"

# Lê JSON do stdin (enviado pelo hook)
INPUT=$(cat)

# Extrai o caminho do arquivo criado
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)

# Se não conseguiu extrair o caminho, sai
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Se o arquivo de sessão atual não existe, sai
if [ ! -f "$SESSAO_ATUAL_FILE" ]; then
    exit 0
fi

SESSAO_DIR=$(cat "$SESSAO_ATUAL_FILE")
CONTEXTO_FILE="$SESSAO_DIR/CONTEXTO.txt"

# Se o diretório de contexto não existe, sai
if [ ! -f "$CONTEXTO_FILE" ]; then
    exit 0
fi

# Registra no CONTEXTO.txt
echo "- $(date +"%H:%M:%S") | $FILE_PATH" >> "$CONTEXTO_FILE"

exit 0
