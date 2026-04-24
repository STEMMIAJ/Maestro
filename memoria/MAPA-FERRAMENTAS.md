# MAPA DE FERRAMENTAS — Sistema STEMMIA / Claude Code

Gerado: 2026-04-19. Versão viva — editar como código (git).

Contagem real:
- Agentes: 85
- Skills (instaladas + cache): 195 (núcleo único: ~80; resto são duplicatas em cache de marketplaces)
- Plugins: 6 pastas (3 próprias + 3 marketplaces/cache)
- MCPs configurados: 17
- Hooks: 6 eventos, 11 comandos
- Scripts PJe (.py): 28
- BAT Windows (raiz stemmia-forense): 21
- Comandos slash diretos: 2 (`buscar-produto`, `mapear-pedido`) + 57 sub-comandos `gsd:*`

Padrão das entradas (manpage curta):
```
### `nome`
- Tipo:
- Função:
- Como invocar:
- Exemplo:
- Quando NÃO usar:
- Arquivo:
```

---

## 1) AGENTES (85, alfabético)

Invocação geral: Task tool com `subagent_type: <nome-do-agente>`. Todos rodam Opus por padrão (`CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-7`).

### `analisador-quesitos-auto`
- Tipo: agente
- Função: Detecta vícios em quesitos (15 categorias), pertinência, duplicidade, sugere reformulação.
- Como invocar: Task `subagent_type: analisador-quesitos-auto`
- Exemplo: "Analise os quesitos do processo X"
- Quando NÃO usar: gerar quesitos novos do zero (use `gerador-peticao-*`).
- Arquivo: `/Users/jesus/.claude/agents/analisador-quesitos-auto.md`

### `analista-neurocomportamental`
- Tipo: agente
- Função: Analisa relatos sobre TEA/TDAH, estilo psiquiatra, sem motivacional.
- Como invocar: Task `subagent_type: analista-neurocomportamental`
- Exemplo: "Analise meu relato de sobrecarga sensorial hoje"
- Quando NÃO usar: laudo pericial formal.
- Arquivo: `/Users/jesus/.claude/agents/analista-neurocomportamental.md`

### `auditor-copias-md`
- Tipo: agente
- Função: Verifica se backups .md foram copiados para Plan Mode (não Mesa).
- Como invocar: Task `subagent_type: auditor-copias-md`
- Arquivo: `/Users/jesus/.claude/agents/auditor-copias-md.md`

### `auditor-espacamento`
- Tipo: agente
- Função: Audita padding/margin/gap em HTML contra 8pt grid e Apple HIG.
- Como invocar: Task `subagent_type: auditor-espacamento`
- Arquivo: `/Users/jesus/.claude/agents/auditor-espacamento.md`

### `auditor-estrutura`
- Tipo: agente
- Função: (descrição vazia no front-matter — ler arquivo)
- Arquivo: `/Users/jesus/.claude/agents/auditor-estrutura.md`

### `auditor-tipografia`
- Tipo: agente
- Função: Audita escalas tipográficas em HTML, compara com referências.
- Arquivo: `/Users/jesus/.claude/agents/auditor-tipografia.md`

### `bug-hunter-sites`
- Tipo: agente
- Função: Caça bugs em HTML/CSS/JS — links, imagens, responsivo, forms, meta, a11y.
- Arquivo: `/Users/jesus/.claude/agents/bug-hunter-sites.md`

### `buscador-academico`
- Tipo: agente
- Função: Referências científicas (PubMed, SciELO, BDTD, Semantic Scholar) para laudos.
- Exemplo: "Cite estudos sobre LER em digitadores"
- Arquivo: `/Users/jesus/.claude/agents/buscador-academico.md`

### `buscador-base-local`
- Tipo: agente
- Função: Busca jurídica offline na Base de Dados Geral (Whoosh, 196 docs).
- Quando NÃO usar: pesquisa atual de jurisprudência (use `buscador-tribunais`).
- Arquivo: `/Users/jesus/.claude/agents/buscador-base-local.md`

### `buscador-tribunais`
- Tipo: agente
- Função: Jurisprudência online — STJ/STF/TST/TJMG/TRF6/TRT3 + DataJud.
- Arquivo: `/Users/jesus/.claude/agents/buscador-tribunais.md`

### `capturador-ideias`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/capturador-ideias.md`

### `classificador-documento`
- Tipo: agente
- Função: Classifica tipo de documento (laudo, atestado, receita, exame, prontuário, petição etc.).
- Arquivo: `/Users/jesus/.claude/agents/classificador-documento.md`

### `classificador-intencoes`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/classificador-intencoes.md`

### `classificador-recursos`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/classificador-recursos.md`

### `classificador-tipo-acao`
- Tipo: agente
- Função: Classifica ação (cível/trabalhista/previdenciária/securitária/criminal) + valor + segredo.
- Arquivo: `/Users/jesus/.claude/agents/classificador-tipo-acao.md`

