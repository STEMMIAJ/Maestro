#!/bin/bash
# Script executado automaticamente ao iniciar sessão do Claude Code
# Hook: SessionStart
# SIMPLIFICADO em 2026-03-12: removida criação de pasta/CONTEXTO.txt
# ATUALIZADO em 2026-04-04: adicionado contexto de urgencias

# Briefing de retorno (se ausência > 2h)
BRIEFING_SCRIPT="$HOME/.claude/plugins/process-mapper/scripts/briefing-retorno.sh"
[ -f "$BRIEFING_SCRIPT" ] && bash "$BRIEFING_SCRIPT"

# Injetar contexto do diário (continuidade entre sessões)
DIARIO_SISTEMA="$HOME/Desktop/STEMMIA — SISTEMA COMPLETO/DIARIO-DO-SISTEMA.md"
DIARIO_PROJETOS="$HOME/Desktop/DIARIO-PROJETOS.md"

echo ""
echo "CONTEXTO DO DIARIO:"
if [ -f "$DIARIO_SISTEMA" ]; then
    echo "--- Diário do Sistema (últimas 15 linhas) ---"
    tail -15 "$DIARIO_SISTEMA"
fi
if [ -f "$DIARIO_PROJETOS" ]; then
    echo "--- Diário de Projetos (últimas 15 linhas) ---"
    tail -15 "$DIARIO_PROJETOS"
fi
echo "--- Fim do contexto ---"

# Contexto de urgencias: top 10 processos mais urgentes
/usr/bin/python3 -c "
import json, glob, os
urgencias = []
for f in glob.glob(os.path.expanduser('~/stemmia-forense/processos/*/URGENCIA.json')):
    try:
        with open(f) as fh:
            u = json.load(fh)
            u['processo'] = os.path.basename(os.path.dirname(f))
            urgencias.append(u)
    except:
        pass
if urgencias:
    urgencias.sort(key=lambda x: (
        0 if x.get('nivel') == 'CRITICAL' else 1 if x.get('nivel') == 'WARNING' else 2,
        x.get('prazo_dias') if x.get('prazo_dias') is not None else 999
    ))
    print()
    print('TOP URGENTES:')
    for u in urgencias[:10]:
        nivel = u.get('nivel', '?')
        icone = '🔴' if nivel == 'CRITICAL' else '🟡' if nivel == 'WARNING' else '🟢'
        dias = u.get('prazo_dias', '?')
        motivo = u.get('motivo', '')[:60]
        cnj = u['processo'][:25]
        print(f'  {icone} {cnj} | {dias}d | {motivo}')
    total_crit = sum(1 for u in urgencias if u.get('nivel') == 'CRITICAL')
    total_warn = sum(1 for u in urgencias if u.get('nivel') == 'WARNING')
    total = len(urgencias)
    print(f'  ({total_crit} criticos, {total_warn} warnings, {total} total)')
" 2>/dev/null

# Health check dos servidores MCP
bash "$HOME/stemmia-forense/hooks/healthcheck-mcp.sh" 2>/dev/null

# Alerta de sessões acumuladas
NUM_SESSOES=$(ps aux | grep -E "^$(whoami).*claude$" | grep -v grep | wc -l | tr -d ' ')
if [ "$NUM_SESSOES" -gt 3 ]; then
    echo "Você tem $NUM_SESSOES sessões do Claude Code abertas. Use /organizar para triagem."
fi

# Injetar contexto das últimas sessões do memoria.db
/usr/bin/python3 -c "
import sqlite3, os
db = os.path.expanduser('~/stemmia-forense/data/memoria.db')
if not os.path.exists(db):
    exit()
conn = sqlite3.connect(db)
rows = conn.execute('''
    SELECT started_at, duration_minutes, slug, topics, substr(summary, 1, 80)
    FROM sessions
    WHERE user_message_count > 0
    ORDER BY started_at DESC LIMIT 5
''').fetchall()
if rows:
    print()
    print('ULTIMAS SESSOES (Memoria):')
    for r in rows:
        data = (r[0] or '?')[:16]
        dur = str(r[1])+'min' if r[1] else '?'
        slug = r[2] or ''
        topics = r[3] or ''
        resumo = r[4] or ''
        print(f'  {data} ({dur}) [{slug}] {topics}')
        if resumo and not resumo.startswith('Context:'):
            print(f'    > {resumo}')
conn.close()
" 2>/dev/null

exit 0
