#!/bin/bash
# plano-obrigatorio.sh — Hook UserPromptSubmit
# Injeta instrução OBRIGATÓRIA para Claude mostrar plano de ação
# em cadeia de pensamento antes de executar qualquer coisa.
#
# Exceções: respostas curtas de aprovação, skills (/)
# Nunca bloqueia (exit 0), apenas injeta texto.

MENSAGEM="${CLAUDE_USER_PROMPT:-}"

# Se não tem mensagem, sair silenciosamente
if [ -z "$MENSAGEM" ]; then
    exit 0
fi

# Converter para minúsculas para comparação
MSG_LOWER=$(echo "$MENSAGEM" | tr '[:upper:]' '[:lower:]' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

# EXCEÇÃO 1: Mensagem muito curta (< 15 chars) — provavelmente aprovação
if [ ${#MSG_LOWER} -lt 15 ]; then
    exit 0
fi

# EXCEÇÃO 2: Respostas de aprovação
APROVACOES="^(sim|ok|pode|aprovo|faz|manda|bora|vai|continua|próximo|proximo|seguinte|beleza|feito|valeu|obrigado|blz|show|top|boa|isso|exato|perfeito|certo|correto|confirmo|confirma|yes|go|do it|approved|next|dale|tá bom|ta bom|manda ver|pode fazer|faz isso|faz tudo|roda|executa|aplica|implementa)$"
if echo "$MSG_LOWER" | grep -qiE "$APROVACOES"; then
    exit 0
fi

# EXCEÇÃO 3: Skills (começam com /)
if echo "$MSG_LOWER" | grep -qE '^\s*/'; then
    exit 0
fi

# EXCEÇÃO 4: Mensagens que já pedem plano (plan mode, plano, planeja)
if echo "$MSG_LOWER" | grep -qiE '(plan mode|plano de ação|planeja|planeje)'; then
    exit 0
fi

# EXCEÇÃO 5: Mensagens puramente de leitura/consulta
LEITURA="^(o que|qual|quais|como|onde|quando|quanto|por que|porque|explica|mostra|lista|ver |veja|lê |leia|abre |abra|busca|pesquisa|procura|status|progresso|painel)"
if echo "$MSG_LOWER" | grep -qiE "$LEITURA"; then
    exit 0
fi

# Para todo o resto: injetar instrução de plano obrigatório
cat << 'PLANO_EOF'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 REGRA OBRIGATÓRIA — PLANO DE AÇÃO EM CADEIA DE PENSAMENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANTES de usar QUALQUER ferramenta de escrita ou execução (Write, Edit, Bash, Agent),
você DEVE obrigatoriamente:

1. Mostrar um PLANO DE AÇÃO em cadeia de pensamento ao usuário
2. Formato obrigatório:

   PLANO DE AÇÃO
   ═════════════
   Entendi que você quer: [resumo do pedido]

   Passo 1: [o que vou fazer] → [por que]
   Passo 2: [o que vou fazer] → [por que]
   Passo 3: [o que vou fazer] → [por que]
   ...

   Arquivos que serão criados/modificados:
   - [caminho 1]
   - [caminho 2]

   Ferramentas que vou usar:
   - [ferramenta 1]: [para que]

   Posso prosseguir?

3. ESPERAR o usuário responder "ok", "pode", "aprovo", "faz" ou similar
4. SÓ ENTÃO executar os passos

EXCEÇÕES (pode agir direto SEM plano):
- Ferramentas de LEITURA (Read, Glob, Grep) → pode usar livremente
- Perguntas e consultas → responder direto
- Se o usuário disse "sem plano" ou "faz direto" → pular o plano

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLANO_EOF

exit 0
