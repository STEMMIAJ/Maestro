# FLUXO 07 — Memória e GitHub

## Aviso

Este arquivo é **só observação**. Não mexer em Git/GitHub agora. O objetivo é entender o que está indo pro repo sem controle e deixar isso documentado para auditoria futura.

## Como está sendo usado hoje

1. Dr. Jesus às vezes diz algo como "salva no github" ou "commita isso".
2. Existe um **hook automático** (não totalmente mapeado) que empurra arquivos da pasta `conversations/` para o branch `main` do repo `STEMMIAJ/Maestro`.
3. O resultado aparece em `https://github.com/STEMMIAJ/Maestro/blob/main/conversations/YYYY-MM-DD-HHhMM-sessao.md`.

## Repos conhecidos

| Repo | Uso | Risco |
|---|---|---|
| `STEMMIAJ/Maestro` | Principal. Scripts, templates, docs. | Possíveis segredos hardcoded em scripts (Telegram BOT_TOKEN, ML CLIENT_SECRET identificados na auditoria 69 scripts — PR #10) |
| `STEMMIAJ/Dexter` (?) | A confirmar | A auditar |

## Branches pendentes no Maestro

| Branch | Estado | Origem |
|---|---|---|
| `main` | Bootstrap + `conversations/` automático | Ativo |
| `dexter-jurisprudencia` | **Tem os 1378 arquivos reais**. Divergente do `main`. | Agente anterior |
| `feat/003-openclaw-daemon` | Contaminada — commit de petições caiu aqui por erro (commit `e516dbb`) | Agente B colidiu com C em 24/abr |
| `doc/008-peticoes-catalogo` | Em aberto | Agente anterior |

## Hooks que empurram pro repo

| Hook | Origem | O que empurra | Controle do Dr. Jesus? |
|---|---|---|---|
| `salva-conversations-github` (nome provável) | `.claude/hooks/` ou `stemmia-forense/hooks/` | Sessão `.md` em `conversations/` | NÃO — automático |
| PreCompact `salvar-contexto-bruto.sh` | `$HOME/stemmia-forense/hooks/` | Gera síntese pré-compact | Local, não vai pro GitHub |
| PreCompact `gerar-sintese-precompact.sh` | idem | Síntese MD pré-compact | Local |

## Pastas que parecem estar indo para o GitHub

1. `Maestro/src/` (scripts Python) — provável.
2. `Maestro/docs/` — provável.
3. `Maestro/conversations/` — **confirmado** via hook automático.
4. `Maestro/peticoes/` — indo pela branch errada.
5. `Maestro/.claude/plans/` — parcial.

## Dúvidas (anotar, não resolver agora)

1. **Qual é o remote `origin`?** Provável `https://github.com/STEMMIAJ/Maestro.git`. Confirmar sem mexer.
2. **O repo é público ou privado?** Crítico porque scripts têm segredos. **PROVÁVEL PÚBLICO** — a confirmar.
3. **`.gitignore` está bloqueando FICHA.json com CPF de autor real?** Não confirmado.
4. **Existe GitHub Actions rodando automaticamente?** Desconhecido.
5. **Tokens expostos em conversations/**? Provável sim — há menções a chat_id Telegram.
6. **Branch `main` recebe pushes diretos ou tem branch protection?** Desconhecido.
7. **Quem autenticou o Git localmente?** SSH? PAT? Token vencido?

## Memória (sistema local, não GitHub)

1. **MEMORY.md** do Claude Code em `/Users/jesus/.claude/projects/-Users-jesus/memory/MEMORY.md` — já é persistente local.
2. **CLAUDE.md** global em `/Users/jesus/.claude/CLAUDE.md` — regras de comportamento.
3. **Diários** em `~/Desktop/DIARIO-PROJETOS.md` e `~/Desktop/STEMMIA — SISTEMA COMPLETO/DIARIO-DO-SISTEMA.md`.
4. **Handoffs de sessão** em `~/Desktop/_MESA/40-CLAUDE/handoffs/`.
5. **Registros de sessão** em `~/Desktop/Projetos - Plan Mode/Registros Sessões/`.

Nenhum desses vai para o GitHub automaticamente.

## O que precisa ser decidido (em outra tarefa)

1. Revogar e rotacionar tokens expostos (Telegram BOT_TOKEN, Mercado Livre CLIENT_SECRET).
2. Adicionar `.gitignore` para `FICHA.json` com CPF real (se o repo for público).
3. Decidir: repo público com dados anonimizados ou repo privado com dados reais?
4. Resolver branches órfãs (`feat/003-openclaw-daemon`, `doc/008-peticoes-catalogo`).
5. Reverter commit `e516dbb` da branch errada.
6. Mergear o real (`dexter-jurisprudencia`) no `main` ou inverso.
7. Documentar o que o hook "salva no github" faz exatamente.

## Hoje

**Só observar, não mexer.** Quando Dr. Jesus marcar `FLUXO-07` como URGENTE no mapa, aí a gente abre isso como tarefa dedicada.
