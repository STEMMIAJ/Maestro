# Proximas acoes — 2026-04-22

Fonte: `conversations/raw/perplexity_conversation_2026-04-22_full.md`.

Divididas em blocos por horizonte de tempo.

## Imediatas (hoje)

1. Confirmar que a conversa bruta esta salva em
   `conversations/raw/perplexity_conversation_2026-04-22_full.md`
   (4440 linhas, ~140k chars). [OK — ja existe.]
2. Validar que os 7 arquivos de sintese existem e estao coerentes:
   - `MEMORY.md`
   - `memory/2026-04-22.md`
   - `reports/conversation_master_summary.md`
   - `reports/conversation_decisions.md`
   - `reports/conversation_open_questions.md`
   - `reports/conversation_entities_and_projects.md`
   - `reports/conversation_next_actions.md` (este arquivo).
3. Atualizar `TASKS_NOW.md` e `CHANGELOG.md` para refletir o estado
   pos-ingestao.
4. Atualizar `NEXT_SESSION_CONTEXT.md` com passos curtos para retomar.
5. Decidir se o projeto ja pode ser renomeado `Maestro` ->
   `Maestro`.

## Proximas (esta semana)

1. Rodada 2 no Claude Code: popular arquivos de agentes e regras com
   base no conteudo extraido da conversa (Fase 4 do comando-mestre).
2. Localizar a pasta Python base dentro de `STEMMIA Dexter` e criar
   subprojeto `conversation_ingestion/` com scripts-placeholder e
   templates.
3. Baixar docs oficiais do OpenClaw em `docs/openclaw-official/`
   (CLI, memory, dashboard, cron, agents, tasks, status/health,
   plugins/hooks). Gerar `openclaw_capabilities_summary.md`,
   `openclaw_command_map.md`, `openclaw_for_this_project.md`.
4. Rodar validacao seca do OpenClaw:
   - `openclaw doctor`
   - `openclaw status`
   - `openclaw health`
   - `openclaw memory status`
   - `openclaw cron status`
   - `openclaw dashboard --no-open`
   Registrar resultados em `CONFIG/openclaw.profile.md`.
5. Gerar relatorios iniciais, sem inventar numeros:
   - `reports/model_options_initial.md` (incluir seccao Opus 4.7 via API).
   - `reports/cost_estimate_initial.md`.
   - `reports/database_options_initial.md` (Supabase x alternativas).
   - `reports/telegram_integration_initial.md`.
   - `reports/stemmia_dashboard_plan_initial.md`.
6. Iniciar inventario da pasta `STEMMIA Dexter` (agente
   `DEXTER-AUDITOR`): listar subpastas, arquivos orfaos, duplicacoes,
   markdowns obsoletos. Nao apagar nem mover — apenas relatorio.

## Futuras (quando OpenClaw estiver rodando)

1. Ativar cron real para jobs diarios/semanais:
   - auditoria Dexter
   - revisao de memoria
   - deteccao de projetos parados
   - geracao de relatorio de progresso.
2. Subir dashboard nativo do OpenClaw como UI inicial.
3. Projetar dashboard propria em `stemmia.com.br`:
   - rotas, componentes, autenticacao.
   - reaproveitar design do Planner Stemmia.
4. Conectar bot Stemmia (Telegram) para notificacoes e relatorios.
5. Escolher e instalar DB (Supabase x alternativa) apos relatorio.
6. Estabelecer politica de backup local + backup site.
7. Renomear definitivamente o projeto para `Maestro` e atualizar
   referencias.
8. Retomar projeto paralelo do banco de laudos periciais:
   - comecar por Previdenciario > Auxilio-acidente > Coluna;
   - coletar 20–30 exemplos iniciais;
   - extrair estrutura por bloco (preambulo, identificacao, historico,
     documentos, exame, discussao, respostas, conclusao);
   - cruzar com sentenca quando houver.
9. Politica de coleta do ecossistema Claude: inventario, classificacao,
   retencao, antes de qualquer raspagem.
10. Integrar Maestro com GSD se couber (decisao pendente).

## Nao fazer agora

- Nao instalar nada sem necessidade real.
- Nao configurar cron real ainda.
- Nao publicar nada no Telegram, site ou bot.
- Nao usar credenciais FTP.
- Nao modificar producao de `stemmia.com.br`.
- Nao inventar dados/custos/metricas — marcar TODO/RESEARCH.
- Nao apagar nem mover arquivos externos sem proposta explicita.
