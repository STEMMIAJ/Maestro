#!/bin/bash
# Hook Notification — coleta snapshot quando Claude envia notificação
# Performance: < 500ms
INPUT=$(cat)
exec "$HOME/.claude/plugins/process-mapper/scripts/coletor-universal.sh" --origem=notification
