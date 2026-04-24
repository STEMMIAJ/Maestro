# PROMPT COMPLETO — Retomar Maestro em sessao nova sem Reads

Versao "self-contained": contem TODO o contexto inline. A IA nao precisa abrir Checkpoint/Plano/TasksNow para saber o que fazer. Reads so viram necessarios quando executar.

Tamanho: ~2800 tokens input (vs ~3500-5500 do compactado que precisa ler 4 arquivos).

---

Cole TUDO abaixo (entre ``` e ```) em sessao nova do Claude Code aberta em `~/Desktop/STEMMIA Dexter/Maestro/`.

```
Voce retoma o projeto Maestro. Nao leia arquivos de contexto — eles estao inline aqui. So leia quando for executar uma fase especifica.

========================================================================
USUARIO
========================================================================
Dr. Jesus Eduardo Noleto de Souza. Medico perito judicial, CRM ativo, Governador Valadares/MG. Autista (TEA) + TDAH. Memoria comprometida, sobrecarga severa. Comportamento esperado: PT-BR direto e seco, sem disclaimers, sem "posso?", sem "pronto" sem verificar, FAZER em vez de explicar. Opus 4.7 em subagentes. Sem acento em path de automacao.

========================================================================
PROJETO
========================================================================
Maestro = hub de governanca do ecossistema pericial Stemmia (~/Desktop/STEMMIA Dexter/). Ingere conversas externas (Perplexity/ChatGPT/Claude/Gemini) e transforma em memoria operacional. Roda ao lado do Dexter (sistema pericial brownfield com 64 scripts Python, 85 agentes Claude, 17 MCPs, 25 plugins).

Diretorio base: /Users/jesus/Desktop/STEMMIA\ Dexter/Maestro/

========================================================================
ESTADO ATUAL (2026-04-23)
========================================================================
Rodada 1 bootstrap (2026-04-22): 100% concluida.
 - Estrutura AGENTS/ (8 agentes), RULES/ (6 arquivos), FLOWS/ (9 arquivos), CRON/ (7 jobs inativos), CONFIG/, docs/openclaw-official/ (8 placeholders).
 - Conversa Perplexity capturada integral via chrome MCP (135992 chars, 4440 linhas) em conversations/raw/perplexity_conversation_2026-04-22_full.md.
 - 5 reports/conversation_*.md sintetizados do texto real.
 - MEMORY.md + memory/2026-04-22.md.
 - 5 scripts Python skeleton em PYTHON-BASE/08-SISTEMAS-COMPLETOS/conversation_ingestion/ (ingest, chunk, extract, generate_memory, checkpoint) + 3 templates.
 - Controle: INTEGRATION-PLAN.md, TASKS_MASTER.md (43 tarefas), TASKS_NOW.md, NEXT_SESSION_CONTEXT.md, CHANGELOG.md.
 - Reports iniciais: model_options, cost_estimate, database_options, telegram_integration, stemmia_dashboard_plan (+progress_snapshot + execution_report_round1).
 - Rename: openclaw-control-center -> Maestro-novo -> Maestro (final).

Rodada 2 continuacao (2026-04-23): 100% concluida.
 - OpenClaw confirmado em https://openclaw.ai (open source, github.com/openclaw/openclaw, gratis, orquestrador+LLM obrigatorio).
 - OpenClaw JA instalado localmente: v2026.4.2, 200MB em ~/.openclaw, auth Anthropic ja configurado (token), default Sonnet 4.6, credencial WhatsApp existe, memoria em main.sqlite.
 - DB decidido: HIBRIDO JSON + SQLite. Sem VPS. Sem Supabase agora. JSON = fonte da verdade (FICHA.json), SQLite = indice rapido, JSON estatico = dashboard publico. Supabase so se dashboard remoto precisar query dinamica.
 - LLM: OpenClaw determinista quando possivel; Haiku 4.5 quando precisa LLM (95% mais barato que Opus); Opus so laudo final.
 - Criada pasta Maestro/futuro/ com README + 00-DUVIDAS + 01-DECISOES-PENDENTES + 02-IDEIAS + 03-BACKLOG-TECNICO + 04-CREDENCIAIS-PEDIR.
 - Criada skill ~/.claude/skills/guardar-futuro/SKILL.md (ativa em frases "guarda na pasta futuro", "anota essa duvida", "tenho uma ideia", "/guardar").
 - Artefatos novos: CHECKPOINT-2026-04-23.md, PLANO-OPERACIONAL-2026-04-23.md, PROMPT-DR-JESUS-PARALELO.md.

Pipeline operacional (9 fases): 0%. Sistema integrado: ~30% mapeado, 0% operacional.

========================================================================
BLOQUEIOS ATIVOS (aguardando Dr. Jesus em outra aba)
========================================================================
Dr. Jesus esta rodando PROMPT-DR-JESUS-PARALELO.md em outra aba/sessao (20-35 min) para coletar:
 - BLK-A ANTHROPIC_API_KEY (console.anthropic.com/settings/keys, nova chave "Maestro-scripts")
 - BLK-B TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID (via @BotFather, depois /start + getUpdates)
 - BLK-C FTP nuvemhospedagem (host/user/pass/port do painel)
 - BLK-D OPENCLAW_STRATEGY: A (limpa tudo), B (backup + restore seletivo = recomendacao), C (mantem versao atual e so integra)

Valores vao para ~/Desktop/credenciais-maestro-2026-04-23.txt. Quando ele voltar, IA move pra Maestro/.env e apaga o txt.

========================================================================
PLANO OPERACIONAL — 9 FASES
========================================================================

FASE 1 (T-OpenClaw, 45-75min) — SEQUENCIAL ate decisao A/B/C
  1. tar czf ~/Desktop/openclaw-backup-2026-04-23.tar.gz ~/.openclaw
  2. Listar ~/.openclaw/credentials/
  3. Aguarda decisao Dr. Jesus A/B/C
  4. Se A/B: npm uninstall -g openclaw && rm -rf ~/.openclaw
  5. npm i -g openclaw && openclaw onboard
  6. Trocar default de Sonnet 4.6 -> Haiku 4.5
  7. workspace aponta pra Maestro/workspace
  8. openclaw doctor sem erros

FASE 2 (T-Docs, 30-45min) — PARALELO com FASE 1
  1. cd /tmp && gh repo clone openclaw/openclaw openclaw-src
  2. Mapear docs/ do repo
  3. Preencher 8 placeholders em Maestro/docs/openclaw-official/:
     cli_overview, memory, dashboard, cron, agents, tasks, status_health, plugins_hooks
  4. Remover tag RESEARCH de cada

FASE 3 (T-Python = 5 agentes em paralelo + 1 integrador, 2-3h) — apos FASE 1
  P1: ingest_conversation.py (filtrar UI noise, normalizar)
  P2: chunk_conversation.py (split por turno USER/PERPLEXITY/tema)
  P3: extract_action_items.py (regex ACTION_VERBS + prioridade/horizonte)
  P4: generate_memory_files.py (escreve MEMORY.md + memory/YYYY-MM-DD.md + reports/*.md)
  P5: generate_session_checkpoint.py (atualiza NEXT_SESSION_CONTEXT + TASKS_NOW)
  P6 (integrador): roda pipeline completo na conversa Perplexity de 135k chars. Diff vs reports existentes como sanity check. Usa Haiku se API key disponivel.
  Regra: ler PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json ANTES de cada script, citar IDs.

FASE 4 (15min) — rodar pipeline na conversa. Ja coberta por P6.

FASE 5 (T-DB, 1-1.5h) — PARALELO com FASE 3
  1. schema.sql em Maestro/banco-local/: tabelas processos/documentos/tarefas/heartbeat
  2. indexer_ficha.py varre ~/Desktop/ANALISADOR\ FINAL/processos/*/FICHA.json -> upsert em maestro.db
  3. exportar_dashboard.py gera Maestro/dashboard/data.json

FASE 6 (T-Dashboard, 2-3h) — PARALELO com FASE 3+5
  1. Maestro/dashboard/index.html: 4 cards grandes, busca CNJ, lista recentes
  2. style.css: reaproveitar paleta Planner Stemmia (ou Inter + neutro)
  3. app.js: fetch data.json
  4. Teste local: python3 -m http.server 8000

FASE 7 (T-Cron, 30min) — pos FASE 3
  1. ~/Library/LaunchAgents/com.stemmia.maestro.heartbeat.plist
  2. Roda a cada 30min: python3 Maestro/scripts/heartbeat.py -> Maestro/logs/heartbeat.log
  3. NAO ativar sem autorizacao.

FASE 8 (T-Deploy, 30-45min) — depende de FTP
  1. Maestro/scripts/deploy.sh com lftp
  2. Teste com arquivo dummy
  3. Upload dashboard/
  4. .htaccess basic auth se plano permitir

FASE 9 (T-Telegram, 1-1.5h) — depende de TOKEN
  1. Maestro/telegram/bot.py com python-telegram-bot (ler falhas.json antes)
  2. Comandos /status /urgentes /ajuda
  3. Polling (nao webhook)
  4. Cron J02 reinicia se cair

Total com times paralelos: 3.5-5h IA + 35min Dr. Jesus. Em sessoes 90min TDAH: 3 sessoes.

========================================================================
TAREFA IMEDIATA AGORA
========================================================================
Se Dr. Jesus disser "vai":
 - Disparar 2 agentes general-purpose (Opus 4.7) EM PARALELO na MESMA mensagem:
   AGENTE 1 = T-OpenClaw: executar passos 1-2 da FASE 1 (backup + inventario credenciais). PARAR antes do passo 3 (uninstall) e reportar o backup + lista de credenciais encontradas.
   AGENTE 2 = T-Docs: executar FASE 2 completa (clone + preencher 8 placeholders). Ler github.com/openclaw/openclaw, mapear docs/, substituir placeholders em Maestro/docs/openclaw-official/.

Se Dr. Jesus trouxer credenciais antes de mandar "vai":
 - Mover valores do txt pra Maestro/.env (criar .gitignore se nao existir).
 - Apagar ~/Desktop/credenciais-maestro-2026-04-23.txt.
 - Confirmar com ls que o txt sumiu e .env existe.
 - Depois aguardar "vai" pra FASE 1+2.

Se Dr. Jesus pedir status:
 - Em 5 linhas: (a) fase atual; (b) % acumulado; (c) o que depende dele; (d) o que IA fara em paralelo; (e) "vai?" ou "aguardo?".

========================================================================
REGRAS HARD (nao negociar)
========================================================================
 - Opus 4.7 em subagentes (CLAUDE_CODE_SUBAGENT_MODEL ja setado global).
 - Nao instalar/deletar sem confirmacao explicita.
 - Backup tar.gz ANTES de qualquer rm -rf em ~/.openclaw.
 - Nao inventar dados. Tudo verificavel com Read/Grep/Bash ou marcado TODO/RESEARCH.
 - Sem acento/espaco/cedilha em paths de automacao.
 - Consultar PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json antes de Python de automacao. Citar IDs (# ref: PW-012).
 - NAO commitar credenciais. .env fica em Maestro/ (gitignored).
 - Anti-mentira hook: so dizer "pronto/concluido/feito" apos Bash/Read/Grep verificar.
 - Se ouvir "guarda na pasta futuro" / "anota essa duvida" / "tenho uma ideia" / "/guardar" -> invocar skill guardar-futuro (grava em Maestro/futuro/*.md).
 - Max 3 linhas entre acoes em resposta.

========================================================================
ARQUIVOS A LER SO QUANDO EXECUTAR (nao no inicio)
========================================================================
Leia apenas o arquivo da fase que vai executar:
 - FASE 1: PLANO-OPERACIONAL-2026-04-23.md (secao FASE 1)
 - FASE 3: os 5 skeletons em PYTHON-BASE/08.../conversation_ingestion/*.py
 - FASE 5: Maestro/reports/database_options_initial.md
 - FASE 6: Maestro/reports/stemmia_dashboard_plan_initial.md
 - Qualquer fase: Maestro/CHECKPOINT-2026-04-23.md se precisar ver tarefas T001-T107 detalhadas.

========================================================================
PRIMEIRA RESPOSTA ESPERADA
========================================================================
Confirme em 3 linhas:
1. "Contexto recebido. Rodada 1+2 = 100%. Pipeline operacional = 0%."
2. "Aguardando: credenciais (txt em Desktop) E/OU 'vai' para FASE 1+2."
3. Uma pergunta unica: "dispara FASE 1+2 agora ou aguardo credenciais?"

Nada de Read/Bash antes dessa resposta.
```

---

## Comparacao entre as 3 opcoes

| Opcao | Tokens iniciais | Precisa Reads? | Risco |
|---|---:|---|---|
| Continuar sessao atual | ~56-66k por msg | nao (contexto ja ta aqui) | perto do limite de 200k |
| PROMPT-RETOMAR-COMPACTO (500 tok + 4 Reads) | ~3.5-5.5k | sim (4 Reads) | IA pode interpretar mal ao re-ler |
| PROMPT-RETOMAR-COMPLETO (este) | ~2.8k | nao para comecar | nenhum — estado todo inline |

Economia vs sessao atual: **~53-63k tokens por mensagem (~95%)**.
Economia vs compactado: **~700-2700 tokens + evita 4 round-trips de Read**.

## Quando usar qual

- **Compacto** (500 tok + 4 Reads): se quer ser purista e garantir que IA releia a fonte oficial.
- **Completo** (este): se quer velocidade + zero ambiguidade + cabe em um prompt. Recomendado.
- **Continuar aqui**: so se forem 1-2 mensagens rapidas ate o fim.
