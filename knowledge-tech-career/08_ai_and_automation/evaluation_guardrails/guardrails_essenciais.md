---
titulo: Guardrails essenciais
bloco: 08_ai_and_automation
tipo: receita
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: tecnico-consolidado
tempo_leitura_min: 4
---

# Guardrails essenciais

Guardrail = filtro determinístico entre o LLM e o mundo. Bloqueia ou corrige saída antes de virar efeito real. Três camadas no Dexter: antes do LLM (input), depois do LLM (output), entre agentes (middleware).

## 1. Validação de schema (structured output)

Forçar saída em JSON conforme JSON Schema. Tratar falha como erro explícito.

Claude aceita `response_format` parcial; OpenAI tem `response_format: json_schema` com validação estrita. Alternativa universal:

```python
import json, jsonschema

schema = {
  "type": "object",
  "required": ["cid", "data_inicio", "incapacidade"],
  "properties": {
    "cid": {"type": "string", "pattern": "^[A-Z]\\d{2}(\\.\\d)?$"},
    "data_inicio": {"type": "string", "format": "date"},
    "incapacidade": {"enum": ["total", "parcial", "nenhuma"]}
  }
}

saida = llm.call(prompt)
try:
    obj = json.loads(saida)
    jsonschema.validate(obj, schema)
except Exception as e:
    # reject, re-prompt ou fail
    ...
```

Para Python: `pydantic` resolve validação + parsing + type safety. `instructor` (lib) integra pydantic direto com LLM.

## 2. Regex / validators de domínio

Campos com formato fechado devem passar por regex ANTES de serem usados:

- **CID-10**: `^[A-Z]\d{2}(\.\d)?$` (ex.: `M54.5`).
- **CNJ**: `^\d{7}-\d{2}\.\d{4}\.\d{1,2}\.\d{2}\.\d{4}$`.
- **CPF**: além do formato, validar dígito verificador.
- **Data ISO**: `^\d{4}-\d{2}-\d{2}$`.
- **OAB**: `^OAB/[A-Z]{2}\s\d+$`.

Falha de regex = saída rejeitada, retry com mensagem de correção ou escala para humano.

## 3. Reject sampling

Se saída falha guardrail, disparar nova chamada com instrução de correção:

```
Tentativa 1 → saída inválida
Prompt retry: "Sua saída anterior tinha erro [X]. Corrija e devolva apenas o JSON válido."
Tentativa 2 → válida? aceitar. Inválida? retry ou fail.
Max 2 retries (CLAUDE.md: falhou 2x = mudar estratégia).
```

## 4. Groundedness check

Para cada claim na saída, verificar se há suporte no contexto:

- Extrair claims (sentenças afirmativas).
- Para cada claim, buscar evidência no contexto (NLI model ou LLM juiz com pergunta: "este trecho do contexto sustenta esta afirmação?").
- Claim sem suporte → marcar `[NAO_FUNDAMENTADO]` ou rejeitar.

Ferramentas: `factscore`, `SelfCheckGPT`, Anthropic citations API [TODO/RESEARCH].

## 5. Hooks anti-mentira (Dexter)

Já implementado. PreToolUse intercepta comando antes de executar. Bloqueia:

- `rm -rf`, `mv` para `/tmp` sem confirmação.
- Paths sensíveis (`_arquivo`, `BACKUP`, `RESERVA`).
- Claims de "feito" / "pronto" sem output de verificação.

Libera com flag explícita (`LIMPAR-LIBERADO`). Ver `reference_hook_anti_limpeza.md` e `reference_anti_mentira.md`.

## 6. Rate limiting / budget

Guardrail operacional:

- Teto de tokens por chamada (Anthropic aceita `max_tokens`).
- Teto de chamadas paralelas (rate limit na API).
- Teto de custo/dia em script orquestrador.
- Backoff exponencial em 429 (DataJud: padrão F1:216-222 no DATAJUD-GUIA.md).

## 7. Allowlist / blocklist de ferramentas

Agente só pode chamar ferramentas explicitamente listadas no frontmatter. Claude Code permite `tools:` em agent `.md`. Negar por padrão; permitir por exceção.

Para perícia: agente de triagem NUNCA deve poder escrever em `/Laudos/` — só ler.

## 8. Estrutura de saída com citações

Exigir no schema:

```json
{
  "conclusao": "...",
  "fontes": [
    {"id": "doc_42", "trecho_literal": "..."},
    {"id": "doc_17", "trecho_literal": "..."}
  ]
}
```

Guardrail posterior: cada `id` deve existir no contexto, e `trecho_literal` deve aparecer textualmente no doc. Se não aparece = alucinação = reject.

## 9. Output filter final

Antes de expor ao usuário ou gravar em arquivo, última varredura:

- Contém nome de paciente fora do contexto autorizado? (LGPD)
- Contém CPF/RG completo quando devia estar mascarado?
- Afirma algo sobre "responsabilidade civil" quando role é médico? (fora de competência)
- Contém disclaimer proibido ("não sou advogado", "consulte um profissional")? (ver CLAUDE.md)

## 10. Fail closed, não fail open

Se guardrail falha, default é rejeitar, não passar. Sistema médico-legal não tolera "deixa passar se der erro".

## Referências

- Anthropic, "Reducing hallucinations with Claude". [TODO/RESEARCH]
- Guardrails AI (lib Python). [TODO/RESEARCH]
- Pydantic AI docs.
