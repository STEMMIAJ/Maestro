#!/bin/bash
# enforcement-verificacao.sh — Hook PostToolUse (Write/Edit)
# Detecta criação de peças processuais e força execução do verificador-100
# Stemmia Forense v4.1.0

# Arquivo que foi escrito/editado vem via STDIN do hook
INPUT=$(cat)

# Extrair caminho do arquivo do output do tool
ARQUIVO=$(echo "$INPUT" | grep -oE '/[^ ]+\.(md|txt)' | head -1)

# Se não encontrou arquivo, sair silenciosamente
[ -z "$ARQUIVO" ] && exit 0

# Nome do arquivo (sem caminho)
NOME=$(basename "$ARQUIVO" | tr '[:upper:]' '[:lower:]')

# Padrões de nomes de peças processuais
PETICAO=0
case "$NOME" in
    proposta-honorarios*) PETICAO=1; TIPO="PROPOSTA-HONORARIOS" ;;
    peticao-aceite*) PETICAO=1; TIPO="PETICAO-ACEITE" ;;
    peticao-agendamento*) PETICAO=1; TIPO="PETICAO-AGENDAMENTO" ;;
    resposta-contestacao*) PETICAO=1; TIPO="RESPOSTA-CONTESTACAO" ;;
    justificativa-honorarios*) PETICAO=1; TIPO="JUSTIFICATIVA-HONORARIOS" ;;
    manifestacao*) PETICAO=1; TIPO="MANIFESTACAO" ;;
    laudo-rascunho*) PETICAO=1; TIPO="LAUDO" ;;
    laudo-pericial*) PETICAO=1; TIPO="LAUDO" ;;
    contestacao*) PETICAO=1; TIPO="CONTESTACAO" ;;
    esclarecimento*) PETICAO=1; TIPO="ESCLARECIMENTO" ;;
    aceite*) PETICAO=1; TIPO="ACEITE" ;;
esac

# Se não é peça processual, sair
[ "$PETICAO" -eq 0 ] && exit 0

# Identificar pasta do processo (subir até encontrar TEXTO-EXTRAIDO.txt)
DIR=$(dirname "$ARQUIVO")
TEXTO=""
for i in 1 2 3; do
    if [ -f "$DIR/TEXTO-EXTRAIDO.txt" ]; then
        TEXTO="$DIR/TEXTO-EXTRAIDO.txt"
        break
    fi
    DIR=$(dirname "$DIR")
done

# Mensagem de enforcement
cat << EOF

⚠️ VERIFICAÇÃO 100% OBRIGATÓRIA

Peça processual detectada: $TIPO
Arquivo: $ARQUIVO
${TEXTO:+Texto-fonte: $TEXTO}

AÇÃO OBRIGATÓRIA antes de informar ao usuário que a peça está pronta:

1. Execute o agente Verificador 100% (subagent_type: "Verificador 100 Percent")
   OU execute manualmente as 6 etapas de verificação:
   - Segmentar a peça em unidades factuais
   - Fazer matching de cada unidade contra TEXTO-EXTRAIDO.txt
   - Verificar leis citadas na base local
   - Detectar vícios processuais (CNJs diferentes)
   - Incorporar verificações existentes
   - Gerar JSON e HTML de verificação

2. Salve o JSON em: $(dirname "$ARQUIVO")/verificacao-$(echo "$TIPO" | tr '[:upper:]' '[:lower:]').json

3. Gere o HTML com:
   python3 ~/Desktop/analisador\ de\ processos/gerar_verificacao.py \\
     --json "$(dirname "$ARQUIVO")/verificacao-$(echo "$TIPO" | tr '[:upper:]' '[:lower:]').json" \\
     --output "$(dirname "$ARQUIVO")/VERIFICACAO-$TIPO.html"

4. Informe o caminho do HTML ao usuário (NÃO abrir automaticamente):
   $(dirname "$ARQUIVO")/VERIFICACAO-$TIPO.html

NÃO informe ao usuário que a peça está pronta sem a verificação.
EOF

exit 0
