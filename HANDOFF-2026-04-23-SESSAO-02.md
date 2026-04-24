# HANDOFF — Maestro sessao 1 -> sessao 2
**Fechamento sessao 1:** 2026-04-23 ~01:55
**cwd:** `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/`

---

## 1. RESUMO EM 5 LINHAS
Sessao 1 montou infraestrutura: OpenClaw v2026.4.21 rein­stalado com Haiku 4.5 padrao; 138 processos indexados em SQLite; dashboard HTML servido via http.server (verificado 200); 6 scripts Python do pipeline de ingestao + `test_pipeline.py` verde (8 turnos, 93 chunks, 406 action items). Credenciais migradas para `Maestro/.env` (chmod 600), TXT do Desktop apagado. Conversa Perplexity de 135 992 chars **PRESERVADA INTEGRA** em `Maestro/conversations/raw/perplexity_conversation_2026-04-22_full.md` — nunca sera tocada. Permissoes simplificadas para "allow tudo exceto destrutivo". Politica de preservacao: MEMORY.md sera INDICE com ponteiros para linhas do raw, nao substituto resumido.

---

## 2. PROMPT DE RETOMADA (colar na sessao 2)

```
Retomo Maestro sessao 2 em ~/Desktop/STEMMIA Dexter/Maestro/.

Ler antes de agir:
  1. PERMISSOES.md (politica de autorizacao aplicada)
  2. HANDOFF-2026-04-23-SESSAO-02.md (este arquivo)
  3. CRONOMETRO.md

Confirmar estado (verificacao minima, 30s):
  openclaw --version                                     # esperado: 2026.4.21
  sqlite3 banco-local/maestro.db "SELECT COUNT(*) FROM processos;"   # esperado: 138
  wc -l conversations/raw/perplexity_conversation_2026-04-22_full.md # esperado: 4440
  test -s .env && echo ".env OK"

Decisao imediata pendente: [ver secao 6]
Acao escolhida: ____
```

---

## 3. ESTADO VERIFICADO (evidencia em CRONOMETRO.md)

| Artefato | Path | Status |
|---|---|---|
| OpenClaw | `~/.openclaw/` (binario `/opt/homebrew/bin/openclaw`) | v2026.4.21 (f788c88), Haiku 4.5, workspace=`Maestro/workspace`, doctor 1-warning (device antigo) |
| Backup OpenClaw | `~/Desktop/openclaw-backup-2026-04-23.tar.gz` | 128 MB |
| Docs OpenClaw | `Maestro/docs/openclaw-official/` | 8 arquivos (56-83 linhas cada, 0 tags RESEARCH) |
| Pipeline scripts | `PYTHON-BASE/08-SISTEMAS-COMPLETOS/conversation_ingestion/` | 6 .py (ingest 315 / chunk 202 / extract 165 / gen_memory 214 / checkpoint 165 / test 144). `test_pipeline.py` exit 0 |
| DB | `Maestro/banco-local/maestro.db` | 138 linhas em `processos`, 0 em `documentos`/`tarefas`, 1 em `heartbeat` |
| Dashboard | `Maestro/dashboard/` | index.html + style.css + app.js + data.json (placeholder). HTTP 200 verificado |
| Conversa raw | `Maestro/conversations/raw/perplexity_conversation_2026-04-22_full.md` | 4440 linhas, 135 992 chars — **NAO TOCAR** |
| Env | `Maestro/.env` | chmod 600, 1021B, 13 chaves |
| Permissoes | `Maestro/.claude/settings.json` + `Maestro/PERMISSOES.md` | simplificada v2 |

---

## 4. DECISOES TOMADAS (nao revisar sem motivo)

| ID | Decisao | Aplicada |
|---|---|---|
| D1 | OpenClaw strategy = B (backup + restore seletivo) | sim |
| D2 | Default model OpenClaw = Haiku 4.5 | sim |
| D3 | DB = JSON fonte-da-verdade + SQLite indice + JSON estatico dashboard | sim |
| D4 | Permissoes = "allow tudo exceto destrutivo" | sim (settings.json v2) |
| D5 | FASE 7 cron heartbeat | **ADIADA** (backlog em `futuro/FASE-7-CRON-HEARTBEAT.md`) |
| D6 | Modelo para FASE 4 P6 integrador = **Sonnet 4.6** em single pass | **PENDENTE DE EXECUCAO** |
| D7 | Estrategia de preservacao: MEMORY.md indexa raw, nao resume | regra; aplicar no P6 |

---

## 5. BLOQUEIOS RESIDUAIS

**B1 — ANTHROPIC_API_KEY nao-persistente no gateway OpenClaw**
- Estado atual: seteada via `launchctl setenv` (volatil, some ao reboot).
- Opcoes:
  - **(a) plist LaunchAgent**: editar `~/Library/LaunchAgents/ai.openclaw.gateway.plist` adicionando bloco `EnvironmentVariables` com `ANTHROPIC_API_KEY`. Mais seguro (permissao so do usuario).
  - (b) plaintext: reconfigurar com `--secret-input-mode plaintext` e gravar no `openclaw.json`.
