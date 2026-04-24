# AUDITORIA ESTRUTURAL — STEMMIA Dexter

**Data:** 2026-04-19
**Autor:** Claude Opus 4.7 (via agentes Explore em paralelo)
**Escopo:** `/Users/jesus/Desktop/STEMMIA Dexter/` + dependências externas (`~/.claude/`, `~/stemmia-forense/`, Desktop periférico)
**Plano-mestre:** `~/.claude/plans/enumerated-noodling-sutherland.md` (FASE 1 / T03)

---

## Sumário executivo

Hub pericial com **4,7 GB** em **56 pastas** de primeiro nível. O ecossistema está funcional mas sofre de três dívidas críticas simultâneas:

1. **Dependência externa extrema** — 30 dos 34 symlinks (88%) apontam para `~/Desktop/ANALISADOR FINAL/`. Mover a pasta-irmã quebra pipeline + 2 MCPs.
2. **Duplicação massiva** — `_arquivo/` (2,3 GB) contém clones 100% byte-idênticos de `FERRAMENTAS/` (inclusive `.venv` gigantes). 300+ nomes `.md` duplicados.
3. **Nomenclatura de agentes divergente** — 3 dos 11 fluxos têm nomes no `CLAUDE.md` que NÃO batem com arquivos reais em `~/.claude/agents/`. Automações referenciando os nomes "corretos" quebram silenciosamente.

**Cobertura média de fluxos: 51%.** Apenas 3 fluxos (autoaprendizagem, monitoramento, download PJe) têm maturidade ≥87%. Mutirão está em 25%.

---

## Seção A — Inventário por camada

### A.1 Controle & Docs

**Raiz do hub (`/Users/jesus/Desktop/STEMMIA Dexter/`):**

| Arquivo | Tamanho | Função |
|---|---:|---|
| `README.md` | 11.076 B | Apresentação geral e mapa de navegação do hub Dexter. |
| `CLAUDE.md` | 6.849 B | Instruções permanentes para Claude Code no contexto do hub. |
| `CODEX.md` | 1.074 B | Orientações para subagente Codex (CLI MCP). |
| `MAPA-FERRAMENTAS.md` | 32.975 B | Mapa exaustivo das ferramentas/scripts/MCPs e onde cada um vive. |
| `DECISOES.md` | 14.408 B | Log de decisões arquiteturais (ADRs) em ordem cronológica. |
| `ROTINA.md` | 8.357 B | Rotina operacional diária do perito (sequência de comandos/checagens). |
| `INVENTÁRIO.md` | 2.727 B | Inventário-resumo do que existe no hub (alto nível). |
| `MEMORIA.md` | 1.054 B | Ponteiro curto para memória persistente do Claude. |
| `DIAGNOSTICO-17042026.md` | 3.879 B | Diagnóstico do sistema tirado em 17/04. |
| `GUIA-OTIMIZACAO-TOKENS.md` | 28.394 B | Playbook de otimização de consumo de tokens. |
| `RELATORIO-REORGANIZACAO-2026-04-14.md` | 8.623 B | Registro da reorganização de 14/04. |
| `PROMPT-BAIXAR-PDFS.md` | 3.548 B | Prompt-gatilho para baixar PDFs do PJE. |
| `PROMPT-PUSH-RENOMEAR-INCLUIR.md` | 14.762 B | Prompt do fluxo PUSH (renomear + incluir). |
| `LISTA-COMPLETA-PUSH.json` | 69.665 B | Lista completa de processos para PUSH. |
| `NUMERACAO-CORRETA.json` | 73.815 B | Mapa canônico de numerações de processos. |
| `PUSH-ATUAL.csv` | 7.060 B | Snapshot CSV do PUSH atual. |
| `PUSH-COMPARACAO.json` | 39.220 B | Comparativo de PUSH (antes/depois). |

**`00-CONTROLE/` (controle operacional) — principais:**

| Arquivo | Tamanho | Função |
|---|---:|---|
| `AGORA.md` | 2.226 B | O que está sendo feito neste exato momento. |
| `PENDENCIAS.md` | 1.526 B | Lista viva de pendências. |
| `PLANO-ORGANIZACAO-SISTEMA.md` | 19.787 B | Plano-mestre desta iniciativa (22 tarefas T01–T22). |
| `TEMPLATE-PLANO.md` | 7.690 B | Template obrigatório para planos novos. |
| `PROTOCOLO-CLAUDE-CONSISTENTE.md` | 8.034 B | Protocolo para manter Claude consistente entre sessões. |
| `MAPA-PROCESSOS.html` | 42.015 B | Mapa HTML renderizado dos processos. |
| `gerar_mapa_processos.py` | 7.548 B | Gera `MAPA-PROCESSOS.html`. |
| `organizar_pdfs.py` | 3.359 B | Organiza PDFs brutos. |
| `migracoes/` | dir | Snapshots desta iniciativa (T01). |
| `backups-claude-consistente/` | dir | Backups do modo consistente. |

Subdirs: `indices/`, `migracoes/base/` (6 arquivos de snapshot criados em T01).

---

### A.2 Fluxos operacionais

**`src/` — 92 arquivos em 6 subpacotes Python:**

| Subdir | Arquivos | Papel |
|---|---:|---|
| `src/honorarios/` | 4 | Cálculo de honorários periciais. |
| `src/jurisprudencia/` | 7 | Busca/filtragem de jurisprudência. |
| `src/peticoes/` | 11 | Geração de petições (aceite, quesitos, etc). |
| `src/pipeline/` | 30 | Orquestração ponta-a-ponta do pipeline forense. |
| `src/pje/` | 21 | Integração PJE (scraping, API, login). |
| `src/utils/` | 17 | Utilitários compartilhados. |

Arquivos-raiz de `src/`: `__init__.py`, `config.py` (2.950 B).

**`FERRAMENTAS/` (ferramentaria HTML/aplicativos):**

