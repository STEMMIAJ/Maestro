---
titulo: Hook Stop que bloqueia término da sessão se detectar "feito/pronto" sem verificação
tipo: evidencia
dominio: Agentes
subtopico: hooks Claude Code + enforcement
nivel_demonstrado: 3
versao: 0.1
status: validada
ultima_atualizacao: 2026-04-23
fonte: /Users/jesus/stemmia-forense/hooks/anti_mentira_stop.py
---

## Descrição
Hook `Stop` do Claude Code que lê o transcript da sessão, extrai o último turno do assistant, checa
tools usadas desde o último prompt do usuário e — se o assistant afirmou sucesso
("feito"/"pronto"/"rodando"/"concluído") SEM ter chamado Bash/Read/Grep/Glob para verificar — registra
em `errors.jsonl` e retorna exit code 2 (bloqueia encerramento). Integra com destilador que depois
clusteriza os registros e gera `feedback_*.md` automaticamente.

## Arquivo real
`/Users/jesus/stemmia-forense/hooks/anti_mentira_stop.py` (symlink para
`/Users/jesus/Desktop/STEMMIA Dexter/src/hooks/anti_mentira_stop.py`)

## Habilidade demonstrada
- `Agentes.arquitetura multi-agente` — 3 (hook + distiller + session_start = pipeline)
- `Prompt eng.` — 3 (feedback loop automático altera comportamento da próxima sessão)
- `Python.sintaxe básica` — 2
- `InfoSec.LGPD aplicada` — 2 (log local, não sai do disco)

## Trecho relevante
```python
def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    transcript_path = payload.get("transcript_path")
    messages = load_messages(Path(transcript_path))
    text = last_assistant_text(messages)
    tools = tools_used_since_last_user(messages)

    finding = detect_unverified_claim(text, tools)
    if not finding:
        return 0

    log_append({
        "ts": datetime.now(timezone.utc).isoformat(),
        "kind": "unverified_claim",
        "claim": finding["claim"],
        "context": text[:1000],
        "tools_used": tools,
        ...
    }, log_path)

    sys.stderr.write(
        f"BLOQUEADO: você declarou '{finding['claim']}' sem verificar. "
        f"Rode Bash/Read/Grep/Glob para confirmar antes de finalizar.\n"
    )
    return 2
```

## Data
2026-04-17 (ver `reference_anti_mentira.md` na MEMORY).

## Validação externa
**Forte** — em produção há >5 dias. Gerou pelo menos 4 feedbacks auto-destilados (`feedback_feito.md`,
`feedback_pronto.md`, `feedback_rodando.md`, `feedback_concluído.md`) com contadores reais (14, 15, 17, 5 ocorrências).

## Limitações conhecidas
- Heurística de "claim não verificado" é regex de palavras-chave; tem falsos-positivos quando usuário pergunta "está feito?".
- Só bloqueia no `Stop`; não intercepta no meio da resposta.
- Depende de `lib/guardrails.py` — sem teste unitário direto.