- **Recomendacao: (a)**. Executar antes de FASE 4 ou de qualquer uso do gateway apos reboot.

**B2 — Token node antigo (device `MacBook Pro de Jesus`) fora do baseline**
- Resolver com `openclaw devices rotate --device d38344... --role node`. Nao-bloqueante.

**B3 — Pairing gateway scope upgrade pendente aprovacao**
- Se usar: `openclaw devices approve fcd85dd2-a53d-4087-99e1-5a413f253eed`. Nao-bloqueante.

---

## 6. OPCOES PARA SESSAO 2 (escolher 1 ou encadear)

### OPCAO A — FASE 4 P6 integrador LLM (~25 min, custo ~$0.20)
Escrever `PYTHON-BASE/08.../conversation_ingestion/integrate_llm.py`:
- Modelo: **Sonnet 4.6** (claude-sonnet-4-6) via Anthropic SDK (`pip install anthropic` — pede ask)
- Input: `ingest.json` + `chunks.json` + `actions.json` (ja produzidos pelos scripts P1-P3)
- Output: sobrescreve `Maestro/MEMORY.md` + `Maestro/memory/2026-04-23.md` + `Maestro/reports/conversation_perplexity.md`
- **Preservacao obrigatoria:** cada item gerado cita `[fonte: raw linhas NNNN-NNNN]`. Sem isso, rejeita.
- Rodar UMA VEZ. Diff antes de commitar.

### OPCAO B — Pipeline pericial minimamente viavel `/pericia [CNJ]` (~55 min)
Entregavel: Dr. Jesus digita `/pericia 5000237-19.2022.8.13.0396` e o sistema:
1. Baixa PDFs via PJe (Parallels/Windows, script legado existe em `~/Desktop/ANALISADOR FINAL/scripts/`)
2. Extrai texto
3. Roda primeira analise (classe, tipo, honorario fixado?)
4. Se nao fixado -> sugere proposta de honorarios automatica
5. Grava `FICHA.json`, indexa no `maestro.db`

Trabalho:
- Agente Explore-Dexter: mapear 64 scripts existentes, identificar aquisicao + analise + proposta
- Agente Wrapper: criar `Maestro/FLOWS/pericia_completa.sh` orquestrando na ordem
- Agente Test: rodar com 1 CNJ real de mutirao

### OPCAO C — Verificador de peticao com ancoragem PDF (~40 min)
Entregavel: `python3 verificar.py peticao.md processo.pdf -> verificacao.html`
- Extrai texto do PDF (pdfplumber; `pip install` ask)
- Para cada paragrafo da peticao, fuzzy match contra PDF
- Output HTML 2 colunas: paragrafo da peticao | trecho fonte no PDF + numero de pagina
- Linka visualmente cada afirmacao -> origem real. Evita alucinacao em peticoes geradas.

### OPCAO D — FASE 8 deploy FTP (~45 min)
Upload `Maestro/dashboard/` para `FTP_HOST` do `.env` via `lftp` (liberacao temporaria de deny). `.htaccess` basic auth.

### OPCAO E — FASE 9 bot Telegram (~90 min)
`Maestro/telegram/bot.py` com python-telegram-bot (pip ask). Comandos `/status`, `/urgentes`, `/ajuda`. Polling (nao webhook).

### Encadeamento sugerido (cabe em 2h se sessao 2 comecar ~02:00)
1. **B** (pipeline pericial) — 55 min — **valor real para pericias desta madrugada**
2. **A** (P6 Sonnet) — 25 min — preserva conversa Perplexity com indexacao
3. **C** (verificador PDF) — 40 min — anti-alucinacao em peticoes

FASE 7/8/9 ficam para outra sessao.

---

## 7. CONTEXTO DO DR. JESUS (humano)

- **Meta madrugada 2026-04-23:** fazer pericias reais ate ~03:00. Sistema e meio, nao fim.
- **Sonho declarado:** automatizar burocracia (aceite, proposta, extracao) para sobrar tempo de analise clinica.
- **Medo explicito:** perder conteudo valioso da conversa Perplexity ao sumarizar. Por isso D6=Sonnet e D7=indexar-nao-resumir.
- **Perfil:** TEA + TDAH, memoria comprometida. Tudo precisa ficar em arquivo, nao em cabeca.

---

## 8. HAIKU 4.5 vs SONNET 4.6 — comparacao pratica

| Dimensao | Haiku 4.5 | Sonnet 4.6 |
|---|---|---|
| Tarefa ideal | extracao, classificacao, regex enriquecido, chunking, resposta rapida | sintese, nuance, decisao, captura de intencao, texto que vai ser lido |
| Velocidade | ~3x Sonnet | baseline |
| Custo relativo | ~1x | ~3x Haiku |
| Risco de perda de ideia sutil | **medio** (corta nuance em sintese) | **baixo** |
| Janela | ampla (adequada a 135k chars) | ampla |
| Uso recomendado no Maestro | pipeline rotineiro (ingest + classify + indexer), bot Telegram, queries OpenClaw | **conversa Perplexity** (single pass, valor alto, roda 1x), laudo final exige Opus |

