# Criterios de completude

## Princípio fundamental

**Afirmações sem evidência no filesystem são proibidas.** "Feito", "pronto", "concluído", "rodando" só podem ser ditos após verificação via `ls`, `grep`, `wc -l`, `cat` ou output de script.

## Tarefa

Uma tarefa só pode ser marcada como `concluida` em `TASKS_MASTER.md` se:

1. O artefato previsto existe no filesystem (arquivo, diretório ou linha específica).
2. Conteúdo não é placeholder vazio (`TODO` isolado, arquivo com 0 bytes, esqueleto sem corpo).
3. Evidência verificável disponível: comando que prova a existência + conteúdo mínimo.

```
# exemplo de evidência aceitável
$ ls -lh Maestro/memory/2026-04-22.md
-rw-r--r-- 1 jesus staff 4.2K Apr 22 18:30 Maestro/memory/2026-04-22.md
$ wc -l Maestro/memory/2026-04-22.md
87 Maestro/memory/2026-04-22.md
```

## Fase

Uma fase só encerra se:

1. Todas as tarefas estão `concluida` **OU** marcadas `parcial` / `bloqueada` com motivo registrado.
2. `TASKS_NOW.md` reflete estado real (não o estado planejado).
3. `CHANGELOG.md` atualizado com delta da fase.
4. `NEXT_SESSION_CONTEXT.md` atualizado com próxima ação mínima (1 frase imperativa).
5. Relatório de fase em `reports/` quando aplicável.

## Rodada

Uma rodada (ex: Rodada 1) só encerra com:

1. `reports/execution_report_roundN.md` listando: executado / planejado / pendente / bloqueado.
2. `logs/roundN_execution_log.md` com cronologia de ações.
3. `NEXT_SESSION_CONTEXT.md` com ação mínima da próxima sessão.
4. `%_panorama` calculado (não estimado) conforme fórmula de FLOW 04.

## Relatórios — distinção obrigatória

| status | definição | exemplo |
|--------|-----------|---------|
| **Executado** | feito + evidência | "arquivo X criado — `ls` confirma 87 linhas" |
| **Planejado** | definido, não iniciado | "script Y a criar no backlog B009" |
| **Pendente** | iniciado mas incompleto | "esqueleto existe, implementação faltando" |
| **Bloqueado** | impossível por dependência externa | "aguarda confirmação OpenClaw (Dr. Jesus)" |

## Flows e scripts

Um FLOW só pode ter status `operacional` se:
- Passos completos documentados.
- Pelo menos uma execução manual registrada em `logs/`.
- Saídas verificadas no filesystem.

Um script Python só pode ser declarado `implementado` se:
- `python3 script.py --help` executa sem erro.
- Pelo menos um smoke test manual rodado e logado.

<!-- atualizado em 2026-04-24 -->
