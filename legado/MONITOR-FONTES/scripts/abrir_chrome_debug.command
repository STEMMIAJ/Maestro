#!/bin/bash
# Abre Chrome com perfil dedicado para automacao AJ/AJG (porta 9223)
# Duplo-click para executar.

set -e

PERFIL="$HOME/Library/Application Support/Google/Chrome-Monitor-Fontes"
mkdir -p "$PERFIL"

# Mata instancias anteriores do mesmo perfil (libera lock)
pkill -f "Chrome-Monitor-Fontes" 2>/dev/null || true
sleep 1

# Remove locks orfaos
rm -f "$PERFIL/Singleton"* 2>/dev/null || true

open -na "Google Chrome" --args \
  --remote-debugging-port=9223 \
  --user-data-dir="$PERFIL" \
  --no-first-run \
  --no-default-browser-check \
  "https://aj.tjmg.jus.br/aj/internet/pendenciasinternet.jsf" \
  "https://ajg.cjf.jus.br/ajg2/internet/pendenciasinternet.jsf"

sleep 2

# Confirma que a porta respondeu
if curl -s --max-time 3 "http://127.0.0.1:9223/json/version" > /dev/null; then
    echo "✓ Chrome debug 9223 ATIVO"
    echo ""
    echo "Agora:"
    echo "  1. Logar em AJ TJMG (aba 1) com CPF e senha"
    echo "  2. Logar em AJG (aba 2) com CPF e senha"
    echo "  3. Deixar Chrome aberto"
    echo ""
    echo "Pode fechar este terminal."
else
    echo "✗ Porta 9223 nao respondeu — Chrome nao iniciou com flag debug"
    echo "  Tentar fechar todas as instancias do Chrome manualmente e rodar de novo"
fi
