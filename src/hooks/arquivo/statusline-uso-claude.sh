#!/bin/bash
# statusline-uso-claude.sh — StatusLine multi-janela para Claude Code
# Mostra: ctx | blk | dia | sem em 1 linha compacta
# Criado em 07/03/2026

export LC_NUMERIC=C

# === Ler contexto da sessão via stdin ===
INPUT=$(cat)

CTX_PCT=$(echo "$INPUT" | jq -r '.context_window.used_percentage // 0' 2>/dev/null | awk '{printf "%.0f", $1}')
[ -z "$CTX_PCT" ] || [ "$CTX_PCT" = "null" ] && CTX_PCT=0

# === Ler cache do monitor (atualizado pelo hook Stop) ===
STATE_FILE="/tmp/claude-uso-state.json"

if [ -f "$STATE_FILE" ]; then
    STATE=$(cat "$STATE_FILE")
    BLOCO_PCT=$(echo "$STATE" | jq -r '.bloco_pct // 0' 2>/dev/null)
    BLOCO_CUSTO=$(echo "$STATE" | jq -r '.bloco_custo // 0' 2>/dev/null)
    BLOCO_REST=$(echo "$STATE" | jq -r '.bloco_restante_min // 0' 2>/dev/null)
    DIA_CUSTO=$(echo "$STATE" | jq -r '.dia_custo // 0' 2>/dev/null)
    SEMANA_CUSTO=$(echo "$STATE" | jq -r '.semana_custo // 0' 2>/dev/null)
    MEDIA_SEMANAL=$(echo "$STATE" | jq -r '.media_semanal // 0' 2>/dev/null)
else
    # Fallback: buscar dados frescos (1ª execução)
    CCUSAGE="/opt/homebrew/bin/ccusage"
    if [ -x "$CCUSAGE" ]; then
        BLOCO_JSON=$("$CCUSAGE" blocks --json --offline 2>/dev/null || echo '{"blocks":[]}')
        BLOCO_ATIVO=$(echo "$BLOCO_JSON" | jq '[.blocks[] | select(.isActive == true and .isGap != true)] | if length > 0 then .[-1] else null end' 2>/dev/null)

        if [ "$BLOCO_ATIVO" != "null" ] && [ -n "$BLOCO_ATIVO" ]; then
            BLOCO_CUSTO=$(echo "$BLOCO_ATIVO" | jq -r '.costUSD // 0')
            BLOCO_REST=$(echo "$BLOCO_ATIVO" | jq -r '.projection.remainingMinutes // 0')
            BLOCO_PROJ_CUSTO=$(echo "$BLOCO_ATIVO" | jq -r '.projection.totalCost // 0')
            if [ "$BLOCO_PROJ_CUSTO" != "0" ] && [ "$BLOCO_PROJ_CUSTO" != "null" ]; then
                BLOCO_PCT=$(echo "$BLOCO_CUSTO $BLOCO_PROJ_CUSTO" | awk '{if($2>0) printf "%.0f", ($1/$2)*100; else print 0}')
            else
                BLOCO_PCT=0
            fi
        else
            BLOCO_PCT=0; BLOCO_CUSTO=0; BLOCO_REST=0
        fi

        HOJE=$(date +%Y-%m-%d)
        DIA_CUSTO=$("$CCUSAGE" daily --json --offline 2>/dev/null | jq --arg hoje "$HOJE" '[.daily[] | select(.date == $hoje)] | if length > 0 then .[-1].totalCost else 0 end' 2>/dev/null || echo 0)
        [ "$DIA_CUSTO" = "null" ] && DIA_CUSTO=0

        SEMANA_CUSTO=$("$CCUSAGE" weekly --json --offline 2>/dev/null | jq '[.weekly[]] | if length > 0 then .[-1].totalCost else 0 end' 2>/dev/null || echo 0)
        [ "$SEMANA_CUSTO" = "null" ] && SEMANA_CUSTO=0
        MEDIA_SEMANAL=500
    else
        BLOCO_PCT=0; BLOCO_CUSTO=0; BLOCO_REST=0; DIA_CUSTO=0; SEMANA_CUSTO=0; MEDIA_SEMANAL=0
    fi
fi

# === Sanitizar valores ===
[ -z "$BLOCO_PCT" ] || [ "$BLOCO_PCT" = "null" ] && BLOCO_PCT=0
[ -z "$BLOCO_CUSTO" ] || [ "$BLOCO_CUSTO" = "null" ] && BLOCO_CUSTO=0
[ -z "$BLOCO_REST" ] || [ "$BLOCO_REST" = "null" ] && BLOCO_REST=0
[ -z "$DIA_CUSTO" ] || [ "$DIA_CUSTO" = "null" ] && DIA_CUSTO=0
[ -z "$SEMANA_CUSTO" ] || [ "$SEMANA_CUSTO" = "null" ] && SEMANA_CUSTO=0
[ -z "$MEDIA_SEMANAL" ] || [ "$MEDIA_SEMANAL" = "null" ] && MEDIA_SEMANAL=0

# === Formatar valores ===
DIA_FMT=$(printf '%.0f' "$DIA_CUSTO" 2>/dev/null || echo "0")
SEMANA_FMT=$(printf '%.0f' "$SEMANA_CUSTO" 2>/dev/null || echo "0")
MEDIA_FMT=$(printf '%.0f' "$MEDIA_SEMANAL" 2>/dev/null || echo "0")
BLOCO_REST_FMT=$(printf '%.0f' "$BLOCO_REST" 2>/dev/null || echo "0")

# === Montar linha ===
# ctx:52% | blk:34%~88m | dia:$78 | sem:$312/483
echo "ctx:${CTX_PCT}% | blk:${BLOCO_PCT}%~${BLOCO_REST_FMT}m | dia:\$${DIA_FMT} | sem:\$${SEMANA_FMT}/${MEDIA_FMT}"
