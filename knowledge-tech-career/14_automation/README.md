---
titulo: Automação — Prompts, Scripts, Pipelines (SPEC-ONLY)
bloco: 14_automation
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 14 — Automation

## Definição do domínio
Prompts curados, scripts Python, jobs OpenClaw, fluxos Telegram, specs de dashboard e pipelines de ingestão que alimentam e mantêm a base. **ATENÇÃO: bloco em modo planejamento — nada executa de verdade ainda.** Apenas specs, pseudocódigo e contratos.

## Subdomínios
- `prompts/` — prompts versionados (promoção de memória, gap analysis, síntese quarterly)
- `scripts/` — Python (ingestão, validação, verificação de link, renderização)
- `openclaw_jobs/` — jobs agendados (crawl, resumo, promoção)
- `telegram_flows/` — interações via @stemmiapericia_bot (pedir síntese, aprovar promoção)
- `dashboard_specs/` — specs de painéis (estado da base, progresso de estudo, backlog)
- `ingestion_pipelines/` — contratos de entrada (inbox → triagem → blocos)

## Perguntas que este bloco responde
- Que prompt gera a síntese mestra X?
- Como um item de `16_inbox/` vira conteúdo em `07_health_data/`?
- Que job roda toda segunda de manhã?
- Qual o contrato de entrada do pipeline de ingestão?

## Como coletar conteúdo
- Extrair prompts já usados no sistema Dexter (hooks, skills, agentes)
- Documentar scripts de `~/Desktop/STEMMIA Dexter/src/automacoes/` reutilizáveis
- Specs de dashboard: wireframe ASCII + métricas
- Pipelines: diagramas de sequência + schema de entrada/saída

## Critérios de qualidade
- Cada prompt versionado (`v0.1`, changelog embutido)
- Cada script tem: docstring, input, output, side-effects, idempotência
- Cada pipeline tem: schema de entrada (JSON/YAML), schema de saída, ponto de falha
- **Nenhuma execução real sem aprovação explícita do Dr. Jesus**

## Exemplos de artefatos
- `prompts/promote_memory_v0.1.md`
- `scripts/link_check.py` (spec, sem executar)
- `openclaw_jobs/weekly_quarterly_digest.yml`
- `telegram_flows/request_summary.md`
- `dashboard_specs/base_health_dashboard.md`
- `ingestion_pipelines/inbox_to_block.md`

## Interseções
- `15_memory` (memory promotion depende de prompts daqui)
- `16_inbox` (ingestion pipelines começam lá)
- `13_reports` (scripts geram relatórios)
- `08_ai_and_automation` (prompts técnicos estão nessa área também)
- `00_governance` (política de execução restrita)
