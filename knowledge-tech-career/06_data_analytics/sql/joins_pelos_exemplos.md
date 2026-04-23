---
titulo: "JOINs por exemplos — INNER, LEFT, RIGHT, FULL"
bloco: "06_data_analytics/sql"
tipo: "referencia"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 7
---

# JOINs explicados por exemplos

Duas tabelas pequenas ilustram as 4 variações. Decore os diagramas — em análise pericial, escolher o JOIN errado perde ou duplica registros.

## Tabelas-exemplo

**pacientes**
| id | nome          |
|----|---------------|
| 1  | Ana           |
| 2  | Bruno         |
| 3  | Carla         |
| 4  | Diego         |

**laudos**
| id | paciente_id | arquivo        |
|----|-------------|----------------|
| 10 | 1           | laudo_ana.pdf  |
| 11 | 1           | laudo_ana2.pdf |
| 12 | 2           | laudo_bruno.pdf|
| 13 | 5           | orfao.pdf      |

## INNER JOIN — interseção

Só linhas com correspondência nas duas tabelas.

```sql
SELECT p.nome, l.arquivo
FROM pacientes p
INNER JOIN laudos l ON l.paciente_id = p.id;
```

Resultado:
| nome  | arquivo        |
|-------|----------------|
| Ana   | laudo_ana.pdf  |
| Ana   | laudo_ana2.pdf |
| Bruno | laudo_bruno.pdf|

Carla e Diego desaparecem (não têm laudo). Registro 13 desaparece (paciente 5 não existe).

## LEFT JOIN — tudo da esquerda

Todos os pacientes, com ou sem laudo. Sem correspondência → NULL.

```sql
SELECT p.nome, l.arquivo
FROM pacientes p
LEFT JOIN laudos l ON l.paciente_id = p.id;
```

| nome  | arquivo        |
|-------|----------------|
| Ana   | laudo_ana.pdf  |
| Ana   | laudo_ana2.pdf |
| Bruno | laudo_bruno.pdf|
| Carla | NULL           |
| Diego | NULL           |

**Uso clássico**: encontrar pacientes **sem** laudo:

```sql
SELECT p.nome
FROM pacientes p
LEFT JOIN laudos l ON l.paciente_id = p.id
WHERE l.id IS NULL;
```

→ Carla, Diego.

## RIGHT JOIN — tudo da direita

Inverso do LEFT. Raramente usado porque basta inverter tabelas e usar LEFT.

```sql
SELECT p.nome, l.arquivo
FROM pacientes p
RIGHT JOIN laudos l ON l.paciente_id = p.id;
```

Resultado inclui `orfao.pdf` com `nome = NULL` (paciente 5 não existe).

## FULL OUTER JOIN — união

Todas as linhas das duas tabelas, pareando quando possível.

```sql
SELECT p.nome, l.arquivo
FROM pacientes p
FULL OUTER JOIN laudos l ON l.paciente_id = p.id;
```

| nome  | arquivo        |
|-------|----------------|
| Ana   | laudo_ana.pdf  |
| Ana   | laudo_ana2.pdf |
| Bruno | laudo_bruno.pdf|
| Carla | NULL           |
| Diego | NULL           |
| NULL  | orfao.pdf      |

**SQLite não tem FULL JOIN nativo** — emular com `UNION` de LEFT + RIGHT.

## CROSS JOIN — produto cartesiano

Toda linha de A × toda linha de B. 4 pacientes × 4 laudos = 16 linhas.
Raro em análise — útil para gerar grade de combinações.

## Armadilhas

1. **JOIN sem ON** → produto cartesiano silencioso, resultado explode.
2. **Filtro em WHERE anula LEFT JOIN**: `WHERE l.arquivo = 'x'` remove as linhas NULL. Usar filtro dentro do ON ou filtrar antes com CTE.
3. **Duplicações**: se tabela B tem múltiplas linhas por chave, JOIN duplica A. Conferir com `COUNT(DISTINCT p.id)`.
4. **Performance**: JOIN em coluna sem índice é lento. Sempre indexar chaves estrangeiras.

## Resumo visual

```
A INNER B    = A ∩ B
A LEFT B     = A (∪ B quando existe)
A RIGHT B    = B (∪ A quando existe)
A FULL B     = A ∪ B
A CROSS B    = A × B
```
