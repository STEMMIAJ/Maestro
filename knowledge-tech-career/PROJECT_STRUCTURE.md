# PROJECT_STRUCTURE.md

Mapa completo da base. Atualizar sempre que um bloco ganhar/perder subdiretório. Blocos numerados são estáveis (ver `CLAUDE.md`).

## Raiz

```
knowledge-tech-career/
├── README.md                     — objetivo, navegação, convenções
├── CLAUDE.md                     — regras do Claude neste projeto
├── MEMORY.md                     — memória estável (visão, princípios)
├── TASKS_MASTER.md               — backlog completo (ids KTC-NNN)
├── TASKS_NOW.md                  — tarefas da próxima rodada
├── NEXT_SESSION_CONTEXT.md       — ponto de retomada
├── CHANGELOG.md                  — histórico append-only
├── PROJECT_STRUCTURE.md          — este arquivo
├── AGENTS/                       — definições dos subagentes
├── 00_governance/
├── 01_ti_foundations/
├── 02_programming/
├── 03_web_development/
├── 04_systems_architecture/
├── 05_security_and_governance/
├── 06_data_analytics/
├── 07_health_data/
├── 08_ai_and_automation/
├── 09_legal_medical_integration/
├── 10_career_map/
├── 11_personal_skill_mapping/
├── 12_sources/
├── 13_reports/
├── 14_automation/
├── 15_memory/
└── 16_inbox/
```

## AGENTS/

Definição dos subagentes que operam a base. Cada agente é um arquivo `.md` com: papel, entradas aceitas, saídas esperadas, limites, modelo (Opus por padrão).

## 00_governance/

Regras, convenções, escopo, ciclo de revisão, critérios de promoção de `16_inbox` para blocos numerados. Único bloco que todo contribuinte (humano ou agente) precisa ler antes de tocar os demais.

## 01_ti_foundations/

Fundamentos de TI. Conhecimento que precede qualquer especialização.

- `concepts/` — abstrações de sistema, modelo OSI, ciclo fetch-decode-execute.
- `hardware_networks_os/` — CPU, memória, disco, rede, sistemas operacionais.
- `internet_web_basics/` — DNS, HTTP/HTTPS, TLS, navegador.
- `software_lifecycle/` — SDLC, metodologias, DevOps resumido.
- `glossario/` — termos fundamentais, 1 frase cada.

## 02_programming/

Programação como disciplina. Evita duplicar com `03_web_development` (que é aplicação).

- `logic_algorithms/`, `python/`, `javascript/`, `bash_terminal/`, `version_control_git/`, `testing_debugging/`, `software_design/`.

## 03_web_development/

Web como plataforma aplicada: construir, servir, expor APIs.

- `html_css/`, `frontend/`, `backend/`, `apis/`, `authentication/`, `deployment/`, `performance_accessibility/`.

## 04_systems_architecture/

Arquitetura além do monolito didático: como sistemas reais se organizam em produção.

- `architecture_patterns/`, `databases/`, `queues_jobs_cron/`, `integrations/`, `observability/`, `scaling_reliability/`.

## 05_security_and_governance/

Segurança da informação aplicada, privacidade e governança. Foco em LGPD, sigilo médico e resoluções CFM quando aplicável.

- `infosec_basics/`, `secrets_access/`, `backups_disaster_recovery/`, `compliance_privacy/`, `incident_response/`.

## 06_data_analytics/

Dados genéricos: estatística, SQL, BI, engenharia de dados básica, experimentação.

- `statistics_foundations/`, `sql/`, `dashboards_bi/`, `data_engineering_basics/`, `experimentation/`, `data_projects/`.

## 07_health_data/

Dados em saúde com profundidade. Intersecção crítica para o usuário.

- `health_informatics/` — RES, HL7, FHIR, OpenEHR.
- `epidemiology_biostatistics/` — desenhos de estudo, medidas de efeito.
- `healthcare_datasets/` — DATASUS (SIH, SIA, CNES, SIM, SINASC, SINAN), e-SUS, ANS.
- `analytics_for_medical_work/` — uso diário do médico perito.
- `clinical_quality_indicators/` — ANS, ONA, Joint Commission.
- `opportunities_for_physicians/` — nichos TI+saúde acessíveis a médicos.

## 08_ai_and_automation/

IA aplicada e automação. Base para tudo que o usuário automatiza com Claude.

- `llm_foundations/`, `prompt_engineering/`, `agent_systems/`, `vector_memory_rag/`, `model_selection/`, `automation_workflows/`, `evaluation_guardrails/`.

## 09_legal_medical_integration/

Ponte formal entre perícia médico-legal e engenharia. Não substitui o sistema pericial (esse vive em `~/Desktop/STEMMIA Dexter/`), mas documenta o conhecimento que o sustenta.

- `pericia_judicial_and_data/`, `pericial_workflows/`, `ai_for_forensic_medical_work/`, `document_automation/`, `auditability_traceability/`.

## 10_career_map/

Mapa explícito de carreiras TI. Objetivo: o usuário enxergar onde encaixar sua formação médica + TI.

- `professions_taxonomy/`, `junior_pleno_senior/`, `role_expectations/`, `salary_market_signals/`, `certifications/`, `portfolios_projects/`, `learning_paths/`.

## 11_personal_skill_mapping/

Espelho do usuário. Honesto. Evolui rodada a rodada.

- `current_state/`, `skill_matrix/`, `gap_analysis/`, `evidence_of_skill/`, `study_backlog/`, `certification_readiness/`.

## 12_sources/

Bibliografia viva. Toda fonte citada em qualquer `.md` técnico tem entrada aqui.

- `official_docs/`, `universities/`, `books/`, `journals/`, `roadmaps/`, `courses/`, `communities/`.

## 13_reports/

Saídas derivadas, não fontes primárias. Snapshots são imutáveis após datados.

- `snapshots/`, `quarterly_reviews/`, `opportunity_reports/`, `market_research/`, `master_summaries/`.

## 14_automation/

Artefatos operacionais: prompts testados, scripts, jobs OpenClaw, fluxos Telegram, specs de dashboard, pipelines de ingestão.

- `prompts/`, `scripts/`, `openclaw_jobs/`, `telegram_flows/`, `dashboard_specs/`, `ingestion_pipelines/`.

## 15_memory/

Memória operacional estruturada.

- `daily/` — diário curto por dia de trabalho.
- `promoted/` — item promovido de `16_inbox` para bloco numerado (registro da promoção).
- `decisions/` — ADR-lite: decisões arquiteturais com contexto e alternativas.
- `checkpoints/` — marcos grandes (ex: fim de trimestre).

## 16_inbox/

Porta de entrada única para conteúdo cru. Nada entra direto nos blocos numerados.

- `raw_conversations/` — exports de sessões.
- `imported_notes/` — notas trazidas de outros sistemas.
- `transcripts/` — transcrições de áudio/vídeo.
- `to_process/` — fila de material aguardando triagem.
