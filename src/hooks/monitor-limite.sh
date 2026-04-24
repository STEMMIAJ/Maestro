#!/bin/bash
# MONITOR DE LIMITE — Roda a cada resposta do Claude
# Hook: Stop (executa ao fim de cada resposta)
# Verifica sinais de rate limit e agenda notificação de reset
# Criado: 05/03/2026

RESET_FILE="/tmp/claude-opus-reset-time"
MODELO_FILE="/tmp/claude-modelo-atual"
NOTIFICADO="/tmp/claude-limite-notificado"

# Detectar modelo atual pelo processo
if ps aux | grep -q "claude.*opus" 2>/dev/null; then
  echo "opus" > "$MODELO_FILE"
fi

# Se existe arquivo de reset, verificar se já passou o tempo
if [ -f "$RESET_FILE" ]; then
  RESET_EPOCH=$(cat "$RESET_FILE" 2>/dev/null)
  NOW_EPOCH=$(date +%s)

  if [ "$NOW_EPOCH" -ge "$RESET_EPOCH" 2>/dev/null ]; then
    # Limite resetou!
    if [ ! -f "$NOTIFICADO" ]; then
      osascript -e 'display notification "Limite do Opus resetou! Pode voltar a usar." with title "Claude Code" sound name "Glass"' 2>/dev/null
      afplay /System/Library/Sounds/Glass.aiff 2>/dev/null &
      touch "$NOTIFICADO"
    fi
    rm -f "$RESET_FILE"
  fi
fi

exit 0