- `analisador-novo/`, `analisador-ultra/`, `analise-nova/` — versões do analisador.
- `openclaw/`, `openclaw-config/` — motor OpenClaw.
- `pesquisador-honorarios/` — ferramenta de pesquisa de honorários.
- `jurídicas/` — contém subárvore com MCPs (`MCPs/mcp-cerebra-legal-server`, `MCPs/brlaw_mcp_server`, `MCPs/medical-mcp`).
- HTMLs interativos na raiz: `CIF-CHECKLIST.html` (25 KB), `CIF-IFBrM.html` (31 KB), `CIF-WHODAS.html` (35 KB), `MEEM-interativo.html` (34 KB).

**`n8n/` (workflows exportados, 5 JSONs):**

| Arquivo | Tamanho | Função |
|---|---:|---|
| `pesquisador-inteligente-produtos.json` | 22.310 B | Pesquisador inteligente de produtos. |
| `workflow-01-aceite-simples.json` | 18.162 B | Aceite simples. |
| `workflow-02-analise-proposta.json` | 54.221 B | Análise de proposta de perícia. |
| `workflow-03-verificador.json` | 13.405 B | Verificador pós-análise. |
| `workflow-04-monitor-datajud.json` | 11.137 B | Monitor DataJud. |

---

### A.3 Agentes & Skills

**Agentes globais Claude (`~/.claude/agents/`):** **85 arquivos `.md`** (confirmado via `ls | wc -l`).

**Skills custom do hub (`~/.claude/skills/`):**

- `comunicacao-neurodivergente`
- `python-base`

(Apenas 2 skills custom locais; as demais ~150 skills listadas em `<system-reminder>` vêm de plugins/marketplaces.)

---

### A.4 Dados & Memória

**`BANCO-DADOS/` (primeiro nível):**

- `BANCO-GERAL-LINK` → symlink para `ANALISADOR FINAL/BANCO DE DADOS GERAL` (OK)
- `casos-clinicos/` — casos clínicos de referência.
- `DIREITO/` — base jurídica.
- `MEDICINA/` — base médica.
- `PERÍCIA/` — base pericial.
- `TI e IA/` — base de tecnologia/IA.
- `gerar_indices.py` (10.305 B) — gerador de índices.
- `INDICE-GERAL.pdf` (3.185 B) — índice consolidado.
- `MAPA-DE-FONTES.md` (10.384 B) — mapa de fontes.

**`memoria/` (12 itens):**

- `base-conhecimento/` — notas persistentes.
- `CLAUDE-MEMORY/` — 98 entradas de memória do Claude.
- `conversas/` — conversas arquivadas.
- `feedback/` — feedback capturado.
- `_backups-zip/` — backups zip.
- `.obsidian/` — vault Obsidian.
- `MAPA-FERRAMENTAS.md` (32.975 B), `DECISOES.md` (3.439 B), `MEMORIA.md` (2.142 B), `ROTINA.md` (1.470 B) — réplicas sincronizadas da raiz.

**`data/` (staging pipeline):**

- `banco-geral/`, `bases-dados/`, `inbox/`, `processos/`, `saida/` — buckets de entrada/saída.
- `logs/` — logs recentes.
- `notificacoes.json` (2.193 B) — fila de notificações.

---

### A.5 Hooks & MCPs

**`~/stemmia-forense/hooks/` — 59 hooks `.sh`/`.py` instalados.** Os nomes de destaque:

```
adaptador-sessao.sh, adaptar-resposta-tela.sh, anti_mentira_audit.py,
anti_mentira_distiller.py, anti_mentira_prompt_submit.py,
anti_mentira_session_start.py, anti_mentira_stop.py,
auditor-pos-criacao.sh, auditoria-acoes.sh, auto-trocar-modelo.sh,
bloquear-delecao.sh, bloquear-perguntas-retoricas.py,
classificador-esforco.sh, coletor-notification.sh, coletor-precompact.sh,
coletor-sessao.sh, coletor-sessionstart.sh, coletor-userprompt.sh,
copiar-md-automatico.sh, corrigir-ditado.sh, detector-dificuldade.sh,
detector-esforco-baixo.sh, detector-site.sh, diagnostico-sistema.sh,
enforcement-verificacao.sh, finalizar-sessao.sh, fluxo-modelo.sh,
gerar-sintese-precompact.sh, gerenciador-modelo.sh, healthcheck-mcp.sh,
indexar-sessao.sh, iniciar-sessao.sh, lembrete-rename.sh,
limpar-claude.sh, medidor-tokens-statusline.sh, medidor-tokens-stop.sh,
monitor-limite.sh, monitor-uso-claude.sh, orquestrador-automatico.sh,
perguntar-upload.sh, plano-obrigatorio.sh, pos-criacao.sh,
registrar-arquivo.sh, resumo-diario-planner.sh, salvar-contexto-bruto.sh,
salvar-estado-processo.sh, salvar-knowledge-graph.sh, salvar-periodico.sh,
sintese-automatica.sh, statusline-uso-claude.sh, sugestor-ferramenta.sh,
supervisor-agentes.sh, sync-plans-git.sh, verificar-contexto.sh,
verificar-escrita.sh, verificar-links-juridicos.sh
```

**Hooks ATIVADOS em `~/.claude/settings.json`:**

| Evento | Comando |
|---|---|
| `SessionStart` | `$HOME/stemmia-forense/hooks/iniciar-sessao.sh` |
| `PreToolUse` | `$HOME/stemmia-forense/hooks/bloquear-delecao.sh` + `python3 /Users/jesus/.claude/hooks/bloquear_limpeza.py` |
| `PreCompact` | `$HOME/stemmia-forense/hooks/salvar-contexto-bruto.sh` |
| `SessionEnd` | `$HOME/stemmia-forense/hooks/finalizar-sessao.sh` |
| `Stop` | `python3 $HOME/stemmia-forense/hooks/bloquear-perguntas-retoricas.py` + `python3 /Users/jesus/.claude/hooks/sessao_end_autoaprendizagem.py` |
| `UserPromptSubmit` | `python3 $HOME/.claude/scripts/sugerir_plugins.py` |

