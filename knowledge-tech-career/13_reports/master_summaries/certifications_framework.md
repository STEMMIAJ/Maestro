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
| CAHIMS / CPHIMS | HIMSS | Iniciante/Sênior | Alta (informática em saúde, EUA) | [TODO/RESEARCH: disponibilidade BR e valor] |

## Sinalização por nível de carreira

| Nível | Certificação faz sentido para |
|---|---|
| Júnior | Mostrar que estudou — Cloud Practitioner, Data Fundamentals, Security+ |
| Pleno | Fechar lacuna específica ou virar referência em nicho — Associate tracks, DP-203, FHIR |
| Sênior | Normalmente não precisa; exceção: consultoria, mudança de país, linguagem formal (CISSP, PMP) |

## Estimativas de custo

| Tipo | Valor aproximado |
|---|---|
| AWS Associate | [TODO/RESEARCH: preço atual em BRL com conversão USD] |
| Microsoft Fundamentals | [TODO/RESEARCH] |
| Google Coursera specializations | ~R$ 200-250/mês Coursera Plus |
| CompTIA Security+ | [TODO/RESEARCH] |
| CISSP | [TODO/RESEARCH] |
| HL7 FHIR | [TODO/RESEARCH] |

## Armadilhas

- **Empilhamento sem projeto** — 5 certificados sem um repositório público = currículo suspeito.
- **Pirâmide errada** — pular fundamento para ir direto em specialty.
- **Validade** — AWS/Azure expiram em 2–3 anos. Planejar renovação.
- **Certificação do empregador que você não quer** — aceitar certificação que a empresa paga e depois não serve para a trilha pessoal.

## Ver também

- `junior_pleno_senior_framework.md` — certificação vs. nível real.
- `health_data_career_paths.md` — certificações específicas de trilha.
