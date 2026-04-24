#!/bin/bash
# salvar-estado-processo.sh
# Salva o estado atual da sessão no arquivo SESSAO-ATUAL.md
# Pode ser chamado manualmente ou pelo hook SessionEnd
#
# Uso: ./salvar-estado-processo.sh [NUMERO-CNJ] [ETAPA] [PROXIMA-ACAO]
# Sem argumentos: atualiza apenas a data

SESSAO_ATUAL="$HOME/Desktop/Arquivos de Métodos de Análise de Processos/CONTEXTO-PORTAVEL/SESSAO-ATUAL.md"
DATA_HOJE=$(date "+%Y-%m-%d")
HORA_ATUAL=$(date "+%H:%M")

CNJ="${1:-}"
ETAPA="${2:-}"
PROXIMA="${3:-}"

# Se SESSAO-ATUAL.md não existe, criar template
if [ ! -f "$SESSAO_ATUAL" ]; then
    mkdir -p "$(dirname "$SESSAO_ATUAL")"
    cat > "$SESSAO_ATUAL" << 'TEMPLATE'
# Estado Atual da Sessão

**Última atualização:** DATA_PLACEHOLDER
**Atualizado por:** Script salvar-estado-processo.sh

---

## Processo em foco

- **Número CNJ:** (nenhum em foco)
- **Etapa atual:** —
- **Próxima ação:** —

---

## O que foi feito hoje

(nada registrado ainda)

---

## Pendências

(nenhuma pendência registrada)
TEMPLATE
fi

# Atualizar data
sed -i '' "s/\*\*Última atualização:\*\*.*/\*\*Última atualização:\*\* $DATA_HOJE às $HORA_ATUAL/" "$SESSAO_ATUAL"

# Se CNJ fornecido, atualizar processo em foco
if [ -n "$CNJ" ]; then
    sed -i '' "s/\*\*Número CNJ:\*\*.*/\*\*Número CNJ:\*\* $CNJ/" "$SESSAO_ATUAL"
fi

if [ -n "$ETAPA" ]; then
    sed -i '' "s/\*\*Etapa atual:\*\*.*/\*\*Etapa atual:\*\* $ETAPA/" "$SESSAO_ATUAL"
fi

if [ -n "$PROXIMA" ]; then
    sed -i '' "s/\*\*Próxima ação:\*\*.*/\*\*Próxima ação:\*\* $PROXIMA/" "$SESSAO_ATUAL"
fi

echo "Estado salvo em $SESSAO_ATUAL ($DATA_HOJE $HORA_ATUAL)"
