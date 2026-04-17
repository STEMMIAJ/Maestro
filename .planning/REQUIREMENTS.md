# Requirements — Sistema Pericial Stemmia

**Versão:** v1.0 — INTEGRAÇÃO FINAL
**Data:** 2026-04-17
**Escopo:** Cola entre componentes existentes + popular banco + UM ponto de entrada operacional

---

## v1 Requirements

### Categoria: BANCO (popular e tornar consultável)

- [ ] **REQ-BANCO-01**: Popular `BANCO-DADOS/{DIREITO,MEDICINA,PERÍCIA,TI}` com PDFs/textos reais. Mínimo: 100 arquivos por área. Fonte: PDFs já existentes em `PERÍCIA FINAL/`, `MODELOS/`, `FENIX/`, `LAUDOS-REFERENCIA/`, e download de fontes públicas (CFM, CRM, INSS, jurisprudência STJ).
- [ ] **REQ-BANCO-02**: Indexação textual (Whoosh) de todo o banco. Comando: `python3 indexar_banco.py` regenera índice em <2min.
- [ ] **REQ-BANCO-03**: Indexação semântica (Chroma + sentence-transformers local, modelo `paraphrase-multilingual-MiniLM-L12-v2`). Sem chamadas externas.
- [ ] **REQ-BANCO-04**: MCP custom `stemmia-banco` expondo 4 tools: `buscar_textual(query)`, `buscar_semantica(query)`, `listar_areas()`, `obter_documento(id)`.
- [ ] **REQ-BANCO-05**: Vault Obsidian apontando pra `BANCO-DADOS/` com plugin Dataview habilitado.

### Categoria: COLA (orquestrador master)

- [ ] **REQ-COLA-01**: Plugin local `stemmia-pericial` na estrutura padrão Claude (`plugin.json`, `agents/`, `commands/`, `skills/`).
- [ ] **REQ-COLA-02**: Plugin empacota TODOS os 85 agentes existentes em `~/.claude/agents/` (link ou cópia).
- [ ] **REQ-COLA-03**: Plugin empacota os 64 scripts Python de `ANALISADOR FINAL/scripts/` (referência, não cópia).
- [ ] **REQ-COLA-04**: Comando único `/perícia [CNJ]` orquestra: download → triagem → análise profunda → busca banco → geração proposta/aceite → verificação.
- [ ] **REQ-COLA-05**: Análise profunda (ANALISE.md) cobertura ≥80% dos 157 processos existentes (hoje: 4%). Rodar `orq-analise-completa` em batch.
- [ ] **REQ-COLA-06**: Plugin instalável no Claude Code via marketplace local (`claude-code plugin install ./stemmia-pericial`).
- [ ] **REQ-COLA-07**: Documentação de uso em README.md do plugin (1 página, comandos principais).

### Categoria: VERIF (verificação manual)

- [ ] **REQ-VERIF-01**: Painel HTML local (`painel-verificacao.html`) lista processos analisados com checkboxes: "verificado / erro / pendente" por seção (CIDs, datas, nomes, valores).
- [ ] **REQ-VERIF-02**: Painel HTML salva estado em `verificacoes.json` (LocalStorage + arquivo).
- [ ] **REQ-VERIF-03**: Checklist PDF imprimível por processo (`gerar_checklist.py [CNJ]` → PDF com quesitos+respostas+espaço pra anotar).
- [ ] **REQ-VERIF-04**: Painel CLI no terminal (`verificar.py [CNJ]`) com navegação por teclado: `j/k` mover, `space` marcar, `q` sair, salva no mesmo `verificacoes.json`.
- [ ] **REQ-VERIF-05**: Os 3 modos compartilham o MESMO `verificacoes.json` (interoperabilidade).

---

## v2 Requirements (deferred — próxima milestone)

- Integração com Cowork (Claude web) — depende do v1 estar estável
- Bot Telegram envia notificação quando análise termina
- Dashboard web público com KPIs de produção
- Auto-geração de laudo a partir do verificado
- Sincronização automática com `~/Desktop/processos-pje-windows/`

---

## Out of Scope (explicitamente fora)

| Item | Por quê |
|---|---|
| Reescrever scripts Python | Funcionam, só faltam ser chamados |
| Criar novos agentes | 85 já existem, basta empacotar |
| N8N cloud | Bloqueado pelo provedor, manter local |
| Computer-use / Playwright | MCPs caídos + proibido pelo perfil |
| Site público | Foco no terminal Claude Code primeiro |
| Sistema Clínica Minas | Projeto separado |
| Reorganizar Mesa Desktop | Fora do escopo, já reorganizada em 14/abr |
| Refatorar 85 agentes | Funcionam isolados, integração resolve |

---

## Traceability

| REQ-ID | Phase | Status |
|---|---|---|
| REQ-BANCO-01 | Phase 1 | Pending |
| REQ-BANCO-02 | Phase 1 | Pending |
| REQ-BANCO-03 | Phase 1 | Pending |
| REQ-BANCO-04 | Phase 1 | Pending |
| REQ-BANCO-05 | Phase 1 | Pending |
| REQ-COLA-01 | Phase 2 | Pending |
| REQ-COLA-02 | Phase 2 | Pending |
| REQ-COLA-03 | Phase 2 | Pending |
| REQ-COLA-04 | Phase 2 | Pending |
| REQ-COLA-05 | Phase 2 | Pending |
| REQ-COLA-06 | Phase 2 | Pending |
| REQ-COLA-07 | Phase 2 | Pending |
| REQ-VERIF-01 | Phase 3 | Pending |
| REQ-VERIF-02 | Phase 3 | Pending |
| REQ-VERIF-03 | Phase 3 | Pending |
| REQ-VERIF-04 | Phase 3 | Pending |
| REQ-VERIF-05 | Phase 3 | Pending |

**Cobertura:** 17/17 (100%), zero órfãos, zero duplicados.

---

**Total v1:** 17 requisitos | 3 categorias
