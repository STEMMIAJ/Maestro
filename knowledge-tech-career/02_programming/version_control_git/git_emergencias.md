---
titulo: Git — emergências
bloco: 02_programming
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 5
---

# Git — emergências

Situações comuns e como sair. Ler tudo com calma antes de agir — comandos destrutivos só quando tiver certeza.

## "Apaguei sem querer / commit errado"

### `git reflog` — seu salva-vidas
Reflog registra **tudo** que HEAD apontou (commits, resets, checkouts) nas últimas semanas. Quase impossível perder trabalho que já foi commitado.

```bash
git reflog
# 78c931c HEAD@{0}: commit: ...
# 05efdba HEAD@{1}: reset: moving to HEAD~1
# ab12cd3 HEAD@{2}: commit: versao que eu achei que perdi
```

Recuperar: `git checkout ab12cd3` ou `git reset --hard ab12cd3`.

## "Mudei arquivo, quero voltar ao último commit"

### `git checkout -- arquivo.py`  (legado)
### `git restore arquivo.py`  (moderno)
Descarta mudanças **não staged** no working tree. **Irrecuperável** se não tiver commit.

```bash
git restore src/extrator.py        # desfaz mudanças locais
git restore .                       # desfaz tudo da pasta atual — CUIDADO
```

## "Fiz `git add` de algo errado"
```bash
git restore --staged arquivo.py    # tira do staging, mantém edição
```

## "Preciso pausar e voltar depois sem commitar"

### `git stash`
Guarda working tree + staging em pilha temporária, deixa tree limpa.

```bash
git stash                          # guarda
git stash push -m "wip monitor"    # com nome
git stash list                     # ver pilha
git stash pop                      # traz de volta o último
git stash apply stash@{1}          # aplica sem remover
git stash drop stash@{0}           # descarta
```

Uso pericial: estou no meio de reescrever scraper, juiz liga pedindo ajuste urgente em outro script. `git stash` → ajusta → commita → `git stash pop` → continua onde parou.

## "Commit com mensagem errada (só o último)"
```bash
git commit --amend -m "nova mensagem"
```

**Só use** se não deu push ainda. `--amend` reescreve commit → se já está no remote, gera divergência.

## "Quero desfazer o último commit"

### `git reset --soft HEAD~1` — desfaz commit, MANTÉM mudanças staged
Útil: commitei coisas demais, quero dividir em 2.

```bash
git reset --soft HEAD~1
# agora os arquivos estão staged, sem commit. Faça add -p + commit de novo.
```

### `git reset --mixed HEAD~1` (padrão) — mantém mudanças no working tree
```bash
git reset HEAD~1
# arquivos editados de volta à árvore, sem staging.
```

### `git reset --hard HEAD~1` — **DESTRUTIVO** — APAGA TUDO
> ⚠️ **CUIDADO** ⚠️
> Descarta commit + staging + working tree. Mudanças não commitadas somem.
> Mudanças commitadas ainda dá para achar via `reflog`, mas é susto grande.

```bash
git reset --hard HEAD~1
```

Use só quando tem certeza. **Nunca** em branch compartilhada após push.

## "Já fiz push do erro"

### `git revert`
Cria **novo commit** que desfaz o anterior. Não reescreve histórico — seguro em branch pública.

```bash
git revert <hash-do-commit-ruim>
```

Exemplo: commitei `.env` com chave. `git revert` **não resolve** — chave continua no histórico. Solução: `git filter-branch` ou [BFG Repo-Cleaner], **trocar a chave** e forçar push. Ver doc específica.

## "Conflito no merge / pull"
```bash
git pull origin main
# CONFLICT (content): Merge conflict in src/extrator.py
```

Abre o arquivo, procura marcadores:
```
<<<<<<< HEAD
minha versão
=======
versão do remote
>>>>>>> origin/main
```

Escolhe o que fica (ou mescla manual), remove os marcadores, salva.
```bash
git add src/extrator.py
git commit
```

Se quiser abortar o merge:
```bash
git merge --abort
git rebase --abort
```

## Regras de ouro
1. Antes de qualquer `reset --hard`, rodar `git status` e `git stash` para salvar lixo.
2. `git reflog` existe — trabalho commitado dificilmente se perde.
3. Nunca `push -f` em `main`. Em branch pessoal, ok.
4. Em dúvida: **não rodar**. Pergunte / leia.