### `clinica-minas-dev`
- Tipo: agente
- Função: Especialista no projeto Sistema Clínica Minas (req, arquitetura, organograma).
- Trigger: usuário menciona "clínica minas".
- Arquivo: `/Users/jesus/.claude/agents/clinica-minas-dev.md`

### `coach-cognitivo`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/coach-cognitivo.md`

### `concierge`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/concierge.md`

### `designer-brief`
- Tipo: agente
- Função: Gera brief de design (paleta/fontes/elementos) por domínio jurídico ou musical.
- Arquivo: `/Users/jesus/.claude/agents/designer-brief.md`

### `designer-juridico`
- Tipo: agente
- Função: Brief de design para sites de advogados por área de atuação.
- Arquivo: `/Users/jesus/.claude/agents/designer-juridico.md`

### `designer-musical`
- Tipo: agente
- Função: Brief de design para sites de músicos por gênero.
- Arquivo: `/Users/jesus/.claude/agents/designer-musical.md`

### `designer-nicho`
- Tipo: agente
- Função: Sugere paleta/fonte/seções a partir de tabela de 30 nichos.
- Trigger: "site de [profissão]".
- Arquivo: `/Users/jesus/.claude/agents/designer-nicho.md`

### `detector-urgencia`
- Tipo: agente
- Função: Detecta prazos processuais e classifica URGENTE/NORMAL/FOLGA.
- Arquivo: `/Users/jesus/.claude/agents/detector-urgencia.md`

### `detetive-inconsistencias`
- Tipo: agente
- Função: Cruza versões dos fatos (PI x contestação x laudo x depoimento) achando contradições.
- Quando NÃO usar: erros materiais simples (use `orq-erros-materiais`).
- Arquivo: `/Users/jesus/.claude/agents/detetive-inconsistencias.md`

### `diagnosticador-sistema`
- Tipo: agente
- Função: Diagnostica problemas (mic, ditado, Bluetooth, Terminal, Claude Code).
- Arquivo: `/Users/jesus/.claude/agents/diagnosticador-sistema.md`

### `extrator-informacoes-doc`
- Tipo: agente
- Função: Extrai datas/nomes/CIDs/medicamentos/exames de um documento individual.
- Arquivo: `/Users/jesus/.claude/agents/extrator-informacoes-doc.md`

### `extrator-partes`
- Tipo: agente
- Função: Extrai autor/réu/advogados/juiz/perito/AT/vara/comarca de processo.
- Arquivo: `/Users/jesus/.claude/agents/extrator-partes.md`

### `gerador-peticao-complexo`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/gerador-peticao-complexo.md`

### `gerador-peticao-medio`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/gerador-peticao-medio.md`

### `gerador-peticao-simples`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/gerador-peticao-simples.md`

### `gerador-roteiro-pericial`
- Tipo: agente
- Função: Roteiro HTML para exame pericial presencial — escalas + quesitos + passo-a-passo.
- Arquivo: `/Users/jesus/.claude/agents/gerador-roteiro-pericial.md`

### Agentes GSD (16) — pipeline "Get Stuff Done"
Suite de planejamento/execução. Spawned pelos comandos slash `/gsd:*`. Não chamar direto a menos que conheça o protocolo.

- `gsd-advisor-researcher` — pesquisa decisão cinzenta (`/gsd:discuss-phase` advisor)
- `gsd-assumptions-analyzer` — extrai premissas com evidência (`/gsd:discuss-phase`)
- `gsd-codebase-mapper` — explora codebase (`/gsd:map-codebase`)
- `gsd-debugger` — método científico de debug (`/gsd:debug`)
- `gsd-executor` — executa planos com commits atômicos
- `gsd-integration-checker` — valida integração entre fases
- `gsd-nyquist-auditor` — gera testes para cobrir requisitos
- `gsd-phase-researcher` — produz RESEARCH.md antes de planejar
- `gsd-plan-checker` — valida plano antes de executar
- `gsd-planner` — gera plano executável de fase
- `gsd-project-researcher` — pesquisa ecossistema antes do roadmap
- `gsd-research-synthesizer` — sintetiza saídas dos researchers
- `gsd-roadmapper` — cria roadmap com fases
- `gsd-ui-auditor` — auditoria visual 6 pilares
- `gsd-ui-checker` — valida UI-SPEC.md
- `gsd-ui-researcher` — produz UI-SPEC.md
- `gsd-user-profiler` — perfil comportamental do dev
- `gsd-verifier` — verifica goal-backward da fase

Arquivos: `/Users/jesus/.claude/agents/gsd-*.md`

### `mapeador-habilidades`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/mapeador-habilidades.md`

