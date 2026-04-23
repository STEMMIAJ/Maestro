# TASKS_MASTER.md — Backlog completo

Backlog total da base. Rodadas puxam daqui para `TASKS_NOW.md`. Status: `EXECUTADO | PLANEJADO | PENDENTE | BLOQUEADO`. Coluna `%` = peso aproximado dentro do panorama total do projeto (soma ≈ 100%).

Convenção de ID: `KTC-NNN`. Não reciclar ids. Tarefa concluída muda status, não sai daqui.

## 00_governance (peso bloco: 4%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-001 | Redigir `00_governance/conventions.md` (nomenclatura, status, idioma) | CLAUDE.md, MEMORY.md | conventions.md | — | PLANEJADO | 1 |
| KTC-002 | Redigir `00_governance/scope.md` (o que entra/não entra) | README.md | scope.md | — | PLANEJADO | 1 |
| KTC-003 | Redigir `00_governance/review_cycle.md` (cadência trimestral) | — | review_cycle.md | KTC-001 | PLANEJADO | 1 |
| KTC-004 | Redigir `00_governance/promotion_rules.md` (inbox → blocos) | MEMORY.md | promotion_rules.md | KTC-001 | PLANEJADO | 1 |

## 01_ti_foundations (peso: 6%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-010 | `concepts/` — modelo OSI, abstrações de sistema | TODO/RESEARCH fontes | notes.md | — | PLANEJADO | 1 |
| KTC-011 | `hardware_networks_os/` — CPU, memória, disco, rede, Linux/macOS/Windows | docs oficiais | notes.md | — | PLANEJADO | 2 |
| KTC-012 | `internet_web_basics/` — DNS, HTTP, TLS, navegador | MDN | notes.md | — | PLANEJADO | 1 |
| KTC-013 | `software_lifecycle/` — SDLC, agile, waterfall, DevOps | — | notes.md | — | PLANEJADO | 1 |
| KTC-014 | `glossario/` — termos fundamentais com 1 frase cada | conteúdo dos demais | glossario.md | KTC-010..013 | PLANEJADO | 1 |

## 02_programming (peso: 9%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-020 | `logic_algorithms/` — complexidade, estruturas, recursão | CLRS resumido | notes.md | — | PLANEJADO | 1 |
| KTC-021 | `python/` — sintaxe, stdlib, venv, packaging | docs.python.org | notes.md | — | PLANEJADO | 2 |
| KTC-022 | `javascript/` — ES moderno, módulos, async | MDN | notes.md | — | PLANEJADO | 1 |
| KTC-023 | `bash_terminal/` — shell, redirecionamento, processos | man pages | notes.md | — | PLANEJADO | 1 |
| KTC-024 | `version_control_git/` — comandos essenciais, fluxos | Pro Git | notes.md | — | PLANEJADO | 1 |
| KTC-025 | `testing_debugging/` — unit, integration, logging | — | notes.md | KTC-021 | PLANEJADO | 1 |
| KTC-026 | `software_design/` — SOLID, patterns mínimos úteis | — | notes.md | KTC-020 | PLANEJADO | 1 |
| KTC-027 | Projeto guia Python aplicado à perícia (script exemplo) | KTC-021..026 | projeto.md | KTC-025 | PLANEJADO | 1 |

## 03_web_development (peso: 7%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-030 | `html_css/` — semântica, layout, acessibilidade base | MDN | notes.md | — | PLANEJADO | 1 |
| KTC-031 | `frontend/` — React/Vue comparação, quando usar | docs oficiais | notes.md | KTC-030 | PLANEJADO | 1 |
| KTC-032 | `backend/` — Node/Python/Go comparação objetiva | — | notes.md | — | PLANEJADO | 1 |
| KTC-033 | `apis/` — REST, GraphQL, gRPC | — | notes.md | KTC-032 | PLANEJADO | 1 |
| KTC-034 | `authentication/` — OAuth2, JWT, sessões | RFCs | notes.md | KTC-033 | PLANEJADO | 1 |
| KTC-035 | `deployment/` — containers, CI/CD, hospedagem | — | notes.md | KTC-032 | PLANEJADO | 1 |
| KTC-036 | `performance_accessibility/` — Core Web Vitals, WCAG | — | notes.md | KTC-030 | PLANEJADO | 1 |

