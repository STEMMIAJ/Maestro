#!/bin/bash
# ══════════════════════════════════════════════════════════════
# DETECTOR DE ESFORÇO BAIXO DO CLAUDE
# Hook Stop — analisa a última resposta do Claude e detecta
# sinais de que o nível de esforço caiu.
#
# Sinais detectados:
# 1. Resposta muito curta (< MIN_RESPOSTA_CHARS)
# 2. Excesso de frases genéricas/preguiçosas
# 3. Ausência de palavras de análise real
# 4. Padrões de "resposta automática" sem reflexão
#
# Saída: alerta sonoro + log + feedback ao Claude (via decision block)
# ══════════════════════════════════════════════════════════════

CONFIG_FILE="$HOME/stemmia-forense/config/LIMITES-ESFORCO.conf"

# Carregar configuração
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
else
    # Defaults se config não existir
    MIN_RESPOSTA_CHARS=200
    MAX_FRASES_GENERICAS=3
    PALAVRAS_ANALISE="analisei|verifiquei|encontrei|identifiquei|detectei|observei"
    FRASES_GENERICAS="conforme solicitado|como mencionado|como discutido|conforme descrito|como explicado|já mencionado|como dito|por favor me avise|espero ter ajudado|fico à disposição|qualquer dúvida"
    SOM_ALERTA="/System/Library/Sounds/Sosumi.aiff"
    LOG_FILE="/tmp/claude-esforco-baixo.log"
    ATIVO=true
fi

# Se desativado, sair
if [[ "$ATIVO" != "true" ]]; then
    exit 0
fi

# Ler input JSON do stdin
INPUT=$(cat)

# Verificar se já estamos em loop de stop hook
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [[ "$STOP_HOOK_ACTIVE" == "true" ]]; then
    exit 0
fi

# Extrair a última mensagem do assistente
LAST_MSG=$(echo "$INPUT" | jq -r '.last_assistant_message // ""')

# Se não há mensagem, sair silenciosamente
if [[ -z "$LAST_MSG" || "$LAST_MSG" == "null" ]]; then
    exit 0
fi

# ── ANÁLISE ──────────────────────────────────────────────────

ALERTAS=""
SCORE=0

# 1. Tamanho da resposta
TAMANHO=${#LAST_MSG}
if [[ $TAMANHO -lt $MIN_RESPOSTA_CHARS ]]; then
    # Exceção: respostas curtas legítimas (confirmações, ok, sim/não, ou respostas < 100 chars)
    if [[ $TAMANHO -lt 100 ]]; then
        : # Respostas muito curtas são quase sempre legítimas — não penalizar
    elif ! echo "$LAST_MSG" | grep -qiE "^(ok|sim|não|pronto|feito|certo|entendido|pode ser|beleza|combinado)[.!]?$"; then
        ALERTAS="${ALERTAS}CURTA ($TAMANHO chars) | "
        SCORE=$((SCORE + 2))
    fi
fi

# 2. Contagem de frases genéricas
CONTAGEM_GENERICAS=$(echo "$LAST_MSG" | grep -oiE "$FRASES_GENERICAS" | wc -l | tr -d ' ')
if [[ $CONTAGEM_GENERICAS -gt $MAX_FRASES_GENERICAS ]]; then
    ALERTAS="${ALERTAS}GENÉRICA ($CONTAGEM_GENERICAS frases) | "
    SCORE=$((SCORE + 2))
fi

# 3. Ausência de palavras de análise (só se resposta > 500 chars, pra não pegar respostas simples)
if [[ $TAMANHO -gt 500 ]]; then
    TEM_ANALISE=$(echo "$LAST_MSG" | grep -ciE "$PALAVRAS_ANALISE")
    if [[ $TEM_ANALISE -eq 0 ]]; then
        ALERTAS="${ALERTAS}SEM ANÁLISE | "
        SCORE=$((SCORE + 1))
    fi
fi

# 4. Padrões de resposta "copiada" (boilerplate)
BOILERPLATE_PATTERNS="Here is|Here's a|I'll help you|I can help|Let me help|Sure, I|Of course|Certainly|Absolutely"
CONTAGEM_BOILERPLATE=$(echo "$LAST_MSG" | grep -oiE "$BOILERPLATE_PATTERNS" | wc -l | tr -d ' ')
if [[ $CONTAGEM_BOILERPLATE -gt 2 ]]; then
    ALERTAS="${ALERTAS}BOILERPLATE ($CONTAGEM_BOILERPLATE) | "
    SCORE=$((SCORE + 1))
fi

# 5. REMOVIDO — critério "SEM REFERÊNCIAS" gerava falsos positivos em análises textuais válidas
# Respostas em prosa (relatórios, explicações) não precisam ter referências a arquivos

# ── DECISÃO ──────────────────────────────────────────────────

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

if [[ $SCORE -ge 4 ]]; then
    # ALERTA ALTO — esforço provavelmente baixo (SIMPLIFICADO: apenas log + notificação, sem decision block)
    echo "[$TIMESTAMP] ⚠️  ESFORÇO BAIXO (score=$SCORE): $ALERTAS" >> "$LOG_FILE"

    # Alerta sonoro
    afplay "$SOM_ALERTA" &

    # Notificação macOS
    osascript -e "display notification \"Esforço baixo detectado (score $SCORE): ${ALERTAS}\" with title \"⚠️ Claude - Esforço Baixo\" sound name \"Sosumi\"" 2>/dev/null &

    exit 0

elif [[ $SCORE -ge 2 ]]; then
    # ALERTA MÉDIO — suspeita, mas não bloqueia
    echo "[$TIMESTAMP] ⚡ ESFORÇO MÉDIO (score=$SCORE): $ALERTAS" >> "$LOG_FILE"

    # Apenas log + som suave, não bloqueia
    afplay "/System/Library/Sounds/Tink.aiff" &

    exit 0

else
    # OK — esforço adequado
    exit 0
fi
