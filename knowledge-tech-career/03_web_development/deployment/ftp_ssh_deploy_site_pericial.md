---
titulo: Deploy FTP/SSH no stemmia.com.br
bloco: 03_web_development
tipo: pratico
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 5
---

# Deploy FTP/SSH no stemmia.com.br

Site stemmia.com.br roda WordPress em hospedagem tradicional via FTP. Fluxo herdado, funciona. Alternativas modernas existem e compensam a médio prazo.

## Fluxo atual (FTP)

Credenciais em `reference_ftp_deploy.md` (senha atualizada 16/mar/2026).

Cliente FTP recomendado:
- **lftp** (CLI, scriptável) — ideal para automação.
- **Transmit** (Mac) — GUI.
- **FileZilla** — multiplataforma.

Sync incremental com lftp:

```bash
lftp -c "set ftp:ssl-allow no; \
  open ftp://usuario:senha@ftp.stemmia.com.br; \
  mirror -R --delete --verbose ./public/ /public_html/teste/"
```

- `-R` = reverso (upload).
- `--delete` = apaga remotos que sumiram local.
- `--verbose` = mostra cada arquivo.

Preferir **FTPS** (TLS) a FTP plano. Confirmar suporte do host.

## Automação — script pronto

Há memória do usuário: `feedback_sync_upload.md` (sempre subir PDFs/HTMLs + atualizar Planner). Roteiro:

1. Gerar PDF/HTML do laudo local (`~/Desktop/_MESA/10-PERICIA/laudos/`).
2. Rodar script de deploy para `stemmia.com.br/teste/laudos/{numero_processo}/`.
3. Atualizar Planner com URL.

Script shell exemplo:

```bash
#!/usr/bin/env bash
# ref: PW-deploy-ftp
set -euo pipefail
source "$HOME/.config/stemmia/ftp.env"  # FTP_USER, FTP_PASS, FTP_HOST

LOCAL_DIR="$1"
REMOTE_DIR="$2"

lftp -u "$FTP_USER,$FTP_PASS" "$FTP_HOST" <<EOF
set ftp:ssl-allow yes
set ssl:verify-certificate no
mirror -R --delete --verbose --parallel=4 "$LOCAL_DIR" "$REMOTE_DIR"
bye
EOF
```

## Camada de segurança

`project_camada_seguranca_planner.md` documenta pendência: proteger `/teste/backup-claude/` com `.htaccess` + auth + noindex.

`.htaccess` básico:

```apache
# /public_html/teste/backup-claude/.htaccess
AuthType Basic
AuthName "Area restrita"
AuthUserFile /home/usuario/.htpasswd
Require valid-user

Header set X-Robots-Tag "noindex, nofollow"
Options -Indexes
```

Criar senha:
```bash
htpasswd -c ~/.htpasswd drjesus
```

Subir `.htaccess` + `.htpasswd` para o host (o `.htpasswd` fora de `public_html`, se possível).

## SSH (se o host permite)

Muitos hosts de WordPress permitem SSH/SFTP. Vantagens:

- **rsync** em vez de lftp (muito mais rápido e confiável).
- **Chave SSH** em vez de senha (mais seguro).

```bash
rsync -avz --delete ./public/ drjesus@ssh.stemmia.com.br:/home/drjesus/public_html/teste/
```

Configurar chave:
```bash
ssh-keygen -t ed25519 -C "stemmia-deploy"
ssh-copy-id drjesus@ssh.stemmia.com.br
```

Adicionar ao `~/.ssh/config`:
```
Host stemmia
  HostName ssh.stemmia.com.br
  User drjesus
  IdentityFile ~/.ssh/id_ed25519
```

Então `rsync ./public/ stemmia:public_html/teste/` direto.

## Alternativas modernas

| Alternativa | Vantagem | Migração |
|-------------|----------|----------|
| **Cloudflare Pages** | Grátis, CDN global, git push → deploy | Migrar WordPress para Hugo/Astro estático |
| **Netlify** | Similar, forms grátis | Idem |
| **VPS própria + nginx** | Controle total, N8N já lá | Mover WordPress para srv19105 |
| **Github Pages** | Simples, grátis | Só estático |

WordPress dinâmico + MySQL = difícil ir direto para estático. Opções:

1. **Headless WordPress** — WP só edita; frontend estático consome REST API.
2. **Simply Static / WP2Static** — plugin exporta WP para HTML; subir estático.
3. **Migração completa** — ir para Hugo/Astro; escrever em Markdown.

## Recomendação para o Dr. Jesus

**Curto prazo** — manter FTP, automatizar com script lftp + env var, adicionar `.htaccess` na pasta sensível.

**Médio prazo** — avaliar "Simply Static": exporta WP → HTML → subir em Cloudflare Pages (grátis). Zero custo, zero manutenção WordPress (sem plugins vulneráveis, sem update).

**Relatório/laudos no site** — criar subdomínio `relatorios.stemmia.com.br` em Cloudflare Pages, deploy via `wrangler pages deploy`, auth via Cloudflare Access (grátis para poucos usuários).

## Armadilhas

- FTP plano sem TLS — credencial em texto claro na rede.
- `mirror --delete` sem `--dry-run` primeiro — apagou prod por caminho errado.
- Senha FTP hardcoded em script versionado.
- WordPress sem update = porta de entrada de ransomware. Se manter WP, ter backup automático + update mensal.
- Sem `.htaccess` protegendo pasta de backup/rascunho = público no Google.
