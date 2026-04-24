#!/bin/bash
# ============================================================
# HOOK: Corretor de Ditado por Voz — UserPromptSubmit
# Sistema Stemmia Forense v8.0
# ============================================================
# Detecta erros comuns de ditado e injeta NOTA DE CONTEXTO
# para o Claude interpretar corretamente.
# NÃO modifica o prompt — apenas adiciona orientação.
# ============================================================
# Entrada: $CLAUDE_USER_PROMPT (variável de ambiente)
# Saída: stdout (nota de contexto, se houver correções)
# Log: ~/stemmia-forense/logs/ditado.log
# Config: ~/stemmia-forense/config/dicionario-ditado.conf
# ============================================================

INPUT="${CLAUDE_USER_PROMPT:-}"
[ -z "$INPUT" ] && exit 0

CONF_FILE="$HOME/stemmia-forense/config/dicionario-ditado.conf"
LOG_FILE="$HOME/stemmia-forense/logs/ditado.log"

[ ! -f "$CONF_FILE" ] && exit 0

# Coletar todas as correções encontradas (sem duplicatas)
CORRECOES=""
CONTAGEM=0
JA_CORRIGIDOS=""

while IFS=$'\t' read -r REGEX CORRECAO CATEGORIA; do
    # Ignorar linhas vazias, comentários e categoria OK
    [ -z "$REGEX" ] && continue
    [[ "$REGEX" =~ ^# ]] && continue
    [ "$CATEGORIA" = "OK" ] && continue

    # Testar se o regex bate com o input (case-insensitive)
    if echo "$INPUT" | grep -iqE "$REGEX" 2>/dev/null; then
        # Extrair a palavra encontrada
        ENCONTRADA=$(echo "$INPUT" | grep -ioE "$REGEX" 2>/dev/null | head -1)
        if [ -n "$ENCONTRADA" ] && [ "$ENCONTRADA" != "$CORRECAO" ]; then
            # Evitar duplicatas (mesma palavra já corrigida)
            CHAVE="${ENCONTRADA}→${CORRECAO}"
            if echo "$JA_CORRIGIDOS" | grep -qF "$CHAVE"; then
                continue
            fi
            JA_CORRIGIDOS="${JA_CORRIGIDOS}|${CHAVE}"

            CORRECOES="${CORRECOES}  - \"${ENCONTRADA}\" → provavelmente \"${CORRECAO}\" [${CATEGORIA}]\n"
            CONTAGEM=$((CONTAGEM + 1))

            # Registrar no log
            echo "$(date '+%Y-%m-%d %H:%M:%S') | ${CATEGORIA} | \"${ENCONTRADA}\" → \"${CORRECAO}\" | Prompt: ${INPUT:0:80}..." >> "$LOG_FILE" 2>/dev/null
        fi
    fi
done < "$CONF_FILE"

# Se houve correções, emitir nota de contexto
if [ $CONTAGEM -gt 0 ]; then
    echo ""
    echo "NOTA DE DITADO (${CONTAGEM} correção(ões) sugeridas):"
    echo -e "$CORRECOES"
    echo "O usuário usa ditado por voz. Interprete o texto com essas correções em mente."
    echo ""
fi

exit 0
