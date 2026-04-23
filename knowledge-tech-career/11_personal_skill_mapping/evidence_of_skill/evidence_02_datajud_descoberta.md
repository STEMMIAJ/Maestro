---
titulo: Descobridor de processos multi-fonte (DJe+DataJud+PJe) com rate limit manual
tipo: evidencia
dominio: APIs
subtopico: consumir REST + threading + rate limit
nivel_demonstrado: 2
versao: 0.1
status: validada
ultima_atualizacao: 2026-04-23
fonte: /Users/jesus/Desktop/STEMMIA Dexter/src/jurisprudencia/descobrir_processos.py
---

## Descrição
Script mestre que consulta em paralelo (ThreadPoolExecutor) três fontes públicas: DJe TJMG (scraping HTML),
DataJud CNJ (API Elasticsearch dos tribunais — aliases tjmg/trf6/trt3) e PJe Consulta Pública. Reconcilia
contra lista local, valida CNJ por presença do nome do perito nas partes e grava consolidado JSON.
Usa `time.sleep(0.5)` como rate limit manual (não é backoff exponencial — dívida conhecida).

## Arquivo real
`/Users/jesus/Desktop/STEMMIA Dexter/src/jurisprudencia/descobrir_processos.py`

## Habilidade demonstrada
- `APIs.consumir REST` — 2 (DataJud Elasticsearch POST com query DSL)
- `Python.requests / httpx` — 2 (urllib.request com ssl.create_default_context)
- `Python.sintaxe básica` — 2 (ThreadPoolExecutor, as_completed)
- `Agentes.tool use` — 1 (consome chave DATAJUD_API_KEY via env)

## Trecho relevante
```python
DATAJUD_KEY = os.getenv("DATAJUD_API_KEY", "")
if not DATAJUD_KEY:
    raise RuntimeError(
        "DATAJUD_API_KEY não setada. Execute: "
        'export DATAJUD_API_KEY="<chave>" '
        "(ver https://datajud-wiki.cnj.jus.br/api-publica/acesso)"
    )
DATAJUD_ENDPOINTS = {
    "tjmg": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search",
    "trf6": "https://api-publica.datajud.cnj.jus.br/api_publica_trf6/_search",
    "trt3": "https://api-publica.datajud.cnj.jus.br/api_publica_trt3/_search",
}
```

Rate limit manual dentro do loop de validação:
```python
time.sleep(0.5)  # Rate limit
```

## Data
2026-04 (cruzamento Mutirão 125). Arquivo ativo via `hub.py`.

## Validação externa
**Média** — integrado ao `hub.py` e orquestrador noturno; chave DataJud real em uso. Referência CNJ Wiki citada no docstring.

## Limitações conhecidas
- `time.sleep(0.5)` não é backoff exponencial (padrão F1:216-222 do PYTHON-BASE). Quebra se API retornar 429.
- SSL context default — não valida pin de certificado.
- Sem teste unitário.
- Reconciliação com lista local assume nome do perito em MAIÚSCULAS (`PERITO_NOME = "NOLETO"`).
