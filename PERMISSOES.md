# PERMISSOES — Projeto Maestro

**Versao:** 2026-04-23
**Escopo:** tudo que acontece dentro de `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/` e no subprojeto `/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/conversation_ingestion/`
**Aplicado via:** `Maestro/.claude/settings.json` (escopo projeto — reflete este documento)

---

## Leitura obrigatoria no inicio de sessao

1. Este arquivo (`Maestro/PERMISSOES.md`)
2. `Maestro/CLAUDE.md`
3. `Maestro/CRONOMETRO.md` (se existir para a sessao corrente)
4. Confirmar `cat Maestro/.claude/settings.json` bate com este doc

Se este arquivo mudar, atualizar o settings.json **na mesma sessao**.

---

## Resumo executivo (regra de ouro)

| Area | Default |
|---|---|
| Ler qualquer arquivo do FS | **allow** |
| Escrever dentro de Maestro/ e conversation_ingestion/ | **allow** |
| Escrever fora desse escopo | **ask** |
| Python stdlib / rodar scripts | **allow** |
| Instalar pacotes (pip/npm/brew) | **ask** |
| Git local (status, diff, add, commit, branch) | **allow** |
| Git push / force / rebase -i / add -i | **deny** |
| Rede (curl/wget/ssh/rsync) | **ask** |
| FTP/SFTP/SCP | **deny** (ate FASE 8 com FTP_* do .env) |
| Cron / launchctl load | **deny** (ate FASE 7 homologada) |
| rm / rm -rf | **ask** (rm -rf exige dupla confirmacao em chat) |
| sudo / open | **deny** (open so com pedido literal) |
| Telegram/Slack via tool SendMessage | **deny** (usar Python+.env) |
| Chrome/playwright via MCP | **deny** (caidos) |

---

## 1. ALLOW (nao pede confirmacao)

### 1.1 Leitura filesystem
```
Read(*)
Glob(*)
Grep(*)
Bash(ls:*)
Bash(stat:*)
Bash(wc:*)
Bash(file:*)
Bash(head:*)
Bash(tail:*)
Bash(find:*)
Bash(diff:*)
Bash(du -sh:*)
Bash(tree:*)
Bash(realpath:*)
Bash(basename:*)
Bash(dirname:*)
Bash(which:*)
Bash(date:*)
Bash(echo:*)
Bash(printf:*)
Bash(test:*)
Bash(md5:*)
Bash(shasum:*)
```

### 1.2 Escrita / edicao (escopo limitado)
```
Edit(/Users/jesus/Desktop/STEMMIA Dexter/Maestro/**)
Write(/Users/jesus/Desktop/STEMMIA Dexter/Maestro/**)
Edit(/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/conversation_ingestion/**)
Write(/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/conversation_ingestion/**)
NotebookEdit(/Users/jesus/Desktop/STEMMIA Dexter/Maestro/**)
Bash(mkdir:*)
Bash(mkdir -p:*)
Bash(touch:*)
Bash(cp:*)
Bash(cp -r:*)
Bash(mv:*)
Bash(ln -s:*)
Bash(ln -sf:*)
Bash(chmod +x:*)
Bash(chmod 600:*)
Bash(chmod 644:*)
Bash(chmod 755:*)
```

### 1.3 Python / Node (stdlib + scripts locais)
```
Bash(python3:*)
Bash(python:*)
Bash(python3 -c:*)
Bash(python3 -m json.tool:*)
Bash(python3 -m http.server:*)
Bash(python3 -m venv:*)
Bash(python3 -m pip list:*)
Bash(pip3 list:*)
Bash(pip3 show:*)
Bash(pip3 freeze:*)
Bash(node:*)
Bash(npm list:*)
Bash(npm run:*)
```

### 1.4 Git local (zero remoto)
```
Bash(git status:*)
Bash(git diff:*)
Bash(git log:*)
Bash(git show:*)
Bash(git blame:*)
Bash(git ls-files:*)
Bash(git branch:*)
Bash(git rev-parse:*)
Bash(git remote -v:*)
Bash(git stash list:*)
Bash(git stash show:*)
Bash(git add:*)
Bash(git commit:*)
Bash(git commit -m:*)
Bash(git checkout:*)
Bash(git switch:*)
Bash(git restore --staged:*)
Bash(git tag:*)
```

