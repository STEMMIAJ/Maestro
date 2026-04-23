---
titulo: Framework de Certificações em TI
tipo: master_summary
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
---

# Framework de Certificações em TI

## Premissa

Certificação é **sinal**, não prova de competência. Contratante usa como filtro quando não tem tempo de avaliar fundo. Para profissional, vale a pena quando:

1. **Fecha lacuna real** — obriga estudo estruturado de área desconhecida.
2. **É linguagem formal do nicho** — em consultoria big-4, em vaga de cloud, em contratação pública.
3. **Sinaliza a um mercado específico** — ex.: AWS para quem nunca tocou nuvem.

Não vale a pena quando:

- Serve de muleta para não construir portfólio.
- Já existe prova de competência mais forte (projeto entregue, publicação, CRM ativo + produto pericial).
- Custo (tempo + dinheiro) é desproporcional ao retorno.

## Regra para o perfil médico-perito

O CRM ativo + produção pericial + Dexter já operam como credencial forte em interseção saúde/TI. Certificação deve preencher o que **falta**, não duplicar o que já existe:

- **Faltando:** fundamento formal de dado, cloud e segurança.
- **Não faltando:** domínio clínico, escrita técnica, raciocínio estruturado.

Prioridade prática: Google Data Analytics > AWS Cloud Practitioner > AWS ML/AI > Security+ > demais.

## Lista — 18 certificações

### Generalistas / fundamentos

| Nome | Emissor | Nível | Relevância médico/perito | Esforço estimado |
|---|---|---|---|---|
| CompTIA ITF+ | CompTIA | Iniciante | Baixa (fundamento genérico) | 20-40h |
| Google IT Support Professional | Google (Coursera) | Iniciante | Baixa-média | 60-100h |

### Cloud

| Nome | Emissor | Nível | Relevância | Esforço |
|---|---|---|---|---|
| AWS Cloud Practitioner (CLF-C02) | AWS | Iniciante | Média-alta (linguagem básica de nuvem) | 40-60h |
| AWS Solutions Architect Associate | AWS | Intermediário | Média | 100-150h |
| Azure Fundamentals (AZ-900) | Microsoft | Iniciante | Média (saúde BR usa muito Azure) | 30-50h |
| Azure Data Fundamentals (DP-900) | Microsoft | Iniciante | Alta (dado em saúde) | 40-60h |
| Google Cloud Digital Leader | Google | Iniciante | Média | 30-50h |

### Dados

| Nome | Emissor | Nível | Relevância | Esforço |
|---|---|---|---|---|
| Google Data Analytics Professional Certificate | Google (Coursera) | Iniciante | Alta (SQL, R, visualização, fundamento) | 100-180h |
| DataCamp Data Analyst / Data Scientist tracks | DataCamp | Iniciante-intermediário | Alta (prática guiada) | 80-200h |
| Microsoft DP-203 Data Engineer Associate | Microsoft | Intermediário | Média-alta | 120-160h |
| IBM Data Science Professional Certificate | IBM (Coursera) | Iniciante | Média | 80-150h |

### Segurança

| Nome | Emissor | Nível | Relevância | Esforço |
|---|---|---|---|---|
| CompTIA Security+ | CompTIA | Iniciante-intermediário | Média-alta (LGPD + base) | 80-120h |
| ISO/IEC 27001 Lead Implementer | PECB / EXIN | Intermediário | Alta (consultoria de compliance saúde) | 60-100h |
| CISSP | (ISC)² | Sênior | Baixa-média (exige 5 anos experiência) | 200-400h |
| Certified Ethical Hacker (CEH) | EC-Council | Intermediário | Baixa (ofensivo, fora do perfil) | 150-200h |

### IA / ML

| Nome | Emissor | Nível | Relevância | Esforço |
|---|---|---|---|---|
| AWS Certified AI Practitioner (AIF-C01) | AWS | Iniciante | Alta (linguagem de IA aplicada) | 40-80h |
| AWS Certified Machine Learning Specialty | AWS | Avançado | Média (profundo em ML prod) | 150-250h |
| Azure AI Fundamentals (AI-900) | Microsoft | Iniciante | Alta | 30-50h |
| Azure AI Engineer Associate (AI-102) | Microsoft | Intermediário | Média-alta | 100-150h |

### Gestão / produto

