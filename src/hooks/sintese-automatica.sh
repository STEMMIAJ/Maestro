#!/bin/bash
# Hook PreCompact — Salva síntese antes de compactar contexto
# Dispara automaticamente quando o Claude Code vai compactar

DIR="$HOME/Desktop/Projetos - Plan Mode/Registros Sessoes"
mkdir -p "$DIR"

DATA=$(date +%Y-%m-%d)
HORA=$(date +%H%M)
ARQUIVO="$DIR/SESSAO-AUTO-${DATA}-${HORA}.md"

# Cria arquivo de síntese (o Claude preencherá via prompt)
cat > "$ARQUIVO" << 'TEMPLATE'
# Síntese Automática de Sessão

**Data:** PLACEHOLDER_DATA
**Motivo:** Compactação automática de contexto

## O que foi feito nesta sessão
- [A ser preenchido pelo Claude]

## Arquivos criados/modificados
- [A ser preenchido]

## Pendências
- [A ser preenchido]

## Decisões tomadas
- [A ser preenchido]
TEMPLATE

# Substitui placeholder
sed -i '' "s/PLACEHOLDER_DATA/$(date '+%d\/%m\/%Y %H:%M')/" "$ARQUIVO"

# Avisa o usuário
afplay /System/Library/Sounds/Sosumi.aiff &
osascript -e 'display notification "Contexto quase cheio! Síntese automática salva em Registros Sessoes." with title "Claude Code - Atenção" with sound name "Sosumi"'

echo "SÍNTESE SALVA: $ARQUIVO"
echo "CONTEXTO QUASE CHEIO — Considere iniciar nova sessão."
