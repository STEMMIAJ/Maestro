#!/bin/zsh
set -euo pipefail

HUB="/Users/jesus/Desktop/STEMMIA Dexter"
CONTROLE="$HUB/00-CONTROLE"
PROMPT="$CONTROLE/PROMPT-INICIAL-CLAUDE-CONSISTENTE.md"
ESTADO="$CONTROLE/ESTADO-CLAUDE-ATUAL.md"
LOG="$CONTROLE/LOG-CLAUDE-CONSISTENTE.md"

# Resolver binário do Claude: command -v primeiro, fallbacks conhecidos depois.
CLAUDE_BIN=""
if command -v claude >/dev/null 2>&1; then
  CLAUDE_BIN="$(command -v claude)"
elif [[ -x "$HOME/.local/bin/claude" ]]; then
  CLAUDE_BIN="$HOME/.local/bin/claude"
elif [[ -x "/opt/homebrew/bin/claude" ]]; then
  CLAUDE_BIN="/opt/homebrew/bin/claude"
fi

mkdir -p "$CONTROLE" "$HUB/CONVERSAS"

criar_se_faltar() {
  local arquivo="$1"
  local titulo="$2"
  if [[ ! -f "$arquivo" ]]; then
    {
      echo "# $titulo"
      echo
      echo "Criado automaticamente por ABRIR-CLAUDE-CONSISTENTE.command em $(date '+%Y-%m-%d %H:%M:%S %Z')."
    } > "$arquivo"
  fi
}

criar_se_faltar "$HUB/MEMORIA.md" "MEMORIA.md"
criar_se_faltar "$HUB/DECISOES.md" "DECISOES.md"
criar_se_faltar "$HUB/ROTINA.md" "ROTINA.md"
criar_se_faltar "$CONTROLE/AGORA.md" "AGORA.md"
criar_se_faltar "$CONTROLE/PROTOCOLO-CLAUDE-CONSISTENTE.md" "PROTOCOLO CLAUDE CONSISTENTE"
criar_se_faltar "$ESTADO" "ESTADO CLAUDE ATUAL"

cat > "$PROMPT" <<'PROMPT_CLAUDE'
Leia nesta ordem, antes de responder:

1. /Users/jesus/Desktop/STEMMIA Dexter/MEMORIA.md
2. /Users/jesus/Desktop/STEMMIA Dexter/DECISOES.md
3. /Users/jesus/Desktop/STEMMIA Dexter/ROTINA.md
4. /Users/jesus/Desktop/STEMMIA Dexter/00-CONTROLE/AGORA.md
5. /Users/jesus/Desktop/STEMMIA Dexter/00-CONTROLE/PROTOCOLO-CLAUDE-CONSISTENTE.md
6. /Users/jesus/Desktop/STEMMIA Dexter/00-CONTROLE/ESTADO-CLAUDE-ATUAL.md

Modo obrigatório:
- Português brasileiro.
- Tom técnico, direto e seco.
- Fazer, não explicar em excesso.
- Prioridade: processos judiciais reais, prazos, petições, laudos e quesitos.
- Nunca apagar sem dupla confirmação.
- Nunca dizer "fiz" sem verificar.
- Nunca dizer "corrigido" sem testar ou declarar o limite exato da verificação.
- Se a tarefa for segura e reversível, execute sem perguntar.
- Se houver processo pendente, não começar por site, Obsidian, painel, estética ou plugin.

Responda agora só neste formato:

PRIORIDADE ATUAL:
ARQUIVO DE ESTADO:
O QUE NÃO MEXER AGORA:
PRÓXIMO COMANDO EXATO:
PROMPT_CLAUDE

if command -v pbcopy >/dev/null 2>&1; then
  pbcopy < "$PROMPT"
  CLIPBOARD="prompt copiado para a área de transferência"
else
  CLIPBOARD="pbcopy indisponível; prompt salvo em $PROMPT"
fi

{
  echo
  echo "## $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "- Hub: $HUB"
  echo "- Prompt inicial: $PROMPT"
  echo "- Clipboard: $CLIPBOARD"
  echo "- Claude bin: $CLAUDE_BIN"
} >> "$LOG"

if [[ "${1:-}" == "--check" ]]; then
  echo "OK: launcher validado."
  echo "Hub: $HUB"
  echo "Prompt: $PROMPT"
  echo "$CLIPBOARD"
  if [[ -n "$CLAUDE_BIN" && -x "$CLAUDE_BIN" ]]; then
    echo "Claude bin: $CLAUDE_BIN"
  else
    echo "AVISO: binário claude não encontrado (command -v claude, ~/.local/bin/claude, /opt/homebrew/bin/claude)."
  fi
  exit 0
fi

if [[ -z "$CLAUDE_BIN" || ! -x "$CLAUDE_BIN" ]]; then
  echo "ERRO: binário claude não encontrado."
  echo "Procurado em: command -v claude, \$HOME/.local/bin/claude, /opt/homebrew/bin/claude"
  echo "Prompt inicial salvo em: $PROMPT"
  exit 1
fi

clear
echo "CLAUDE CONSISTENTE"
echo
echo "1. Prompt inicial já copiado."
echo "2. Quando o Claude abrir, cole com Cmd+V e aperte Enter."
echo "3. Se ele enrolar, feche e rode este arquivo de novo."
echo
echo "Hub: $HUB"
echo
cd "$HUB"
exec "$CLAUDE_BIN"