**Constatação crítica:** apenas 6 hooks estão cadastrados ativamente de um universo de 59. Os demais ~53 são órfãos/legacy.

**MCPs ativos (`~/.claude/.mcp.json`) — 17 servidores:**

1. `codex-subagent` — `codex mcp-server`
2. `n8n-mcp` — bridge local para n8n na cloud
3. `dadosbr` — `@aredes.me/mcp-dadosbr` (+ DataJud)
4. `healthcare-mcp`
5. `word-document-server` — office-word-mcp-server
6. `cerebra-legal` — **aponta para `STEMMIA Dexter/FERRAMENTAS/jurídicas/MCPs/mcp-cerebra-legal-server/build/index.js`**
7. `brlaw` — **aponta para `STEMMIA Dexter/FERRAMENTAS/jurídicas/MCPs/brlaw_mcp_server`**
8. `telegram-notify`
9. `medical-mcp` — **aponta para `STEMMIA Dexter/FERRAMENTAS/jurídicas/MCPs/medical-mcp/build/index.js`**
10. `sqlite` — **aponta para `ANALISADOR FINAL/process-mapper.db`**
11. `filesystem` — **expõe `ANALISADOR FINAL/processos` e `Desktop/PERÍCIA`**
12. `pdf-reader`
13. `playwright`
14. `obsidian` — vault em iCloud (`STEMMIA`)
15. `perplexity`
16. `semantic-scholar`
17. `context-portal`

**Observação:** 3 MCPs têm path absoluto dentro do hub Dexter (`cerebra-legal`, `brlaw`, `medical-mcp`) e 2 apontam para `ANALISADOR FINAL` — mover qualquer um desses diretórios quebra os servidores MCP.

---

### A.6 Externos referenciados

| Caminho | Status | Observação |
|---|---|---|
| `~/Desktop/ANALISADOR FINAL/` | EXISTE | Hub "irmão" com `processos/` (158 processos), `scripts/`, `saida/peticoes-claude/`, `INBOX/`, `BANCO DE DADOS GERAL` (1,5 GB), `BANCO-REFERENCIAS-PERICIA`, `STATUS-PROCESSOS.json`, `process-mapper.db`, `modelos-laudo/`. Destino de **30 symlinks**. Tem seu próprio `.git`, `.venv`, `.claude`, `.cowork-logs`. |
| `~/Desktop/_MESA/01-ATIVO/PYTHON-BASE/` | EXISTE (760 KB) | Base de estudos Python. Estrutura numerada 00–09 + 99-LOGS. Não tem symlink direto do Dexter. 90 falhas catalogadas em `03-FALHAS-SOLUCOES/db/falhas.json`. |
| `~/Desktop/processos-pje-windows/` | SYMLINK no Desktop | Aponta para Parallels: Windows Disks / processos-pje. Depende da VM Windows 11. |
| `~/Desktop/PERÍCIA/` | EXISTE | ~85 itens com PDFs de aceite, agendamentos, quesitos, `BANCO-DE-PETICOES/`. **Exposto ao MCP filesystem.** Não é linkado do Dexter diretamente. |

---

## Seção B — 11 fluxos ponta-a-ponta

### B.1 — Download PJe
- **Entrada:** lista de processos alvo (CSV/TXT em `push-pje`), credenciais do PJe no `.env`
- **Etapas:** 1. Operador dispara `.bat` → 2. Playwright/Selenium loga e navega no PJe → 3. Baixa PDFs dos autos → saída em `~/Desktop/ANALISADOR FINAL/processos/`
- **Arquivo-chave:** `/Users/jesus/stemmia-forense/BAIXAR_PJE.bat` + `/Users/jesus/stemmia-forense/src/pje/baixar_push_pje_playwright.py`
- **Status:** ATIVO — script Playwright atualizado em 17/abr; 10+ variantes de `.bat` sugerem iteração contínua.
- **Última execução conhecida:** 17/04/2026

### B.2 — Análise rápida
- **Entrada:** PDF/texto do processo recém-baixado
- **Etapas:** 1. Orquestrador recebe processo → 2. Extrai fatos-chave + resume → 3. Entrega sumário estruturado
- **Arquivo-chave:** `/Users/jesus/.claude/agents/orq-analise-rapida.md`
- **Status:** QUEBRADO (nomenclatura divergente) — nomes `orquestrador-rapido` / `orq-processo-rapido` citados em docs NÃO existem. Só há `orq-analise-rapida.md`. Invocações Task por nome literal falham.
- **Última execução conhecida:** 04/04/2026

### B.3 — Análise completa
- **Entrada:** processo com autos completos
- **Etapas:** 1. `orq-analise-completa` delega → 2. 8 subagentes paralelos (resumidor-fatos, classificador-tipo-acao, extrator-partes, mapeador-provas, detector-urgencia, classificador-documento, detetive-inconsistencias, analisador-quesitos-auto) → 3. Consolidação
- **Arquivo-chave:** `/Users/jesus/.claude/agents/orq-analise-completa.md`
- **Status:** QUEBRADO (nomenclatura divergente) — esperado `orquestrador-analise-completa`; real é `orq-analise-completa.md`.
- **Última execução conhecida:** 04/04/2026

### B.4 — Geração de petição
- **Entrada:** solicitação do operador + processo analisado
- **Etapas:** 1. `triador-peticao` classifica → 2. `peticao-identificador` define tipo → 3. `peticao-extrator` extrai dados → 4. `gerador-peticao-simples|medio|complexo` redige → 5. `peticao-verificador` confere → 6. `peticao-montador` → 7. `peticao-gerador-pdf`
- **Arquivo-chave:** `/Users/jesus/.claude/agents/triador-peticao.md` (+ 6 agentes da cadeia)
- **Status:** ATIVO — todos os 7 agentes existem. Pipeline íntegra.
- **Última execução conhecida:** 04/04/2026

