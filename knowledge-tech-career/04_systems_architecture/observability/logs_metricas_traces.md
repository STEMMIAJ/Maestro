---
titulo: Logs, Métricas e Traces
bloco: 04_systems_architecture
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 7
---

# Logs, Métricas e Traces

Três pilares da observabilidade. Responsabilidades diferentes; juntos, permitem entender o que aconteceu em produção.

## Logs — o que aconteceu

Eventos discretos, textuais, pesados em detalhe.

Exemplo (estruturado):

```json
{"ts":"2026-04-23T10:00:00Z","level":"ERROR","svc":"pericia-api",
 "req_id":"abc123","user":"456","event":"datajud_fail",
 "numero":"1001234-56.2025","error":"timeout","duration_ms":30012}
```

**Estruturar logs** (JSON) — chave/valor legível por máquina. Nada de `print("erro")`.

Ferramentas:
- **Python** — `logging` com `python-json-logger`, **structlog** (melhor).
- **Node** — `pino`, `winston`.
- **Go** — `slog` (stdlib) ou `zap`.

Centralização:
- **Grafana Loki** — barato, label-based (bom em k8s).
- **Elasticsearch + Kibana (ELK)** — clássico, pesado.
- **Datadog, New Relic, Sentry (eventos), BetterStack** — SaaS.
- **CloudWatch Logs, GCP Logging** — cloud nativo.

Níveis: DEBUG < INFO < WARN < ERROR < CRITICAL. Produção: INFO+ default.

Regras:
- **Nunca** logar PII/segredo (senha, token, CPF completo). Mascarar.
- Correlation ID por request (propagar `X-Request-ID` / W3C `traceparent`).
- Retenção adequada (30–90 dias típico). Logs antigos vão para storage frio.

## Métricas — quanto / quão rápido

Agregados numéricos ao longo do tempo. Baratas para guardar anos.

Tipos:
- **Counter** — só cresce (requests totais, erros totais).
- **Gauge** — sobe/desce (memória usada, fila pendente).
- **Histogram/Summary** — distribuição (latência p50/p95/p99).

Exemplo Prometheus:

```
http_requests_total{method="GET",status="200",route="/processos"} 1842
http_request_duration_seconds_bucket{le="0.1"} 1700
http_request_duration_seconds_bucket{le="0.5"} 1820
fila_datajud_pendentes 42
```

Ferramentas:
- **Prometheus** — padrão open-source. Pull-based. PromQL para queries.
- **VictoriaMetrics** — compatível Prometheus, mais eficiente em escala.
- **Grafana** — visualização (dashboards).
- **Datadog, New Relic** — SaaS.
- **StatsD** (legado) — push-based.

### Os 4 sinais dourados (Google SRE)

1. **Latência** — tempo de resposta.
2. **Tráfego** — volume (req/s).
3. **Erros** — taxa de falha.
4. **Saturação** — uso de recurso (CPU, memória, fila).

Dashboard mínimo de qualquer serviço cobre esses 4.

## Traces — por onde passou

Um request atravessa múltiplos serviços. Trace = sequência completa; spans = passos individuais.

```
trace: abc123 (total 420ms)
  span: api-gateway (10ms)
  span: pericia-api /processos (380ms)
    span: postgres SELECT (250ms)        ← gargalo
    span: datajud GET (100ms)
  span: api-gateway response (30ms)
```

Propaga via header `traceparent` (W3C Trace Context).

Ferramentas:
- **Jaeger** — open-source, padrão clássico.
- **Tempo (Grafana)** — moderno, barato.
- **Zipkin** — clássico.
- **Datadog APM, New Relic, Honeycomb** — SaaS.
- **Sentry Performance** — combina erros + traces.

## OpenTelemetry (OTel)

**Padrão aberto unificado** para gerar logs+métricas+traces. Instrumentar uma vez, exportar para qualquer backend.

SDKs:
- Python: `opentelemetry-sdk`, auto-instrumentation para FastAPI/httpx/psycopg2.
- Node, Go, Java, .NET, Ruby — todos cobertos.

Arquitetura:

```
app  ──(OTLP)──▶  OTel Collector  ──▶  [Prometheus, Loki, Tempo, Datadog, ...]
```

Collector centraliza, transforma, roteia. Trocar de vendor = reconfigurar collector, não o app.

## Eventos de erro — Sentry

Subcategoria de logs, focada em exceções com contexto:
- Stack trace completa.
- Variáveis locais no momento do erro.
- Breadcrumbs (ações anteriores).
- Agrupamento automático de erros similares.
- Alertas configuráveis.

SDK trivial em quase qualquer linguagem. Padrão para frontend + backend de produção.

## Dashboards

Grafana é padrão. Dashboards por:
- Serviço (latência, erros, throughput).
- Negócio (laudos/dia, processos por vara, tempo médio de resposta).
- Infra (CPU, memória, disco).
- SLO (Service Level Objective) — gráfico de "orçamento de erro" restante.

## SLI/SLO/SLA

- **SLI** (Indicator) — medida real ("99.87% das requests < 500ms").
- **SLO** (Objective) — alvo ("99.9% < 500ms").
- **SLA** (Agreement) — contrato com cliente + penalidade.

Error budget = (1 - SLO). Se 99.9% é meta, 0.1% de erro é "permitido". Consumiu o budget = pausar features, focar em estabilidade.

## Para o sistema pericial

Stack leve possível:
- **Logs** — structlog em JSON para arquivo + rotação (`logrotate`); ou Loki se rodar dashboards Grafana.
- **Métricas** — Prometheus scraping FastAPI (`prometheus-fastapi-instrumentator`).
- **Traces** — OpenTelemetry + Tempo ou Jaeger local; ou só Sentry Performance (mais simples).
- **Erros** — Sentry free tier.

Cron/launchd jobs: cada um faz `curl` em **Healthchecks.io** ao fim. Alerta no Telegram se falhar.

Dashboard único em Grafana na VPS srv19105:
- Latência média do FastAPI.
- Taxa de erro DataJud/PJe.
- Fila de jobs pendentes.
- Processos monitorados / novos do dia.
- Espaço em disco do banco.

## Armadilhas

- Logar INFO de tudo em prod — volume explode, custo sobe, sinal afoga em ruído.
- Métrica por usuário (cardinalidade alta) — Prometheus trava. Usar labels controlados.
- Dashboard sem alerta = decoração. Alertas baseados em SLO.
- Alerta barulhento — zera trust. Ajustar thresholds, agrupar.
- Sem retenção planejada — disco enche em silêncio.
- PII nos logs — LGPD te pega.
