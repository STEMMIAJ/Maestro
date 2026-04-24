#!/bin/bash
# HOOK: Bloqueia QUALQUER comando de deleção sem dupla confirmação
# Tipo: PreToolUse (Bash)
# Intercepta: rm, trash, unlink, find -delete, rmdir com conteúdo

TOOL_INPUT="${CLAUDE_TOOL_INPUT:-}"

# Extrair o comando do JSON
COMANDO=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('command',''))" 2>/dev/null || echo "$TOOL_INPUT")

# Padrões de deleção
if echo "$COMANDO" | grep -qiE '^\s*rm\s|[;&|]\s*rm\s|^\s*trash\s|[;&|]\s*trash\s|^\s*unlink\s|-delete|^\s*rmdir\s'; then
    # Verificar se é limpeza inofensiva (lock files, .DS_Store, Thumbs.db)
    LIXO_SEGURO=false
    if echo "$COMANDO" | grep -qE '~\$|\.DS_Store|Thumbs\.db'; then
        # Mesmo lixo seguro: BLOQUEIA e avisa
        echo "BLOQUEADO: Comando de deleção detectado." >&2
        echo "" >&2
        echo "Comando: $COMANDO" >&2
        echo "" >&2
        echo "REGRA: NUNCA deletar sem dupla confirmação do usuário." >&2
        echo "Ação: Pergunte ao usuário DUAS VEZES antes de deletar." >&2
        echo "1ª vez: Liste os arquivos que serão deletados" >&2
        echo "2ª vez: Peça confirmação explícita ('sim, pode deletar')" >&2
        exit 1
    fi

    echo "BLOQUEADO: Comando de deleção detectado." >&2
    echo "" >&2
    echo "Comando: $COMANDO" >&2
    echo "" >&2
    echo "REGRA ABSOLUTA: NUNCA deletar arquivos sem DUPLA CONFIRMAÇÃO." >&2
    echo "" >&2
    echo "Protocolo obrigatório:" >&2
    echo "1. LISTAR todos os arquivos que seriam deletados" >&2
    echo "2. PERGUNTAR ao usuário: 'Posso deletar estes X arquivos?'" >&2
    echo "3. ESPERAR resposta explícita do usuário" >&2
    echo "4. PERGUNTAR DE NOVO: 'Confirma a deleção de X arquivos? Isso é irreversível.'" >&2
    echo "5. SÓ ENTÃO executar" >&2
    exit 1
fi

# Não é comando de deleção — passa
exit 0
