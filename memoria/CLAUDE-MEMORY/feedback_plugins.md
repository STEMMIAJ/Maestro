---
name: feedback_plugins
description: Sempre documentar plugins instalados/criados na pasta da Mesa (PLUGINS CLAUDE)
type: feedback
---

Ao instalar ou criar qualquer plugin, SEMPRE atualizar `~/Desktop/PLUGINS CLAUDE/PLUGINS-NOVOS.md` com entrada completa (data, nome, fonte, localização, o que faz, comandos/skills/agentes/hooks adicionados).

**Why:** O usuário tem muitos plugins (43+ marketplace, 36 skills próprias) e precisa de um catálogo centralizado na Mesa para lembrar o que tem.

**How to apply:** Após qualquer instalação/criação de plugin, preencher o template em PLUGINS-NOVOS.md e rodar `python3 ~/Desktop/ANALISADOR\ FINAL/scripts/atualizar_plugins.py` para atualizar PLUGINS-INSTALADOS.md.
