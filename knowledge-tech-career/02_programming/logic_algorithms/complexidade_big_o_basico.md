---
titulo: Complexidade e Big-O básico
bloco: 02_programming
tipo: conceito
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 5
---

# Complexidade e Big-O básico

Big-O descreve como o tempo (ou memória) de um algoritmo cresce conforme a entrada cresce. `n` = tamanho da entrada (ex.: 100 processos → `n=100`).

Não mede segundos. Mede **forma** de crescimento.

## O(1) — tempo constante
Executa em tempo fixo, independente de `n`.

Exemplo: acessar `processos[0]` numa lista. Custa o mesmo com 10 ou 10 milhões de itens.

Por que importa: operação de dicionário `processos_por_cnj["0001234-56.2025.8.13.0024"]` é O(1). Por isso dict é preferível a `for` em lista quando há busca frequente.

## O(n) — tempo linear
Cresce proporcional à entrada. Dobra a entrada → dobra o tempo.

Exemplo: percorrer lista de 100 processos para filtrar quais têm audiência marcada.
```python
for p in processos:   # n passos
    if p.tem_audiencia:
        ...
```
100 processos → 100 iterações. 1000 → 1000. Tranquilo até milhões.

## O(log n) — tempo logarítmico
Cresce muito devagar. Dobrar a entrada acrescenta 1 passo só.

Exemplo: busca binária em lista ordenada. 1 milhão de itens → ~20 passos.

Por que importa: índice de banco de dados (B-tree) é O(log n). Por isso consulta SQL com índice é rápida mesmo com milhões de linhas.

## O(n²) — tempo quadrático
Dois loops aninhados sobre a mesma entrada. Dobra entrada → 4× o tempo.

Exemplo — achar processos duplicados comparando todos com todos:
```python
for a in processos:       # n
    for b in processos:   # n
        if a.cnj == b.cnj and a is not b:
            ...
```
100 processos → 10.000 comparações. 10.000 → 100 milhões. Evitar.

Solução: usar `set` de CNJs já vistos → cai para O(n).

## Regra de bolso
| Complexidade | Até onde aguenta (rule of thumb) |
|---|---|
| O(1), O(log n) | Qualquer tamanho |
| O(n), O(n log n) | Até ~10⁷ itens |
| O(n²) | Até ~10⁴ itens |
| O(2ⁿ), O(n!) | Até ~20 itens |

Se o script demora muito com pouca entrada, o problema provavelmente é complexidade ruim — não hardware.
