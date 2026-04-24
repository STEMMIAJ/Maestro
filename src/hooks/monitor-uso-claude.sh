#!/bin/bash
# monitor-uso-claude.sh — Hook Stop: monitora uso por janela temporal
# Consulta ccusage (blocks/daily/weekly) e alerta ao cruzar limiares
# Criado em 07/03/2026

set -euo pipefail
export LC_NUMERIC=C

# === Caminhos ===
CONFIG_DIR="$HOME/stemmia-forense/config"
LIMITES_CONF="$CONFIG_DIR/LIMITES-USO-CLAUDE.conf"
STATE_FILE="/tmp/claude-uso-state.json"
CCUSAGE="/opt/homebrew/bin/ccusage"

# === Verificações rápidas ===
[ ! -x "$CCUSAGE" ] && exit 0
[ ! -f "$LIMITES_CONF" ] && exit 0

# === Carregar configuração ===
source "$LIMITES_CONF"

# === Ler estado anterior ===
if [ -f "$STATE_FILE" ]; then
    STATE=$(cat "$STATE_FILE")
else
    STATE='{}'
fi

get_state() {
    echo "$STATE" | jq -r ".$1 // \"$2\"" 2>/dev/null || echo "$2"
}

ULTIMO_BLOCO_LIMIAR=$(get_state "ultimo_bloco_limiar" "0")
ULTIMO_DIA_LIMIAR=$(get_state "ultimo_dia_limiar" "0")
ULTIMA_SEMANA_LIMIAR=$(get_state "ultima_semana_limiar" "0")
ULTIMO_BLOCO_ID=$(get_state "ultimo_bloco_id" "")
ULTIMO_CHECK=$(get_state "ultimo_check" "0")

# === Anti-spam: não checar mais que 1x a cada 30s ===
NOW_EPOCH=$(date +%s)
if [ "$ULTIMO_CHECK" != "0" ]; then
    DIFF=$((NOW_EPOCH - ULTIMO_CHECK))
    [ "$DIFF" -lt 30 ] && exit 0
fi

# === Funções de notificação ===
notificar_aviso() {
    local MSG="$1"
    afplay "${SOM_AVISO}" &>/dev/null &
    echo "$MSG" >> /tmp/claude-uso-alertas.log
}

notificar_alerta() {
    local MSG="$1"
    afplay "${SOM_ALERTA}" &>/dev/null &
    osascript -e "display notification \"$MSG\" with title \"Claude — Alerta de Uso\"" &>/dev/null &
    echo "$MSG" >> /tmp/claude-uso-alertas.log
}

notificar_critico() {
    local MSG="$1"
    afplay "${SOM_CRITICO}" &>/dev/null &
    osascript -e "display notification \"$MSG\" with title \"Claude — USO CRÍTICO\" sound name \"Sosumi\"" &>/dev/null &
    echo "$MSG" >> /tmp/claude-uso-alertas.log
}

# === 1. BLOCO DE 5H ===
BLOCO_JSON=$("$CCUSAGE" blocks --json --offline 2>/dev/null || echo '{"blocks":[]}')
BLOCO_ATIVO=$(echo "$BLOCO_JSON" | jq '[.blocks[] | select(.isActive == true and .isGap != true)] | if length > 0 then .[-1] else null end' 2>/dev/null)

BLOCO_PCT=0
BLOCO_CUSTO=0
BLOCO_RESTANTE=0
BLOCO_ID=""

