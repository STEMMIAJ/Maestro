# OpenClaw — Agents

## Visao geral
Agentes no OpenClaw sao **identidades isoladas** que combinam: workspace proprio (`~/.openclaw/workspace-<name>` por default), perfil de auth/modelo, skills visiveis, e routing bindings que amarram canais/contas a um agente especifico. Todos compartilham o mesmo Gateway. O agente `main` e reservado e nao pode ser deletado nem reutilizado como id.

## Comandos
Todos sob `openclaw agents`:

- `agents list [--bindings] [--json]` — lista agentes configurados. Sem subcomando, `openclaw agents` equivale a `list`.
- `agents add [name] [--workspace <dir>] [--model <id>] [--agent-dir <dir>] [--bind <channel[:accountId]>] [--non-interactive] [--json]` — cria agente. Nao-interativo exige nome + `--workspace`.
- `agents bindings [--agent <id>] [--json]` — lista bindings de roteamento.
- `agents bind --agent <id> --bind <channel[:accountId]>` — adiciona binding. Repetivel.
- `agents unbind --agent <id> (--bind ... | --all)` — remove bindings. `--all` e `--bind` sao mutuamente exclusivos.
- `agents delete <id> [--force] [--json]` — apaga agente. Workspace e state vao para Trash (nao sao hard-deleted). `main` nao pode ser apagado.
- `agents set-identity [--agent <id>] [--workspace <dir>] [--identity-file <path>] [--from-identity] [--name <name>] [--theme <theme>] [--emoji <emoji>] [--avatar <value>]` — grava identidade em `agents.list[].identity`.

## Routing bindings
Binding no formato `channel[:accountId]`:
- Sem `accountId`: bate com a conta default do canal.
- `accountId: "*"`: fallback channel-wide (menos especifico que explicito).
- Se ja existe binding sem `accountId`, um novo bind com conta explicita **faz upgrade in-place**, nao duplica.

Skills visiveis por agente sao configuradas em `agents.defaults.skills` e `agents.list[].skills` em `openclaw.json`.

## Identity files
Cada workspace aceita `IDENTITY.md` na raiz. `set-identity --from-identity` le desse arquivo (ou `--identity-file <path>`). Avatars resolvem relativos ao workspace root.

Campos gravados:
- `name`, `theme`, `emoji`, `avatar` (path relativo, URL http(s), ou data URI).

## Exemplos praticos
```bash
# Criar agente ops com workspace proprio e bind telegram
openclaw agents add ops \
  --workspace ~/.openclaw/workspace-ops \
  --bind telegram:ops \
  --non-interactive

# Listar e revisar bindings
openclaw agents list --bindings
openclaw agents bindings --agent ops --json

# Atualizar identidade via IDENTITY.md
openclaw agents set-identity --workspace ~/.openclaw/workspace-ops --from-identity
```

Config sample:
```json5
{
  agents: {
    list: [
      {
        id: "main",
        identity: { name: "OpenClaw", theme: "space lobster", emoji: "🦞", avatar: "avatars/openclaw.png" }
      }
    ]
  }
}
```

## Relacao com Maestro
- Maestro ja tem 8 agentes descritos em markdown em `AGENTS/`. Formato nao e identico ao de `openclaw agents`.
- Integracao viavel: criar um agente OpenClaw por cluster (ex.: `pericia`, `peticao`, `pje`), apontar `--workspace` para a respectiva pasta do Maestro e replicar skills/permissoes em `agents.list[].skills` de `openclaw.json`.
- Alternativa minima: manter tudo como agente `main` e usar subagentes Claude Code para especializar.

## Referencia
- Arquivo fonte: `docs/cli/agents.md`.
- Conceitos: `docs/concepts/multi-agent.md`, `docs/concepts/agent-workspace.md`.
- Skills config: `docs/tools/skills-config.md`.
- Commit: `35ec4a9991`.
