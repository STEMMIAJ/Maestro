---
name: PENDENTE — Camada de segurança no Stemmia Planner
description: Backup CLAUDE foi subido para stemmia.com.br/teste/backup-claude/. Falta proteger com .htaccess + IP allowlist + cabeçalho noindex.
type: project
originSessionId: 11924f1d-2075-435c-82ab-62f52b3897c2
---
# 19/abr/2026 — Camada de segurança PENDENTE no Stemmia

## Contexto
- Usuário pediu upload do backup Claude para o Stemmia Planner
- Backup contém: settings.json, MCP credentials, FTP password (em referência), 48.591 arquivos
- ZIP foi protegido com senha local (`~/Desktop/BACKUP CLAUDE/SENHA-ZIP-NAO-SUBIR.txt`)
- MAS o ZIP em si está num diretório FTP que pode ser indexado

## Risco atual
- Se alguém adivinhar URL `stemmia.com.br/teste/backup-claude/BACKUP-CLAUDE-LEVE-2026-04-19.zip`, baixa o arquivo
- Senha do ZIP protege se baixarem, mas é melhor não deixarem nem listar
- Diretório `/teste/` no FTP NÃO tem .htaccess de proteção atualmente

## Lembrar de fazer (ordem)
1. Criar `.htaccess` em `/teste/backup-claude/` com:
   ```
   Options -Indexes
   <Files "*.zip">
       Require ip 191.X.X.X  # IP residencial dele
       AuthType Basic
       AuthName "Backup Restrito"
       AuthUserFile /home/stemmiac/.htpasswd-backup
       Require valid-user
   </Files>
   Header set X-Robots-Tag "noindex, nofollow"
   ```
2. Criar `.htpasswd-backup` com `htpasswd -c .htpasswd-backup jesus`
3. Adicionar `/teste/backup-claude/` ao `robots.txt` como Disallow
4. Testar acesso anônimo (deve dar 403)
5. Configurar rotação: manter só últimos 3 backups (cron cleanup)

## Quando lembrar
- No próximo `/stemmia` ou início de sessão de manhã
- Se usuário mencionar: backup, planner, segurança, stemmia, FTP, vazamento
- Antes de subir QUALQUER outro backup

## Arquivos relacionados
- Backup local: `~/Desktop/BACKUP CLAUDE/`
- Senha ZIP: `~/Desktop/BACKUP CLAUDE/SENHA-ZIP-NAO-SUBIR.txt` (não subir!)
- Credencial FTP: `reference_ftp_deploy.md`
