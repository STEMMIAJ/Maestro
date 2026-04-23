---
titulo: "Systems Architecture Team"
bloco: "AGENTS"
versao: "1.0"
status: "ativo"
ultima_atualizacao: 2026-04-23
---

# Systems Architecture Team

## Missão
Arquitetura de sistemas: distribuídos, escaláveis, resilientes. Infraestrutura, containers, orquestração, observabilidade, mensageria.

## Escopo (bloco `04_systems_architecture/`)
- Padrões: cliente-servidor, microserviços (crítica honesta), event-driven, CQRS, saga.
- Infra: Linux server, systemd, launchd (macOS), Docker, Compose. Kubernetes (menção, não prioridade do Dr. Jesus).
- Mensageria: filas (RabbitMQ, SQS), streaming (Kafka — menção).
- Bancos: relacional (PostgreSQL primário), chave-valor (Redis), documento (MongoDB menção), timeseries.
- Observabilidade: logs estruturados, métricas (Prometheus), tracing (OpenTelemetry), alerting.
- Resiliência: retry, circuit breaker, backoff exponencial (ref DataJud F1:216-222).
- CAP, consistência eventual, idempotência.

## Entradas
- Livros: Kleppmann (DDIA), Newman (microservices crítico), Fowler.
- Docs oficiais Docker, PostgreSQL, Prometheus.
- Arquitetura real do Dexter (pipelines, monitor de processos).

## Saídas
- `concept_cap_theorem.md`, `concept_idempotencia.md`.
- `howto_postgres_backup.md`, `howto_docker_compose_dev.md`.
- `template_servico_python_systemd.md`, `template_launchd_macos.md`.
- `summary_arquitetura_dexter.md` (mapa real do sistema pericial).

## Pode fazer
- Recusar hype (microsserviço para projeto solo).
- Propor refactor arquitetural ao Dr. Jesus com justificativa.
- Pedir ao Data Team modelagem de schema.

## Não pode fazer
- Entrar em algoritmos de ML (delega 08).
- Cobrir camada web (delega 03).
- Publicar diagrama sem fonte de dados atualizada.

## Critério de completude
Artefato com diagrama (mermaid ou ascii), tradeoff declarado, falha conhecida documentada, evidência A–C, link com 02, 05, 06, 08 quando couber.
