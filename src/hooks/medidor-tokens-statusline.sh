#!/bin/bash
# medidor-tokens-statusline.sh — StatusLine command
# Exibe % de uso do contexto na barra de status do Claude Code
# Recebe JSON via stdin com context_window data

INPUT=$(cat)

# Extrair percentuais
USED=$(echo "$INPUT" | jq -r '.context_window.used_percentage // 0' 2>/dev/null | awk '{printf "%.0f", $1}')
REMAINING=$(echo "$INPUT" | jq -r '.context_window.remaining_percentage // 100' 2>/dev/null | awk '{printf "%.0f", $1}')

# Fallback se jq falhar
[ -z "$USED" ] || [ "$USED" = "null" ] && USED=0
[ -z "$REMAINING" ] || [ "$REMAINING" = "null" ] && REMAINING=100

# Indicador visual baseado no percentual usado
if [ "$USED" -ge 80 ]; then
    ICON="[CRITICO]"
elif [ "$USED" -ge 60 ]; then
    ICON="[ALERTA]"
elif [ "$USED" -ge 40 ]; then
    ICON="[MEDIO]"
else
    ICON="[OK]"
fi

# Barra visual (10 blocos)
BLOCOS=$((USED / 10))
BARRA=""
for i in $(seq 1 $BLOCOS); do BARRA="${BARRA}█"; done
for i in $(seq $((BLOCOS+1)) 10); do BARRA="${BARRA}░"; done

# Estimativa de turnos restantes (~5% por turno médio)
TURNOS_REST=$(( (100 - USED) / 5 ))
[ "$TURNOS_REST" -lt 0 ] && TURNOS_REST=0

echo "ctx: ${BARRA} ${USED}% ${ICON} ~${TURNOS_REST} turnos"
