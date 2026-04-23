---
titulo: Sintaxe mínima de Python
bloco: 02_programming
tipo: referencia
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 8
---

# Sintaxe mínima de Python

Cobre 90% do que aparece em script pericial.

## Tipos básicos
```python
numero = 42              # int
valor = 3.14             # float
nome = "José Silva"      # str
presente = True          # bool
nada = None              # None (ausência de valor)
```

Converter entre tipos: `int("10")`, `str(42)`, `float("3.14")`.

## Operadores
```python
2 + 3      # 5
10 / 3     # 3.333
10 // 3    # 3   (divisão inteira)
10 % 3     # 1   (resto)
2 ** 8     # 256 (potência)

a == b     # igualdade
a != b     # diferença
a and b    # E lógico
a or b     # OU lógico
not a      # negação
```

## Condicional
```python
if idade >= 18:
    status = "adulto"
elif idade >= 12:
    status = "adolescente"
else:
    status = "crianca"
```

Indentação é obrigatória (4 espaços). Não há `{}`.

## Loops
```python
# for — itera sobre coleção
for processo in lista_processos:
    print(processo.cnj)

# range — sequência numérica
for i in range(10):        # 0..9
    print(i)

# while — até condição virar falsa
tentativas = 0
while tentativas < 3:
    if tentar_login():
        break
    tentativas += 1
```

`break` sai do loop. `continue` pula para próxima iteração.

## Funções
```python
def extrair_cnj(texto: str) -> str | None:
    """Extrai número CNJ no formato 0000000-00.0000.0.00.0000."""
    import re
    match = re.search(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", texto)
    return match.group(0) if match else None

numero = extrair_cnj("Processo 0001234-56.2025.8.13.0024 ...")
```

Anotações `: str` e `-> str | None` são opcionais mas valem: ajudam o editor a avisar erro.

Parâmetros com valor padrão:
```python
def baixar(url: str, timeout: int = 30) -> bytes:
    ...
baixar("https://..")           # timeout=30
baixar("https://..", timeout=60)
```

## Classes
Classe = molde para criar objetos com dados (atributos) e funções (métodos).

```python
class Processo:
    def __init__(self, cnj: str, autor: str):
        self.cnj = cnj
        self.autor = autor
        self.movimentacoes = []

    def adicionar_movimentacao(self, texto: str):
        self.movimentacoes.append(texto)

    def __repr__(self):
        return f"Processo({self.cnj})"

p = Processo("0001-2024", "João")
p.adicionar_movimentacao("Juntada de laudo")
print(p)   # Processo(0001-2024)
```

Quando usar classe: quando há **dados + operações que andam juntos**. Para script simples, função é suficiente — não criar classe só por criar.

## Estrutura de arquivo
```python
# imports no topo
import json
from pathlib import Path

# constantes
PASTA_LAUDOS = Path.home() / "Desktop" / "laudos"

# funções
def carregar_ficha(caminho: Path) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))

# ponto de entrada
if __name__ == "__main__":
    ficha = carregar_ficha(PASTA_LAUDOS / "FICHA.json")
    print(ficha["cnj"])
```

`if __name__ == "__main__":` — roda só quando o arquivo é executado direto, não quando importado por outro.

## Armadilhas
- Listas e dicts são passados por referência — modificar dentro de função altera o original.
- Comparar com `None` usa `is`: `if x is None`, não `if x == None`.
- Strings são imutáveis: `s.replace("a","b")` retorna nova string, não muda `s`.
