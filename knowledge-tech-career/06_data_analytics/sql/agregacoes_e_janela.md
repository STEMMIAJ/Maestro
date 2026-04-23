---
titulo: "Agregações e funções de janela — COUNT/SUM/AVG, GROUP BY vs OVER"
bloco: "06_data_analytics/sql"
tipo: "referencia"
nivel: "intermediario"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 7
---

# Agregações e funções de janela

`GROUP BY` reduz linhas — um registro por grupo. **Função de janela** (`OVER`) preserva linhas e anexa agregado como coluna extra. Dois paradigmas que resolvem problemas diferentes.

## Agregações básicas

- `COUNT(*)` — total de linhas.
- `COUNT(col)` — linhas com valor não-nulo.
- `COUNT(DISTINCT col)` — valores únicos.
- `SUM(col)` — soma.
- `AVG(col)` — média. NULL é ignorado.
- `MIN(col)`, `MAX(col)`.
- `GROUP_CONCAT(col)` (SQLite/MySQL) ou `STRING_AGG` (PG) — concatena valores.

## GROUP BY

```sql
SELECT tribunal,
       COUNT(*) AS total,
       COUNT(DISTINCT classe) AS classes_distintas,
       AVG(valor_causa) AS valor_medio
FROM processos
GROUP BY tribunal;
```

Resultado: uma linha por tribunal.

## HAVING vs WHERE

```sql
SELECT classe, COUNT(*) AS n
FROM processos
WHERE data_autuacao >= '2024-01-01'   -- filtra linhas
GROUP BY classe
HAVING COUNT(*) >= 5;                  -- filtra grupos
```

## Funções de janela — OVER

Sintaxe base:

```sql
<funcao>(col) OVER (
  [PARTITION BY col_part]
  [ORDER BY col_ord]
  [ROWS BETWEEN ...]
)
```

Não colapsa linhas. Cada linha recebe agregado da sua "janela".

## Exemplo: total por tribunal sem perder as linhas

```sql
SELECT numero_cnj,
       tribunal,
       valor_causa,
       SUM(valor_causa) OVER (PARTITION BY tribunal) AS total_tribunal,
       valor_causa * 1.0 / SUM(valor_causa) OVER (PARTITION BY tribunal) AS peso
FROM processos;
```

Cada processo mantém suas colunas e ganha **total do tribunal** e **peso relativo**.

## Ranking

- `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` — posição única (1, 2, 3…).
- `RANK()` — empates compartilham posição, pula a seguinte (1, 1, 3).
- `DENSE_RANK()` — empates compartilham, sem pular (1, 1, 2).
- `NTILE(4)` — quartis; `NTILE(10)` — decis.

```sql
SELECT numero_cnj, tribunal, valor_causa,
       ROW_NUMBER() OVER (PARTITION BY tribunal ORDER BY valor_causa DESC) AS rn
FROM processos;
```

Filtrar `rn = 1` pega o processo de maior valor por tribunal.

## Lead / Lag — comparar com linhas vizinhas

```sql
SELECT numero_cnj, data,
       LAG(data) OVER (PARTITION BY numero_cnj ORDER BY data) AS mov_anterior,
       julianday(data) - julianday(LAG(data) OVER (PARTITION BY numero_cnj ORDER BY data)) AS dias_desde_ultima
FROM movimentacoes;
```

Útil em auditoria temporal de laudos / movimentações.

## Janela deslizante

Média móvel de 7 dias:

```sql
SELECT data,
       AVG(total_perícias) OVER (
         ORDER BY data
         ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS media_movel_7d
FROM perícias_diarias;
```

## Quando usar cada

| Necessidade | Ferramenta |
|---|---|
| Uma linha por grupo, só agregados | GROUP BY |
| Manter detalhe + mostrar agregado | OVER (PARTITION BY) |
| Rankings top-N por grupo | ROW_NUMBER + filtro |
| Comparação com linha anterior | LAG/LEAD |
| Média móvel / cumulativa | OVER + ROWS BETWEEN |

## Performance

- Funções de janela são pesadas — indexar as colunas de PARTITION e ORDER.
- Evitar múltiplas janelas diferentes no mesmo SELECT; usar CTEs.
- SQLite suporta window functions desde a 3.25 (2018); versões antigas não.