### 1.5 OpenClaw (instalado em FASE 1)
```
Bash(openclaw --help:*)
Bash(openclaw --version:*)
Bash(openclaw config get:*)
Bash(openclaw config set:*)
Bash(openclaw status:*)
Bash(openclaw health:*)
Bash(openclaw doctor:*)
Bash(openclaw memory:*)
Bash(openclaw tasks:*)
Bash(openclaw agents:*)
Bash(openclaw plugins:*)
Bash(openclaw cron list:*)
```

### 1.6 SQLite local
```
Bash(sqlite3:*)
```

### 1.7 macOS utilities
```
Bash(osascript -e:*)       # notificacoes display notification
Bash(pbcopy:*)
Bash(pbpaste:*)
Bash(say:*)
Bash(ps:*)
Bash(top -l 1:*)
Bash(lsof -i:*)
```

### 1.8 Deno / curl local (loopback apenas)
```
Bash(curl http://localhost:*)
Bash(curl http://127.0.0.1:*)
```

### 1.9 MCPs uteis
```
mcp__plugin_context7_context7__query-docs
mcp__plugin_context7_context7__resolve-library-id
mcp__claude_ai_Context7__query-docs
mcp__claude_ai_Context7__resolve-library-id
mcp__claude_ai_PubMed__*
mcp__plugin_episodic-memory_episodic-memory__read
mcp__plugin_episodic-memory_episodic-memory__search
mcp__claude_ai_Exa__web_search_exa
mcp__claude_ai_Exa__web_fetch_exa
```

### 1.10 Web (allowlist)
```
WebFetch(domain:code.claude.com)
WebFetch(domain:docs.anthropic.com)
WebFetch(domain:api.anthropic.com)
WebFetch(domain:github.com)
WebFetch(domain:raw.githubusercontent.com)
WebFetch(domain:openclaw.ai)
WebFetch(domain:python.org)
WebFetch(domain:pypi.org)
```

---

## 2. ASK (pede confirmacao uma vez)

### 2.1 Destrutivo controlado
```
Bash(rm:*)                         # arquivo unico
Bash(rmdir:*)
Bash(chmod 000:*)
Bash(git reset --hard:*)
Bash(git clean -fd:*)
Bash(git branch -D:*)
Bash(git stash drop:*)
Bash(git push --force-with-lease:*)
```

### 2.2 Pacotes
```
Bash(pip3 install:*)
Bash(pip install:*)
Bash(pipx install:*)
Bash(npm install:*)
Bash(npm install -g:*)
Bash(npm uninstall:*)
Bash(brew install:*)
Bash(brew upgrade:*)
Bash(uv add:*)
Bash(uv pip install:*)
Bash(npx:*)
```

### 2.3 Rede
```
WebFetch(*)                         # dominios fora da allowlist
WebSearch
Bash(curl:*)                        # fora de localhost
Bash(wget:*)
Bash(rsync:*)
Bash(ssh:*)
Bash(git clone:*)
```

### 2.4 Processos
```
Bash(kill:*)
Bash(killall:*)
Bash(pkill:*)
Bash(osascript:*)                   # scripts mais complexos que -e
```

### 2.5 Agendamento (read-only fica em allow)
```
Bash(launchctl list:*)              # leitura OK
Bash(crontab -l:*)                  # leitura OK
ScheduleWakeup
CronList
```

### 2.6 Virtualizacao
```
Bash(prlctl:*)                      # Parallels PJe
```

### 2.7 Agent harness
```
TeamCreate
TeamDelete
EnterWorktree
ExitWorktree
CronCreate
CronDelete
```

---

## 3. DENY (sem excecao sem ordem explicita no chat)

### 3.1 Destrutivo sem recuperacao
```
Bash(rm -rf:*)                      # exige dupla confirmacao em chat
Bash(dd:*)
Bash(truncate:*)
Bash(chown:*)
Bash(sudo:*)                        # NUNCA
Bash(open:*)                        # regra raiz
```

### 3.2 Git remoto
```
Bash(git push:*)
Bash(git push --force:*)
Bash(git push -f:*)
Bash(git push origin --force:*)
Bash(git rebase -i:*)               # regra raiz: -i proibido
Bash(git add -i:*)
Bash(git config --global:*)         # regra raiz: NUNCA update config
```

