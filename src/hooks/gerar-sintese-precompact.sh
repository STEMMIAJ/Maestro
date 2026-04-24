#!/bin/bash
# Script PreCompact SIMPLIFICADO: Lê dados já salvos pelo hook 17 (salvar-contexto-bruto.sh)
# e emite systemMessage resumido que sobrevive à compactação.
#
# ANTES: parseava o JSONL inteiro (duplicando hook 17). 284 linhas.
# AGORA: lê o CONTEXTO.txt já preenchido e emite resumo. ~60 linhas.
#
# Hook: PreCompact (roda JUNTO com salvar-contexto-bruto.sh)

PLAN_MODE_DIR="$HOME/Desktop/Projetos - Plan Mode"
SESSAO_ATUAL_FILE="$PLAN_MODE_DIR/.sessao_atual"

# Se não há sessão atual, sai
[ ! -f "$SESSAO_ATUAL_FILE" ] && exit 0

SESSAO_DIR=$(cat "$SESSAO_ATUAL_FILE")
[ ! -d "$SESSAO_DIR" ] && exit 0

CONTEXTO_FILE="$SESSAO_DIR/CONTEXTO.txt"
[ ! -f "$CONTEXTO_FILE" ] && exit 0

TIMESTAMP=$(date +"%Y-%m-%d %H:%M")

# Extrai mensagens do usuário do CONTEXTO.txt (já salvas pelo hook 17)
MENSAGENS_USUARIO=$(grep "USUÁRIO:" "$CONTEXTO_FILE" 2>/dev/null | head -5)

# Extrai arquivos criados (registrados pelo hook 11 - registrar-arquivo.sh)
ARQUIVOS=$(grep "^- [0-9]" "$CONTEXTO_FILE" 2>/dev/null | tail -20 | sed 's/^- [0-9:]* | //')

# ===== SAÍDA: systemMessage que sobrevive à compactação =====
echo "=== CONTEXTO PRESERVADO DA SESSÃO ANTERIOR (PreCompact $TIMESTAMP) ==="
echo ""

if [ -n "$MENSAGENS_USUARIO" ]; then
    echo "MENSAGENS DO USUÁRIO:"
    echo "$MENSAGENS_USUARIO" | head -c 2000
    echo ""
fi

if [ -n "$ARQUIVOS" ]; then
    echo "ARQUIVOS CRIADOS/REGISTRADOS NESTA SESSÃO:"
    echo "$ARQUIVOS"
    echo ""
fi

echo "SÍNTESE COMPLETA EM: $CONTEXTO_FILE"
echo ""
echo "IMPORTANTE: Continue o trabalho de onde parou. Leia o CONTEXTO.txt se precisar de mais detalhes."
echo "=== FIM DO CONTEXTO PRESERVADO ==="

exit 0
