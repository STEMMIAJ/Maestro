# CHANGELOG

Histórico de mudanças da base `knowledge-tech-career`. Append-only. Datas em `YYYY-MM-DD`.

## [0.2.0] — 2026-04-23 — Rodada 2: densificação técnica

### EXECUTADO

- +22 artefatos em `01_ti_foundations/` (redes, SO, hardware, TCP/IP, shell, conceitos e howtos).
- +24 artefatos em `02_programming/` (Python denso: sintaxe, I/O, requests, erros, pipeline pericial, testes, padrões).
- +27 artefatos combinados em `06_data_analytics/` (+15) e `07_health_data/` (+12): analítica tabular, SQL, FHIR, HL7, datasets públicos.
- +26 artefatos combinados em `08_ai_and_automation/` (+20) e `09_legal_medical_integration/` (+6): LLM, RAG, agentes, prompt engineering aplicado à perícia, integrações jurídico-médicas.
- +9 evidências reais em `11_personal_skill_mapping/evidence_of_skill/` (PJe Playwright CDP, DataJud descoberta, DJEN async tenacity, stop hook anti-mentira, verificador petição PDF, template laudo com placeholders, skill modo-sonnet relay, distiller feedback auto, + catálogo-template).
- Symlink criado: `02_programming/python/python-base → ~/Desktop/STEMMIA Dexter/PYTHON-BASE` (acopla 179 MB de base técnica com 90 falhas catalogadas, sem duplicação).
- Checkpoint gravado em `15_memory/checkpoints/checkpoint_2026-04-23_round2.md`.
- Snapshot de progresso gravado em `13_reports/snapshots/progress_snapshot_round2.md`.
- Base saiu de 73 → 190 MDs em 112 diretórios.

### EM EXECUÇÃO

- Rodada 3 em execução paralela: agentes construindo 03_web_development, 04_systems_architecture, 05_security_and_governance, 10_career_map, 16_inbox; integrador cruzando PYTHON-BASE com 02 e 14; pesquisador resolvendo TODOs.

### PLANEJADO (próximas rodadas)

- Promoção de rascunhos densos para `status: vigente` após revisão humana.
- Inicializar Git + push para GitHub privado.
- Rodar `openclaw memory index --path <root>`.
- Importar conversa piloto ChatGPT/Claude em `16_inbox/raw_conversations/`.

### PENDENTE

- Decisão Git local vs submódulo do Dexter.
- Validação do comando OpenClaw na versão instalada.

### BLOQUEADO

- Nada novo.

## 2026-04-23 — Rodada 1: fundação

### EXECUTADO

- Criada árvore física de 112 diretórios sob `/Users/jesus/Desktop/STEMMIA Dexter/knowledge-tech-career/`.
- 17 blocos numerados instanciados: `00_governance`, `01_ti_foundations`, `02_programming`, `03_web_development`, `04_systems_architecture`, `05_security_and_governance`, `06_data_analytics`, `07_health_data`, `08_ai_and_automation`, `09_legal_medical_integration`, `10_career_map`, `11_personal_skill_mapping`, `12_sources`, `13_reports`, `14_automation`, `15_memory`, `16_inbox`.
- Pasta `AGENTS/` criada.
- Subdiretórios internos de cada bloco criados conforme especificação (ex: `01_ti_foundations/concepts`, `07_health_data/healthcare_datasets`, `14_automation/openclaw_jobs`, etc).
- Agentes construtores lançados em paralelo pelo orquestrador Claude Code (DocsMestres responsável pelos documentos mestres).
- Criados 8 documentos mestres na raiz:
  - `README.md` — objetivo, navegação, convenções, conexão com Dexter/Maestro/Git.
  - `CLAUDE.md` — papel do Claude, limites, obrigações de fim de rodada.
  - `MEMORY.md` — memória estável (visão, princípios, 3 camadas).
  - `TASKS_MASTER.md` — backlog com 60+ tarefas distribuídas em 17 blocos, pesos por bloco.
  - `TASKS_NOW.md` — 10 tarefas priorizadas para a próxima rodada.
  - `NEXT_SESSION_CONTEXT.md` — ponto de retomada.
  - `CHANGELOG.md` — este arquivo.
  - `PROJECT_STRUCTURE.md` — mapa da árvore com descrição por bloco.
- Contrato de status adotado: `EXECUTADO | PLANEJADO | PENDENTE | BLOQUEADO`.
- Contrato de nomenclatura adotado: pastas/arquivos em `snake_case` ASCII, sem acentos/espaços/cedilha; conteúdo Markdown em português correto com acentos.

### PLANEJADO (próxima rodada)

- KTC-001, KTC-002, KTC-004 (governança).
- KTC-170, KTC-174 (agentes base).
- KTC-110, KTC-100, KTC-120 (primeiros conteúdos substantivos).

### PENDENTE

- Inicialização de submódulo Git específico para esta pasta (aguardando decisão: manter dentro do Git do Dexter ou separar).
- Integração formal com OpenClaw/Maestro (aguardando KTC-142).

### BLOQUEADO

- Nenhum item no momento.

### Decisões registradas

- Blocos numerados são estáveis; renomear exige aprovação humana.
- `16_inbox/` é a única porta de entrada para conteúdo cru.
- `AGENTS/docs_mestres.md` considerado implicitamente EXECUTADO pela entrega desta rodada (KTC-171).
