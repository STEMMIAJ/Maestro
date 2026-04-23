---
titulo: "SQL mínimo — SELECT, WHERE, JOIN, GROUP BY, ORDER BY"
bloco: "06_data_analytics/sql"
tipo: "referencia"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 9
---

# SQL mínimo para o perito analista

Linguagem universal para consultar bancos relacionais. Mesma sintaxe serve para DATAJUD (extraído), DATASUS (exportado), SQLite local de laudos.

## Ordem lógica de execução

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

Diferente da ordem de escrita (SELECT vem primeiro na escrita). Entender a ordem lógica evita erros comuns.

## Tabela-exemplo: processos

```
processos(id, numero_cnj, tribunal, classe, data_autuacao, valor_causa, parte_autora, status)
movimentacoes(id, processo_id, data, tipo, descricao)
```

## SELECT + FROM

```sql
SELECT numero_cnj, tribunal, data_autuacao
FROM processos;
```

`SELECT *` traz tudo — útil para explorar, ruim em produção (lento, frágil a mudanças).

## WHERE — filtro de linhas

```sql
SELECT numero_cnj, valor_causa
FROM processos
WHERE tribunal = 'TJMG'
  AND valor_causa > 50000
  AND data_autuacao >= '2024-01-01';
```

Operadores úteis:
- `=`, `<>`, `<`, `>`, `<=`, `>=`
- `IN ('TJMG', 'TJSP')`, `NOT IN`
- `BETWEEN 1000 AND 5000`
- `LIKE 'AÇÃO%'` (% = qualquer sequência; _ = um caractere)
- `IS NULL`, `IS NOT NULL`

## ORDER BY

```sql
SELECT numero_cnj, valor_causa
FROM processos
ORDER BY valor_causa DESC, data_autuacao ASC;
```

`DESC` decrescente; `ASC` padrão.

## LIMIT / OFFSET

```sql
SELECT * FROM processos
ORDER BY data_autuacao DESC
LIMIT 20 OFFSET 40;
```

Paginação: pula 40, traz 20.

## JOIN — unindo tabelas

```sql
SELECT p.numero_cnj, m.data, m.tipo
FROM processos p
INNER JOIN movimentacoes m ON m.processo_id = p.id
WHERE p.tribunal = 'TJMG'
  AND m.tipo = 'PUBLICACAO';
```

Alias (`p`, `m`) reduz digitação.

## GROUP BY — agregação

```sql
SELECT tribunal, COUNT(*) AS total, AVG(valor_causa) AS valor_medio
FROM processos
WHERE data_autuacao >= '2024-01-01'
GROUP BY tribunal
ORDER BY total DESC;
```

Regra: tudo no SELECT que **não é função de agregação** precisa estar no GROUP BY.

## HAVING — filtro após agregação

```sql
SELECT tribunal, COUNT(*) AS total
FROM processos
GROUP BY tribunal
HAVING COUNT(*) > 10;
```

`WHERE` filtra linhas individuais; `HAVING` filtra grupos.

## Funções úteis

- **Agregação**: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.
- **String**: `UPPER`, `LOWER`, `SUBSTR`, `REPLACE`, `||` (concat SQLite/PG).
- **Data**: `DATE(col)`, `strftime('%Y-%m', col)` (SQLite), `EXTRACT(YEAR FROM col)` (PG).
- **CASE WHEN**: condicional em linha.

```sql
SELECT
  numero_cnj,
  CASE
    WHEN valor_causa < 10000 THEN 'baixo'
    WHEN valor_causa < 100000 THEN 'medio'
    ELSE 'alto'
  END AS faixa
FROM processos;
```

## CTE (Common Table Expression)

Subconsulta nomeada, melhora legibilidade.

```sql
WITH processos_altos AS (
  SELECT * FROM processos WHERE valor_causa > 1000000
)
SELECT tribunal, COUNT(*)
FROM processos_altos
GROUP BY tribunal;
```

## Armadilhas

- `NULL` não compara com `=` — usar `IS NULL`.
- `COUNT(col)` ignora NULL; `COUNT(*)` conta todas as linhas.
- Divisão inteira em alguns SGBDs: `SUM(x) / COUNT(*)` pode truncar — usar `* 1.0`.
- `ORDER BY` fora de subqueries pode ser ignorado pelo planner.
