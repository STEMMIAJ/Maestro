#!/bin/bash
# classificador-esforco.sh — Hook UserPromptSubmit
# Analisa complexidade do prompt e sugere modo de esforço
# Regex puro bash (0 custo de tokens, <5ms)

INPUT="${CLAUDE_USER_PROMPT:-}"
[ -z "$INPUT" ] && exit 0

MSG=$(echo "$INPUT" | tr '[:upper:]' '[:lower:]')

# ESFORÇO ALTO — padrões que exigem raciocínio profundo
ALTO_REGEX='ultrathink|análise completa|analise completa|/completa|/pipeline|/pipeline-laudo|/pipeline-contestacao|nexo causal|laudo pericial.*complex|cruzar.*documento|inconsistên|contestar.*honor|impugnar.*laudo|arquitetura.*agent|criar.*skill|criar.*hook|novo agente|nova skill|multi.*document|contradit|ambíguo|ambiguo|pipeline completo|pipeline contestação|pipeline do laudo'

# ESFORÇO BAIXO — padrões triviais
BAIXO_REGEX='^/t |^corrige?\s|typo|erro de digit|só muda|apenas muda|só troca|apenas troca|qual (é o |o )?cid|qual.*artigo|qual.*prazo|converte?|quantos dias|data de hoje|formata|renomeia|qual a dose|mg/kg'

if echo "$MSG" | grep -qiE "$ALTO_REGEX"; then
    echo ""
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  SUGESTÃO DE ESFORÇO: ALTO                    ║"
    echo "║  → Adicione 'ultrathink' ao seu pedido        ║"
    echo "║  → Tarefa complexa detectada                  ║"
    echo "╚═══════════════════════════════════════════════╝"
    echo ""
elif echo "$MSG" | grep -qiE "$BAIXO_REGEX"; then
    echo ""
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  SUGESTÃO DE ESFORÇO: BAIXO                   ║"
    echo "║  → Tarefa simples. Use /t para economizar     ║"
    echo "║    contexto desativando thinking              ║"
    echo "╚═══════════════════════════════════════════════╝"
    echo ""
fi
# MÉDIO: silêncio (é o default)

exit 0
