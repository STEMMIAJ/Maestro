---
name: Fix Ultraplan Cloud Access
description: Ultraplan cloud sessions agora recebem planos — GitHub remote privado + hook auto-sync + fix symlink CLAUDE.md
type: project
originSessionId: 8315c24b-f52e-4537-bc0d-072c9e212b48
---
Resolvido em 16/abr/2026. Detalhes completos em:
`~/Desktop/STEMMIA Dexter/DOCS/changelog-sistema/2026-04-16-fix-ultraplan.md`

**Why:** `/ultraplan` não recebia planos porque ~/  não tinha git remote e CLAUDE.md era symlink quebrado no clone.

**How to apply:**
- Repo privado: `github.com/STEMMIAJ/claude-ultraplan`
- Hook auto-sync: `~/stemmia-forense/hooks/sync-plans-git.sh` (PostToolUse Write/Edit)
- `.gitignore` restritivo: só plans + CLAUDE.md tracked
- `git status` mostra `T .claude/CLAUDE.md` — normal, ignorar
