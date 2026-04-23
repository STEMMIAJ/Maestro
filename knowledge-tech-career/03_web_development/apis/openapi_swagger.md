---
titulo: OpenAPI / Swagger
bloco: 03_web_development
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: padrao-oai
tempo_leitura_min: 5
---

# OpenAPI / Swagger

OpenAPI Specification (OAS) = padrão para descrever APIs REST. Arquivo YAML/JSON legível por humano e máquina. Swagger = conjunto de ferramentas em volta do OpenAPI (UI, codegen, editor).

## Estrutura básica

```yaml
openapi: 3.1.0
info:
  title: Pericia API
  version: 0.1.0
servers:
  - url: https://api.stemmia.com.br
paths:
  /processos/{numero}:
    get:
      summary: Busca processo por número CNJ
      parameters:
        - name: numero
          in: path
          required: true
          schema:
            type: string
            pattern: '^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$'
      responses:
        '200':
          description: Processo encontrado
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Processo'
        '404':
          description: Não encontrado
components:
  schemas:
    Processo:
      type: object
      required: [numero, autor, reu]
      properties:
        numero: { type: string }
        autor:  { type: string }
        reu:    { type: string }
        vara:   { type: string }
```

## Dois fluxos de trabalho

**Design-first** — escrever OpenAPI primeiro, gerar servidor e cliente. Ideal quando múltiplos times consomem.

**Code-first** — código gera OpenAPI. FastAPI, NestJS, Spring Boot fazem automaticamente.

No FastAPI: declarar Pydantic + type hints → `/openapi.json` e `/docs` aparecem sozinhos. Código é a fonte da verdade.

## Gerar cliente

```bash
# gerar cliente TypeScript
npx openapi-typescript-codegen --input api.yaml --output ./src/api
```

Alternativas:
- `openapi-generator` — suporta 40+ linguagens.
- `openapi-fetch` — cliente TS tipado direto do schema, zero codegen.
- `orval` — TS + React Query/SWR hooks.

Benefício: refactor no backend (renomear campo, mudar tipo) quebra em compile-time no frontend.

## Documentar

- **Swagger UI** — interface interativa, "try it out". `/docs` no FastAPI.
- **ReDoc** — documentação estática, melhor para leitura. `/redoc` no FastAPI.
- **Stoplight Studio** — editor visual + mock server.
- **Scalar** — UI moderna, alternativa bonita ao Swagger UI.

## Validação e mock

- **Prism** (Stoplight) — mock server a partir do spec. Frontend desenvolve sem backend pronto.
- **Spectral** — linter. Aplica regras (ex: "toda rota deve ter descrição"). Integra em CI.
- **Dredd** — testa se implementação bate com spec.

## Padrões úteis

- **Versionamento** — `/v1/processos` vs header `Accept: application/vnd.api.v1+json`. Path é mais simples e visível.
- **Paginação** — `?page=1&per_page=50` ou cursor `?cursor=abc`. Retornar `total`, `next`, `prev` no envelope ou `Link` header.
- **Filtros** — `?vara=federal&status=ativo`.
- **Erros padronizados** — RFC 7807 (Problem Details): `{type, title, status, detail, instance}`.

## OpenAPI 3.1

- Compatível com JSON Schema 2020-12.
- Suporta tipos anuláveis (`type: [string, null]`).
- `webhooks` nativos.

FastAPI gera 3.1 desde 0.100. Django REST Framework precisa `drf-spectacular`.

## Para o sistema pericial

1. Escrever endpoints FastAPI com type hints.
2. `/docs` vira documentação viva.
3. Gerar cliente TS para o frontend SvelteKit/React.
4. `spectral lint` no CI para manter qualidade.
5. Versionar spec em git (`openapi.yaml` no repo) mesmo com code-first — serve como contrato.

## Armadilhas

- Documentar depois e esquecer. Code-first resolve: docs sempre sincronizadas.
- Spec grande demais sem `$ref` — duplicação de schemas. Reusar via `components/schemas`.
- Cliente gerado jogado no git vs regenerado no build. Decidir política (preferir regerar).
- Mistura de OpenAPI 2.0 (Swagger) e 3.x em ferramentas antigas. Padronizar em 3.1.
