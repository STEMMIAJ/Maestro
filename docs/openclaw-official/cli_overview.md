# OpenClaw — CLI Overview

## Visao geral
O binario `openclaw` e a superficie unica para operar Gateway, agentes, memoria, cron, browser, canais de chat, plugins, hooks e modelos. O shape geral e `openclaw [--dev] [--profile <name>] <comando> [subcomando] [flags]`. A maior parte dos comandos fala com o Gateway via RPC; alguns (setup, onboard, doctor, config) operam sobre o config local.

## Comandos principais (raiz)
Grupos documentados no indice CLI:

- Setup/onboarding: `setup`, `onboard`, `configure`, `config`, `doctor`, `completion`, `update`, `reset`, `uninstall`, `backup`.
- Controle de servico: `gateway`, `daemon` (alias legado), `logs`, `tui`, `dashboard`.
- Agentes e sessoes: `agent`, `agents`, `sessions`, `acp`, `mcp`.
- Diagnostico: `status`, `health`, `doctor`, `system event|heartbeat|presence`.
- Mensageria e canais: `message`, `channels`, `directory`, `pairing`, `qr`, `clawbot`.
- Automacao: `cron`, `tasks`, `flows` (alias legado para `tasks flow`), `hooks`, `webhooks`.
- Conhecimento: `memory`, `wiki`, `skills`, `docs`.
- Runtime remoto: `nodes`, `node`, `devices`, `browser`, `sandbox`.
- Extensao: `plugins`, `approvals`, `security`, `secrets`, `models`, `infer`.

## Flags globais
- `--dev`: isola estado em `~/.openclaw-dev` e troca portas default.
- `--profile <name>`: isola estado em `~/.openclaw-<name>`.
- `--container <name>`: executa em container nomeado.
- `--no-color` (ou `NO_COLOR=1`): desliga ANSI.
- `--update`: atalho para `openclaw update` (instalacoes source).
- `-V` / `--version` / `-v`: imprime versao e sai.

A maioria dos subcomandos aceita `--json` para saida estruturada e `--timeout <ms>` para RPCs do Gateway. Comandos sobre o Gateway aceitam `--url`, `--token`, `--password`, `--expect-final`.

## Configuracao minima
1. `openclaw setup --wizard` ou `openclaw onboard` — cria `openclaw.json`, registra credenciais e (opcional) instala o daemon.
2. `openclaw gateway install` / `start` — sobe o servico local (launchd/systemd/schtasks).
3. `openclaw doctor` — valida config, credenciais e plugins.
4. `openclaw dashboard` — abre a Control UI autenticada.
5. `openclaw status --deep` — verifica canais e servicos.

## Exemplos praticos
```bash
# Atualizar binario e mostrar status
openclaw update
openclaw status --all

# Saida JSON para scripting
openclaw agents list --json
openclaw cron list --json

# Diagnostico profundo do gateway
openclaw gateway status --deep --json
```

## Slash commands no chat
Mensagens em canais aceitam `/...` nativos: `/status`, `/trace`, `/config`, `/debug` (este ultimo requer `commands.debug: true`). Detalhes em `/tools/slash-commands` das docs.

## Referencia
- Repo: https://github.com/openclaw/openclaw (commit usado: `35ec4a9991`).
- Arquivo fonte: `docs/cli/index.md`.
- Docs publicas: https://docs.openclaw.ai/cli/ (ou `openclaw docs <query>` para busca local).