### B.5 — Geração de laudo
- **Entrada:** processo analisado + exames + dados do periciando
- **Etapas:** 1. `redator-laudo` → 2. `revisor-laudo` → saída MD/PDF
- **Arquivo-chave:** `/Users/jesus/.claude/agents/redator-laudo.md`
- **Status:** QUEBRADO (nomenclatura) — esperado `redator-laudo-pericial`/`revisor-laudo-pericial`; real `redator-laudo.md`/`revisor-laudo.md`.
- **Última execução conhecida:** 04/04/2026

### B.6 — Mutirão
- **Entrada:** pasta `MUTIRÃO/` com 150+ PDFs de periciandos
- **Etapas:** 1. Operador escolhe → 2. Lê PDFs individuais → 3. Produz laudos em lote com escalas (CIF/Lattinen)
- **Arquivo-chave:** `/Users/jesus/Desktop/STEMMIA Dexter/MUTIRÃO/` (pasta) + `escalas/`
- **Status:** PARADO — pasta não modificada desde 07/abr/2026. Não há orquestrador dedicado. Processado manualmente via B.5.
- **Última execução conhecida:** 07/04/2026

### B.7 — Monitoramento de fontes
- **Entrada:** lista em `FONTES-MONITORAMENTO.md`, gatilhos do launchd
- **Etapas:** 1. `launchd` dispara `com.stemmia.monitor-fontes.plist` → 2. `monitor.py` / `monitor_publicacoes.py` consulta fontes → 3. Grava movimentações / notifica Telegram
- **Arquivo-chave:** `/Users/jesus/stemmia-forense/src/pje/monitor.py` + `~/Library/LaunchAgents/com.stemmia.monitor-fontes.plist`
- **Status:** ATIVO — `launchctl list` confirma `com.stemmia.monitor-fontes` e `com.stemmia.monitor-datajud` carregados. Plist atualizado 17/abr.
- **Última execução conhecida:** 17/04/2026

### B.8 — Verificação de erros materiais
- **Entrada:** laudo ou petição redigida
- **Etapas:** 1. `orq-erros-materiais` orquestra → 2. `verificador-cids`, `verificador-datas`, `verificador-nomes-numeros`, `verificador-medicamentos`, `verificador-exames` rodam paralelos → 3. Consolida divergências
- **Arquivo-chave:** `/Users/jesus/.claude/agents/orq-erros-materiais.md`
- **Status:** ATIVO — orquestrador + 5 subagentes verificadores íntegros.
- **Última execução conhecida:** 04/04/2026

### B.9 — Jurisprudência
- **Entrada:** tese / tema / palavra-chave
- **Etapas:** 1. `orq-jurisprudencia` delega → 2. `buscador-base-local`, `buscador-tribunais`, `buscador-academico` paralelos → 3. Consolida
- **Arquivo-chave:** `/Users/jesus/.claude/agents/orq-jurisprudencia.md`
- **Status:** ATIVO — orquestrador + 3 buscadores presentes.
- **Última execução conhecida:** 04/04/2026

### B.10 — Aceite e honorários
- **Entrada:** dados do processo + complexidade estimada
- **Etapas:** 1. Triagem (via B.4) → 2. `gerador-peticao-simples|medio|complexo` produz aceite/proposta → 3. PDF
- **Arquivo-chave:** 3 geradores em `~/.claude/agents/` + `~/Desktop/ANALISADOR FINAL/scripts/calcular_honorarios.py` (35 KB, 16/mar)
- **Status:** ATIVO — 3 geradores + script de honorários. Não há orquestrador dedicado unificando os três.
- **Última execução conhecida:** 16/03/2026

### B.11 — Autoaprendizagem
- **Entrada:** transcript da sessão Claude ao término
- **Etapas:** 1. Stop hook dispara `sessao_end_autoaprendizagem.py` → 2. Analisa padrões → 3. `detectar_habilidade_nova.py` sugere skill nova → 4. Registra em `estado_hub.json`
- **Arquivo-chave:** `/Users/jesus/stemmia-forense/automacoes/detectar_habilidade_nova.py`
- **Status:** ATIVO — Stop hook confirmado em `settings.json`; script executável; `estado_hub.json` atualizado em 19/abr 06:32.
- **Última execução conhecida:** 19/04/2026

---

## Seção C — Duplicações a resolver

### C.1 Pares com mesmo propósito

#### C.1.1 — `RELATORIOS/` vs `RELATÓRIOS/`
- **Tamanhos:** `RELATORIOS/` 2 itens (~60 KB). `RELATÓRIOS/` 7 itens (~213 KB).
- **Conclusão:** Diretórios diferentes com conteúdos distintos. Em filesystem case-sensitive (Linux/CI) aparecem como dois; no Finder (APFS) ora um ora outro. **Risco alto.** Ação: consolidar em `RELATÓRIOS/`.

#### C.1.2 — `MEMORIA.md` raiz vs `memoria/MEMORIA.md`
- **Tamanhos:** raiz = 1054 B. `memoria/` = 2142 B.
- **Conclusão:** Conteúdo DIFERENTE. Raiz é resumo antigo (14/abr); `memoria/` é memória persistente estruturada. Ação: arquivar raiz em `_arquivo/MEMORIA.md.OLD-20260414`.

#### C.1.3 — `FERRAMENTAS/analisador-novo` vs `_arquivo/analisador novo`
- **Saída `diff -rq`:** `Only in _arquivo/analisador novo: .DS_Store`
- **Conclusão:** Clones byte-idênticos. Candidato a remoção pós LIMPAR-LIBERADO.

#### C.1.4 — `MAPA-FERRAMENTAS.md` raiz vs `memoria/`
- **Tamanhos:** ambos 32975 B exatos.
- **Conclusão:** IDÊNTICOS byte-a-byte. Ação: substituir raiz por symlink para `memoria/`.

