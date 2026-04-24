# FLOW 07 — Coleta para dashboard web

## Objetivo

Agregar metadados locais (processos, tarefas, perícias) em um JSON sem PII e empurrá-los para um DB remoto que alimenta o dashboard público `stemmia.com.br`.

## Gatilho

- Cron J07 (diário 06h55) quando ativo.
- Request on-demand quando o dashboard recarregar.
- Manual: "atualizar dashboard".

## Entradas

| artefato | caminho | observação |
|----------|---------|------------|
| FICHAs de processos | `~/Desktop/ANALISADOR FINAL/processos/*/FICHA.json` | metadados sem PII |
| TASKS_MASTER | `Maestro/TASKS_MASTER.md` | estado Maestro |
| TASKS_NOW | `Maestro/TASKS_NOW.md` | foco atual |
| Logs recentes | `Maestro/logs/` | apenas metadados (data, status, duração) |
| DB endpoint | [TODO/RESEARCH] Supabase ou alternativo | ver `reports/database_options_initial.md` |

## Passos

1. Ler todos `FICHA.json` de processos; extrair: CNJ, status, última atualização — sem nome de paciente.
2. Ler `TASKS_MASTER.md`: extrair totais por status.
3. Ler `TASKS_NOW.md`: extrair top 3 tarefas.
4. Ler `logs/`: extrair última execução de cada FLOW (data + status).
5. Montar JSON agregado `payload_dashboard_YYYY-MM-DD.json` em `reports/`.
6. Validar: nenhum campo com nome real, CPF, CID, diagnóstico.
7. Empurrar para DB via API REST (credenciais em `~/.config/maestro/secrets.env`).
8. Logar HTTP status em `logs/flow_07_YYYY-MM-DD.log`.

## Saídas

| artefato | caminho |
|----------|---------|
| Payload JSON | `reports/payload_dashboard_YYYY-MM-DD.json` |
| Log HTTP | `logs/flow_07_YYYY-MM-DD.log` |
| Dados no DB remoto | [TODO/RESEARCH] tabela `maestro_snapshot` |

## Dashboard — rotas previstas

| rota | conteúdo |
|------|---------|
| `/dashboard-dexter` | estado global STEMMIA Dexter |
| `/dashboard-pericias` | perícias em andamento (sem PII) |
| `/dashboard-maestro` | fases do Maestro + progresso |

## Falhas conhecidas / Rollback

| falha | sintoma | rollback |
|-------|---------|----------|
| PII detectada no JSON | campo com nome real | abortar passo 7; gravar `logs/flow_07_pii_block.log` |
| DB indisponível | HTTP 5xx | logar; manter payload local; retentar no próximo ciclo |
| FICHA.json malformado | JSONDecodeError | pular processo; registrar em log |
| DB não decidido | credenciais ausentes | abortar passo 7; payload salvo em `reports/` |

## Dependências críticas

- DB confirmado: Supabase ou alternativo ([TODO/RESEARCH] — ver `reports/database_options_initial.md`).
- Credenciais: `~/.config/maestro/secrets.env` (modo 600, fora do git).
- Frontend: [TODO/RESEARCH] Next.js / Astro / Eleventy.

## Status

- Planejado.
- Planejamento em `reports/stemmia_dashboard_plan_initial.md`.
- Nenhum código de frontend criado nesta rodada.
- Cron J07: planejado, não ativo.
