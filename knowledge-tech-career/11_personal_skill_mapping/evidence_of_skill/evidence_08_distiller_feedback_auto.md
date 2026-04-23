---
titulo: Destilador que clusteriza errors.jsonl e auto-gera feedback_*.md quando padrão recorre
tipo: evidencia
dominio: Python
subtopico: clustering leve + ETL JSONL -> Markdown
nivel_demonstrado: 2
versao: 0.1
status: validada
ultima_atualizacao: 2026-04-23
fonte: /Users/jesus/stemmia-forense/hooks/anti_mentira_distiller.py
---

## Descrição
Ferramenta standalone que lê `errors.jsonl` (alimentado pelo hook stop), normaliza mensagens (lowercase,
strip punctuation, trim), extrai assinatura por top-3 tokens, agrupa em buckets e — quando um bucket
ultrapassa THRESHOLD=3 ocorrências — gera um arquivo `feedback_{slug}.md` com template frontmatter
YAML + exemplos + instrução "antes de declarar sucesso, verificar com Bash/Read/Grep/Glob". É a
ponte entre detecção (hook) e aprendizado persistente (feedback na MEMORY).

## Arquivo real
`/Users/jesus/stemmia-forense/hooks/anti_mentira_distiller.py`

## Habilidade demonstrada
- `Python.sintaxe básica` — 2 (defaultdict, tuple signature, slug builder)
- `Agentes.avaliação (evals)` — 1 (closes loop mas sem métrica formal de precisão)
- `Dados saúde` — N/A
- `Python.pytest / testes` — 0

## Trecho relevante
```python
THRESHOLD = 3
MAX_SLUG_TOKENS = 3

FEEDBACK_TEMPLATE = """\
---
name: {name}
description: Padrão recorrente detectado pelo destilador anti-mentira: {signals}
type: feedback
---

Padrão detectado automaticamente após {count} ocorrências entre {first_date} e {last_date}.

**Sinais:** {signals}
**Exemplos do que o usuário disse:**
{examples}

**How to apply:** Antes de declarar sucesso, verificar com Bash/Read/Grep/Glob.
"""

def _signature(event: dict) -> tuple:
    signals = event.get("signals") or []
    if not signals:
        msg = event.get("user_message") or event.get("claim") or ""
        signals = _normalize(msg).split()[:MAX_SLUG_TOKENS]
    norm = [_normalize(s).split()[0] for s in signals if s and _normalize(s).split()]
    return tuple(sorted(set(norm))[:MAX_SLUG_TOKENS])
```

## Data
2026-04-17/19.

## Validação externa
**Média** — 4 feedbacks auto-gerados comprováveis na MEMORY (feito/pronto/rodando/concluído com counts 14/15/17/5).

## Limitações conhecidas
- Clustering é token-based trivial — 2 mensagens com mesma palavra-core diferente geram buckets separados.
- THRESHOLD=3 é hard-coded, sem config.
- Sem lógica de "esqueça" — feedback antigo nunca expira.
- Nunca passou por code review externo.
