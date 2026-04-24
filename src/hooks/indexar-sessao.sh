#!/bin/bash
# Hook SessionEnd: indexa sessão recém-encerrada no memoria.db
# Roda em background para não bloquear o Claude Code

INPUT=$(cat)

# Extrair session_id do JSON
SESSION_ID=$(echo "$INPUT" | /usr/bin/python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('session_id', data.get('sessionId', '')))
except: pass
" 2>/dev/null)

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "None" ] || [ "$SESSION_ID" = "" ]; then
    exit 0
fi

JSONL="$HOME/.claude/projects/-Users-jesus/${SESSION_ID}.jsonl"
if [ ! -f "$JSONL" ]; then
    # Fallback: tentar com username do sistema
    JSONL="$HOME/.claude/projects/-Users-$(whoami)/${SESSION_ID}.jsonl"
    [ ! -f "$JSONL" ] && exit 0
fi

# Indexar sessão em background
(
    cd "$HOME/stemmia-forense/src" 2>/dev/null
    /usr/bin/python3 -m memoria.cli index-file "$JSONL" --quiet 2>/dev/null
    /usr/bin/python3 -m memoria.cli export-html 2>/dev/null
) &

exit 0
