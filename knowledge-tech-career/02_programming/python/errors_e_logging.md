---
titulo: Erros e logging em Python
bloco: 02_programming
tipo: tutorial
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 6
---

# Erros e logging

## `try / except`
Captura erro sem parar o programa.

```python
try:
    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()
except requests.Timeout:
    log.warning("timeout — tentar depois")
except requests.HTTPError as e:
    log.error("HTTP %s em %s", e.response.status_code, url)
except Exception as e:
    log.exception("erro inesperado")   # inclui traceback completo
    raise                               # re-levanta — nao engolir erro
```

Regras:
- Capturar exceção **específica**, não `Exception` genérico no bloco principal.
- Nunca `except: pass` — esconder erro dá bug fantasma depois.
- Se não sabe tratar, **re-levanta** com `raise`.

## `raise` — lançar erro próprio
```python
def extrair_cnj(texto: str) -> str:
    import re
    m = re.search(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", texto)
    if not m:
        raise ValueError(f"CNJ nao encontrado em: {texto[:80]}")
    return m.group(0)
```

## `logging` — substitui `print`
`print` não tem nível, não tem timestamp, não tem filtro. Em produção, usar `logging`.

### Níveis
| Nível | Quando |
|---|---|
| `DEBUG` | Diagnóstico detalhado (variáveis, fluxo) |
| `INFO` | Marco de execução ("baixado processo X") |
| `WARNING` | Algo estranho mas seguiu (retry, arquivo faltando) |
| `ERROR` | Falha numa operação (download não concluiu) |
| `CRITICAL` | Sistema não pode continuar |

### Setup mínimo
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("monitor.log", encoding="utf-8"),
        logging.StreamHandler(),   # também no terminal
    ],
)
log = logging.getLogger(__name__)
```

### Uso
```python
log.info("iniciando download de %s processos", len(lista))
log.debug("payload: %s", payload)
log.warning("tentativa %d falhou, backoff %ds", tent, espera)
log.error("nao foi possivel baixar %s", url)
log.exception("erro inesperado")   # dentro de except — inclui traceback
```

Usar `%s` e passar argumentos depois (preguiçoso). `log.info(f"{x}")` funciona, mas formata mesmo quando o nível está desligado — mais lento.

## Por que não `print` em script sério
- Não dá para desligar sem editar código.
- Não tem timestamp → impossível debugar "quando foi".
- Mistura-se com saída útil do programa.
- Não grava em arquivo automaticamente.

`logging` resolve tudo isso com 3 linhas de setup.

## Padrão pericial
Todo script de longa duração (monitor, scraper) deve:
1. Logar em `logs/<script>-<data>.log`.
2. `INFO` para marcos (início, fim, contagem).
3. `ERROR` com exceção no `except`.
4. Rotacionar log (ver `logging.handlers.RotatingFileHandler`) se passar de ~10 MB.