### 3.3 Agendamento (ativar = deny ate homologado)
```
Bash(crontab -e:*)
Bash(crontab -r:*)
Bash(launchctl load:*)
Bash(launchctl unload:*)
Bash(launchctl start:*)
Bash(launchctl stop:*)
Bash(at:*)
Bash(systemctl:*)
```

### 3.4 FTP / SFTP / SCP (ate FASE 8 com ordem explicita)
```
Bash(sftp:*)
Bash(scp:*)
Bash(ftp:*)
Bash(lftp:*)
Bash(nc:*)
Bash(telnet:*)
```

### 3.5 Browser / MCPs caidos
```
Bash(google-chrome:*)
Bash(chromium:*)
Bash(chromedriver:*)
mcp__plugin_superpowers-chrome_chrome__use_browser
mcp__*__playwright__*
mcp__*__browser-mcp__*
```

### 3.6 Escrita em paths proibidos
```
Write(/Users/jesus/Desktop/STEMMIA Dexter/data/**)
Edit(/Users/jesus/Desktop/STEMMIA Dexter/data/**)
Write(/Users/jesus/Desktop/STEMMIA Dexter/MUTIRAO/**)
Write(/Users/jesus/Desktop/STEMMIA Dexter/PROCESSOS-PENDENTES/**)
Write(/Users/jesus/.pjeoffice-pro/**)
Write(/etc/**)
Write(/usr/**)
Write(/System/**)
Write(/Library/**)
```

### 3.7 Comunicacao externa via harness
```
RemoteTrigger
SendMessage                         # Telegram/Slack usa Python+.env diretamente
```

### 3.8 Servidor virt
```
Bash(prlsrvctl:*)
```

---

## 4. Env vars herdadas / requeridas

Definidas em `Maestro/.env` (chmod 600, **NAO COMMITAR**):

```
ANTHROPIC_API_KEY=sk-ant-...         # sensivel, nunca logar
TELEGRAM_BOT_TOKEN=...               # FASE 9
TELEGRAM_CHAT_ID=...
FTP_HOST=177.73.233.49                # FASE 8
FTP_USER=maestro@stemmia.com.br
FTP_PASS=...
FTP_PORT=21
OPENCLAW_STRATEGY=B
MAESTRO_ROOT=/Users/jesus/Desktop/STEMMIA Dexter/Maestro
PYTHON_BASE_ROOT=/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE
FALHAS_DB=/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json
CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-7
PYTHONIOENCODING=utf-8
LANG=pt_BR.UTF-8
LC_ALL=pt_BR.UTF-8
```

---

## 5. Liberacoes condicionais por fase

| Fase | O que libera | Gatilho |
|---|---|---|
| 7 Cron heartbeat | `Bash(launchctl load:*)`, `Bash(launchctl unload:*)` | plist homologado + ordem "ativa cron" |
| 8 Deploy FTP | `Bash(lftp:*)` para `FTP_HOST` apenas | ordem "deploy FTP" |
| 9 Telegram bot | Nada novo (Python+requests via stdlib ou lib instalada sob ask) | `TELEGRAM_BOT_TOKEN` em `.env` + ordem "roda bot" |

Cada liberacao precisa ser registrada em secao "Historico" deste documento.

---

## 6. Historico de mudancas

| Data | Mudanca | Motivo |
|---|---|---|
| 2026-04-23 01:35 | Criacao inicial | Consolidar permissoes do projeto + aplicar settings.json local |
| 2026-04-23 01:52 | Simplificada para "allow tudo exceto destrutivo" | Dr. Jesus pediu acelerar fluxo. ALLOW: Bash(*), WebFetch(*), WebSearch, Edit/Write dentro de STEMMIA Dexter/. ASK: rm, reset --hard, clean -fd, instaladores (pip/npm/brew), ssh, kill. DENY mantido rigoroso: rm -rf, sudo, open, git push, crontab -e, launchctl load, FTP/SFTP/SCP, paths proibidos (data, MUTIRAO, PJeOffice, /etc, /usr, /System, /Library), chrome MCP. |

---

## 7. Referencia cruzada

- Regras raiz: `~/.claude/CLAUDE.md`
- Regras projeto Stemmia: `~/Desktop/STEMMIA Dexter/CLAUDE.md`
- Regras Maestro: `~/Desktop/STEMMIA Dexter/Maestro/CLAUDE.md`
- Settings aplicado: `~/Desktop/STEMMIA Dexter/Maestro/.claude/settings.json`
- Falhas Python: `~/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json`