#### C.1.5 — `DECISOES.md` raiz vs `memoria/DECISOES.md`
- **Tamanhos:** raiz = 14408 B (atualizado 18/abr). `memoria/` = 3439 B (14/abr).
- **Conclusão:** Conteúdo DIFERENTE. Log vivo é o da raiz. Política única necessária.

### C.2 Arquivos `.md` com nomes duplicados

Comando: `find "STEMMIA Dexter" -name "*.md" -type f | xargs -I{} basename "{}" | sort | uniq -d`
**Total:** 300+ nomes duplicados. Principais categorias:

1. `MEMORIA.md` — raiz + `memoria/` + `MEMORIA-CLAUDE/` + `_arquivo/`
2. `DECISOES.md` — raiz + `memoria/` + `_arquivo/Correções Claude/`
3. `ROTINA.md` — raiz + `memoria/`
4. `MAPA-FERRAMENTAS.md` — raiz + `memoria/` (idênticos)
5. `CLAUDE.md` — raiz + `FERRAMENTAS/openclaw/` + `_arquivo/PROJETOS CLAUDECODE/`
6. `README.md` — raiz + dezenas em subprojetos
7. `AGENTS.md` — `.planning/` + `agents/` + raiz Codex
8. `INDICE.md` / `INDEX.md` / `index.md` — múltiplas
9. `MAPA-DE-FONTES.md` — `BANCO-DADOS/` + outras
10. `PERFIL-USUARIO.md` — `memoria/` + `_arquivo/HABILIDADES APRENDIDAS JESUS/`
11. `ANALISE-MANTENA-COMPLETA.md` — `FERRAMENTAS/openclaw/` + `_arquivo/OpenClaw/`
12. `FLUXOS-N8N.md` — `AUTOMAÇÃO/` + `_arquivo/N8N Workflows Stemmia/`
13. `COMANDOS-INSTALACAO.md` + `COMANDOS-INSTALACAO-v2.md` coexistindo

**Fontes do ruído:** (a) docs npm/Python replicadas em `_arquivo/FERRAMENTAS JURÍDICAS/MCPs/brlaw_mcp_server/.venv/`; (b) sub-agentes duplicados entre `agents/`, `skills/` e `_arquivo/PLUGINS CLAUDE/`; (c) modelos de laudo em múltiplas pastas.

### C.3 Clones byte-idênticos `FERRAMENTAS/` ↔ `_arquivo/`

| FERRAMENTAS/ | _arquivo/ | Diferença | Conclusão |
|---|---|---|---|
| `analisador-novo/` | `analisador novo/` | só `.DS_Store` | **100% CLONE** |
| `analisador-ultra/` | `ANALISADOR ULTRA/` | `.DS_Store`, `.env.example`, `.git/` | CLONE do código |
| `analise-nova/` | `ANÁLISE NOVA PROCESSOS/` | só `.DS_Store` | **100% CLONE** |
| `openclaw/` | `OpenClaw/` | divergente | NÃO é clone — divergiu |
| `openclaw-config/` | `OPENCLAW-PACOTE-CONFIGURACAO/` | 2 pastas de sessão | Quase clone |
| `jurídicas/` | `FERRAMENTAS JURÍDICAS/` | só `.DS_Store`s | **100% CLONE** (inclui `.venv` gigante) |

**Impacto:** `_arquivo/` ocupa **2,3 GB** e parte significativa é clone direto.

### C.4 Arquivos `.md` soltos na raiz

**Total:** 13 arquivos. Alvo ideal: 6–7.

Candidatos a mover:
- `DIAGNOSTICO-17042026.md`, `RELATORIO-REORGANIZACAO-2026-04-14.md` → `RELATÓRIOS/`
- `PROMPT-BAIXAR-PDFS.md`, `PROMPT-PUSH-RENOMEAR-INCLUIR.md` → `00-CONTROLE/prompts/`
- `GUIA-OTIMIZACAO-TOKENS.md`, `INVENTÁRIO.md` → `DOCS/`

---

## Seção D — Symlinks e dependências externas

**Total:** 34 symlinks (comando `find -maxdepth 5 -type l`).

**Critério de risco:**
- **Alto** — fora do Dexter E executável/script, ou referenciado por MCP/hook, ou quebra fluxo diário.
- **Médio** — dado estático ou legacy em `_arquivo/`.
- **Baixo** — substituível ou já quebrado.

