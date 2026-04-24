# CHANGELOG — Maestro

## 2026-04-24 — Onda 2 + Onda 2.5 (verificador pipeline + auditoria CNJ)

### Adicionado
- `verificadores/auditar_numero_cnj_ficha.py` — varre 167 FICHAs, detecta e corrige numero_cnj divergente do nome da pasta. Encontrou 37 discrepâncias (2 CNJ errado, 35 campo vazio). Uso: `python3 auditar_numero_cnj_ficha.py [--fix]`
- `FLOWS/pericia_completa.sh` — etapa 6/6 adicionada: verificador de rastreabilidade de petição. exit 1=REVISAR (warning), exit 2=BLOQUEADA (aborta pipeline). Flags: `--skip-verificador`, `--peticao=<arquivo.md>` (#11)

### Modificado
- `verificadores/verificador_peticao_pdf.py` — dois fixes: (1) etapa 1.5 de token único (IDs numéricos ≥8 dígitos, datas, CNJs) com busca exata antes do fuzzy sliding window; (2) corpus expandido para incluir todos os *.txt da pasta (não só TEXTO-EXTRAIDO.txt). Resultado em Perícia 88: 0 SEM-ANCORA (era 4), score médio 73.9% (era 64.4%), veredito REVISAR (era BLOQUEADA) (#11)

## 2026-04-24 — Handoff sessao 5

- `HANDOFFS/HANDOFF-2026-04-24-04h54.md` — registro de encerramento da sessao

## 2026-04-24 — Sessao 5 (documentacao leiga GitHub + politica salvamento)

### Adicionado
- `docs/github/01-EXPLICACAO-LEIGA.md` — git/GitHub em portugues sem jargao, metafora fotografia
- `docs/github/02-COMO-SALVAR.md` — passo a passo de quando/como commitar e pushar
- `docs/github/03-FLUXO-VISUAL.md` — diagrama ASCII do ciclo de 16 passos de sessao
- `docs/github/04-GLOSSARIO.md` — glossario A-W + cola-parede com 11 comandos essenciais
- `docs/politica/POLITICA-SALVAMENTO.md` — regras explicitas de quando commitar/pushar

### Alterado
- `CLAUDE.md` — adicionada URL do repo, POLITICA-SALVAMENTO.md no inicio, secao politica resumida, referencias aos 5 novos docs
- `~/Desktop/STEMMIA Dexter/CLAUDE.md` — bloco Maestro expandido com comandos canonicos prontos para colar

### Deploy publico
- Uploaded para https://stemmia.com.br/maestro/ (4 guias + index) via FTP

---

## 2026-04-24 — Sessao 4 (auditoria + sincronizacao)

### Adicionado
- `futuro/plist-gateway-proposto.plist` — versao do plist gateway com ANTHROPIC_API_KEY persistente (placeholder no lugar do segredo).
- `futuro/B1-resolucao.md` — procedimento manual para aplicar plist (backup, substituir placeholder via sed, plutil -lint, reload, rollback).
- `legado-bootstrap/` — pasta nova; armazena 4 arquivos legados das sessoes 1-3 ja superados pelo HANDOFF.

### Movido (preservacao, sem perda)
- `CHECKPOINT-2026-04-23.md` → `legado-bootstrap/`
- `PLANO-OPERACIONAL-2026-04-23.md` → `legado-bootstrap/`
- `PROMPT-DR-JESUS-PARALELO.md` → `legado-bootstrap/`
- `PROMPT-RETOMAR-COMPLETO.md` → `legado-bootstrap/`

### Alterado
- `TASKS_NOW.md` reescrito: removido drift sobre BLK-A/B/C/D (resolvidos em sessoes 1-3); estado atual = aguardando decisao A/B/C.

### Pendente
- Aplicacao manual de B1 (depende de ordem explicita `ativa launchctl B1` por causa de PERMISSOES v2).
- ~~Decisao A/B/C pelo Dr. Jesus~~ → **escolheu B**, executado.

### OPCAO B executada (pipeline pericial /pericia [CNJ])
- `FLOWS/pericia_completa.sh` modificado: +30 linhas (`--dry-run`, pre-check de 5 deps, info PDF/TEXTO-EXTRAIDO/FICHA)
- `Maestro/bin/pericia` criado (wrapper, chmod +x)
- `FLOWS/USAGE-pericia.md` criado (manual uso, validacao, disponibilizar global)
- Validacao: dry-run com CNJ real `0012022-56.2012.8.13.0059` retorna exit 0 com 5/5 deps OK; CNJ inexistente retorna exit 1.
- 5 deps confirmadas: `src/automacoes/triar_pdf.py`, `ANALISADOR FINAL/analisador de processos/{pipeline_analise.py,consolidar_ficha.py,calcular_honorarios.py}`, `Maestro/banco-local/indexer_ficha.py`.

### FASE 3 (fechamento sessao 4)
- `HANDOFF-2026-04-24-SESSAO-04.md` criado
- `NEXT_SESSION_CONTEXT.md` reescrito
- `memory/2026-04-24.md` criado

### Auditoria executada
- Verificado estado real: OpenClaw v2026.4.21 instalado, 138 processos no SQLite, conversa Perplexity integra (4440 linhas), 6 scripts pipeline + integrate_llm.py em PYTHON-BASE/08-SISTEMAS-COMPLETOS/conversation_ingestion/, 8 docs OpenClaw em docs/openclaw-official/ (reais, nao placeholder), AGENTS/RULES/FLOWS/CRON/CONFIG completos.

---

## 2026-04-22 — Rodada 1 (bootstrap)

### Adicionado
- Estrutura base: AGENTS/, RULES/, FLOWS/, CRON/, CONFIG/, conversations/, memory/, logs/, reports/, docs/openclaw-official/.
- 8 agentes em AGENTS/*.md.
- INTEGRATION-PLAN.md, TASKS_MASTER.md, TASKS_NOW.md, NEXT_SESSION_CONTEXT.md.
- Captura integral da conversa Perplexity (135k+ chars, 4440 linhas) via chrome MCP em conversations/raw/.
- MEMORY.md + memory/2026-04-22.md.
- 5 relatorios sintetizados da conversa real (reports/conversation_*.md).
- Subprojeto Python em PYTHON-BASE/08-SISTEMAS-COMPLETOS/conversation_ingestion/ com 5 esqueletos + 3 templates + README.
- README.md, CLAUDE.md, OPENCLAW-ARCHITECTURE.md do Maestro.
- RULES/, FLOWS/01..08, CRON/ e CONFIG/ planejados (nao ativos).
- docs/openclaw-official/ com 8 arquivos placeholder/RESEARCH.
- reports/openclaw_{capabilities_summary, command_map, for_this_project}.md.
- reports/{model_options, cost_estimate, database_options, telegram_integration, stemmia_dashboard_plan}_initial.md.
- reports/progress_snapshot.md.
- reports/execution_report_round1.md.
- logs/round1_execution_log.md, logs/conversation_ingestion.log.

### Alterado
- Diretorio renomeado: openclaw-control-center -> Maestro-novo -> Maestro (final).

### Bloqueado
- Download documentacao OpenClaw oficial (fonte nao confirmada pelo Dr. Jesus).

### Nao executado (por regra)
- Ativacao de cron, envio ao Telegram, deploy ao site, uso de FTP.
- Instalacao de dependencias.
- Mudancas em producao do stemmia.com.br.
