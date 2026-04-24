#!/bin/bash
# ADAPTADOR DE RESPOSTA À TELA
# Hook: UserPromptSubmit
# Detecta tamanho da janela e instrui o Claude a caber na tela visível
# Criado: 05/03/2026

INPUT=$(cat)

# Pegar tamanho do terminal
LINES=$(tput lines 2>/dev/null || echo 40)
COLS=$(tput cols 2>/dev/null || echo 120)

# Reservar linhas para prompt + input do usuário (~8 linhas)
LINHAS_UTEIS=$((LINES - 8))

# Classificar tamanho
if [ "$LINHAS_UTEIS" -lt 15 ]; then
  MODO="ultra-curto"
  MAX="10 linhas"
elif [ "$LINHAS_UTEIS" -lt 25 ]; then
  MODO="curto"
  MAX="18 linhas"
elif [ "$LINHAS_UTEIS" -lt 40 ]; then
  MODO="medio"
  MAX="30 linhas"
else
  MODO="normal"
  MAX="50 linhas"
fi

cat << EOF
ADAPTADOR DE TELA ATIVO — Janela: ${LINES}L x ${COLS}C → Modo: ${MODO}

REGRA: Sua resposta INTEIRA deve caber em no máximo ${MAX} visíveis.
- Se precisar de mais: dividir em blocos e perguntar "continuo?"
- Tabelas: máximo ${COLS} colunas de largura
- Listas: máximo 5-7 itens por bloco
- Se for instrução para o usuário: numerar e ser direto (1 linha por passo)
- NÃO repetir o que já foi dito. Só o que é NOVO.
EOF

exit 0
