#!/bin/bash
# Hook SessionEnd: Finaliza sessão, salva backup e atualiza Relatório Diário
#
# COMO FUNCIONA:
# 1. Salva transcrição bruta se ainda não foi salva (backup)
# 2. Marca "SESSÃO ENCERRADA" no CONTEXTO.txt
# 3. Extrai título/categoria/descrição do resumo (ou usa fallback)
# 4. Atualiza Semana-XX-YYYY.html com novo card
# 5. Atualiza RELATORIO-INDEX.html se necessário

PLAN_MODE_DIR="$HOME/Desktop/Projetos - Plan Mode"
SESSAO_ATUAL_FILE="$PLAN_MODE_DIR/.sessao_atual"
RELATORIOS_DIR="$PLAN_MODE_DIR/Relatorios"
SCRIPTS_DIR="$PLAN_MODE_DIR/scripts"

# Lê JSON do stdin
INPUT=$(cat)

# Se não há sessão atual, sai
if [ ! -f "$SESSAO_ATUAL_FILE" ]; then
    exit 0
fi

SESSAO_DIR=$(cat "$SESSAO_ATUAL_FILE")
CONTEXTO_FILE="$SESSAO_DIR/CONTEXTO.txt"

# Se o arquivo de contexto não existe, sai
if [ ! -f "$CONTEXTO_FILE" ]; then
    exit 0
fi

# ============================================
# 1. BACKUP: Salva transcrição se não foi salva
# ============================================
if ! grep -q "TRANSCRIÇÃO SALVA EM" "$CONTEXTO_FILE" 2>/dev/null; then
    # Chama o script de salvar contexto bruto passando o mesmo stdin
    echo "$INPUT" | "$SCRIPTS_DIR/salvar-contexto-bruto.sh"
fi

# ============================================
# 2. Marca SESSÃO ENCERRADA
# ============================================
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
{
    echo ""
    echo "==============================================================================="
    echo "SESSÃO ENCERRADA em $TIMESTAMP"
    echo "==============================================================================="
} >> "$CONTEXTO_FILE"

# ============================================
# 3. Extrai informações do resumo (se existir)
# ============================================

# Valores padrão (fallback)
SESSAO_NOME=$(basename "$SESSAO_DIR")
TITULO="$SESSAO_NOME"
CATEGORIA="Sessão"
DESCRICAO=""

# Tenta extrair do RESUMO DA SESSÃO
if grep -q "RESUMO DA SESSÃO" "$CONTEXTO_FILE" 2>/dev/null; then
    # Extrai título
    TITULO_EXTRAIDO=$(grep -A1 "RESUMO DA SESSÃO" "$CONTEXTO_FILE" | grep "^Título:" | sed 's/^Título:[[:space:]]*//' | head -1)
    [ -n "$TITULO_EXTRAIDO" ] && TITULO="$TITULO_EXTRAIDO"

    # Extrai categoria
    CATEGORIA_EXTRAIDA=$(grep "^Categoria:" "$CONTEXTO_FILE" | sed 's/^Categoria:[[:space:]]*//' | head -1)
    [ -n "$CATEGORIA_EXTRAIDA" ] && CATEGORIA="$CATEGORIA_EXTRAIDA"

    # Extrai objetivo/descrição (linha após ## Objetivo)
    DESCRICAO_EXTRAIDA=$(grep -A1 "^## Objetivo" "$CONTEXTO_FILE" | tail -1 | sed 's/^[[:space:]]*//')
    [ -n "$DESCRICAO_EXTRAIDA" ] && DESCRICAO="$DESCRICAO_EXTRAIDA"
fi

# Se não tem descrição, usa lista de arquivos criados
if [ -z "$DESCRICAO" ]; then
    ARQUIVOS_CRIADOS=$(grep -A100 "ARQUIVOS CRIADOS NESTA SESSÃO" "$CONTEXTO_FILE" | grep "^- " | head -5 | sed 's/^- [0-9:]*[[:space:]]*|[[:space:]]*//' | tr '\n' ', ' | sed 's/,$//')
    if [ -n "$ARQUIVOS_CRIADOS" ]; then
        DESCRICAO="Arquivos: $ARQUIVOS_CRIADOS"
    else
        DESCRICAO="Sessão de trabalho no Claude Code"
    fi
fi

# Limita tamanhos
TITULO=$(echo "$TITULO" | head -c 80)
DESCRICAO=$(echo "$DESCRICAO" | head -c 300)

# Hora atual
HORA=$(date +"%H:%M")

