#!/bin/bash
# Hook: UserPromptSubmit — lembra de renomear na 2ª mensagem da sessão
# Detecta se é a 2ª interação e sugere /rename

SESSION_DIR="$HOME/.claude/projects/-Users-jesusnoleto"
PROMPT="${CLAUDE_USER_PROMPT:-}"

# Arquivo marcador da sessão atual (criado pelo SessionStart ou na 1ª execução)
MARKER="/tmp/claude-rename-marker-$$"

# Buscar o JSONL mais recente (sessão atual)
SESSION_FILE=$(ls -t "$SESSION_DIR"/*.jsonl 2>/dev/null | head -1)
[ -z "$SESSION_FILE" ] && exit 0

# Contar mensagens do tipo "human" no JSONL
MSG_COUNT=$(grep -c '"type":"human"' "$SESSION_FILE" 2>/dev/null || echo 0)

# Na 2ª mensagem do usuário, sugerir /rename
if [ "$MSG_COUNT" -eq 2 ]; then
    # Verificar se já tem nome customizado (slug diferente do padrão adjective-noun-animal)
    SLUG=$(grep -o '"slug":"[^"]*"' "$SESSION_FILE" 2>/dev/null | head -1 | sed 's/"slug":"//;s/"//')

    # Padrão típico: word-word-word (3 palavras com hífen)
    if echo "$SLUG" | grep -qE '^[a-z]+-[a-z]+-[a-z]+$'; then
        echo "Dica: use /rename para dar um nome descritivo a esta sessão (atual: $SLUG)"
    fi
fi
