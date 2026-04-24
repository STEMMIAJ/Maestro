#!/bin/bash
# AUTO-TROCAR MODELO — Intercepta rate limit e abre Sonnet automaticamente
# Hook: Notification
# Quando o Claude exibe "You're out of extra usage", este hook age sozinho
# Criado: 05/03/2026

INPUT=$(cat)

# Extrair mensagem da notificação
MSG=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    msg = json.dumps(data)
    print(msg)
except:
    print('')
" 2>/dev/null)

# Detectar rate limit
if echo "$MSG" | grep -qiE "out of.*usage|rate.limit|limit.*reset|usage.*reset|extra.usage"; then

  HANDOFF="$HOME/stemmia-forense/config/HANDOFF.md"
  SESSOES_DIR="$HOME/.claude/projects/-Users-jesusnoleto"

  # Extrair reset time se disponível
  RESET_HORA=$(echo "$MSG" | grep -oE 'resets? [0-9]+[apm: ]+' | head -1)

  # Pegar última sessão
  SESSAO_FILE=$(ls -t "$SESSOES_DIR"/*.jsonl 2>/dev/null | head -1)
  SESSAO_ID=""
  if [ -n "$SESSAO_FILE" ]; then
    SESSAO_ID=$(basename "$SESSAO_FILE" .jsonl)
  fi

  # Extrair contexto da sessão
  CONTEXTO="/tmp/contexto-sessao-anterior.md"
  echo "# Contexto da sessão anterior (auto-extraído)" > "$CONTEXTO"
  echo "**Extraído em:** $(date '+%d/%m/%Y %H:%M')" >> "$CONTEXTO"
  echo "**Motivo:** Rate limit do Opus atingido" >> "$CONTEXTO"
  echo "" >> "$CONTEXTO"

  if [ -n "$SESSAO_ID" ]; then
    python3 -c "
import json
msgs = []
try:
    with open('$SESSOES_DIR/$SESSAO_ID.jsonl', 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get('type') in ('user', 'assistant'):
                    content = data.get('message', {}).get('content', '')
                    if isinstance(content, list):
                        text = ' '.join(c.get('text', '') for c in content if c.get('type') == 'text')
                    elif isinstance(content, str):
                        text = content
                    else:
                        text = ''
                    if text and len(text) > 10:
                        role = 'USUÁRIO' if data['type'] == 'user' else 'CLAUDE'
                        msgs.append(f'**{role}:** {text[:300]}')
            except:
                pass
    for m in msgs[-15:]:
        print(m)
        print()
except:
    pass
" >> "$CONTEXTO" 2>/dev/null
  fi

  # Notificar o usuário (SIMPLIFICADO: apenas notificação, sem abrir Terminal automaticamente)
  osascript -e 'display notification "Limite do Opus atingido! Use: claude --model sonnet" with title "Claude Code - Rate Limit" sound name "Glass"' 2>/dev/null

  afplay /System/Library/Sounds/Glass.aiff 2>/dev/null &
fi

exit 0
