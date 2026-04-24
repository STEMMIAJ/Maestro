# OpenClaw — Tasks

## Visao geral
**Tasks** sao o **ledger de atividade** do OpenClaw: registros de trabalho que roda **fora** da sessao principal de conversa — runs ACP, spawns de subagent, execucoes de cron isoladas e operacoes CLI. Tasks **nao sao** um scheduler: cron e heartbeat decidem QUANDO; tasks registram O QUE aconteceu, quando, e com qual desfecho. Heartbeats e chat normal nao criam tasks.

Persistencia: SQLite em `$OPENCLAW_STATE_DIR/tasks/runs.sqlite`. Retencao: 7 dias apos estado terminal, depois prune automatico.

## Ciclo de vida
```
queued -> running -> { succeeded | failed | timed_out | cancelled | lost }
```
- `lost`: runtime autoritativo some por mais de 5 minutos.
- Transicoes sao automaticas (start/end/error do run do agente atualiza o task).

## Fontes que criam task
| Fonte                    | runtime    | Notify policy default |
| ------------------------ | ---------- | --------------------- |
| ACP background runs      | `acp`      | `done_only`           |
| Subagent orchestration   | `subagent` | `done_only`           |
| Cron jobs (todos)        | `cron`     | `silent`              |
| `openclaw agent` via GW  | `cli`      | `silent`              |
| `video_generate`         | `cli`      | `silent`              |

## Comandos
```bash
openclaw tasks list [--runtime acp|subagent|cron|cli] [--status <s>] [--json]
openclaw tasks show <lookup>                 # aceita taskId, runId, ou sessionKey
openclaw tasks cancel <lookup>               # mata sessao filha (ACP/subagent) ou marca cancelled
openclaw tasks notify <lookup> <done_only|state_changes|silent>
openclaw tasks audit [--json]                # stale/lost/delivery_failed/cleanup
openclaw tasks maintenance [--apply] [--json]
openclaw tasks flow list|show|cancel         # orquestracao TaskFlow acima de tasks
```

Colunas de `tasks list`: Task ID, Kind, Status, Delivery, Run ID, Child Session, Summary.

## Entrega de notificacoes
Dois paths em estado terminal:
1. **Direct delivery** — se o task tem `requesterOrigin` (canal), a conclusao vai direto (Telegram/Discord/Slack/etc.). Subagent completions preservam thread/topic binding.
2. **Session-queued delivery** — se direct falhar ou nao houver origin, vira system event na sessao do requester e aparece no proximo heartbeat.

Completion dispara heartbeat wake imediato — sem precisar aguardar o tick agendado.

## Audit
`openclaw tasks audit` detecta:
- `stale_queued` (>10 min em queued) — warn
- `stale_running` (>30 min em running) — error
- `lost` — error
- `delivery_failed` (com policy != silent) — warn
- `missing_cleanup` — warn
- `inconsistent_timestamps` — warn

Achados aparecem tambem em `openclaw status`.

## Exemplos praticos
```bash
# Panorama geral
openclaw tasks list
openclaw tasks list --runtime cron --status running

# Investigar um run
openclaw tasks show 01JB...  --json
openclaw tasks audit --json

# Aumentar verbosidade de um task em andamento
openclaw tasks notify 01JB... state_changes

# Preview e aplicar maintenance
openclaw tasks maintenance
openclaw tasks maintenance --apply
```

## Relacao com Maestro
- Maestro mantem `TASKS_MASTER.md` e `TASKS_NOW.md` como tarefas **humanas** (backlog + foco atual). O modelo tem outra granularidade: items duram dias/semanas, nao minutos.
- `openclaw tasks` e ledger de **execucoes** (minutos). Sao camadas **complementares**, nao concorrentes.
- Integracao sugerida: quando um job do Maestro for executavel (cron/ACP/subagent), logar o `taskId` no proprio TASKS_NOW.md para rastreabilidade.

## Referencia
- Arquivo fonte: `docs/automation/tasks.md` e `docs/cli/index.md` (secao `tasks`).
- Relacionados: `docs/automation/taskflow.md`, `docs/automation/cron-jobs.md`, `docs/gateway/heartbeat.md`.
- Commit: `35ec4a9991`.
