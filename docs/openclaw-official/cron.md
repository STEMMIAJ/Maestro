# OpenClaw — Cron

## Visao geral
`openclaw cron` gerencia jobs agendados do Gateway. Jobs tem `--name` e **exatamente um** de `--at` (one-shot), `--every` (intervalo) ou `--cron` (expressao cron 5 campos). Payload obrigatorio: **um** entre `--system-event` ou `--message`. Jobs podem rodar em sessao main, isolada, current ou explicita (`session:<id>`). Definicoes vivem em `~/.openclaw/cron/jobs.json`; estado de execucao em `~/.openclaw/cron/jobs-state.json`; logs por job em `~/.openclaw/cron/runs/<jobId>.jsonl`.

## Comandos
```
openclaw cron status [--json]
openclaw cron list [--all] [--json]
openclaw cron add   (alias: create) --name ... <--at|--every|--cron> <--system-event|--message> [flags]
openclaw cron edit <id>
openclaw cron rm <id>   (aliases: remove, delete)
openclaw cron enable <id>
openclaw cron disable <id>
openclaw cron runs --id <id> [--limit <n>]
openclaw cron run <id> [--due]
openclaw cron show <id>     # preview da rota de entrega resolvida
```
Todos aceitam `--url`, `--token`, `--timeout`, `--expect-final` para RPC remoto.

## Flags relevantes de `add`/`edit`
- Sessao: `--session main|isolated|current|session:<id>`.
- Entrega: `--announce` (default em jobs isolados), `--no-deliver`, `--webhook`, `--channel <chan>`, `--to <target>`, `--best-effort-deliver` / `--no-best-effort-deliver`.
- Agente/modelo: `--agent <id>`, `--clear-agent`, `--model <id>` (se nao permitido cai para default do agente).
- Contexto: `--light-context` (isolados apenas; bootstrap minimo).
- Retention: one-shot (`--at`) auto-deleta apos sucesso; `--keep-after-run` preserva.
- Timezone: `--at` sem offset e UTC por default; `--tz <iana>` interpreta como wall-clock local.

## Comportamento operacional
- Jobs recorrentes que falham usam retry exponencial: 30s -> 1m -> 5m -> 15m -> 60m, depois voltam ao agendamento normal.
- `openclaw cron run <job-id>` retorna assim que o run e enfileirado; acompanhe em `openclaw cron runs --id <job-id>`.
- `cron run` e force-run por default. Use `--due` para so executar se estiver vencido.
- Isolated cron suprime replies ack-only: se o primeiro resultado for so status e nao ha subagent descendente responsavel, re-prompta uma vez.
- Retorno `NO_REPLY` / `no_reply` suprime entrega direta e fallback.
- Failure notifications seguem: `delivery.failureDestination` -> `cron.failureDestination` global -> target primario do announce.
- Retention: `cron.sessionRetention` (default `24h`), `cron.runLog.maxBytes` e `cron.runLog.keepLines`.

## Exemplos praticos
```bash
# Job diario com mensagem e entrega silenciosa em sessao isolada
openclaw cron add \
  --name "Brief matinal" \
  --cron "0 7 * * *" \
  --session isolated \
  --message "Resuma atualizacoes overnight." \
  --light-context \
  --no-deliver

# Ajustar canal e target de um job existente
openclaw cron edit <job-id> --announce --channel telegram --to "123456789"

# Forcar uma execucao manual e inspecionar logs
openclaw cron run <job-id>
openclaw cron runs --id <job-id> --limit 50
```

## Relacao com Maestro
- `CRON/00_plan.md` do Maestro lista 7 jobs planejados (J01..J07). Cada um pode virar `openclaw cron add --cron "<expr>" --name "J0X-..." --message "..."`.
- Para migracao gradual: manter launchd atual e criar os cron jobs OpenClaw espelhados com `--no-deliver` ate validar; depois desligar launchd e habilitar entrega.

## Referencia
- Arquivo fonte: `docs/cli/cron.md` e `docs/automation/cron-jobs.md`.
- Commit: `35ec4a9991`.
- Indice CLI: `docs/cli/index.md` secao `cron`.
