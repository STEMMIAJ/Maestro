# OpenClaw — Status / Health

## Visao geral
OpenClaw oferece dois comandos de diagnostico, com escopos diferentes:

- `openclaw status` — diagnostico **de alto nivel** da linked session: canais, sessoes recentes, usage de providers, task pressure e servicos (Gateway + node host). Pode rodar offline (graceful degrade) se SecretRefs nao resolverem.
- `openclaw health` — **snapshot de saude do Gateway** via RPC. Sempre fala com o servico rodando; retorna estado cacheado ou, com `--verbose`, forca probe ao vivo.

Ambos aceitam `--json` para scripting.

## `openclaw status`
```bash
openclaw status                  # overview rapido
openclaw status --all            # diagnose completo, pasteable, read-only
openclaw status --deep           # live probes (WhatsApp Web, Telegram, Discord, Slack, Signal)
openclaw status --usage          # X% left por provider (Anthropic, Copilot, Gemini CLI, Codex, MiniMax, Xiaomi, z.ai)
openclaw status --timeout 5000
openclaw status --verbose        # alias: --debug
```

Inclui:
- Gateway + node host service install/runtime status.
- Update channel + git SHA (em source checkouts).
- Task summary: `active | failures | byRuntime`.
- Secrets overview (em `--all`), com `secretDiagnostics` em JSON quando SecretRef fica unavailable.
- Fallback de transcript para recuperar metrics (tokens, cache, modelo ativo) quando a live session esta esparsa.

## `openclaw health`
```bash
openclaw health
openclaw health --json
openclaw health --timeout 2500   # default 10000
openclaw health --verbose        # forca live probe; expande accounts+agents
openclaw health --debug
```

- Default retorna snapshot cacheado e refresh em background.
- `--verbose` forca live probe e imprime detalhes de conexao do gateway.
- Output inclui session stores por agente quando multiplos agentes configurados.

## Comandos relacionados (aprofundamento)
- `openclaw gateway status [--deep] [--no-probe] [--require-rpc] [--json]` — estado do servico do Gateway (launchd/systemd/schtasks) + log path + probe target URL.
- `openclaw gateway probe` — probe direto RPC.
- `openclaw logs --follow [--limit <n>] [--json]` — tail do log do Gateway.
- `openclaw doctor [--deep] [--repair]` — health checks com sugestao de fix.
- `openclaw tasks audit` — issues operacionais de tasks (tambem refletido em `status`).
- `openclaw memory status --deep` — saude do indice de memoria.
- `openclaw channels status --probe` — probe por canal (fallback quando GW indisponivel).

## Exemplos praticos
```bash
# Script de heartbeat externo (cron macOS ou launchd)
openclaw status --json > /tmp/openclaw-status.json
jq '.tasks.active, .tasks.failures' /tmp/openclaw-status.json

# Live probe completo
openclaw status --deep --usage --verbose

# So checar se o gateway esta saudavel
openclaw health --json --timeout 2000
```

## Relacao com Maestro
- Integrar no painel local: `openclaw status --json` como heartbeat para o dashboard stemmia.
- Incluir em cron J01 (relatorio matinal) `openclaw health --json` e `openclaw status --all` como anexos.
- Em scripts bash de diagnostico do Dexter, preferir `openclaw status --json` (estavel, read-only) em vez de parsear `status` textual.

## Referencia
- Arquivos fonte: `docs/cli/status.md`, `docs/cli/health.md`.
- Tambem citado em `docs/cli/index.md` (secoes `status`, `health`, `gateway status`).
- Conceito de usage: `docs/concepts/usage-tracking.md`.
- Commit: `35ec4a9991`.
