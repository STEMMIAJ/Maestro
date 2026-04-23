---
titulo: Rate Limit e Idempotência
bloco: 03_web_development
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 5
---

# Rate Limit e Idempotência

Duas proteções que toda API de produção precisa. Rate limit controla VOLUME; idempotência controla REPETIÇÃO segura.

## Rate limiting

Limitar requests por chave (IP, usuário, token) num intervalo. Protege contra abuso, protege dependências (DB, APIs externas como DataJud).

### Algoritmos

**Token bucket** — balde com N tokens, recupera M tokens/s. Cada request consome 1. Permite rajada curta, mantém média. Mais usado.

**Leaky bucket** — balde vaza taxa constante. Requests entram na fila; se enche, dropa. Suaviza picos, mas não permite rajada.

**Fixed window** — contador zera a cada janela (ex: 100 req/min). Simples; problema: rajada no fim de uma janela + início da próxima = 200 reqs em 2s.

**Sliding window log** — registra timestamp de cada request, conta os últimos N segundos. Preciso, custoso em memória.

**Sliding window counter** — aproximação: ponderar janela atual + anterior. Bom balanço.

### Headers de resposta (padrão de facto)

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1745414400
Retry-After: 30
```

Se estourar: `429 Too Many Requests` + `Retry-After`.

Padrão IETF em evolução: `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` (sem `X-`).

### Implementação

- **Nginx** — `limit_req_zone` + `limit_req`.
- **Redis** — contador com TTL (`INCR` + `EXPIRE`). Biblioteca: `slowapi` (FastAPI), `express-rate-limit` (Node), `django-ratelimit`.
- **Cloudflare / API Gateway** — nível infra, sem tocar no código.
- **Envoy/Traefik** — sidecar.

Exemplo FastAPI com slowapi:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/processos")
@limiter.limit("30/minute")
def listar(request: Request): ...
```

### Para DataJud

DataJud tem rate limit próprio (120 req/min típicos, varia). Backoff exponencial obrigatório:

```
tentativa n → esperar (2^n + jitter) segundos, max 60s
```

Nunca martelar depois de 429 — incluir jitter (aleatório 0–1s) para não sincronizar muitos clientes.

## Idempotência

Operação idempotente = executar N vezes tem mesmo efeito de executar 1 vez. GET, PUT, DELETE são idempotentes por definição. POST geralmente não é.

### Por que importa

Cliente manda POST `/pagamentos`, rede cai antes da resposta. Cliente retenta → cobra duas vezes.

### Idempotency-Key (Stripe pattern)

Cliente gera UUID por operação, envia no header:

```
POST /pagamentos
Idempotency-Key: 3f29c1e4-7c2b-4a0f-9b1d-ec0f8b2a11c8
Content-Type: application/json

{"valor": 500}
```

Servidor:
1. Olha cache/DB se já viu essa chave.
2. Se sim → retorna resposta cacheada.
3. Se não → processa, salva resposta associada à chave (TTL 24–48h).

Retentativa retorna mesma resposta sem duplicar efeito.

### Implementar

- Redis: `SETNX idem:{key} in-progress` + TTL. Ao concluir, armazenar resposta.
- Tabela DB com UNIQUE constraint em `idempotency_key`.

### Casos comuns

- **Criar recurso** → Idempotency-Key.
- **Incrementar** (`POST /likes`) → evitar; usar PUT com valor absoluto quando possível.
- **Webhooks** — sempre tratar como potencialmente duplicados. Dedupe por `event_id`.

## Combinando

- Rate limit por IP + por token + por rota (ex: login mais estrito).
- Idempotency em toda operação financeira ou com efeito externo (enviar email, disparar worker).
- Backoff exponencial com jitter no cliente quando receber 429.

## Armadilhas

- Rate limit só por IP falha atrás de NAT corporativo. Adicionar limite por token.
- TTL curto demais na cache de idempotência perde retentativas genuínas.
- Não cachear a resposta original — retentativa processa de novo.
- 429 sem `Retry-After` força cliente a chutar. Sempre enviar.
