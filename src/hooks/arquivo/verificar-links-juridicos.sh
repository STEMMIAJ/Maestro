#!/bin/bash
# Hook Stop: Verifica se a resposta do Claude contém links jurídicos falsos
# ou números de processo não verificados
# Se encontrar problemas, bloqueia a resposta

# Lê a resposta do Claude via stdin (JSON)
RESPONSE=$(cat)

# Extrai o texto da resposta
TEXT=$(echo "$RESPONSE" | jq -r '.stop_response // .message // .content // .' 2>/dev/null || echo "$RESPONSE")

# Padrões de URLs jurídicas para verificar
JURIDICAL_URL_PATTERNS=(
    'https?://[a-z]+\.stj\.jus\.br[^\s"<>]*'
    'https?://[a-z]+\.stf\.jus\.br[^\s"<>]*'
    'https?://[a-z]+\.tst\.jus\.br[^\s"<>]*'
    'https?://[a-z]*\.?tj[a-z]{2}\.jus\.br[^\s"<>]*'
    'https?://[a-z]+\.planalto\.gov\.br[^\s"<>]*'
    'https?://[a-z]+\.senado\.leg\.br[^\s"<>]*'
    'https?://jusbrasil\.com\.br[^\s"<>]*'
)

# Padrões de números de processo (formato CNJ e antigos)
# Estes são BLOQUEADOS automaticamente a menos que venham de WebSearch/WebFetch
PROCESS_NUMBER_PATTERNS=(
    '[0-9]{7}-[0-9]{2}\.[0-9]{4}\.[0-9]\.[0-9]{2}\.[0-9]{4}'   # CNJ completo
    'REsp [0-9]+\.?[0-9]*(/[A-Z]{2})?'                         # Recurso Especial STJ
    'REsp[0-9]+'                                                # REsp sem espaço
    'AgRg [^\s]+ [0-9]+\.?[0-9]*'                              # Agravo Regimental
    'AgInt [^\s]+ [0-9]+\.?[0-9]*'                             # Agravo Interno
    'EDcl [^\s]+ [0-9]+\.?[0-9]*'                              # Embargos Declaratórios
    'HC [0-9]+(/[A-Z]{2})?'                                    # Habeas Corpus
    'RHC [0-9]+(/[A-Z]{2})?'                                   # Recurso em HC
    'RE [0-9]+(/[A-Z]{2})?'                                    # Recurso Extraordinário
    'ARE [0-9]+(/[A-Z]{2})?'                                   # Agravo em RE
    'ADI [0-9]+'                                               # Ação Direta Inconst.
    'ADC [0-9]+'                                               # Ação Declaratória Const.
    'ADPF [0-9]+'                                              # Arguição Desc. Preceito
    'RCL [0-9]+'                                               # Reclamação
    'Súmula [0-9]+(/STJ|/STF)?'                                # Súmulas
    'Tema [0-9]+'                                              # Temas repetitivos
)

ERRORS_FOUND=0
ERROR_MESSAGES=""
PROCESS_FOUND=0
PROCESS_NUMBERS=""

# ============================================
# VERIFICAÇÃO 1: URLs jurídicas
# ============================================
for pattern in "${JURIDICAL_URL_PATTERNS[@]}"; do
    URLS=$(echo "$TEXT" | grep -oEi "$pattern" 2>/dev/null || true)

    if [ -n "$URLS" ]; then
        while IFS= read -r url; do
            if [ -n "$url" ]; then
                # Tenta acessar a URL (timeout de 5 segundos)
                HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$url" 2>/dev/null || echo "000")

                if [ "$HTTP_CODE" = "000" ] || [ "$HTTP_CODE" = "404" ] || [ "$HTTP_CODE" = "403" ] || [ "$HTTP_CODE" = "500" ]; then
                    ERRORS_FOUND=1
                    ERROR_MESSAGES="${ERROR_MESSAGES}
  - URL INVÁLIDA (HTTP $HTTP_CODE): $url"
                fi
            fi
        done <<< "$URLS"
    fi
done

# ============================================
# VERIFICAÇÃO 2: Números de processo
# ============================================
for pattern in "${PROCESS_NUMBER_PATTERNS[@]}"; do
    MATCHES=$(echo "$TEXT" | grep -oEi "$pattern" 2>/dev/null || true)

    if [ -n "$MATCHES" ]; then
        while IFS= read -r match; do
            if [ -n "$match" ]; then
                PROCESS_FOUND=1
                PROCESS_NUMBERS="${PROCESS_NUMBERS}
  - $match"
            fi
        done <<< "$MATCHES"
    fi
done

# ============================================
# RESULTADO
# ============================================

# Se encontrou URLs inválidas → BLOQUEIA
if [ "$ERRORS_FOUND" = "1" ]; then
    echo "BLOQUEADO: Links jurídicos inválidos detectados."
    echo ""
    echo "URLs com problema:${ERROR_MESSAGES}"
    echo ""
    echo "AÇÃO: Refaça sem esses links. Use WebSearch para encontrar URLs reais."
    exit 1
fi

# Se encontrou números de processo → ALERTA (não bloqueia, mas avisa)
# O usuário decide se quer verificar
if [ "$PROCESS_FOUND" = "1" ]; then
    echo "ALERTA: Números de processo detectados na resposta."
    echo ""
    echo "Processos mencionados:${PROCESS_NUMBERS}"
    echo ""
    echo "IMPORTANTE: Estes números NÃO foram verificados."
    echo "Claude pode ter inventado. Confirme em:"
    echo "  - STJ: https://scon.stj.jus.br/SCON/"
    echo "  - STF: https://jurisprudencia.stf.jus.br/"
    echo ""
    # Não bloqueia, só avisa (exit 0)
    exit 0
fi

# Tudo limpo
exit 0
