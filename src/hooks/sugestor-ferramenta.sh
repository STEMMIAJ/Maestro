#!/bin/bash
# ============================================================
# SUGESTOR DE FERRAMENTA
# Hook: UserPromptSubmit
# ============================================================
# Analisa o pedido do usuário e sugere qual ferramenta do
# sistema Stemmia é mais adequada (skill, agente, hook, pipeline).
#
# Gatilhos: "o que uso pra", "qual comando", "como faço pra",
# "tem algum", "existe algo", "qual skill", "qual agente"
#
# Criado em: 05/03/2026
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

# Detectar se o usuário está perguntando sobre qual ferramenta usar
PERGUNTA_FERRAMENTA=false

if echo "$PROMPT_LOWER" | grep -qiE "o que uso|qual comando|como fa[çz]o pra|tem algum|existe algo|qual skill|qual agente|qual pipeline|que ferramenta|melhor forma de|jeito de fazer"; then
    PERGUNTA_FERRAMENTA=true
fi

if [ "$PERGUNTA_FERRAMENTA" = true ]; then
    cat << 'GUIDANCE'
ATENÇÃO — USUÁRIO PERGUNTANDO SOBRE FERRAMENTAS

O usuário quer saber qual ferramenta usar. Consulte o mapa abaixo e sugira a mais adequada:

## MAPA RÁPIDO DE FERRAMENTAS POR SITUAÇÃO

### Recebi algo novo do tribunal
- Print do PJe → pipeline de petição (Triador → Gerador → Conferidor)
- Nomeação → /nomeacao
- Contestação de honorários → /contestar
- Impugnação → /justificar

### Preciso analisar processo
- Rápido (2-3 min) → /rapida
- Completo (8 agentes) → /completa
- Documento individual → /documento
- Quesitos → /quesitos

### Preciso gerar documento
- Proposta de honorários → /proposta
- Aceite → /aceite
- Agendamento → /agendar
- Laudo → /pipeline-laudo
- Pipeline completo → /pipeline

### Preciso verificar algo
- Peça jurídica → /conferir
- Leis/referências → /verificar
- Verificação 100% → /verificar-peticao

### Preciso buscar informação
- Jurisprudência → Orquestrador de Jurisprudência
- Base de dados local → Buscador na Base Local
- Artigo científico → Buscador Acadêmico
- Produto/preço → Pesquisador de Produtos

### Organização e produtividade
- Priorizar processos → /priorizar
- Ver agenda → calendário HTML ou bot Planner
- Status geral → PAINEL.html
- Sessões abertas → /organizar

### Sobre o sistema
- Criar hook/skill/agente → plugin-dev skills
- Auditar estrutura → auditor-estrutura
- Medir tokens → medidor-tokens
- Coach cognitivo → Coach Cognitivo

Responda de forma DIRETA: "Para isso, use /comando — ele faz X."
Se tiver mais de uma opção, listar no máximo 2-3 com explicação de 1 linha.
GUIDANCE
fi

exit 0