### `mapeador-provas`
- Tipo: agente
- Função: Mapeia todas as provas/documentos do processo (tipo, data, anexado, relevância).
- Arquivo: `/Users/jesus/.claude/agents/mapeador-provas.md`

### `medidor-tokens`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/medidor-tokens.md`

### `nomeador-peticao`
- Tipo: agente
- Função: Gera nome descritivo padrão Windows para petição.
- Arquivo: `/Users/jesus/.claude/agents/nomeador-peticao.md`

### `orq-analise-completa`
- Tipo: agente (orquestrador)
- Função: Dispara 8 sub-agentes paralelos — gera 12 arquivos (ANALISE.md, SCORE, verificações, quesitos, provas, inconsistências).
- Quando NÃO usar: rodar análise rápida (use `orq-analise-rapida`).
- Arquivo: `/Users/jesus/.claude/agents/orq-analise-completa.md`

### `orq-analise-documento`
- Tipo: agente (orquestrador)
- Função: Analisa 1 documento no contexto do processo.
- Arquivo: `/Users/jesus/.claude/agents/orq-analise-documento.md`

### `orq-analise-rapida`
- Tipo: agente (orquestrador)
- Função: 4 sub-agentes paralelos, resumo do processo em 2-3 min.
- Arquivo: `/Users/jesus/.claude/agents/orq-analise-rapida.md`

### `orq-erros-materiais`
- Tipo: agente (orquestrador)
- Trigger: "verificar erros", "analisar erros materiais", "conferir processo".
- Arquivo: `/Users/jesus/.claude/agents/orq-erros-materiais.md`

### `orq-jurisprudencia`
- Tipo: agente (orquestrador)
- Função: 3 buscadores paralelos (base local + tribunais + acadêmico).
- Trigger: "buscar jurisprudência", "precedente sobre".
- Arquivo: `/Users/jesus/.claude/agents/orq-jurisprudencia.md`

### `orquestrador-verificacao-proposta`
- Tipo: agente (orquestrador)
- Função: Verificação de propostas de honorários — JSON + HTML interativo.
- Arquivo: `/Users/jesus/.claude/agents/orquestrador-verificacao-proposta.md`

### `padronizador-estilo`
- Tipo: agente
- Função: Consulta perfil de estilo ANTES de gerar petição.
- Arquivo: `/Users/jesus/.claude/agents/padronizador-estilo.md`

### `pesquisador-produtos`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/pesquisador-produtos.md`

### Agentes de petição (montador completo)
- `peticao-conferidor` — confere
- `peticao-extrator` — extrai dados
- `peticao-gerador-pdf` — gera PDF
- `peticao-identificador` — identifica tipo
- `peticao-montador` — monta peça
- `peticao-verificador` — verifica final

Arquivos: `/Users/jesus/.claude/agents/peticao-*.md`

### `redator-laudo`
- Tipo: agente
- Função: Monta estrutura completa de laudo a partir de análise + quesitos + 19 templates.
- Arquivo: `/Users/jesus/.claude/agents/redator-laudo.md`

### `resumidor-fatos`
- Tipo: agente
- Função: Resume fatos do processo em 5-10 frases cronológicas.
- Arquivo: `/Users/jesus/.claude/agents/resumidor-fatos.md`

### `resumo-sessao`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/resumo-sessao.md`

### `revisor-laudo`
- Tipo: agente
- Função: Revisa laudo — quesitos, fundamentação, coerência, CIDs, português, formatação.
- Arquivo: `/Users/jesus/.claude/agents/revisor-laudo.md`

### `revisor-texto-ditado`
- Tipo: agente
- Função: Corrige pontuação/ortografia do ditado SEM mudar palavras/sentido.
- Arquivo: `/Users/jesus/.claude/agents/revisor-texto-ditado.md`

### `supervisor-sistema`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/supervisor-sistema.md`

### `tradutor-tecnico`
- Tipo: agente
- Função: Traduz termos de TI para leigo com analogias médicas (TEA+TDAH, anomia).
- Arquivo: `/Users/jesus/.claude/agents/tradutor-tecnico.md`

### `transformador-requisitos`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/transformador-requisitos.md`

### `transicao-sessao`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/transicao-sessao.md`

### `triador-peticao`
- Tipo: agente
- Arquivo: `/Users/jesus/.claude/agents/triador-peticao.md`

### `verificador-100`
- Tipo: agente
- Função: Rastreia CADA afirmação até a fonte no processo (verificação 100%).
- Arquivo: `/Users/jesus/.claude/agents/verificador-100.md`

### `verificador-cids`
- Tipo: agente
- Função: Valida CID-10 contra DataSUS (12.451 códigos).
- Arquivo: `/Users/jesus/.claude/agents/verificador-cids.md`

### `verificador-cruzado`
- Tipo: agente
- Função: Cruza dados de 1 documento com texto completo do processo.
- Arquivo: `/Users/jesus/.claude/agents/verificador-cruzado.md`

