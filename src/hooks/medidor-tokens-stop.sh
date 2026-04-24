#!/bin/bash
# medidor-tokens-stop.sh — Hook Stop
# Notifica quando uso de contexto cruza limiares de 10%
# Salva histórico em log para análise posterior

STATE_FILE="$HOME/.claude/.token-state.json"
LOG_FILE="$HOME/stemmia-forense/hooks/token-usage.log"

INPUT=$(cat)

# Anti-loop: se stop_hook_active, sair
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null)
[ "$STOP_HOOK_ACTIVE" = "true" ] && exit 0

# Extrair dados de contexto
USED_PCT=$(echo "$INPUT" | jq -r '.context_window.used_percentage // 0' 2>/dev/null | awk '{printf "%.0f", $1}')
INPUT_TOKENS=$(echo "$INPUT" | jq -r '.context_window.input_tokens // 0' 2>/dev/null)
CTX_SIZE=$(echo "$INPUT" | jq -r '.context_window.context_window_size // 200000' 2>/dev/null)

# Se não conseguiu dados, sair silenciosamente
[ -z "$USED_PCT" ] || [ "$USED_PCT" = "null" ] || [ "$USED_PCT" = "0" ] && exit 0

# Ler último limiar notificado
LAST_THRESHOLD=0
if [ -f "$STATE_FILE" ]; then
    LAST_THRESHOLD=$(jq -r '.last_threshold // 0' "$STATE_FILE" 2>/dev/null || echo 0)
fi

# Calcular limiar atual (múltiplo de 10)
CURRENT_THRESHOLD=$(( (USED_PCT / 10) * 10 ))

# Só notifica se cruzou novo limiar de 10%
if [ "$CURRENT_THRESHOLD" -gt "$LAST_THRESHOLD" ] && [ "$CURRENT_THRESHOLD" -gt 0 ]; then

    # Salvar estado
    jq -n \
        --argjson threshold "$CURRENT_THRESHOLD" \
        --argjson used "$USED_PCT" \
        --arg time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{last_threshold: $threshold, last_used: $used, last_updated: $time}' \
        > "$STATE_FILE" 2>/dev/null

    # Log para histórico
    echo "$(date '+%Y-%m-%d %H:%M') | ${USED_PCT}% usado | ${INPUT_TOKENS} tokens | ctx ${CTX_SIZE}" >> "$LOG_FILE" 2>/dev/null

    # Calcular restantes
    REMAINING=$((100 - USED_PCT))
    TURNOS_REST=$((REMAINING / 5))

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo " ALERTA DE CONTEXTO: ${USED_PCT}% utilizado"
    echo " Restando: ~${REMAINING}% (~${TURNOS_REST} turnos estimados)"
    if [ "$USED_PCT" -ge 80 ]; then
        echo " AÇÃO RECOMENDADA: Use /compact ou inicie nova sessão"
        afplay /System/Library/Sounds/Basso.aiff 2>/dev/null &
    elif [ "$USED_PCT" -ge 60 ]; then
        echo " AVISO: Contexto em uso moderado-alto"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

exit 0
