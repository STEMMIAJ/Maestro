---
titulo: "Mapa de Certificações por Trilha"
bloco: "10_career_map"
tipo: "referencia"
nivel: "todos"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "parcial"
tempo_leitura_min: 12
---

# Mapa de Certificações por Trilha

Certificação é sinal, não competência. Bem escolhida, abre portas em RH tradicional, valida base teórica, estrutura estudo. Mal escolhida, consome dinheiro e tempo sem retorno.

[TODO/RESEARCH: atualizar preços 2026 (consultar sites oficiais) e validade vigente]

## Regras gerais

1. **Não tirar em massa.** 1 certificação boa > 5 genéricas.
2. **Casar com projeto real.** Certifica depois de ter construído algo que use o conteúdo.
3. **Priorizar de emissor forte.** AWS, Microsoft, Google, CNCF, ISC2, ISACA, (ISC)², CompTIA, Anthropic/OpenAI.
4. **Verificar validade.** Muitas expiram em 3 anos.
5. **Custo-benefício.** Algumas custam USD 300+ por tentativa.

## Cloud

| Certificação | Emissor | Nível | Custo aproximado | Observação |
|--------------|---------|-------|------------------|-----------|
| AWS Cloud Practitioner | AWS | Intro | USD 100 | Base conceitual |
| AWS Solutions Architect Associate | AWS | Pleno | USD 150 | Padrão de entrada |
| AWS Solutions Architect Professional | AWS | Sênior | USD 300 | Prova longa e difícil |
| AWS DevOps Engineer Professional | AWS | Sênior | USD 300 | — |
| AWS Security Specialty | AWS | Especialista | USD 300 | Foco em segurança |
| GCP Associate Cloud Engineer | Google | Pleno | USD 125 | — |
| GCP Professional Cloud Architect | Google | Sênior | USD 200 | — |
| Azure Fundamentals (AZ-900) | MS | Intro | USD 99 | — |
| Azure Administrator (AZ-104) | MS | Pleno | USD 165 | — |

## Dados

| Certificação | Emissor | Observação |
|--------------|---------|-----------|
| Databricks Data Engineer Associate | Databricks | Stack Spark/Delta |
| Databricks Data Engineer Professional | Databricks | — |
| Snowflake SnowPro Core | Snowflake | DW moderno |
| GCP Professional Data Engineer | Google | BigQuery-centrado |
| AWS Data Engineer Associate | AWS | Novo 2024 |
| dbt Analytics Engineering | dbt Labs | Transformações SQL |
| Airflow Certification | Astronomer | Orquestração |

[TODO/RESEARCH: preços]

## Segurança

| Certificação | Emissor | Nível | Observação |
|--------------|---------|-------|-----------|
| Security+ | CompTIA | Intro | Base geral |
| CySA+ | CompTIA | Pleno | Blue team |
| CISSP | (ISC)² | Sênior | Gerencial, requer experiência |
| CCSP | (ISC)² | Sênior | Cloud security |
| CISM | ISACA | Sênior | Gestão |
| CEH | EC-Council | Pleno | Pentest orientado |
| OSCP | Offensive Security | Pleno-Sênior | Prático, duro, reconhecido |
| PNPT | TCM Security | Pleno | Alternativa ao OSCP |
| GSEC, GCIH, GCFA | SANS/GIAC | Variados | Caros, alta reputação |
| ISO 27001 Lead Implementer / Auditor | PECB/Exin | Pleno | Compliance |
| Exin Privacy & Data Protection | Exin | Pleno | GDPR/LGPD |
| DPO — ENCE, IAPP CIPM/CIPP/CIPT | IAPP | Pleno | Privacidade |

## IA / LLM

| Certificação | Emissor | Observação |
|--------------|---------|-----------|
| Deep Learning Specialization | deeplearning.ai (Coursera) | Clássico, Ng |
| TensorFlow Developer | Google | Base TF |
| AWS ML Specialty | AWS | Aplicado |
| Azure AI Engineer (AI-102) | MS | Aplicado, Azure OpenAI |
| NVIDIA Generative AI | NVIDIA | Novo |
| Anthropic/OpenAI: sem certificação formal, usar docs oficiais |

[TODO/RESEARCH: verificar se Anthropic lançou certificação oficial 2026]

## DevOps / Kubernetes

| Certificação | Emissor | Observação |
|--------------|---------|-----------|
| CKA (Certified Kubernetes Administrator) | CNCF/Linux Foundation | Padrão |
| CKAD (Application Developer) | CNCF | App em K8s |
| CKS (Kubernetes Security) | CNCF | Sec em K8s |
| Terraform Associate | HashiCorp | IaC |
| Vault Associate | HashiCorp | Cofre |
| LFCS (Linux Foundation Certified SysAdmin) | LF | Linux |
| RHCSA / RHCE | Red Hat | Linux corporativo |

## Produto / Ágil

| Certificação | Emissor | Observação |
|--------------|---------|-----------|
| CSPO / CSM | Scrum Alliance | Papéis Scrum |
| PSPO / PSM | Scrum.org | Alternativa |
| SAFe | Scaled Agile | Empresa grande |
| PMP | PMI | Gestão tradicional |

## Saúde + Dados (nicho Dr. Jesus)

| Certificação | Emissor | Observação |
|--------------|---------|-----------|
| CPHIMS / CAHIMS | HIMSS | Informática em saúde |
| Certified in Healthcare Privacy (CHPC) | HCCA | Privacidade em saúde |
| OHDSI / OMOP training | OHDSI | RWE |
| HL7 FHIR Foundation | HL7 | Interoperabilidade |

## Estratégia para Dr. Jesus (priorização)

Ordem sugerida por retorno pericial + valor técnico:

1. **Exin Privacy & Data Protection Foundation** — barato, valida base LGPD formal.
2. **IAPP CIPM** — posicionamento DPO em saúde.
3. **AWS Cloud Practitioner** — base conceitual de nuvem em 40h estudo.
4. **dbt Analytics Engineering** — se for entrar em Data.
5. **CISSP** — longo prazo, após 5 anos de experiência formal documentada.

Evitar inicialmente: OSCP (caro e prático-intenso), CISSP sem experiência, massa de certs AWS/Azure redundantes.

## Como preparar

1. Ler ementa oficial.
2. 1 livro oficial + 1 curso prático.
3. Simulados até score > 80% consistente.
4. Marcar prova com 4 semanas de margem.
5. Fazer.
6. Renovar via CPE quando aplicável.

## Referência cruzada

- `../role_expectations/expectativas_por_papel.md`
- `../salary_market_signals/sinais_de_mercado_br_2026.md`
- `../learning_paths/trilha_medico_para_tech.md`

[TODO/RESEARCH: preços oficiais por moeda, validade, política de retake em 2026]
