#!/bin/bash
# ============================================================
# HOOK: Supervisor de Agentes — PreToolUse (Bash|Write|Edit)
# Sistema Stemmia Forense v8.0
# ============================================================
# Verifica se ações de escrita/execução estão dentro do plano
# aprovado. Se detectar desvio, BLOQUEIA e alerta.
# ============================================================
# Entrada: $CLAUDE_TOOL_NAME, $CLAUDE_TOOL_INPUT
# Saída: stderr (alertas), exit code (0=ok, 2=bloqueado)
# Log: ~/stemmia-forense/logs/supervisor.log
# Config: ~/stemmia-forense/config/SUPERVISOR-REGRAS.conf
# Plano: ~/stemmia-forense/config/PLANO-APROVADO.json
# ============================================================

TOOL_NAME="${CLAUDE_TOOL_NAME:-}"
TOOL_INPUT="${CLAUDE_TOOL_INPUT:-}"
LOG_FILE="$HOME/stemmia-forense/logs/supervisor.log"
REGRAS_FILE="$HOME/stemmia-forense/config/SUPERVISOR-REGRAS.conf"
PLANO_FILE="$HOME/stemmia-forense/config/PLANO-APROVADO.json"

# Se não tiver input, passa
[ -z "$TOOL_INPUT" ] && exit 0

# Se não tem regras NEM plano, sair imediatamente (fast path)
[ ! -f "$REGRAS_FILE" ] && [ ! -f "$PLANO_FILE" ] && exit 0

# Extrair informações relevantes do tool input (JSON) — usa jq se disponível, senão Python
if command -v jq >/dev/null 2>&1; then
    if [ "$TOOL_NAME" = "Bash" ]; then
        ALVO=$(echo "$TOOL_INPUT" | jq -r '.command // empty' 2>/dev/null || echo "$TOOL_INPUT")
        TIPO="COMANDO"
    elif [ "$TOOL_NAME" = "Write" ] || [ "$TOOL_NAME" = "Edit" ]; then
        ALVO=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty' 2>/dev/null || echo "")
        TIPO=$( [ "$TOOL_NAME" = "Write" ] && echo "ESCRITA" || echo "EDICAO" )
    else
        exit 0
    fi
else
    if [ "$TOOL_NAME" = "Bash" ]; then
        ALVO=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('command',''))" 2>/dev/null || echo "$TOOL_INPUT")
        TIPO="COMANDO"
    elif [ "$TOOL_NAME" = "Write" ] || [ "$TOOL_NAME" = "Edit" ]; then
        ALVO=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('file_path',''))" 2>/dev/null || echo "")
        TIPO=$( [ "$TOOL_NAME" = "Write" ] && echo "ESCRITA" || echo "EDICAO" )
    else
        exit 0
    fi
fi

[ -z "$ALVO" ] && exit 0

# ============================================================
# FASE 1: Regras ABSOLUTAS (sempre valem, com ou sem plano)
# ============================================================

