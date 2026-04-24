#!/usr/bin/env bash
# Hook PostToolUse para Write — verifica se arquivo foi realmente criado no disco.
# Recebe JSON do Claude Code via stdin com dados do tool_use.

set -euo pipefail

# Ler stdin (JSON do hook)
INPUT=$(cat 2>/dev/null || true)

# Se stdin vazio, sair silencioso
if [ -z "$INPUT" ]; then
  exit 0
fi

# Extrair file_path do JSON
# O Claude Code passa o input do tool em tool_input.file_path
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Estrutura: tool_input.file_path
    fp = data.get('tool_input', {}).get('file_path', '')
    if not fp:
        # Fallback: tentar tool_result ou outros campos
        fp = data.get('file_path', '')
    print(fp)
except Exception:
    print('')
" 2>/dev/null || echo "")

# Se não conseguiu extrair path, sair silencioso (não bloquear)
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Expandir ~ e $HOME se presentes
FILE_PATH=$(eval echo "$FILE_PATH" 2>/dev/null || echo "$FILE_PATH")

# Verificar se arquivo existe
if [ ! -f "$FILE_PATH" ]; then
  echo "ERRO: ARQUIVO NAO FOI CRIADO: $FILE_PATH" >&2
  echo "O Write reportou sucesso mas o arquivo nao existe no disco." >&2
  echo "Verifique permissoes e caminho." >&2
  exit 1
fi

# Verificar se arquivo tem conteudo (nao esta vazio)
if [ ! -s "$FILE_PATH" ]; then
  echo "AVISO: Arquivo criado mas VAZIO: $FILE_PATH" >&2
  exit 1
fi

# Tudo OK — silencioso
exit 0