## 04_systems_architecture (peso: 7%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-040 | `architecture_patterns/` — mono, micro, hexagonal, eventos | Fowler | notes.md | — | PLANEJADO | 1 |
| KTC-041 | `databases/` — relacional x NoSQL x vetorial | docs | notes.md | — | PLANEJADO | 2 |
| KTC-042 | `queues_jobs_cron/` — filas, workers, scheduling | — | notes.md | KTC-040 | PLANEJADO | 1 |
| KTC-043 | `integrations/` — webhooks, ETL, iPaaS | — | notes.md | KTC-033 | PLANEJADO | 1 |
| KTC-044 | `observability/` — logs, métricas, traces | OpenTelemetry | notes.md | — | PLANEJADO | 1 |
| KTC-045 | `scaling_reliability/` — SLO, caching, failover | Google SRE | notes.md | KTC-044 | PLANEJADO | 1 |

## 05_security_and_governance (peso: 6%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-050 | `infosec_basics/` — CIA, ameaças, modelo STRIDE | OWASP | notes.md | — | PLANEJADO | 1 |
| KTC-051 | `secrets_access/` — gestão de credenciais, MFA, RBAC | — | notes.md | KTC-050 | PLANEJADO | 1 |
| KTC-052 | `backups_disaster_recovery/` — 3-2-1, RTO, RPO | — | notes.md | — | PLANEJADO | 1 |
| KTC-053 | `compliance_privacy/` — LGPD, HIPAA, resoluções CFM | LGPD texto | notes.md | — | PLANEJADO | 2 |
| KTC-054 | `incident_response/` — playbook mínimo | NIST 800-61 | notes.md | KTC-050 | PLANEJADO | 1 |

## 06_data_analytics (peso: 7%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-060 | `statistics_foundations/` — descritiva, inferência, viés | — | notes.md | — | PLANEJADO | 2 |
| KTC-061 | `sql/` — SELECT a window functions | docs Postgres | notes.md | KTC-041 | PLANEJADO | 1 |
| KTC-062 | `dashboards_bi/` — Metabase, Superset, Power BI | — | notes.md | KTC-061 | PLANEJADO | 1 |
| KTC-063 | `data_engineering_basics/` — ETL, modelagem dim/fato | Kimball | notes.md | KTC-061 | PLANEJADO | 1 |
| KTC-064 | `experimentation/` — A/B, teste de hipótese | — | notes.md | KTC-060 | PLANEJADO | 1 |
| KTC-065 | `data_projects/` — template de projeto analítico | — | template.md | KTC-063 | PLANEJADO | 1 |

## 07_health_data (peso: 9%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-070 | `health_informatics/` — RES, HL7 v2, FHIR, OpenEHR | HL7.org | notes.md | — | PLANEJADO | 2 |
| KTC-071 | `epidemiology_biostatistics/` — desenhos, medidas | — | notes.md | KTC-060 | PLANEJADO | 1 |
| KTC-072 | `healthcare_datasets/` — DATASUS, SIH, SIA, CNES, e-SUS | DATASUS | notes.md | — | PLANEJADO | 2 |
| KTC-073 | `analytics_for_medical_work/` — uso diário na perícia | casos reais | notes.md | KTC-072 | PLANEJADO | 1 |
| KTC-074 | `clinical_quality_indicators/` — ANS, ONA, Joint Commission | — | notes.md | KTC-070 | PLANEJADO | 1 |
| KTC-075 | `opportunities_for_physicians/` — nichos TI+saúde | pesquisa mercado | notes.md | KTC-072 | PLANEJADO | 2 |

