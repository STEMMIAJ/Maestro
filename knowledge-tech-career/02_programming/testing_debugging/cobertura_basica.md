---
titulo: Cobertura de testes — básico
bloco: 02_programming
tipo: tutorial
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: medio
tempo_leitura_min: 3
---

# Cobertura de testes — básico

Cobertura = porcentagem do código que é executado durante os testes. Mostra quais linhas nunca foram rodadas em nenhum teste.

Não mede qualidade do teste. Mede **alcance**. 100% cobertura pode ter 100% de teste ruim.

## Instalar
```bash
pip install coverage
# ou o plugin pytest
pip install pytest-cov
```

## Uso direto — `coverage`
```bash
coverage run -m pytest
coverage report
```

Saída típica:
```
Name                 Stmts   Miss  Cover
----------------------------------------
src/extratores.py       20      2    90%
src/parser_pje.py       45     30    33%
----------------------------------------
TOTAL                   65     32    50%
```

Lê: `parser_pje.py` tem 45 linhas, testes rodaram só 15. 30 nunca foram executadas.

## Ver quais linhas não foram cobertas
```bash
coverage report -m          # com "Missing"
coverage html               # gera htmlcov/ com relatório visual
open htmlcov/index.html     # só se permitido
```

HTML mostra código-fonte com linhas vermelhas (não cobertas) e verdes (cobertas).

## Uso via pytest — mais prático
```bash
pytest --cov=src --cov-report=term-missing
```

- `--cov=src` mede cobertura só da pasta `src/`.
- `--cov-report=term-missing` mostra linhas faltantes no terminal.
- `--cov-report=html` gera HTML.

## Quando vale a pena

### Vale
- Código crítico (parser de CNJ, extração de prontuário, cálculo de honorário).
- Biblioteca compartilhada que outros scripts dependem.
- Antes de refatorar — garantir que nada quebre.

### Não vale
- Script `util_rápido.py` que roda uma vez.
- Código de UI, integração com GUI.
- Projeto de exploração, prova de conceito descartável.

## Meta realista
- **80%** é bom.
- **100%** é suspeito — provavelmente inclui testes triviais só para o número.
- **<50%** em código crítico = risco alto.

## Ignorar código irrelevante
Em `.coveragerc`:
```ini
[run]
omit =
    */tests/*
    */__init__.py
    */migrations/*
```

## Regra pericial
Não obcecar com o número. Foco: **toda função que toma decisão** (if, regex, cálculo que vai para laudo) deve ter ao menos 1 teste. Cobertura alta é consequência, não objetivo.