### `verificador-datas`
- Tipo: agente
- Função: Linha do tempo + detecção de incoerências temporais.
- Arquivo: `/Users/jesus/.claude/agents/verificador-datas.md`

### `verificador-de-fontes`
- Tipo: agente
- Função: Valida URLs/fontes em documentos gerados.
- Quando usar: APÓS gerar qualquer documento com referências.
- Arquivo: `/Users/jesus/.claude/agents/verificador-de-fontes.md`

### `verificador-exames`
- Tipo: agente
- Função: Lista exames citados, verifica anexação e plausibilidade dos resultados.
- Arquivo: `/Users/jesus/.claude/agents/verificador-exames.md`

### `verificador-medicamentos`
- Tipo: agente
- Função: Valida dosagens, compatibilidade CID, existência, via de administração.
- Arquivo: `/Users/jesus/.claude/agents/verificador-medicamentos.md`

### `verificador-nomes-numeros`
- Tipo: agente
- Função: Consistência de nomes/CPF/processo ao longo das peças.
- Arquivo: `/Users/jesus/.claude/agents/verificador-nomes-numeros.md`

---

## 2) SKILLS

Skills carregadas no harness atual (visíveis ao Skill tool). Núcleo único — duplicatas em `plugins/cache/` e `plugins/marketplaces/` são instâncias do mesmo skill por versão.

### Skills locais próprias (em `~/.claude/skills/`)
- `python-base` — consultar antes de gerar/revisar Python de automação. Arquivo: `/Users/jesus/.claude/skills/python-base/SKILL.md`
- `comunicacao-neurodivergente` — regras de tom seco, sem motivacional. Arquivo: `/Users/jesus/.claude/skills/comunicacao-neurodivergente/SKILL.md`

### Skills do plugin `stemmia-compras`
- `mapear-pedido` — transcreve pedido longo em etapas numeradas
- `buscar-produto` — pesquisa via N8N (SerpAPI + Gemini)
Arquivos: `/Users/jesus/.claude/plugins/stemmia-compras/skills/`

### Skills do plugin `superpowers` (5.0.7)
- `using-superpowers`, `using-git-worktrees`, `test-driven-development`, `systematic-debugging`, `dispatching-parallel-agents`, `executing-plans`, `finishing-a-development-branch`, `brainstorming`, `writing-plans`, `requesting-code-review`, `receiving-code-review`, `writing-skills`, `verification-before-completion`, `subagent-driven-development`
Arquivos: `/Users/jesus/.claude/plugins/cache/superpowers-marketplace/superpowers/5.0.7/skills/`

### Skills do plugin `superpowers-lab` (0.4.0)
- `windows-vm`, `slack-messaging`, `finding-duplicate-functions`, `mcp-cli`, `using-tmux-for-interactive-commands`
Arquivos: `/Users/jesus/.claude/plugins/cache/superpowers-marketplace/superpowers-lab/0.4.0/skills/`

### Skills do plugin `superpowers-developing-for-claude-code`
- `working-with-claude-code`, `developing-claude-code-plugins`
Arquivos: `/Users/jesus/.claude/plugins/cache/superpowers-marketplace/superpowers-developing-for-claude-code/0.3.1/skills/`

### Skills do plugin `superpowers-chrome` (1.6.1)
- `browsing` — controle de Chrome via MCP
Arquivo: `/Users/jesus/.claude/plugins/cache/superpowers-marketplace/superpowers-chrome/1.6.1/skills/browsing/SKILL.md`

### Skills do plugin `episodic-memory` (1.0.15)
- `remembering-conversations` — busca em histórico de conversas
Arquivo: `/Users/jesus/.claude/plugins/cache/superpowers-marketplace/episodic-memory/1.0.15/skills/`

### Skills do plugin `obsidian` (1.0.1)
- `obsidian-cli`, `obsidian-markdown`, `obsidian-bases`, `defuddle`, `json-canvas`
Arquivos: `/Users/jesus/.claude/plugins/cache/obsidian-skills/obsidian/1.0.1/skills/`

### Skills do plugin `n8n-skills`
- `n8n-node-configuration`, `n8n-code-javascript`, `n8n-code-python`, `n8n-workflow-patterns`, `n8n-expression-syntax`, `n8n-validation-expert`, `n8n-mcp-tools-expert`
Arquivos: `/Users/jesus/.claude/plugins/marketplaces/n8n-skills/skills/`

### Skills do plugin `claude-plugins-official`
- `claude-automation-recommender`, `claude-md-improver`, `playground`, `skill-creator`, `frontend-design`, `math-olympiad`, `session-report`
- `mcp-server-dev`: `build-mcp-server`, `build-mcp-app`, `build-mcpb`
- `plugin-dev`: `command-development`, `skill-development`, `plugin-settings`, `plugin-structure`, `hook-development`, `mcp-integration`, `agent-development`
- `hookify`: `writing-rules`
- External: `discord/access`, `discord/configure`, `telegram/access`, `telegram/configure`, `imessage/access`, `imessage/configure`
Arquivos: `/Users/jesus/.claude/plugins/marketplaces/claude-plugins-official/`

