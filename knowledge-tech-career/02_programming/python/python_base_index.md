---
id: python_base_index
title: PYTHON-BASE — Índice consolidado
status: EXECUTADO
bloco: 02_programming/python
origem: /Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/
symlink_relativo: ./python-base/
data_criacao: 2026-04-23
atualizacao: 2026-04-23
responsavel: agente R3-PythonBaseIntegrator
fonte_primaria: ./python-base/_INDICE-CONSULTAVEL.md
fonte_secundaria: ./python-base/README.md
tamanho_mb: 179
relacionado:
  - KTC-021
  - KTC-027
  - KTC-141
tags: [python, automacao, base-conhecimento, pje, playwright]
---

# PYTHON-BASE — Índice consolidado

Base de conhecimento Python aplicada à automação pericial (PJe, TJMG, CJF, DJEN, Telegram). 179 MB, 11 subpastas numeradas, 90 falhas catalogadas em JSON, 8 templates prontos, 11 sistemas completos.

**Quando consultar:** antes de gerar, revisar ou corrigir qualquer script Python de automação (browser, CDP, scraping, ETL, integração). Regra vinculante no `CLAUDE.md` global do Dr. Jesus.

## Estrutura por subpasta

### `00-PLANO/` — plano de crescimento
- Arquivo único: `PLANO-DE-ACAO.md`
- Define fases 1–5 de maturação da base
- Consultar: quando expandir escopo ou registrar nova fase
- Link: [./python-base/00-PLANO/](./python-base/00-PLANO/)

### `01-FUNDAMENTOS/` — stdlib e padrões centrais
- 11 arquivos Markdown: asyncio, cli-argparse-typer, data-pulling, errors-exceptions, integracoes, logging-estruturado, pathlib-mac-windows, retry-tenacity, revisao-codigo, subprocess-seguro, typing
- Consultar: antes de usar qualquer biblioteca padrão do Python em automação
- Link: [./python-base/01-FUNDAMENTOS/](./python-base/01-FUNDAMENTOS/)

### `02-AUTOMACAO-NAVEGADOR/` — browser automation
- 4 subpastas: `playwright/`, `selenium/`, `requests-httpx/`, `patterns/`
- Cobertura: instalação, seletores, sessão, download, anti-bot
- Consultar: qualquer script que abra navegador ou chame HTTP
- Link: [./python-base/02-AUTOMACAO-NAVEGADOR/](./python-base/02-AUTOMACAO-NAVEGADOR/)

### `03-FALHAS-SOLUCOES/` — BD de 90 falhas catalogadas
- `db/falhas.json` (1262 linhas, 90 entradas) + `db/falhas.schema.json`
- `casos-reais/REGISTRO.md` (falhas não destiladas ainda)
- `INDEX.md` com distribuição por tecnologia e categoria
- Distribuição: playwright 56, selenium 20, cdp 10, pje específicos 25, requests/asyncio/subprocess/geral 4
- Consultar: **sempre** antes de gerar código. Citar IDs no código gerado (`# ref: PW-012`)
- Ver também: [python_base_falhas_top_20.md](./python_base_falhas_top_20.md)
- Link: [./python-base/03-FALHAS-SOLUCOES/](./python-base/03-FALHAS-SOLUCOES/)

### `04-NLP-PARA-PYTHON/` — do ditado ao código
- 5 arquivos: 1-como-ditar, 2-do-ditado-ao-plano, 3-do-plano-ao-codigo, 4-exemplos-reais, 5-skills-hooks-claude
- Consultar: quando usuário (autista, TDAH, memória comprometida) dita requisito e precisa virar código sem perda semântica
- Link: [./python-base/04-NLP-PARA-PYTHON/](./python-base/04-NLP-PARA-PYTHON/)

