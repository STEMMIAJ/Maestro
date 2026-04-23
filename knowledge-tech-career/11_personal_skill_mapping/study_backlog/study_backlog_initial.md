---
titulo: Backlog de Estudo — Corte Inicial
bloco: 11_personal_skill_mapping
arquivo: study_backlog/study_backlog_initial.md
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# Backlog de Estudo — Dr. Jesus

Prioridade: **P0** fazer nas próximas 4 semanas · **P1** próximos 3 meses · **P2** próximos 6–12 meses.

Formato por item: título · por que importa · recurso primário · entrada mínima · saída esperada.

## P0 (4 semanas — 2026-04-23 a 2026-05-21)

### 1. pytest — primeira suite real
- **Por que**: lacuna ALTA #1. Pipeline pericial sem teste = risco.
- **Recurso**: "Python Testing with pytest" (Brian Okken) — caps 1–3
- **Entrada**: 4h leitura + 2h prática
- **Saída**: 5 testes passando sobre `usar_template_pericia.py`

### 2. git branch + merge conflict
- **Por que**: lacuna ALTA #3. Sem branch = sem segurança.
- **Recurso**: "Pro Git" (Chacon) caps 3 + prática em repo-sandbox
- **Entrada**: 2h leitura + 3h exercício
- **Saída**: feature-branch criada, merge com conflito resolvido manualmente, documentado

### 3. SQL JOIN + GROUP BY sobre Dexter
- **Por que**: lacuna ALTA #2.
- **Recurso**: SQLBolt caps 6–10 + banco real do Dexter
- **Entrada**: 3h exercícios
- **Saída**: 10 queries resolvidas, 1 relatório cruzado gerado

### 4. Auditoria LGPD do ecossistema
- **Por que**: lacuna ALTA #5. Risco regulatório.
- **Recurso**: Guia ANPD dados sensíveis + `grep` por CPF/prontuário
- **Entrada**: 4h
- **Saída**: checklist de conformidade + lista de correções

### 5. Docker — container do primeiro script
- **Por que**: lacuna ALTA #4.
- **Recurso**: "Docker Curriculum" (prakhar1989) + Docker Getting Started
- **Entrada**: 3h leitura + 3h prática
- **Saída**: 1 script Python rodando em container local

## P1 (próximos 3 meses — até 2026-07-23)

### 6. pytest avançado — fixtures, parametrize, mocks
- **Por que**: extender cobertura para pipelines inteiros.
- **Recurso**: Okken caps 4–6
- **Entrada**: 6h
- **Saída**: 3 pipelines cobertos

### 7. pandas intermediário (merge, groupby, pivot)
- **Por que**: relatórios periciais em massa.
- **Recurso**: "Python for Data Analysis" (McKinney) caps 5–8
- **Entrada**: 10h
- **Saída**: notebook com 5 análises reais sobre laudos anonimizados

### 8. Estatística inferencial com Python
- **Por que**: lacuna MÉDIA #6.
- **Recurso**: StatQuest (YouTube) + scipy.stats docs
- **Entrada**: 12h
- **Saída**: 1 notebook com t-test, chi², regressão linear aplicada a dados de incapacidade

### 9. FastAPI — primeiro endpoint
- **Por que**: abrir Dexter para integrações (laudo por POST).
- **Recurso**: docs oficiais FastAPI (tiangolo)
- **Entrada**: 8h
- **Saída**: 1 endpoint rodando localmente, auth básica, retorna PDF

### 10. RAG POC com vector DB
- **Por que**: lacuna MÉDIA #8. Buscar doutrina/laudos semanticamente.
- **Recurso**: docs Chroma + SQLite-VSS + artigo Anthropic contextual retrieval
- **Entrada**: 10h
- **Saída**: POC indexando 50 laudos, busca semântica funcional

### 11. Regex avançado aplicado a processos
- **Por que**: parsing de movimentações PJe/DJEN depende disso.
- **Recurso**: regex101 + "Regular Expressions Cookbook"
- **Entrada**: 4h
- **Saída**: 10 padrões prontos catalogados

### 12. Git rebase, cherry-pick, bisect
- **Por que**: refinar histórico, debug histórico.
- **Recurso**: "Pro Git" caps 7
- **Entrada**: 4h
- **Saída**: rebase interativo executado em repo-sandbox, bisect usado para achar 1 bug plantado

### 13. Inglês técnico — escrita
- **Por que**: lacuna MÉDIA #9.
- **Recurso**: 1 issue/mês em repo público + Grammarly feedback
- **Entrada**: 1h/semana
- **Saída**: 3 issues/PRs em inglês aceitos

### 14. Evals para agentes (Claude/Anthropic)
- **Por que**: lacuna MÉDIA #10.
- **Recurso**: Anthropic cookbook — evaluations
- **Entrada**: 8h
- **Saída**: suite de 20 casos-teste pericial rodando com CI local

### 15. FHIR R4 — Patient, Observation, Encounter
- **Por que**: lacuna MÉDIA #7.
- **Recurso**: hl7.org/fhir + simplifier.net
- **Entrada**: 8h
- **Saída**: 1 Patient + Observation em JSON válido, script que lê/escreve

## P2 (6–12 meses — até 2027-04)

### 16. AWS Cloud Practitioner — estudo formal
- **Por que**: CV vazio em cloud. Decidir perseguir ou não.
- **Recurso**: AWS Skill Builder (gratuito) + Tutorials Dojo
- **Entrada**: 40h
- **Saída**: decisão: tomar prova ou descartar

### 17. Design de sistemas distribuídos — leitura
- **Por que**: base teórica para futuro SaaS.
- **Recurso**: "Designing Data-Intensive Applications" (Kleppmann)
- **Entrada**: 60h (leitura lenta)
- **Saída**: resumos por capítulo em `15_memory/promoted/`

### 18. Terraform básico
- **Por que**: infra-como-código antes de escalar.
- **Recurso**: HashiCorp Learn
- **Entrada**: 15h
- **Saída**: 1 bucket + 1 Lambda provisionados (se AWS decidido)

### 19. React mínimo para dashboards internos
- **Por que**: alternativa ao Streamlit se houver limite.
- **Recurso**: "The Road to React" (Wieruch)
- **Entrada**: 20h
- **Saída**: 1 dashboard lendo API FastAPI do item 9

### 20. Observabilidade (logs, métricas, traces)
- **Por que**: pipelines em produção precisam de observabilidade.
- **Recurso**: Grafana OSS + Loki tutorials
- **Entrada**: 15h
- **Saída**: Dexter emitindo logs estruturados + dashboard simples

### 21. Arquitetura de dados de saúde (OMOP CDM)
- **Por que**: padrão para pesquisa. Se migrar para produção acadêmica.
- **Recurso**: OHDSI Book of OHDSI (gratuito)
- **Entrada**: 20h
- **Saída**: conceito mapeado, decisão sobre adoção

### 22. Security+ — decisão
- **Por que**: avaliar se vale perseguir em 2027.
- **Recurso**: Professor Messer (YouTube, gratuito)
- **Entrada**: 5h para avaliar
- **Saída**: decisão perseguir/descartar

### 23. Publicação — 1 artigo ou talk
- **Por que**: evidência externa forte de habilidade.
- **Recurso**: blog pessoal + comunidades (Dev.to, Hacker News, SBIS)
- **Entrada**: 15h
- **Saída**: 1 publicação sobre "IA aplicada a perícia médico-judicial"

## Revisão
Reavaliar P0 em 2026-05-21. P1 em 2026-07-23. P2 em 2026-10-23.
