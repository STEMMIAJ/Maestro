# OpenClaw para o Maestro — recomendacao inicial (PRE-RESEARCH)

Gerado em 2026-04-22. Sujeito a revisao apos confirmacao.

## Quais capacidades do OpenClaw se aplicam ao Maestro

| Capacidade | Aplica? | Motivo | Prioridade |
|------------|---------|--------|------------|
| Cron | Sim | Jobs J01..J07 dependem de agendamento confiavel | Alta |
| Memoria indexada | Sim | `MEMORY.md` + `memory/*.md` precisam de busca semantica | Media |
| Tasks | Sim (parcial) | `TASKS_MASTER.md` pode migrar se sincronizacao bidirecional funcionar | Media |
| Agents | Sim | 8 agentes definidos em `AGENTS/` precisam de registro e execucao | Media |
| Dashboard local | Sim (futuro) | Substituicao de terminal para Dr. Jesus; TEA/TDAH exige interface clara | Baixa |
| Status/health | Sim | Fonte de dado para bot Telegram C03/C04 | Media |
| Plugins/hooks | Sim (condicional) | Somente se cron e memory nao cobrirem automacoes finas | Baixa |
| Gateway | Nao claro | Nao mencionado na conversa — TODO/RESEARCH | — |
| Multi-usuario/auth | Nao | Uso solo; Dr. Jesus e unico operador | Nao aplica |

## Capacidades que NAO se aplicam (ou redundantes)

- CDN / deploy remoto — o Maestro e local; deploy e do site stemmia.com.br, nao do OpenClaw.
- Analytics de uso — dados de pericia nao passam pelo OpenClaw diretamente.
- Integracao com provedores externos (Slack, Jira, etc.) — nao usados.

## Hipoteses
1. OpenClaw = camada de automacao (cron + memoria + status + agents).
2. Maestro = camada de governanca (decisoes, planos, relatorios humanos).
3. Python base = camada de transformacao (ETL, parsing, chunking).

## Adocao sugerida por fases
### Bootstrap (1 semana apos confirmacao)
- Instalar OpenClaw local.
- `openclaw init` no diretorio Maestro.
- Rodar apenas `openclaw status` e `openclaw memory list` (leitura).
- Nenhum cron ativo ainda.

### Expansao 1 (2a semana)
- Ativar 1 cron: J02 (backup diario local).
- Observar 7 dias. Log de falhas.

### Expansao 2 (3a semana)
- Ativar J01 (relatorio matinal) + J03 (auditoria semanal).
- Integrar bot Stemmia (ainda sem envio real — stub de logging).

### Expansao 3 (4a+)
- Ativar restante (J04..J07).
- Migrar TASKS_MASTER para OpenClaw tasks se sincronizacao bidirecional for boa.
- Dashboard local OpenClaw + dashboard publico stemmia.com.br.

## Sinais de abandono
Se em 2 semanas:
- OpenClaw esta mais fricao que automacao.
- Bugs ou dependencias quebram fluxo.
- Dr. Jesus prefere scripts Python puros.

Entao: aposentar OpenClaw, manter apenas Python base + cron launchd + bot Telegram direto.

## Dependencia critica
Confirmacao do que e OpenClaw. Sem isso, este documento e especulativo.
