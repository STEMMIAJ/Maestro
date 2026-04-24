# Parâmetros Oficiais da API Pública DataJud (CNJ)

Referência autoritativa para TODA integração DataJud no sistema Stemmia Forense.
**Cliente único:** `src/pje/datajud_client.py` — TODO código DEVE importar daqui.

## Autenticação

| Parâmetro | Valor |
|-----------|-------|
| Base URL | `https://api-publica.datajud.cnj.jus.br` |
| Endpoint | `POST /{tribunal_alias}/_search` |
| Header Auth | `Authorization: APIKey {DATAJUD_API_KEY}` |
| Content-Type | `application/json` |
| Env var | `DATAJUD_API_KEY` |

**IMPORTANTE:** O header usa `APIKey` (A maiúsculo, P maiúsculo, K maiúsculo). NÃO usar `ApiKey`.

## Tribunal Aliases

| Segmento CNJ (J.TT) | Alias | Tribunal |
|----------------------|-------|----------|
| `8.13` | `api_publica_tjmg` | Justiça Estadual MG |
| `5.06` | `api_publica_trf6` | Justiça Federal MG |
| `5.03` | `api_publica_trf3` | Justiça Federal (fallback) |
| `5.01` | `api_publica_trf1` | TRF 1ª Região |
| `5.03` | `api_publica_trt3` | TRT 3ª Região |

Formato CNJ: `NNNNNNN-DD.AAAA.J.TT.OOOO` — posições 14-16 (0-indexed 13-15) do número limpo codificam J (justiça) e TT (tribunal).

## Formato de Query (Elasticsearch DSL)

### Por número CNJ
```json
{
  "query": {"match": {"numeroProcesso": "50016159820258130074"}},
  "size": 1
}
```
**CNJ deve ser sem formatação** (só dígitos, 20 caracteres).

### Por assunto (perícia)
```json
{
  "size": 50,
  "query": {
    "bool": {
      "should": [
        {"match": {"assuntos.codigo": "9985"}},
        {"match_phrase": {"assuntos.nome": "Perícia"}}
      ],
      "minimum_should_match": 1,
      "filter": [{"range": {"dataAjuizamento": {"gte": "2020-01-01"}}}]
    }
  },
  "sort": [{"dataAjuizamento": {"order": "desc"}}]
}
```

## Formato de Resposta

```
response.hits.hits[*]._source
```

### Campos principais do `_source`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `numeroProcesso` | string | CNJ sem formatação |
| `classe` | `{nome, codigo}` | Classe processual |
| `orgaoJulgador` | `{nome}` | Vara/tribunal |
| `assuntos` | `[{nome, codigo}]` | Lista de assuntos |
| `movimentos` | `[{dataHora, nome, codigo, complementosTabelados}]` | Movimentações |
| `dataAjuizamento` | string ISO | Data de ajuizamento |
| `dataHoraUltimaAtualizacao` | string ISO | Última atualização |
| `grau` | string | Grau de jurisdição |

### Campos de movimentação
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `dataHora` | string ISO | `2025-03-01T00:00:00.000Z` |
| `nome` | string | Nome da movimentação |
| `codigo` | int | Código TPU |
| `complementosTabelados` | `[{nome, descricao}]` | Complementos |

## Rate Limits (auto-impostos)

| Parâmetro | Valor |
|-----------|-------|
| Delay entre requests batch | 300ms |
| Timeout por request | 15s |
| Max retries | 3 |
| Backoff | Exponencial: `2^tentativa` segundos |
| Delay jurisprudência | 2s entre tribunais |

## Detecção de Nomeação

- **Código TPU:** `60011` (nomeação de perito)
- **Texto:** movimento contendo "nomeação" ou "perito" no nome ou complementos
- **Assuntos perícia:** códigos `9985`, `10028`, `7771`

## Teste curl

```bash
export DATAJUD_API_KEY="cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
curl -s -X POST \
  "https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search" \
  -H "Content-Type: application/json" \
  -H "Authorization: APIKey ${DATAJUD_API_KEY}" \
  -d '{"query":{"match":{"numeroProcesso":"50016159820258130074"}},"size":1}' \
  | python3 -m json.tool
```

## Teste Python

```python
from src.pje.datajud_client import consultar_processo, detectar_nomeacao
r = consultar_processo("5001615-98.2025.8.13.0074")
print(f"Classe: {r['classe']['nome']}")
print(f"Órgão: {r['orgaoJulgador']['nome']}")
print(f"Movimentos: {len(r.get('movimentos', []))}")
print(f"Nomeação: {detectar_nomeacao(r.get('movimentos', []))}")
```

## Fontes oficiais
- Página principal: https://datajud-wiki.cnj.jus.br/api-publica/
- Acesso/API key: https://datajud-wiki.cnj.jus.br/api-publica/acesso/
- Endpoints: https://datajud-wiki.cnj.jus.br/api-publica/endpoints/
- Termo de uso: https://formularios.cnj.jus.br/wp-content/uploads/2023/05/Termos-de-uso-api-publica-V1.1.pdf
