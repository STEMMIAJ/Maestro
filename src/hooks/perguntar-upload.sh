#!/bin/bash
# Hook PostToolUse — Pergunta se quer subir arquivo para o servidor
# Evento: PostToolUse (Write, Edit)
# Detecta criação/edição de arquivos importantes e sugere upload

TOOL_NAME="${CLAUDE_TOOL_NAME:-}"
FILE_PATH="${CLAUDE_FILE_PATH:-}"

# Só ativar para Write e Edit
[[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]] && exit 0

# Só ativar para arquivos importantes (Mesa, Plan Mode, stemmia-forense)
case "$FILE_PATH" in
  *Desktop/*.html|*Desktop/*.md|*Desktop/*.json)
    ;;
  *"Plan Mode"/*.html|*"Plan Mode"/*.md)
    ;;
  *"stemmia-forense"/*.html|*"stemmia-forense"/PAINEL*.html)
    ;;
  *)
    exit 0
    ;;
esac

# Ignorar arquivos temporários e de sistema
case "$FILE_PATH" in
  */.*|*/.claude/*|*/node_modules/*|*/venv/*)
    exit 0
    ;;
esac

NOME_ARQUIVO=$(basename "$FILE_PATH")

echo "UPLOAD DISPONÍVEL: \"$NOME_ARQUIVO\" pode ser enviado para stemmia.com.br/webdev/projetos/. Use: subir-projeto \"$FILE_PATH\"" >&2

exit 0
