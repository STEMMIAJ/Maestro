# Maestro — RULES.md

Contrato de execução. Vale para Claude Code, sub-agentes, e para o próprio Dr. Jesus.
Ordem de precedência: RULES.md > WORKFLOW.md > pedido ad-hoc do usuário.
Exceção: usuário escreve `QUEBRAR-REGRA-N` na mensagem → regra N desativada só para aquela mensagem.

---

## R1 — Trabalho = Issue

Nenhum código sai do dedo sem issue aberta. Issue tem:
- Título imperativo curto (`Adicionar verificador X`)
- Descrição: problema, resultado esperado, arquivos que provavelmente mudam
- Label: `feat` | `fix` | `refactor` | `doc` | `blocker`

## R2 — Uma issue, um branch, um PR

- Branch: `tipo/NNN-slug` (ex: `feat/042-verificador-genero-juiz`)
- PR fecha issue com `Closes #NNN`
- Nunca trabalhar direto em `main`

## R3 — Commit é pequeno e auto-contido

- Uma mudança lógica por commit
- Mensagem: `tipo(escopo): imperativo curto` — máx 72 chars no título
- Corpo (opcional): o PORQUÊ, não o QUÊ

## R4 — Definition of Done

Ver `DEFINITION_OF_DONE.md`. Os 5 itens ou nada.

## R5 — Testes existem ou o código não existe

- Todo script novo tem ao menos 1 teste/verificação (pode ser `bash -n script.sh`, `python -c "import módulo"`, ou smoke test)
- Teste falhou → commit revertido, não "corrigido na próxima"

## R6 — Zero arquivo fora do repo

Tudo relacionado ao Maestro vive dentro de `Maestro/`. Handoffs ficam em `Maestro/HANDOFFS/`. Backups temporários em `Maestro/.tmp/` (gitignored).

## R7 — ADR antes de decisão grande

Framework novo, mudança de padrão, deletar módulo, mudar schema: escrever ADR primeiro, abrir PR só do ADR, mergear, DEPOIS implementar.

## R8 — Sem limpeza sem autorização

Proibido `rm`, `rm -rf`, renomeação em massa, "arrumar pastas". Usuário precisa escrever `LIMPAR-LIBERADO`.

## R9 — Claude decide ou para

Faltou contexto → parar e fazer 1 pergunta. Proibido: "vou assumir", "provavelmente é", "deve ser".

## R10 — Sessão termina com handoff

`HANDOFFS/HANDOFF-YYYY-MM-DD-HHhMM.md` com:
```
Issue: #N
Commits: [lista]
Estado: DONE | BLOCKED | PAUSED
Próximo passo: <1 linha executável>
```

## R11 — Push é obrigatório

Fim de sessão sem `git push` = sessão não encerrada. Se push falhar → vira issue `blocker`.

## R12 — Anti-mentira

Proibido dizer "feito", "pronto", "rodando", "concluído" sem output colado. Hooks de verificação do sistema aplicam.
