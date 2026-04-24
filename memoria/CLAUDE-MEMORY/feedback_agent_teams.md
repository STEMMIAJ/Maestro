---
name: Agent Teams são essenciais
description: Ativar CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 - feature que dava fluidez ao workflow anterior
type: feedback
---

No Mac anterior o usuário rodava 12 sessões paralelas e o workflow era excelente. Agent Teams é a feature que coordena múltiplas sessões trabalhando juntas com task list compartilhada.

**Why:** Usuário reportou que no Mac anterior "examinava 7 processos ao mesmo tempo" e agora "não consegue fazer nada". A feature estava desativada por padrão neste Mac.

**How to apply:** Sempre que o usuário pedir paralelismo massivo, sugerir Agent Teams. Variável: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 no settings.json > env.
