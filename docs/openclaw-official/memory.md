# OpenClaw — Memory

## Visao geral
Memoria do OpenClaw e busca semantica (vector + embedding) sobre `MEMORY.md` e arquivos em `memory/*.md` do workspace do agente. A implementacao e fornecida pelo plugin ativo no slot `plugins.slots.memory` (default: `memory-core`; `"none"` desativa). Existem duas camadas: **short-term** (arquivos diarios `memory/YYYY-MM-DD.md`) e **long-term** (`MEMORY.md`, alimentado por "promotion"/"dreaming").

## Comandos
Todos sob `openclaw memory`:

- `memory status [--deep] [--index] [--fix] [--agent <id>] [--verbose] [--json]` — stats do indice; `--deep` checa vector+embedding; `--fix` repara locks de recall e metadados de promotion; `--index` forca reindex se sujo.
- `memory index [--force] [--agent <id>] [--verbose]` — reindexa arquivos.
- `memory search "<query>" [--max-results <n>] [--min-score <n>] [--agent <id>] [--json]` — busca semantica. Aceita `--query <text>` no lugar do positional.
- `memory promote [--apply] [--limit <n>] [--min-score <n>] [--min-recall-count <n>] [--min-unique-queries <n>] [--include-promoted] [--agent <id>] [--json]` — ranqueia candidatos do short-term e, com `--apply`, anexa ao `MEMORY.md` marcando como promovidos.
- `memory promote-explain <selector> [--agent <id>] [--include-promoted] [--json]` — explica o score de um candidato.
- `memory rem-harness [--path <file-or-dir>] [--grounded] [--agent <id>] [--include-promoted] [--json]` — preview das reflexoes REM sem escrever.
- `memory rem-backfill --path <file-or-dir> [--stage-short-term] [--rollback] [--rollback-short-term]` — escreve/remove diary entries em `DREAMS.md`.

## Dreaming
Sistema de consolidacao em background. Habilitar via:
```json
{
  "plugins": { "entries": { "memory-core": { "config": { "dreaming": { "enabled": true } } } } }
}
```
Tres fases sequenciais: **light** (staging), **REM** (reflexao, escreve em `DREAMS.md`), **deep** (promocao durable para `MEMORY.md`). Toggle in-chat: `/dreaming on|off|status`. Sweep default: `0 3 * * *` (gerenciado pelo proprio `memory-core`, sem `cron add` manual). Thresholds default do deep: `minScore=0.8`, `minRecallCount=3`, `minUniqueQueries=3`, `recencyHalfLifeDays=14`, `maxAgeDays=30`.

## Exemplos praticos
```bash
# Reindexar e buscar
openclaw memory index --force
openclaw memory search "roteiro pericia osteoartrose"

# Preview de promocao e aplicar com thresholds mais frouxos
openclaw memory promote --limit 10 --min-score 0.75
openclaw memory promote --apply

# Diagnostico profundo do vetor
openclaw memory status --deep --json
```

## Relacao com Maestro
- Maestro mantem memoria em markdown puro (`memory/YYYY-MM-DD.md`, `MEMORY.md`). O layout e compativel com o que `memory-core` espera.
- Se o Gateway OpenClaw for ativado com `workspace.dir` apontando para o diretorio do Maestro, `memory index` ja passa a indexar os mesmos arquivos.
- O promotion loop (dreaming) do OpenClaw pode, opcionalmente, assumir a consolidacao automatica do short-term que hoje e manual.

## Referencia
- Arquivo fonte: `docs/cli/memory.md` e `docs/concepts/memory*.md`.
- Commit: `35ec4a9991` (github.com/openclaw/openclaw).
- Conceito: https://docs.openclaw.ai/concepts/memory e https://docs.openclaw.ai/concepts/dreaming.
