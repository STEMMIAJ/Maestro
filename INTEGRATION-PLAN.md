# INTEGRATION-PLAN — Maestro (openclaw-control-center)

Roadmap completo Fases 0–8. Atualizado em 2026-04-24 refletindo estado real após sessão 4.

## Estado por fase

| fase | nome | status | % alvo | % real |
|------|------|--------|--------|--------|
| 0 | Plano + time de agentes | **CONCLUÍDA** | 5% | 5% |
| 1 | Captura da conversa | **CONCLUÍDA** | 15% | 12% (placeholder) |
| 2 | Memória operacional | **PARCIAL** | 30% | 20% (gerada, curadoria pendente) |
| 3 | Subprojeto Python conversation_ingestion | **CONCLUÍDA** (esqueletos) | 45% | 40% |
| 4 | Governança: RULES, FLOWS, CRON, CONFIG | **CONCLUÍDA** (enriquecida sessão 4) | 65% | 58% |
| 5 | Documentação oficial OpenClaw | **BLOQUEADA** | 80% | — |
| 6 | Modelos, custos, DB, Telegram, dashboard | **PARCIAL** (relatórios iniciais gerados) | 90% | 70% |
| 7 | TASKS_MASTER completo + progress_snapshot | **PENDENTE** | 95% | — |
| 8 | Relatório final + checkpoint Rodada 1 | **PENDENTE** | 100% | — |

**Panorama atual estimado: ~45–50% da Rodada 1.**

---

## Fase 0 — Plano de ação e time de agentes

**Status: CONCLUÍDA** (Rodada 1, 2026-04-22)

Artefatos criados:
- `AGENTS/*.md` (8 agentes: ORCHESTRATOR, MEMORY-INGESTION-TEAM, DEXTER-AUDITOR, etc.)
- `INTEGRATION-PLAN.md`, `TASKS_MASTER.md`, `TASKS_NOW.md`, `NEXT_SESSION_CONTEXT.md`, `CHANGELOG.md`

---

## Fase 1 — Captura da conversa Perplexity

**Status: CONCLUÍDA** (com ressalva: captura automática falhou; placeholder gerado)

- Conversa Perplexity (URL `bb7372f9-c9d4-4195-9653-e56098864476`, 4440 linhas) intacta no OpenClaw SQLite (138 processos).
- Placeholder em `conversations/raw/perplexity_conversation_2026-04-22_input.md`.
- Log em `logs/conversation_ingestion.log`.
- **Ressalva:** extração automática via MCP chrome não foi possível nesta rodada. Conversa completa disponível no OpenClaw; acesso manual pendente.

---

## Fase 2 — Memória operacional

**Status: PARCIAL**

Executado:
- `MEMORY.md` gerado.
- `memory/2026-04-22.md` gerado.
- `reports/conversation_{master_summary, decisions, open_questions, entities_and_projects, next_actions}.md` — 5 arquivos gerados.

Pendente:
- Curadoria FLOW 03 (primeira rodada após segunda conversa ingerida).
- MEMORY.md com delta claro de sessões posteriores.

---

## Fase 3 — Subprojeto Python (conversation_ingestion)

**Status: CONCLUÍDA** (esqueletos funcionais; implementação completa é backlog)

Localização: `~/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/conversation_ingestion/`

Scripts criados (esqueleto documentado):
- `ingest_conversation.py`
- `chunk_conversation.py`
- `extract_action_items.py`
- `generate_memory_files.py`
- `generate_session_checkpoint.py`

Também criados: `templates/`, `README.md`.

Implementação completa: backlog B006.

---

## Fase 4 — Governança: RULES, FLOWS, CRON, CONFIG

**Status: CONCLUÍDA** (estrutura inicial Rodada 1 + enriquecimento completo sessão 4)

Artefatos:
- `README.md`, `CLAUDE.md`, `OPENCLAW-ARCHITECTURE.md`
- `RULES/` (5 arquivos): naming, scope, privacy, completeness, change_control
- `FLOWS/` (9 arquivos): 00_index + 01–08
- `CRON/` (2 arquivos): 00_plan, dry_run_commands
- `CONFIG/` (2 arquivos): 00_config_plan, openclaw_hooks

