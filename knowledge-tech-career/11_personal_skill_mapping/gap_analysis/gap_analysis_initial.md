---
titulo: Análise de Lacunas Inicial
bloco: 11_personal_skill_mapping
arquivo: gap_analysis/gap_analysis_initial.md
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# Análise de Lacunas — Corte Inicial

Classificação: **ALTA** (trava projeto atual ou cargo-alvo próximo), **MÉDIA** (limita crescimento 6–12 meses), **BAIXA** (nice-to-have, sem urgência).

## ALTA

### 1. Testes automatizados (pytest)
- **Lacuna**: zero suite real. Scripts do Dexter rodam sem cobertura.
- **Impacto**: qualquer mudança quebra silenciosamente. Risco alto em pipelines periciais (erro = laudo errado).
- **Ação mínima**: escrever pytest para 1 função de `usar_template_pericia.py`. Até 2026-05-15.
- **Bloco**: `02_programming/testing/`

### 2. SQL intermediário (JOIN, GROUP BY, CTE)
- **Lacuna**: SELECT simples só. Banco Dexter com dezenas de tabelas não é explorado.
- **Impacto**: impossível extrair relatório cruzado (processos × movimentações × prazos) sem depender de Claude.
- **Ação mínima**: 10 exercícios de JOIN sobre o SQLite do Dexter. Até 2026-05-30.
- **Bloco**: `06_data_analytics/sql/`

### 3. Git além do básico (branch, merge, rebase)
- **Lacuna**: medo de quebrar repo. Evita branch paralela.
- **Impacto**: trabalha sempre em main, sem segurança. Rollback difícil.
- **Ação mínima**: exercício formal com `git-worktree` + feature branch em repo-sandbox. Até 2026-05-10.
- **Bloco**: `01_ti_foundations/git/`

### 4. Docker básico
- **Lacuna**: zero. Ambientes frágeis, dependências no Mac.
- **Impacto**: não consegue rodar pipeline em outro computador. Portabilidade zero.
- **Ação mínima**: containerizar 1 script Python existente. Até 2026-06-15.
- **Bloco**: `04_systems_architecture/containers/`

### 5. Segurança aplicada (segredos, LGPD técnica)
- **Lacuna**: .env funciona, mas gestão informal. Dados sensíveis de saúde circulam.
- **Impacto**: risco regulatório real. Perito lida com dado sensível por definição.
- **Ação mínima**: auditoria de onde existe CPF/prontuário em claro no ecossistema + checklist LGPD. Até 2026-05-20.
- **Bloco**: `05_security_and_governance/`

## MÉDIA

### 6. Estatística aplicada com pandas/numpy
- **Lacuna**: conceito médico existe, código estatístico não.
- **Impacto**: não consegue quantificar incapacidade em massa, nem validar padrões em laudos.
- **Ação mínima**: 1 notebook com t-test e regressão sobre dados reais anonimizados.
- **Bloco**: `06_data_analytics/statistics/`

### 7. FHIR / HL7 básico
- **Lacuna**: não conhece padrão.
- **Impacto**: se interoperar com hospital/PEP, começa do zero.
- **Ação mínima**: ler especificação FHIR R4 resumo + 1 exemplo de Patient resource.
- **Bloco**: `07_health_data/fhir/`

### 8. Vector DB + embeddings (RAG prático)
- **Lacuna**: conhece teoria, nunca implementou.
- **Impacto**: laudos e doutrina não são indexados semanticamente.
- **Ação mínima**: POC com SQLite-VSS ou Chroma sobre 10 laudos.
- **Bloco**: `08_ai_and_automation/rag/`

### 9. Inglês técnico escrito
- **Lacuna**: hesita ao escrever.
- **Impacto**: perde acesso a comunidade global, entrevistas internacionais, contribuições OSS.
- **Ação mínima**: 1 issue ou PR em inglês em repo open source / mês.
- **Bloco**: `10_career_map/communication/`

### 10. Avaliação de agentes (evals)
- **Lacuna**: ajusta prompt no olhômetro.
- **Impacto**: não mede regressão quando muda skill/agente.
- **Ação mínima**: montar conjunto de 20 casos-teste pericial + script de eval.
- **Bloco**: `08_ai_and_automation/evaluation/`

## BAIXA

### 11. JavaScript / Node
- **Lacuna**: quase zero.
- **Impacto**: sem front-end próprio, depende de HTML estático. Não urgente — dashboards podem ser Streamlit/Panel.
- **Ação mínima**: ignorar até decisão de construir front-end dinâmico.
- **Bloco**: `03_web_development/javascript/`

### 12. Kubernetes / orquestração
- **Lacuna**: zero.
- **Impacto**: irrelevante para uso atual (máquina única, launchd). Só importa se escalar para SaaS.
- **Ação mínima**: adiar até 2027+.
- **Bloco**: `04_systems_architecture/orchestration/`

### 13. Cloud certification (AWS/GCP)
- **Lacuna**: zero prática.
- **Impacto**: CV vazio nessa área. Mas não é requisito do trabalho atual.
- **Ação mínima**: decidir se persegue Cloud Practitioner em Q4 2026.
- **Bloco**: `10_career_map/certifications/`

### 14. Frontend design / UX
- **Lacuna**: zero teoria formal.
- **Impacto**: interfaces internas feias mas funcionais. Só importa se virar produto para terceiros.
- **Ação mínima**: adiar.
- **Bloco**: `03_web_development/design/`

### 15. Mobile (iOS/Android nativo)
- **Lacuna**: zero.
- **Impacto**: nenhum no horizonte atual.
- **Ação mínima**: descartado do backlog.
- **Bloco**: N/A

## Revisão
Reavaliar em 2026-07-23. Gaps ALTA não resolvidos viram P0 em `study_backlog/`.
