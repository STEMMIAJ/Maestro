---
titulo: Dados e Analytics
bloco: 06_data_analytics
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 06 — Dados e Analytics

## Definição do domínio

Este bloco cobre a cadeia que transforma dado bruto em decisão: estatística descritiva e inferencial, SQL, dashboards/BI, fundamentos de engenharia de dados (ingestão, transformação, armazenamento), experimentação e projetos de dados de ponta a ponta.

O foco é prática: consultar um banco sem depender de terceiros, montar um dashboard que responda pergunta real, desenhar experimento que não gere conclusão espúria, e entregar análise reprodutível (notebook versionado, pipeline idempotente).

Aplicações imediatas: análise de produtividade pericial, série histórica de laudos, comparação entre comarcas, indicadores clínicos agregados, dashboards operacionais do sistema.

## Subdomínios

- `statistics_foundations/` — descritiva, distribuições, intervalo de confiança, teste de hipótese, correlação vs. causalidade.
- `sql/` — SELECT, JOIN, GROUP BY, window functions, CTE, performance de query, indexação.
- `dashboards_bi/` — Metabase, Superset, Power BI, princípios de visualização (Tufte, Cairo).
- `data_engineering_basics/` — ETL/ELT, schema, formatos (CSV, Parquet, JSONL), orquestração (Airflow, Dagster), dbt.
- `experimentation/` — A/B test, poder estatístico, viés, design de experimento, observacional vs. experimental.
- `data_projects/` — portfólio reprodutível: notebook + dados + README + conclusão.

## Perguntas que este bloco responde

1. Quando usar média, mediana ou moda?
2. Como escrever SQL que não estoura o banco em produção?
3. O que é p-valor e o que ele não é?
4. Qual a diferença entre ETL e ELT e quando cada um cabe?
5. Como montar dashboard que responde pergunta em vez de enfeitar?
6. O que é viés de sobrevivência e como detectar?
7. Como tornar uma análise reprodutível por terceiro?
8. Quando Parquet ganha de CSV?

## Como coletar conteúdo para este bloco

- Livros: "Statistics Done Wrong" (Reinhart), "SQL for Data Analysis" (Tanimura), "The Visual Display of Quantitative Information" (Tufte), "Storytelling with Data" (Knaflic).
- Documentação oficial PostgreSQL, DuckDB, dbt, Metabase.
- Datasets públicos para prática (DATASUS, IBGE, Kaggle).
- Cursos: Data Engineering Zoomcamp, CS109 Harvard.
- Projetos próprios: análise de laudos, produtividade, comparativo DJEN.

## Critérios de qualidade das fontes

Seguir `00_governance/source_quality_rules.md`. Em estatística, preferir livros-texto e papers revisados; descartar blog que confunde correlação com causalidade. Em SQL/engenharia, registrar versão do motor. Dataset sem dicionário não entra.

## Exemplos de artefatos que podem entrar

- Cheatsheet SQL (janelas, CTE recursiva, upsert).
- Template de notebook reprodutível (dados + código + conclusão + limitações).
- Dashboard Metabase com KPIs periciais.
- Guia de viés em amostra pericial (não-aleatória por natureza).
- Pipeline dbt de ingestão DataJud → marts → dashboard.
- Relatório de análise: produção mensal por comarca, com IC.

## Interseções com outros blocos

- `02_programming` — Python/pandas é ferramenta base.
- `04_systems_architecture` — pipeline é arquitetura.
- `05_security_and_governance` — dado sensível exige anonimização.
- `07_health_data` — aplicação direta em epidemiologia e indicadores clínicos.
- `08_ai_and_automation` — RAG e fine-tune consomem dados estruturados.
- `13_reports` — entregáveis finais moram lá, construídos aqui.
