---
id: python_base_sistemas_completos
title: PYTHON-BASE — Inventário de 08-SISTEMAS-COMPLETOS
status: EXECUTADO
bloco: 02_programming/python
origem: /Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/
total_subpastas: 11
tipos:
  - sistemas_producao
  - pipelines
  - teoria_arquitetural
  - exemplos_didaticos
data_criacao: 2026-04-23
tags: [python, sistemas, arquitetura, pje, tjmg, monitor]
---

# PYTHON-BASE — Inventário de `08-SISTEMAS-COMPLETOS/`

Onze subpastas. Três tipos: sistemas em produção, pipelines reutilizáveis, material teórico (arquitetura/camadas/deploy). 68 Markdown + 2092 arquivos Python no total.

## Sistemas em produção

### `distancias-gv/` — status: completo
Calcula distância rodoviária das 1621 localidades TJMG até Governador Valadares. Reusa parse do scraper TJMG, geocoding via Nominatim com cache, distância via OSRM + fallback Google + haversine. Saída em CSV, JSON e HTML ordenada.
- **Arquivo principal:** `distancias_gv.py`
- **Caso real documentado:** falha SSL LibreSSL → fallback subprocess curl (em REGISTRO.md).
- Link: [./python-base/08-SISTEMAS-COMPLETOS/distancias-gv/](./python-base/08-SISTEMAS-COMPLETOS/distancias-gv/)

### `guia-tjmg-scraper/` — status: completo
Scraper GET puro (sem JSF/AJAX) das 1621 localidades do Guia Judiciário TJMG. Playwright headless + 16 pages em paralelo, retry 2x, skip de PDFs já baixados. Gera manifesto JSON e log de falhas.
- **Arquivo principal:** `scraper.py` + `fix_colisoes.py` (correção de PDFs homônimos)
- **Caso real documentado:** colisão de slugs em distritos homônimos → filename com código.
- Link: [./python-base/08-SISTEMAS-COMPLETOS/guia-tjmg-scraper/](./python-base/08-SISTEMAS-COMPLETOS/guia-tjmg-scraper/)

### `guia-tjmg-classificador/` — status: completo
Classifica as 1621 localidades em comarca-sede, município integrante ou distrito. Gera `data/localidades.json` + `data/comarcas.json` + relatório. Inclui consulta por cidade (`minha_area.py`) e glossário jurídico.
- **Arquivo principal:** `classificar.py`
- Link: [./python-base/08-SISTEMAS-COMPLETOS/guia-tjmg-classificador/](./python-base/08-SISTEMAS-COMPLETOS/guia-tjmg-classificador/)

### `monitor-processos-novo-2026-04-22/` — status: parcial
Sistema autônomo de descoberta/notificação de nomeações, intimações e movimentações onde Dr. Jesus figura como perito. Arquitetura em sprints: Sprint 1 (fundação) e Sprint 2 (DJEN) prontos; Sprint 3 (AJG-CJF, AJ-JT, AJ-TJMG com Playwright + Keychain), Sprint 4 (launchd produção + circuit breaker) e Sprint 5 (Tier 2 + bot interativo) pendentes.
- **Arquivo principal:** `02-scripts/monitor/fontes/djen.py` + scheduler
- **Leitura obrigatória:** `00-plano/PLANO-ACAO.md`, `04-docs/INSTALACAO.md`, `04-docs/TROUBLESHOOTING.md`
- Link: [./python-base/08-SISTEMAS-COMPLETOS/monitor-processos-novo-2026-04-22/](./python-base/08-SISTEMAS-COMPLETOS/monitor-processos-novo-2026-04-22/)

## Pipelines reutilizáveis

### `conversation_ingestion/` — status: completo
Pipeline ETL para ingerir conversas externas (Perplexity, ChatGPT, Claude, Gemini) e transformar em memória operacional. Etapas: `ingest_conversation.py` → `chunk_conversation.py` → `extract_action_items.py` → `generate_memory_files.py` → `generate_session_checkpoint.py` + `integrate_llm.py`. Testes em `test_pipeline.py` + `tests/`.
- **Arquivo principal:** `ingest_conversation.py`
- Link: [./python-base/08-SISTEMAS-COMPLETOS/conversation_ingestion/](./python-base/08-SISTEMAS-COMPLETOS/conversation_ingestion/)

## Utilitários

### `perplexity-tempo/` — status: completo
Calcula tempo gasto ditando versus esperando resposta em cada mensagem de thread da Perplexity. Usa endpoint privado `rest/thread/{uuid}` com `entry_created_datetime` vs `entry_updated_datetime`. Útil para calibrar carga cognitiva e horário de trabalho.
- **Arquivo principal:** `perplexity_tempo.py` + `capturar_thread.js`
- Link: [./python-base/08-SISTEMAS-COMPLETOS/perplexity-tempo/](./python-base/08-SISTEMAS-COMPLETOS/perplexity-tempo/)

### `taiobeiras-status/` — status: parcial
Utilitário de status para comarca Taiobeiras. Sem README; só `taiobeiras_status.py`. Função e estado não documentados — marcar como dívida técnica.
- **Arquivo principal:** `taiobeiras_status.py`
- Link: [./python-base/08-SISTEMAS-COMPLETOS/taiobeiras-status/](./python-base/08-SISTEMAS-COMPLETOS/taiobeiras-status/)

## Exemplos didáticos

### `exemplos-reais/` — status: completo
Três sistemas didáticos ponta a ponta:
- `exemplo-1-sistema-clinica/` — FastAPI + SQLModel + Typer CLI (gestão de pacientes)
- `exemplo-2-monitor-pericial/` — DDD com adapters (DataJud, DJEN, Telegram, AJG/CJF, AJ-TJMG) + ports + repositório JSON
- `exemplo-3-bot-telegram/` — bot stemmia com auth, handlers de processos, status
- Link: [./python-base/08-SISTEMAS-COMPLETOS/exemplos-reais/](./python-base/08-SISTEMAS-COMPLETOS/exemplos-reais/)

## Teoria arquitetural (Markdown)

### `arquitetura/` — status: completo
- 6 arquivos: clean-architecture, event-driven, hexagonal, microservicos-python, monolito-modular, mvc
- Consultar antes de decidir topologia
- Link: [./python-base/08-SISTEMAS-COMPLETOS/arquitetura/](./python-base/08-SISTEMAS-COMPLETOS/arquitetura/)

### `camadas/` — status: completo
- 7 arquivos: api-fastapi, auth-oauth-jwt, cli-typer, db-sqlmodel, frontend-htmx-jinja, observabilidade-logs-prometheus, workers-rq-celery
- Cada camada técnica com padrão recomendado
- Link: [./python-base/08-SISTEMAS-COMPLETOS/camadas/](./python-base/08-SISTEMAS-COMPLETOS/camadas/)

### `deploy/` — status: completo
- 6 arquivos: cloud-fly-railway, docker-compose, local-venv, mac-launchd, vps-systemd-linux, windows-services
- Cada opção com quando usar, quando evitar
- Link: [./python-base/08-SISTEMAS-COMPLETOS/deploy/](./python-base/08-SISTEMAS-COMPLETOS/deploy/)

## Lacunas identificadas

- `taiobeiras-status/`: sem README, sem requirements, função pouco clara.
- `monitor-processos-novo-2026-04-22/`: sprints 3–5 pendentes.
- Integração entre `distancias-gv` e `guia-tjmg-classificador` (mesma fonte, consumidores separados) — oportunidade de módulo compartilhado.
