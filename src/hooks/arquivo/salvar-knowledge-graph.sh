#!/bin/bash
# Hook PreCompact: salvar entidades no Knowledge Graph antes de compactar
# Appenda ao ~/.claude/knowledge-graph.jsonl
# Formato: cada linha e um JSON com entidade + observacoes + timestamp

KG_FILE="$HOME/.claude/knowledge-graph.jsonl"
SESSAO_ID="sessao-$(date +%Y%m%d-%H%M%S)"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Coletar contexto minimo da sessao
# O hook PreCompact recebe o resumo via stdin ou CLAUDE_COMPACT_SUMMARY
RESUMO="${CLAUDE_COMPACT_SUMMARY:-sessao sem resumo capturado}"

# Criar entidade de sessao
cat >> "$KG_FILE" <<EOF
{"type":"entity","name":"$SESSAO_ID","entityType":"session","observations":["$TIMESTAMP: Sessao compactada"],"timestamp":"$TIMESTAMP"}
EOF

exit 0