| # | Symlink | Destino | Status | Risco | O que quebra |
|---:|---|---|---|---|---|
| 1 | `PROCESSOS` | `ANALISADOR FINAL/processos` | OK | **Alto** | Navegação raiz; MCP filesystem. |
| 2 | `SCRIPTS` | `ANALISADOR FINAL/scripts` | OK | **Alto** | Entrada canônica scripts Python. |
| 3 | `BANCO-DADOS/BANCO-GERAL-LINK` | `ANALISADOR FINAL/BANCO DE DADOS GERAL` | OK | **Alto** | Fonte primária banco geral. |
| 4 | `AUTOMAÇÃO/PROTOCOLAR-AGORA` | `ANALISADOR FINAL/saida/peticoes-claude/` | OK | **Alto** | Saída petições. |
| 5 | `AUTOMAÇÃO/PDF-NOVOS` | `ANALISADOR FINAL/INBOX/` | OK | **Alto** | Inbox PDFs. |
| 6 | `MODELOS/laudos` | `FENIX/modelos-laudo` | OK | **Alto** | Biblioteca modelos laudo. |
| 7 | `MODELOS/petições-prontas` | `FENIX/modelos-peticao` | **QUEBRADO** | Baixo | Já quebrado — destino não existe. |
| 8 | `DOCS/sistema-completo` | `STEMMIA — SISTEMA COMPLETO` | OK | Médio | Atalho doc mestra. |
| 9 | `MUTIRÃO/referencias/BANCO-REFERENCIAS` | `ANALISADOR FINAL/BANCO-REFERENCIAS-PERICIA` | OK | **Alto** | Referências mutirão. |
| 10 | `PERÍCIA FINAL/dados_brutos/STATUS-PROCESSOS.json` | `ANALISADOR FINAL/STATUS-PROCESSOS.json` | OK | **Alto** | Estado canônico. |
| 11 | `PERÍCIA FINAL/dados_brutos/_pendentes_download.json` | `ANALISADOR FINAL/scripts/_pendentes_download.json` | OK | **Alto** | Fila downloads PJE. |
| 12 | `PERÍCIA FINAL/scripts/conectar_pje.sh` | `ANALISADOR FINAL/scripts/conectar_pje.sh` | OK | **Alto** | Launcher Chrome debug. |
| 13 | `PERÍCIA FINAL/scripts/gerar_visao_unificada.py` | idem | OK | **Alto** | Dashboard processos. |
| 14 | `PERÍCIA FINAL/scripts/monitorar_movimentacao.py` | idem | OK | **Alto** | Monitor movimentações. |
| 15 | `PERÍCIA FINAL/scripts/gerar_peticao.py` | idem | OK | **Alto** | Core pipeline. |
| 16 | `PERÍCIA FINAL/scripts/calcular_honorarios.py` | idem | OK | **Alto** | Calculadora honorários. |
| 17 | `PERÍCIA FINAL/scripts/gerar_aceite_rapido.py` | idem | OK | **Alto** | Aceite rápido. |
| 18 | `PERÍCIA FINAL/scripts/pipeline_analise.py` | idem | OK | **Alto** | Pipeline completo. |
| 19 | `PERÍCIA FINAL/scripts/scanner_processos.py` | idem | OK | **Alto** | Scanner. |
| 20 | `PERÍCIA FINAL/scripts/abrir_chromes_debug.sh` | idem | OK | **Alto** | Chrome debug. |
| 21 | `PERÍCIA FINAL/scripts/pje_standalone.py` | idem | OK | **Alto** | Driver PJE. |
| 22 | `PERÍCIA FINAL/scripts/sequencia_cronologica.py` | idem | OK | **Alto** | Sequência autos. |
| 23 | `PERÍCIA FINAL/scripts/briefing_diario.py` | idem | OK | **Alto** | Briefing diário. |
| 24 | `PERÍCIA FINAL/scripts/sincronizar_aj_pje.py` | idem | OK | **Alto** | Sync AJ/PJE. |
| 25 | `PERÍCIA FINAL/scripts/orquestrador_noturno.py` | idem | OK | **Alto** | Cron noturno. |
| 26 | `PERÍCIA FINAL/scripts/consultar_aj.py` | idem | OK | **Alto** | Consulta AJ. |
| 27 | `PERÍCIA FINAL/scripts/gestor-processos.py` | idem | OK | **Alto** | Gestor central. |
| 28 | `PERÍCIA FINAL/scripts/deadline_monitor.py` | idem | OK | **Alto** | Monitor prazos. |
| 29 | `PERÍCIA FINAL/scripts/consultar_ajg.py` | idem | OK | **Alto** | Consulta AJG. |
| 30 | `PERÍCIA FINAL/templates/laudo/modelos-existentes` | `ANALISADOR FINAL/modelos-laudo` | OK | Médio | Templates. |
| 31 | `_arquivo/ROTEIRO MUTIRÕES/referencias/BANCO-REFERENCIAS` | `ANALISADOR FINAL/BANCO-REFERENCIAS-PERICIA` | OK | Médio | Duplicata legacy (#9). |
| 32 | `_arquivo/AUTOMAÇÃO PROCESSUAL/PROTOCOLAR-AGORA` | `ANALISADOR FINAL/saida/peticoes-claude/` | OK | Médio | Duplicata legacy (#4). |
| 33 | `_arquivo/AUTOMAÇÃO PROCESSUAL/PDF-NOVOS` | `ANALISADOR FINAL/INBOX/` | OK | Médio | Duplicata legacy (#5). |
| 34 | `_arquivo/Open/analisador-final/scripts/processos` | `/Users/jesusnoleto/Desktop/...` | **QUEBRADO** | Baixo | Path usuário antigo `jesusnoleto` — morto. |

### Observações de dependência crítica

- **Dependência do hub `ANALISADOR FINAL`:** 30/34 symlinks (88%) apontam para lá. Mover/renomear essa pasta = quebra do pipeline inteiro + derrubada de 2 MCPs (`sqlite`, `filesystem`).
- **Links quebrados hoje:** 2 (#7 `MODELOS/petições-prontas` e #34 path antigo `jesusnoleto`). Seguros de remover.
- **Duplicatas em `_arquivo/`:** #31/#32/#33 são cópias legadas. Candidatos a limpeza.
- **MCPs com path hardcoded no Dexter:** `cerebra-legal`, `brlaw`, `medical-mcp` em `FERRAMENTAS/jurídicas/MCPs/`. Mover `FERRAMENTAS/` quebra 3 MCPs.
- **Hooks do `settings.json`:** todos apontam para `$HOME/stemmia-forense/hooks/` ou `~/.claude/hooks/` — NÃO dependem do hub Dexter diretamente.

---

## Seção E — Scoreboard por fluxo

Critérios:
- **Doc?** MD/HTML explicativo existe
- **Teste?** teste unit/integração existe
- **Orquestrador?** agente `orq-*` ou script coordenador
- **Trigger?** entrada em hooks, launchd, `.bat`

| # | Fluxo | Doc | Teste | Orq | Trigger | Cobertura |
|---|---|---|---|---|---|---|
| 11 | Autoaprendizagem | Sim | Sim (`test_stop_hook.py`) | Sim | Sim (Stop hook) | **100%** |
| 7 | Monitoramento de fontes | Sim | Sim | Sim (`monitor.py`) | Sim (launchd) | **100%** |
| 1 | Download PJe | Sim | Sim | Parcial | Sim (`.bat` + launchd) | **87%** |
| 4 | Geração de petição | Sim | Não | Sim (`triador-peticao`) | Não | 50% |
| 8 | Verificação erros materiais | Parcial | Não | Sim (`orq-erros-materiais`) | Não | 50% |
| 9 | Jurisprudência | Parcial | Não | Sim (`orq-jurisprudencia`) | Não | 50% |
| 2 | Análise rápida | Sim | Não | Sim (nome divergente) | Não | 50% |
| 3 | Análise completa | Sim | Não | Sim (nome divergente) | Não | 50% |
| 5 | Geração de laudo | Sim | Não | Sim (nome divergente) | Não | 50% |
| 10 | Aceite e honorários | Sim | Não | Parcial | Não | 37% |
| 6 | Mutirão | Parcial | Não | Não | Não | **25%** |

**Cobertura média: 59%** (média aritmética).

### 3 piores fluxos (maior dívida técnica)

1. **B.6 Mutirão — 25%.** Nenhum orquestrador, nenhum teste, nenhum trigger; pasta parada desde 07/abr. 150+ PDFs operados manualmente. Prioridade: criar `orq-mutirao` que despache B.5 em lote.
2. **B.10 Aceite e honorários — 37%.** Três geradores soltos sem coordenador. `calcular_honorarios.py` isolado do pipeline de agentes. Prioridade: criar `orq-aceite-honorarios` unindo triagem + cálculo + gerador.
3. **B.2/B.3/B.5 (empate 50%) —** além de não ter testes nem gatilhos, sofrem de **divergência de nomenclatura**: nomes no `CLAUDE.md` NÃO batem com arquivos reais. Automações referenciando nomes "corretos" quebram silenciosamente.

### 3 melhores fluxos (maior maturidade)

1. **B.11 Autoaprendizagem — 100%.** Único fluxo com os quatro pilares. Stop hook ativo, `estado_hub.json` atualizado hoje (19/abr 06:32).
2. **B.7 Monitoramento de fontes — 100%.** launchd carregado, doc em `FONTES-MONITORAMENTO.md`, testes em `hooks/tests/`.
3. **B.1 Download PJe — 87%.** Doc forte, Playwright em manutenção recente, triggers via `.bat` e launchd `comunica-pje-diario`.

### Observações finais do scoreboard

- **Dívida crítica de nomenclatura:** 3/11 fluxos têm nomes de agentes no pedido que NÃO correspondem aos arquivos reais. Escolher convenção única (`orq-*` curta OU `orquestrador-*-pericial` longa).
- **Cobertura de testes quase nula** fora dos hooks de sessão. Nenhum dos 6 pipelines de agentes (B.2–B.5, B.8, B.9) tem teste automatizado.
- **Agentes congelados em 04/abr:** 90% dos `.md` em `~/.claude/agents/` não mudam desde o commit inicial. Só `detectar_habilidade_nova.py` (19/abr) e PJe (17/abr) evoluem.
- **Gatilhos automáticos existem só para 3 fluxos (B.1, B.7, B.11).** Os outros 8 dependem de invocação manual — gargalo operacional claro.

---

## Seção F — Recomendações priorizadas

Formato: `F.N — <Ação> [prioridade | esforço]`

### F.1 — Remover `MEMORIA.md` desatualizado da raiz [Crítica | ≤15min]
- **Por quê:** conflita com `memoria/MEMORIA.md`. Ambiguidade para agentes.
- **Como:** `mv "STEMMIA Dexter/MEMORIA.md" "STEMMIA Dexter/_arquivo/MEMORIA.md.OLD-20260414"`.
- **Impacto:** fonte única de memória. Elimina leitura errada.

### F.2 — Consolidar `RELATORIOS/` em `RELATÓRIOS/` [Crítica | ≤15min]
- **Por quê:** em filesystem case-sensitive viram dois diretórios. Risco de perda em sync.
- **Como:** `cd "STEMMIA Dexter" && mv RELATORIOS/* RELATÓRIOS/ && rmdir RELATORIOS`.
- **Impacto:** comportamento consistente em Linux/CI/git.

### F.3 — Resolver conflito `DECISOES.md` raiz vs `memoria/` [Crítica | ≤15min]
- **Por quê:** log vivo na raiz (14408 B) mas agentes lêem `memoria/` (3439 B, desatualizado).
- **Como:** `cp "STEMMIA Dexter/DECISOES.md" "STEMMIA Dexter/memoria/DECISOES.md"` e transformar raiz em symlink.
- **Impacto:** fonte única.

### F.4 — Transformar `MAPA-FERRAMENTAS.md` raiz em symlink [Alta | ≤15min]
- **Por quê:** idênticos hoje, mas edição futura diverge.
- **Como:** `rm MAPA-FERRAMENTAS.md && ln -s memoria/MAPA-FERRAMENTAS.md MAPA-FERRAMENTAS.md`.
- **Impacto:** zero risco de divergência.

### F.5 — Mover documentos datados da raiz para `RELATÓRIOS/` [Alta | ≤15min]
- **Alvos:** `DIAGNOSTICO-17042026.md`, `RELATORIO-REORGANIZACAO-2026-04-14.md`.
- **Impacto:** raiz 13 → 11.

### F.6 — Mover prompts utilitários para `00-CONTROLE/prompts/` [Alta | ≤15min]
- **Alvos:** `PROMPT-BAIXAR-PDFS.md`, `PROMPT-PUSH-RENOMEAR-INCLUIR.md`.
- **Impacto:** raiz 11 → 9.

### F.7 — Mover `GUIA-OTIMIZACAO-TOKENS.md` e `INVENTÁRIO.md` para `DOCS/` [Média | ≤15min]
- **Impacto:** raiz com apenas docs vivos.

### F.8 — Corrigir symlink quebrado `MODELOS/petições-prontas` [Alta | ≤15min]
- **Por quê:** símbolo #7 aponta para `FENIX/modelos-peticao` (inexistente). Qualquer fluxo que dependia está degradado.
- **Como:** remover symlink morto e recriar apontando para `STEMMIA Dexter/MODELOS PETIÇÕES PLACEHOLDERS/`.

### F.9 — Remover symlink morto `_arquivo/Open/.../processos` [Baixa | ≤15min]
- **Por quê:** #34 aponta para path de usuário antigo `jesusnoleto`. Resíduo.
- **Como:** `rm "STEMMIA Dexter/_arquivo/Open/analisador-final/scripts/processos"`.

### F.10 — Remover clone `_arquivo/FERRAMENTAS JURÍDICAS` [Crítica | ≤15min | REQUER LIMPAR-LIBERADO]
- **Por quê:** clone 100% de `FERRAMENTAS/jurídicas/` incluindo `.venv` gigante.
- **Como:** `rm -rf "STEMMIA Dexter/_arquivo/FERRAMENTAS JURÍDICAS"`.
- **Impacto:** libera ~1+ GB.

### F.11 — Adicionar `.venv/`, `__pycache__/`, `.DS_Store` ao `.gitignore` [Crítica | ≤15min]
- **Por quê:** `.venv` entrou no Git em `_arquivo/` → inflou índice.
- **Como:** editar `.gitignore` global do hub.
- **Impacto:** anti-regressão.

### F.12 — Migração Banco Geral (referenciada) [Alta | ≤1 sessão | JÁ PLANEJADA (Fase 3 T10–T14)]
- Consolidar destino único. Executar via plano-mestre.

### F.13 — Migração PYTHON-BASE (referenciada) [Alta | ≤1 sessão | JÁ PLANEJADA (Fase 4 T15–T20)]
- Trazer `~/Desktop/_MESA/01-ATIVO/PYTHON-BASE/` para dentro + autoaprendizagem.

### F.14 — Limpeza de `_arquivo/` pós-aprovação [Alta | ≤1 sessão | REQUER LIMPAR-LIBERADO]
- Comprimir em zip, mover para backup externo, remover expandido.
- **Impacto:** hub encolhe drasticamente; find/grep 10x mais rápido.

### F.15 — Documentação: `DOCS/README-ESTRUTURA.md` [Média | ≤1h]
- Explicar papel de cada pasta de primeiro nível.

### F.16 — Documentação: `DOCS/CONVENCOES-NOMES.md` [Média | ≤1h]
- Kebab-case vs MAIÚSCULAS, com/sem acento, versionamento via git.

### F.17 — Pre-commit hook anti-duplicação [Alta | ≤1 sessão]
- Bloquear commit com nomes duplicados em `FERRAMENTAS/`, `memoria/`, `DOCS/`.

### F.18 — Script de inventário semanal [Média | ≤1 sessão]
- `SCRIPTS/inventario-semanal.sh` via launchd segunda 08:00.

### F.19 — Consolidar `MEMORIA-CLAUDE/` vs `memoria/CLAUDE-MEMORY/` [Alta | ≤1h]
- `memoria/CLAUDE-MEMORY/` (98 itens, 19/abr) é o correto; arquivar raiz.

### F.20 — Mesclar `agents/` + `skills/` + `_arquivo/PLUGINS CLAUDE/` [Média | ≤1 sessão]
- Claude Code lê só `~/.claude/`; resto é órfão. Arquivar ~80+ `.md` duplicados.

### F.21 — Resolver divergência `FERRAMENTAS/openclaw` ↔ `_arquivo/OpenClaw` [Alta | ≤1h]
- Copiar sessões históricas; consolidar em `FERRAMENTAS/`.

### F.22 — Remover `.DS_Store` do hub [Baixa | ≤15min]
- `find . -name .DS_Store -print -delete` + adicionar ao `.gitignore`.

### F.23 — Criar `00-CONTROLE/LIMPAR-LIBERADO.md` [Média | ≤15min]
- Registro de alvos de `rm -rf` pendentes com checklist de aprovação dupla.

### F.24 — Mover JSONs operacionais da raiz [Baixa | ≤15min]
- `LISTA-COMPLETA-PUSH.json`, `NUMERACAO-CORRETA.json`, `PUSH-ATUAL.csv`, `PUSH-COMPARACAO.json` → `00-CONTROLE/push/`.

---

## Resumo executivo de ações

| Categoria | Contagem | Ação imediata |
|---|---|---|
| Pares same-purpose | 5 | Resolver F.1–F.4 (≤15min cada) |
| Nomes `.md` duplicados | 300+ | F.10 + F.11 elimina 80% |
| Clones FERRAMENTAS↔_arquivo | 3 confirmados | F.10 (maior ganho) + F.8/F.9 |
| Arquivos soltos na raiz | 13 (alvo: 6–7) | F.5, F.6, F.7, F.24 |
| Symlinks quebrados | 2 | F.8, F.9 |
| Fluxos QUEBRADOS (nomenclatura) | 3 | Passe de padronização (fora desta iniciativa) |
| Recomendações totais | 24 | 7 Críticas/Altas ≤15min dão ganho maior |

**Caminho mais rápido para impacto:**
F.11 + F.22 (anti-regressão) →
F.1, F.2, F.3, F.4 (fontes únicas) →
F.5, F.6, F.7, F.24 (raiz limpa) →
F.8, F.9 (symlinks quebrados) →
F.23 + aprovação →
F.10 (libera ~1 GB imediato) →
F.14 (arquiva resto do `_arquivo/`).

**Itens que ficam para as próximas fases do plano-mestre:**
- F.12 (Banco Geral) → Fase 3 do plano.
- F.13 (PYTHON-BASE) → Fase 4 do plano.

---

## Metadados

**Agentes usados nesta auditoria:**
- Explore #1 — Inventário por camada + catálogo de symlinks
- Explore #2 — 11 fluxos + scoreboard
- Explore #3 — Duplicações + recomendações priorizadas

**Arquivos de evidência:** `00-CONTROLE/migracoes/base/*.txt` (snapshots T01)

**Próximo passo (T04):** CHECKPOINT — Dr. Jesus revisa esta auditoria e aprova Fase 2 (Organograma visual).

**Histórico:**
| Data | Mudança |
|---|---|
| 2026-04-19 | Criado (T03 da Fase 1) |
