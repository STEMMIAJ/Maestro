# ROADMAP — Sistema Pericial Stemmia (Integração Final)

**Versão:** v1.0
**Data:** 2026-04-17
**Granularidade:** coarse (3 fases)
**Modo:** yolo
**Cobertura:** 17/17 requisitos v1 mapeados

---

## Phases

- [ ] **Phase 1: BANCO** — Popular BANCO-DADOS e expor via MCP custom (textual + semantico)
- [ ] **Phase 2: COLA** — Plugin master `stemmia-pericial` com comando unico `/pericia [CNJ]`
- [ ] **Phase 3: VERIF** — Painel de verificacao manual em 3 modos (HTML, PDF, CLI)

---

## Phase Details

### Phase 1: BANCO
**Goal**: Banco de Dados deixa de estar vazio e passa a ser consultavel programaticamente por busca textual e semantica.
**Depends on**: Nada (primeira fase)
**Complexity**: M
**Requirements**: REQ-BANCO-01, REQ-BANCO-02, REQ-BANCO-03, REQ-BANCO-04, REQ-BANCO-05
**Success Criteria** (o que deve ser VERDADE):
  1. `BANCO-DADOS/{DIREITO,MEDICINA,PERICIA,TI}` contem >= 100 arquivos reais (PDF/MD/TXT) por area, verificavel via `find BANCO-DADOS -type f | wc -l`.
  2. Comando `python3 indexar_banco.py` regenera indice Whoosh em < 2 minutos sem erro.
  3. Indice semantico Chroma criado com modelo `paraphrase-multilingual-MiniLM-L12-v2` rodando 100% local (zero chamadas externas verificavel via captura de rede).
  4. MCP `stemmia-banco` aparece em `claude mcp list` e responde as 4 tools (`buscar_textual`, `buscar_semantica`, `listar_areas`, `obter_documento`) com resultados nao-vazios.
  5. Vault Obsidian abre em `BANCO-DADOS/` com Dataview habilitado e lista os arquivos populados.
**Plans**: TBD
**UI hint**: no

### Phase 2: COLA
**Goal**: Os 85 agentes + 64 scripts + 5 workflows ficam acessiveis por UM comando que orquestra o pipeline completo, e a cobertura de ANALISE.md sobe de 4% para >= 80%.
**Depends on**: Phase 1 (orquestrador chama `stemmia-banco` na etapa de busca)
**Complexity**: L
**Requirements**: REQ-COLA-01, REQ-COLA-02, REQ-COLA-03, REQ-COLA-04, REQ-COLA-05, REQ-COLA-06, REQ-COLA-07
**Success Criteria** (o que deve ser VERDADE):
  1. Plugin `stemmia-pericial` instalavel via `claude-code plugin install ./stemmia-pericial` sem erro, com `plugin.json` valido.
  2. `claude /agents` mostra os 85 agentes empacotados pelo plugin (link/copia para `~/.claude/agents/`).
  3. Plugin referencia (nao copia) os 64 scripts de `ANALISADOR FINAL/scripts/` e `which` resolve cada um quando invocado.
  4. Comando `/pericia [CNJ]` executa download -> triagem -> analise profunda -> busca banco -> proposta/aceite -> verificacao em < 10 minutos para um CNJ ja baixado.
  5. Cobertura de `ANALISE.md` sobe para >= 80% dos 157 processos (>= 126/157), verificavel via `find processos -name ANALISE.md | wc -l`.
  6. README.md do plugin (1 pagina) documenta os comandos principais e exemplo de uso.
**Plans**: TBD
**UI hint**: no

### Phase 3: VERIF
**Goal**: Dr. Jesus consegue verificar manualmente cada analise gerada em 3 modos interoperaveis (HTML para mouse, PDF para imprimir, CLI para velocidade), com estado compartilhado.
**Depends on**: Phase 2 (precisa de processos com ANALISE.md gerada para verificar)
**Complexity**: M
**Requirements**: REQ-VERIF-01, REQ-VERIF-02, REQ-VERIF-03, REQ-VERIF-04, REQ-VERIF-05
**Success Criteria** (o que deve ser VERDADE):
  1. `painel-verificacao.html` aberto em browser local lista todos os processos com ANALISE.md e mostra checkboxes "verificado/erro/pendente" por secao (CIDs, datas, nomes, valores).
  2. Marcar checkbox no HTML persiste em `verificacoes.json` (via LocalStorage + escrita em arquivo) e sobrevive a recarga da pagina.
  3. `python3 gerar_checklist.py [CNJ]` gera PDF imprimivel com quesitos+respostas+espaco para anotacao manual.
  4. `python3 verificar.py [CNJ]` abre TUI no terminal com navegacao `j/k/space/q` e grava no MESMO `verificacoes.json` que o HTML usa.
  5. Os 3 modos sao testados em >= 10 processos reais e o `verificacoes.json` mantem consistencia entre eles (sem corrupcao, sem perda de marcacao).
**Plans**: TBD
**UI hint**: yes

---

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. BANCO | 0/TBD | Not started | - |
| 2. COLA | 0/TBD | Not started | - |
| 3. VERIF | 0/TBD | Not started | - |

---

## Coverage Map

| Requirement | Phase |
|---|---|
| REQ-BANCO-01 | Phase 1 |
| REQ-BANCO-02 | Phase 1 |
| REQ-BANCO-03 | Phase 1 |
| REQ-BANCO-04 | Phase 1 |
| REQ-BANCO-05 | Phase 1 |
| REQ-COLA-01 | Phase 2 |
| REQ-COLA-02 | Phase 2 |
| REQ-COLA-03 | Phase 2 |
| REQ-COLA-04 | Phase 2 |
| REQ-COLA-05 | Phase 2 |
| REQ-COLA-06 | Phase 2 |
| REQ-COLA-07 | Phase 2 |
| REQ-VERIF-01 | Phase 3 |
| REQ-VERIF-02 | Phase 3 |
| REQ-VERIF-03 | Phase 3 |
| REQ-VERIF-04 | Phase 3 |
| REQ-VERIF-05 | Phase 3 |

**Total:** 17/17 mapeados, zero orfaos, zero duplicados.

---

## Phase Dependencies (visual)

```
Phase 1 (BANCO)
   |
   v
Phase 2 (COLA)  -- consome stemmia-banco MCP
   |
   v
Phase 3 (VERIF) -- consome ANALISE.md gerados
```

---

*Last updated: 2026-04-17 — initial draft*
