---
titulo: "Pipeline ETL básico — DATAJUD para SQLite para dashboard"
bloco: "06_data_analytics/data_engineering_basics"
tipo: "pratica"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 10
---

# Pipeline ETL básico

ETL = **Extract, Transform, Load**. Fluxo que pega dado de uma fonte, normaliza, grava em destino analítico. Aplicação direta na perícia: baixar movimentações do DATAJUD, normalizar, armazenar, visualizar.

## Fases

### 1. Extract

Buscar dado bruto na fonte.

- API REST (DATAJUD, DJEN, Comunica PJe).
- Scraping HTML (TJMG, TJSP, tribunais sem API).
- Arquivos (CSV, Excel, PDF de intimação).
- Banco de produção (Postgres do PJe, leitor-só).

Regras:
- **Idempotência**: re-rodar não duplica dados.
- **Paginação + backoff exponencial** (DataJud: máx 120 req/min).
- Salvar resposta bruta (`raw/`) em JSON datado antes de transformar — auditoria e reprocessamento.

### 2. Transform

Normalizar para esquema analítico.

- Limpeza: trim, lowercase, remover acentos em chaves (não em conteúdo).
- Deduplicação por chave (número CNJ + data + tipo).
- Conversão de tipos (data ISO, decimais).
- Enriquecimento: derivar campos (tribunal a partir do número CNJ, faixa de valor).
- Aplicar regras de negócio (filtrar homônimos, só manter processos onde o perito é nomeado).

### 3. Load

Gravar em destino otimizado para consulta.

- SQLite para volumes até ~1 GB.
- Postgres para concorrência e volumes maiores.
- Parquet para análise colunar (Pandas, DuckDB).

Estratégias:
- **Full refresh**: apaga tudo e recarrega. Simples, OK em datasets pequenos.
- **Upsert (MERGE)**: insere novos, atualiza existentes por chave.
- **Append-only**: sempre INSERT; snapshots históricos.

## Exemplo: DATAJUD → SQLite → dashboard

### Estrutura de pastas

```
pipeline_datajud/
  raw/           # JSONs crus datados
  staging/       # CSVs normalizados
  db/            # pericia.db
  scripts/
    extract.py
    transform.py
    load.py
    run.sh
  logs/
```

### extract.py (esqueleto)

```python
import json, requests, time
from datetime import datetime
from pathlib import Path

URL = "https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search"
API_KEY = "..."  # ref: DATAJUD-GUIA.md

def buscar(ano_desde: int) -> list[dict]:
    resultados, after = [], None
    while True:
        body = {"size": 1000, "query": {...}, "sort": [{"@timestamp": "asc"}]}
        if after: body["search_after"] = after
        r = requests.post(URL, json=body, headers={"Authorization": f"APIKey {API_KEY}"})
        r.raise_for_status()
        hits = r.json()["hits"]["hits"]
        if not hits: break
        resultados.extend(hits)
        after = hits[-1]["sort"]
        time.sleep(0.5)  # backoff
    return resultados

out = Path("raw") / f"tjmg_{datetime.now():%Y%m%d_%H%M}.json"
out.write_text(json.dumps(buscar(2024), ensure_ascii=False))
```

### transform.py

```python
import json, pandas as pd
from pathlib import Path

latest = max(Path("raw").glob("tjmg_*.json"))
docs = [h["_source"] for h in json.loads(latest.read_text())]

df = pd.DataFrame(docs)
df["data_autuacao"] = pd.to_datetime(df["dataAjuizamento"])
df["numero_cnj"] = df["numeroProcesso"].str.replace(r"\D", "", regex=True)
df = df.drop_duplicates("numero_cnj")
df = df[df["classe"].isin(["AÇÃO CIVIL", "PROCEDIMENTO COMUM"])]

df.to_csv("staging/processos.csv", index=False)
```

### load.py

```python
import sqlite3, pandas as pd

con = sqlite3.connect("db/pericia.db")
df = pd.read_csv("staging/processos.csv")

df.to_sql("_stage_processos", con, if_exists="replace", index=False)
con.execute("""
INSERT INTO processos (numero_cnj, tribunal, classe, data_autuacao, valor_causa)
SELECT numero_cnj, 'TJMG', classe, data_autuacao, valor_causa
FROM _stage_processos
WHERE numero_cnj NOT IN (SELECT numero_cnj FROM processos);
""")
con.commit(); con.close()
```

### run.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/extract.py   >> logs/extract.log  2>&1
python3 scripts/transform.py >> logs/transform.log 2>&1
python3 scripts/load.py      >> logs/load.log      2>&1
```

Agendar via launchd (ver `agendamento_cron_launchd.md`).

## Boas práticas

1. **Um script faz uma coisa** (extract separado de transform).
2. **Falha ruidosa**: `set -euo pipefail`, `raise_for_status`, logs com timestamp.
3. **Observabilidade**: contar linhas processadas, comparar com run anterior. Queda > 30% → alerta.
4. **Schema evolution**: versionar DDL; migrations idempotentes.
5. **Testes**: unitário na função de transformação com JSON de exemplo.
6. **Secrets**: nunca no código; usar `.env` + `pass`/Keychain.

## Quando evoluir

- Volume > 10 GB → avaliar Airflow ou Prefect.
- Múltiplas fontes + joins complexos → dbt em cima do destino.
- Necessidade near-real-time → streaming (Kafka, Debezium) — overkill para perícia solo.
