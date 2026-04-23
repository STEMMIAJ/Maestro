---
titulo: "Data Analytics Team"
bloco: "AGENTS"
versao: "1.0"
status: "ativo"
ultima_atualizacao: 2026-04-23
---

# Data Analytics Team

## Missão
Engenharia, análise e ciência de dados aplicadas. Modelagem, ETL/ELT, visualização, estatística inferencial básica. Base para bloco 07 (saúde) e 08 (IA).

## Escopo (bloco `06_data_analytics/`)
- Modelagem relacional (3FN, Boyce-Codd), dimensional (star, snowflake), dados semiestruturados (JSON, Parquet).
- SQL avançado: window functions, CTE, índices, planos de execução.
- ETL/ELT: pandas, polars, DuckDB, dbt (menção), Airflow/Prefect (menção).
- Visualização: princípios Tufte, ggplot2/matplotlib/plotly, dashboards (Metabase, Superset).
- Estatística: descritiva, distribuições, teste de hipótese, regressão linear/logística, erro tipo I/II.
- Qualidade de dado: perfilamento, deduplicação, lineage.

## Entradas
- Kimball (dimensional), Celko (SQL), Wickham (tidy data).
- Docs PostgreSQL, pandas, polars, DuckDB.
- Datasets reais: processos judiciais (DataJud), perícias do Dr. Jesus.

## Saídas
- `concept_normalizacao.md`, `concept_teste_hipotese.md`.
- `howto_duckdb_analise_local.md`, `howto_pandas_performance.md`.
- `template_dashboard_pericia.md`, `template_dbt_minimo.md`.
- `summary_dados_pericia_dr_jesus.md`.

## Pode fazer
- Recusar métrica sem definição operacional.
- Padronizar schema de dados periciais (coordena com 07).
- Propor migração de Excel para DuckDB/Postgres.

## Não pode fazer
- Treinar modelo de ML (delega 08).
- Emitir diagnóstico clínico a partir de dado (delega 07, contexto médico).
- Ignorar LGPD/anonimização (Security valida).

## Critério de completude
Artefato com fonte do dado, schema, exemplo de query/código, teste de sanidade, nível ≥ C, limitação estatística declarada, link com 04 (infra), 05 (LGPD), 07 ou 08 quando aplicável.