# ============================================
# 4. Atualiza Relatório Semanal
# ============================================

# Calcula semana e ano
SEMANA=$(date +"%V")
ANO=$(date +"%Y")
RELATORIO_SEMANAL="$RELATORIOS_DIR/Semana-$SEMANA-$ANO.html"

# Data formatada para o dia-section
DIA_SEMANA=$(LC_TIME=pt_BR.UTF-8 date +"%A" 2>/dev/null || date +"%A")
# Converte para português se necessário
case "$DIA_SEMANA" in
    Monday) DIA_SEMANA="Segunda-feira" ;;
    Tuesday) DIA_SEMANA="Terca-feira" ;;
    Wednesday) DIA_SEMANA="Quarta-feira" ;;
    Thursday) DIA_SEMANA="Quinta-feira" ;;
    Friday) DIA_SEMANA="Sexta-feira" ;;
    Saturday) DIA_SEMANA="Sabado" ;;
    Sunday) DIA_SEMANA="Domingo" ;;
esac

DIA=$(date +"%d")
MES_NUM=$(date +"%m")
# Mês em português
case "$MES_NUM" in
    01) MES="janeiro" ;;
    02) MES="fevereiro" ;;
    03) MES="marco" ;;
    04) MES="abril" ;;
    05) MES="maio" ;;
    06) MES="junho" ;;
    07) MES="julho" ;;
    08) MES="agosto" ;;
    09) MES="setembro" ;;
    10) MES="outubro" ;;
    11) MES="novembro" ;;
    12) MES="dezembro" ;;
esac

DATA_FORMATADA="$DIA de $MES de $ANO"
DIA_HEADER="$DATA_FORMATADA ($DIA_SEMANA)"

# Flag para saber se o arquivo é novo
ARQUIVO_NOVO=false

# Se o arquivo semanal não existe, cria com template
if [ ! -f "$RELATORIO_SEMANAL" ]; then
    ARQUIVO_NOVO=true

    # Calcula período da semana (início e fim)
    # Semana começa na segunda
    INICIO_SEMANA=$(date -v-$(date +%u)d+1d +"%d %b" 2>/dev/null || date +"%d %b")
    FIM_SEMANA=$(date -v-$(date +%u)d+7d +"%d %b" 2>/dev/null || date +"%d %b")

    cat > "$RELATORIO_SEMANAL" << 'TEMPLATE_EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Semana SEMANA_NUM - ANO_NUM - Relatorio de Progresso</title>
    <style>
        :root {
            --cor-fundo: #ffffff;
            --cor-texto: #1a1a1a;
            --cor-codigo: #F5F5F5;
            --cor-borda: #e0e0e0;
            --cor-destaque: #0066cc;
            --cor-sucesso: #38a169;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: var(--cor-texto);
            background: var(--cor-fundo);
            padding: 1cm;
        }
        h1 { font-size: 24px; margin-bottom: 5px; }
        h2 { font-size: 18px; margin: 25px 0 15px; color: var(--cor-destaque); }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            border-bottom: 3px solid var(--cor-destaque);
            margin-bottom: 30px;
        }
        .voltar {
            color: var(--cor-destaque);
            text-decoration: none;
            font-size: 14px;
        }
        .voltar:hover { text-decoration: underline; }
        .busca-container {
            position: sticky;
            top: 0;
            background: white;
            padding: 15px 0;
            border-bottom: 1px solid var(--cor-borda);
            margin-bottom: 20px;
            z-index: 100;
        }
        .busca-input {
            width: 100%;
            padding: 10px 15px;
            font-size: 14px;
            border: 2px solid var(--cor-borda);
            border-radius: 8px;
            outline: none;
        }
        .busca-input:focus { border-color: var(--cor-destaque); }
        .dia-section { margin-bottom: 30px; }
        .dia-header {
            background: var(--cor-codigo);
            padding: 10px 15px;
            border-radius: 4px;
            margin-bottom: 15px;
            font-weight: 600;
        }
        .item-card {
            border: 1px solid var(--cor-borda);
            border-radius: 8px;
            margin-bottom: 15px;
            padding: 15px;
        }
        .item-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        .item-nome {
            font-size: 16px;
            font-weight: 600;
            color: var(--cor-destaque);
        }
        .item-hora {
            font-size: 12px;
            color: #666;
            background: var(--cor-codigo);
            padding: 2px 8px;
            border-radius: 4px;
        }
        .item-caminho {
            font-family: monospace;
            font-size: 12px;
            color: #666;
            background: var(--cor-codigo);
            padding: 5px 10px;
            border-radius: 4px;
            margin-bottom: 10px;
            word-break: break-all;
        }
        .item-descricao { margin-bottom: 10px; }
        .categoria-tag {
            display: inline-block;
            background: var(--cor-sucesso);
            color: white;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 11px;
            margin-top: 10px;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid var(--cor-borda);
            margin-top: 30px;
        }
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>Semana SEMANA_NUM - ANO_NUM</h1>
            <p style="color:#666;">PERIODO_SEMANA</p>
        </div>
        <a href="RELATORIO-INDEX.html" class="voltar">← Voltar ao indice</a>
    </div>
    <div class="busca-container">
        <input type="text" class="busca-input" id="buscaInput" placeholder="Buscar arquivo, conceito ou descricao...">
    </div>

    <!-- CONTEUDO_DIAS -->

    <div class="footer">
        <p>Total de itens nesta semana: 0</p>
        <p>Atualizado em: DATA_ATUALIZACAO</p>
    </div>
    <script>
        document.getElementById('buscaInput').addEventListener('input', function(e) {
            const termo = e.target.value.toLowerCase();
            const items = document.querySelectorAll('.item-card');
            items.forEach(item => {
                const texto = item.textContent.toLowerCase();
                if (texto.includes(termo) || termo === '') {
                    item.classList.remove('hidden');
                } else {
                    item.classList.add('hidden');
                }
            });
        });
    </script>
