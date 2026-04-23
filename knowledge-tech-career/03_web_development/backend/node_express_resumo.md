---
titulo: Node.js + Express — Resumo
bloco: 03_web_development
tipo: referencia
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 4
---

# Node.js + Express — Resumo

Node.js = runtime JavaScript server-side (V8 do Chrome fora do browser). Express = framework web minimalista, padrão histórico no ecossistema.

## Stack mínima

```bash
npm init -y
npm install express
```

```js
// server.js
import express from "express";
const app = express();
app.use(express.json());

app.get("/processos", (req, res) => {
  res.json([{ numero: "1001234-56.2025" }]);
});

app.post("/processos", (req, res) => {
  // req.body já parseado
  res.status(201).json({ ok: true });
});

app.listen(3000, () => console.log("rodando em :3000"));
```

Executar: `node server.js` ou `node --watch server.js`.

## Conceitos

- **Middleware** — função `(req, res, next) => {}` na cadeia. `app.use(fn)` aplica global. Ordem importa.
- **Router** — `express.Router()` para modularizar rotas por domínio.
- **Body parsing** — `express.json()`, `express.urlencoded()`.
- **Error handling** — middleware com 4 args `(err, req, res, next)` ao final.

## Alternativas modernas no ecossistema Node

| Framework | Destaque |
|-----------|----------|
| **Express** | Padrão de fato, minimalista, manutenção em modo estável |
| **Fastify** | ~2x mais rápido, schema JSON nativo, plugins |
| **Hono** | Leve, edge-first (Cloudflare Workers, Deno, Bun) |
| **NestJS** | Opinativo, tipo Angular, DI, decorators, TypeScript-first |
| **Koa** | Sucessor espiritual do Express pelo mesmo autor, async/await nativo |

Projeto novo em 2026: Hono (edge) ou Fastify (Node puro). Express ainda domina por legado e documentação.

## Quando escolher Node

- Time JS/TS já existente (frontend React/Vue).
- Workloads I/O-bound (proxy, gateway, websocket, SSE).
- Integração com ecossistema npm (LLMs, Puppeteer, scraping).
- Serverless edge (Cloudflare Workers, Vercel, Deno Deploy).

Quando não:
- CPU-pesado (processar PDF, imagem). Usar Python, Go, Rust.
- Equipe Python madura e backend modesto. FastAPI entrega igual, tipado.

## Para o contexto do Dr. Jesus

Sistema pericial é Python-first (DataJud, perícia, Streamlit). Node entra se: (1) frontend crescer e precisar de SSR Next.js, (2) automação com Playwright/Puppeteer para PJe (há alternativa Python também), (3) webhook rápido em Cloudflare Worker.

Não migrar backend Python existente para Node sem motivo concreto.

## Mínimo viável

- Usar TypeScript desde o primeiro arquivo (`tsx` ou Bun rodam TS direto).
- Gerenciador: pnpm ou bun. npm clássico é lento.
- Testar com Node Test Runner nativo (`node --test`) ou Vitest.
- Deploy: Docker, PM2 em VPS, Cloud Run, Fly.io.
