---
titulo: "SQLite local para perícia — banco de laudos em arquivo"
bloco: "06_data_analytics/sql"
tipo: "pratica"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 8
---

# SQLite local para perícia

SQLite = banco relacional em **um único arquivo**, sem servidor. Ideal para base de laudos, índice de processos, log de movimentações do perito que trabalha solo.

## Por que SQLite

- Zero configuração. Um `.db` portátil, dá para copiar, versionar (com cuidado), backupar.
- Nativo no macOS (`/usr/bin/sqlite3`) e em Python (`import sqlite3`, stdlib).
- Suporta transações, índices, FTS (full-text search), JSON.
- Limites práticos: até ~1 TB; milhões de linhas sem sofrimento.
- Quando **não** usar: múltiplos usuários escrevendo ao mesmo tempo (lock). Para isso, PostgreSQL.

## Esquema-exemplo para perícias

```sql
CREATE TABLE processos (
  id INTEGER PRIMARY KEY,
  numero_cnj TEXT UNIQUE NOT NULL,
  tribunal TEXT,
  vara TEXT,
  classe TEXT,
  parte_autora TEXT,
  data_nomeacao DATE,
  valor_causa REAL,
  status TEXT DEFAULT 'ativo'
);

CREATE TABLE laudos (
  id INTEGER PRIMARY KEY,
  processo_id INTEGER REFERENCES processos(id),
  data_entrega DATE,
  tempo_elaboracao_horas REAL,
  arquivo_pdf TEXT,
  quesitos_total INTEGER,
  honorarios REAL
);

CREATE INDEX ix_laudos_processo ON laudos(processo_id);
CREATE INDEX ix_processos_tribunal ON processos(tribunal);
```

## CLI `sqlite3`

```bash
sqlite3 ~/Desktop/pericia.db

# úteis:
.mode column
.headers on
.tables
.schema processos
.import --csv arquivo.csv processos
.output relatorio.csv
SELECT ...;
.output stdout
.quit
```

Importar CSV direto:

```bash
sqlite3 pericia.db <<'EOF'
.mode csv
.import processos_exportados.csv processos
EOF
```

## Python — sqlite3 stdlib

```python
import sqlite3
from pathlib import Path

DB = Path.home() / "Desktop/pericia.db"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row  # acesso por nome de coluna
cur = con.cursor()

# INSERT seguro (sempre placeholders, nunca f-string)
cur.execute(
    "INSERT INTO laudos(processo_id, data_entrega, honorarios) VALUES (?, ?, ?)",
    (42, "2026-04-20", 3500.00)
)
con.commit()

# SELECT
for row in cur.execute("SELECT numero_cnj, classe FROM processos WHERE tribunal = ?", ("TJMG",)):
    print(row["numero_cnj"], row["classe"])

con.close()
```

## Pandas — análise rápida

```python
import pandas as pd
import sqlite3

con = sqlite3.connect(DB)
df = pd.read_sql_query(
    "SELECT l.*, p.tribunal FROM laudos l JOIN processos p ON p.id = l.processo_id",
    con
)
df.groupby("tribunal")["honorarios"].agg(["count", "mean", "sum"])
```

## Relatórios típicos para perito

```sql
-- Laudos entregues por mês
SELECT strftime('%Y-%m', data_entrega) AS mes, COUNT(*) AS n, SUM(honorarios) AS receita
FROM laudos
GROUP BY mes
ORDER BY mes DESC;

-- Tempo médio por classe processual
SELECT p.classe, AVG(l.tempo_elaboracao_horas) AS h_medio, COUNT(*) AS n
FROM laudos l JOIN processos p ON p.id = l.processo_id
GROUP BY p.classe
HAVING n >= 3
ORDER BY h_medio DESC;

-- Processos sem laudo há mais de 90 dias (atraso)
SELECT p.numero_cnj, p.data_nomeacao,
       julianday('now') - julianday(p.data_nomeacao) AS dias
FROM processos p
LEFT JOIN laudos l ON l.processo_id = p.id
WHERE l.id IS NULL
  AND dias > 90;
```

## Boas práticas

- **Sempre placeholders** (`?`) — evita SQL injection e erros de tipo.
- **Transações explícitas** em cargas grandes: `BEGIN; ...; COMMIT;` — reduz I/O 100×.
- **Backup**: `sqlite3 pericia.db ".backup /caminho/backup.db"` (consistente, com DB aberto).
- **WAL mode** para concorrência leitura/escrita: `PRAGMA journal_mode = WAL;`.
- **FTS5** para busca textual em laudos: `CREATE VIRTUAL TABLE laudos_fts USING fts5(texto);`.

## Integração no sistema de perícias

Apontar para `~/Desktop/STEMMIA Dexter/dados/pericia.db`. Backup diário no launchd (03h, junto com mesa-sweep). Versionar só o schema (`schema.sql`), nunca o `.db` em git — binário cresce rápido.
