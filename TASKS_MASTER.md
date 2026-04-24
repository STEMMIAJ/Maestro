# TASKS_MASTER — openclaw-control-center

Rodada 1 — 2026-04-22.

Campos: id | fase | descricao | status | %

| id | fase | descricao curta | status | % contrib |
|----|------|-----------------|--------|-----------|
| T001 | F0 | Criar AGENTS/ (8 arquivos) | concluida | 4 |
| T002 | F0 | Criar INTEGRATION-PLAN.md | concluida | 1 |
| T003 | F0 | Criar TASKS_MASTER.md | concluida | 1 |
| T004 | F0 | Criar TASKS_NOW.md | concluida | 1 |
| T005 | F0 | Criar NEXT_SESSION_CONTEXT.md | concluida | 1 |
| T006 | F0 | Criar CHANGELOG.md | concluida | 1 |
| T007 | F1 | Tentar captura automatica Perplexity | concluida (bloqueada:403) | 1 |
| T008 | F1 | Criar placeholder conversations/raw/..._input.md | concluida | 2 |
| T009 | F1 | Criar logs/conversation_ingestion.log | concluida | 1 |
| T010 | F2 | Criar MEMORY.md | concluida | 3 |
| T011 | F2 | Criar memory/2026-04-22.md | concluida | 2 |
| T012 | F2 | reports/conversation_master_summary.md | concluida | 2 |
| T013 | F2 | reports/conversation_decisions.md | concluida | 2 |
| T014 | F2 | reports/conversation_open_questions.md | concluida | 2 |
| T015 | F2 | reports/conversation_entities_and_projects.md | concluida | 2 |
| T016 | F2 | reports/conversation_next_actions.md | concluida | 2 |
| T017 | F3 | conversation_ingestion/README.md | concluida | 2 |
| T018 | F3 | ingest_conversation.py (esqueleto) | concluida | 2 |
| T019 | F3 | chunk_conversation.py (esqueleto) | concluida | 2 |
| T020 | F3 | extract_action_items.py (esqueleto) | concluida | 2 |
| T021 | F3 | generate_memory_files.py (esqueleto) | concluida | 2 |
| T022 | F3 | generate_session_checkpoint.py (esqueleto) | concluida | 2 |
| T023 | F3 | templates/ (3 templates) | concluida | 2 |
| T024 | F4 | README.md OCCC | concluida | 2 |
| T025 | F4 | CLAUDE.md OCCC | concluida | 2 |
| T026 | F4 | OPENCLAW-ARCHITECTURE.md | concluida | 3 |
| T027 | F4 | RULES/ (arquivos base) | concluida | 2 |
| T028 | F4 | FLOWS/ (01..08) | concluida | 3 |
| T029 | F4 | CRON/ (planejado) | concluida | 2 |
| T030 | F4 | CONFIG/ (planejado) | concluida | 2 |
| T031 | F5 | docs/openclaw-official/ 8 paginas | parcial (RESEARCH) | 5 |
| T032 | F5 | reports/openclaw_capabilities_summary.md | concluida | 2 |
| T033 | F5 | reports/openclaw_command_map.md | concluida | 2 |
| T034 | F5 | reports/openclaw_for_this_project.md | concluida | 2 |
| T035 | F6 | reports/model_options_initial.md | concluida | 3 |
| T036 | F6 | reports/cost_estimate_initial.md | concluida | 2 |
| T037 | F6 | reports/database_options_initial.md | concluida | 2 |
| T038 | F6 | reports/telegram_integration_initial.md | concluida | 2 |
| T039 | F6 | reports/stemmia_dashboard_plan_initial.md | concluida | 2 |
| T040 | F7 | reports/progress_snapshot.md | concluida | 2 |
| T041 | F8 | reports/execution_report_round1.md | concluida | 2 |
| T042 | F8 | logs/round1_execution_log.md | concluida | 2 |
| T043 | F8 | NEXT_SESSION_CONTEXT.md consolidado | concluida | 2 |

Total contributivo planejado: 100%.

## Tarefas fora da rodada 1 (backlog)
- B001 Colar conversa Perplexity integral em conversations/raw/perplexity_conversation_2026-04-22_input.md e reexecutar pipeline.
- B002 Baixar documentacao oficial OpenClaw (quando URL/fonte confirmada).
- B003 Implementar Python ingestion real (alem do esqueleto).
- B004 Definir modelo de custo final (Opus 4.7 via API sim/nao).
- B005 Escolher banco de dados (Supabase x alternativas).
- B006 Desenhar dashboard Stemmia (wireframes).
- B007 Configurar bot Telegram Stemmia.
- B008 Migrar pastas orfas detectadas em DEXTER-AUDITOR.
- B009 Ativar cron OpenClaw (apos validacao manual).
- B010 Integracao com banco-de-dados de laudos existente.
