# Maestro/futuro — Parking lot de duvidas, decisoes e ideias

Pasta para **nao perder nada** durante fluxo intenso. Quando Dr. Jesus disser:

- "guarda na pasta futuro"
- "guarda isso pra depois"
- "anota esse problema"
- "tenho uma ideia"

A skill `guardar-futuro` roteia para o arquivo correto.

## Estrutura

| Arquivo | O que entra | Formato |
|---|---|---|
| `00-DUVIDAS.md` | Perguntas abertas, coisas que ainda nao sei responder | Lista com data + pergunta |
| `01-DECISOES-PENDENTES.md` | Decisoes que dependem do Dr. Jesus (escolher modelo/DB/nome) | Lista com data + decisao + opcoes |
| `02-IDEIAS.md` | Ideias soltas que surgem no meio do trabalho | Lista com data + ideia + contexto |
| `03-BACKLOG-TECNICO.md` | Tarefas tecnicas de implementacao futura | Lista com data + tarefa + prioridade |
| `04-CREDENCIAIS-PEDIR.md` | Lista do que preciso pedir ao Dr. Jesus (Telegram, FTP, APIs) | Lista com data + item + por que precisa |

## Regra
- Sempre com data no formato `YYYY-MM-DD`.
- Sempre com contexto de UMA linha (de onde veio).
- Nunca apagar — somente marcar `[RESOLVIDO YYYY-MM-DD]` no inicio da linha quando fechar.

## Retomada
- No inicio de sessao, leio `00-DUVIDAS.md` e `01-DECISOES-PENDENTES.md`.
- Se Dr. Jesus disser "o que ta travado?" → eu leio `01-DECISOES-PENDENTES.md`.
- Se disser "o que ta faltando fazer?" → eu leio `03-BACKLOG-TECNICO.md`.