if [ "$BLOCO_ATIVO" != "null" ] && [ -n "$BLOCO_ATIVO" ]; then
    BLOCO_ID=$(echo "$BLOCO_ATIVO" | jq -r '.id // ""')
    BLOCO_CUSTO=$(echo "$BLOCO_ATIVO" | jq -r '.costUSD // 0')
    BLOCO_RESTANTE=$(echo "$BLOCO_ATIVO" | jq -r '.projection.remainingMinutes // 0')

    # Calcular % baseado em tokens usados vs projeção do limite
    BLOCO_TOKENS=$(echo "$BLOCO_ATIVO" | jq -r '.totalTokens // 0')
    BLOCO_PROJ_TOKENS=$(echo "$BLOCO_ATIVO" | jq -r '.projection.totalTokens // 0')

    if [ "$BLOCO_PROJ_TOKENS" != "0" ] && [ "$BLOCO_PROJ_TOKENS" != "null" ]; then
        # Estimar limite do bloco: projeção / (tempo restante / tempo total) * fator
        # Usar custo como proxy: custo atual / custo projetado * 100
        BLOCO_PROJ_CUSTO=$(echo "$BLOCO_ATIVO" | jq -r '.projection.totalCost // 0')
        if [ "$BLOCO_PROJ_CUSTO" != "0" ] && [ "$BLOCO_PROJ_CUSTO" != "null" ]; then
            BLOCO_PCT=$(echo "$BLOCO_CUSTO $BLOCO_PROJ_CUSTO" | awk '{if($2>0) printf "%.0f", ($1/$2)*100; else print 0}')
        fi
    fi

    # Se mudou de bloco, resetar limiares
    if [ "$BLOCO_ID" != "$ULTIMO_BLOCO_ID" ]; then
        ULTIMO_BLOCO_LIMIAR=0
    fi
fi

# === 2. DIÁRIO ===
HOJE=$(date +%Y-%m-%d)
DIA_JSON=$("$CCUSAGE" daily --json --offline 2>/dev/null || echo '{"daily":[]}')

DIA_CUSTO=$(echo "$DIA_JSON" | jq --arg hoje "$HOJE" '[.daily[] | select(.date == $hoje)] | if length > 0 then .[-1].totalCost else 0 end' 2>/dev/null || echo 0)
[ "$DIA_CUSTO" = "null" ] && DIA_CUSTO=0

