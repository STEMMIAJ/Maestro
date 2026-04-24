---
name: reference_anti_mentira
description: Sistema de hooks que bloqueia mentiras, captura frustração e destila erros recorrentes em memórias
type: reference
originSessionId: 08e70dc6-4073-4004-a8ee-afb6a9963bbf
---
# Sistema Anti-Mentira / Anti-Recusa / Anti-Condescendência

**Localização dos hooks:** `~/stemmia-forense/hooks/anti_mentira_*.py`
**Log de erros:** `~/.claude/projects/-Users-jesus/memory/errors.jsonl`
**Instalado em:** 17/abr/2026

## Hooks instalados

- **Stop** (`anti_mentira_stop.py`) — bloqueia término se assistant declarou "feito/funcionando/corrigido/pronto" sem rodar Bash/Read/Grep/Glob desde o último turno do usuário. Exit code 2 + mensagem em stderr.
- **UserPromptSubmit** (`anti_mentira_prompt_submit.py`) — detecta frustração do usuário (mentiu, insuportável, não funciona, recusou, imbecil etc), grava em log e injeta lembrete de regras no próximo turno.
- **SessionStart** (`anti_mentira_session_start.py`) — injeta últimos 3 erros não-resolvidos como contexto.

## Comandos úteis

**Destilar erros recorrentes em novas memórias** (rodar manualmente após algumas semanas):
```bash
python3 ~/stemmia-forense/hooks/anti_mentira_distiller.py \
  --log ~/.claude/projects/-Users-jesus/memory/errors.jsonl \
  --memory-dir ~/.claude/projects/-Users-jesus/memory
```

**Dry-run (ver o que seria criado sem escrever):**
```bash
python3 ~/stemmia-forense/hooks/anti_mentira_distiller.py \
  --log ~/.claude/projects/-Users-jesus/memory/errors.jsonl \
  --memory-dir ~/.claude/projects/-Users-jesus/memory \
  --dry-run
```

**Auditar últimos 7 dias de transcripts:**
```bash
python3 ~/stemmia-forense/hooks/anti_mentira_audit.py --days 7
```

**Inspecionar log:**
```bash
tail -20 ~/.claude/projects/-Users-jesus/memory/errors.jsonl | python3 -m json.tool --json-lines
```

**Marcar erro como resolvido manualmente:** editar `errors.jsonl` e adicionar `"resolved": true` na linha correspondente.

**Rodar suite de testes (após qualquer edição em `lib/`):**
```bash
cd ~/stemmia-forense/hooks && python3 -m pytest -v
```

## Schema do errors.jsonl

```json
{
  "ts": "2026-04-17T14:32:11Z",
  "kind": "frustration | unverified_claim | refusal | condescension",
  "user_message": "...",
  "context": "...",
  "session_id": "...",
  "resolved": false
}
```

## Tunning

- Adicionar/remover gatilhos de frustração: editar `FRUSTRATION_MARKERS` em `~/stemmia-forense/hooks/lib/guardrails.py`
- Adicionar tools que contam como verificação: editar `VERIFICATION_TOOLS` no mesmo arquivo
- Mudar threshold de destilação (default 3): editar constante `THRESHOLD` em `anti_mentira_distiller.py`

## Operação

- O destilador NÃO roda automaticamente. Manual de propósito: gerar memória nova é decisão que deve passar pelo seu olho. Sempre `--dry-run` primeiro.
- Se um hook quebrar, restaurar o backup `~/.claude/settings.json.bak-anti-mentira-*` ou comentar a entrada.
- O log cresce indefinidamente. Após ~6 meses ou 10000 linhas: `mv errors.jsonl errors-$(date +%Y%m).jsonl && touch errors.jsonl`.
