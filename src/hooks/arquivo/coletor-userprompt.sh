#!/bin/bash
# Hook UserPromptSubmit — coleta a cada 30 prompts (throttled)
# Performance: < 10ms no skip, < 500ms quando coleta
INPUT=$(cat)

# Throttle: counter file por sessão (usa PID do terminal pai)
PPID_HASH=$(echo "$$-$PPID" | md5 2>/dev/null | head -c 8)
COUNTER_FILE="/tmp/process-mapper-prompt-$PPID_HASH"

# Incrementa counter
COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo "0")
COUNT=$((COUNT + 1))
echo "$COUNT" > "$COUNTER_FILE"

# Só coleta a cada 30 prompts
if [ $((COUNT % 30)) -eq 0 ]; then
    exec "$HOME/.claude/plugins/process-mapper/scripts/coletor-universal.sh" --origem=userprompt
fi

exit 0
