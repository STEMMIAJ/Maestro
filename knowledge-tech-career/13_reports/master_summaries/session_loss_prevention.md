---
titulo: Prevenção de Perda de Sessão
tipo: master_summary
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
---

# Prevenção de Perda de Sessão

## Premissa

Perda de sessão = qualquer situação em que trabalho já feito some, ou em que a próxima sessão começa sem saber o que a anterior fez. Causas típicas: editor não salvo, commit não feito, push não feito, Time Machine desligado, memória Markdown não atualizada, contexto de chat compactado sem resumo.

Para perfil com memória comprometida (TEA + TDAH), **redundância não é paranoia, é requisito funcional.** A regra: ao menos 3 das 5 camadas abaixo ativas por padrão, 4-5 em trabalho crítico.

## As 5 camadas de proteção

### Camada 1 — Salvar no editor
- Autosave ligado (VS Code: `"files.autoSave": "afterDelay"`).
- Cmd+S como reflexo motor a cada 2-3 minutos, mesmo com autosave.
- Nunca deixar editor fechar sem salvar todos os abertos.

### Camada 2 — Commit local
- `git commit` a cada unidade lógica concluída.
- Mensagem descritiva (ver `git_survival_manual.md`).
- Proteção contra: editor corrompe, arquivo sobrescrito, erro destrutivo.

### Camada 3 — Push remoto
- `git push` ao menos no fim de cada sessão.
- Em trabalho crítico: push a cada 3-4 commits.
- Proteção contra: HD falha, MacBook roubado, pasta apagada.

### Camada 4 — Backup de sistema (Time Machine)
- Time Machine **sempre ligado**, disco externo conectado.
- Histórico de incidente: 19/abr/2026, Time Machine desligado causou perda de settings/skills — ver memória `project_recuperacao_19abr2026.md`.
- Proteção contra: deleção acidental fora de Git, config apagada, arquivo fora de repo.

### Camada 5 — Memória Markdown
- `15_memory/checkpoints/`, `CHANGELOG.md`, `NEXT_SESSION_CONTEXT.md`.
- `DIARIO-PROJETOS.md` atualizado.
- Resumo de sessão em `~/Desktop/Projetos - Plan Mode/Registros Sessões/`.
- Proteção contra: próxima sessão sem contexto, retrabalho por esquecimento.

## Matriz camada × ameaça

| Ameaça | C1 Editor | C2 Commit | C3 Push | C4 TM | C5 Markdown |
|---|---|---|---|---|---|
| Crash do editor | ✓ | ✓ | ✓ | ✓ | — |
| `rm` acidental de arquivo | — | ✓ (se commitado) | ✓ | ✓ | — |
| HD/SSD falha | — | — | ✓ | ✓ (se disco externo OK) | — |
| Máquina roubada | — | — | ✓ | — | — |
| Próxima sessão sem contexto | — | ✓ (mensagens) | ✓ | — | ✓ |
| Contexto Claude compactado | — | — | — | — | ✓ |

Leitura: só Markdown salva da compactação de contexto. Só push salva de roubo. Usar todas.

## Ritual mínimo de início de sessão

```
1. Ler ~/Desktop/DIARIO-PROJETOS.md
2. Ler NEXT_SESSION_CONTEXT.md do projeto ativo
3. git pull
4. git status
5. Abrir CHANGELOG.md em aba fixa
```

Tempo: 3-5 minutos. Sem isso, começa no escuro e repete trabalho.

## Ritual mínimo de fim de sessão

```
1. git status     (checar arquivos não commitados)
2. git add . && git commit -m "checkpoint fim sessão AAAA-MM-DD"
3. git push
4. Atualizar CHANGELOG.md (3-5 linhas)
5. Atualizar NEXT_SESSION_CONTEXT.md (o que vem depois)
6. Atualizar DIARIO-PROJETOS.md se marco bateu
7. Salvar resumo em ~/Desktop/Projetos - Plan Mode/Registros Sessões/SESSAO-[TEMA]-[DATA].md
```

Tempo: 5-10 minutos. Parecem muito até a primeira vez que perde 4 horas por ter pulado.

## Checklist de pós-sessão

- [ ] Arquivos salvos no editor (Cmd+S em todos).
- [ ] `git status` limpo ou commitado.
- [ ] `git push` feito com sucesso (checar output).
- [ ] CHANGELOG.md tem entrada de hoje.
- [ ] NEXT_SESSION_CONTEXT.md atualizado.
- [ ] Resumo salvo em Registros Sessões.
- [ ] Time Machine rodou no último dia (checar menu bar).
- [ ] Se trabalho pericial: atualizado em 00-CONTROLE/ do Dexter.

## Sinais de que a sessão está prestes a acabar

| Sinal | O que significa | Ação imediata |
|---|---|---|
| Token usage > 80% no statusLine | Contexto Claude vai comprimir | Salvar checkpoint Markdown AGORA, antes de compactar |
| Latência alta nas respostas | Servidor congestionado ou contexto pesado | Salvar, fazer pausa, reabrir |
| Sensação de cansaço / foco caindo | Decisões pioram após esse ponto | Rodar ritual de fim, parar. NÃO é preguiça, é proteção. |
| "Vou só terminar mais uma coisa" | Risco alto de esquecer commitar | Commitar o que tem, depois seguir |
| Respostas incoerentes do agente | Contexto corrompido ou comprimido | Salvar contexto em Markdown, abrir sessão nova |

## Uso de `15_memory/checkpoints/`

Quando contexto está prestes a ser compactado, salvar estado bruto em arquivo dentro de `15_memory/checkpoints/` com formato:

```
checkpoint-2026-04-23-1430.md
```

Conteúdo mínimo:

```markdown
# Checkpoint AAAA-MM-DD HH:MM

## O que eu estava fazendo
<3-5 linhas>

## Estado atual
- Arquivo aberto: <caminho>
- Última decisão tomada: <qual>
- Próxima ação planejada: <qual>

## Arquivos modificados na sessão
- <lista>

## Bloqueios / dúvidas pendentes
- <lista>

## Hash do último commit
<git log -1 --oneline>
```

Esse arquivo permite reabrir sessão Claude nova sem perder fio da meada.

## Regra de ouro

Trabalho que não está em **duas camadas** não existe. Arquivo só salvo no editor = ainda não existe. Commit só local = ainda não existe. Push sem Markdown de contexto = existe mas próxima sessão não vai achar.

## Ver também

- `git_survival_manual.md` — camadas 2 e 3 em detalhe.