**Ordem de custo/qualidade:** Haiku 4.5 < Sonnet 4.6 < Opus 4.7.
**Preservacao:** independente do modelo, **conversa raw nao sera alterada**. LLM produz anotacoes que apontam para a raw; a raw continua sendo a verdade.

**Custo estimado de 1 run Sonnet na conversa Perplexity (135k chars ~ 34k tokens):** ordem de grandeza de centavos de dolar, nao dolares. Rodar uma unica vez. Aceitavel.

---

## 9. REGRAS HERDADAS (sessao 2 nao pode quebrar)

- Hook anti-mentira ativo: qualquer afirmacao de estado (OK, verificado, em pe) exige Bash/Read/Grep previo. Verbos proibidos sem evidencia: "feito", "pronto", "concluido", "funcionando", "corrigido".
- Subagentes: Opus 4.7 (`CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-7` no env do settings.json).
- Sem acento/espaco/cedilha em paths novos.
- `.env` chmod 600. Nunca logar valor. Nunca commitar (ja no .gitignore).
- `ANTHROPIC_API_KEY` em script Python: `grep ^ANTHROPIC_API_KEY .env | cut -d= -f2-` ou `python-dotenv` — nunca colar em stdout.
- Notificar em marcos: `osascript -e 'display notification "..." with title "Maestro" sound name "Glass"'`.
- Atualizar `CRONOMETRO.md` a cada marco.
- Ao fim da sessao 2: atualizar HANDOFF criando `HANDOFF-2026-04-23-SESSAO-03.md`.

---

## 10. ARQUIVOS CRIADOS/MODIFICADOS SESSAO 1

Novos:
- `Maestro/.env` (600)
- `Maestro/.gitignore`
- `Maestro/.claude/settings.json`
- `Maestro/PERMISSOES.md`
- `Maestro/HANDOFF-2026-04-23-SESSAO-02.md` (este)
- `Maestro/futuro/FASE-7-CRON-HEARTBEAT.md`
- `Maestro/banco-local/schema.sql`
- `Maestro/banco-local/indexer_ficha.py`
- `Maestro/banco-local/exportar_dashboard.py`
- `Maestro/banco-local/maestro.db`
- `Maestro/dashboard/index.html`
- `Maestro/dashboard/style.css`
- `Maestro/dashboard/app.js`
- `Maestro/dashboard/data.json`
- `Maestro/docs/openclaw-official/{cli_overview,memory,dashboard,cron,agents,tasks,status_health,plugins_hooks}.md`
- `PYTHON-BASE/08-SISTEMAS-COMPLETOS/conversation_ingestion/{ingest,chunk,extract,generate_memory,checkpoint}_*.py` (completados)
- `PYTHON-BASE/08-SISTEMAS-COMPLETOS/conversation_ingestion/test_pipeline.py`
- `~/Desktop/openclaw-backup-2026-04-23.tar.gz`
- `~/.openclaw/` (reinstalado + configurado)

Modificados:
- `Maestro/CLAUDE.md` (+ secao PERMISSOES)
- `Maestro/CRONOMETRO.md` (timestamps)

Apagados:
- `~/Desktop/credenciais-maestro-2026-04-23.txt` (conteudo migrado para `.env`)

---

## 11. PATHS CRITICOS (atalhos)

```
# Processos reais
/Users/jesus/Desktop/ANALISADOR FINAL/processos/            # 142 FICHA.json
/Users/jesus/Desktop/ANALISADOR FINAL/scripts/              # scripts legados de aquisicao+analise

# Automacao nova
~/Desktop/STEMMIA Dexter/src/automacoes/                    # (alias ~/stemmia-forense/automacoes)
~/Desktop/STEMMIA Dexter/src/hooks/                         # anti-mentira

# PJe
~/Desktop/STEMMIA Dexter/PJE-INFRA/                         # perfis Chrome/Playwright
~/.pjeoffice-pro/                                           # NAO MOVER (path hardcoded)

# Base de falhas (consulta obrigatoria antes de Python de automacao)
~/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json

# Maestro
~/Desktop/STEMMIA Dexter/Maestro/
```

---

## 12. BACKLOG (carry-over)

- [ ] FASE 7 cron heartbeat (adiada — ver `futuro/FASE-7-CRON-HEARTBEAT.md`)
- [ ] Fixar ANTHROPIC_API_KEY via plist (B1)
- [ ] Rotacionar token device antigo (B2)
- [ ] Aprovar pairing gateway (B3)
- [ ] FASE 8 deploy FTP
- [ ] FASE 9 bot Telegram
- [ ] Populador de `documentos` e `tarefas` em maestro.db (campos ficaram NULL na maioria das FICHAs)

---

## 13. CRONOMETRO

```
Sessao 1: 00:57 -> 01:55 (~58 min de trabalho)
Fim da sessao 1. Sessao 2 pode comecar limpa a qualquer momento.
Meta Dr. Jesus: pericias reais ate 03:00.
Orcamento sessao 2 sugerido: 2h (ate ~04:00) encadeando B + A + C.
```