# Média dos últimos 7 dias (excluindo hoje)
MEDIA_7D=$(echo "$DIA_JSON" | jq --arg hoje "$HOJE" '
    [.daily[] | select(.date != $hoje and .totalCost > 0)] | .[-7:] |
    if length > 0 then (map(.totalCost) | add / length) else 100 end
' 2>/dev/null || echo 100)
[ "$MEDIA_7D" = "null" ] && MEDIA_7D=100

DIA_PCT=$(echo "$DIA_CUSTO $MEDIA_7D" | awk '{if($2>0) printf "%.0f", ($1/$2)*100; else print 0}')

# === 3. SEMANAL ===
SEMANA_JSON=$("$CCUSAGE" weekly --json --offline 2>/dev/null || echo '{"weekly":[]}')

SEMANA_CUSTO=$(echo "$SEMANA_JSON" | jq '[.weekly[]] | if length > 0 then .[-1].totalCost else 0 end' 2>/dev/null || echo 0)
[ "$SEMANA_CUSTO" = "null" ] && SEMANA_CUSTO=0

# Média semanal (últimas 4 semanas completas, exceto a atual)
MEDIA_SEMANAL=$(echo "$SEMANA_JSON" | jq '
    [.weekly[]] | if length > 1 then .[0:-1] | .[-4:] |
    if length > 0 then (map(.totalCost) | add / length) else 500 end
    else 500 end
' 2>/dev/null || echo 500)
[ "$MEDIA_SEMANAL" = "null" ] && MEDIA_SEMANAL=500

SEMANA_PCT=$(echo "$SEMANA_CUSTO $MEDIA_SEMANAL" | awk '{if($2>0) printf "%.0f", ($1/$2)*100; else print 0}')

# === Dia da semana (para calcular % temporal da semana) ===
DIA_SEMANA=$(date +%u)  # 1=seg, 7=dom
SEMANA_TEMPORAL_PCT=$(echo "$DIA_SEMANA" | awk '{printf "%.0f", ($1/7)*100}')

# === 4. VERIFICAR LIMIARES E NOTIFICAR ===

# --- Bloco ---
if [ "$BLOCO_PCT" -ge "$BLOCO_CRITICO" ] && [ "$ULTIMO_BLOCO_LIMIAR" -lt "$BLOCO_CRITICO" ]; then
    notificar_critico "Bloco 5h: ${BLOCO_PCT}% usado. Restam ~${BLOCO_RESTANTE}min. Trocar modelo ou pausar."
    ULTIMO_BLOCO_LIMIAR=$BLOCO_CRITICO
elif [ "$BLOCO_PCT" -ge "$BLOCO_ALERTA" ] && [ "$ULTIMO_BLOCO_LIMIAR" -lt "$BLOCO_ALERTA" ]; then
    notificar_alerta "Bloco 5h: ${BLOCO_PCT}% usado. Considere trocar para Sonnet neste bloco."
    ULTIMO_BLOCO_LIMIAR=$BLOCO_ALERTA
elif [ "$BLOCO_PCT" -ge "$BLOCO_AVISO" ] && [ "$ULTIMO_BLOCO_LIMIAR" -lt "$BLOCO_AVISO" ]; then
    notificar_aviso "Bloco 5h: ${BLOCO_PCT}% usado. Custo: \$$(printf '%.2f' "$BLOCO_CUSTO")"
    ULTIMO_BLOCO_LIMIAR=$BLOCO_AVISO
fi

# --- Dia ---
if [ "$DIA_PCT" -ge "$DIA_CRITICO" ] && [ "$ULTIMO_DIA_LIMIAR" -lt "$DIA_CRITICO" ]; then
    notificar_critico "Dia muito pesado: \$$(printf '%.0f' "$DIA_CUSTO") (média: \$$(printf '%.0f' "$MEDIA_7D")). Considere pausar tarefas complexas."
    ULTIMO_DIA_LIMIAR=$DIA_CRITICO
elif [ "$DIA_PCT" -ge "$DIA_ALERTA" ] && [ "$ULTIMO_DIA_LIMIAR" -lt "$DIA_ALERTA" ]; then
    notificar_alerta "Dia acima da média: \$$(printf '%.0f' "$DIA_CUSTO") (média: \$$(printf '%.0f' "$MEDIA_7D"))"
    ULTIMO_DIA_LIMIAR=$DIA_ALERTA
elif [ "$DIA_PCT" -ge "$DIA_AVISO" ] && [ "$ULTIMO_DIA_LIMIAR" -lt "$DIA_AVISO" ]; then
    notificar_aviso "Uso diário: \$$(printf '%.0f' "$DIA_CUSTO") (${DIA_PCT}% da média)"
    ULTIMO_DIA_LIMIAR=$DIA_AVISO
fi

# --- Semana ---
if [ "$SEMANA_PCT" -ge "$SEMANA_CRITICO" ] && [ "$ULTIMA_SEMANA_LIMIAR" -lt "$SEMANA_CRITICO" ]; then
    notificar_critico "Quase no limite semanal: \$$(printf '%.0f' "$SEMANA_CUSTO") (média: \$$(printf '%.0f' "$MEDIA_SEMANAL")). Priorize urgências."
    ULTIMA_SEMANA_LIMIAR=$SEMANA_CRITICO
elif [ "$SEMANA_PCT" -ge "$SEMANA_ALERTA" ] && [ "$ULTIMA_SEMANA_LIMIAR" -lt "$SEMANA_ALERTA" ]; then
    notificar_alerta "Semana consumindo rápido: \$$(printf '%.0f' "$SEMANA_CUSTO") (${SEMANA_PCT}% da média semanal)"
    ULTIMA_SEMANA_LIMIAR=$SEMANA_ALERTA
elif [ "$SEMANA_PCT" -ge "$SEMANA_AVISO" ] && [ "$ULTIMA_SEMANA_LIMIAR" -lt "$SEMANA_AVISO" ]; then
    notificar_aviso "Uso semanal: \$$(printf '%.0f' "$SEMANA_CUSTO") (${SEMANA_PCT}% da média)"
    ULTIMA_SEMANA_LIMIAR=$SEMANA_AVISO
fi

# === 5. SALVAR ESTADO ===
cat > "$STATE_FILE" << EOJSON
{
  "ultimo_bloco_limiar": $ULTIMO_BLOCO_LIMIAR,
  "ultimo_dia_limiar": $ULTIMO_DIA_LIMIAR,
  "ultima_semana_limiar": $ULTIMA_SEMANA_LIMIAR,
  "ultimo_bloco_id": "$BLOCO_ID",
  "ultimo_check": $NOW_EPOCH,
  "bloco_pct": $BLOCO_PCT,
  "bloco_custo": $BLOCO_CUSTO,
  "bloco_restante_min": $BLOCO_RESTANTE,
  "dia_custo": $DIA_CUSTO,
  "dia_pct": $DIA_PCT,
  "media_diaria_7d": $MEDIA_7D,
  "semana_custo": $SEMANA_CUSTO,
  "semana_pct": $SEMANA_PCT,
  "media_semanal": $MEDIA_SEMANAL
}
EOJSON

exit 0
