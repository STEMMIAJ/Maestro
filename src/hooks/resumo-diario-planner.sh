#!/bin/bash
# Resumo Diario do Planner
# Roda via launchd a cada 12h
# Le o localStorage exportado e gera resumo em Markdown

PLANNER_DIR="$HOME/Desktop/Planner"
EXPORT_FILE="$PLANNER_DIR/planner-auto-export.json"
REGISTROS_DIR="$HOME/Desktop/Projetos - Plan Mode/Registros Sessões"
DATA=$(date +"%Y-%m-%d")
HORA=$(date +"%H:%M")
RESUMO_FILE="$REGISTROS_DIR/RESUMO-PLANNER-$DATA.md"

# Se nao tem export, notificar e sair
if [ ! -f "$EXPORT_FILE" ]; then
    osascript -e 'display notification "Abra o planner e exporte um backup para ativar resumos automaticos" with title "Planner" subtitle "Sem dados para resumo"'
    exit 0
fi

# Gerar resumo basico usando python (disponivel no macOS)
python3 - "$EXPORT_FILE" "$RESUMO_FILE" "$DATA" "$HORA" << 'PYEOF'
import json, sys
from datetime import datetime, timedelta

export_file = sys.argv[1]
resumo_file = sys.argv[2]
data = sys.argv[3]
hora = sys.argv[4]

with open(export_file, 'r') as f:
    state = json.load(f)

today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
total = 0
done = 0
urgent = []
overdue = []
this_week = []
block_stats = []

for block in state.get('blocks', []):
    if block.get('type') in ('today', 'medications'):
        continue
    bt, bd = 0, 0
    for section in block.get('sections', []):
        for task in section.get('tasks', []):
            bt += 1
            total += 1
            if task.get('done'):
                bd += 1
                done += 1
            else:
                if task.get('urgency') == 'high':
                    urgent.append(f"- {task['text']} [{block['name']}]")
                if task.get('deadline'):
                    try:
                        dl = datetime.strptime(task['deadline'], '%Y-%m-%d')
                        diff = (dl - today).days
                        if diff < 0:
                            overdue.append(f"- {task['text']} ({abs(diff)}d atrasado) [{block['name']}]")
                        elif diff <= 7:
                            this_week.append(f"- {task['text']} ({diff}d) [{block['name']}]")
                    except:
                        pass
    if bt > 0:
        pct = round((bd/bt)*100)
        block_stats.append(f"- {block.get('icon','')} {block['name']}: {bd}/{bt} ({pct}%)")

resumo = f"""# RESUMO PLANNER - {data} {hora}

## Progresso
- Total: {total}
- Feitas: {done}
- Pendentes: {total - done}
- Progresso: {round((done/total)*100) if total > 0 else 0}%

## Por Bloco
{chr(10).join(block_stats)}
"""

if overdue:
    resumo += f"\n## ATRASADAS ({len(overdue)})\n{chr(10).join(overdue)}\n"
if urgent:
    resumo += f"\n## URGENTES ({len(urgent)})\n{chr(10).join(urgent)}\n"
if this_week:
    resumo += f"\n## ESTA SEMANA ({len(this_week)})\n{chr(10).join(this_week)}\n"

with open(resumo_file, 'w') as f:
    f.write(resumo)

print(f"Resumo salvo em {resumo_file}")
PYEOF

# Notificar
osascript -e "display notification \"Resumo do planner atualizado\" with title \"Planner\" subtitle \"$DATA $HORA\""
