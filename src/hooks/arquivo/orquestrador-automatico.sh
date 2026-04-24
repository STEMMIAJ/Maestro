#!/bin/bash
# ===========================================================================
# ORQUESTRADOR AUTOMÁTICO — Hook UserPromptSubmit
# ===========================================================================
# Detecta a intenção do usuário por regex e injeta instrução no contexto
# do Claude ANTES do modelo processar a mensagem.
#
# Substitui e absorve o antigo verificar-inbox-pericia.sh.
#
# Variável de ambiente: CLAUDE_USER_PROMPT (texto do usuário)
# Saída stdout: instruções para o Claude (ou vazio se nada detectado)
# Exit code: sempre 0 (nunca bloqueia)
# ===========================================================================

# Configuração
REPO_DIR="$HOME/stemmia-forense"
CONF_FILE="$REPO_DIR/config/orquestrador-padroes.conf"
INBOX="$HOME/stemmia-forense/INBOX"

# Captura do prompt
INPUT="${CLAUDE_USER_PROMPT:-}"

# Sem prompt ou sem config → sai silencioso
[ -z "$INPUT" ] && exit 0
[ ! -f "$CONF_FILE" ] && exit 0

# Armazena matches: "PRIORIDADE|SKILL_KEY|INSTRUÇÃO"
MATCHES=""
SEEN_SKILLS=""

while IFS=$'\t' read -r PRIO CATEG ACAO REGEX INSTRUCAO; do
    # Ignora linhas vazias e comentários
    [ -z "$PRIO" ] && continue
    case "$PRIO" in \#*) continue ;; esac

    # Testa regex contra o prompt (case-insensitive)
    if echo "$INPUT" | grep -iqE "$REGEX" 2>/dev/null; then
        # Deduplica: se a mesma ação já foi detectada, pula
        SKILL_KEY="$ACAO"
        case "$SEEN_SKILLS" in
            *"$SKILL_KEY"*) continue ;;
        esac
        SEEN_SKILLS="$SEEN_SKILLS|$SKILL_KEY"
        MATCHES="${MATCHES}${PRIO}|${INSTRUCAO}"$'\n'
    fi
done < "$CONF_FILE"

# Verificação da INBOX (se detectou nomeação ou análise)
if echo "$SEEN_SKILLS" | grep -q "skill:nomeacao\|skill:analisar"; then
    if [ -d "$INBOX" ]; then
        PDF_COUNT=$(find "$INBOX" -maxdepth 1 \( -name "*.pdf" -o -name "*.PDF" \) 2>/dev/null | wc -l | tr -d ' ')
        if [ "$PDF_COUNT" -eq 0 ]; then
            MATCHES="${MATCHES}9|INBOX VAZIA: Nenhum PDF encontrado em $INBOX. O usuário precisa colocar o PDF lá antes da análise."$'\n'
        else
            PDF_NAMES=$(find "$INBOX" -maxdepth 1 \( -name "*.pdf" -o -name "*.PDF" \) -exec basename {} \; 2>/dev/null | head -5 | tr '\n' ', ' | sed 's/,$//')
            MATCHES="${MATCHES}9|INBOX: ${PDF_COUNT} PDF(s) encontrado(s): ${PDF_NAMES}"$'\n'
        fi
    fi
fi

# Se nenhum match, sai silencioso
CLEAN=$(echo "$MATCHES" | tr -d '[:space:]')
[ -z "$CLEAN" ] && exit 0

# Ordena por prioridade e imprime
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ORQUESTRADOR AUTOMÁTICO — DETECÇÕES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "$MATCHES" | sort -t'|' -k1,1n | while IFS='|' read -r PRIO INSTRUCAO; do
    [ -z "$INSTRUCAO" ] && continue
    echo ""
    echo "  $INSTRUCAO"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

exit 0