### `05-FONTES-OFICIAIS/` — whitelist/blacklist de docs
- `WHITELIST.md` — fontes aceitas (docs.python.org, playwright.dev, etc.)
- `BLACKLIST.md` — fontes rejeitadas (blogs desatualizados, respostas velhas de Stack)
- Consultar: antes de citar URL como referência em código ou documentação
- Link: [./python-base/05-FONTES-OFICIAIS/](./python-base/05-FONTES-OFICIAIS/)

### `06-TEMPLATES/` — 8 templates Python prontos
- async-httpx-retry, etl-csv-sqlite, mac-windows-path-helper, pdf-extract-texto, script-cli-typer-com-logging, telegram-alerta, webhook-fastapi-minimo, teste_indexer_dummy
- Consultar: primeiro recurso antes de escrever script do zero. Copiar template, adaptar
- Ver também: [python_base_templates.md](./python_base_templates.md)
- Link: [./python-base/06-TEMPLATES/](./python-base/06-TEMPLATES/)

### `07-PESQUISA-AGENTES/` — relatórios de 7 times
- 7 subpastas: auditoria-pje, browser, fontes, manual, nlp, python, sistemas
- 14 arquivos Markdown de pesquisa consolidada (RELATORIO.md, CASOS-PJE.md, etc.)
- Consultar: quando precisar justificar decisão arquitetural com evidência
- Link: [./python-base/07-PESQUISA-AGENTES/](./python-base/07-PESQUISA-AGENTES/)

### `08-SISTEMAS-COMPLETOS/` — 11 sistemas ponta a ponta
- arquitetura (teoria), camadas (teoria), deploy (teoria)
- conversation_ingestion (pipeline), distancias-gv (produção), guia-tjmg-classificador (produção), guia-tjmg-scraper (produção), monitor-processos-novo-2026-04-22 (sprints 1–2 completos), perplexity-tempo (utilitário), taiobeiras-status (utilitário), exemplos-reais (3 exemplos didáticos)
- 68 Markdown + 2092 arquivos Python
- Consultar: antes de arquitetar sistema novo. Ver se padrão já existe
- Ver também: [python_base_sistemas_completos.md](./python_base_sistemas_completos.md)
- Link: [./python-base/08-SISTEMAS-COMPLETOS/](./python-base/08-SISTEMAS-COMPLETOS/)

### `09-MANUAL-LEIGO/` — Python para não-programador
- 5 subpastas: fases-projeto, glossario, ia-como-copiloto, o-que-e-python, python-vs-outras
- 20 arquivos Markdown em linguagem acessível
- Consultar: quando usuário pede explicação de conceito, não código
- Link: [./python-base/09-MANUAL-LEIGO/](./python-base/09-MANUAL-LEIGO/)

### `99-LOGs/` — logs do indexador
- backup-2026-04-23, indexer-20260420.log, inicio-times.log, launchd-stderr.log, launchd-stdout.log
- Consultar: debug do próprio indexador da base
- Link: [./python-base/99-LOGS/](./python-base/99-LOGS/)

## Fluxo de consulta padrão (obrigatório antes de codar)

1. `grep` no `_INDICE-CONSULTAVEL.md` para descobrir se padrão já existe
2. `jq` sobre `03-FALHAS-SOLUCOES/db/falhas.json` filtrando tecnologia envolvida
3. Buscar template em `06-TEMPLATES/`
4. Verificar exemplo real em `08-SISTEMAS-COMPLETOS/`
5. Se falha nova ocorrer → registrar em `03-FALHAS-SOLUCOES/casos-reais/REGISTRO.md`

Ver [como_consultar_python_base.md](./como_consultar_python_base.md) para comandos prontos.

## Referências cruzadas

- TASKS_MASTER.md: KTC-021, KTC-027, KTC-141, KTC-180..KTC-183 (novas)
- Skill Claude: `/python-base` (registrada no CLAUDE.md global)
- Symlink reverso: `~/Desktop/STEMMIA Dexter/PYTHON-BASE/` (fonte real)
