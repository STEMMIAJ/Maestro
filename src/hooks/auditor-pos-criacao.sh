#!/bin/bash
# auditor-pos-criacao.sh — Hook PostToolUse (Write)
# Detecta criação de novo agente ou skill e sugere auditar

# Ler JSON do tool use via stdin
INPUT=$(cat)

# Extrair caminho do arquivo
ARQUIVO=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$ARQUIVO" ] && exit 0

NOME=$(basename "$ARQUIVO")

# Verificar se é agente ou skill
case "$ARQUIVO" in
    */.claude/agents/*.md)
        echo ""
        echo "╔═══════════════════════════════════════════════════╗"
        echo "║  NOVO AGENTE DETECTADO: $NOME"
        echo "║  → Diga: 'audita a estrutura dos meus agentes'    ║"
        echo "║    para verificar se está correto e completo.     ║"
        echo "╚═══════════════════════════════════════════════════╝"
        echo ""
        ;;
    */stemmia-forense/skills/*/SKILL.md)
        echo ""
        echo "╔═══════════════════════════════════════════════════╗"
        echo "║  NOVA SKILL DETECTADA: $NOME"
        echo "║  → Diga: 'audita a estrutura dos meus agentes'    ║"
        echo "║    para verificar se está correta e completa.     ║"
        echo "╚═══════════════════════════════════════════════════╝"
        echo ""
        ;;
esac

exit 0