if [ -f "$REGRAS_FILE" ]; then
    while IFS=$'\t' read -r ACAO PADRAO CATEGORIA MENSAGEM; do
        [ -z "$ACAO" ] && continue
        [[ "$ACAO" =~ ^# ]] && continue

        if echo "$ALVO" | grep -iqE "$PADRAO" 2>/dev/null; then
            # Registrar no log
            echo "$(date '+%Y-%m-%d %H:%M:%S') | ${ACAO} | ${CATEGORIA} | ${TOOL_NAME} | ${ALVO:0:100}" >> "$LOG_FILE" 2>/dev/null

            if [ "$ACAO" = "BLOQUEAR" ]; then
                echo "" >&2
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
                echo " SUPERVISOR: AÇÃO BLOQUEADA" >&2
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
                echo "Ferramenta: ${TOOL_NAME}" >&2
                echo "Alvo: ${ALVO:0:200}" >&2
                echo "Regra: ${CATEGORIA} — ${MENSAGEM}" >&2
                echo "" >&2
                echo "Pergunte ao usuário antes de prosseguir." >&2
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
                exit 2
            elif [ "$ACAO" = "ALERTAR" ]; then
                echo "" >&2
                echo "⚠ SUPERVISOR: ${CATEGORIA} — ${MENSAGEM}" >&2
                echo "  Alvo: ${ALVO:0:200}" >&2
                echo "" >&2
                # Alerta não bloqueia, apenas avisa
            fi
        fi
    done < "$REGRAS_FILE"
fi

# ============================================================
# FASE 2: Verificação contra plano aprovado (se existir)
# ============================================================

if [ -f "$PLANO_FILE" ]; then
    # Verificar se o arquivo/comando está no escopo do plano
    DENTRO_ESCOPO=false

    if [ "$TIPO" = "COMANDO" ]; then
        # Para comandos Bash, verificar contra comandos_permitidos
        PERMITIDOS=$(python3 -c "
import json, re, sys
try:
    plano = json.load(open('$PLANO_FILE'))
    cmd = '''$ALVO'''
    for padrao in plano.get('comandos_permitidos', []):
        if re.search(padrao, cmd):
            print('SIM')
            sys.exit(0)
    # Verificar comandos apenas de leitura (sempre permitidos)
    if re.search(r'^(cat|head|tail|less|more|ls|find|grep|wc|file|stat|pdfinfo|pdftotext)\s', cmd):
        print('SIM')
        sys.exit(0)
    print('NAO')
except:
    print('SIM')  # Se erro ao ler plano, não bloqueia
" 2>/dev/null)

        [ "$PERMITIDOS" = "SIM" ] && DENTRO_ESCOPO=true
    else
        # Para Write/Edit, verificar contra arquivos_permitidos e escopo_pastas
        PERMITIDOS=$(python3 -c "
import json, fnmatch, sys, os
try:
    plano = json.load(open('$PLANO_FILE'))
    arquivo = '$ALVO'
    # Verificar arquivos_permitidos (glob)
    for padrao in plano.get('arquivos_permitidos', []):
        padrao_exp = os.path.expanduser(padrao)
        if fnmatch.fnmatch(arquivo, padrao_exp):
            print('SIM')
            sys.exit(0)
    # Verificar escopo_pastas
    for pasta in plano.get('escopo_pastas', []):
        pasta_exp = os.path.expanduser(pasta)
        if arquivo.startswith(pasta_exp):
            print('SIM')
            sys.exit(0)
    # Arquivos em /tmp/ sempre permitidos
    if arquivo.startswith('/tmp/'):
        print('SIM')
        sys.exit(0)
    print('NAO')
except:
    print('SIM')
" 2>/dev/null)

        [ "$PERMITIDOS" = "SIM" ] && DENTRO_ESCOPO=true
    fi

    if [ "$DENTRO_ESCOPO" = false ]; then
        # Registrar desvio
        echo "$(date '+%Y-%m-%d %H:%M:%S') | DESVIO | ${TIPO} | ${TOOL_NAME} | ${ALVO:0:100}" >> "$LOG_FILE" 2>/dev/null

        echo "" >&2
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
        echo " SUPERVISOR: DESVIO DO PLANO DETECTADO" >&2
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
        echo "Ferramenta: ${TOOL_NAME}" >&2
        echo "Tipo: ${TIPO}" >&2
        echo "Alvo: ${ALVO:0:200}" >&2
        echo "" >&2
        echo "Este ${TIPO,,} NÃO está na lista de ações" >&2
        echo "aprovadas no plano." >&2
        echo "" >&2
        echo "Pergunte ao usuário se deseja permitir esta" >&2
        echo "ação antes de continuar." >&2
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
        exit 2
    fi
fi

# Registrar ação aprovada
echo "$(date '+%Y-%m-%d %H:%M:%S') | OK | ${TIPO} | ${TOOL_NAME} | ${ALVO:0:100}" >> "$LOG_FILE" 2>/dev/null

exit 0
