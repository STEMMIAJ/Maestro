#!/bin/bash
# Hook PreCompact — coleta snapshot da sessão quando contexto vai ser compactado
# Performance: < 500ms
INPUT=$(cat)
exec "$HOME/.claude/plugins/process-mapper/scripts/coletor-universal.sh" --origem=precompact
