---
titulo: Jobs do OpenClaw — convenções e ciclo de vida
tipo: readme_tecnico
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
---

# 14_automation/openclaw_jobs

Pasta reservada às **definições declarativas de jobs** executados pelo OpenClaw (memória Markdown). O OpenClaw funciona como Maestro Control Center: indexa Markdown, permite busca semântica e, via jobs, executa rotinas periódicas de leitura/promoção/revisão sobre a base deste repositório.

## Definição de "job"

Um job é um arquivo Markdown (ou YAML dentro de `.openclaw/jobs/` futuramente) que descreve:

- **nome**: slug estável (`reindex-daily`, `promote-memory-weekly`)
- **trigger**: `manual`, `cron`, `on_commit`, `on_inbox_change`
- **input**: pastas/globs de leitura (`15_memory/**`, `16_inbox/**`)
- **operation**: `index`, `search`, `promote`, `review`, `digest`
- **output**: destino (`13_reports/master_summaries/` ou `15_memory/promoted/`)
- **schedule**: cron expr (quando trigger=cron)
- **owner**: Dr. Jesus / Maestro / Claude Code (quem assina o resultado)

## Ciclo de vida

1. **Rascunho** — job descrito aqui, ainda não registrado no OpenClaw.
2. **Registrado** — referenciado por `openclaw memory index` / `openclaw memory search`.
3. **Ativo** — executa via cron (launchd no macOS) ou gatilho.
4. **Monitorado** — resultado gravado em `13_reports/`.
5. **Aposentado** — job movido para `_archive/` mantendo histórico.

## Regras

- Nenhum job executa antes de revisão manual do Dr. Jesus.
- Jobs destrutivos (move/delete) são **proibidos** nesta base; apenas leitura e criação de novos arquivos.
- Todo job gera log em `13_reports/automation_logs/YYYY-MM-DD_<slug>.md`.

## Jobs previstos (TODO)

- `reindex-daily` — `openclaw memory index` sobre `15_memory/` e `12_sources/`.
- `digest-weekly` — resumo dos últimos 7 dias de `16_inbox/` para `13_reports/`.
- `stale-sweep-quarterly` — detectar READMEs não tocados há 90 dias.
- `promotion-review` — sugerir promoção de `16_inbox/raw_conversations/` para `15_memory/promoted/`.

## Ver também

- `14_automation/ingestion_pipelines/README.md`
- `13_reports/master_summaries/maestro_operational_model.md`
