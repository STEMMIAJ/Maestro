#!/usr/bin/env bash
# Instala os hooks do Maestro no diretório .git/hooks
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

HOOK_SRC="hooks"
HOOK_DST=".git/hooks"

for h in pre-commit pre-push; do
  cp "$HOOK_SRC/$h" "$HOOK_DST/$h"
  chmod +x "$HOOK_DST/$h"
  echo "✓ instalado: $HOOK_DST/$h"
done

echo "✓ hooks instalados. Teste com: git commit --allow-empty -m 'test'"
