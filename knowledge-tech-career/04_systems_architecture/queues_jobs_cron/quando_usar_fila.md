---
titulo: Quando Usar Fila
bloco: 04_systems_architecture
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 6
---

# Quando Usar Fila

Fila = buffer entre produtor (quem cria trabalho) e consumidor (quem executa). Não é sempre necessária; quando é, resolve problemas caros de outro jeito.

## 4 motivos legítimos

1. **Tarefa lenta que não precisa resposta imediata ao usuário.**
   Usuário clica "gerar PDF de laudo". Gerar leva 30s. Request HTTP timeout. Solução: enfileirar; responder "em processamento"; worker gera; notificar ao terminar.

2. **Picos irregulares que sobrecarregariam downstream.**
   100 clientes pedem ao mesmo tempo → fila absorve → worker processa 10/s → DataJud não recebe 100 requests simultâneos (que violariam rate limit).

3. **Múltiplos consumidores do mesmo evento.**
   "LaudoEntregue" → email + Telegram + dashboard + log auditoria. Sem fila: serviço produtor conhece todos os consumidores (acoplamento). Com fila pub/sub: produtor publica, consumidores assinam.

4. **Retry e resiliência.**
   API externa (PJe) instável. Sem fila: usuário vê erro; retenta manualmente. Com fila: worker retenta automaticamente com backoff, DLQ se desistir.

## Quando NÃO usar

- Operação rápida (< 200ms) com resposta síncrona ao usuário.
- Um único consumidor, fluxo simples.
- Consistência forte obrigatória (fila introduz eventual consistency).
- Time não tem capacidade de operar fila (monitorar, DLQ, reprocessar).

Adicionar fila "por garantia" aumenta complexidade sem ganho. Mede primeiro.

## Idempotência — obrigatória

Fila entrega **at-least-once** na prática. Mesma mensagem pode chegar 2x (worker crasha após processar, antes de commitar ack). Consumidor precisa ser idempotente.

Estratégias:
- **Operação naturalmente idempotente** — UPSERT, `SET status='enviado'`.
- **Dedupe por event_id** — registrar `event_id` processado; ignorar repetido.
- **Hash de payload** — usar como chave natural.

```python
def processar(evento):
    if ja_processado(evento.id):
        return
    with transacao:
        fazer_trabalho(evento)
        marcar_processado(evento.id)
```

## Retry e DLQ

Padrão: backoff exponencial com jitter, máx N tentativas, falhou = Dead Letter Queue.

```
tentativa 1 → processa → falha
aguarda 2s + jitter
tentativa 2 → processa → falha
aguarda 4s + jitter
...
tentativa 6 → DLQ
```

DLQ = fila separada para mensagens "impossíveis de processar". Operador investiga: bug no worker? Dados corrompidos? Depois reprocessa ou descarta.

**Sem DLQ** mensagem fica em loop infinito, travando recursos.

## Visibility timeout

SQS/Redis: mensagem "invisível" por N segundos após consumir. Se worker não ack, volta à fila. Escolher N > tempo máximo de processamento normal + margem.

Timeout muito curto = mesma mensagem processada 2x em paralelo.
Timeout muito longo = falha do worker atrasa retry.

## Ordenação vs paralelismo

- **FIFO estrita** — 1 consumidor, ordem preservada. Lento.
- **Parcial** (por chave) — SQS FIFO com `MessageGroupId`, Kafka por partition. Mensagens da mesma chave em ordem; grupos diferentes em paralelo.
- **Sem ordem** — paralelismo máximo. Escolher se possível.

Usar ordem estrita só quando realmente necessário.

## Payload — tamanho

Limite típico 256 KB (SQS) ou MBs (Kafka). Para arquivos grandes: **claim-check pattern**:

```
produtor:
  upload S3 → obtém URL
  publica evento com URL

consumidor:
  recebe evento
  baixa de S3
```

Mantém mensagem pequena, rápida, barata.

## Schema de evento

Evento precisa ser interpretável anos depois. Padronizar:

```json
{
  "id": "uuid",
  "type": "LaudoEntregue",
  "version": 1,
  "occurred_at": "2026-04-23T10:00:00Z",
  "source": "pericia-api",
  "data": { "laudo_id": "...", "processo_numero": "..." }
}
```

Versionar (`version: 1`). Quando adicionar campo, `version: 2`; manter retrocompatibilidade.

## Observabilidade

Métricas essenciais:
- **Profundidade da fila** (mensagens esperando).
- **Idade da mensagem mais velha** (lag).
- **Taxa de processamento**.
- **Taxa de erro**.
- **Mensagens em DLQ**.

Alertar quando: lag > X, DLQ não vazia, worker parado.

## Para o sistema pericial

**Casos concretos**:

1. **Download PJe** — enfileira pedido; worker baixa (Selenium). DLQ se PJe fora do ar. Idempotente por `numero_processo`.
2. **OCR de laudo grande** — enfileira; worker processa com Tesseract/LayoutParser. Idempotente por hash do PDF.
3. **Consulta DataJud em lote** — 50 processos para atualizar. Enfileirar; workers respeitam rate limit. Idempotente via UPSERT na tabela.
4. **Notificação Telegram** — enfileirar mensagem; worker envia respeitando rate limit Telegram.

**Stack**:
- Redis + **RQ** (Redis Queue) ou **Dramatiq** — Python, simples.
- Workers via launchd (`python -m rq worker default`).
- Dashboard **RQ Dashboard** para ver fila e DLQ.

## Armadilhas

- Fila sem monitor — lotou, travou, não percebeu.
- Worker sem idempotência — evento duplicado causa lado-efeito duplicado.
- Timeout do HTTP request do usuário esperando resultado da fila (trava UI). Usar websocket/SSE/polling.
- Mensagem gigante. Claim-check.
- Esquecer de testar DLQ. Dia que acontecer, operador não sabe reprocessar.
