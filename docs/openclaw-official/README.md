# docs/openclaw-official

Copias LOCAIS da documentacao oficial de OpenClaw para consulta sem rede.

## Status (2026-04-23) — CONFIRMADO
- Site oficial: https://openclaw.ai
- Repositorio: https://github.com/openclaw/openclaw
- Licenca: open source (gratuito; custo = LLM que voce usa)
- Instalacao: `npm i -g openclaw && openclaw onboard` OU `curl -fsSL https://openclaw.ai/install.sh | bash`

## Natureza confirmada
OpenClaw = orquestrador com LLM + skills/plugins + browser control + shell access + cron/tasks. Funciona via apps de chat (WhatsApp/Telegram/Discord/Slack/Signal/iMessage) OU CLI local. Suporta backends: Claude (recomendado), GPT, modelos locais (MiniMax 2.5).

## Proximos passos (backlog B002)
1. `gh repo clone openclaw/openclaw /tmp/openclaw-src` (so leitura)
2. Mapear docs internas: README, docs/, CONTRIBUTING.
3. Copiar 8 topicos prioritarios aqui (substituir placeholders):
   - cli_overview.md
   - memory.md
   - dashboard.md
   - cron.md
   - agents.md
   - tasks.md
   - status_health.md
   - plugins_hooks.md

## Como baixar
1. `gh repo clone openclaw/openclaw` (preferencial — traz markdown original).
2. WebFetch da pagina /docs se existir.
3. MCP chrome se precisar render JS.
