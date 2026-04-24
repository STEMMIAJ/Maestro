---
name: Ruflo - Orquestrador de Agentes
description: Ruflo v3.5.51 instalado em 06/abr/2026 — orquestrador de swarms, memória persistente, 98 agents, 30 skills, MCP server
type: reference
---

## Ruflo v3.5.51

Instalado via `curl -fsSL https://cdn.jsdelivr.net/gh/ruvnet/ruflo@main/scripts/install.sh | bash -s -- --full`

**O que é:** Orquestrador de agentes AI para Claude Code. Gerencia swarms (enxames de agentes paralelos), memória persistente, hooks automáticos.

**O que criou no projeto ~/stemmia-forense/:**
- `.claude/agents/` — 98 agents (analysis, architecture, browser, github, swarm, etc.)
- `.claude/skills/` — 30 skills (pair-programming, github-workflow, hooks-automation, etc.)
- `.claude/commands/` — 10 commands (analysis, automation, github, monitoring, etc.)
- `.claude/helpers/` — hook handlers Node.js
- `.claude-flow/` — config, data, logs, sessions
- `.mcp.json` — MCP server local
- `.claude/settings.json` — hooks locais do projeto (NÃO conflita com global)

**Comandos principais:**
- `ruflo doctor` — diagnóstico do sistema
- `ruflo daemon start` — inicia workers em background
- `ruflo memory init` — inicializa banco de memória
- `ruflo swarm init` — inicializa swarm de agentes
- `ruflo init --start-all` — inicia tudo de uma vez

**MCP server:** configurado em `.claude.json` (local), comando `ruflo mcp start`

**Adicionou ao CLAUDE.md global:**
- Instrução para usar ToolSearch para encontrar ferramentas ruflo MCP
- Tools: memory_store, memory_search, hooks_route, swarm_init, agent_spawn
