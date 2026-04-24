#!/bin/bash
# limpar-claude.sh — Lista sessões Claude e permite matar as abandonadas
# Criado em 2026-03-02

echo ""
echo "═══════════════════════════════════════════════"
echo "  SESSÕES DO CLAUDE CODE ATIVAS"
echo "═══════════════════════════════════════════════"
echo ""

# Buscar processos claude (o binário principal, não subprocessos)
PIDS=$(ps aux | grep -E '[c]laude' | grep -v "grep\|caffeinate\|Updater\|Helper\|GPU\|Renderer" | grep -E "node.*claude|/claude" | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "  Nenhuma sessão Claude encontrada."
    echo ""
    exit 0
fi

# Listar cada sessão
echo "  PID      UPTIME     DIRETÓRIO"
echo "  ───────  ─────────  ──────────────────────────"

COUNT=0
PID_LIST=()
for PID in $PIDS; do
    # Uptime do processo
    ETIME=$(ps -o etime= -p "$PID" 2>/dev/null | tr -d ' ')
    # Diretório de trabalho
    CWD=$(lsof -p "$PID" -Fn 2>/dev/null | grep "^n/" | grep "cwd" -A1 | grep "^n" | head -1 | cut -c2-)
    if [ -z "$CWD" ]; then
        CWD=$(ls -l /proc/"$PID"/cwd 2>/dev/null | awk '{print $NF}')
    fi
    [ -z "$CWD" ] && CWD="(desconhecido)"

    # Simplificar caminho
    CWD_SHORT="${CWD/#$HOME/~}"

    COUNT=$((COUNT + 1))
    PID_LIST+=("$PID")
    printf "  %-8s %-10s %s\n" "$PID" "$ETIME" "$CWD_SHORT"
done

echo ""
echo "  Total: $COUNT sessões"
echo ""

# Identificar a sessão ATUAL (o terminal de onde estamos rodando)
CURRENT_PPID=$(ps -o ppid= -p $$ 2>/dev/null | tr -d ' ')

echo "═══════════════════════════════════════════════"
echo ""

# Perguntar o que fazer
echo "  Opções:"
echo "    [enter] — Não fazer nada"
echo "    [a]     — Matar TODAS (exceto a atual)"
echo "    [PID]   — Matar sessão específica"
echo ""
read -r -p "  Escolha: " CHOICE

case "$CHOICE" in
    "")
        echo "  Nada alterado."
        ;;
    a|A)
        echo ""
        KILLED=0
        for PID in "${PID_LIST[@]}"; do
            # Não matar o processo pai do terminal atual
            if [ "$PID" != "$CURRENT_PPID" ]; then
                kill "$PID" 2>/dev/null && KILLED=$((KILLED + 1))
            fi
        done
        echo "  $KILLED sessões encerradas."
        ;;
    *)
        if kill -0 "$CHOICE" 2>/dev/null; then
            kill "$CHOICE" 2>/dev/null
            echo "  Sessão $CHOICE encerrada."
        else
            echo "  PID inválido: $CHOICE"
        fi
        ;;
esac

echo ""
