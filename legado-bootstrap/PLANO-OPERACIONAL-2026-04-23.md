# PLANO OPERACIONAL — Maestro — 2026-04-23

Plano com **times de agentes em paralelo** para minimizar tempo do Dr. Jesus e maximizar throughput.

## Premissa
- Dr. Jesus roda `PROMPT-DR-JESUS-PARALELO.md` em outra aba/sessao.
- IA principal (esta sessao) executa fases que nao dependem de credencial enquanto isso.
- Sincronizacao: quando credencial chegar, IA integra.

## Times de agentes

| Time | Agentes | Objetivo | Paralelo com |
|---|---|---|---|
| **T-OpenClaw** | 1 agente general-purpose | backup + uninstall + reinstall + integrar com Maestro | T-Docs |
| **T-Docs** | 1 agente Explore | clonar `github.com/openclaw/openclaw`, mapear docs, preencher os 8 placeholders RESEARCH | T-OpenClaw |
| **T-Python** | 5 agentes general-purpose em paralelo | 1 script cada (ingest, chunk, extract, generate, checkpoint) | T-DB, T-Dashboard |
| **T-DB** | 1 agente general-purpose | schema SQLite + script indexer que varre `ANALISADOR FINAL/processos/*/FICHA.json` | T-Python, T-Dashboard |
| **T-Dashboard** | 1 agente frontend-developer | HTML vanilla MVP + JSON estatico loader | T-Python, T-DB |
| **T-Cron** | 1 agente general-purpose | gerar launchd plist para J07 (heartbeat), ativacao manual depois | sequencial pos T-Python |
| **T-Telegram** | 1 agente general-purpose | stub -> real, usando TOKEN do .env | sequencial pos-credencial |
| **T-Deploy** | 1 agente general-purpose | script lftp upload, testar com arquivo dummy primeiro | sequencial pos-FTP |

## Sequenciamento real (gantt textual)

```
Tempo    0h       1h       2h       3h       4h       5h       6h       7h
         |========|========|========|========|========|========|========|
T-OpenClaw   [###########]                                                   backup+uninstall+reinstall+integrar
T-Docs       [###########]                                                   clonar+preencher 8 docs
T-Python              [####################]                                 5 scripts em paralelo
T-DB                  [#############]                                        schema+indexer
T-Dashboard                  [####################]                          HTML+JSON loader
T-Cron                                  [######]                             plist heartbeat
T-Telegram                                     [############]                integracao real (apos token)
T-Deploy                                              [######]               upload dashboard (apos FTP)
```

Dois pontos de sincronia bloqueantes:
- **S1 (1h):** T-OpenClaw precisa saber a decisao A/B/C do Dr. Jesus.
- **S2 (3h):** T-Telegram precisa TOKEN. T-Deploy precisa FTP. T-Python (opcional LLM) precisa API key.

Se Dr. Jesus terminar o prompt paralelo em 30min, S1/S2 nao bloqueiam nada.

## Fases detalhadas

### FASE 1 — OpenClaw reset + reintegracao (time T-OpenClaw, 45-75 min)
Sub-tarefas (sequenciais no mesmo time):
1. Backup: `tar czf ~/Desktop/openclaw-backup-2026-04-23.tar.gz ~/.openclaw` (200MB, ~30s)
2. Listar o que tem em `~/.openclaw/credentials/` e perguntar se salva separado.
3. `npm uninstall -g openclaw`
4. `rm -rf ~/.openclaw` (SO se estrategia A ou B escolhida)
5. `npm i -g openclaw`
6. `openclaw onboard` — reconfigurar auth Anthropic.
7. Ajustar default model: trocar Sonnet por **Haiku 4.5** para cron/hooks, Opus so quando pedido explicitamente.
8. Apontar workspace para `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/workspace` (criar pasta).
9. Testar: `openclaw doctor`, `openclaw --version`, rodar um comando simples para confirmar.

**Output esperado:** `openclaw doctor` sem erros + openclaw.json novo em ~/.openclaw + memoria vazia em main.sqlite.

