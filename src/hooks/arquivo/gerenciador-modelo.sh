#!/bin/bash
# ============================================================
# GERENCIADOR AUTOMÁTICO DE MODELO (Opus/Sonnet)
# Hook: UserPromptSubmit
# Detecta limite do Opus e orienta troca + salva handoff
# Criado: 05/03/2026
# ============================================================
# HOOKS DE MODELO — Papéis de cada um:
#
#   gerenciador-modelo.sh (este)
#     - UserPromptSubmit. Detecta quando o usuário menciona
#       limite/economia/handoff e orienta a troca de modelo.
#     - Também trata "continua do handoff" e "salva handoff".
#
#   auto-trocar-modelo.sh
#     - Notification. Reage ao evento real de rate limit
#       ("You're out of extra usage"). Extrai contexto da
#       sessão, notifica via osascript e toca som.
#
#   fluxo-modelo.sh
#     - UserPromptSubmit. Detecta linguagem natural sobre
#       alternar modelo ("segue o fluxo", "trocar pro sonnet",
#       "volta pro opus") e guia o processo passo a passo.
#       Também trata "continua do handoff".
#
#   alternador-modelo.sh — REMOVIDO (dead code).
#     Era PreToolUse, verificava /tmp/claude-modelo-erro.
#     Funcionalidade coberta por auto-trocar-modelo.sh (evento
#     real) e gerenciador-modelo.sh (interação com o usuário).
# ============================================================

INPUT=$(cat)
USER_PROMPT=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('user_prompt', ''))
except:
    print('')
" 2>/dev/null)

PROMPT_LOWER=$(echo "$USER_PROMPT" | tr '[:upper:]' '[:lower:]')
HANDOFF="$HOME/stemmia-forense/config/HANDOFF.md"
MODELO_ATUAL="${CLAUDE_MODEL:-opus}"

# Detectar se usuário menciona limite/modelo
if echo "$PROMPT_LOWER" | grep -qiE "limite|acabou|sem credito|sem crédito|sem dinheiro|rate limit|caro demais|economizar|trocar modelo|usar sonnet|continua do handoff"; then

  if echo "$PROMPT_LOWER" | grep -qiE "continua do handoff|continuar handoff|pega o handoff"; then
    if [ -f "$HANDOFF" ]; then
      cat << EOF
HANDOFF DETECTADO — Leia o arquivo antes de continuar:
Arquivo: $HANDOFF

INSTRUÇÕES:
1. Leia o HANDOFF.md com Read tool
2. Continue EXATAMENTE de onde parou
3. Foque nos itens marcados como "Sonnet pode fazer"
4. NÃO tente fazer os itens marcados como "precisa de Opus"
5. Ao terminar, atualize o HANDOFF.md removendo o que completou
EOF
    fi
  else
    cat << EOF
ECONOMIA DE MODELO DETECTADA

O usuário quer economizar. ANTES de responder:
1. Salve o estado atual em: $HANDOFF
   - O que foi feito, o que falta, arquivos-chave
2. Classifique CADA tarefa pendente:
   - SONNET: criar/editar arquivos, rodar comandos, organizar
   - OPUS: raciocínio complexo, análise jurídica, arquitetura
3. Informe o usuário:
   - "Salvei o handoff. Troque com /model sonnet"
   - "Sonnet pode fazer X, Y, Z"
   - "Guarde pro Opus: A, B, C"
EOF
  fi
fi

# Detectar "salva o estado" / "salva handoff"
if echo "$PROMPT_LOWER" | grep -qiE "salva o estado|salvar estado|salva handoff|gera handoff"; then
  cat << EOF
HANDOFF SOLICITADO — Gere o arquivo $HANDOFF com:
1. Data/hora e nome da sessão
2. O que foi feito (completo)
3. O que falta — separado em SONNET e OPUS
4. Arquivos-chave com caminhos absolutos
5. Próximo passo imediato
EOF
fi

exit 0
