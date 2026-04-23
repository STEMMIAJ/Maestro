---
titulo: Padrões de Integração
bloco: 04_systems_architecture
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 6
---

# Padrões de Integração

Sistemas raramente vivem sós. Integrar com APIs externas, bancos de dados, filas, outros serviços é a realidade. Quatro padrões dominantes; usar o certo economiza arquitetura errada.

## 1. Webhook

Sistema A dispara HTTP para URL configurada em sistema B quando algo acontece. "**Servidor chama servidor**" em push.

```
GitHub → POST /webhook → seu servidor recebe evento "push"
Stripe → POST /webhook → recebe "payment_succeeded"
DJEN → POST /webhook → nova intimação (se suportasse)
```

Prós:
- **Tempo real** — evento viaja na hora.
- Barato — sem polling.
- Padrão universal.

Contras:
- Sistema B precisa endpoint público (ou tunnel: ngrok, Cloudflare Tunnel).
- Sem garantia de entrega padronizada. Fornecedores decentes retentam; muitos não.
- Autenticar remetente (HMAC, IP allowlist).
- Idempotência obrigatória (evento pode chegar 2x).

Boas práticas ao receber:
- Verificar assinatura HMAC.
- Responder 200 **rápido** (< 2s). Processamento pesado → enfileirar e voltar ao evento.
- Dedupe por `event_id`.

## 2. Polling

Sistema A consulta sistema B periodicamente. "**Cliente pergunta servidor**" em pull.

```
monitor.py: a cada 15 min:
  GET https://djen.cnj.jus.br/api/comunicacoes?desde=...
  comparar com último checkpoint
  disparar eventos para novidades
```

Prós:
- Sistema B não precisa saber de sistema A.
- Funciona com APIs que não oferecem webhook.
- Controle total de frequência.

Contras:
- Latência = intervalo de polling.
- Desperdício — 99% das vezes não tem nada novo.
- Rate limit de chamadas.

Variações:
- **Polling simples** — SELECT a cada N segundos.
- **Long polling** — servidor segura request até ter novidade (ou timeout). Menos chamadas; mais conexões abertas.
- **Delta polling** — usar `?since=timestamp` ou cursor para pegar só novidades.

Quando usar: API externa não tem webhook (DataJud, DJEN antigo). Integrações internas legacy.

## 3. Pub/Sub (event bus)

Sistema A publica em **tópico**; sistemas B, C, D consomem. Broker no meio (Redis Pub/Sub, SNS+SQS, Kafka, NATS).

```
produtor → publica "NovaMovimentacao" → broker → consumidores [dashboard, telegram, log]
```

Prós:
- Desacoplamento total (A não conhece B/C/D).
- Múltiplos consumidores sem alterar produtor.
- Escala horizontal.
- Registro/audit dos eventos.

Contras:
- Infra do broker.
- Consistência eventual.
- Debug distribuído exige observabilidade.
- Schema de evento precisa versionamento.

Detalhado em `event_driven_e_queues.md`.

## 4. Shared database

Múltiplos serviços leem/escrevem na mesma tabela.

Prós:
- Simples no começo.
- Transação ACID entre serviços.

Contras:
- **Acoplamento duro** — mudança de schema quebra todos os consumidores.
- Viola encapsulamento (regra de negócio do serviço A pode ser ignorada por serviço B escrevendo direto).
- Deploy sincronizado obrigatório.

Quando aceitável:
- Um sistema + ferramenta de relatório read-only.
- BI/ETL lendo réplica.

**Evitar** entre serviços que escrevem. Preferir API ou eventos.

## Outros padrões

### Request/Reply com broker

Produtor envia mensagem + `reply_to`. Consumidor processa e publica resposta no `reply_to`. Útil em RPC assíncrono (RabbitMQ RPC).

### CDC (Change Data Capture)

Ler WAL/binlog do DB e emitir eventos. Debezium lê Postgres WAL, publica no Kafka. "Observar" DB sem bater em toda tabela.

Uso: sincronizar ES/cache com Postgres em tempo real.

### API Gateway + BFF

Gateway (Kong, Traefik, AWS API Gateway) centraliza autenticação, rate limit, roteamento para microsserviços. BFF (Backend for Frontend) agrega chamadas para compor view.

### File-based (SFTP, batch)

Sistema A deixa CSV em SFTP; sistema B lê toda noite. Primitivo, mas indestrutível em ambiente corporativo. EDI bancário, órgãos públicos antigos.

### Message bus transacional (Outbox)

Salvar evento em tabela `outbox` dentro da mesma transação do DB. Worker separado lê outbox, publica no broker. Garante "salvou no DB ↔ publicou evento" atômico.

## Matriz de decisão

| Cenário | Padrão |
|---------|--------|
| Provedor suporta webhook (Stripe, GitHub) | **Webhook** |
| API externa só tem GET, sem webhook (DataJud) | **Polling com cursor** |
| Múltiplos serviços internos reagindo a 1 fato | **Pub/Sub** |
| Sincronizar DB → busca/cache | **CDC** |
| Integração batch noturna com órgão legacy | **SFTP + batch** |
| RPC com resposta assíncrona | **Request/Reply via fila** |
| Microsserviços com gateway | **API Gateway + BFF** |

## Resiliência

Toda integração externa é instável. Padrões defensivos:

- **Timeout** — sempre. Default baixo (5–30s). Nunca "infinito".
- **Retry com backoff** — exponencial + jitter.
- **Circuit breaker** — após N falhas em janela, parar de tentar por T segundos. Evita sobrecarga em fornecedor já caído.
- **Bulkhead** — isolar pool de conexões por integração. DataJud caindo não consome threads do PJe.
- **Fallback** — cache local antigo, valor default, degradação graciosa.
- **Rate limit próprio** — respeitar limite do fornecedor + margem.

Libs: `tenacity` (Python), `pybreaker`, `httpx-retries`.

## Para o sistema pericial

Integrações reais:

| Fonte | Padrão atual | Observações |
|-------|--------------|-------------|
| **DataJud (CNJ)** | Polling | Rate limit + backoff (F1:216-222) |
| **DJEN** | Polling | 3x/dia via launchd |
| **Comunica PJe** | Pendente (cadastro CNJ) | Quando ativo, será webhook |
| **PJe** (download peças) | Request/Reply via Selenium | Stateful, frágil |
| **Telegram bot** | Polling/webhook | @stemmiapericia_bot |
| **N8N workflows** | Webhook | srv19105 |
| **FTP stemmia.com.br** | Batch via script | Deploy de laudos/relatórios |

Com Comunica PJe ativado: **webhook + outbox** no sistema pericial, consumidores internos via Pub/Sub.

## Armadilhas

- Polling sem cursor — reconsulta tudo, desperdício + rate limit.
- Webhook sem verificar assinatura — qualquer um dispara.
- Sem timeout na chamada externa — 1 travada derruba serviço.
- Retry infinito em erro 4xx (fornecedor rejeita; retentar não muda). Retry só em 5xx e timeouts.
- Acoplar serviços via shared DB. Dor garantida em 1 ano.