### Skills do plugin `awesome-claude-plugins`
- `senior-frontend`, `theme-factory`, `developer-growth-analysis`, `canvas-design`, `changelog-generator`, `artifacts-builder`, `mcp-builder`, `frontend-design`
- `skill-bus`: `add-sub`, `pause-subs`, `unpause-subs`, `list-subs`, `remove-sub`, `reflecting-on-sessions`, `help`
- `perf`: `benchmark`, `theory`, `baseline`, `theory-tester`, `profile`, `code-paths`, `analyzer`, `investigation-logger`
Arquivos: `/Users/jesus/.claude/plugins/marketplaces/awesome-claude-plugins/`

### Skills do plugin `claude-mem` (openclaw)
- `do`, `make-plan`, `smart-explore`, `mem-search`
Arquivos: `/Users/jesus/.claude/plugins/marketplaces/claude-mem/`

### Skills do plugin `ui-ux-pro-max-skill`
- `ui-ux-pro-max`, `design`, `banner-design`, `ui-styling`, `brand`, `slides`, `design-system`
Arquivos: `/Users/jesus/.claude/plugins/cache/ui-ux-pro-max-skill/ui-ux-pro-max/2.0.1/.claude/skills/`

### Skills do plugin `process-mapper`
- (ver `~/.claude/plugins/process-mapper/skills/`)

### Skills do plugin `elements-of-style`
- `writing-clearly-and-concisely`
Arquivo: `/Users/jesus/.claude/plugins/cache/superpowers-marketplace/elements-of-style/1.0.0/skills/`

### Skills do plugin `claude-session-driver`
- `driving-claude-code-sessions`
Arquivo: `/Users/jesus/.claude/plugins/cache/superpowers-marketplace/claude-session-driver/1.0.1/skills/`

Total real de SKILL.md no disco: 195 (inclui duplicatas por marketplace + cache de versões).

---

## 3) PLUGINS (6 pastas)

### `stemmia-forense`
- Tipo: plugin local próprio
- Função: agentes + commands + hooks + skills do dia-a-dia pericial
- Conteúdo: `agents/`, `commands/`, `hooks/`, `skills/`, `README.md`
- Arquivo: `/Users/jesus/.claude/plugins/stemmia-forense/`

### `stemmia-compras`
- Tipo: plugin local próprio
- Função: pesquisa de produtos via N8N
- Conteúdo: `commands/`, `skills/` (mapear-pedido, buscar-produto)
- Arquivo: `/Users/jesus/.claude/plugins/stemmia-compras/`

### `process-mapper`
- Tipo: plugin local próprio
- Função: mapeamento de processos judiciais
- Conteúdo: `agents/`, `data/`, `scripts/`, `skills/`
- Arquivo: `/Users/jesus/.claude/plugins/process-mapper/`

### `marketplaces/`
- Tipo: cache de marketplaces de plugins (claude-mem, claude-plugins-official, awesome-claude-plugins, n8n-skills, obsidian-skills, ui-ux-pro-max-skill, episodic-memory)
- Arquivo: `/Users/jesus/.claude/plugins/marketplaces/`

### `cache/`
- Tipo: cache de plugins por versão (superpowers, claude-plugins-official, etc.)
- Arquivo: `/Users/jesus/.claude/plugins/cache/`

### `data/`
- Tipo: dados persistentes de plugins (skill-bus subscriptions etc.)
- Arquivo: `/Users/jesus/.claude/plugins/data/`

---

## 4) MCPs (17 servidores)

Configurados em `/Users/jesus/.claude/.mcp.json`. Tools são chamadas como `mcp__<server>__<tool>`.

### `codex-subagent`
- Função: subagente Codex como MCP
- Comando: `codex mcp-server`

### `n8n-mcp`
- Função: orquestração N8N (workflows, nodes, exec)
- Endpoint: `https://n8n.srv19105.nvhm.cloud`
- Tools chave: `mcp__claude_ai_n8n__execute_workflow`, `search_workflows`, `get_workflow_details`
- Path: `/Users/jesus/.claude/plugins/marketplaces/n8n-mcp/dist/mcp/index.js`

### `dadosbr`
- Função: dados públicos brasileiros (CNPJ, CEP, DataJud)
- Pacote: `@aredes.me/mcp-dadosbr`
- Env: `DATAJUD_API_KEY`

### `healthcare-mcp`
- Função: dados de saúde (FDA, ICD, drug interactions)
- Pacote: `healthcare-mcp`

### `word-document-server`
- Função: criar/editar arquivos Word (.docx)
- Pacote: `office-word-mcp-server`

