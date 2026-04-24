---
name: Setup MacBook — sincronização iCloud
description: Script de setup, o que sincroniza via iCloud, e pendência do Mac Mini
type: project
---

## Setup entre Mac Mini e MacBook

Tudo do Stemmia sincroniza via iCloud usando symlinks.

### Script de setup
```
bash ~/Library/Mobile\ Documents/com~apple~CloudDocs/Stemmia/setup-macbook.sh
```
- Instala brew, ferramentas, pacotes Python, ccusage
- Cria symlinks no Desktop e ~/.claude apontando para iCloud

### O que sincroniza (tudo via symlink → iCloud)
- ~/.claude/agents (64 agentes)
- ~/.claude/plugins/stemmia-forense (35 skills)
- ~/.claude/plugins/process-mapper
- ~/.claude/projects/-Users-jesus/memory
- ~/.claude/CLAUDE.md
- ~/.claude/settings.json
- ~/Desktop/ANALISADOR FINAL (hooks, scripts, config)
- ~/Desktop/PERÍCIA
- ~/Desktop/adaptador tamanho sessões
- ~/Desktop/Projetos - Plan Mode

### Pendência: Mac Mini
O Mac Mini ainda tem CLAUDE.md e settings.json como cópias locais (não symlinks).
Precisa rodar o setup-macbook.sh de novo lá para atualizar para symlinks:
```
bash ~/Library/Mobile\ Documents/com~apple~CloudDocs/Stemmia/setup-macbook.sh
```
Isso vai substituir as cópias locais por symlinks para o iCloud.
