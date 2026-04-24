#!/bin/bash
# pos-criacao.sh — Hook PostToolUse (Write)
# Detecta criação de agentes/skills/plugins e roda scripts pós-criação automaticamente.
# Recebe JSON do PostToolUse via stdin.

SCRIPTS_DIR="$HOME/stemmia-forense/src/utilidades"
LOG="/tmp/pos-criacao-hook.log"

# Ler JSON do stdin
INPUT=$(cat)

# Extrair file_path do tool_input do Write
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # PostToolUse fornece tool_input com os parâmetros da ferramenta
    ti = data.get('tool_input', {})
    print(ti.get('file_path', ''))
except:
    print('')
" 2>/dev/null)

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Função de timeout compatível com macOS (sem coreutils)
run_with_timeout() {
    local timeout_sec="$1"
    shift
    "$@" &
    local pid=$!
    ( sleep "$timeout_sec" && kill "$pid" 2>/dev/null ) &
    local watchdog=$!
    wait "$pid" 2>/dev/null
    local ret=$?
    kill "$watchdog" 2>/dev/null
    wait "$watchdog" 2>/dev/null
    return $ret
}

# Detectar se é agente, skill ou pipeline
if echo "$FILE_PATH" | grep -qiE '(agents/|skills/|pipelines/|\.agent\.md|\.skill\.md)'; then
    run_with_timeout 30 python3 "$SCRIPTS_DIR/gerar_guia_comandos.py" >/dev/null 2>>"$LOG" &
fi

# Detectar se é plugin
if echo "$FILE_PATH" | grep -qiE '(plugins/|\.plugin\.)'; then
    run_with_timeout 30 python3 "$SCRIPTS_DIR/atualizar_plugins.py" >/dev/null 2>>"$LOG" &
fi

# Não bloquear o hook — processos em background
wait 2>/dev/null
exit 0
