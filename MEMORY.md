# MEMORY.md — Maestro (ex openclaw-control-center)

Memoria estavel, curada, de longo prazo. Derivada de:
`conversations/raw/perplexity_conversation_2026-04-22_full.md`.

Nao replicar a conversa inteira aqui. Este arquivo sobrevive meses; so entra
o que for compromisso arquitetural ou limite de seguranca recorrente.

---

## 1. Identidade do projeto

- Nome atual da pasta: `Maestro` (ex `openclaw-control-center`).
- Nome final previsto: `Maestro`.
- Caminho: `~/Desktop/STEMMIA Dexter/Maestro/`.
- Papel: centro de governanca do ecossistema STEMMIA Dexter. Nao e deposito de
  dados; e camada de controle, auditoria, memoria operacional e orquestracao.

## 2. Visao de longo prazo (compromisso)

Integrar por papeis, nao migrar:

- Perplexity: arquiteto/estrategista externo — desenha taxonomia, prompts e
  auditoria de sistema.
- Claude Code: executor local forte — cria arquivos, scripts, agentes e
  estruturas dentro do escopo do projeto.
- OpenClaw (codinome interno possivel): camada de supervisao, cron, memoria
  indexada, tasks, dashboard e observabilidade.
- Dr. Jesus: valida amostras, escolhe prioridade, corrige rumo. Nao e o
  executor de baixo nivel.

## 3. Meta real do projeto Maestro

1. Criar infra pessoal de memoria, auditoria e organizacao da pasta
   `STEMMIA Dexter`.
2. Manter comandos recorrentes de revisao de projetos, ideias, sessoes,
   memorias e banco de dados.
3. Usar Claude Code como executor com contexto de projeto travado.
4. Evoluir para interface visual (dashboard) em `stemmia.com.br`.
5. Conectar bot Stemmia (Telegram) para relatorios e avisos.
6. Preservar conversas estrategicas (Perplexity, Claude, outras) como
   memoria operacional, evitando reexplicar tudo do zero.

## 4. Filosofia de memoria

- `MEMORY.md`: memoria curada, estavel, durable.
- `memory/YYYY-MM-DD.md`: nota de sessao, volatil, corrente.
- `reports/*`: snapshots e analises derivadas.
- `conversations/raw/*`: fontes brutas. Nao editar.
- `conversations/processed/*`: derivados estruturados.
- Regra: memoria util e reutilizavel, nao acumulo bruto.

## 5. Limites de seguranca recorrentes

- Nao usar acento, espaco ou ç em paths/arquivos de automacao.
- Nao instalar nada sem necessidade real.
- Nao configurar cron real sem aprovacao explicita.
- Nao publicar em Telegram/site/producao sem aprovacao.
- Nao usar credenciais FTP em rodadas automaticas.
- Nao modificar arquivos em producao de `stemmia.com.br`.
- Nao inventar dados, custos, metricas — marcar `TODO/RESEARCH`.
- Diferenciar sempre: executado, planejado, pendente, bloqueado.
- Nao apagar nem mover arquivos externos ao projeto sem proposta explicita.
- Claude Archivist: tratar exportacoes e memorias com classificacao e
  privacidade — nao "raspar tudo" do ecossistema Claude indiscriminadamente.

## 6. Convencao de nomes

- Paths de automacao em ASCII, sem espaco, sem acento, sem ç.
- Markdown para regras, agentes, fluxos, relatorios, checklists.
- Python para scripts de transformacao, sumarizacao, indexacao.
- Arquivos de memoria diaria: `memory/YYYY-MM-DD.md`.
- Conversas brutas: `conversations/raw/<origem>_<data>_full.md`.

## 7. Agentes de referencia (contrato estavel)

Cada agente tem missao curta, escopo, entradas, saidas, proibicoes e criterio
de completude. Agentes previstos:

- `ORCHESTRATOR` — coordena, nao altera dado sensivel.
- `DEXTER-AUDITOR` — inventaria pasta `STEMMIA Dexter`, sem apagar/mover.
- `MEMORY-CURATOR` / `MEMORY-INGESTION-TEAM` — consolida memoria util.
- `IDEA-ARCHAEOLOGIST` — recupera ideias antigas em arquivos/transcricoes.
- `PROJECT-CARTOGRAPHER` — classifica projetos por status.
- `CLAUDE-ARCHIVIST` — mapeia artefatos Claude com privacidade.
- `OPENCLAW-SUPERVISOR` — cron, tasks, status, health, logs, dashboard.
- `WEB-DASHBOARD-PLANNER` / `WEB-INTERFACE-PLANNER` — UI visual futura.
- `TELEGRAM-INTEGRATION-PLANNER` — bot Stemmia, sem postar nada ainda.
- `DATABASE-ARCHITECT` — Supabase vs alternativas, backup local + site.
- `COST-MODEL-ANALYST` — modelos e custo (Opus 4.7 via API, etc.).

## 8. Regra para ordens ao Claude Code

Toda ordem deve conter: PAPEL, OBJETIVO, ESCOPO, ENTRADAS, SAIDAS,
PROIBICOES, CRITERIO DE COMPLETUDE. Ordem sem esses blocos e rejeitada.

## 9. Pontos sensiveis que podem voltar

- Claude Opus 4.7 via API para este projeto — avaliar custo vs beneficio.
- Supabase vs alternativas + backup no proprio site.
- Dashboard em `stemmia.com.br` reutilizando design do Planner Stemmia.
- Baixar artefatos do ecossistema Claude: sempre com inventario, politica de
  retencao e auditoria ANTES da coleta.

## 10. Principio final

Utilidade real, continuidade entre sessoes, reaproveitamento maximo de
contexto. Reduzir ao minimo a necessidade do Dr. Jesus reexplicar tudo.