</body>
</html>
TEMPLATE_EOF

    # Substitui placeholders
    sed -i '' "s/SEMANA_NUM/$SEMANA/g" "$RELATORIO_SEMANAL"
    sed -i '' "s/ANO_NUM/$ANO/g" "$RELATORIO_SEMANAL"
    sed -i '' "s/PERIODO_SEMANA/$INICIO_SEMANA - $FIM_SEMANA/g" "$RELATORIO_SEMANAL"
    sed -i '' "s/DATA_ATUALIZACAO/$(date +"%d\/%m\/%Y %H:%M")/g" "$RELATORIO_SEMANAL"
fi

# ============================================
# Insere o card no arquivo semanal
# ============================================

# Escapa caracteres especiais para sed
TITULO_ESCAPED=$(echo "$TITULO" | sed 's/[&/\]/\\&/g')
DESCRICAO_ESCAPED=$(echo "$DESCRICAO" | sed 's/[&/\]/\\&/g')
CATEGORIA_ESCAPED=$(echo "$CATEGORIA" | sed 's/[&/\]/\\&/g')
CAMINHO_ESCAPED=$(echo "$CONTEXTO_FILE" | sed 's/[&/\]/\\&/g')

# Gera o HTML do card
CARD_HTML="        <div class=\"item-card\" data-searchable>
            <div class=\"item-header\">
                <span class=\"item-nome\">$TITULO_ESCAPED</span>
                <span class=\"item-hora\">$HORA</span>
            </div>
            <div class=\"item-caminho\">$CAMINHO_ESCAPED</div>
            <div class=\"item-descricao\">
                <p>$DESCRICAO_ESCAPED</p>
            </div>
            <span class=\"categoria-tag\">$CATEGORIA_ESCAPED</span>
        </div>"

# Verifica se já existe dia-section para hoje
if grep -q "$DIA_HEADER" "$RELATORIO_SEMANAL" 2>/dev/null; then
    # Dia já existe, adiciona card dentro dele
    # Encontra a linha do dia-header e insere o card após o fechamento do dia-header div
    # Usa awk para inserir após a linha que contém o dia-header
    awk -v card="$CARD_HTML" -v header="$DIA_HEADER" '
    {
        print
        if (index($0, header) > 0) {
            getline
            print
            print card
        }
    }
    ' "$RELATORIO_SEMANAL" > "$RELATORIO_SEMANAL.tmp" && mv "$RELATORIO_SEMANAL.tmp" "$RELATORIO_SEMANAL"
else
    # Dia não existe, cria nova dia-section
    DIA_SECTION="    <div class=\"dia-section\">
        <div class=\"dia-header\">$DIA_HEADER</div>

$CARD_HTML
    </div>
"
    # Insere antes do footer
    awk -v section="$DIA_SECTION" '
    /<div class="footer">/ {
        print section
        print ""
    }
    { print }
    ' "$RELATORIO_SEMANAL" > "$RELATORIO_SEMANAL.tmp" && mv "$RELATORIO_SEMANAL.tmp" "$RELATORIO_SEMANAL"
