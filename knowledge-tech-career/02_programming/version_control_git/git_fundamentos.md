---
titulo: Git — fundamentos
bloco: 02_programming
tipo: conceito
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 7
---

# Git — fundamentos

Git = sistema de controle de versão distribuído. Guarda histórico de todas as alterações do projeto, permite voltar, ramificar e comparar.

## Repositório (repo)
Pasta com uma subpasta oculta `.git/` que guarda todo histórico. Criada com:
```bash
git init                           # inicializa repo na pasta atual
git clone https://github.com/x/y   # baixa repo existente
```

Por que importa: sem repo, cada arquivo só tem a versão atual. Com repo, existe o agora + todo o passado recuperável.

## Três áreas
Git trabalha com três níveis — entender isso é a base.

```
working tree  -->  index (staging)  -->  repo (commits)
  arquivos          git add              git commit
  editados
```

### Working tree (árvore de trabalho)
O que está no disco, visível no Finder. Arquivos editados/novos ficam aqui antes de entrar no Git.

### Index / staging
Antessala. Arquivos que você marcou para entrar no próximo commit. Entra via `git add`.

Por que existe: permite escolher quais mudanças commitar. Editei 10 arquivos mas quero commitar só 3 — stage só esses.

### Repo (histórico)
Pasta `.git/` com todos os commits. Cada commit é um snapshot completo do projeto num momento.

## Commit — o que é
Um commit é:
- Snapshot do projeto inteiro (todos os arquivos staged).
- Mensagem descrevendo a mudança.
- Hash único (ex.: `78c931c`).
- Ponteiro para commit anterior (forma a linha do tempo).

```bash
git commit -m "adiciona extrator de CNJ"
```

Regra pericial: commit pequeno, atômico, com mensagem que explica **por quê** (não só o quê). `"corrige bug de fuso horário em data de movimentação"` > `"update"`.

## Branch
Linha de desenvolvimento paralela. `main` é a branch padrão.

```bash
git branch                     # lista
git branch nova-feature        # cria
git checkout nova-feature      # troca para ela
git checkout -b nova-feature   # cria e troca (atalho)
```

Por que importa: testar mudança arriscada sem mexer na main. Se der errado, apaga a branch e nada muda na main.

Exemplo pericial: reescrever o scraper PJe — cria branch `refactor-scraper-pje`, trabalha lá, merge na main só quando funcionar.

## HEAD
Ponteiro para o commit atual (onde você está). Normalmente aponta para a ponta da branch atual.

```bash
git log --oneline
# * 78c931c (HEAD -> main) gitignore restritivo
# * 05efdba Git init para ultraplan funcionar
```

`HEAD~1` = commit anterior ao HEAD. `HEAD~3` = três atrás.

## Remote
Cópia do repo em outro lugar (normalmente GitHub/GitLab). Normalmente chamado `origin`.

```bash
git remote -v                              # lista remotes
git remote add origin https://github.com/...
git push origin main                       # envia commits para o remote
git pull origin main                       # puxa commits do remote
```

## Fluxo mental
1. Edita arquivo (working tree).
2. `git add <arquivo>` marca para commit (index).
3. `git commit -m "msg"` grava snapshot (repo).
4. `git push` envia para GitHub (remote).

Repetir essas 4 linhas resolve 90% do uso diário.

## Comandos de inspeção
```bash
git status           # o que mudou, o que está staged
git diff             # diff do working tree vs index
git diff --staged    # diff do index vs último commit
git log              # histórico completo
git log --oneline    # uma linha por commit
git show HEAD        # último commit (diff completo)
```

## Armadilhas de iniciante
- Esquecer `git add` antes do commit → commit vazio ou sem aquela mudança.
- Commitar `.env` com senha → senha no histórico público. Pânico. Ver `gitignore_e_segredos.md`.
- `git push -f` em branch compartilhada → reescreve histórico dos outros. Evitar.
- Trabalhar direto na main em projeto sério → sem rede de segurança. Branch → PR → merge é o padrão.
