---
name: Tradução técnica inline
description: Ao usar termos técnicos pela primeira vez, explicar em linguagem leiga com analogia médica
type: feedback
---

Ao usar termos técnicos de TI pela PRIMEIRA vez, incluir micro-definição inline automaticamente (sem perguntar).
- Formato: **termo** (definição em 5 palavras máx)
- Só na primeira ocorrência. Depois, usar o termo normalmente.
- Exemplo: "O **endpoint** (porta de entrada do sistema) está offline."
- NUNCA usar analogias longas. NUNCA over-explaining. Apenas micro-definição factual.

**Why:** Usuário é médico, não é de TI. Neurodivergente com anomia — termos desaparecem da memória entre sessões. Micro-definição factual é suficiente.

**How to apply:** Sempre que usar termo técnico novo. NÃO explicar termos já dominados:
hook, skill, agent, pipeline, prompt, HTML, CSS, JSON, Python, script, Claude Code, MCP, terminal, FTP, Git, branch, commit, API, bug, debug, worktree, plugin, context window, token, bash, regex, deploy, backup, webhook, workflow, N8N

Se o usuário perguntar "o que é X" → usar agente `tradutor-tecnico.md` (4 camadas)
NUNCA perguntar "quer que eu explique?". Incluir a micro-definição E PRONTO.
