#!/bin/bash
# ===========================================================================
# coletor-sessao.sh — Hook SessionEnd do process-mapper
# ===========================================================================
# Roda AUTOMATICAMENTE quando uma sessão do Claude Code fecha.
# Delega toda a lógica para coletor-universal.sh.
#
# PERFORMANCE: < 500ms
# FALHA: exit 0 SEMPRE — nunca bloqueia fechamento de sessão
# ===========================================================================

# Lê JSON do stdin (requerido por hooks Claude Code)
INPUT=$(cat)

exec "$HOME/.claude/plugins/process-mapper/scripts/coletor-universal.sh" --origem=sessionend
