---
titulo: Manual de Sobrevivência Git
tipo: master_summary
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
---

# Manual de Sobrevivência Git

## O que é Git

Git é um sistema que tira **fotos** do projeto ao longo do tempo e permite voltar a qualquer foto. Cada foto é um commit. Analogia útil: é um "salvar como" estruturado, com histórico infinito e capacidade de comparar versões. Não é backup automático — exige disciplina humana de fotografar.

## Vocabulário mínimo

### commit
- A foto do projeto em um instante, com mensagem descrevendo o que mudou.
- Mora no seu computador até você fazer push.
- Exemplo: `git commit -m "adiciona script de download PJe"`

### push
- Envia os commits locais para o servidor remoto (GitHub, GitLab).
- Sem push, o código só existe na sua máquina.
- Exemplo: `git push`

### pull
- Baixa do remoto o que mudou e junta com o local.
- Use antes de começar a trabalhar.
- Exemplo: `git pull`

### branch
- Linha paralela de desenvolvimento. `main` é a linha principal.
- Branches servem para experimentar sem quebrar o principal.
- Exemplo: `git checkout -b experimento-novo-laudo`

### status
- Mostra o estado atual: o que mudou, o que está pronto para commit.
- Comando que mais se usa. Rode sempre que não souber onde está.
- Exemplo: `git status`

### log
- Lista os commits anteriores, do mais novo para o mais antigo.
- Exemplo: `git log --oneline -20`

### diff
- Mostra exatamente o que mudou em relação ao último commit.
- Exemplo: `git diff`

### add
- Marca arquivos para entrar no próximo commit (staging).
- Exemplo: `git add arquivo.py` ou `git add .` (tudo).

## Rotina mínima de sobrevivência

```
git status
git add .
git commit -m "mensagem curta do que mudou"
git push
```

Quatro comandos. Essa é a rotina. Decorar.

## Por que commit cedo e frequente

1. **Reversão barata** — se o próximo passo quebrar, volta para o commit de 10 minutos atrás, não para o de ontem.
2. **Memória externa** — mensagem de commit é diário técnico. Autista/TDAH recupera contexto melhor lendo commits do que tentando lembrar.
3. **Pressão psicológica baixa** — sessões curtas com commit no final rendem mais que sessões longas com "vou commitar depois".
4. **Prova de trabalho** — histórico é portfólio.

Regra prática: **commit a cada unidade lógica concluída** (função nova, bug corrigido, parágrafo de doc, config ajustada). Não espere "terminar o dia".

## Como recuperar trabalho

### Voltar arquivo a como estava no último commit
```
git checkout -- arquivo.py
```
Perde alteração não commitada desse arquivo. Não desfaz commit.

### Guardar alteração sem commitar (stash)
```
git stash                 # guarda
git stash pop             # devolve
git stash list            # lista guardados
```
Útil quando precisa trocar de branch rápido.

### Ver tudo que já aconteceu (reflog)
```
git reflog
```
Lista **todas** as ações (commit, checkout, reset, merge). Salva-vidas quando parece que "sumiu tudo". Nada some realmente no Git por 90 dias.

### Voltar a um commit anterior sem perder histórico
```
git revert <hash>
```
Cria commit novo que desfaz o antigo. Seguro em branch compartilhado.

### Voltar a um commit anterior reescrevendo histórico
```
git reset --hard <hash>
```
Destrutivo. **Só em branch local, nunca em branch que já foi empurrado com colega.**

## O que NÃO fazer

- `rm -rf .git` — apaga todo o histórico do repositório. Sem volta.
- `git push --force` em `main` — reescreve histórico do servidor. Quebra trabalho de quem sincronizou.
- Commit de `.env`, senha, chave de API, token, certificado. Use `.gitignore`.
- Commit de arquivo gigante (PDF de 500 MB, vídeo, base de dado bruta). Git infla e fica lento. Use Git LFS ou armazenamento separado.
- Mensagem "ajustes", "fix", "wip" repetida. Em 3 meses ninguém sabe o que foi.
- Trabalhar direto em `main` em repositório com mais gente. Use branch.

## Adaptação para perfil neurodivergente (TEA + TDAH)

### Apelidar mentalmente
- Commit = "foto do projeto".
- Branch = "sala de experimento, tranca a porta".
- Stash = "gaveta temporária".
- Reflog = "câmera de segurança, grava tudo por 90 dias".

### Passos curtos, checklists externos
Cola na parede do escritório:

```
[ ] git status
[ ] git add .
[ ] git commit -m "___________"
[ ] git push
```

### Checkpoint de fim de sessão (obrigatório)
Antes de fechar editor:
1. `git status` — algum arquivo não salvo?
2. `git add . && git commit -m "checkpoint fim sessão AAAA-MM-DD"`
3. `git push`
4. Registrar em `CHANGELOG.md` ou `15_memory/checkpoints/`.

Sem isso, sessão seguinte começa no escuro. Ver `session_loss_prevention.md`.

### Mensagem de commit em 3 partes

```
<verbo> <o quê>

<por que / contexto se precisar>
<referência a issue/processo>
```

Exemplos:
- `adiciona download automático PJe 139` — verbo + objeto.
- `corrige timeout no datajud_client (ref F1:216)` — com referência.

### Tolerância a erro
Errou o commit? `git commit --amend` arruma a última mensagem (antes do push). Errou depois do push em branch pessoal: `git push --force-with-lease` (menos destrutivo que `--force`).

## Comandos de emergência

| Situação | Comando |
|---|---|
| "Apaguei o arquivo!" | `git checkout HEAD -- arquivo` |
| "Commitei lixo!" | `git reset HEAD~1` (mantém mudança, desfaz commit) |
| "Não sei onde estou" | `git status` e `git log --oneline -10` |
| "Perdi meu trabalho" | `git reflog` e ache o hash |
| "Conflito ao fazer pull" | Abre arquivo, procura `<<<<<<<`, resolve, `git add`, `git commit` |

## Ver também

- `session_loss_prevention.md` — Git como uma das 5 camadas.
