#!/bin/bash
# Hook UserPromptSubmit: Salva transcrição automaticamente a cada 15 mensagens
#
# COMO FUNCIONA:
# 1. Mantém contador em /tmp/claude-msg-counter-[SESSION_ID]
# 2. A cada 15 mensagens, converte o JSONL da sessão em TXT legível
# 3. Copia para a pasta da sessão em Projetos - Plan Mode
# 4. Informa o usuário via stdout

INPUT=$(cat)

# Extrai session_id
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // .sessionId // empty' 2>/dev/null)
if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
    exit 0
fi

COUNTER_FILE="/tmp/claude-msg-counter-${SESSION_ID}"
INTERVALO=15

# Incrementa contador
if [ -f "$COUNTER_FILE" ]; then
    CONTAGEM=$(cat "$COUNTER_FILE")
    CONTAGEM=$((CONTAGEM + 1))
else
    CONTAGEM=1
fi
echo "$CONTAGEM" > "$COUNTER_FILE"

# Verifica se atingiu o intervalo
RESTO=$((CONTAGEM % INTERVALO))
if [ "$RESTO" -ne 0 ]; then
    exit 0
fi

# ========================================
# HORA DE SALVAR
# ========================================

CONVERSOR="$HOME/stemmia-forense/src/utilidades/converter_sessoes_jsonl.py"
JSONL_ORIGINAL="$HOME/.claude/projects/-Users-$(whoami)/${SESSION_ID}.jsonl"
PLAN_MODE_DIR="$HOME/Desktop/Projetos - Plan Mode"
SESSAO_DIR="$PLAN_MODE_DIR/Registros Sessões"

# Verifica se os recursos existem
if [ ! -f "$CONVERSOR" ]; then
    exit 0
fi

if [ ! -f "$JSONL_ORIGINAL" ]; then
    exit 0
fi

mkdir -p "$SESSAO_DIR"

# Converte JSONL → TXT
SAIDA_TEMP="/tmp/claude-autosave-${SESSION_ID}"
mkdir -p "$SAIDA_TEMP"

python3 "$CONVERSOR" --jsonl-file "$JSONL_ORIGINAL" --saida "$SAIDA_TEMP" 2>/dev/null

# Copia para pasta de sessões
GERADO=$(ls -t "$SAIDA_TEMP"/SESSAO-*.txt 2>/dev/null | head -1)
if [ -n "$GERADO" ] && [ -f "$GERADO" ]; then
    NOME_BASE=$(basename "$GERADO")
    cp "$GERADO" "$SESSAO_DIR/$NOME_BASE"
    TAMANHO=$(wc -l < "$GERADO" | tr -d ' ')
    echo "[AUTO-SAVE] Transcrição salva ($CONTAGEM mensagens, $TAMANHO linhas). Arquivo: $SESSAO_DIR/$NOME_BASE"
fi

exit 0
