#!/bin/bash
# Hook SessionStart — NÃO coleta dados (sessão acabou de abrir)
# Apenas checa se é hora de disparar análise de padrões
# Performance: < 200ms (2 queries SQLite)
INPUT=$(cat)
exec "$HOME/.claude/plugins/process-mapper/scripts/coletor-universal.sh" --origem=sessionstart --apenas-trigger
