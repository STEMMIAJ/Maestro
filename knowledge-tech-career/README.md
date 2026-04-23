# knowledge-tech-career

Base de conhecimento formal, privada, do usuário (médico perito judicial, autista/TEA + TDAH) sobre TI, desenvolvimento, web, arquitetura, segurança, dados, dados em saúde, IA/automação, interseção com perícia médico-legal, mapa de carreiras em TI e mapeamento pessoal de habilidades.

Não é diário. Não é rascunho. É a camada estável, consultável, versionada. Rascunhos vão para `16_inbox/` e, depois de filtrados, promovidos para os blocos numerados.

## Objetivo

1. Consolidar em Markdown linear, sem dependências exóticas, tudo que o usuário precisa saber/estudar/aplicar em TI aplicada à perícia e à prática médica.
2. Servir de substrato para agentes (Claude Code, OpenClaw, Maestro) lerem, indexarem e responderem com referência direta ao arquivo-fonte.
3. Tornar explícito o mapa de carreiras em TI e o estado atual de habilidades do usuário (gap analysis permanente).
4. Evitar retrabalho: toda decisão, fonte e snapshot fica registrado.

## Como navegar

- `00_governance/` — regras, convenções, escopo.
- `01_ti_foundations/` → `06_data_analytics/` — trilhas técnicas gerais.
- `07_health_data/` — dados em saúde (HL7/FHIR, DATASUS, SUS, ICD, SNOMED, RES).
- `08_ai_and_automation/` — LLM, agentes, RAG, avaliação.
- `09_legal_medical_integration/` — ponte entre TI/IA e perícia judicial (laudo, rastreabilidade, auditoria).
- `10_career_map/` — taxonomia de profissões TI, nível júnior/pleno/sênior, certificações, trilhas.
- `11_personal_skill_mapping/` — onde o usuário está, o que falta, evidências.
- `12_sources/` — bibliografia, docs oficiais, cursos.
- `13_reports/` — relatórios derivados (snapshots trimestrais, oportunidades, pesquisa de mercado).
- `14_automation/` — prompts, scripts, jobs OpenClaw, fluxos Telegram, pipelines de ingestão.
- `15_memory/` — memória operacional (daily, promoted, decisions, checkpoints).
- `16_inbox/` — entrada crua (conversas, notas, transcrições, material a processar).
- `AGENTS/` — definição dos subagentes que operam esta base.

Ponto de entrada rápido: `PROJECT_STRUCTURE.md` (mapa), `TASKS_NOW.md` (próxima rodada), `NEXT_SESSION_CONTEXT.md` (onde parei).

## O que entra

- Conhecimento técnico com fonte identificável.
- Mapeamentos estruturados (skill matrix, taxonomias, roadmaps).
- Decisões arquiteturais e justificativas.
- Prompts testados e scripts com referência a ID de falha quando aplicável (`PYTHON-BASE`).

## O que NÃO entra

- Código de produção (fica nos projetos Dexter).
- Material sensível (laudos, processos, pacientes).
- Logs brutos, dumps, binários.
- Opinião sem fonte, generalidade motivacional.

## Conexão com o ecossistema

- **Dexter** (`~/Desktop/STEMMIA Dexter/`) é raiz. Esta base é um módulo dele.
- **Claude Code** é o construtor: lê/escreve arquivos, roda agentes em paralelo, respeita `CLAUDE.md`.
- **Maestro / OpenClaw** indexam a árvore Markdown e expõem busca semântica.
- **Git** versiona tudo (o repositório raiz do Dexter já tem git inicializado; esta pasta herda).
- **Obsidian** pode ser usado como leitor/editor local (wikilinks suportados). Não é obrigatório.

## Convenções duras

- Nomes de pasta/arquivo: `snake_case`, sem acentos, sem espaços, sem cedilha.
- Dentro do Markdown: português correto, com acentos.
- Toda afirmação factual → fonte em `12_sources/` ou marcada `TODO/RESEARCH`.
- Status explícito em cada item: `EXECUTADO`, `PLANEJADO`, `PENDENTE`, `BLOQUEADO`.
- Nada é apagado sem registro em `CHANGELOG.md`.

## Ordem de leitura sugerida para retomar o projeto

1. `NEXT_SESSION_CONTEXT.md`
2. `TASKS_NOW.md`
3. `PROJECT_STRUCTURE.md`
4. Bloco alvo da sessão.
5. Atualizar `CHANGELOG.md` ao final.
