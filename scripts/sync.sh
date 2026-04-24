#!/usr/bin/env bash
# Sincroniza main com origin. Aborta se houver mudanças locais não commitadas.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if [ -n "$(git status --porcelain)" ]; then
  echo "✗ Há mudanças não commitadas. Commite ou stash antes de sync." >&2
  git status --short
  exit 1
fi

BRANCH=$(git branch --show-current)
echo "[sync] branch atual: $BRANCH"

git fetch origin
git checkout main
git pull --ff-only origin main

if [ "$BRANCH" != "main" ]; then
  git checkout "$BRANCH"
  echo "[sync] rebasing $BRANCH em main"
  git rebase main
fi

echo "✓ sync OK"
