# STATE — Sistema Pericial Stemmia

**Last updated:** 2026-04-17

---

## Project Reference

- **Nome:** Sistema Pericial Stemmia — Integração Final
- **Tipo:** BROWNFIELD (integração, não criação)
- **Core value:** `/pericia [CNJ]` dispara pipeline completo (download → análise → banco → petição → verificação) sem o usuário lembrar qual script chamar.
- **Foco atual:** Phase 1 (BANCO)
- **Modo:** yolo
- **Granularidade:** coarse

---

## Current Position

- **Phase:** 1 (BANCO) — Not started
- **Plan:** Nenhum criado (próximo: `/gsd:plan-phase 1`)
- **Status:** Roadmap aprovado, aguardando planejamento da Phase 1
- **Progresso geral:** 0/3 fases concluídas

```
[          ] 0%   Phase 1 (BANCO)
[          ] 0%   Phase 2 (COLA)
[          ] 0%   Phase 3 (VERIF)
```

---

## Performance Metrics

| Métrica | Baseline (17/abr) | Meta v1 | Atual |
|---|---|---|---|
| ANALISE.md cobertura | 6/157 (4%) | >= 80% (126/157) | 4% |
| BANCO-DADOS arquivos | 12 total | >= 100/área (400+ total) | 12 |
| Plugins ativos | 25 (5 usados) | +1 (stemmia-pericial) | 25 |
| MCPs custom | 0 | 1 (stemmia-banco) | 0 |
| Comando único `/pericia` | não existe | funcional <10min | n/a |

---

## Accumulated Context

### Decisões-chave (de PROJECT.md)

1. 3 fases coarse (não 12 microfases) — usuário pediu progresso visível
2. YOLO mode — perfil pede "decidir e fazer, sem perguntar"
3. Tudo Opus 4.7 — regra absoluta CLAUDE.md
4. Subagent-driven — não depender de boa vontade entre sessões
5. Hub = `STEMMIA Dexter/` — DECISOES.md (14/abr/2026)
6. Banco populado ANTES de criar MCP (sem conteúdo, busca retorna vazio)
7. Verificador testa 3 modos (HTML+PDF+CLI) — usuário pediu testar todos

### TODOs imediatos

- [ ] `/gsd:plan-phase 1` — decompor Phase 1 (BANCO) em plans executáveis
- [ ] Identificar fontes de PDFs já existentes (PERÍCIA FINAL, MODELOS, FENIX, LAUDOS-REFERENCIA) antes de baixar de fontes públicas
- [ ] Confirmar local de instalação do MCP `stemmia-banco` (pasta dentro do hub Dexter)

### Blockers

- Nenhum no momento.

### Riscos conhecidos

- MCPs caídos (playwright, browser-mcp) — não usar nesta iniciativa
- N8N cloud bloqueado — manter só local
- Computer-use proibido pelo perfil

---

## Session Continuity

### Última sessão

- **Data:** 2026-04-17
- **Ação:** Inicialização do projeto GSD (PROJECT.md + REQUIREMENTS.md + ROADMAP.md + STATE.md)
- **Resultado:** Roadmap de 3 fases aprovado, 17/17 requisitos mapeados.

### Próxima sessão

- **Ação:** `/gsd:plan-phase 1`
- **Objetivo:** Gerar plans executáveis para Phase 1 (BANCO).
- **Contexto a recuperar:** ler PROJECT.md, REQUIREMENTS.md, ROADMAP.md (este arquivo aponta para tudo).

### Arquivos-chave

- `.planning/PROJECT.md` — visão e decisões
- `.planning/REQUIREMENTS.md` — 17 requisitos com traceability preenchido
- `.planning/ROADMAP.md` — 3 fases, success criteria, coverage
- `.planning/STATE.md` — este arquivo (memória do projeto)
- `.planning/config.json` — granularity=coarse, mode=yolo
- `DIAGNOSTICO-17042026.md` — estado real do sistema (raiz do hub)

---

*Memória persistente. Atualizar a cada transição de fase ou marco relevante.*
