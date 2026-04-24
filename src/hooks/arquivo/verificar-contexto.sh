#!/bin/bash
# Hook Stop: Verifica se o CONTEXTO.txt tem resumo da sessão
# Se não tiver, bloqueia o Claude e força ele a escrever
#
# COMO FUNCIONA:
# 1. Verifica stop_hook_active para evitar loop infinito
# 2. Lê .sessao_atual para encontrar CONTEXTO.txt
# 3. Verifica se contém "RESUMO DA SESSÃO"
# 4. Se não: retorna JSON com decision=block e reason com instruções
# 5. Se sim: sai com 0 permitindo o Claude parar

PLAN_MODE_DIR="$HOME/Desktop/Projetos - Plan Mode"
SESSAO_ATUAL_FILE="$PLAN_MODE_DIR/.sessao_atual"

# Lê JSON do stdin
INPUT=$(cat)

# CRÍTICO: Verifica stop_hook_active para evitar loop infinito
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null)
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    # Já rodou uma vez e bloqueou, não bloqueia de novo
    exit 0
fi

# Se não há sessão atual, permite parar (não tem onde salvar)
if [ ! -f "$SESSAO_ATUAL_FILE" ]; then
    exit 0
fi

SESSAO_DIR=$(cat "$SESSAO_ATUAL_FILE")
CONTEXTO_FILE="$SESSAO_DIR/CONTEXTO.txt"

# Se o arquivo de contexto não existe, permite parar
if [ ! -f "$CONTEXTO_FILE" ]; then
    exit 0
fi

# Verifica se já tem resumo da sessão
if grep -q "RESUMO DA SESSÃO" "$CONTEXTO_FILE" 2>/dev/null; then
    # Já tem resumo, permite parar
    exit 0
fi

# Não tem resumo: bloqueia e instrui o Claude a escrever
# O reason será enviado ao Claude como sua próxima instrução

REASON="ANTES de encerrar, você DEVE atualizar o CONTEXTO.txt desta sessão com um resumo.

Use o Edit tool para ADICIONAR ao final do arquivo $CONTEXTO_FILE o seguinte conteúdo:

===============================================================================
RESUMO DA SESSÃO (por Claude)
===============================================================================
Título: [título curto e descritivo, máx 50 chars]
Categoria: [escolha UMA: Automação | Jurídico | Sites | Configuração | Documentação | Pericia | Outro]

## Objetivo
[1 frase descrevendo o objetivo principal da sessão]

## O que foi feito
- [item 1]
- [item 2]
- [mais itens se necessário]

## Decisões tomadas
- [decisão 1, se houver]

## Arquivos criados/modificados
- [/caminho/arquivo] - [breve descrição]

## Pendências
- [pendência 1, se houver, ou \"Nenhuma\"]
===============================================================================

IMPORTANTE: Baseie o resumo nas ações que você executou nesta sessão. Seja conciso mas informativo."

# Retorna JSON com decision block
# O jq -n cria um JSON do zero
jq -n --arg reason "$REASON" '{
    "decision": "block",
    "reason": $reason
}'

exit 0
