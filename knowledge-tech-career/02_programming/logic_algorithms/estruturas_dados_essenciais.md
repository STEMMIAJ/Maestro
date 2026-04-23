---
titulo: Estruturas de dados essenciais (Python)
bloco: 02_programming
tipo: conceito
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 5
---

# Estruturas de dados essenciais

Quatro estruturas resolvem 80% dos casos: **lista**, **dict**, **set**, **tupla**.

## Lista `list`
Sequência ordenada, mutável, permite duplicados.

```python
processos = ["0001-2024", "0002-2024", "0003-2024"]
processos.append("0004-2024")
processos[0]  # "0001-2024" — O(1)
"0005-2024" in processos  # O(n) — lento se grande
```

Quando usar: precisa da ordem, precisa iterar, quantidade moderada. Ex.: lista de movimentações de um processo em ordem cronológica.

## Dict `dict`
Mapa chave→valor. Busca por chave O(1). Chaves únicas.

```python
processos_por_cnj = {
    "0001-2024": {"autor": "João", "status": "aguardando pericia"},
    "0002-2024": {"autor": "Maria", "status": "laudo entregue"},
}
processos_por_cnj["0001-2024"]["status"]  # O(1)
```

Quando usar: precisa buscar por identificador. Ex.: mapear CNJ→dados do processo, CID→descrição, nome do arquivo→caminho.

Por que importa: trocar `for p in lista: if p.cnj == alvo` por `dict[alvo]` transforma O(n) em O(1). Em 10.000 processos, diferença de segundos para instantâneo.

## Set `set`
Coleção sem ordem, sem duplicados, busca O(1).

```python
cnjs_ja_baixados = {"0001-2024", "0002-2024"}
if "0003-2024" not in cnjs_ja_baixados:
    baixar(...)
    cnjs_ja_baixados.add("0003-2024")
```

Quando usar: deduplicar, testar pertencimento rápido, operações de conjunto (união, interseção). Ex.: CNJs novos = `cnjs_djen - cnjs_ja_vistos`.

## Tupla `tuple`
Igual a lista, porém imutável. Pode ser chave de dict.

```python
coordenada = (latitude, longitude)   # não vai mudar
chave = ("2026-04-23", "TJMG")       # pode ser chave em dict
```

Quando usar: agrupar valores que não devem mudar; retornar múltiplos valores de função (`return nome, cpf, idade`).

## Escolha rápida
| Precisa | Use |
|---|---|
| Ordem + duplicados + iteração | `list` |
| Buscar por chave rápido | `dict` |
| Remover duplicados / pertencimento | `set` |
| Pacote imutável de valores | `tuple` |

Regra: se o código tem `for x in lista: if x.id == alvo`, quase sempre o certo é `dict`.