| Nome | Emissor | Nível | Relevância | Esforço |
|---|---|---|---|---|
| PSPO I (Scrum.org) | Scrum.org | Iniciante | Média | 20-30h |
| PSM I (Scrum.org) | Scrum.org | Iniciante | Baixa-média | 20-30h |
| PMP | PMI | Intermediário | Baixa (custo alto, ROI baixo para saúde/TI direto) | 200-300h |

### Específicas saúde/TI

| Nome | Emissor | Nível | Relevância | Esforço |
|---|---|---|---|---|
| HL7 FHIR Fundamentals | HL7 International | Iniciante | Alta (padrão de interoperabilidade saúde) | 40-80h |
| CAHIMS / CPHIMS | HIMSS | Iniciante/Sênior | Alta (informática em saúde, EUA) | **Dado (2026-04-23):** sem centro oficial BR; prova via Pearson VUE EUA (remoto ou presencial). Equivalente nacional: cpTICS da SBIS — fonte: https://sbis.org.br/certificacoes/ |
| cpTICS (SBIS) | SBIS | Iniciante | Alta (profissional TIC em saúde BR) | **Dado (2026-04-23):** certificação nacional, exame periódico, foco LGPD/interoperabilidade/PEP — fonte: https://sbis.org.br/certificacoes/certificacao-profissional/ |

## Sinalização por nível de carreira

| Nível | Certificação faz sentido para |
|---|---|
| Júnior | Mostrar que estudou — Cloud Practitioner, Data Fundamentals, Security+ |
| Pleno | Fechar lacuna específica ou virar referência em nicho — Associate tracks, DP-203, FHIR |
| Sênior | Normalmente não precisa; exceção: consultoria, mudança de país, linguagem formal (CISSP, PMP) |

## Estimativas de custo (2026-04-23)

| Certificação | Preço oficial 2026 | Fonte |
|---|---|---|
| AWS Cloud Practitioner (CLF-C02) | **USD 100** (~R$ 510) | https://aws.amazon.com/certification/certified-cloud-practitioner/ |
| AWS Solutions Architect Associate (SAA-C03) | **USD 150** (~R$ 765). Após 1a AWS, 50% off nas próximas | https://aws.amazon.com/certification/certified-solutions-architect-associate/ |
| Azure AI Fundamentals (AI-900) | **USD 99** (~R$ 505). Atenção: AI-900 retira em 30-jun-2026, substituída por AI-901 | https://learn.microsoft.com/en-us/credentials/certifications/exams/ai-900/ |
| Azure Fundamentals (AZ-900) | **USD 99** (~R$ 505) | https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/ |
| Google Data Analytics Professional (Coursera) | **USD 49/mês** ou Coursera Plus ~USD 59/mês; total 3–6 meses = USD 150–294 | https://www.coursera.org/professional-certificates/google-data-analytics |
| DataCamp Premium (inclui Data Analyst track) | **USD 13/mês** anual (~USD 156/ano) ou USD 19/mês mensal | https://www.datacamp.com/pricing |
| CompTIA Security+ (SY0-701) | **USD 425** voucher; com material USD 700–1000 total | https://www.comptia.org/certifications/security |
| CISSP | **USD 749** (Americas); +USD 199 Peace of Mind opcional | https://www.isc2.org/register-for-exam/isc2-exam-pricing |
| HL7 FHIR Foundational | **USD ~500–800** exame; +curso USD 500–2000 opcional | https://www.hl7.org/certification/fhir.cfm |
| Linux Foundation LFS101 (Intro Linux) | **Gratuito** no edX (curso); certificado verificado USD 99 | https://training.linuxfoundation.org/training/introduction-to-linux/ — [BUSCA FEITA EM 2026-04-23 — valor confirmado na página do curso] |
| cpTICS (SBIS) | **Dado (2026-04-23):** [BUSCA FEITA EM 2026-04-23 — valor exato não público; inscrição via site SBIS por edital]. Edições anteriores: ~R$ 400–700 | https://sbis.org.br/certificacoes/ |

## Armadilhas

- **Empilhamento sem projeto** — 5 certificados sem um repositório público = currículo suspeito.
- **Pirâmide errada** — pular fundamento para ir direto em specialty.
- **Validade** — AWS/Azure expiram em 2–3 anos. Planejar renovação.
- **Certificação do empregador que você não quer** — aceitar certificação que a empresa paga e depois não serve para a trilha pessoal.

## Ver também

- `junior_pleno_senior_framework.md` — certificação vs. nível real.
- `health_data_career_paths.md` — certificações específicas de trilha.