### `cerebra-legal`
- Função: análise legal estruturada (raciocínio jurídico)
- Path: `/Users/jesus/Desktop/STEMMIA Dexter/FERRAMENTAS/jurídicas/MCPs/mcp-cerebra-legal-server/build/index.js`

### `brlaw`
- Função: jurisprudência BR (servidor uv)
- Path: `/Users/jesus/Desktop/STEMMIA Dexter/FERRAMENTAS/jurídicas/MCPs/brlaw_mcp_server`

### `telegram-notify`
- Função: envia notificações ao bot @stemmiapericia_bot
- Env: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID=8397602236`

### `medical-mcp`
- Função: utilidades médicas
- Path: `/Users/jesus/Desktop/STEMMIA Dexter/FERRAMENTAS/jurídicas/MCPs/medical-mcp/build/index.js`

### `sqlite`
- Função: SQL contra `process-mapper.db`
- Path: `/Users/jesus/Desktop/ANALISADOR FINAL/process-mapper.db`

### `filesystem`
- Função: acesso a arquivos restrito
- Roots: `~/Desktop/ANALISADOR FINAL/processos`, `~/Desktop/PERÍCIA`

### `pdf-reader`
- Função: leitura de PDFs
- Pacote: `pdf-reader-mcp`

### `playwright`
- Função: controle de browser (Playwright)
- Tools: `mcp__playwright__browser_*` (navigate, click, snapshot, fill_form, take_screenshot etc.)

### `obsidian`
- Função: acesso ao vault Obsidian STEMMIA
- Vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/STEMMIA`
- Comando: `obsidian-mcp`

### `perplexity`
- Função: busca via Perplexity API
- Env: `PERPLEXITY_API_KEY`

### `semantic-scholar`
- Função: papers acadêmicos
- Pacote: `semanticscholar-mcp-server`

### `context-portal`
- Função: gerenciamento de contexto/projeto
- Pacote: `context-portal`

### Outros MCPs visíveis no harness (deferred via ToolSearch)
- `mcp-brasil` — 326 tools jurídicas/governamentais (`call_tool`, `executar_lote`, `listar_features`, `planejar_consulta`, `recomendar_tools`, `search_tools`)
- `pje-mcp` — PJe (`pje_buscar_processo`, `pje_listar_processos`, `pje_status`, `pje_configurar_certificado`, etc.)
- `mercadolivre` — `search_items`, `get_item`, `get_categories`, etc.
- `claude_ai_PubMed` — `search_articles`, `get_full_text_article`, `find_related_articles`
- `claude_ai_Context7` — docs de bibliotecas
- `claude_ai_Exa` — `web_search_exa`, `web_fetch_exa`
- `claude_ai_Amplitude` — analytics (não usado em perícia)
- `sequential-thinking` — `sequentialthinking`
- `sentry`, `Linear`, `Stripe`, `Supabase`, `Canva`, `Cloudflare`, `Gmail`, `Google Calendar`, `Google Drive`, `monday.com`, `CData`, `Port_IO` — todos `authenticate` (não autenticados)

---

## 5) HOOKS (6 eventos, 11 comandos)

Configurados em `/Users/jesus/.claude/settings.json`.

### `SessionStart` (2)
- `~/stemmia-forense/hooks/iniciar-sessao.sh` — bootstrap de sessão
- `python3 ~/stemmia-forense/hooks/anti_mentira_session_start.py` — sistema anti-mentira

### `PreToolUse` (matcher: Bash) (1)
- `~/stemmia-forense/hooks/bloquear-delecao.sh` — bloqueia rm/delete sem dupla confirmação

### `UserPromptSubmit` (2)
- `python3 ~/.claude/scripts/sugerir_plugins.py` — sugere plugin pertinente ao prompt
- `python3 ~/stemmia-forense/hooks/anti_mentira_prompt_submit.py` — captura intenção

### `Stop` (2)
- `python3 ~/stemmia-forense/hooks/bloquear-perguntas-retoricas.py` — bloqueia "posso?" / "quer que eu?"
- `python3 ~/stemmia-forense/hooks/anti_mentira_stop.py` — valida claims antes de finalizar

### `PreCompact` (2)
- `~/stemmia-forense/hooks/salvar-contexto-bruto.sh` — backup bruto antes do compact
- `~/stemmia-forense/hooks/gerar-sintese-precompact.sh` — síntese para Registros Sessões

### `SessionEnd` (2)
- `~/stemmia-forense/hooks/finalizar-sessao.sh` — fecha sessão
- `~/stemmia-forense/hooks/indexar-sessao.sh` — indexa para busca posterior

Editar: `~/.claude/settings.json` (chave `hooks`).

---

## 6) SCRIPTS PJe (28 .py em `~/stemmia-forense/src/pje/`)