### FASE 2 — Docs OpenClaw (time T-Docs, 30-45 min) — PARALELO com Fase 1
1. `cd /tmp && gh repo clone openclaw/openclaw openclaw-src`
2. Mapear arquivos: `ls openclaw-src/docs/`, `ls openclaw-src/packages/`, ler `README.md`.
3. Copiar conteudo real para 8 placeholders:
   - cli_overview.md
   - memory.md
   - dashboard.md
   - cron.md
   - agents.md
   - tasks.md
   - status_health.md
   - plugins_hooks.md
4. Cada arquivo: cabecalho com `source: github.com/openclaw/openclaw/<path>` + data de pull.
5. Se algum topico nao existir nos docs oficiais, marcar `## NAO DOCUMENTADO OFICIALMENTE` e remover RESEARCH.

**Output esperado:** 8 arquivos em `Maestro/docs/openclaw-official/*.md` sem tag RESEARCH no topo.

### FASE 3 — Python pipeline real (time T-Python, 2-3h) — PARALELO com Fase 2 apos Fase 1
5 agentes, 1 para cada script. Cada agente recebe:
- Esqueleto atual em `PYTHON-BASE/08-SISTEMAS-COMPLETOS/conversation_ingestion/*.py`
- Template de output esperado
- Exemplo de entrada (conversa Perplexity de 135k chars)
- Regra: ler `PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json` antes; citar IDs de falhas no codigo.