Sessão 4 adicionou:
- Pipeline `/pericia` operacional em `Maestro/bin/pericia` (validado).
- Proposta B1 plist em `Maestro/futuro/B1-resolucao.md` (manual, não ativo).
- 4 legados arquivados em `Maestro/legado-bootstrap/`.
- OPÇÃO B selecionada para estrutura de ingestão (ver `NEXT_SESSION_CONTEXT.md`).
- Enriquecimento de todos FLOWS/01–08 com seções: objetivo, entradas, falhas/rollback.
- Enriquecimento de RULES/01–05 com tabelas, exemplos, hierarquia.
- CRON/dry_run_commands.md expandido para todos J01–J07.
- CONFIG/openclaw_hooks.md com referência a `docs/openclaw-official/` e perfil de modelo.

---

## Fase 5 — Documentação oficial OpenClaw

**Status: BLOQUEADA** (aguarda confirmação do Dr. Jesus)

Pré-condição: Dr. Jesus confirma o que é o OpenClaw (ferramenta pública, repo, URL).

Quando desbloqueada:
1. Baixar/copiar docs para `docs/openclaw-official/` (mínimo 8 páginas).
2. Atualizar `reports/openclaw_{capabilities_summary, command_map, for_this_project}.md`.
3. Atualizar sintaxe presumida em `FLOWS/08_integracao_openclaw.md` e `CONFIG/openclaw_hooks.md`.
4. Desbloquear FLOW 08.

---

## Fase 6 — Modelos, custos, DB, Telegram, dashboard

**Status: PARCIAL** (relatórios iniciais gerados na Rodada 1; decisões pendentes)

Executado:
- `reports/{model_options, cost_estimate, database_options, telegram_integration, stemmia_dashboard_plan}_initial.md` — gerados.

Pendente (RESEARCH):
- Decisão sobre DB remoto (Supabase vs alternativo).
- Confirmação de tecnologia frontend para dashboard.
- Bot token Telegram configurado em `~/.config/maestro/secrets.env`.

---

## Fase 7 — TASKS_MASTER completo + progress_snapshot

**Status: PENDENTE**

Entregáveis:
- `TASKS_MASTER.md` completo: todos os ids, dependências, responsáveis, % por tarefa.
- `reports/progress_snapshot.md` atualizado com `%_panorama` calculado.

Próxima sessão: executar FLOW 04 completo após atualizar TASKS_MASTER.

---

## Fase 8 — Relatório final e checkpoint Rodada 1

**Status: PENDENTE**

Entregáveis:
- `reports/execution_report_round1.md` (executado / planejado / pendente / bloqueado).
- `logs/round1_execution_log.md` com cronologia completa.
- `NEXT_SESSION_CONTEXT.md` consolidado com ação mínima da Rodada 2.

---

## Princípios não negociáveis

- Sem acentos / espaços / ç em paths automatizados.
- Não instalar libs ou dependências sem pedido explícito.
- Não configurar cron real, não enviar Telegram, não tocar FTP.
- Não inventar dados. Marcar `[TODO/RESEARCH]` sempre que necessário.
- Diferenciar executado / planejado / pendente / bloqueado em todo relatório.
- Opus 4.7 obrigatório para subagentes.
- Evidência verificável obrigatória para declarar qualquer item "concluído".

## Rollback por fase

| fase | rollback |
|------|---------|
| 0 | Apagar `AGENTS/*.md` + arquivos de controle raiz |
| 1 | Apagar `conversations/raw/perplexity_*.md` + `logs/conversation_ingestion.log` |
| 2 | Apagar `MEMORY.md`, `memory/2026-04-22.md`, `reports/conversation_*.md` |
| 3 | Apagar `PYTHON-BASE/08-SISTEMAS-COMPLETOS/conversation_ingestion/` |
| 4 | Apagar `RULES/`, `FLOWS/`, `CRON/`, `CONFIG/` (estrutura criada nesta fase) |
| 5–8 | Arquivos isolados por fase; mover para `_arquivo/fase_N_rollback_YYYY-MM-DD/` |

Com git: `git revert <commit da fase>` ou `git checkout -- <pasta da fase>`.

<!-- atualizado em 2026-04-24 — sessão 4 -->
