---
titulo: Memória Operacional
bloco: 15_memory
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 15 — Memory

## Definição do domínio
Memória operacional da base: notas diárias, memórias promovidas (sobreviveram à triagem), log de decisões e checkpoints de sessão. Separa o que é ruído (daily) do que é sinal (promoted). Espelha modelo de memória episódica → semântica.

## Subdomínios
- `daily/` — notas do dia (rápidas, sem rigor)
- `promoted/` — notas que foram revistas e promovidas (viram referência)
- `decisions/` — log imutável de decisões (ADR-like: contexto, decisão, consequência)
- `checkpoints/` — estado de sessão (o que estava em curso, como retomar)

## Perguntas que este bloco responde
- O que foi feito hoje / ontem / semana passada?
- Que nota virou conhecimento consolidado?
- Por que decidi X em Y data?
- Onde parei na sessão anterior?

## Como coletar conteúdo
- `daily/` gerado ao fim de cada sessão (manual ou via hook de `handoff-sessao`)
- Promoção: revisão semanal decide o que sobe para `promoted/`
- Decisões: toda escolha estrutural vira ADR curto aqui
- Checkpoints: usados no retorno após sobrecarga/contexto perdido

## Critérios de qualidade
- Daily: datado (`YYYY-MM-DD.md`), sem pressão de forma
- Promoted: frontmatter + fonte (qual daily deu origem)
- Decision: formato ADR (contexto → opções → decisão → data → consequências)
- Checkpoint: o suficiente para retomar sem reler 2h de sessão

## Exemplos de artefatos
- `daily/2026-04-23.md`
- `promoted/2026-04_regra_citacao_obrigatoria.md`
- `decisions/ADR-001_estrutura_blocos_00_a_16.md`
- `checkpoints/sessao_2026-04-23_readmes_bloco09-16.md`

## Interseções
- Todos os blocos (referência quando memória vira conteúdo consolidado)
- `14_automation/prompts/promote_memory_*.md` (prompt de promoção)
- `13_reports/quarterly_reviews` (revisão lê decisions e promoted)
- `00_governance` (cadência de revisão)
