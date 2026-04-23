---
titulo: Modelo operacional do Maestro / OpenClaw
tipo: relatorio_governanca
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
---

# Maestro Operational Model

Modelo operacional do Maestro (Control Center sobre OpenClaw). Descreve ciclo, cronograma e comandos.

## Ciclo canônico

```
    indexar  →  buscar  →  promover  →  revisar  →  (volta a indexar)
```

1. **Indexar** — `openclaw memory index` varre Markdown, constrói índice invertido + embeddings.
2. **Buscar** — `openclaw memory search` atende consultas semânticas durante trabalho real.
3. **Promover** — conteúdo bruto de `16_inbox/` aprovado vira memória em `15_memory/promoted/`.
4. **Revisar** — jobs periódicos detectam stale, duplicado, lacuna; geram relatório em `13_reports/`.

O ciclo é **incremental**: indexação diária, busca sob demanda, promoção semanal, revisão trimestral.

## Cronograma recomendado

| Cadência | Ação | Comando / Job |
|---|---|---|
| A cada commit relevante | reindex seletivo | `openclaw memory index <path>` |
| Diário 03h | reindex full | job `reindex-daily` |
| Semanal (domingo 20h) | digest da semana | job `digest-weekly` → `13_reports/` |
| Semanal | revisar `16_inbox/` e promover | manual, com checklist |
| Mensal | auditar `15_memory/promoted/` | relatório qualidade |
| Trimestral | knowledge refresh | spec `knowledge_refresh_pipeline_spec.md` |
| Trimestral | source validation | spec `source_validation_pipeline_spec.md` |
| Ad hoc | skill mapping | spec `skill_mapping_pipeline_spec.md` |

## Comandos — exemplos reais para esta base

### Indexação

```bash
# Indexacao completa do repo
openclaw memory index "~/Desktop/STEMMIA Dexter/knowledge-tech-career"

# Indexacao incremental de um bloco
openclaw memory index "~/Desktop/STEMMIA Dexter/knowledge-tech-career/08_ai_and_automation"

# Forcar rebuild (quando esquema mudar)
openclaw memory index --rebuild "~/Desktop/STEMMIA Dexter/knowledge-tech-career"
```

### Busca

```bash
# Busca semantica sobre todo o repo
openclaw memory search "prompt caching anthropic"

# Restringir a um bloco
openclaw memory search "criterios DII previdenciario" --scope 09_legal_medical_integration

# Busca por skill mapeada
openclaw memory search "evidencias de python async aplicado" --scope 11_personal_skill_mapping

# Busca em conversas promovidas
openclaw memory search "decisao sobre PJe CDP" --scope 15_memory/promoted
```

### Promoção (quando comando existir — TODO verificar cobertura OpenClaw)

```bash
# Listar candidatos a promocao (stub, RESEARCH)
openclaw memory review --inbox 16_inbox/raw_conversations

# Promover item aprovado (manual por enquanto: mv + commit)
```

## Conteúdo que entra no índice

- `00_governance/` a `11_personal_skill_mapping/` — fontes primárias de conhecimento.
- `12_sources/` — catálogo de fontes (metadados, não conteúdo integral).
- `13_reports/` — relatórios gerados por jobs.
- `15_memory/promoted/` — memória aprovada.
- **Excluir** `16_inbox/` do índice principal — é staging. Índice separado opcional (`--index inbox`).

## Papéis humanos

- **Dr. Jesus**: decide promoção, aprova refreshes, ajusta taxonomia.
- **Claude Code**: executa edições, escreve relatórios, redige promoções.
- **Maestro**: não decide. Sugere, busca, registra.

## Critérios de qualidade do índice

- Cobertura: >95% dos `.md` do repo indexados.
- Frescor: `last_indexed` < 24h na média.
- Precisão: top-5 de busca contém a resposta em >80% das queries (amostragem mensal, TODO medir).

## Falhas e troubleshooting

- **Busca vazia** onde deveria achar → checar `last_indexed`, rodar `index --rebuild`.
- **Resultados irrelevantes** → frontmatter pobre ou títulos genéricos. Enriquecer `titulo`, `tags`.
- **Memória promovida não aparece** → verificar se path está no escopo do index.
- **Conflito com Obsidian** — Obsidian escreve wikilinks `[[...]]` que OpenClaw pode não resolver. Preferir links relativos.

## TODO / RESEARCH

- Confirmar comandos exatos de `openclaw` na versão instalada.
- Definir escopo do índice "inbox" separado.
- Política de backup do índice (ou reindex sempre a partir do Markdown — zero estado).
- Integração com `git post-commit` para reindex incremental automático.

## Ver também

- `maestro_vs_claude_vs_git.md`
- `when_to_use_what.md`
- `14_automation/openclaw_jobs/README.md`
