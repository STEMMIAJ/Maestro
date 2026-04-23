---
id: python_base_templates
title: PYTHON-BASE — Inventário de 06-TEMPLATES
status: EXECUTADO
bloco: 02_programming/python
origem: /Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/06-TEMPLATES/
total_templates: 8
data_criacao: 2026-04-23
regra_uso: copiar template existente antes de escrever do zero
tags: [python, templates, skeleton, starter]
---

# PYTHON-BASE — Inventário de `06-TEMPLATES/`

Oito arquivos `.py` prontos para copiar e adaptar. Cada um cross-platform (Mac + Windows + Linux). **Regra:** antes de escrever qualquer script novo, procurar aqui primeiro.

## Templates disponíveis

### `script-cli-typer-com-logging.py`
- **Função:** esqueleto de CLI completo com Typer + logging JSON + config via pydantic-settings.
- **Quando usar:** qualquer script com argumentos de linha de comando e logs estruturados.
- **Deps:** `typer[all]`, `pydantic-settings`, `structlog`.
- Link: [./python-base/06-TEMPLATES/script-cli-typer-com-logging.py](./python-base/06-TEMPLATES/script-cli-typer-com-logging.py)

### `async-httpx-retry.py`
- **Função:** HTTP async paralelo com retry exponencial, rate-limit e logging.
- **Quando usar:** consumo de qualquer API (DataJud, DJEN, Google Maps, OSRM) com múltiplas requisições.
- **Deps:** `httpx`, `tenacity`.
- Link: [./python-base/06-TEMPLATES/async-httpx-retry.py](./python-base/06-TEMPLATES/async-httpx-retry.py)

### `telegram-alerta.py`
- **Função:** envia mensagem Telegram com retry e suporte a anexo PDF.
- **Quando usar:** qualquer notificação automática (monitor de processos, alertas de falha, relatórios).
- **Deps:** `httpx`, `tenacity`. Requer `TELEGRAM_TOKEN` em env.
- Link: [./python-base/06-TEMPLATES/telegram-alerta.py](./python-base/06-TEMPLATES/telegram-alerta.py)

### `webhook-fastapi-minimo.py`
- **Função:** webhook FastAPI com validação HMAC + pydantic.
- **Quando usar:** receber notificações externas (N8N, GitHub, serviço terceiro) com verificação de assinatura.
- **Deps:** `fastapi[standard]`, `uvicorn`, `pydantic`.
- Link: [./python-base/06-TEMPLATES/webhook-fastapi-minimo.py](./python-base/06-TEMPLATES/webhook-fastapi-minimo.py)

### `etl-csv-sqlite.py`
- **Função:** pipeline CSV → validação pydantic → gravação SQLite via SQLModel.
- **Quando usar:** ingerir planilha externa (pacientes, localidades, tabelas SUS) em banco local.
- **Deps:** `sqlmodel`, `pydantic`.
- Link: [./python-base/06-TEMPLATES/etl-csv-sqlite.py](./python-base/06-TEMPLATES/etl-csv-sqlite.py)

### `pdf-extract-texto.py`
- **Função:** extrai texto corrido (pypdf) e tabelas (pdfplumber) de PDF.
- **Quando usar:** extração de autos PJe baixados, laudos antigos, petições.
- **Deps:** `pypdf`, `pdfplumber`.
- Link: [./python-base/06-TEMPLATES/pdf-extract-texto.py](./python-base/06-TEMPLATES/pdf-extract-texto.py)

### `mac-windows-path-helper.py`
- **Função:** helper para traduzir caminhos Mac ↔ Windows (setup Parallels).
- **Quando usar:** qualquer script que precise abrir arquivo em ambos os hosts (PJe Windows, perícia Mac).
- **Deps:** só stdlib (`pathlib`, `re`, `sys`).
- Link: [./python-base/06-TEMPLATES/mac-windows-path-helper.py](./python-base/06-TEMPLATES/mac-windows-path-helper.py)

### `teste_indexer_dummy.py`
- **Função:** script dummy mínimo para testar o indexador da própria PYTHON-BASE.
- **Quando usar:** validar que novos arquivos são detectados pelo indexador.
- **Deps:** `requests`, `selenium` (apenas para testar imports).
- Link: [./python-base/06-TEMPLATES/teste_indexer_dummy.py](./python-base/06-TEMPLATES/teste_indexer_dummy.py)

## Fluxo de adaptação

1. Copiar template relevante para diretório destino (`14_automation/scripts/` ou similar).
2. Renomear conforme caso de uso.
3. Manter cabeçalho docstring com `"""..."""` + seção `Uso`.
4. Ajustar deps e validar com `uv pip install`.
5. Registrar em `TASKS_MASTER.md` como entrega.

## Lacunas

- Falta template para **Playwright persistent context** (padrão PJe). Candidato a criar — usar `08-SISTEMAS-COMPLETOS/guia-tjmg-scraper/scraper.py` como base.
- Falta template para **subprocess seguro** (apesar de `01-FUNDAMENTOS/subprocess-seguro.md` existir).
- Falta template para **launchd plist** (apenas doc em `08-SISTEMAS-COMPLETOS/deploy/mac-launchd.md`).