### `atualizar_pdfs.py`
- Função: atualiza PDFs de processos no diretório
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/atualizar_pdfs.py`

### `atualizar-pje.py`
- Função: atualiza dados gerais do PJe
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/atualizar-pje.py`

### `baixar_avulsos_emergencia.py`
- Função: download de emergência de documentos avulsos
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/baixar_avulsos_emergencia.py`

### `baixar_documentos_processo_aberto.py`
- Função: baixa todos os docs do processo já aberto no PJe
- Quando usar: processo aberto no Chrome PJe via debug 9223
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/baixar_documentos_processo_aberto.py`

### `baixar_prioritarios.py`
- Função: baixa apenas processos marcados como prioridade
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/baixar_prioritarios.py`

### `baixar_push_pje_playwright.py`
- Função: download via Playwright (alternativa ao Selenium)
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/baixar_push_pje_playwright.py`

### `baixar_push_pje.py`
- Função: download principal (Selenium + Chrome debug 9223 + perfil isolado)
- Quando usar: rotina diária PJe (via BAIXAR_PJE.bat no Windows)
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/baixar_push_pje.py`

### `comparar_versoes.py`
- Função: compara versões de PDFs/processos
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/comparar_versoes.py`

### `consultar_aj.py`
- Função: consulta AJ (assistência judiciária) genérica
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/consultar_aj.py`

### `consultar_ajg.py`
- Função: consulta AJG específica
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/consultar_ajg.py`

### `contar_push_pje.py`
- Função: conta itens do PUSH PJe
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/contar_push_pje.py`

### `datajud_client.py`
- Função: cliente HTTP da API DataJud (CNJ)
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/datajud_client.py`

### `deadline_monitor.py`
- Função: monitora prazos processuais
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/deadline_monitor.py`

### `gerar_lista_prioridade.py`
- Função: gera lista de processos prioritários
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/gerar_lista_prioridade.py`

### `gerar_lista_push_de_aj.py .rtf`
- Função: gera lista PUSH a partir de AJ (atenção: nome com espaço + .rtf)
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/gerar_lista_push_de_aj.py .rtf`

### `incluir_push.py`
- Função: inclui processos no PUSH PJe
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/incluir_push.py`

### `inventariar_primeira_pagina_pje.py`
- Função: inventaria primeira página do PJe (lista de pendentes)
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/inventariar_primeira_pagina_pje.py`

### `monitor.py`
- Função: monitor genérico
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/monitor.py`

### `monitorar_movimentacao.py`
- Função: monitora movimentações em processos cadastrados
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/monitorar_movimentacao.py`

### `organizar_processos_pje.py`
- Função: organiza pasta de processos baixados
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/organizar_processos_pje.py`

### `pje_clicar_prancheta_abrir.py`
- Função: clica na prancheta + abre processo (automação UI específica)
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/pje_clicar_prancheta_abrir.py`

### `pje_standalone.py`
- Função: execução standalone do PJe (sem orquestrador)
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/pje_standalone.py`

### `pje_verificacao.py`
- Função: verificação pós-download
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/pje_verificacao.py`

### `sincronizar_aj_pje.py`
- Função: sincroniza AJ com PJe
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/sincronizar_aj_pje.py`

### `teste_conexao.py`
- Função: testa conexão PJe (ping/auth)
- Arquivo: `/Users/jesus/stemmia-forense/src/pje/teste_conexao.py`

Auxiliares (não-py): `EMERGENCIA_BAIXAR_DOCS.bat`, `EMERGENCIA_CONSOLE_JS.txt`, `iniciar_chrome_debug.bat`, `listar_e_copiar.bat`, `monitor-publicacoes/`, `_analise-erros/`, `run.bat`, `run_auto.bat`, `docs_5030880.txt`, `lista-processos.txt`, `novos-online-nao-baixados.txt`, `taiobeiras-faltantes-hoje.txt`, `taiobeiras-prioridade.txt`.

---

## 7) BAT WINDOWS (21 em `~/stemmia-forense/`)

Executar do Mac com: `open -a "Parallels Desktop" /Users/jesus/stemmia-forense/<NOME>.bat`

