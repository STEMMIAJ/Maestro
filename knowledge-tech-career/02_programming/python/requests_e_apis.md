---
titulo: Requests e APIs em Python
bloco: 02_programming
tipo: tutorial
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 7
---

# Requests e APIs

## Conceito
API REST = endereço HTTP que devolve JSON. Chama-se por `GET` (ler), `POST` (criar), `PUT`/`PATCH` (atualizar), `DELETE` (apagar).

## `requests` — lib padrão
Instalar: `pip install requests`.

```python
import requests

r = requests.get("https://api.exemplo.com/processos")
print(r.status_code)      # 200 ok, 401 sem autorização, 429 rate limit, 500 erro servidor
print(r.json())           # dict/list Python
```

## Timeout — OBRIGATÓRIO
Sem timeout, se o servidor travar, seu script trava para sempre.

```python
r = requests.get(url, timeout=30)   # 30 s no total
# ou
r = requests.get(url, timeout=(5, 30))  # 5 s conectar, 30 s ler
```

## Headers
```python
headers = {
    "Authorization": "ApiKey CHAVE_AQUI",   # ref: nunca hardcode, ler de env
    "Content-Type": "application/json",
    "User-Agent": "stemmia-forense/1.0",
}
r = requests.get(url, headers=headers, timeout=30)
```

## POST com JSON
```python
payload = {"numeroProcesso": "0001234-56.2025.8.13.0024"}
r = requests.post(url, json=payload, headers=headers, timeout=30)
```

`json=...` serializa automático e seta `Content-Type: application/json`.

## Retry com backoff exponencial
Rate limit (HTTP 429) e erro transitório (500/502/503) exigem **esperar e tentar de novo**, dobrando o tempo.

```python
import time, requests

def buscar_com_retry(url, headers, max_tentativas=5):
    for tent in range(max_tentativas):
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504):
            espera = 2 ** tent          # 1, 2, 4, 8, 16 s
            time.sleep(espera)
            continue
        r.raise_for_status()            # erro definitivo — levanta exceção
    raise RuntimeError(f"falhou apos {max_tentativas} tentativas")
```

`2 ** tent` é exponencial. Protege a API de martelada e evita ser banido.

## Exemplo real — DataJud (CNJ)
API pública do CNJ indexa processos por tribunal. Endpoint usa alias (ex.: `api_publica_tjmg`).

```python
import os, requests

API_KEY = os.environ["DATAJUD_API_KEY"]   # nunca hardcode
URL = "https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search"

headers = {
    "Authorization": f"ApiKey {API_KEY}",
    "Content-Type": "application/json",
}
query = {
    "query": {
        "match": {"numeroProcesso": "00012345620258130024"}
    },
    "size": 10,
}

r = requests.post(URL, json=query, headers=headers, timeout=30)
r.raise_for_status()
for hit in r.json()["hits"]["hits"]:
    print(hit["_source"]["classe"]["nome"])
```

Sobre DataJud: consultar antes `~/Desktop/STEMMIA Dexter/DOCS/datajud/DATAJUD-GUIA.md` (guia oficial do sistema).

## Segurança
- Chave em variável de ambiente (`os.environ`), nunca no código.
- `.env` sempre no `.gitignore`.
- `r.raise_for_status()` após chamada — falha explícita é melhor que silenciosa.

## Armadilhas
- `r.text` vs `r.json()` — `text` é string crua, `json()` é objeto Python.
- `r.json()` levanta `ValueError` se resposta não for JSON — verificar `Content-Type` antes se duvidoso.
- Sem timeout → script trava. Sem retry → falha com qualquer soluço de rede.
