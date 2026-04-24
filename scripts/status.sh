#!/usr/bin/env bash
# Mostra estado atual do Maestro em ~10 linhas. Use no início de toda sessão.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " MAESTRO — STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "[branch]   $(git branch --show-current)"
echo "[HEAD]     $(git log -1 --oneline)"
echo "[dirty?]   $(git status --porcelain | wc -l | tr -d ' ') arquivos modificados"
echo "[upstream] $(git rev-parse --abbrev-ref '@{u}' 2>/dev/null || echo '(sem upstream)')"
echo "[ahead]    $(git rev-list --count '@{u}..HEAD' 2>/dev/null || echo '0') commits à frente"
echo "[behind]   $(git rev-list --count 'HEAD..@{u}' 2>/dev/null || echo '0') commits atrás"
echo
echo "[issues abertas]"
gh issue list --state open --limit 20 2>/dev/null || echo "  (gh não autenticado ou remote não existe)"
echo
echo "[PRs abertos]"
gh pr list --state open --limit 10 2>/dev/null || echo "  (nenhum)"
echo
echo "[últimos 5 commits]"
git log --oneline -5
echo
echo "[último handoff]"
ls -t HANDOFFS/ 2>/dev/null | head -1 || echo "  (nenhum handoff ainda)"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