## 08_ai_and_automation (peso: 10%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-080 | `llm_foundations/` — tokens, contexto, sampling, cache | Anthropic docs | notes.md | — | PLANEJADO | 2 |
| KTC-081 | `prompt_engineering/` — padrões, few-shot, XML/JSON | — | notes.md | KTC-080 | PLANEJADO | 2 |
| KTC-082 | `agent_systems/` — loops, tools, handoff | Claude Code docs | notes.md | KTC-081 | PLANEJADO | 2 |
| KTC-083 | `vector_memory_rag/` — embedding, chunking, retrieval | — | notes.md | KTC-041 | PLANEJADO | 1 |
| KTC-084 | `model_selection/` — Opus/Sonnet/Haiku, custo/latência | — | notes.md | KTC-080 | PLANEJADO | 1 |
| KTC-085 | `automation_workflows/` — N8N, launchd, cron | — | notes.md | — | PLANEJADO | 1 |
| KTC-086 | `evaluation_guardrails/` — eval sets, red team | — | notes.md | KTC-082 | PLANEJADO | 1 |

## 09_legal_medical_integration (peso: 8%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-090 | `pericia_judicial_and_data/` — tipos de perícia, dados envolvidos | experiência | notes.md | — | PLANEJADO | 2 |
| KTC-091 | `pericial_workflows/` — do pedido ao laudo, pontos automatizáveis | — | notes.md | KTC-090 | PLANEJADO | 2 |
| KTC-092 | `ai_for_forensic_medical_work/` — LLM como triagem, limites | KTC-082 | notes.md | KTC-082 | PLANEJADO | 2 |
| KTC-093 | `document_automation/` — templates de laudo, placeholders | templates atuais | notes.md | KTC-091 | PLANEJADO | 1 |
| KTC-094 | `auditability_traceability/` — logs assinados, hash, carimbo de tempo | ICP-Brasil | notes.md | KTC-094-RESEARCH | PLANEJADO | 1 |

## 10_career_map (peso: 10%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-100 | `professions_taxonomy/` — lista estruturada de cargos TI | roadmap.sh | notes.md | — | PLANEJADO | 2 |
| KTC-101 | `junior_pleno_senior/` — matriz de senioridade por função | — | matriz.md | KTC-100 | PLANEJADO | 2 |
| KTC-102 | `role_expectations/` — o que cada função entrega no dia a dia | — | notes.md | KTC-100 | PLANEJADO | 1 |
| KTC-103 | `salary_market_signals/` — faixas BR/remoto USD, fontes | pesquisa | notes.md | KTC-100 | PLANEJADO | 1 |
| KTC-104 | `certifications/` — quais valem para cada função | — | notes.md | KTC-100 | PLANEJADO | 1 |
| KTC-105 | `portfolios_projects/` — padrões de projeto para portfólio | — | notes.md | KTC-100 | PLANEJADO | 1 |
| KTC-106 | `learning_paths/` — trilhas por objetivo (dado/backend/IA) | roadmap.sh | notes.md | KTC-100 | PLANEJADO | 2 |

## 11_personal_skill_mapping (peso: 7%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-110 | `current_state/` — snapshot honesto do que o usuário sabe hoje | auto-avaliação | snapshot.md | — | PLANEJADO | 1 |
| KTC-111 | `skill_matrix/` — grade de habilidades com níveis 0–4 | KTC-101 | matrix.md | KTC-101 | PLANEJADO | 2 |
| KTC-112 | `gap_analysis/` — diferença entre estado atual e alvo | KTC-110, KTC-106 | gaps.md | KTC-111 | PLANEJADO | 1 |
| KTC-113 | `evidence_of_skill/` — artefatos, projetos, certificações | Dexter | evidencias.md | KTC-111 | PLANEJADO | 1 |
| KTC-114 | `study_backlog/` — próximas unidades de estudo | KTC-112 | backlog.md | KTC-112 | PLANEJADO | 1 |
| KTC-115 | `certification_readiness/` — prontidão para certs específicas | KTC-104 | readiness.md | KTC-104 | PLANEJADO | 1 |