1. **Agente P1:** `ingest_conversation.py` — filtrar UI_NOISE, normalizar markdown, metadata de entrada.
2. **Agente P2:** `chunk_conversation.py` — detectar turnos USER/PERPLEXITY, split por tema/decisao.
3. **Agente P3:** `extract_action_items.py` — regex ACTION_VERBS, extrair prioridade/horizonte.
4. **Agente P4:** `generate_memory_files.py` — escrever MEMORY.md + memory/YYYY-MM-DD.md + reports/*.md.
5. **Agente P5:** `generate_session_checkpoint.py` — atualizar NEXT_SESSION_CONTEXT + TASKS_NOW.

Apos entrega dos 5, **agente P6 (integrador):** rodar o pipeline completo na conversa Perplexity salva. Validar output vs reports existentes (sanity check). Se houver LLM (API key disponivel), usar Haiku em P2 e P4 para melhorar qualidade; senao, regex puro.

**Output esperado:** 5 scripts funcionais + pipeline rodado end-to-end no arquivo real + diff entre memoria atual e memoria gerada.

### FASE 4 — Rodar pipeline na conversa (15 min) — dependente de Fase 3
Ja coberta pelo agente P6 acima.

### FASE 5 — SQLite index (time T-DB, 1-1.5h) — PARALELO com Fase 3
1. Definir schema minimo em `Maestro/banco-local/schema.sql`:
   - tabela `processos` (cnj PK, autor, reu, cid_principal, data_fatos, status, comarca, valor_causa, path_ficha)
   - tabela `documentos` (id, cnj FK, tipo, data, path, hash)
   - tabela `tarefas` (id, cnj FK, tipo_peticao, prazo, status)
   - tabela `heartbeat` (timestamp, tipo, payload_json)
2. Script `indexer_ficha.py` em `Maestro/banco-local/`:
   - Varrer `~/Desktop/ANALISADOR FINAL/processos/*/FICHA.json`
   - Upsert em `Maestro/banco-local/maestro.db`
3. Script `exportar_dashboard.py`:
   - Consulta agregada (contagem por status, comarca, cid) -> gera `Maestro/dashboard/data.json`

**Output esperado:** `maestro.db` com ~40 processos + `dashboard/data.json` valido.

### FASE 6 — Dashboard MVP (time T-Dashboard, 2-3h) — PARALELO com Fase 3+5
1. HTML vanilla em `Maestro/dashboard/index.html`:
   - 4 cards grandes: total processos, prazos urgentes, pericias semana, ultima atualizacao
   - Busca por CNJ (filtro JS no client)
   - Lista de 10 processos mais recentes
2. CSS em `Maestro/dashboard/style.css`:
   - Reutilizar paleta/fonts do "Planner Stemmia" existente (se arquivo disponivel; se nao, Inter + paleta neutra)
   - Contraste alto, sem animacao
3. JS em `Maestro/dashboard/app.js`: fetch `data.json` + render.
4. Testar local: `python3 -m http.server 8000` + abrir `localhost:8000/dashboard/`.

**Output esperado:** dashboard abre sem erros, mostra numeros reais dos 40 processos.

### FASE 7 — Cron J07 heartbeat (time T-Cron, 30 min) — pos Fase 3
1. Criar `~/Library/LaunchAgents/com.stemmia.maestro.heartbeat.plist`.
2. Roda a cada 30min: `python3 Maestro/scripts/heartbeat.py` que escreve linha em `Maestro/logs/heartbeat.log`.
3. **Nao ativar** (`launchctl load`) sem autorizacao. Arquivo fica pronto, Dr. Jesus aciona quando quiser.

**Output esperado:** plist valido + script testavel manualmente + instrucao de ativacao 1-liner.

### FASE 8 — Deploy dashboard (time T-Deploy, 30-45 min) — dependente de FTP
1. Criar `Maestro/scripts/deploy.sh` com `lftp` (nao curl ftp, lftp resume melhor).
2. Testar com arquivo dummy `hello-maestro.txt` primeiro para confirmar auth e permissoes.
3. Se OK, upload de `Maestro/dashboard/` -> `stemmia.com.br/dashboard-maestro/`.
4. Adicionar `.htaccess` com basic auth se plano suportar.

**Output esperado:** URL publica (privada por auth) respondendo com dashboard.

### FASE 9 — Telegram bot real (time T-Telegram, 1-1.5h) — dependente de TOKEN
1. Script `Maestro/telegram/bot.py`:
   - Lib: `python-telegram-bot` (mas **consultar falhas.json primeiro**).
   - Comando `/status`: le `logs/heartbeat.log` -> responde ultima linha.
   - Comando `/urgentes`: le SQLite -> lista 5 prazos proximos.
   - Comando `/ajuda`: lista comandos.
2. Rodar em modo polling (nao webhook — evita expor porta).
3. Testar manualmente, depois adicionar a cron J02 para reiniciar se cair.

**Output esperado:** bot respondendo no chat do Dr. Jesus.

## Resumo de tempo

| Trilha | Sem paralelismo | Com paralelismo (times) | Ganho |
|---|---:|---:|---:|
| Total serial | 8-12h | — | — |
| Total com T-Python em 5 agents + T-Docs/T-DB/T-Dashboard paralelos | — | **3.5-5h** reloginho + ~35min do Dr. Jesus em prompt paralelo | ~55% mais rapido |

Em sessoes de 90min TDAH-amigaveis: **3 sessoes** em vez de 6-8.

## Riscos

| Risco | Mitigacao |
|---|---|
| Uninstall do ~/.openclaw perde credenciais do WhatsApp | Backup tar.gz antes + restore manual se precisar |
| Scripts Python quebram com conversas muito grandes | Chunking com limite de 50k chars por passagem |
| FTP nuvemhospedagem bloqueia upload (permissao) | Testar com dummy primeiro (Fase 8.2) |
| Telegram bot polling consome bateria | Rodar so no desktop, nao no iPhone |
| LLM da resposta ruim sem contexto | Passar MEMORY.md + CLAUDE.md do Maestro no prompt system |

## Rollback por fase

Cada fase tem 1 acao de rollback de 1 minuto:
- F1: reinstalar backup `tar xzf ~/Desktop/openclaw-backup-2026-04-23.tar.gz -C /`
- F2: `rm -rf Maestro/docs/openclaw-official/*.md` e restaurar placeholders do git
- F3-9: `git checkout Maestro/` (arquivos ainda nao comitados? entao so apagar os novos)
