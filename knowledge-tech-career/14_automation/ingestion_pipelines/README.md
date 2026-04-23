---
titulo: Ingestion Pipelines — material bruto a memória estruturada
tipo: readme_tecnico
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
---

# 14_automation/ingestion_pipelines

Pipelines de ingestão são **specs (não código)** que descrevem como transformar material bruto (exports de IA, transcrições, notas de Obsidian, PDFs, HTMLs) em memória estruturada dentro deste repositório.

## Fluxo canônico

```
fonte bruta  →  16_inbox/raw_<tipo>/  →  parse/normalize  →  dedupe  →
extracao de decisoes/fatos  →  15_memory/promoted/<bloco>/  →  indexacao OpenClaw
```

## Princípios

- **Não destrutivo**: raw nunca é apagado — é referenciado.
- **Idempotente**: rodar duas vezes não duplica memória.
- **Rastreável**: cada arquivo promovido cita `source_path`, `source_hash`, `ingested_at`.
- **Explícito sobre confiança**: `evidence_level` (oficial / academico / experiencia / inferencia).
- **Humano aprova promoção**: pipeline sugere, Dr. Jesus confirma antes de mover para `15_memory/promoted/`.

## Pipelines previstos

| Pipeline | Spec | Status |
|---|---|---|
| Conversas de IA | `conversations_ingestion_plan.md` | spec |
| Fontes multi-IA | `ai_conversation_sources.md` | catalogo |
| Backlog futuro | `future_imports_from_other_ai_tools.md` | backlog |
| Skill mapping | `../scripts/skill_mapping_pipeline_spec.md` | spec |
| Knowledge refresh | `../scripts/knowledge_refresh_pipeline_spec.md` | spec |
| Source validation | `../scripts/source_validation_pipeline_spec.md` | spec |

## Saídas canônicas

- `15_memory/promoted/` — memória aprovada.
- `13_reports/ingestion_logs/` — log estruturado (TODO criar pasta).
- `11_personal_skill_mapping/skill_matrix.md` — evidências de skill coletadas.

## Não-objetivos

- Não é ETL de banco relacional. Markdown-first.
- Não faz NLP pesado dentro do repo — extrações avançadas podem delegar a scripts em `~/stemmia-forense/automacoes/` e gravar resultado aqui.
