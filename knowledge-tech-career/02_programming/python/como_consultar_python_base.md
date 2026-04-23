---
id: como_consultar_python_base
title: Como consultar a PYTHON-BASE antes de escrever ou corrigir script
status: EXECUTADO
bloco: 02_programming/python
regra_vinculante: CLAUDE.md global (seção PYTHON DE AUTOMAÇÃO)
aplica_quando: browser, CDP, scraping, download, ETL, integração, launchd
data_criacao: 2026-04-23
tags: [python, workflow, consulta, falhas, templates]
---

# Como consultar a PYTHON-BASE antes de escrever ou corrigir script

Sequência obrigatória de 4 passos. Se pular qualquer um e uma falha já catalogada voltar a acontecer, é retrabalho não justificado.

## 1. Grep no índice consultável

Descobrir se padrão/arquivo já existe.

```bash
grep -i "playwright.*download" "/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/_INDICE-CONSULTAVEL.md"
grep -i "telegram" "/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/_INDICE-CONSULTAVEL.md"
```

Se encontrar linha relevante, ir direto ao arquivo citado em `08-SISTEMAS-COMPLETOS/` ou `06-TEMPLATES/`.

## 2. Busca em falhas.json

Filtrar por tecnologia, categoria ou texto livre no sintoma.

```bash
FALHAS="/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json"

# Por tecnologia
jq '.[] | select(.tecnologia=="playwright") | {id, sintoma, solucao}' "$FALHAS"

# Por sintoma (busca parcial, case-insensitive)
jq '.[] | select(.sintoma | test("timeout"; "i")) | {id, sintoma}' "$FALHAS"

# Por tag PJe
jq '.[] | select(.tags | index("pje")) | {id, categoria, sintoma}' "$FALHAS"

# Apenas bloqueadores
jq '.[] | select(.severidade=="bloqueador") | {id, tecnologia, sintoma}' "$FALHAS"

# Por ID específico
jq '.[] | select(.id=="PW-012")' "$FALHAS"
```

**Regra:** para cada IDs citado ou relevante ao caso, adicionar comentário no código gerado.

```python
# ref: PW-012  (storage_state persistente)
# ref: PJE-002 (renovar sessão PJe a cada 20 min)
async with async_playwright() as pw:
    ...
```

## 3. Conferir template disponível

```bash
ls "/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/06-TEMPLATES/"
```

Templates atuais (ver `python_base_templates.md`): CLI Typer, async-httpx-retry, Telegram, webhook FastAPI, ETL CSV→SQLite, PDF extract, path helper Mac/Windows.

Se existir template próximo do caso → copiar e adaptar. Não reescrever do zero.

## 4. Conferir sistema completo análogo

```bash
ls "/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/"
```

Se for scraping TJMG → ver `guia-tjmg-scraper/scraper.py`.
Se for ETL de conversas → ver `conversation_ingestion/`.
Se for monitor de fontes → ver `monitor-processos-novo-2026-04-22/`.

## 5. Registrar falha nova

Se durante execução uma falha NÃO catalogada ocorrer, registrar imediatamente:

```bash
# Editar
$EDITOR "/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/casos-reais/REGISTRO.md"
```

Formato (copiar do topo do REGISTRO.md):

```markdown
## YYYY-MM-DD — [tecnologia] [sintoma curto]
- **Script:** caminho absoluto
- **Sintoma:** cola do terminal
- **Causa raiz:** 1 frase
- **Fix:** 1 frase
- **Virou entrada em falhas.json?** sim (ID) / não
```

A cada 10 casos reais → destilar em `db/falhas.json` (nova entrada com ID sequencial, ex: `HTTPX-001`).

## Atalhos úteis

```bash
# Abrir índice principal
open "/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/_INDICE-CONSULTAVEL.md"

# Abrir base de falhas
open "/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/"

# Ver distribuição de falhas
cat "/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/INDEX.md"
```

## Checklist rápido antes de entregar script

- [ ] Cabeçalho docstring com `Uso:` e deps.
- [ ] Todos os IDs relevantes de `falhas.json` citados como comentário.
- [ ] Template reusado sempre que possível (listar qual na docstring).
- [ ] Logging estruturado (padrão de `01-FUNDAMENTOS/logging-estruturado.md`).
- [ ] Cross-platform se aplicável (ver `mac-windows-path-helper.py`).
- [ ] Se nova falha → REGISTRO.md atualizado no mesmo commit.