fi

# ============================================
# Atualiza contadores no footer
# ============================================

# Conta total de item-cards
TOTAL_ITENS=$(grep -c 'class="item-card"' "$RELATORIO_SEMANAL" 2>/dev/null || echo "0")

# Atualiza o total no footer
sed -i '' "s/Total de itens nesta semana: [0-9]*/Total de itens nesta semana: $TOTAL_ITENS/" "$RELATORIO_SEMANAL"

# Atualiza data de atualização
DATA_ATUAL=$(date +"%d/%m/%Y %H:%M")
sed -i '' "s/Atualizado em: [0-9\/: ]*/Atualizado em: $DATA_ATUAL/" "$RELATORIO_SEMANAL"

# ============================================
# 5. Atualiza INDEX se arquivo é novo
# ============================================

INDEX_FILE="$RELATORIOS_DIR/RELATORIO-INDEX.html"

if [ "$ARQUIVO_NOVO" = true ] && [ -f "$INDEX_FILE" ]; then
    # Calcula período da semana para o index
    INICIO_SEMANA_SHORT=$(date -v-$(date +%u)d+1d +"%d %b" 2>/dev/null || date +"%d %b")
    FIM_SEMANA_SHORT=$(date -v-$(date +%u)d+7d +"%d %b" 2>/dev/null || date +"%d %b")

    # Nova entrada para o index
    NOVA_ENTRADA="        <li class=\"semana-item\">
            <a href=\"Semana-$SEMANA-$ANO.html\" class=\"semana-link\">
                <div>
                    <div class=\"semana-nome\">Semana $SEMANA - $ANO</div>
                    <div class=\"semana-periodo\">$INICIO_SEMANA_SHORT - $FIM_SEMANA_SHORT</div>
                </div>
                <div class=\"semana-stats\">
                    <div class=\"semana-contagem\">1</div>
                    <div class=\"semana-label\">itens</div>
                </div>
            </a>
        </li>"

    # Insere após a linha que contém "2026</div>" (header do ano)
    # ou após "semanas-lista" se não encontrar
    if grep -q "ano-header\">$ANO" "$INDEX_FILE" 2>/dev/null; then
        # Encontra a ul.semanas-lista após o ano correspondente e insere
        awk -v entry="$NOVA_ENTRADA" -v ano="$ANO" '
        /ano-header.*>'"$ANO"'/ { found_year = 1 }
        found_year && /semanas-lista/ { found_list = 1 }
        found_list && /<\/ul>/ && !inserted {
            print entry
            inserted = 1
        }
        { print }
        ' "$INDEX_FILE" > "$INDEX_FILE.tmp"

        # Se não inseriu, tenta método alternativo
        if ! grep -q "Semana-$SEMANA-$ANO" "$INDEX_FILE.tmp" 2>/dev/null; then
            # Insere logo após <ul class="semanas-lista"> do ano atual
            awk -v entry="$NOVA_ENTRADA" -v ano="$ANO" '
            /ano-header.*>'"$ANO"'/ { found_year = 1 }
            found_year && /semanas-lista/ && !inserted {
                print
                print entry
                inserted = 1
                next
            }
            { print }
            ' "$INDEX_FILE" > "$INDEX_FILE.tmp"
        fi

        mv "$INDEX_FILE.tmp" "$INDEX_FILE"
    fi

    # Atualiza contador de semanas
    TOTAL_SEMANAS=$(grep -c 'semana-item' "$INDEX_FILE" 2>/dev/null || echo "0")
    sed -i '' "s/<div class=\"stat-numero\">[0-9]*<\/div>\s*<div class=\"stat-label\">Semanas registradas/<div class=\"stat-numero\">$TOTAL_SEMANAS<\/div>\n            <div class=\"stat-label\">Semanas registradas/" "$INDEX_FILE" 2>/dev/null || true

    # Atualiza última atualização no footer
    sed -i '' "s/<strong>Ultima atualizacao:<\/strong> [0-9\/]*/<strong>Ultima atualizacao:<\/strong> $(date +"%d\/%m\/%Y")/" "$INDEX_FILE"
fi

# Atualiza contador de itens da semana no INDEX (mesmo se não é novo)
if [ -f "$INDEX_FILE" ]; then
    # Atualiza o contador da semana específica
    # Encontra a linha com Semana-XX-YYYY e atualiza o contagem
    sed -i '' "/<a href=\"Semana-$SEMANA-$ANO.html\"/,/<\/li>/ s/<div class=\"semana-contagem\">[0-9]*</<div class=\"semana-contagem\">$TOTAL_ITENS</" "$INDEX_FILE" 2>/dev/null || true
