# Glossário — toda palavra que você vai encontrar

> Ordem: alfabética. Releia quando esquecer — você vai esquecer, é normal.

## A

**ADR (Architecture Decision Record)**
Arquivo `.md` que registra uma decisão importante. Ex: "por que usamos GitHub em vez de Notion". Fica em `DECISIONS/`. Protege contra "a gente já discutiu isso" 3 meses depois.

**Actions (GitHub Actions)**
Robô do GitHub que roda automaticamente quando algo acontece no repo (ex: novo PR). No seu caso, roda `enforce-dod.yml` que verifica os 5 itens de Definition of Done.

## B

**Branch (linha paralela)**
Uma versão alternativa do código. Você cria uma pra experimentar sem mexer na principal. Se der certo, funde (merge). Se der errado, descarta.

**Blocker (issue bloqueadora)**
Problema que impede continuar o trabalho. Label `blocker` no GitHub. Prioridade máxima: enquanto existir, não se trabalha em outra coisa.

## C

**Commit (foto do estado)**
Foto imutável do estado dos arquivos naquele momento. Tem: hash (identificador), mensagem, autor, data. Nunca se apaga.

**CHANGELOG.md**
Arquivo que lista, em ordem cronológica, o que mudou em cada entrega. Uma linha por mudança.

**CHARTER.md**
Arquivo que descreve a missão do projeto em 1 página. Serve pra saber "o que o Maestro faz e NÃO faz".

**CLAUDE.md**
Arquivo de instruções pro agente Claude. Ele lê quando começa a trabalhar numa pasta.

## D

**Definition of Done (DOD)**
Os 5 critérios binários que tornam uma tarefa "terminada". Sem os 5, não está pronta. Nunca "quase pronta".

## F

**Fork**
Cópia de um repo pra você mexer à vontade. Você não precisa — só é relevante se alguém quiser contribuir.

## G

**gh (GitHub CLI)**
Ferramenta de linha de comando do GitHub. Permite criar issue, abrir PR, fazer merge, etc, direto do terminal. Já instalada no seu Mac.

**git**
Ferramenta que faz o versionamento (as "fotos"). Não depende da internet — funciona local.

**GitHub**
Site onde suas fotos (commits) ficam guardadas na nuvem. Backup remoto + lugar pra issues + Actions.

## H

**Hash**
Identificador único de um commit. Ex: `9b31de2`. Você usa pra referenciar uma foto específica.

**Handoff**
Arquivo em `HANDOFFS/` que fecha uma sessão. Diz: o que fiz, em que estado parei, qual o próximo passo.

**Hook (git hook)**
Script que o git roda automaticamente em momentos específicos. Seu Maestro tem 2:
- `pre-commit`: bloqueia commit direto em main, bloqueia commits com segredos
- `pre-push`: bloqueia force-push em main

## I

**Issue**
Uma unidade de trabalho no GitHub. Ex: "#1 Validar pipeline E2E". Tem título, descrição, label. Aberta ou fechada.

## L

**Label**
Etiqueta de uma issue/PR. Seus principais: `feat`, `fix`, `refactor`, `doc`, `blocker`.

## M

**Main (branch principal)**
A linha do tempo oficial. Tudo que está aqui é o "estado oficial" do sistema. Proibido commitar direto — sempre via PR.

**Merge**
Juntar uma branch paralela de volta em main. Com `--squash`, os vários commits da branch viram 1 só em main (mais limpo).

## O

**Origin**
Apelido pro repo remoto (GitHub). Quando você faz `git push origin main`, está dizendo "empurre para o GitHub, na linha main".

## P

**PR (Pull Request)**
Pedido pra juntar uma branch em main. "Por favor, revise e aceite estas mudanças." O porteiro (Actions) revisa primeiro.

**Push**
Enviar commits locais para o GitHub.

**Pull**
Baixar commits do GitHub pro seu Mac. Útil quando você trabalha em outro computador ou outro agente mudou algo.

## R

**Remote (repo remoto)**
O repo no GitHub. Oposto do "local" (no seu Mac). Seu remote se chama `origin` e aponta pra `https://github.com/STEMMIAJ/Maestro.git`.

**Repo (repository)**
O projeto inteiro versionado. Seu repo principal é `Maestro`.

**Rebase**
Reordenar commits de uma branch em cima de outra. Avançado — o Claude cuida disso quando precisa.

**Revert**
Desfazer um commit criando um NOVO commit que anula. Git nunca apaga — sempre acrescenta.

## S

**Status (git status)**
Mostra o que mudou desde a última foto. É o comando que você roda quando está perdido.

**Stage / Staging**
"Área de montagem" — mudanças que estão preparadas pra entrar no próximo commit. `git add` põe lá. `git commit` transforma em foto.

**Squash**
Juntar vários commits em um só. Usado no merge de PR pra manter main limpa.

## T

**Tag**
Etiqueta com nome em um commit específico (ex: `v1.0`). Útil pra marcar versões importantes.

## W

**Working tree (árvore de trabalho)**
Os arquivos "vivos" que você vê na pasta. Diferente do que está em commit (histórico) ou staging (preparado).

**Workflow (arquivo `.github/workflows/*.yml`)**
Configuração do que GitHub Actions deve rodar. Seu Maestro tem `enforce-dod.yml`.

---

## Comandos mais usados (cola de parede)

| Comando | O que faz |
|---|---|
| `git status` | ver o que mudou |
| `git add -A` | preparar tudo pro próximo commit |
| `git commit -m "mensagem"` | bater a foto |
| `git push` | enviar ao GitHub |
| `git pull` | baixar do GitHub |
| `git log --oneline -10` | ver últimos 10 commits |
| `git diff` | ver linhas que mudaram |
| `gh issue list --state open` | listar tarefas abertas |
| `gh issue create --title "X"` | criar tarefa nova |
| `gh pr create --fill` | abrir Pull Request |
| `gh pr merge --squash` | aceitar e mergear um PR |

Esses 11 comandos cobrem 95% do que você vai fazer.