- `ANALISAR_PROCESSOS_PJE.bat` — análise dos processos baixados
- `BAIXAR_60_FALTANTES_PJE.bat` — baixar lote de 60 faltantes
- `BAIXAR_DOCUMENTOS_PROCESSO_ABERTO.bat` — docs do processo já aberto
- `BAIXAR_PJE_17042026_LOGADO.bat` — download datado 17/04, sessão logada
- `BAIXAR_PJE_17042026.bat` — download datado 17/04
- `BAIXAR_PJE_PILOTO_TESTE_LOGADO.bat` — teste piloto
- `BAIXAR_PJE_PLAYWRIGHT_17042026.bat` — Playwright datado [ARQUIVADO 2026-04-23 em `~/stemmia-forense/arquivado-2026-04-23/`]
- `BAIXAR_PJE_PLAYWRIGHT.bat` — Playwright genérico
- `BAIXAR_PJE.bat` — rotina principal de download (Selenium)
- `BAIXAR_SELENIUM_UNBUFFERED.bat` — Selenium sem buffer (logs em tempo real)
- `BAIXAR_TAIOBEIRAS_PJE.bat` — específico Taiobeiras
- `CONTAR_PJE_PUSH.bat` — contar PUSH
- `DIAG_PYTHON_PJE.bat` — diagnóstico Python no Windows
- `DIAG_REDE_WINDOWS.bat` — diagnóstico de rede
- `FIX_GREENLET_E_BAIXAR.bat` — fix de erro greenlet
- `FIX_VCRUNTIME_ARM64.bat` — fix VC runtime ARM64
- `INCLUIR_E_BAIXAR_NOVOS_ONLINE.bat` — incluir + baixar novos
- `INCLUIR_FALTANTES_PJE.bat` — incluir faltantes
- `MATAR_E_REINICIAR_PJE.bat` — matar processos + reiniciar
- `PJE_BAIXAR_CLICANDO_ABRIR.bat` — clica em "abrir" na prancheta
- `TAIOBEIRAS_INCLUIR_E_BAIXAR.bat` — específico Taiobeiras incluir+baixar

---

## 8) COMANDOS SLASH (2 diretos + 57 `gsd:*`)

### Comandos diretos
- `/buscar-produto <produto>` — pesquisa em lojas BR via N8N (SerpAPI + Gemini). Arquivo: `/Users/jesus/.claude/commands/buscar-produto.md`
- `/mapear-pedido` — transcreve mensagem longa em etapas numeradas. Arquivo: `/Users/jesus/.claude/commands/mapear-pedido.md`

### Comandos `/gsd:*` (57)
Pipeline de desenvolvimento. Arquivos: `/Users/jesus/.claude/commands/gsd/*.md`

Lifecycle: `new-project`, `new-milestone`, `new-workspace`, `list-workspaces`, `remove-workspace`, `add-phase`, `insert-phase`, `remove-phase`, `complete-milestone`, `milestone-summary`

Planejamento: `plan-phase`, `plan-milestone-gaps`, `research-phase`, `discuss-phase`, `validate-phase`, `list-phase-assumptions`, `roadmapper` (via subagent)

Execução: `execute-phase`, `do`, `next`, `quick`, `fast`, `autonomous`, `manager`, `pause-work`, `resume-work`, `reapply-patches`

UI: `ui-phase`, `ui-review`

Verificação: `verify-work`, `audit-milestone`, `audit-uat`, `health`, `forensics`, `debug`

TODO/backlog: `add-todo`, `check-todos`, `add-backlog`, `review-backlog`, `note`, `plant-seed`, `add-tests`

PR/branch: `pr-branch`, `ship`, `cleanup`

Telemetria/perfil: `stats`, `profile-user`, `set-profile`, `progress`, `update`, `session-report`, `review`, `thread`, `workstreams`

Suporte: `help`, `settings`, `join-discord`, `map-codebase`

---

## DIAGRAMA RÁPIDO — quando usar o quê (perícia)

```
Recebi nomeação                  → orq-analise-rapida
Análise profunda                 → orq-analise-completa
Pesquisar jurisprudência         → orq-jurisprudencia
Buscar artigos médicos           → buscador-academico (+ MCP PubMed paralelo)
Verificar erros materiais        → orq-erros-materiais
Verificar proposta honorários    → orquestrador-verificacao-proposta
Gerar laudo                      → padronizador-estilo → redator-laudo → revisor-laudo → verificador-de-fontes
Baixar processos PJe (Windows)   → BAIXAR_PJE.bat (chama baixar_push_pje.py)
Monitorar movimentações          → monitor.py + monitorar_movimentacao.py
Texto ditado                     → revisor-texto-ditado
Pesquisar produto                → /buscar-produto <nome>
```

---

## REFERÊNCIAS

- Settings: `/Users/jesus/.claude/settings.json`
- MCP config: `/Users/jesus/.claude/.mcp.json`
- Agentes: `/Users/jesus/.claude/agents/`
- Skills locais: `/Users/jesus/.claude/skills/`
- Plugins: `/Users/jesus/.claude/plugins/`
- Commands: `/Users/jesus/.claude/commands/`
- Hooks Stemmia: `/Users/jesus/stemmia-forense/hooks/`
- Scripts PJe: `/Users/jesus/stemmia-forense/src/pje/`
- BAT Windows: `/Users/jesus/stemmia-forense/`
- Diário: `/Users/jesus/Desktop/DIARIO-PROJETOS.md`
- CLAUDE.md global: `/Users/jesus/.claude/CLAUDE.md`
