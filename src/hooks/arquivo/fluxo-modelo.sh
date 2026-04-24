#!/bin/bash
# DETECTOR DE FLUXO DE ALTERNÂNCIA DE MODELO
# Hook: UserPromptSubmit
# Detecta linguagem natural sobre trocar modelo e guia o usuário
# Criado: 05/03/2026

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

# Detectar intenção de alternar modelo (linguagem natural)
if echo "$PROMPT_LOWER" | grep -qiE "segue o fluxo|fluxo de alternar|trocar pro sonnet|volta pro opus|alternar modelo|mudar modelo|economizar modelo|fluxo modelo|troca de modelo|vai pro sonnet|sonnet agora|opus voltou|reset.* opus|limite.*modelo"; then

  HANDOFF="$HOME/stemmia-forense/config/HANDOFF.md"
  RESET_FILE="/tmp/claude-opus-reset-time"

  # Verificar se tem reset agendado
  RESET_INFO=""
  if [ -f "$RESET_FILE" ]; then
    RESET_EPOCH=$(cat "$RESET_FILE")
    NOW=$(date +%s)
    FALTA=$(( (RESET_EPOCH - NOW) / 60 ))
    if [ "$FALTA" -gt 0 ]; then
      RESET_INFO="Opus reseta em ~${FALTA} minutos."
    else
      RESET_INFO="Opus JÁ RESETOU! Pode voltar a usar."
    fi
  fi

  cat << EOF
FLUXO DE ALTERNÂNCIA DETECTADO

O usuário quer alternar de modelo. Siga este roteiro:

1. PERGUNTE: "Quer ir pro Sonnet agora ou o Opus já voltou?"
2. SE IR PRO SONNET:
   a. Atualize o HANDOFF.md com estado atual
   b. Diga: "Handoff salvo. Faça isso:"
   c. "- Aperte Escape para sair"
   d. "- Digite: claude --model sonnet"
   e. "- Na nova sessão diga: continua do handoff"
3. SE OPUS VOLTOU:
   a. Leia o HANDOFF.md
   b. Continue os itens marcados "OPUS PRECISA FAZER"
   c. Atualize removendo o que completou

${RESET_INFO}
Handoff atual: $HANDOFF
EOF
fi

# Detectar "continua do handoff" / "pega o handoff"
if echo "$PROMPT_LOWER" | grep -qiE "continua do handoff|pega o handoff|segue o handoff|retoma|de onde parou|onde parei"; then
  HANDOFF="$HOME/stemmia-forense/config/HANDOFF.md"
  if [ -f "$HANDOFF" ]; then
    cat << EOF
RETOMADA DE HANDOFF

1. Leia o arquivo: $HANDOFF
2. Identifique o modelo atual (opus ou sonnet)
3. Faça APENAS as tarefas do seu nível:
   - Sonnet: itens marcados "SONNET PODE FAZER"
   - Opus: TODOS os itens
4. Ao completar cada item, atualize o HANDOFF.md
5. Quando terminar tudo, diga: "Handoff concluído!"
EOF
  else
    echo "Sem handoff pendente. Tudo limpo."
  fi
fi

exit 0
