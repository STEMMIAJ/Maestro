#!/bin/bash
# Script para salvar transcrição bruta da conversa no CONTEXTO.txt
# Hooks: PreCompact (principal), chamado também pelo finalizar-sessao.sh
#
# COMO FUNCIONA:
# 1. Recebe JSON via stdin com campo "transcript_path" (caminho do JSONL)
# 2. Lê o arquivo .sessao_atual para saber onde salvar
# 3. Parseia o JSONL e extrai: mensagens do usuário, ações do Claude, textos
# 4. Appenda tudo formatado ao CONTEXTO.txt

PLAN_MODE_DIR="$HOME/Desktop/Projetos - Plan Mode"
SESSAO_ATUAL_FILE="$PLAN_MODE_DIR/.sessao_atual"

# Lê JSON do stdin
INPUT=$(cat)

# Tenta extrair transcript_path do JSON (método original)
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty' 2>/dev/null)

# FALLBACK: se não veio transcript_path, busca o .jsonl pelo session_id
if [ -z "$TRANSCRIPT_PATH" ] || [ "$TRANSCRIPT_PATH" = "null" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
    SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // .sessionId // empty' 2>/dev/null)
    if [ -n "$SESSION_ID" ] && [ "$SESSION_ID" != "null" ]; then
        JSONL_DIR="$HOME/.claude/projects/-Users-$(whoami)"
        CANDIDATE="$JSONL_DIR/$SESSION_ID.jsonl"
        if [ -f "$CANDIDATE" ]; then
            TRANSCRIPT_PATH="$CANDIDATE"
        fi
    fi

    # FALLBACK 2: pega o .jsonl modificado mais recentemente
    if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
        JSONL_DIR="$HOME/.claude/projects/-Users-$(whoami)"
        TRANSCRIPT_PATH=$(ls -t "$JSONL_DIR"/*.jsonl 2>/dev/null | head -1)
    fi

    # Se ainda não encontrou, sai
    if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
        exit 0
    fi
fi

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

# Identifica o tipo de evento (PreCompact ou SessionEnd)
HOOK_EVENT=$(echo "$INPUT" | jq -r '.hook_event_name // "unknown"' 2>/dev/null)
TRIGGER=$(echo "$INPUT" | jq -r '.trigger // ""' 2>/dev/null)
if [ "$HOOK_EVENT" = "PreCompact" ]; then
    EVENT_LABEL="PreCompact"
    [ -n "$TRIGGER" ] && EVENT_LABEL="PreCompact-$TRIGGER"
else
    EVENT_LABEL="SessionEnd"
fi

# Marca de timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")

# Inicia a seção de transcrição
{
    echo ""
    echo "==============================================================================="
    echo "TRANSCRIÇÃO SALVA EM: $TIMESTAMP ($EVENT_LABEL)"
    echo "==============================================================================="
    echo ""
} >> "$CONTEXTO_FILE"

# Processa o JSONL linha por linha
# Formato JSONL (v2): .type = "user"/"assistant", mensagem em .message.content
# Formato JSONL (v1 legado): .type = "human"/"assistant", conteúdo em .content
while IFS= read -r line; do
    # Ignora linhas vazias
    [ -z "$line" ] && continue

    # Extrai tipo do objeto
    TYPE=$(echo "$line" | jq -r '.type // empty' 2>/dev/null)

    # Processa mensagens de usuário
    if [ "$TYPE" = "user" ] || [ "$TYPE" = "human" ]; then
        # Formato v2: .message.content | Formato v1: .content
        TEXT=$(echo "$line" | jq -r '
            if .message then
                if (.message.content | type) == "string" then
                    .message.content
                elif (.message.content | type) == "array" then
                    [.message.content[] | select(.type == "text") | .text] | join(" ")
                else
                    ""
                end
            elif .content then
                if (.content | type) == "string" then
                    .content
                elif (.content | type) == "array" then
                    [.content[] | select(.type == "text") | .text] | join(" ")
                else
                    ""
                end
            else
                ""
            end
        ' 2>/dev/null)

        if [ -n "$TEXT" ] && [ "$TEXT" != "null" ] && [ "$TEXT" != "" ]; then
            MSG_TIME=$(echo "$line" | jq -r '.timestamp // empty' 2>/dev/null)
            if [ -n "$MSG_TIME" ] && [ "$MSG_TIME" != "null" ]; then
                MSG_TIME=$(echo "$MSG_TIME" | sed 's/T/ /' | cut -d'.' -f1 | cut -d' ' -f2 | cut -c1-5)
            else
                MSG_TIME="--:--"
            fi

            TEXT_TRUNCATED=$(echo "$TEXT" | head -c 1000)
            [ ${#TEXT} -gt 1000 ] && TEXT_TRUNCATED="${TEXT_TRUNCATED}..."

            echo "[$MSG_TIME] USUÁRIO: $TEXT_TRUNCATED" >> "$CONTEXTO_FILE"
            echo "" >> "$CONTEXTO_FILE"
        fi
    fi

    # Processa mensagens do assistente (Claude)
    if [ "$TYPE" = "assistant" ]; then
        MSG_TIME=$(echo "$line" | jq -r '.timestamp // empty' 2>/dev/null)
        if [ -n "$MSG_TIME" ] && [ "$MSG_TIME" != "null" ]; then
            MSG_TIME=$(echo "$MSG_TIME" | sed 's/T/ /' | cut -d'.' -f1 | cut -d' ' -f2 | cut -c1-5)
        else
            MSG_TIME="--:--"
        fi

        # Formato v2: .message.content[] | Formato v1: .content[]
        CONTENT_PATH=".message.content[]?"
        echo "$line" | jq -c "$CONTENT_PATH // empty" 2>/dev/null | while IFS= read -r content_item; do
            [ -z "$content_item" ] && continue

            CONTENT_TYPE=$(echo "$content_item" | jq -r '.type // empty' 2>/dev/null)

            if [ "$CONTENT_TYPE" = "text" ]; then
                TEXT=$(echo "$content_item" | jq -r '.text // empty' 2>/dev/null)
                if [ -n "$TEXT" ] && [ "$TEXT" != "null" ]; then
                    TEXT_TRUNCATED=$(echo "$TEXT" | head -c 500)
                    [ ${#TEXT} -gt 500 ] && TEXT_TRUNCATED="${TEXT_TRUNCATED}..."
                    echo "[$MSG_TIME] CLAUDE (texto): $TEXT_TRUNCATED" >> "$CONTEXTO_FILE"
                    echo "" >> "$CONTEXTO_FILE"
                fi
            fi

            if [ "$CONTENT_TYPE" = "tool_use" ]; then
                TOOL_NAME=$(echo "$content_item" | jq -r '.name // empty' 2>/dev/null)

                case "$TOOL_NAME" in
                    Write|Read|Edit)
                        TOOL_INPUT=$(echo "$content_item" | jq -r '.input.file_path // empty' 2>/dev/null)
                        ;;
                    Bash)
                        TOOL_INPUT=$(echo "$content_item" | jq -r '.input.command // empty' 2>/dev/null)
                        TOOL_INPUT=$(echo "$TOOL_INPUT" | head -c 200)
                        ;;
                    Grep|Glob)
                        TOOL_INPUT=$(echo "$content_item" | jq -r '.input.pattern // empty' 2>/dev/null)
                        ;;
                    WebFetch|WebSearch)
                        TOOL_INPUT=$(echo "$content_item" | jq -r '.input.url // .input.query // empty' 2>/dev/null)
                        ;;
                    Task)
                        TOOL_INPUT=$(echo "$content_item" | jq -r '.input.description // empty' 2>/dev/null)
                        ;;
                    *)
                        TOOL_INPUT=$(echo "$content_item" | jq -r '.input | keys[0] as $k | .[$k] // empty' 2>/dev/null)
                        ;;
                esac

                if [ -n "$TOOL_NAME" ] && [ "$TOOL_NAME" != "null" ]; then
                    if [ -n "$TOOL_INPUT" ] && [ "$TOOL_INPUT" != "null" ]; then
                        echo "[$MSG_TIME] CLAUDE ($TOOL_NAME): $TOOL_INPUT" >> "$CONTEXTO_FILE"
                    else
                        echo "[$MSG_TIME] CLAUDE ($TOOL_NAME)" >> "$CONTEXTO_FILE"
                    fi
                fi
            fi
        done

        # Fallback v1: se .message não existe, tenta .content[]
        if ! echo "$line" | jq -e '.message' >/dev/null 2>&1; then
            echo "$line" | jq -c '.content[]? // empty' 2>/dev/null | while IFS= read -r content_item; do
                [ -z "$content_item" ] && continue
                CONTENT_TYPE=$(echo "$content_item" | jq -r '.type // empty' 2>/dev/null)
                if [ "$CONTENT_TYPE" = "text" ]; then
                    TEXT=$(echo "$content_item" | jq -r '.text // empty' 2>/dev/null)
                    if [ -n "$TEXT" ] && [ "$TEXT" != "null" ]; then
                        TEXT_TRUNCATED=$(echo "$TEXT" | head -c 500)
                        [ ${#TEXT} -gt 500 ] && TEXT_TRUNCATED="${TEXT_TRUNCATED}..."
                        echo "[$MSG_TIME] CLAUDE (texto): $TEXT_TRUNCATED" >> "$CONTEXTO_FILE"
                        echo "" >> "$CONTEXTO_FILE"
                    fi
                fi
            done
        fi
    fi

done < "$TRANSCRIPT_PATH"

echo "" >> "$CONTEXTO_FILE"

# Copia JSONL original como backup íntegro
if [ -n "$TRANSCRIPT_PATH" ] && [ -f "$TRANSCRIPT_PATH" ]; then
    cp "$TRANSCRIPT_PATH" "$SESSAO_DIR/TRANSCRICAO-COMPLETA.jsonl" 2>/dev/null
fi

exit 0
