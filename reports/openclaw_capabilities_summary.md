# OpenClaw — resumo de capacidades (PRE-RESEARCH)

Gerado em 2026-04-22. Baseado em inferencia + placeholders. Revisar apos confirmacao da doc oficial.

## O que OpenClaw faz no projeto Maestro

OpenClaw e a camada transversal de automacao e supervisao do Maestro. Suas funcoes centrais no projeto:

1. **Cron gerenciado** — agenda jobs J01..J07 sem depender de launchd ou cron do SO; permite ativar/pausar/rodar individual via CLI.
2. **Memoria indexada e pesquisavel** — indexa `MEMORY.md` + `memory/YYYY-MM-DD.md` e expoe busca semantica (`memory search`, `memory index`, `memory promote`).
3. **Tasks sincronizadas** — espelha ou substitui `TASKS_MASTER.md` com estado persistente; audita tarefas paradas.
4. **Agents** — registra e executa agentes definidos em `AGENTS/`; expoe `openclaw agent run <nome>`.
5. **Dashboard local** — UI de console ou web leve para Dr. Jesus ver estado sem abrir terminal.
6. **Status/health** — heartbeat do sistema; fonte de dados para bot Telegram (C03, C04).
7. **Plugins/hooks** — pontos de extensao para automacoes finas (ex.: notificar ao fim de job).

**Nota:** Todas as capacidades acima sao PRESUMIDAS a partir da CLI listada na conversa. Confirmacao pendente (TASKS_NOW T045).

## Capacidades presumidas
| Capacidade | Uso no Maestro | Prioridade | Status |
|------------|----------------|------------|--------|
| Cron | J01..J07 (diario/semanal/mensal) | alta | planejado |
| Memoria persistente | complementa MEMORY.md, busca | media | planejado |
| Tasks | sincroniza TASKS_MASTER | media | planejado |
| Agents | expor agentes do Maestro | media | planejado |
| Dashboard local | visao tecnica para Dr. Jesus | baixa | planejado |
| Status/health | heartbeat + bot Telegram | media | planejado |
| Plugins/hooks | automacoes finas | baixa | planejado |

## O que NAO esta claro
- Se OpenClaw chama modelos LLM ou e apenas orquestrador.
- Se suporta multi-projeto.
- Se tem autenticacao/multiusuario.
- Se tem API HTTP ou apenas CLI.
- Custo (gratuito / pago / self-hosted).

## Dependencia bloqueante
Confirmacao do nome e URL oficial pelo Dr. Jesus (TASKS_NOW T045).
