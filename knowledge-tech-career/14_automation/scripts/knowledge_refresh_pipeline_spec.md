---
titulo: Knowledge Refresh Pipeline — spec
tipo: spec_pipeline
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
---

# Knowledge Refresh Pipeline

**Objetivo**: rodar trimestralmente. Releia os READMEs de cada bloco (`00_governance` a `11_personal_skill_mapping`), detecte conteúdo estagnado e sugira atualizações. **Sugere, não edita.**

## Entradas

- `0*_*/README.md`, `10_career_map/README.md`, `11_personal_skill_mapping/README.md`, `12_sources/**/README.md`.
- `git log -- <readme>` de cada — para medir frescor real (último commit relevante).
- `15_memory/promoted/**` — novas memórias por bloco desde último refresh.
- `12_sources/**` — novas fontes adicionadas por bloco.

## Critérios de "stale"

Um README é **stale** se qualquer das condições:

- `ultima_atualizacao` no frontmatter > 90 dias atrás.
- Último commit git > 90 dias e houve ≥3 novas memórias promovidas no bloco no período.
- Bloco acumulou ≥5 TODO/RESEARCH não endereçados citados em outros arquivos.
- Taxonomia de skills do bloco mudou (`11_personal_skill_mapping/taxonomy.yaml` diff).

## Saída

- `13_reports/master_summaries/knowledge_refresh_YYYY-Q<n>.md` com, por bloco:
  - status (`fresco` / `stale` / `critico`)
  - motivo
  - lista de memórias novas a incorporar
  - lista de TODO/RESEARCH pendentes
  - sugestão de seções a adicionar/reescrever
- `13_reports/automation_logs/YYYY-MM-DD_knowledge_refresh.jsonl`.

## Algoritmo

1. Enumerar READMEs-alvo.
2. Ler frontmatter + `git log -1 --format=%cI <file>`.
3. Contar memórias promovidas no bloco desde `ultima_atualizacao`.
4. Scan de TODO/RESEARCH: regex `\b(TODO|RESEARCH|FIXME)\b` em arquivos do bloco.
5. Classificar (fresco <60d, atencao 60-90d, stale 90-180d, critico >180d).
6. Gerar relatório Markdown determinístico (ordenado por criticidade desc).

## Regras

- **Read-only em READMEs**. Zero escrita fora de `13_reports/`.
- Rodar com `--quarter auto` detecta trimestre vigente; `--quarter 2026-Q2` força.
- Sem consulta a rede.

## Agendamento

Proposta: `CronCreate` trimestral — 1 de jan/abr/jul/out às 03h. Spec apenas; **não criar agora**.

## TODO

- Definir se `ultima_atualizacao` do frontmatter é autoritativa ou se git é.
- Criar schema JSON do relatório para permitir pós-processamento futuro.
- Integrar com skill_matrix para detectar "bloco com skill subindo mas README não reflete".