fi

# Atualiza Painel Diário no Desktop
PAINEL_SCRIPT="$HOME/.claude/plugins/process-mapper/scripts/gerar-painel-diario.py"
[ -f "$PAINEL_SCRIPT" ] && python3 "$PAINEL_SCRIPT" &

# Injeta relatórios no Planner
PLANNER_SCRIPT="$HOME/.claude/plugins/process-mapper/scripts/injetar-relatorios-planner.py"
[ -f "$PLANNER_SCRIPT" ] && python3 "$PLANNER_SCRIPT" &

# ============================================
# 6. Gera TRANSCRIÇÃO LEGÍVEL automaticamente
# ============================================

CONVERSOR_SCRIPT="$HOME/stemmia-forense/src/utilidades/converter_sessoes_jsonl.py"
JSONL_BACKUP="$SESSAO_DIR/TRANSCRICAO-COMPLETA.jsonl"
TRANSCRICAO_LEGIVEL="$SESSAO_DIR/TRANSCRICAO-LEGIVEL.txt"

if [ -f "$CONVERSOR_SCRIPT" ]; then
    # Tenta usar JSONL de backup (copiado pelo salvar-contexto-bruto.sh)
    if [ -f "$JSONL_BACKUP" ]; then
        python3 "$CONVERSOR_SCRIPT" --jsonl-file "$JSONL_BACKUP" --saida "$SESSAO_DIR" 2>/dev/null
        # Renomeia para nome padrão se gerou
        GERADO=$(ls -t "$SESSAO_DIR"/SESSAO-*.txt 2>/dev/null | head -1)
        if [ -n "$GERADO" ] && [ -f "$GERADO" ]; then
            mv "$GERADO" "$TRANSCRICAO_LEGIVEL" 2>/dev/null
        fi
    else
        # Tenta pegar o JSONL original pelo session_id
        SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // .sessionId // empty' 2>/dev/null)
        if [ -n "$SESSION_ID" ] && [ "$SESSION_ID" != "null" ]; then
            JSONL_ORIGINAL="$HOME/.claude/projects/-Users-$(whoami)/$SESSION_ID.jsonl"
            if [ -f "$JSONL_ORIGINAL" ]; then
                python3 "$CONVERSOR_SCRIPT" --jsonl-file "$JSONL_ORIGINAL" --saida "$SESSAO_DIR" 2>/dev/null
                GERADO=$(ls -t "$SESSAO_DIR"/SESSAO-*.txt 2>/dev/null | head -1)
                if [ -n "$GERADO" ] && [ -f "$GERADO" ]; then
                    mv "$GERADO" "$TRANSCRICAO_LEGIVEL" 2>/dev/null
                fi
            fi
        fi
    fi
fi

# ============================================
# 7. Gera TRANSCRIÇÃO HTML EDITÁVEL
# ============================================

HTML_SCRIPT="$HOME/stemmia-forense/src/utilidades/gerar_transcricao_html.py"

if [ -f "$HTML_SCRIPT" ]; then
    if [ -f "$JSONL_BACKUP" ]; then
        python3 "$HTML_SCRIPT" --jsonl-file "$JSONL_BACKUP" --saida "$SESSAO_DIR" 2>/dev/null
    elif [ -n "$SESSION_ID" ] && [ "$SESSION_ID" != "null" ] && [ -f "$JSONL_ORIGINAL" ]; then
        python3 "$HTML_SCRIPT" --jsonl-file "$JSONL_ORIGINAL" --saida "$SESSAO_DIR" 2>/dev/null
    fi
fi

# ============================================
# 8. Copia plano do Plan Mode (se existir)
# ============================================

PLANS_DIR="$HOME/.claude/plans"
if [ -d "$PLANS_DIR" ]; then
    # Copia o plano mais recente (modificado na última hora)
    PLANO_RECENTE=$(find "$PLANS_DIR" -name "*.md" -mmin -60 2>/dev/null | head -1)
    if [ -n "$PLANO_RECENTE" ] && [ -f "$PLANO_RECENTE" ]; then
        mkdir -p "$SESSAO_DIR/plan-mode"
        cp "$PLANO_RECENTE" "$SESSAO_DIR/plan-mode/" 2>/dev/null
    fi
fi

# Limpa arquivo de sessão atual
rm -f "$SESSAO_ATUAL_FILE"

exit 0
