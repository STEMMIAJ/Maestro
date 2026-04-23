---
titulo: Debug com pdb, breakpoint e logging
bloco: 02_programming
tipo: tutorial
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 4
---

# Debug — pdb, breakpoint, print e logging

Três ferramentas. Cada uma para um momento.

## `print` — investigação rápida, descartável
Coloca, roda, entende, **apaga**.

```python
def processar(ficha):
    print("DEBUG ficha recebida:", ficha)
    cnj = ficha.get("cnj")
    print("DEBUG cnj extraido:", cnj)
    ...
```

Quando usar: script curto, bug óbvio, 30 segundos de investigação.

Problema: `print` vira ruído. Esquecer uns no código é feio e em produção polui. Sempre apagar depois.

## `logging.debug` — investigação durável, controlável
Vira log com nível `DEBUG`. Desliga sem editar código (muda só `level=`).

```python
import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def processar(ficha):
    log.debug("ficha recebida: %s", ficha)
    cnj = ficha.get("cnj")
    log.debug("cnj extraido: %s", cnj)
    ...
```

Quando usar: script em produção, bug intermitente, quer registro histórico, precisa ativar/desligar sem recompilar.

Dica: instrumentar pontos suspeitos com `log.debug` e deixar lá. Em produção, nível `INFO`; investigando, troca para `DEBUG`.

## `breakpoint()` — inspeção interativa
Python 3.7+. Para execução e abre shell no ponto exato.

```python
def processar(ficha):
    cnj = ficha.get("cnj")
    breakpoint()               # pausa aqui
    resultado = ...
```

Ao rodar, cai no `(Pdb)`. Comandos essenciais:

| Comando | Faz |
|---|---|
| `n` (next) | próxima linha |
| `s` (step) | entra na função |
| `c` (continue) | segue até próximo breakpoint |
| `l` (list) | mostra código ao redor |
| `p <var>` | imprime variável |
| `pp <var>` | pretty-print (dict/list bonito) |
| `w` (where) | stack trace |
| `q` (quit) | aborta execução |

Variáveis livres: qualquer nome do escopo atual.
```
(Pdb) p ficha
{'cnj': '0001-2024', ...}
(Pdb) p type(cnj)
<class 'NoneType'>
(Pdb) cnj or "sem numero"
'sem numero'
```

Quando usar: bug opaco, precisa olhar estado real, testar hipóteses ao vivo.

Desligar: `PYTHONBREAKPOINT=0 python3 script.py` — sem editar código.

## `pdb` — módulo completo
`breakpoint()` é o jeito moderno. Equivalente antigo:
```python
import pdb; pdb.set_trace()
```

Rodar um script direto no debugger desde o início:
```bash
python3 -m pdb script.py
```

## Quando usar cada
| Situação | Ferramenta |
|---|---|
| "O valor dessa variável tá certo?" durante desenvolvimento | `print` |
| Script roda 2 h em produção, falha às vezes | `logging.debug` persistente |
| "Quero navegar pelo estado, testar expressão" | `breakpoint()` |
| Script externo que você não quer editar | `python3 -m pdb script.py` |

## Exemplo pericial — debug de parser PJe
Scraper retorna lista vazia. Suspeita: seletor CSS mudou.

```python
def extrair_processos(html):
    soup = BeautifulSoup(html, "lxml")
    itens = soup.select("div.processo-item")
    log.debug("encontrou %d itens com seletor antigo", len(itens))
    if not itens:
        breakpoint()                # cai aqui só se vazio
    for item in itens:
        ...
```

No breakpoint, inspeciona `soup.prettify()[:2000]` para ver HTML real e descobrir o novo seletor.

## Armadilhas
- `print` commitado no repo é sinal de "não terminei". Remover antes de PR.
- `breakpoint()` no código de produção = travamento. Nunca deixar.
- `logging.basicConfig` só surte efeito se chamado **antes** do primeiro log. Chamar no topo do script.
