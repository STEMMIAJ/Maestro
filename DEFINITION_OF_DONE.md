# Maestro — Definition of Done

Uma tarefa **só** é "DONE" quando TODOS os 5 itens abaixo estão verdadeiros.
Zero flexibilidade. Zero "quase pronto".

---

## DOD-1 — Código commitado

```bash
git log --oneline <branch>
```
Mostra pelo menos 1 commit referenciando a issue (`#NNN` na mensagem ou no corpo).

## DOD-2 — Teste rodou e passou

Output do teste colado no PR. Exemplos válidos:
- `pytest tests/test_x.py -v` → `passed`
- `bash -n script.sh` → exit 0
- `python -c "import módulo; módulo.main()"` → sem traceback
- Smoke test manual com output textual

## DOD-3 — CHANGELOG atualizado

Linha nova em `CHANGELOG.md`:
```
- YYYY-MM-DD: [feat|fix|refactor|doc] descrição (#NNN)
```

## DOD-4 — Issue fechada

PR mergeado contém `Closes #NNN`. GitHub fecha automaticamente.

## DOD-5 — Push verde

```bash
git push
# → "Everything up-to-date" ou "...main -> main"
```
Workflow `enforce-dod.yml` no Actions = ✅ verde.

---

## Se algum item falhar

- **Não dizer "feito"**
- **Não encerrar sessão como DONE**
- Usar estado `BLOCKED` no handoff + descrever qual item falhou

## Por que essa rigidez?

Dr. Jesus tem TEA+TDAH. "Quase pronto" vira "nunca pronto" vira "sistema abandonado". Os 5 itens são o contrato que **externaliza** a definição de "terminado" — não depende de estado emocional, energia, cansaço.
