---
titulo: Relatórios Consolidados
bloco: 13_reports
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 13 — Reports

## Definição do domínio
Relatórios consolidados e sínteses que Maestro/OpenClaw geram ou consomem. Saída legível para decisão (humana e agentes). Snapshot periódico do estado da base, do mercado, de oportunidades e da própria carreira.

## Subdomínios
- `snapshots/` — foto de um momento (estado da base, do skill map, do backlog)
- `quarterly_reviews/` — revisão trimestral: o que avançou, o que travou, replanejamento
- `opportunity_reports/` — vagas, editais, concursos, licitações relevantes
- `market_research/` — salários, stacks em alta, tendências por segmento
- `master_summaries/` — sínteses mestras ("1 página sobre IA aplicada a perícia, abril 2026")

## Perguntas que este bloco responde
- Como estava o sistema no início do trimestre vs hoje?
- Onde o mercado está indo no próximo semestre?
- Que vaga ou edital apareceu e compensa perseguir?
- Que síntese mandar para colega/juiz/contratante?

## Como coletar conteúdo
- Pipelines em `14_automation/` geram relatórios periódicos
- Inputs: `11_personal_skill_mapping`, `10_career_map`, `12_sources`
- Pesquisa manual de editais (CNJ, TRF, universidades) e vagas
- Web research (com fontes datadas sempre)

## Critérios de qualidade
- Cada relatório tem data de geração e janela temporal coberta
- Separar FATO (dado datado) de INTERPRETAÇÃO (análise)
- Snapshot = imutável após gerado (versionado)
- Master summary = máx 1 página, densidade alta

## Exemplos de artefatos
- `snapshots/2026-Q2_state_of_base.md`
- `quarterly_reviews/2026-Q1_review.md`
- `opportunity_reports/2026-04_editais_pericia.md`
- `market_research/2026-04_salarios_data_saude_br.md`
- `master_summaries/ia_pericia_1pag.md`

## Interseções
- `11_personal_skill_mapping` (alimenta quarterly_reviews)
- `14_automation` (pipelines geram relatórios)
- `15_memory/decisions` (decisões derivadas de reports ficam lá)
- `10_career_map` (opportunity_reports consomem taxonomia de cargos)
