---
titulo: "Pesquisa Round 1 — preenchimento de TODO/RESEARCH"
tipo: market_research
versao: 0.1
status: vigente
data: 2026-04-23
agente: R3-Researcher (Opus 4.7)
---

# Pesquisa Round 1 — 2026-04-23

Objetivo: preencher marcações `[TODO/RESEARCH]` prioritárias com dados verificáveis. Hoje 2026-04-23.

## Escopo atacado

| # | Arquivo | TODOs fechados | Observação |
|---|---|---|---|
| 1 | `13_reports/master_summaries/certifications_framework.md` | 6 (tabela de custos) + 1 (CAHIMS/CPHIMS disponibilidade BR) | Adicionada linha cpTICS/SBIS e Linux Foundation LFS101 |
| 2 | `13_reports/master_summaries/ti_career_overview.md` | Adicionada seção nova "Bandas salariais BR 2026" (5 famílias × 3 níveis) | Seção não tinha TODO explícito mas foi priorizada pelo escopo |
| 3 | `13_reports/master_summaries/health_data_career_paths.md` | 2 (SBIS/títulos BR; Fiocruz EAD farmacoepi) | Fiocruz sem curso fixo de farmacoepi; alternativas apontadas |
| 4 | `08_ai_and_automation/automation_workflows/n8n_zapier_make_comparacao.md` | 3 (Zapier 2026, Make 2026, bloco TODO final) | Make migrou operations→credits em ago/2025 |
| 5 | `07_health_data/healthcare_datasets/datasus_tabnet_sia_sih.md` | 1 (tutorial TabNet 2026) | Tutorial oficial DATASUS ainda é a versão 2020 (não houve update) |

Arquivos não atacados porque não existem ainda no repositório:
- `10_career_map/salary_market_signals/sinais_de_mercado_br_2026.md` (pasta vazia)
- `10_career_map/certifications/mapa_certificacoes_por_trilha.md` (pasta vazia)

## Achados por TODO fechado

### Preços de certificação (2026)

| Item | Valor | Confiança | Fonte |
|---|---|---|---|
| AWS Cloud Practitioner CLF-C02 | USD 100 | Alta | aws.amazon.com/certification/certified-cloud-practitioner/ |
| AWS Solutions Architect Associate SAA-C03 | USD 150 | Alta | aws.amazon.com |
| Azure AI-900 | USD 99 (retira 30/jun/2026 → AI-901) | Alta | learn.microsoft.com |
| Azure AZ-900 | USD 99 | Alta | learn.microsoft.com |
| Google Data Analytics (Coursera) | USD 49/mês (USD 150–294 total 3–6 meses) | Alta | coursera.org |
| DataCamp Premium | USD 13/mês anual (USD 156/ano) | Alta | datacamp.com/pricing |
| CompTIA Security+ SY0-701 | USD 425 voucher (USD 700–1000 com material) | Alta | flashgenius.net; getcertified4less.com |
| CISSP (ISC)² | USD 749 | Alta | isc2.org/register-for-exam/isc2-exam-pricing |
| HL7 FHIR Foundational | USD 500–800 (faixa) | Média | hl7.org/certification/ (preço não publicado em único lugar, varia por evento) |
| Linux Foundation LFS101 | Gratuito edX; cert USD 99 | Alta | training.linuxfoundation.org |
| SBIS cpTICS | Edital periódico; valor não público | Baixa-média | sbis.org.br/certificacoes/ |

### Preços de automação (2026)

| Produto | Valor | Confiança | Fonte |
|---|---|---|---|
| Zapier Free | 100 tasks/mês | Alta | zapier.com/pricing |
| Zapier Starter | USD 19,99/mês anual, 750 tasks | Alta | zapier.com/pricing |
| Zapier Professional | USD 49/mês, 2.000 tasks | Alta | zapier.com/pricing |
| Zapier Team | USD 69,50/user/mês anual | Alta | zapier.com/pricing |
| Make Free | 1.000 créditos/mês | Alta | make.com/en/pricing |
| Make Core | USD 10,59/mês, 10k créditos | Alta | make.com/en/pricing |
| Make Pro | USD 18,82/mês | Alta | make.com/en/pricing |

