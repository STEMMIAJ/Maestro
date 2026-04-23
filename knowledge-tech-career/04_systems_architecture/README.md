---
titulo: Arquitetura de Sistemas
bloco: 04_systems_architecture
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 04 — Arquitetura de Sistemas

## Definição do domínio

Arquitetura é o conjunto de decisões caras de reverter: como partes de um sistema se separam, conversam, persistem estado e toleram falha. Este bloco cobre padrões (monolito, serviços, event-driven), bancos (relacional, documento, chave-valor, série temporal), filas e jobs, integrações entre sistemas, observabilidade e estratégias de escala e confiabilidade.

O objetivo é dar ao leitor a capacidade de ler um diagrama de arquitetura, identificar pontos de falha e discutir trade-offs (latência vs. consistência, custo vs. disponibilidade) sem jargão oco.

A prática do sistema pericial é laboratório natural: múltiplas fontes (DJEN, PJe, DataJud, Telegram, N8N), múltiplos bancos (SQLite, JSON, arquivos), múltiplos jobs (cron, launchd, hooks). Cada um desses é um caso de arquitetura real.

## Subdomínios

- `architecture_patterns/` — monolito, serviços, hexagonal, event-driven, CQRS, SAGA.
- `databases/` — SQL (Postgres, SQLite), NoSQL (Mongo, Redis), busca (Elastic), séries temporais.
- `queues_jobs_cron/` — filas (Redis, RabbitMQ, SQS), workers, cron, launchd, idempotência.
- `integrations/` — API REST, webhook, polling, contratos, retries, backoff.
- `observability/` — logs estruturados, métricas, traces, dashboards, alertas.
- `scaling_reliability/` — cache, replicação, failover, circuit breaker, SLO/SLI.

## Perguntas que este bloco responde

1. Quando quebrar um monolito em serviços compensa?
2. Qual banco escolher para qual formato de dado?
3. Por que fila é quase sempre melhor que chamada síncrona em job longo?
4. O que é idempotência e por que webhook precisa dela?
5. Como saber se um sistema está saudável sem abrir cada tela?
6. O que é backoff exponencial e por que rate limit exige ele?
7. Qual a diferença entre SLA, SLO e SLI?
8. Como planejar para falha parcial (um serviço caído não derruba tudo)?

## Como coletar conteúdo para este bloco

- Livros: "Designing Data-Intensive Applications" (Kleppmann), "Release It!" (Nygard), "Site Reliability Engineering" (Google).
- Documentação oficial dos bancos (Postgres, Redis, Elastic).
- Blogs de engenharia de empresas maduras (Netflix, Stripe, Shopify) com data registrada.
- Padrões do microservices.io.
- Casos internos: monitor de processos, orquestrador DJEN, pipeline de laudos.

## Critérios de qualidade das fontes

Seguir `00_governance/source_quality_rules.md`. Arquitetura tem muito conteúdo de moda; filtrar por evidência (post-mortem público, métrica publicada, livro revisado). Descartar tutorial que promete "arquitetura perfeita".

## Exemplos de artefatos que podem entrar

- Diagrama C4 (contexto, container, componente) do sistema pericial.
- Comparativo de bancos com critérios de escolha (tabela).
- Runbook de incidente para fila travada.
- Template de log estruturado JSON.
- Checklist de design review (segurança, observabilidade, custo, reversibilidade).
- Post-mortem de incidente real do monitor de processos.

## Interseções com outros blocos

- `01_ti_foundations` — redes e SO sustentam qualquer arquitetura.
- `02_programming` — design de software é a porta.
- `03_web_development` — APIs e deploy se encaixam aqui.
- `05_security_and_governance` — segurança é requisito arquitetural.
- `06_data_analytics` — pipelines de dados exigem arquitetura.
- `08_ai_and_automation` — agentes e RAG têm arquitetura própria.
- `14_automation` — jobs e workflows caem em queues_jobs_cron.
