# Entidades e projetos — 2026-04-22

Fonte: `conversations/raw/perplexity_conversation_2026-04-22_full.md`.

Mapeamento das entidades mencionadas na conversa e suas relacoes.

## Entidades principais

### Dexter (universo local)

- O que e: a pasta-mae `~/Desktop/STEMMIA Dexter/` onde moram TODOS os
  subprojetos do Dr. Jesus.
- Papel: espaco fisico do ecossistema. Nao e um app, e um territorio.
- Conteudo: projetos antigos (pericia, scripts, automacoes), memoria,
  conversas, banco de dados, agentes, skills.
- Na conversa: referido como "Dexter" e "pasta Dexter". Precisa ser
  inventariado, auditado, classificado e mapeado.

### Maestro (ex openclaw-control-center, hoje Maestro)

- O que e: projeto de governanca dentro de Dexter.
- Caminho atual: `~/Desktop/STEMMIA Dexter/Maestro/`.
- Nome final: `Maestro`.
- Papel: centro de controle, auditoria, memoria operacional, orquestracao
  de agentes. Nao guarda dados de pericia, controla o sistema.
- Principais modulos: AGENTS, RULES, FLOWS, CRON, SCRIPTS, CONFIG, DATA,
  WEB-UI, conversations, memory, logs, reports, docs/openclaw-official.

### Claude Code

- O que e: CLI/harness da Anthropic usado localmente.
- Papel no ecossistema: executor forte. Cria arquivos, scripts, agentes.
- Governado por: `CLAUDE.md` (global e do projeto), settings por escopo
  (`~/.claude/settings.json`, `.claude/settings.json`,
  `.claude/settings.local.json`).
- Na conversa: referido como "o Claude" ou "Claude Code". Deve agir so
  dentro do escopo do projeto Maestro.

### OpenClaw

- O que e: ferramenta (possivelmente codinome interno) de orquestracao
  com CLI: `setup`, `onboard`, `configure`, `doctor`, `dashboard`,
  `status`, `health`, `agents`, `agent`, `tasks`, `flows`, `memory`,
  `sessions`, `cron add/list/run/runs/edit/remove`, `logs`,
  `gateway status`, `tasks audit`, `tasks maintenance`.
- Papel: supervisao, cron, memoria indexada, tasks, dashboard, logs.
- Memoria: trabalha bem com `MEMORY.md` + `memory/YYYY-MM-DD.md` + busca
  semantica (`memory index`, `memory search`, `memory promote --apply`).
- Na conversa: confirmado que cobre o basico; exige que a conversa vire
  memoria estruturada em Markdown para ser util.

### Perplexity

- O que e: assistente de pesquisa/arquitetura externo.
- Papel: desenha estrategia, taxonomia, prompts, auditoria de sistema.
  Nao executa no sistema de arquivos.
- Na conversa: quem produziu o comando-mestre e a arquitetura.

### Dr. Jesus

- Usuario. Perito medico judicial. TEA + TDAH.
- Papel: validador, decisor, corretor de rumo. Nao executa baixo nivel.

### stemmia.com.br (site e dashboard)

- Site existente.
- Planejado: hospedar dashboard web proprio do Maestro futuramente.
- Rotas sugeridas: `/dashboard-dexter`, `/dashboard-pericias`.
- Nao mencionado em detalhe: stack atual do site — TODO/RESEARCH.
- Nao mexer em producao nesta rodada.

### Bot Stemmia (Telegram)

- Canal planejado para relatorios de andamento, avisos de jobs, resumos
  diarios/semanal, notificacoes do sistema.
- Na conversa: so em nivel de planejamento. Nao configurar ainda.
- Stack/hospedagem: nao mencionados — TODO/RESEARCH.

### Banco de dados

- Duplo significado na conversa:
  1. Banco de dados operacional do ecossistema (Supabase x alternativas),
     com backup local e backup no site.
  2. Banco de dados de laudos periciais medicos judiciais (projeto
     paralelo do Dr. Jesus, eixo 1 da conversa).
- Status: duvida aberta; decisao por relatorio, nao por execucao.

### Planner Stemmia

- Produto/design existente. Mencionado como fonte para reaproveitar
  componentes visuais na futura dashboard.
- Detalhes tecnicos: nao mencionados — TODO/RESEARCH.

### Conversation ingestion (subprojeto Python)

- Pipeline reutilizavel para ingerir conversas (Perplexity, Claude, etc.)
  e gerar memoria operacional.
- Scripts: `ingest_conversation.py`, `chunk_conversation.py`,
  `extract_action_items.py`, `generate_memory_files.py`,
  `generate_session_checkpoint.py`.
- Vive na pasta Python base do `STEMMIA Dexter` — pasta exata ainda a
  definir.

## Relacoes

```
Dr. Jesus
   |
   | valida/decide
   v
Perplexity (arquiteto) ---- desenha ----> Maestro
                                           |
                                           | orquestra
                                           v
                              Claude Code (executor)
                                           |
                                           | cria/popula
                                           v
                              Dexter (territorio)
                                   |
                         +---------+---------+---------+
                         |         |         |         |
                       memoria   agentes   scripts   banco
                                                     dados
                                                      |
                                                      | futuro
                                                      v
                                              stemmia.com.br
                                                      |
                                                      | avisa
                                                      v
                                              Bot Stemmia
                                              (Telegram)

        OpenClaw = camada transversal: cron, memory index,
                   tasks, dashboard nativo, logs, health.
```

## Projetos relevantes no ecossistema

- Maestro (governanca) — este projeto.
- Banco de laudos periciais (eixo paralelo, taxonomia ja desenhada).
- Site stemmia.com.br + futura dashboard.
- Bot Stemmia (Telegram).
- Subprojeto `conversation_ingestion/` (Python base).
- Projetos antigos em Dexter (a mapear pelo `DEXTER-AUDITOR`).

## Nao mencionado na conversa

- Integracao com GSD (ferramenta ja usada no repo) — TODO/RESEARCH.
- Nome real/oficial de "OpenClaw" — possivelmente codinome. Precisa
  confirmacao.
