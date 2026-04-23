---
titulo: REST vs GraphQL vs RPC
bloco: 03_web_development
tipo: comparacao
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 7
---

# REST vs GraphQL vs RPC

Três estilos de API. Escolha depende de: forma dos dados, quem consome, maturidade do time, latência.

## REST (Representational State Transfer)

Recursos com URL, verbos HTTP, representações JSON.

```
GET    /processos            → lista
GET    /processos/123        → detalhe
POST   /processos            → criar
PUT    /processos/123        → substituir
PATCH  /processos/123        → atualizar parcial
DELETE /processos/123        → remover
```

Prós:
- Cacheável por HTTP (ETag, Cache-Control, CDN).
- Ferramental universal (curl, Postman, browser).
- Simples para CRUD clássico.
- OpenAPI gera docs e clientes.

Contras:
- Over-fetching (recebe dados desnecessários).
- Under-fetching (precisa de N chamadas para montar view).
- Versionamento tende a proliferar endpoints (`/v1`, `/v2`).

## GraphQL

Cliente declara exatamente o que precisa em uma única query.

```graphql
query {
  processo(numero: "1001234-56.2025") {
    autor
    vara
    movimentacoes(ultimas: 5) {
      data
      descricao
    }
  }
}
```

Prós:
- Zero over/under-fetching.
- Um endpoint (`/graphql`), schema forte, introspection.
- Cliente mobile economiza banda.
- Composição de dados de múltiplas fontes (federação, Apollo).

Contras:
- Cache HTTP não funciona bem (tudo POST). Precisa cache client-side (Apollo, Relay, urql).
- Complexidade no servidor (resolvers, N+1, DataLoader).
- Rate limiting + query cost difíceis.
- Observabilidade mais difícil (requests parecem iguais).
- Segurança: query maliciosa pode derrubar servidor (depth limit, cost analysis).

## RPC (Remote Procedure Call)

Chamar função no servidor como se fosse local. Estilos:

- **JSON-RPC** — `POST /rpc {"method": "buscarProcesso", "params": {...}}`.
- **gRPC** — binário (Protobuf) sobre HTTP/2, streaming bidirecional. Ecossistema Google.
- **tRPC** — TypeScript end-to-end, tipos compartilhados cliente/servidor sem codegen.

Prós:
- Chamadas diretas, sem ginástica de "qual verbo".
- gRPC: binário compacto, streaming, multiplexing HTTP/2.
- tRPC: produtividade TS absurda, refactor seguro.

Contras:
- Menos amigável para browser (gRPC-Web precisa de proxy).
- Cache HTTP não se aplica.
- Acoplamento cliente-servidor (em tRPC é uma feature; em gRPC exige schema compartilhado).

## Matriz de decisão

| Caso | Escolha |
|------|---------|
| API pública (terceiros consomem) | **REST** (ou GraphQL se grafo rico) |
| CRUD clássico interno | **REST** |
| Microserviços backend-to-backend | **gRPC** |
| App mobile com rede instável | **GraphQL** (query única) |
| Monorepo TS full-stack | **tRPC** |
| Dashboard com múltiplas entidades relacionadas | **GraphQL** |
| Integração com webhooks, CDN, cache | **REST** |
| Streaming bidirecional (chat, telemetria) | **gRPC** ou WebSocket |

## Híbridos e evolução

- **GraphQL Federation** — múltiplos serviços GraphQL compondo um schema (Apollo Federation).
- **REST + JSON:API** — spec padroniza relacionamentos, reduz over/under-fetching.
- **HATEOAS** — REST "puro" com links; pouco usado na prática.
- **Connect RPC** — gRPC que funciona bem com HTTP/1 e browser.

## Custo operacional

- REST tem menor custo de operação (cache HTTP, debugging fácil, ferramentas maduras).
- GraphQL exige time que entenda resolvers, cache client, proteção contra queries pesadas.
- gRPC exige pipeline de geração de stub (Protobuf) e infraestrutura HTTP/2.

## Para o sistema pericial

- **API interna dashboard ↔ backend** → REST simples. 20 endpoints cobrem tudo.
- **Se expandir para app mobile do Dr. Jesus** → GraphQL talvez valha (buscar processo + movimentações + documentos em 1 request).
- **Não justificado hoje** → gRPC (zero ganho num sistema mono-servidor).

Armadilha comum: adotar GraphQL pela modinha e pagar complexidade sem ganho. REST bem feito com OpenAPI resolve 90% dos casos.
