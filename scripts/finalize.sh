#!/usr/bin/env bash
# Encerra sessão: cria handoff, verifica commits, força push.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

TS=$(date +"%Y-%m-%d-%Hh%M")
HANDOFF_DIR="HANDOFFS"
mkdir -p "$HANDOFF_DIR"
HANDOFF="$HANDOFF_DIR/HANDOFF-$TS.md"

BRANCH=$(git branch --show-current)
LAST_COMMITS=$(git log --oneline -10)

cat > "$HANDOFF" <<EOF
# Handoff — $TS

**Branch:** $BRANCH
**Data/hora:** $(date -Iseconds)

## Commits desta sessão
\`\`\`
$LAST_COMMITS
\`\`\`

## Estado
- [ ] DONE
- [ ] BLOCKED
- [ ] PAUSED

## Issue trabalhada
#<NNN>

## Próximo passo (1 linha executável)
<ex: \`git checkout main && gh pr merge 42 --squash\`>

## Observações
<livre>
EOF

echo "[finalize] handoff criado: $HANDOFF"
echo "[finalize] edite-o com o estado real antes de commitar"
echo
echo "Quando terminar de editar, rode:"
echo "  git add $HANDOFF && git commit -m 'chore(handoff): sessão $TS' && git push"
