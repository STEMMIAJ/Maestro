# Sistema Pericial Stemmia — Integração Final

## What This Is

Hub central do ecossistema de perícia médica judicial do Dr. Jesus. Sistema BROWNFIELD com 5 anos de acumulação: 64 scripts Python funcionais, 85 agentes Claude especializados, 17 MCPs, 25 plugins, 5 workflows N8N, 7 hooks. Tudo funciona ISOLADO; nada está integrado num fluxo único.

**Esta iniciativa NÃO cria coisas novas.** Faz a **cola** entre o que já existe + popula o banco de dados (vazio na prática, 12 arquivos em 100 pastas estruturadas) + cria UM ponto de entrada operacional.

## Context

**Usuário:** médico perito judicial, autista (TEA) + TDAH, memória comprometida, sobrecarga severa após falecimento do pai (11/fev/2026).

**Dor central:** "Claude começa, vê 50 ferramentas soltas, perde o fio e desiste." Cada sessão começa do zero. Nada termina.

**Estado atual mensurado (DIAGNOSTICO-17042026.md):**
- 157 pastas de processos / 142 com FICHA.json (90%) / **6 com ANALISE.md (4%)**
- 100 subpastas no BANCO-DADOS / **12 arquivos reais (1% populado)**
- 25 plugins instalados / ~5 usados
- 50+ comandos GSD instalados / **ZERO projetos GSD criados** (este é o primeiro)

## Core Value

**O ÚNICO comportamento que precisa funcionar:**
Dr. Jesus digita `/perícia [CNJ]` e o sistema dispara TUDO sequencialmente sem ele precisar lembrar qual script chamar: download → análise leve → análise profunda → busca no banco → geração de petição → verificação → entrega.

Tudo o resto é secundário.

## Requirements

### Validated (já existem e funcionam)
- ✓ Pipeline PJe/AJ/AJG download (Selenium + Chrome CDP 9223) — existing
- ✓ Triagem leve (FICHA.json + URGENCIA.json) — existing, 90% cobertura
- ✓ 85 agentes especializados (peticao-*, verificador-*, redator-laudo) — existing
- ✓ Workflows N8N locais (aceite, análise, verificador, monitor DataJud) — existing
- ✓ Sistema de memória (episodic-memory + claude-mem) — existing

### Active (a entregar nesta iniciativa)
- [ ] **REQ-BANCO-01**: BANCO-DADOS populado com PDFs/textos reais (mínimo 100 arquivos por área)
- [ ] **REQ-BANCO-02**: MCP custom `stemmia-banco` consultável por busca textual (Whoosh)
- [ ] **REQ-BANCO-03**: MCP `stemmia-banco` consultável por busca semântica (Chroma + embeddings locais)
- [ ] **REQ-BANCO-04**: Vault Obsidian apontado pro banco (navegação visual)
- [ ] **REQ-COLA-01**: Plugin master `stemmia-pericial` empacotando 85 agentes + 64 scripts
- [ ] **REQ-COLA-02**: Comando único `/perícia [CNJ]` orquestra pipeline completo
- [ ] **REQ-COLA-03**: Análise profunda (ANALISE.md) cobertura ≥80% dos processos (hoje: 4%)
- [ ] **REQ-VERIF-01**: Painel HTML local de verificação manual (clicar/marcar verificado/erro)
- [ ] **REQ-VERIF-02**: Checklist PDF imprimível por processo
- [ ] **REQ-VERIF-03**: Painel CLI no terminal (rapidez, sem mouse)

### Out of Scope (explicitamente fora)
- Reescrever scripts Python existentes — só integrar
- Criar novos agentes — usar os 85 que já existem
- N8N cloud — bloqueado, manter só local
- Computer-use — proibido pelo perfil
- Site público / Cowork web — focar no terminal Claude Code primeiro
- Sistema Clínica Minas — projeto separado
- Reorganizar Mesa Desktop — fora de escopo

## Key Decisions

| Decisão | Rationale | Outcome |
|---|---|---|
| 3 fases coarse | Usuário pediu progresso visível, não 12 microfases | Pending |
| YOLO mode | Perfil: "decidir e fazer, sem perguntar" | Pending |
| Tudo Opus | Regra do CLAUDE.md: NUNCA rebaixar | Pending |
| Subagent-driven (Opus) | Não dependência de boa vontade entre sessões | Pending |
| Hub = `STEMMIA Dexter/` | Decisão registrada em DECISOES.md (14/abr/2026) | Pending |
| Banco populado ANTES de MCP | Sem conteúdo, busca retorna vazio | Pending |
| Verificador testa 3 modos (HTML+PDF+CLI) | Usuário pediu testar todos, não escolheu | Pending |

## Constraints

- **Tempo do usuário:** mínimo (sobrecarga, autismo, TDAH). Cada interação custa.
- **Hardware:** Mac M-series, 16GB+ RAM. Roda local. PJe SÓ no Windows/Parallels.
- **Modelos:** Opus 4.7 obrigatório (CLAUDE_CODE_SUBAGENT_MODEL).
- **MCPs caídos:** playwright, browser-mcp — NÃO usar nesses MCPs nesta iniciativa.
- **Permissões:** Bash(*), Edit(*), Write(*), WebFetch(*), WebSearch — zero fricção.

## Success Criteria (mensurável no fim do projeto)

1. Cobertura ANALISE.md ≥80% dos 157 processos (era 4%)
2. BANCO-DADOS com ≥100 arquivos por área (era 12 total)
3. Comando `/perícia [CNJ]` executa pipeline completo em <10min
4. Painel verificação manual usado em ≥10 processos reais
5. Plugin `stemmia-pericial` instalável via marketplace local

## Evolution

Documento evolui em transições de fase e milestone.

**Após cada fase:**
1. Requisitos invalidados → Out of Scope
2. Requisitos validados → Validated com referência da fase
3. Novos requisitos → Active
4. Decisões → Key Decisions

---

*Last updated: 2026-04-17 após inicialização*
