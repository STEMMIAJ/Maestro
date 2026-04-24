#!/bin/bash
# ============================================================
# DETECTOR DE DIFICULDADE
# Hook: UserPromptSubmit
# ============================================================
# Detecta quando o usuário está com dificuldade e oferece
# modos de ajuda personalizados.
#
# Gatilhos: "não sei", "como faz", "não entendo", "tô perdido",
# "me ajuda", "confuso", "complicado", "não consigo", "difícil"
#
# Criado em: 05/03/2026
# ============================================================

# Ler o prompt do usuário do stdin (formato JSON)
INPUT=$(cat)
USER_PROMPT=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('user_prompt', ''))
except:
    print('')
" 2>/dev/null)

# Converter para minúsculas
PROMPT_LOWER=$(echo "$USER_PROMPT" | tr '[:upper:]' '[:lower:]')

# Padrões de dificuldade
DIFICULDADE=false

# Expressões de desconhecimento
if echo "$PROMPT_LOWER" | grep -qiE "não sei|nao sei|num sei|n sei"; then
    DIFICULDADE=true
    TIPO="desconhecimento"
fi

# Expressões de confusão
if echo "$PROMPT_LOWER" | grep -qiE "não entendo|nao entendo|confuso|confusa|tô perdido|to perdido|me perdi|perdido"; then
    DIFICULDADE=true
    TIPO="confusão"
fi

# Pedidos de ajuda
if echo "$PROMPT_LOWER" | grep -qiE "me ajuda|como fa[zç]|como que faz|como eu fa[zç]|o que (é|e) isso|que que é"; then
    DIFICULDADE=true
    TIPO="pedido_ajuda"
fi

# Expressões de frustração
if echo "$PROMPT_LOWER" | grep -qiE "não consigo|nao consigo|difícil|dificil|complicado|travei|empaquei|não dá|nao da|impossível|impossivel"; then
    DIFICULDADE=true
    TIPO="frustração"
fi

# Expressões de sobrecarga
if echo "$PROMPT_LOWER" | grep -qiE "muito (coisa|informação|texto|grande|longo)|cansado|cansada|esgotado|demais|sobrecarregado"; then
    DIFICULDADE=true
    TIPO="sobrecarga"
fi

if [ "$DIFICULDADE" = true ]; then
    # Retornar instrução para o Claude oferecer modos de ajuda
    cat << 'GUIDANCE'
ATENÇÃO — DIFICULDADE DETECTADA

O usuário demonstrou dificuldade. ANTES de responder normalmente, ofereça os 3 modos de ajuda:

---
Percebi que pode estar com dúvida aqui. Como prefere que eu ajude?

**A) Faz pra mim** — Eu resolvo e depois te entrego um resumo simples do que fiz.
**B) Me ensina** — Explico passo a passo, com analogias, no seu ritmo.
**C) Faz e explica** — Eu resolvo E te dou um relatório didático de tudo que fiz e por quê.

(Só responder A, B ou C — ou pode ignorar e continuar normalmente.)

---

IMPORTANTE: Se o tipo de dificuldade for "sobrecarga", adicionar também:
**D) Pausa guiada** — Sugiro o que priorizar agora e o que pode ficar pra depois.

Após a escolha, adaptar o estilo da resposta ao modo escolhido.
GUIDANCE
fi

exit 0