## 12_sources (peso: 5%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-120 | `official_docs/` — índice de docs oficiais usados | — | index.md | — | PLANEJADO | 1 |
| KTC-121 | `universities/` — cursos abertos (MIT OCW, Stanford) | — | index.md | — | PLANEJADO | 1 |
| KTC-122 | `books/` — bibliografia com status de leitura | — | index.md | — | PLANEJADO | 1 |
| KTC-123 | `journals/` — periódicos relevantes (JAMIA, BMJ Health Inf) | — | index.md | — | PLANEJADO | 1 |
| KTC-124 | `roadmaps/` — roadmap.sh, frontendmasters roadmap | — | index.md | — | PLANEJADO | 0 |
| KTC-125 | `courses/` — cursos pagos/gratuitos com status | — | index.md | — | PLANEJADO | 0 |
| KTC-126 | `communities/` — comunidades relevantes | — | index.md | — | PLANEJADO | 1 |

## 13_reports (peso: 4%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-130 | Template de `snapshots/` | — | template.md | — | PLANEJADO | 1 |
| KTC-131 | Template de `quarterly_reviews/` | — | template.md | KTC-130 | PLANEJADO | 1 |
| KTC-132 | Template de `opportunity_reports/` | — | template.md | — | PLANEJADO | 1 |
| KTC-133 | Primeiro `master_summaries/` da base | árvore | summary.md | KTC-110 | PLANEJADO | 1 |

## 14_automation (peso: 5%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-140 | `prompts/` — catálogo inicial de prompts testados | uso real | index.md | — | PLANEJADO | 1 |
| KTC-141 | `scripts/` — scripts de manutenção da base | PYTHON-BASE | scripts | KTC-021 | PLANEJADO | 1 |
| KTC-142 | `openclaw_jobs/` — definição de jobs de indexação | OpenClaw | jobs.md | — | PLANEJADO | 1 |
| KTC-143 | `telegram_flows/` — fluxos de notificação relevantes | — | flows.md | — | PLANEJADO | 1 |
| KTC-144 | `dashboard_specs/` — especificação do dashboard da base | KTC-062 | spec.md | KTC-062 | PLANEJADO | 1 |
| KTC-145 | `ingestion_pipelines/` — pipeline inbox → blocos | KTC-004 | pipeline.md | KTC-004 | PLANEJADO | 0 |

## 15_memory (peso: 3%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-150 | Template `daily/` | — | template.md | — | PLANEJADO | 1 |
| KTC-151 | Template `promoted/` | KTC-004 | template.md | KTC-004 | PLANEJADO | 1 |
| KTC-152 | Template `decisions/` (ADR-lite) | — | template.md | — | PLANEJADO | 1 |
| KTC-153 | Template `checkpoints/` | — | template.md | — | PLANEJADO | 0 |

## 16_inbox (peso: 2%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-160 | README do inbox explicando fluxo | KTC-004 | README.md | KTC-004 | PLANEJADO | 1 |
| KTC-161 | Subpastas `raw_conversations`, `imported_notes`, `transcripts`, `to_process` com placeholder | — | .keep | — | PLANEJADO | 1 |

## AGENTS (peso: 1%)

| ID | Descrição | Entradas | Saídas | Depende | Status | % |
|---|---|---|---|---|---|---|
| KTC-170 | `AGENTS/README.md` — o que cada agente faz | — | README.md | — | PLANEJADO | 0 |
| KTC-171 | `AGENTS/docs_mestres.md` — papel do agente construtor | este prompt | .md | — | EXECUTADO | 0 |
| KTC-172 | `AGENTS/indexador.md` — agente de indexação para OpenClaw | — | .md | KTC-142 | PLANEJADO | 0 |
| KTC-173 | `AGENTS/curador_fontes.md` — validador de `12_sources/` | — | .md | KTC-120 | PLANEJADO | 0 |
| KTC-174 | `AGENTS/auditor_status.md` — verifica status coerentes | — | .md | — | PLANEJADO | 1 |
