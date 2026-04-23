---
titulo: Skill Mapping Pipeline — spec
tipo: spec_pipeline
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
---

# Skill Mapping Pipeline

**Objetivo**: manter `11_personal_skill_mapping/skill_matrix.md` sincronizado com evidências reais espalhadas pelos demais blocos do repo e pelas conversas ingeridas.

## Entradas

- `11_personal_skill_mapping/` — skill_matrix atual + taxonomia de skills.
- `15_memory/promoted/**` — memória aprovada com frontmatter.
- `13_reports/**` — relatórios que mencionam entregas.
- `16_inbox/raw_conversations/_meta/index.jsonl` — volume de conversas por tema.
- `12_sources/**` — fontes estudadas (indica *input*, não *output*).
- Opcional: `git log --author="Jesus"` em repos relacionados.

## Saída

- `11_personal_skill_mapping/skill_matrix.md` atualizado.
- `13_reports/master_summaries/skill_matrix_diff_YYYY-MM-DD.md` com diff.
- `13_reports/automation_logs/YYYY-MM-DD_skill_mapping.jsonl`.

## Algoritmo

1. **Carregar taxonomia** — lista de skills esperadas (ex: `python.async`, `pje.cdp`, `pericia.laudo_previdenciario`, `ai.prompt_caching`). Arquivo: `11_personal_skill_mapping/taxonomy.yaml` (TODO criar).
2. **Varrer evidências** — para cada arquivo em `15_memory/promoted/`, ler frontmatter `skills: [...]`, e corpo procurando tags `#skill/<slug>`.
3. **Agregar** por skill:
   - `evidence_count`
   - `last_seen` (max `data_origem`)
   - `levels`: quantas evidências por `evidence_level`
   - `artifacts`: lista de paths citando a skill
4. **Classificar nível** (heurística inicial, ajustar):
   - `exposto`: 1–2 evidências, só leitura/estudo.
   - `aplicado`: ≥3 evidências com `evidence_level: experiencia`.
   - `sólido`: ≥6 evidências, inclui ≥1 entrega real documentada em `13_reports/`.
   - `dominio`: ≥12 evidências + skill já ensinada/documentada por Jesus.
5. **Gerar matrix** — Markdown com tabela `skill | nivel | evidence_count | last_seen | top 3 artifacts`.
6. **Diff** — comparar com versão anterior (git), gerar relatório humano-legível.
7. **Sugerir lacunas** — skills da taxonomia com 0 evidência → seção "Lacunas" no relatório.

## Regras de integridade

- Não rebaixar nível automaticamente — só humano faz downgrade.
- Nível só sobe com evidências **promovidas** (não raw).
- Se uma skill some por >180 dias sem nova evidência → flag "skill_dormente".

## Invocação

```
python ~/stemmia-forense/automacoes/skill_mapping.py \
  --repo "~/Desktop/STEMMIA Dexter/knowledge-tech-career" \
  --apply
```

## TODO

- Definir taxonomy.yaml — partir do `10_career_map/` atual.
- Regras de parsing de tags `#skill/...` no corpo Markdown.
- Integração com `git log` (evidência "fiz commit tocando X").
- Decidir se embeddings do OpenClaw ajudam na classificação automática (RESEARCH).
