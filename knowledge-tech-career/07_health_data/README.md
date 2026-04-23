---
titulo: Dados em Saude
bloco: 07_health_data
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 07 — Dados em Saúde

## Definição do domínio

Bloco de interseção entre medicina e dados: informática em saúde, epidemiologia e bioestatística aplicadas, datasets públicos brasileiros (DATASUS, TabNet, SIA, SIH, SIM, SINASC, CNES), analytics voltado à prática clínica e pericial, indicadores de qualidade e identificação de oportunidades profissionais para médicos em dados.

Objetivo: capacitar o médico a extrair, analisar e interpretar dados de saúde de forma autônoma — para epidemiologia local, auditoria, perícia, pesquisa e tomada de decisão clínica baseada em evidência de mundo real (RWE).

Aplicação direta na prática pericial: estimar prevalência de condição em determinada população, comparar achados do periciado com distribuição populacional, sustentar laudo com dado público referenciado.

## Subdomínios

- `health_informatics/` — prontuário eletrônico, padrões (HL7 FHIR, CID-10/11, CIAP, TUSS, SNOMED), interoperabilidade.
- `epidemiology_biostatistics/` — medidas de frequência (prevalência, incidência), risco (RR, OR, HR), testes diagnósticos (sensibilidade, especificidade, VPP, VPN), desenho de estudo.
- `healthcare_datasets/` — DATASUS, TabNet, SIA, SIH, SIM, SINASC, CNES, e-SUS, PNS, e datasets internacionais (MIMIC, UK Biobank).
- `analytics_for_medical_work/` — aplicação de SQL/Python a dados clínicos, geração de relatório pericial quantitativo, análise de séries de casos.
- `clinical_quality_indicators/` — indicadores AHRQ, OECD, ANS, protocolos de qualidade, auditoria clínica.
- `opportunities_for_physicians/` — papéis em healthtech, CMO técnico, consultoria em dados, pesquisa clínica, docência, perícia quantitativa.

## Perguntas que este bloco responde

1. Como extrair prevalência de CID específico por município no DATASUS?
2. Qual a diferença entre SIH e SIA e quando usar cada um?
3. Como calcular sensibilidade e especificidade de um teste com tabela 2x2?
4. O que é HL7 FHIR e por que importa para interoperabilidade?
5. Como usar dado populacional para sustentar nexo causal em laudo?
6. Quais indicadores a ANS exige de operadora e como auditá-los?
7. Que papéis existem no mercado para médico com competência em dados?
8. Como desenhar estudo observacional com dado secundário sem cometer viés clássico?

## Como coletar conteúdo para este bloco

- DATASUS (datasus.saude.gov.br) e TabNet como fonte primária.
- PubMed (MCP já configurado) para revisão de literatura.
- Livros: "Modern Epidemiology" (Rothman), "Clinical Prediction Models" (Steyerberg), "Bioestatística" (Pagano/Gauvreau).
- Documentação HL7 FHIR, CID-10/11 (OMS), TUSS (ANS).
- Guias da ANS, Ministério da Saúde, CFM.
- Projetos próprios: análise de casos periciais, séries de laudos.

## Critérios de qualidade das fontes

Seguir `00_governance/source_quality_rules.md`. Para saúde, priorizar fonte oficial (OMS, MS, ANS, CFM), revista indexada (MEDLINE, SciELO) e documentação padrão. Dataset sem dicionário de variáveis não entra. Registrar versão (CID-10 2016, FHIR R5).

## Exemplos de artefatos que podem entrar

- Guia prático de extração TabNet (passo a passo com screenshots).
- Dicionário do SIH-SUS traduzido e comentado.
- Template de análise pericial quantitativa (prevalência local + IC).
- Tabela comparativa CID-10 × CID-11 × CIAP-2 para códigos frequentes em perícia.
- Notebook de análise MIMIC-IV com pergunta clínica.
- Mapa de carreiras: médico → data scientist clínico, CMIO, consultor RWE.

## Interseções com outros blocos

- `05_security_and_governance` — dado de saúde é sensível (LGPD art. 11).
- `06_data_analytics` — ferramental (SQL, stats, dashboard) vem de lá.
- `08_ai_and_automation` — LLMs em saúde, RAG sobre literatura, extração de prontuário.
- `09_legal_medical_integration` — perícia quantitativa e nexo epidemiológico.
- `10_career_map` — oportunidades para médico em dados.
- `13_reports` — relatórios periciais com dados populacionais.
