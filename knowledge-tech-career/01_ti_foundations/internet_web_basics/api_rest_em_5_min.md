---
titulo: "API REST em 5 minutos"
bloco: "01_ti_foundations/internet_web_basics"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 6
---

# API REST em 5 minutos

## O que é API

*Application Programming Interface*. Contrato pelo qual um software expõe funcionalidades para outro software consumir. API web = endpoints HTTP que retornam dados (geralmente JSON).

Exemplo: API do DataJud. Seu script envia `POST /api_publica_tjmg/_search` com filtros, recebe JSON com processos.

## REST

*Representational State Transfer*. Estilo arquitetural (não protocolo) para projetar APIs web com algumas convenções:

1. **Recursos identificados por URL** — `/processos/123`, `/laudos/456`.
2. **Verbos HTTP** mapeiam operações.
3. **Stateless** — cada requisição contém tudo que precisa; servidor não guarda sessão entre chamadas.
4. **Representação em JSON** (ou XML).

Nem toda API chamada de "REST" segue 100% — mais comum é "RESTish".

## Verbos principais

- **GET** — lê recurso. Não altera estado. `GET /processos/123` devolve dados do processo 123.
- **POST** — cria recurso. `POST /laudos` com JSON no corpo cria um laudo novo. Servidor devolve o recurso criado, geralmente com `id`.
- **PUT** — substitui recurso inteiro. `PUT /laudos/456` com JSON completo sobrescreve o laudo 456.
- **PATCH** — altera parcialmente. `PATCH /laudos/456` com `{"status":"assinado"}` muda só o status.
- **DELETE** — remove. `DELETE /laudos/456` apaga.

Convenção: GET é seguro (não altera nada) e idempotente (repetir = mesmo resultado). PUT e DELETE são idempotentes mas não seguros. POST não é idempotente.

## JSON no corpo

Formato de serialização textual leve. Tipos: string, number, boolean, null, array, object.

```json
{
  "numero_processo": "0001234-56.2026.8.13.0024",
  "partes": ["Autor X", "Réu Y"],
  "valor_causa": 50000.00,
  "prazo_dias": 30
}
```

Cabeçalho `Content-Type: application/json` avisa ao servidor como parsear.

## Status codes

Número de 3 dígitos que resume o resultado:

- **2xx — Sucesso**
  - `200 OK` — padrão para GET bem-sucedido.
  - `201 Created` — POST criou recurso; resposta deve ter `Location` apontando para a nova URL.
  - `204 No Content` — sucesso sem corpo (típico de DELETE).
- **3xx — Redirecionamento**
  - `301 Moved Permanently`, `302 Found`.
- **4xx — Erro do cliente**
  - `400 Bad Request` — JSON malformado, parâmetro inválido.
  - `401 Unauthorized` — falta autenticação.
  - `403 Forbidden` — autenticado mas sem permissão.
  - `404 Not Found` — recurso inexistente.
  - `429 Too Many Requests` — rate limit.
- **5xx — Erro do servidor**
  - `500 Internal Server Error` — exceção não tratada.
  - `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout`.

Regra de ouro: **4xx = você errou, 5xx = eles erraram**.

## Autenticação

Formas comuns:
- **API key** no header (`X-API-Key: abc123`).
- **Bearer token** (OAuth/JWT): `Authorization: Bearer eyJ...`.
- **Basic auth**: `Authorization: Basic <base64(usuario:senha)>` — só com HTTPS.

DataJud usa API key; Gmail usa OAuth.

## Exemplo completo (DataJud)

```
POST https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search
Headers:
  Authorization: APIKey cDZHYzlZa0JadVREZDJCendQbXY6...
  Content-Type: application/json
Body:
  {"query": {"match": {"numeroProcesso": "00012345620268130024"}}}

Resposta:
  200 OK
  {"hits": {"total": {"value": 1}, "hits": [...]}}
```

## Por que importa para o perito

- **Monitor de processos** consome DataJud, DJEN e Comunica PJe via API REST. Entender status codes evita "martelar" API durante rate limit (429 exige backoff exponencial).
- **Integração N8N ↔ Claude** é API REST (webhook recebe POST, retorna JSON).
- **Análise de fraude em e-commerce** examina chamadas REST entre front e back — autenticação fraca (API key no JS do cliente) é vulnerabilidade óbvia.

## Referências

- Fielding, R. — *Architectural Styles and the Design of Network-based Software Architectures*, 2000.
- RFC 9110 (HTTP Semantics), RFC 8259 (JSON).