### Salários BR 2026 (medianas e faixas)

| Família | Júnior | Pleno (mediana) | Sênior | Fonte principal |
|---|---|---|---|---|
| Desenvolvimento | R$ 2.300–3.900 | R$ 6.671 (full-stack) | R$ 10.271 mediana; piso real R$ 13.000+ | Glassdoor BR; huntit.com.br |
| Analista de dados | R$ 3.500–5.500 | R$ 5.500–9.000 | R$ 9.000–15.000+ | blog.somostera.com |
| Cientista de dados | R$ 6.000+ | R$ 11.085 (mediana Glassdoor) | R$ 17.000–24.000+ | sigmoidal.ai; Glassdoor |
| DevOps/Cloud | R$ 5.000–7.000 | R$ 8.050 mediana | R$ 12.049 mediana | Glassdoor |
| Segurança | SOC Jr R$ 4–7k | R$ 8.542–14.148 | Pentester sênior R$ 15–25k; CISO R$ 24–30k+ | salario.com.br; IT Forum |

Confiança: média-alta. Glassdoor e salario.com.br agregam autodeclaração; tendem a **subestimar** sênior em empresas top-tier e remoto internacional.

### Saúde BR

- **SBIS:** certificação profissional cpTICS ativa; eventos CBIS e Hospitalar; programas proTICS. Alta confiança. Fonte: sbis.org.br/certificacoes/.
- **Fiocruz EAD:** 90+ cursos gratuitos via Campus Virtual; catálogo dinâmico por edital. Farmacoepi específico **não encontrado fixo**. Confiança: alta para existência do portal, baixa para curso específico.
- **DATASUS TabNet:** tutorial oficial ainda é o PDF de 2020 (DATASUS não atualizou em 2026). Alta confiança.

## TODOs não resolvidos

| TODO | Motivo | Próximo passo |
|---|---|---|
| CAHIMS/CPHIMS valor exato BR | HIMSS não publica preço regional único | Contato direto himss.org |
| cpTICS SBIS valor da inscrição | Edital periódico, valor varia | Monitorar sbis.org.br edital 2026 |
| N8N v2 features novas | Não buscado nesta rodada | Rodada 2: changelog github.com/n8n-io/n8n |
| voyage-law-2 preços | Não buscado nesta rodada | Rodada 2: docs.voyageai.com/pricing |
| Anthropic docs URLs (contextual retrieval, embeddings, building effective agents) | Não buscado nesta rodada | Rodada 2: anthropic.com/news + anthropic.com/engineering |
| TISS 4.01 versão vigente 2026 | Não buscado | Rodada 2: ANS site |
| CID-11 cronograma transição Brasil 2026 | Não buscado | Rodada 2: MS/OMS |
| CNES endpoint REST 2026 | Não buscado | Rodada 2: cnes.datasus.gov.br |
| Vigitel 2024 dados | Não buscado | Rodada 2: portal.saude.gov.br/vigitel |

## Ressalvas

- Preços USD→BRL convertidos a ~USD 1 = R$ 5,10 (abril/2026, aproximação).
- Salários sêniores em Glassdoor são **subestimados** vs realidade do mercado top-tier e remoto internacional. Usar como piso, não teto.
- HL7 FHIR preço é faixa (USD 500–800) por não haver tabela pública única; confiança média.
- cpTICS SBIS: valor exato não publicado em página permanente; inscrições por edital.

## Próxima rodada sugerida (Round 2)

1. Fechar TODOs de docs Anthropic (URLs oficiais) — bloco `08_ai_and_automation/`.
2. Fechar TODOs de saúde pública (Vigitel 2024, CID-11 transição, TISS versão) — bloco `07_health_data/`.
3. Fechar TODOs de infraestrutura (CNES REST, DataJud tabelas processuais) — bloco `09_legal_medical_integration/`.
4. Popular arquivos ainda inexistentes em `10_career_map/salary_market_signals/` e `10_career_map/certifications/` com os dados já coletados nesta rodada.
5. Validar norma ABNT para hash em prova digital + Res. CNJ 396/2021 (bloco `01_ti_foundations/concepts/`).
