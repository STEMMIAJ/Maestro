---
titulo: "Expectativas por Papel — Dev, Data, SRE, AI Engineer"
bloco: "10_career_map"
tipo: "referencia"
nivel: "todos"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 10
---

# Expectativas por Papel

Cada papel tem competências mínimas esperadas em cada senioridade. Listas abaixo são checklist funcional — se falta algo da lista do pleno, ainda não é pleno naquele papel.

## 1. Software Developer (Backend/Fullstack)

### Júnior
- Git básico (branch, PR, rebase simples)
- Escrever função testável, nomear variável legível
- Usar linter e formatter sem reclamar
- Entender HTTP, status codes, REST básico
- SQL básico (SELECT, JOIN, WHERE)
- Rodar aplicação localmente seguindo README

### Pleno
- Desenhar API pequena de ponta a ponta
- Escrever testes unitários e de integração
- Lidar com BD relacional: índice, transação, migração
- Observabilidade mínima: log estruturado, métrica
- Code review construtivo
- Entender CI/CD do time, debugar pipeline quebrado

### Sênior
- Arquitetar sistema com múltiplos serviços
- Definir contratos (OpenAPI, gRPC) e versionamento
- Trade-off consistência/disponibilidade, sync/async
- Mentorar, recrutar, definir padrão técnico
- Influenciar decisão de produto com dado técnico

## 2. Data Engineer

### Júnior
- SQL sólido (CTE, window function, explain básico)
- Python com pandas ou SQL-first com dbt
- Ingestão simples (CSV, API, webhook)
- Ler README de pipeline alheio e rodar

### Pleno
- DAG Airflow/Prefect completa com retry e alert
- Modelagem dimensional (fato/dimensão, SCD)
- dbt com testes, documentação, CI
- Particionamento e performance em DW (BigQuery, Snowflake, Redshift)
- Contrato de dados com produtor

### Sênior
- Arquitetura lakehouse, medalhão (bronze/silver/gold)
- Governança: catálogo, lineage, qualidade
- Custo de nuvem sob controle (FinOps)
- Padrão de streaming (Kafka, Kinesis, CDC)
- Definir política org-wide de dado

## 3. SRE / DevOps / Platform

### Júnior
- Linux/Shell confortável
- Docker básico: build, run, debug
- Git + GitHub Actions simples
- Ler log, identificar stack trace

### Pleno
- Kubernetes operação: deploy, rollback, debug de pod
- IaC: Terraform ou Pulumi módulo próprio
- Observabilidade: Prometheus + Grafana + tracing
- Runbook para incidente comum
- Plantão eficaz

### Sênior
- Definir SLI/SLO, error budget
- Post-mortem sem culpa, ação corretiva concreta
- Arquitetura multi-região, failover
- Capacidade e custo em escala
- Plataforma self-service para dev

## 4. AI Engineer / LLM Engineer

### Júnior
- Consumir API de LLM (OpenAI, Anthropic) em Python
- Prompt básico, formatação estruturada (JSON)
- RAG simples com embeddings + vetor DB local
- Log de chamadas, cálculo de custo

### Pleno
- Eval framework (promptfoo, ragas, LangSmith)
- RAG com ranking, filtro, chunking adequado
- Prompt caching, batch, streaming
- Observability: latência, custo por unidade de negócio
- Lidar com tool calling e orquestração

### Sênior
- Arquitetura multi-agente com guardrails
- Red team de próprios produtos de IA
- Fine-tuning quando faz sentido vs. prompt + RAG
- Política de privacidade (LGPD/GDPR) nas chamadas
- Decidir build vs. buy, hosted vs. self-host

## 5. Security Engineer

### Júnior
- Ler log de SIEM, triagem de alerta
- OWASP Top 10 conceitual
- Uso de scanner SAST/DAST básico
- Gestão de senha, MFA, criptografia básica

### Pleno
- Threat model de aplicação
- Pentest interno de escopo limitado
- Resposta a incidente com runbook
- IAM em nuvem (AWS/GCP/Azure) com menor privilégio
- Compliance (ISO 27001, SOC 2) aplicado

### Sênior
- Programa de segurança org-wide
- Negociação com produto para shift-left
- Métrica de risco comunicável à diretoria
- Gestão de vulnerabilidade crônica
- Playbook de resposta em escala

## Checklist cruzado — perito-tech híbrido

Dr. Jesus no papel **Perito com Automação (self-employed)**:

- [x] Python de automação nível pleno
- [x] Git básico (usa em projetos próprios)
- [x] SQL básico (SQLite do Dexter)
- [x] Segurança: LGPD aplicada, MFA, backup cifrado
- [ ] CI/CD pessoal: [TODO/RESEARCH: implementar GitHub Actions para testes básicos do Dexter]
- [ ] Observabilidade: [TODO — métricas básicas no monitor de processos]
- [ ] Eval framework para IA pericial: [TODO]

## Como ler o checklist

1. Marcar o que já sabe fazer em produção.
2. Priorizar 3 gaps por quadrimestre.
3. Cada gap = 1 projeto real (não curso).

## Referência cruzada

- `../junior_pleno_senior/sinais_concretos_de_cada_nivel.md`
- `../professions_taxonomy/familias_profissionais_detalhadas.md`
- `../certifications/mapa_certificacoes_por_trilha.md`
- `../learning_paths/trilha_medico_para_tech.md`
