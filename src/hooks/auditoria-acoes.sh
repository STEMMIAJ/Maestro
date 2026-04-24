#!/bin/bash
# Hook: Registra todas as acoes de edicao/escrita em log de auditoria
# Evento: PostToolUse (Edit|Write)

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_DIR="$HOME/Desktop/Projetos - Plan Mode/Registros Sessões/auditorias"
LOG_FILE="$LOG_DIR/AUDIT-$(date '+%Y-%m-%d').log"

# Garantir que o diretorio existe
mkdir -p "$LOG_DIR"

# Registrar a acao
echo "[$TIMESTAMP] Tool: $CLAUDE_TOOL_NAME | File: ${CLAUDE_FILE_PATH:-N/A}" >> "$LOG_FILE"

exit 0
