---
title: Project Sync Memoria Obsidian
aliases: [project_sync_memoria_obsidian]
tags: [claude-memory, project]
categoria: project
sincronizado: 2026-04-19T05:26:18
---

# Sync Memoria Claude -> Obsidian + FTP (19/abr/2026)

## O que e
Sistema de sincronizacao automatica das memorias do Claude para:
1. Vault Obsidian local (leitura visual + busca)
2. Backup remoto online via FTP (resgate em desastre)

## Arquivos
- Script sync local: `/Users/jesus/stemmia-forense/automacoes/sync_memoria_obsidian.py`
- Script upload FTP: `/Users/jesus/stemmia-forense/automacoes/upload_memoria_ftp.py`
- Plist launchd: `/Users/jesus/Library/LaunchAgents/com.stemmia.sync-memoria.plist`
- Log: `/Users/jesus/.claude/projects/-Users-jesus/memory/sync-memoria.log`

## Caminhos
- **Origem (Claude):** `/Users/jesus/.claude/projects/-Users-jesus/memory/`
- **Destino Obsidian:** `/Users/jesus/Desktop/STEMMIA Dexter/memoria/CLAUDE-MEMORY/`
- **ZIP local:** `/Users/jesus/Desktop/STEMMIA Dexter/memoria/_backups-zip/`
- **Remoto FTP:** `/teste/backup-claude/memorias/`

## URL backup online
- Index: `https://stemmia.com.br/teste/backup-claude/memorias/`
- Ultimo ZIP: `https://stemmia.com.br/teste/backup-claude/memorias/LATEST.md`
- MEMORY.md legivel: `https://stemmia.com.br/teste/backup-claude/memorias/MEMORY.md`
- Protegido por Basic Auth (.htaccess) + noindex

## Cron
Roda 02h diariamente. Comando manual:
```
launchctl load ~/Library/LaunchAgents/com.stemmia.sync-memoria.plist
launchctl start com.stemmia.sync-memoria
```

## Como restaurar (cenario desastre)
1. Baixar ZIP de `https://stemmia.com.br/teste/backup-claude/memorias/CLAUDE-MEMORY-*.zip`
2. Extrair para pasta temporaria
3. Copiar `*.md` (sem o frontmatter Obsidian) de volta para `~/.claude/projects/-Users-jesus/memory/`
4. O frontmatter pode ser removido com: `sed -i '' '/^---$/,/^---$/d' arquivo.md`

## Politica de retencao
- **Local:** ultimos 7 ZIPs em `_backups-zip/`
- **Remoto:** ultimos 7 ZIPs no FTP

## Comandos uteis
```bash
# rodar sync agora
python3 /Users/jesus/stemmia-forense/automacoes/sync_memoria_obsidian.py

# subir para FTP agora
python3 /Users/jesus/stemmia-forense/automacoes/upload_memoria_ftp.py

# ver log
tail -f /Users/jesus/.claude/projects/-Users-jesus/memory/sync-memoria.log
```
