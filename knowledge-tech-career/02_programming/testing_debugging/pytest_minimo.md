---
titulo: Pytest mínimo
bloco: 02_programming
tipo: tutorial
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 7
---

# Pytest mínimo

`pytest` = framework de teste Python. Descobre automaticamente funções `test_*` e roda.

Por que testar: script pericial que extrai CNJ — se uma regex muda e quebra silenciosamente, laudos saem com número errado. Teste detecta antes de chegar no juiz.

## Instalação
```bash
pip install pytest
```

## Convenção de arquivos
- Arquivos: `test_*.py` ou `*_test.py`.
- Funções: `def test_algo():`.
- Classes: `class TestAlgo:` com métodos `def test_*`.

Estrutura pericial típica:
```
projeto/
  src/
    extratores.py
  tests/
    test_extratores.py
```

## Exemplo — validar função de extração de CNJ
`src/extratores.py`:
```python
import re

CNJ_REGEX = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")

def extrair_cnj(texto: str) -> str | None:
    m = CNJ_REGEX.search(texto)
    return m.group(0) if m else None
```

`tests/test_extratores.py`:
```python
from src.extratores import extrair_cnj

def test_extrai_cnj_simples():
    texto = "Processo 0001234-56.2025.8.13.0024 distribuido."
    assert extrair_cnj(texto) == "0001234-56.2025.8.13.0024"

def test_retorna_none_se_sem_cnj():
    assert extrair_cnj("sem numero aqui") is None

def test_pega_primeiro_cnj_quando_ha_varios():
    texto = "Processos 0001234-56.2025.8.13.0024 e 0009999-99.2025.8.13.0024"
    assert extrair_cnj(texto) == "0001234-56.2025.8.13.0024"
```

Rodar:
```bash
pytest                    # descobre e roda tudo
pytest tests/             # só pasta tests
pytest -v                 # verbose (mostra cada teste)
pytest -k "cnj"           # só testes com "cnj" no nome
pytest --tb=short         # traceback curto
```

## `assert` — a única afirmação que precisa
Pytest reescreve `assert` para mostrar valores na falha.
```python
assert soma(2, 3) == 5
assert "erro" not in log
assert len(lista) > 0
assert resultado is None
```

Sem biblioteca especial, sem `assertEqual`. Só `assert`.

## Fixture — preparar estado para o teste
Fixture é função marcada com `@pytest.fixture` que prepara algo usado pelos testes (arquivo temporário, banco, mock de API).

```python
import pytest
from pathlib import Path
import json

@pytest.fixture
def ficha_exemplo(tmp_path):
    """Cria FICHA.json temporária para o teste."""
    ficha = tmp_path / "FICHA.json"
    ficha.write_text(json.dumps({"cnj": "0001-2024", "autor": "João"}))
    return ficha

def test_ler_ficha(ficha_exemplo):
    dados = json.loads(ficha_exemplo.read_text())
    assert dados["cnj"] == "0001-2024"
```

`tmp_path` é fixture built-in do pytest: pasta temporária única por teste, apagada no fim.

Por que importa: teste não deve depender de arquivo no seu disco que só existe na sua máquina.

## `parametrize` — rodar o mesmo teste com vários inputs
```python
import pytest
from src.extratores import extrair_cnj

@pytest.mark.parametrize("texto,esperado", [
    ("Processo 0001234-56.2025.8.13.0024.", "0001234-56.2025.8.13.0024"),
    ("Numero: 9999999-99.2024.8.26.0100 Apelacao", "9999999-99.2024.8.26.0100"),
    ("Sem CNJ aqui", None),
    ("", None),
])
def test_extrair_cnj(texto, esperado):
    assert extrair_cnj(texto) == esperado
```

Pytest roda 4 testes — um por tupla. Se um falha, só esse é reportado.

Por que importa: cobre muitos casos sem duplicar código. Em validação de regex/parser, `parametrize` é obrigatório.

## Marcar teste esperado a falhar / lento
```python
@pytest.mark.skip(reason="endpoint mudou, pendente")
def test_antigo(): ...

@pytest.mark.slow
def test_baixa_tudo(): ...
```

Rodar só rápidos: `pytest -m "not slow"`.

## Cobertura rápida
Ver `cobertura_basica.md`.

## Regra pericial
- Toda função que extrai dado crítico (CNJ, CPF, CID, data) → teste `parametrize` com 5–10 casos reais.
- Bug encontrado em produção → primeiro criar teste que reproduz, depois corrigir. Garante que não volta.
