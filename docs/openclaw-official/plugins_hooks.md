# OpenClaw — Plugins / Hooks

## Visao geral
Existem **dois sistemas** distintos e complementares:

1. **Plugins** (`openclaw plugins`) — extensoes de Gateway. Podem registrar capabilities (provider de modelo, speech, image, browser), tools, commands, services, rotas HTTP, metodos RPC de gateway, hooks, MCP/LSP servers. Formatos suportados:
   - **Nativo OpenClaw**: arquivo `openclaw.plugin.json` com `configSchema` inline.
   - **Bundles compativeis**: Codex (`.codex-plugin/plugin.json`), Claude (`.claude-plugin/plugin.json` ou layout Claude default), Cursor (`.cursor-plugin/plugin.json`).
2. **Hooks** (`openclaw hooks`) — automacoes internas orientadas a evento (`command:new`, `command:reset`, `gateway:startup`, `agent:bootstrap`, etc.). Podem vir de bundled, workspace (`<workspace>/hooks/`, disabled por default), managed dirs, ou empacotados como **hook packs** (instalados via `openclaw plugins install`).

Plugins podem registrar hooks; hooks gerenciados por plugin nao sao toggled via `openclaw hooks` — toggle o plugin dono.

## Plugins — comandos
```bash
openclaw plugins list [--enabled] [--verbose] [--json]
openclaw plugins inspect <id> [--json]          # alias: info
openclaw plugins inspect --all
openclaw plugins install <path|archive|npm-spec|clawhub:<pkg>|plugin@marketplace> [--pin] [--force] [-l|--link] [--dangerously-force-unsafe-install]
openclaw plugins uninstall <id> [--dry-run] [--keep-files]
openclaw plugins enable <id>
openclaw plugins disable <id>
openclaw plugins update <id-or-npm-spec> [--all] [--dry-run]
openclaw plugins doctor
openclaw plugins marketplace list <source> [--json]
```

Notas importantes:
- Bare specs: OpenClaw procura ClawHub primeiro, depois npm.
- npm specs **registry-only** (`name` ou `name@exact-version` ou `name@dist-tag`). Git/URL/file/semver range rejeitados. Install roda `--ignore-scripts`.
- `@latest` e bare continuam no stable; prerelease precisa opt-in explicito (`@beta`, `@rc`, `@1.2.3-beta.4`).
- A maioria das mudancas de plugin exige **gateway restart**.
- Formato e mostrado em `plugins list`: `Format: openclaw` ou `Format: bundle` (+ subtype `codex|claude|cursor`).
- Classificacao em `inspect`: `plain-capability`, `hybrid-capability`, `hook-only`, `non-capability`.

## Hooks — comandos
```bash
openclaw hooks list [--eligible] [--verbose] [--json]
openclaw hooks info <name> [--json]
openclaw hooks check [--json]
openclaw hooks enable <name>
openclaw hooks disable <name>
# Deprecados (forward para plugins):
openclaw hooks install <path-or-spec>   # -> openclaw plugins install
openclaw hooks update [id]              # -> openclaw plugins update
```

Observacoes:
- Hooks de workspace ficam **disabled por default** ate `enable` explicito.
- Enable/disable edita `hooks.internal.entries.<name>.enabled` em `~/.openclaw/openclaw.json`; **restart do gateway** e necessario para recarregar.
- Plugin-managed hooks sao travados: toggle o plugin dono.

## Hooks bundled
- **session-memory** — salva contexto ao disparar `/new` ou `/reset`. Output: `~/.openclaw/workspace/memory/YYYY-MM-DD-slug.md`. Eventos: `command:new`, `command:reset`.
- **bootstrap-extra-files** — injeta arquivos extras (ex.: `AGENTS.md`, `TOOLS.md` monorepo-local) durante `agent:bootstrap`.
- **command-logger** — loga todos os eventos de comando em `~/.openclaw/logs/commands.log`.
- **boot-md** — roda `BOOT.md` em `gateway:startup` (apos canais iniciarem).

## Exemplos praticos
```bash
# Instalar um plugin da ClawHub com versao pinned
openclaw plugins install clawhub:openclaw-codex-app-server@1.2.3 --pin

# Inspecao profunda de um plugin
openclaw plugins inspect memory-core --json

# Habilitar hook bundled que salva contexto de sessao
openclaw hooks enable session-memory
openclaw gateway restart

# Auditar problemas de carga
openclaw plugins doctor
openclaw hooks check --json
```

## Relacao com Maestro
- Hooks Claude Code atuais vivem em `~/.claude/hooks/` (ex.: `bloquear_limpeza.py`). Esses hooks sao do **Claude Code CLI**, nao do OpenClaw — coexistem sem conflito.
- Migracao possivel: transformar hooks anti-mentira em **hook pack** OpenClaw (pasta com manifest + handler) e instalar via `openclaw plugins install -l <path>` para usar tambem em runs ACP/cron do Gateway.
- Para plugins do Claude Code (`~/Desktop/PLUGINS CLAUDE/`), manter catalogo separado; OpenClaw nao os executa.

## Referencia
- Arquivos fonte: `docs/cli/plugins.md`, `docs/cli/hooks.md`, `docs/automation/hooks.md`, `docs/plugins/architecture.md`, `docs/plugins/manifest.md`, `docs/plugins/bundles.md`.
- Commit: `35ec4a9991`.
- Indice CLI: `docs/cli/index.md` secoes `plugins` e `hooks`.
