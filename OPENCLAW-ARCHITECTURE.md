# OPENCLAW-ARCHITECTURE.md

## Status da ferramenta OpenClaw
**BLOQUEIO — RESEARCH:** o nome "OpenClaw" nao foi confirmado como ferramenta publica canonica. Pode ser:
- Codinome interno do Dr. Jesus para um conjunto (Claude Code + OpenCode + scripts).
- Referencia ao "OpenCode" (competidor do Claude Code).
- Outro projeto a identificar.

Acao pendente: Dr. Jesus confirma nome oficial e/ou URL da documentacao. Ver `TASKS_NOW.md` item T045.

## Papel pretendido do OpenClaw no Maestro
(Conforme a conversa-fonte indicar — arquivos em docs/openclaw-official/ e reports/openclaw_*.md populados quando fonte confirmada.)

### Responsabilidades pretendidas
| Area | OpenClaw | Claude Code | Dexter / Python base |
|------|----------|-------------|----------------------|
| Cron / agendamento | ATIVO (quando configurado) | nao | backup em launchd |
| Memoria persistente | ATIVO (store proprio) | contexto efemero | arquivos MD |
| Tarefas (queue) | ATIVO | reativo | nao |
| Dashboard local | ATIVO (se oferece) | nao | `painel/` HTML |
| Health / status | ATIVO | via scripts | manual |
| Plugins / hooks | ATIVO | ATIVO | nao |
| Agents | delegacao | ATIVO | agentes clinicos `agents/` |

## Comandos previstos (TODO/RESEARCH)
Sujeito a confirmacao da doc oficial:
- `openclaw init`
- `openclaw memory add/list/search`
- `openclaw task add/list/done`
- `openclaw agent run`
- `openclaw cron list/enable/disable`
- `openclaw dashboard`
- `openclaw status`
- `openclaw plugin list/enable`

Atualizar `reports/openclaw_command_map.md` com mapeamento fluxo->comando apos confirmacao.

## O que o Maestro delega / mantem
- **Delegar ao OpenClaw:** agendamento, persistencia longa, notificacoes recorrentes.
- **Manter no Claude Code:** redacao, analise, sintese de conversas, geracao de arquivos complexos.
- **Manter em Python base:** ingestao, chunk, extracao, parsing determinista.

## Dependencia bloqueante
Ate confirmacao de OpenClaw (fonte oficial), tratar como **camada planejada**: todos os FLOWS/ citam "delegar ao OpenClaw quando instalado".
