# Maestro — WORKFLOW.md

Fluxo de execução de TODA sessão. 13 passos. Sem pular.

---

## Passo 1 — Abrir sessão
```bash
cd ~/Desktop/STEMMIA\ Dexter/Maestro
bash scripts/status.sh
```
Output mostra: branch atual, último commit, issues abertas, PRs pendentes.

## Passo 2 — Escolher 1 issue
```bash
gh issue list --state open
```
Escolher UMA. Se não houver, encerrar sessão.

## Passo 3 — Criar branch
```bash
git checkout main && git pull
git checkout -b feat/NNN-slug
```

## Passo 4 — Ler contexto
Ler os arquivos do repo que a issue provavelmente afeta. Não abrir fora do repo.

## Passo 5 — ADR? (se decisão grande)
Se a tarefa mexe em arquitetura/schema/padrão → criar `DECISIONS/ADR-NNNN-titulo.md`, commitar, parar aqui e pedir revisão.

## Passo 6 — Implementar
Código em commits pequenos. Cada commit auto-contido.

## Passo 7 — Teste/verificação
Rodar teste. Colar output no terminal. Se vermelho → voltar ao Passo 6.

## Passo 8 — CHANGELOG
Adicionar linha em `CHANGELOG.md`:
```
- YYYY-MM-DD: [tipo] descrição curta (#NNN)
```

## Passo 9 — Commit final + push
```bash
git add -A
git commit -m "tipo(escopo): mensagem"
git push -u origin <branch>
```

## Passo 10 — Abrir PR
```bash
gh pr create --fill --body "Closes #NNN"
```

## Passo 11 — CI (Actions)
Esperar workflow `enforce-dod.yml` passar. Se falhar → voltar ao Passo 6.

## Passo 12 — Merge
```bash
gh pr merge --squash --delete-branch
```

## Passo 13 — Handoff
```bash
bash scripts/finalize.sh
```
Cria handoff automaticamente + lembra de `git push` final.

---

## Se travar

1. Criar issue nova com label `blocker`
2. Colar output do erro
3. Encerrar sessão (passo 13)
4. Próxima sessão começa destravando o blocker OU escolhendo outra issue
