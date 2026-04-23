---
titulo: Arquitetura Event-Driven e Filas
bloco: 04_systems_architecture
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 7
---

# Arquitetura Event-Driven e Filas

Event-driven = sistemas se comunicam por **eventos** (fato ocorrido) em vez de chamadas diretas. Desacopla produtor do consumidor.

## Conceitos-base

- **Evento** — fato imutável ("LaudoEntregue", "ProcessoDistribuido"). Passado, não imperativo.
- **Produtor** — quem emite.
- **Consumidor** — quem reage. Pode ser N.
- **Broker** — infraestrutura que transporta (Kafka, RabbitMQ, SQS, Redis Streams).
- **Tópico** / **fila** — canal.
- **Commit / ack** — consumidor confirma processamento.

## Queue vs Pub/Sub vs Log

**Queue (SQS, RabbitMQ, Redis RPUSH/LPOP)** — mensagem vai para UM consumidor (competing consumers). Ideal: jobs (redimensionar imagem, enviar email).

**Pub/Sub (Redis Pub/Sub, Google Pub/Sub, SNS)** — mensagem vai para TODOS consumidores ativos. Sem persistência (em Redis Pub/Sub clássico). Ideal: notificações efêmeras.

**Log (Kafka, Redis Streams, Kinesis)** — fluxo append-only, cada consumidor tem offset. Permite replay. Ideal: event sourcing, CDC, auditoria.

## Quando usar eventos

Indicado:
- Operação lenta que não precisa resposta imediata (gerar PDF, OCR de 200 páginas).
- Múltiplos reagentes ao mesmo fato (ao "LaudoEntregue": enviar email, atualizar dashboard, notificar Telegram, gravar log).
- Integração entre sistemas heterogêneos.
- Absorver pico (fila enfileira, worker processa conforme capacidade).
- Desacoplamento entre serviços (um muda, outro não se importa).

Não indicado:
- Operação que precisa resposta síncrona ao usuário ("ver detalhe do processo" não manda evento).
- Fluxo simples com 1 passo.
- Latência < 100ms obrigatória.
- Consistência forte ACID necessária.

## Opções de broker

### SQS (AWS)

Fila gerenciada. Fácil, pay-per-use. FIFO ou Standard. Visibility timeout + DLQ nativos.

Uso típico: Lambda puxa mensagens, processa.

### Redis Streams

Já tem Redis? Streams vem junto. Persistente, consumer groups, XADD/XREADGROUP. Mais simples que Kafka, menos escalável.

Ideal: aplicação pequena/média, um Redis só.

### Kafka

Log distribuído pesado. Partições, replicação, retenção configurável. Throughput gigante.

Ideal: alto volume (>10k msg/s), event sourcing, data pipeline.

Custo operacional alto — gerenciar cluster, Zookeeper (ou KRaft), partition rebalancing. Managed: Confluent Cloud, MSK, Redpanda.

### RabbitMQ

AMQP, routing complexo (exchanges, bindings), prioridades, TTL. Clássico enterprise. Throughput menor que Kafka.

### NATS

Leve, rápido, JetStream para persistência. Alternativa moderna pequena.

## Padrões

### Competing consumers

Vários workers consomem da mesma fila. Mensagem vai para 1. Paraleliza processamento.

### Fan-out

Produtor publica em tópico; múltiplas filas assinam. Cada consumidor tem sua fila (isolamento). SNS → SQS no AWS é o padrão.

### Dead Letter Queue (DLQ)

Mensagem que falha N vezes vai para DLQ. Operador investiga. **Obrigatório em produção**.

### Outbox pattern

Garantir que evento seja publicado atomicamente com mudança no DB:
1. Transação: salvar entidade + inserir em tabela `outbox`.
2. Worker lê `outbox` e publica no broker.
3. Marca como publicado.

Resolve "salvei no DB mas broker caiu".

### Saga

Transação distribuída via eventos compensatórios. "ReservarVoo" → "ReservarHotel" → se falhar → "CancelarVoo".

### Event sourcing

Estado reconstruído a partir dos eventos. Mais complexo; use só se auditoria/replay for requisito forte.

## Entrega e garantias

- **At most once** — pode perder. Raro aceitar.
- **At least once** — padrão. Consumidor precisa ser **idempotente** (processar 2x = efeito de 1x).
- **Exactly once** — difícil. Kafka tem "exactly once semantics" sob condições (transações + idempotent producer).

Consumidor idempotente: registrar `event_id` processado, ignorar repetidos. Ou usar operação naturalmente idempotente (UPSERT).

## Retry e backoff

Processou falhou → retentar com **backoff exponencial + jitter**. Max N tentativas → DLQ.

```
tentativa 1: imediato
tentativa 2: 2s + rand(0,1)
tentativa 3: 4s + rand(0,2)
tentativa 4: 8s + rand(0,4)
→ DLQ
```

## Para o sistema pericial

**Cenários naturais para fila**:

1. **Download de PJe** — usuário clica "baixar processo 123". Enfileira; worker baixa. UI mostra "em processamento", atualiza quando pronto.
2. **OCR de laudo** — pesado. Enfileirar, worker isolado processa.
3. **Monitor de publicações DJEN** — fonte consulta API, publica evento "NovaMovimentacao". Consumidores: dashboard, Telegram, banco.
4. **Envio em lote de emails/ofícios** — enfileirar 50, worker envia respeitando rate limit.

**Stack sugerida**: **Redis Streams** (um Redis para cache + fila), **RQ** ou **Dramatiq** (Python workers simples). Evitar Kafka (overkill) e RabbitMQ (operação).

**Outbox**: tabela `eventos_outbox` no mesmo SQLite/Postgres; processo `publicador.py` no launchd lê e publica.

## Armadilhas

- Consumidor sem idempotência + retry = duplicar efeito.
- Sem DLQ = mensagem infinita em loop, bloqueia fila.
- Mensagens grandes (> 256 KB) = mandar referência (S3 URL) em vez do payload.
- Evento com schema livre → clientes quebram em mudança. Versionar schema (Avro, Protobuf, JSON Schema).
- "Event-driven para tudo" = debug impossível, latência imprevisível. Usar onde faz sentido.
