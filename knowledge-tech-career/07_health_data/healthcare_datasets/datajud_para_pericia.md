---
titulo: "DATAJUD para perícia — API pública CNJ, aliases, rate limit"
bloco: "07_health_data/healthcare_datasets"
tipo: "pratica"
nivel: "intermediario"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "maduro"
tempo_leitura_min: 10
---

# DATAJUD — API pública do CNJ para perícia

Repositório unificado de dados processuais dos tribunais brasileiros, mantido pelo CNJ. API REST pública para consulta estruturada de processos e movimentações. Essencial para monitorar nomeações, prazos e publicações do perito.

## Visão geral

- **Mantenedor**: CNJ (Conselho Nacional de Justiça).
- **Resolução CNJ 331/2020** institui; Resolução 360/2020 regulamenta API pública.
- **Formato**: Elasticsearch REST com autenticação por chave (header `Authorization: APIKey <chave>`).
- **Chave pública**: fornecida pelo CNJ, rotacionada ocasionalmente — conferir `~/Desktop/STEMMIA Dexter/DOCS/datajud/02-oficial-cnj/wiki/api-publica__acesso.md`.
- **Formatos aceitos**: JSON (POST `_search`).

## Endpoint

```
https://api-publica.datajud.cnj.jus.br/api_publica_{alias}/_search
```

Onde `{alias}` identifica o tribunal. Tabela completa em `~/Desktop/STEMMIA Dexter/DOCS/datajud/INDICES-ELASTICSEARCH.md`. Exemplos:

| Tribunal | Alias |
|---|---|
| TJMG | `tjmg` |
| TJSP | `tjsp` |
| TJRJ | `tjrj` |
| TST | `tst` |
| STJ | `stj` |
| STF | `stf` |
| TRF1 | `trf1` |
| TRT3 (MG) | `trt3` |

## Rate limit

- Limite oficial: **120 requisições/minuto por chave**.
- Ultrapassar → HTTP 429. **Obrigatório backoff exponencial** (padrão interno F1:216-222).
- Evitar rajadas; usar fila e throttling (`time.sleep(0.5)` entre chamadas basta para volumes pequenos).

## Campos úteis

Documento retornado tem `_source` com:

- `numeroProcesso` — CNJ 20 dígitos (com pontuação).
- `classe` — código + nome.
- `assuntos[]` — códigos CNJ de assunto.
- `dataAjuizamento`, `dataHoraUltimaAtualizacao`.
- `orgaoJulgador` — vara.
- `movimentos[]` — array de movimentações (código + nome + dataHora + complementos).
- `sistema` — PJe, eProc, Projudi etc.
- `tribunal` — sigla.
- `valorCausa`, `grau`, `nivelSigilo`.

## Exemplo — buscar processo pelo CNJ

```python
import requests

URL = "https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search"
HEADERS = {"Authorization": "APIKey " + CHAVE, "Content-Type": "application/json"}

body = {
  "query": {"match": {"numeroProcesso": "50001234520248130024"}}
}
r = requests.post(URL, json=body, headers=HEADERS, timeout=30)
r.raise_for_status()
hits = r.json()["hits"]["hits"]
```

## Exemplo — paginação com `search_after`

Datajud não suporta `from` acima de 10.000. Usar `search_after`:

```python
body = {
  "size": 1000,
  "query": {"range": {"dataAjuizamento": {"gte": "2024-01-01"}}},
  "sort": [{"@timestamp": "asc"}, {"_id": "asc"}]
}
after = None
while True:
    if after: body["search_after"] = after
    r = requests.post(URL, json=body, headers=HEADERS)
    r.raise_for_status()
    hits = r.json()["hits"]["hits"]
    if not hits: break
    yield from hits
    after = hits[-1]["sort"]
    time.sleep(0.5)
```

## Queries prontas (exemplos)

Arquivo local: `~/Desktop/STEMMIA Dexter/DOCS/datajud/EXEMPLOS-QUERY.md`.

- Processos em que "JESUS" aparece como perito: filtrar por `movimentos.complementosTabelados` código 51 (nomeação).
- Processos de uma classe específica: `{"term":{"classe.codigo": 436}}` (Procedimento do Juizado).
- Publicações na última semana: `{"range":{"movimentos.dataHora":{"gte":"now-7d/d"}}}`.

## Aplicações periciais

1. **Monitor de nomeações**: buscar diariamente movimentos código 51 (nomeação de perito) filtrando por nome nos complementos.
2. **Controle de prazos**: buscar próximas audiências (movimento 970 — designação) em processos da carteira.
3. **Estatística da prática**: extrair todos os processos onde o perito foi nomeado nos últimos 5 anos → dashboard com classe, valor, tribunal, tempo médio.
4. **Conferência de laudo publicado**: movimento 246 (juntada de laudo) + 14 dias → prazo de impugnação.
5. **Estatística de impugnação**: quantas perícias tiveram impugnação após laudo.

## Integração com monitor

- Script `monitorar_movimentacao.py` em `~/Desktop/STEMMIA Dexter/src/automacoes/`.
- Cruzar com DJEN (Diário da Justiça Eletrônico Nacional) e Comunica PJe para redundância.
- Guardar em `pericia.db` (SQLite) e acionar Telegram quando nomeação detectada.

## Limitações

1. **Latência**: tribunais enviam periodicamente; atraso de horas a dias.
2. **Não substitui sistema oficial** do tribunal para peticionar; só para consulta.
3. **Nível de sigilo**: processos em sigilo não retornam (ou retornam mascarados).
4. **Qualidade dos dados**: depende do tribunal. Alguns têm movimentos genéricos sem código padronizado.
5. **Chave pública** tem cota global — uso abusivo pode levar à revogação.

## Checklist antes de usar

- [ ] Chave atual verificada na wiki espelhada?
- [ ] Alias do tribunal correto?
- [ ] Backoff exponencial implementado?
- [ ] Campos e códigos de movimento na TPU (tabela processual unificada)?
- [ ] Logs de extração auditáveis?
- [ ] Nunca re-publicar dado sensível (sigilo) obtido acidentalmente.
