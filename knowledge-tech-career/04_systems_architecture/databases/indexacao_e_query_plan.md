---
titulo: Indexação e Query Plan
bloco: 04_systems_architecture
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 7
---

# Indexação e Query Plan

Índice = estrutura auxiliar que acelera busca por custo de espaço e escrita. Sem índice, DB varre tabela inteira (**sequential scan**). Com índice certo, vai direto.

## Tipos de índice (Postgres)

### B-tree (padrão)

Árvore balanceada. Rápido para `=`, `<`, `>`, `BETWEEN`, `ORDER BY`, `LIKE 'prefixo%'`.

```sql
CREATE INDEX ix_processos_vara ON processos(vara);
CREATE INDEX ix_processos_vara_status ON processos(vara, status);
```

**Ordem das colunas importa** em índice composto. `(vara, status)` serve query por `vara` ou `vara+status`; **não** serve query só por `status`.

### GIN (Generalized Inverted Index)

Para colunas com múltiplos valores: arrays, JSON-B, tsvector (full-text), trigrams.

```sql
CREATE INDEX ix_processos_tags ON processos USING GIN(tags);
CREATE INDEX ix_laudos_fts ON laudos USING GIN(to_tsvector('portuguese', conteudo));
CREATE INDEX ix_processos_metadata ON processos USING GIN(metadata jsonb_path_ops);
```

### GiST

Para geometria (PostGIS), range types, full-text alternativo.

### BRIN (Block Range Index)

Compacto, bom para colunas naturalmente ordenadas (timestamp de inserção em tabela gigante).

### Hash

Só `=`. Raramente usado; B-tree cobre.

### Unique

Garante unicidade. Também acelera busca.

```sql
CREATE UNIQUE INDEX ix_processos_numero ON processos(numero);
```

### Parcial (partial index)

Índice só em subset.

```sql
-- só processos ativos, não arquivados
CREATE INDEX ix_processos_ativos ON processos(vara, prazo)
  WHERE status = 'ativo';
```

Economia de espaço, queries mais rápidas.

### Expressão

Indexar resultado de função.

```sql
CREATE INDEX ix_processos_numero_lower ON processos(LOWER(numero));
-- query correspondente:
SELECT * FROM processos WHERE LOWER(numero) = LOWER('...');
```

## EXPLAIN — como o DB vai executar

```sql
EXPLAIN SELECT * FROM processos WHERE vara = '1ª Vara Federal';
```

Saída possível:
```
Seq Scan on processos  (cost=0.00..234.00 rows=1200 width=128)
  Filter: (vara = '1ª Vara Federal'::text)
```

`Seq Scan` = leu tudo. Ruim em tabela grande.

Com índice:
```
Index Scan using ix_processos_vara on processos  (cost=0.29..8.31 rows=1200 width=128)
  Index Cond: (vara = '1ª Vara Federal'::text)
```

Muito melhor. Variantes: `Bitmap Index Scan`, `Index Only Scan` (não precisa ir à tabela).

### EXPLAIN ANALYZE

Executa de verdade e mede:

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
```

Mostra tempo real + leituras de disco vs cache. Essencial para diagnosticar.

Regra: se `actual rows` diverge muito de `estimated rows`, estatísticas desatualizadas. Rodar `ANALYZE processos`.

## Lentidão típica — diagnóstico

| Sintoma | Causa provável | Remédio |
|---------|----------------|---------|
| `Seq Scan` em tabela grande | Falta índice | `CREATE INDEX` |
| `N+1 queries` (100 SELECTs ao listar) | ORM sem eager loading | `JOIN` / `select_related` |
| Query lenta com `LIKE '%x%'` | Índice B-tree não serve | Trigram + GIN, ou full-text |
| `ORDER BY + LIMIT` lento | Falta índice ordenado | Índice nas colunas do `ORDER BY` |
| Update/insert lento | Muitos índices, locks | Reavaliar índices; batch |
| DISTINCT lento em milhões | Agregação custosa | Índice + agregação incremental |
| `WHERE col IS NULL` sem índice | B-tree cobre, mas cardinalidade | Parcial com `WHERE col IS NULL` |

## Quando NÃO indexar

- Coluna com baixa seletividade (sexo M/F em 1M linhas — full scan é melhor).
- Tabela pequena (< ~1000 linhas) — overhead supera ganho.
- Coluna atualizada com frequência e pouco consultada.

Cada índice custa: espaço em disco + CPU em cada INSERT/UPDATE/DELETE. Índice excessivo = escrita lenta.

## Estatísticas

DB mantém histograma por coluna. `ANALYZE` atualiza. Autovacuum do Postgres roda automático, mas pode ficar atrás em tabelas muito escritas.

```sql
ANALYZE processos;
VACUUM ANALYZE processos;  -- + libera espaço
```

## Composite index + covering

Índice que inclui TODAS as colunas da query = "index-only scan" (não precisa ler a tabela).

```sql
CREATE INDEX ix_processos_vara_cover
  ON processos(vara, status) INCLUDE (numero, autor);

-- query totalmente servida pelo índice:
SELECT numero, autor FROM processos
 WHERE vara = '...' AND status = 'ativo';
```

## Índice para JOIN

FK geralmente merece índice (não automático em Postgres). Query com `JOIN outro_tabela ON outro.processo_id = processos.id` exige índice em `outro.processo_id`.

## Ferramentas

- `pg_stat_statements` — queries mais lentas/frequentes.
- `pgBadger` — análise de logs.
- `pgAnalyze` / `pganalyze` — dashboards SaaS.
- `auto_explain` — loga plano de queries lentas automaticamente.
- `hypopg` — simular índice sem criar (ver ganho hipotético).

## Para o sistema pericial

Índices prováveis:
- `UNIQUE` em `processos.numero`.
- B-tree em `processos.vara`, `processos.status`, `processos.prazo`.
- GIN em `to_tsvector('portuguese', laudo.conteudo)` para busca textual.
- pgvector `ivfflat`/`hnsw` em embedding de laudo para similaridade.
- Parcial em `processos WHERE status = 'ativo'` (filtro padrão do dashboard).

Rodar `EXPLAIN ANALYZE` em toda query que aparecer no dashboard. Meta: < 100ms em 10k processos.

## Armadilhas

- Criar índice para cada coluna "por garantia" — escrita despenca.
- Esquecer de indexar FK.
- Consultar com `WHERE data::text LIKE '2026%'` em vez de `WHERE data >= '2026-01-01'` — conversão mata índice.
- Função no lado do índice (`WHERE UPPER(nome) = 'X'`) sem índice funcional.
- `ANALYZE` atrasado após grande importação → planner escolhe ruim.
