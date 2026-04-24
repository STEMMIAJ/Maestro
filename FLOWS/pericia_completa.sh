#!/usr/bin/env bash
# pericia_completa.sh — wrapper /pericia [CNJ]
# Encadeia pipeline legado (extraction -> analise -> consolidacao -> honorarios -> indexacao).
# NAO faz download PJe (requer Parallels/Windows). Input: CNJ ja baixado em processos/.
#
# Uso:
#   ./pericia_completa.sh <CNJ>
#   ./pericia_completa.sh <CNJ> --skip-indexacao
#   ./pericia_completa.sh <CNJ> --pular-triagem
#
# Fail-fast: se qualquer etapa retornar != 0, aborta e reporta.
# Log completo em Maestro/logs/pericia-<CNJ>-<timestamp>.log.

set -u  # var nao-definida => erro. NAO uso -e pra controlar erros por etapa.

CNJ="${1:-}"
if [ -z "$CNJ" ]; then
  echo "Uso: $0 <CNJ> [--skip-indexacao] [--pular-triagem]" >&2
  echo "Exemplo: $0 5008297-73.2025.8.13.0105" >&2
  exit 2
fi
shift

SKIP_INDEXACAO=0
PULAR_TRIAGEM=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --skip-indexacao) SKIP_INDEXACAO=1 ;;
    --pular-triagem) PULAR_TRIAGEM=1 ;;
    --dry-run) DRY_RUN=1 ;;
    *) echo "[WARN] flag desconhecida: $arg" >&2 ;;
  esac
done

# --- Paths ---
DEXTER="/Users/jesus/Desktop/STEMMIA Dexter"
ANALISADOR="/Users/jesus/Desktop/ANALISADOR FINAL"
PROCESSOS="$ANALISADOR/processos"
SCRIPTS_ANALISE="$ANALISADOR/analisador de processos"
TRIAR_PDF="$DEXTER/src/automacoes/triar_pdf.py"
INDEXER="$DEXTER/Maestro/banco-local/indexer_ficha.py"
LOGDIR="$DEXTER/Maestro/logs"

PASTA="$PROCESSOS/$CNJ"
TS=$(date "+%Y%m%d-%H%M%S")
LOG="$LOGDIR/pericia-$CNJ-$TS.log"

# --- Helpers ---
say() {
  echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"
}

etapa() {
  local nome="$1"
  shift
  say "────── ETAPA: $nome ──────"
  say "CMD: $*"
  "$@" 2>&1 | tee -a "$LOG"
  local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then
    say "[FAIL] $nome retornou $rc. Abortando."
    say "Log: $LOG"
    exit "$rc"
  fi
  say "[OK] $nome"
}

mkdir -p "$LOGDIR"
say "╔══════════════════════════════════════════════════════════╗"
say "║ PERICIA COMPLETA — CNJ: $CNJ"
say "║ Log: $LOG"
[ "$DRY_RUN" -eq 1 ] && say "║ MODO: dry-run (so verifica deps + pasta, nao executa)"
say "╚══════════════════════════════════════════════════════════╝"

# --- Pre-check pasta ---
if [ ! -d "$PASTA" ]; then
  say "[FAIL] Pasta nao existe: $PASTA"
  say "Opcoes: (a) baixar via sincronizar_aj_pje.py (requer Parallels) (b) criar pasta + colocar PDF manualmente"
  exit 1
fi
say "[OK] Pasta processo: $PASTA"

# --- Pre-check dependencias (sempre roda; em dry-run sai aqui) ---
say "────── PRE-CHECK DEPENDENCIAS ──────"
DEPS_OK=1
for dep in "$TRIAR_PDF" \
           "$SCRIPTS_ANALISE/pipeline_analise.py" \
           "$SCRIPTS_ANALISE/consolidar_ficha.py" \
           "$SCRIPTS_ANALISE/calcular_honorarios.py" \
           "$INDEXER"; do
  if [ -f "$dep" ]; then
    say "[OK] dep: $dep"
  else
    say "[MISS] dep: $dep"
    DEPS_OK=0
  fi
done

if [ "$DEPS_OK" -eq 0 ]; then
  say "[FAIL] dependencias faltando — pipeline nao roda"
  exit 3
fi

# Conteudo da pasta
PDF_COUNT=$(find "$PASTA" -maxdepth 2 -iname "*.pdf" 2>/dev/null | wc -l | tr -d ' ')
TXT_OK=$([ -f "$PASTA/TEXTO-EXTRAIDO.txt" ] && echo "sim" || echo "nao")
FICHA_OK=$([ -f "$PASTA/FICHA.json" ] && echo "sim" || echo "nao")
say "[INFO] PDFs na pasta: $PDF_COUNT | TEXTO-EXTRAIDO.txt: $TXT_OK | FICHA.json: $FICHA_OK"

if [ "$DRY_RUN" -eq 1 ]; then
  say "[DRY-RUN OK] tudo verificado, nada executado. Saindo."
  exit 0
fi

# Detectar se PDF ja foi extraido
TEM_TXT=0
if [ -f "$PASTA/TEXTO-EXTRAIDO.txt" ]; then
  TEM_TXT=1
  say "TEXTO-EXTRAIDO.txt ja existe ($(wc -l < "$PASTA/TEXTO-EXTRAIDO.txt") linhas)"
fi

# --- Etapa 1: triar/enriquecer (extrai texto + cria FICHA esqueleto) ---
if [ "$PULAR_TRIAGEM" -eq 1 ]; then
  say "[SKIP] triagem (flag --pular-triagem)"
elif [ "$TEM_TXT" -eq 1 ]; then
  say "[SKIP] triar_pdf — TEXTO-EXTRAIDO.txt ja existe"
else
  etapa "1/5 triar_pdf enriquecer" \
    python3 "$TRIAR_PDF" enriquecer --pasta "$PASTA"
fi

# --- Etapa 2: analise paralela (5 scripts) ---
cd "$SCRIPTS_ANALISE" || { say "[FAIL] cd $SCRIPTS_ANALISE"; exit 1; }

etapa "2/5 pipeline_analise" \
  python3 pipeline_analise.py "$PASTA"

# --- Etapa 3: consolidar JSONs de analise -> FICHA.json ---
etapa "3/5 consolidar_ficha" \
  python3 consolidar_ficha.py "$PASTA"

# --- Etapa 4: calcular honorarios (usa FICHA consolidada) ---
# calcular_honorarios aceita --processo <FICHA.json>
etapa "4/5 calcular_honorarios" \
  python3 calcular_honorarios.py --processo "$PASTA/FICHA.json"

# --- Etapa 5: indexar em maestro.db ---
if [ "$SKIP_INDEXACAO" -eq 1 ]; then
  say "[SKIP] indexacao (flag --skip-indexacao)"
else
  etapa "5/5 indexer_ficha" \
    python3 "$INDEXER" --source "$PASTA"
fi

# --- Resumo ---
say "╔══════════════════════════════════════════════════════════╗"
say "║ PIPELINE COMPLETO — $CNJ"
say "║ Log: $LOG"
say "║ FICHA: $PASTA/FICHA.json"
say "╚══════════════════════════════════════════════════════════╝"

# Notificacao macOS (Glass)
osascript -e "display notification \"Pipeline concluido: $CNJ\" with title \"Maestro\" sound name \"Glass\"" 2>/dev/null || true

exit 0
