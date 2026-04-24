#!/bin/bash
# adaptador-sessao.sh — Hook UserPromptSubmit
# Lê o estado gravado pelo hook Stop e injeta aviso se necessário.
# Tempo alvo: ~100ms (sem chamadas externas)

STATE_FILE="/tmp/adaptador-sessao-state.json"

# Se não existe estado ainda (primeira mensagem da sessão), sair silencioso
if [[ ! -f "$STATE_FILE" ]]; then
    exit 0
fi

# Ler estado com Python (mais robusto que jq para nosso caso)
read -r ALERT_LEVEL LAST_SHOWN BLOCK_PCT CONTEXT_PCT BLOCK_COST BLOCK_REMAINING NEXT_COST BLOCK_LIMIT BLOCK_TOTAL BURN_RATE BLOCK_PROJ_PCT < <(python3 -c "
import json
try:
    with open('$STATE_FILE') as f:
        d = json.load(f)
    alert = d['prediction']['alert_level']
    last = d.get('last_alert_shown', 'silencio')
    bpct = d['block']['percent']
    cpct = d['context']['percent']
    bcost = d['block']['cost_usd']
    brem = d['block']['remaining_minutes']
    ncost = d['prediction']['next_turn_cost_usd']
    blimit = d['block']['limit']
    btotal = d['block']['total_tokens']
    burn = d['block']['burn_rate_tpm']
    bproj = d['block'].get('projected_percent', 0)
    print(f'{alert} {last} {bpct:.1f} {cpct:.1f} {bcost:.2f} {brem} {ncost:.4f} {blimit} {btotal} {burn:.0f} {bproj:.1f}')
except Exception as e:
    print('silencio silencio 0 0 0 0 0 0 0 0 0')
" 2>/dev/null || echo "silencio silencio 0 0 0 0 0 0 0 0 0")

# Mapa de hierarquia: silencio < medio < alto < critico
level_to_num() {
    case "$1" in
        silencio) echo 0 ;;
        medio)    echo 1 ;;
        alto)     echo 2 ;;
        critico)  echo 3 ;;
        *)        echo 0 ;;
    esac
}

CURRENT_NUM=$(level_to_num "$ALERT_LEVEL")
LAST_NUM=$(level_to_num "$LAST_SHOWN")

# Só mostrar se ESCALOU (nunca repete mesmo nível)
if [[ $CURRENT_NUM -le $LAST_NUM ]] && [[ $CURRENT_NUM -lt 3 ]]; then
    # Não escalou e não é crítico — sair silencioso
    # Exceção: crítico SEMPRE mostra
    exit 0
fi

# Se é silêncio, nunca mostrar nada
if [[ "$ALERT_LEVEL" == "silencio" ]]; then
    exit 0
fi

# Atualizar last_alert_shown no state file
python3 -c "
import json
try:
    with open('$STATE_FILE') as f:
        d = json.load(f)
    d['last_alert_shown'] = '$ALERT_LEVEL'
    with open('$STATE_FILE', 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
except:
    pass
" 2>/dev/null

# Formatar números para exibição
BLOCK_PCT_INT=${BLOCK_PCT%.*}
CONTEXT_PCT_INT=${CONTEXT_PCT%.*}
REMAINING_H=$((BLOCK_REMAINING / 60))
REMAINING_M=$((BLOCK_REMAINING % 60))

# Converter tokens para formato legível
BLOCK_TOTAL_M=$(python3 -c "print(f'{$BLOCK_TOTAL/1_000_000:.1f}')" 2>/dev/null || echo "?")
BLOCK_LIMIT_M=$(python3 -c "print(f'{$BLOCK_LIMIT/1_000_000:.0f}')" 2>/dev/null || echo "?")
BLOCK_PROJ_INT=${BLOCK_PROJ_PCT%.*}

# ── Gerar aviso conforme nível ──

case "$ALERT_LEVEL" in
    medio)
        cat <<EOF
<system-reminder>
━━━ ADAPTADOR DE SESSÃO ━━━━━━━━━━━━━━━━━━━━━━
 Bloco: ${BLOCK_PCT_INT}% usado (${BLOCK_TOTAL_M}M / ${BLOCK_LIMIT_M}M tokens)
 Projeção 5h: ${BLOCK_PROJ_INT}% | Contexto: ${CONTEXT_PCT_INT}%
 Custo estimado próximo turno: \$${NEXT_COST}
 Tempo restante no bloco: ${REMAINING_H}h${REMAINING_M}min
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Sugestão: respostas mais curtas ou trocar para Sonnet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
</system-reminder>
EOF
        ;;
    alto)
        cat <<EOF
<system-reminder>
⚠️ ━━━ ADAPTADOR DE SESSÃO — ALERTA ALTO ━━━━━━
 Bloco: ${BLOCK_PCT_INT}% usado (${BLOCK_TOTAL_M}M / ${BLOCK_LIMIT_M}M tokens)
 Projeção 5h: ${BLOCK_PROJ_INT}% | Contexto: ${CONTEXT_PCT_INT}%
 Custo estimado próximo turno: \$${NEXT_COST}
 Tempo restante no bloco: ${REMAINING_H}h${REMAINING_M}min

 AÇÕES RECOMENDADAS:
  1. /compact — compactar contexto
  2. Trocar para Sonnet (mais barato)
  3. /clear — nova sessão limpa
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
</system-reminder>
EOF
        ;;
    critico)
        cat <<EOF
<system-reminder>
🔴 ━━━ ADAPTADOR DE SESSÃO — CRÍTICO ━━━━━━━━━━
 Bloco: ${BLOCK_PCT_INT}% usado (${BLOCK_TOTAL_M}M / ${BLOCK_LIMIT_M}M tokens)
 Projeção 5h: ${BLOCK_PROJ_INT}% | Contexto: ${CONTEXT_PCT_INT}%
 Custo estimado próximo turno: \$${NEXT_COST}
 Bloqueio por limite pode acontecer A QUALQUER MOMENTO.

 AÇÃO OBRIGATÓRIA — escolha uma:
  1. /clear — encerrar sessão e começar limpa
  2. Trocar para Sonnet AGORA
  3. /compact + respostas mínimas

 O Claude DEVE dar respostas CURTAS a partir de agora.
 NÃO expandir explicações. NÃO criar arquivos grandes.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
</system-reminder>
EOF
        ;;
esac

exit 0
