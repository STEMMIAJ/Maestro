# Como salvar no GitHub — passo a passo

> Regra mestra: **nenhum trabalho fica só no seu Mac**. Todo fim de sessão termina em `git push`.

## Quando salvar

| Situação | Ação |
|---|---|
| Terminou uma mudança lógica (ex: criou 1 arquivo novo) | commit imediato |
| Fechou uma issue (5 itens DONE) | commit + push |
| Vai fazer pausa de 15 min | commit + push |
| Fim de sessão (sempre, sem exceção) | handoff + commit + push |
| Antes de qualquer mudança arriscada | commit + push (backup) |
| Começou ideia mas não sabe se vai ficar | NÃO comitar ainda; deixar em "staging" |

**Regra de bolso:** se o trabalho já **funciona** ou é **um passo útil**, é hora de commitar. Não espere "terminar tudo".

## O fluxo padrão (você cola isto na conversa)

```
Salvar o que fizemos:
1. cd "/Users/jesus/Desktop/STEMMIA Dexter/Maestro"
2. git status — me mostrar o que mudou
3. git add -A — incluir tudo
4. git commit -m "tipo(escopo): descrição curta" — use o tipo certo: feat/fix/refactor/doc/chore
5. git push — enviar ao GitHub
6. Me confirmar o hash do commit e o link no GitHub
```

O Claude faz, mostra o resultado, você vê no GitHub.

## Como escrever a mensagem de commit

Formato obrigatório: `tipo(escopo): frase curta no imperativo`

| Tipo | Quando usar | Exemplo |
|---|---|---|
| `feat` | funcionalidade nova | `feat(peticao): gerar petição aceite para TJMG` |
| `fix` | corrigir bug | `fix(pje): tratar timeout de 2h na sessão` |
| `refactor` | melhorar código sem mudar comportamento | `refactor(cron): unificar 3 scripts de agendamento` |
| `doc` | documentação | `doc(github): adicionar guia de pull request` |
| `chore` | rotina (bootstrap, deps, config) | `chore(bootstrap): estrutura Maestro inicial` |
| `test` | testes | `test(datajud): cobrir caso de CNJ inválido` |

A regra é simples: **leia a mensagem sozinha 3 meses depois. Se você entender, tá boa.**

## Pull Request — quando trabalho sai da linha paralela e entra na principal

Linha principal = branch `main` (é a versão "oficial" do Maestro).

Se você ou o Claude está fazendo mudança grande (mais de 1 commit, ou mexendo em coisa crítica), NÃO comita direto em `main`. Usa uma **branch paralela**:

```
Claude, vou fazer algo grande. Cria uma branch feat/NNN-<slug>, faz as mudanças lá, quando terminar abre Pull Request pra main.
```

### O que acontece no PR

1. Claude cria branch `feat/042-novo-verificador`
2. Faz commits nessa branch
3. Abre PR: "quero juntar `feat/042-novo-verificador` em `main`"
4. GitHub Actions roda o porteiro `enforce-dod.yml` (5 verificações):
   - PR fecha alguma issue? (`Closes #N`)
   - CHANGELOG.md foi atualizado?
   - PR tem output de teste colado?
   - Todos os itens de DOD estão marcados?
   - Scripts `.sh` passam em `bash -n`?
5. **Se tudo verde:** merge liberado
6. **Se algo vermelho:** você vê no GitHub exatamente o que falta

Você aperta um botão (ou manda o Claude fazer) e pronto.

## Comando pra FECHAR uma sessão (SEMPRE)

Cola isto no fim de toda sessão:

```
Encerrar sessão do Maestro:
1. bash scripts/finalize.sh
2. Abrir o handoff que foi criado e preencher: Issue, Estado (DONE/BLOCKED/PAUSED), Próximo passo
3. git add HANDOFFS/HANDOFF-*.md
4. git commit -m "chore(handoff): sessão YYYY-MM-DD"
5. git push
6. Me mostrar o link do commit no GitHub
```

Se você esquecer de fazer isso — **o trabalho não se perde**. Fica como commit local. Basta rodar o comando na próxima vez.

## Duas coisas que NUNCA se fazem

1. **`git push --force` em main** — reescreve o histórico remoto. Seu hook `pre-push` bloqueia.
2. **`git reset --hard` sem entender** — joga fora mudanças locais. Não use. Se alguém sugerir, pare.

## Se você quiser salvar AGORA (sem Claude)

Terminal aberto, cola:

```bash
cd "/Users/jesus/Desktop/STEMMIA Dexter/Maestro"
git status
git add -A
git commit -m "chore: salvando progresso"
git push
```

Funciona. Você é o dono do repo.
