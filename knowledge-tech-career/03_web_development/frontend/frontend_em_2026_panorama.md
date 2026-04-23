---
titulo: Frontend em 2026 — Panorama
bloco: 03_web_development
tipo: panorama
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 7
---

# Frontend em 2026 — Panorama

Frontend moderno gira em torno de 3 eixos: **framework**, **estratégia de renderização**, **ferramenta de build**.

## Os 4 frameworks dominantes

| Framework | Modelo | Curva | Ecossistema | Uso típico |
|-----------|--------|-------|-------------|-----------|
| React | Virtual DOM + JSX | Média | Gigante | Apps corporativos, React Native |
| Vue 3 | Reatividade + templates | Baixa | Grande | Apps internos, prototipagem |
| Svelte 5 | Compilador, sem VDOM | Baixa | Crescendo | Apps pequenos/médios, SSR |
| Solid | JSX + sinais (fine-grained) | Média | Pequeno | Performance crítica |

React continua padrão de mercado (60%+ das vagas). Svelte cresce em projetos novos pela simplicidade. Solid é React feito certo para quem já sabe React.

## Estratégias de renderização

**SPA (Single Page App)** — tudo no browser. JS baixa a casca, renderiza conteúdo via API. Rápido após o load inicial, ruim para SEO e primeiro carregamento. Ex: dashboard interno.

**SSR (Server-Side Rendering)** — servidor gera HTML em cada request. Bom para SEO e primeiro byte rápido. Custo de servidor maior. Ex: Next.js, Nuxt, SvelteKit.

**SSG (Static Site Generation)** — build gera HTML estático de tudo. Hospedagem em CDN (barato). Não serve conteúdo dinâmico. Ex: blog, landing page, docs.

**ISR/PPR (híbridos)** — parte estática, parte dinâmica. Next.js 15+ com Partial Prerendering mistura tudo.

**RSC (React Server Components)** — componentes rodam no servidor, zero JS no cliente. Reduz bundle. Ainda em maturação.

## Matriz de decisão (2026)

| Projeto | Escolha |
|---------|---------|
| Landing page de 5 páginas | Astro (SSG) |
| Blog de conteúdo | Astro ou Hugo |
| Dashboard interno autenticado | React SPA ou SvelteKit SPA |
| App público com SEO | Next.js (SSR/PPR) ou SvelteKit |
| Sistema interno simples | Streamlit / Django templates |
| App offline-first | Svelte + PWA |
| Prototipagem rápida | Vue 3 |

## Build tools

- **Vite** — padrão de fato. Dev server instantâneo (ESM nativo), build via Rollup. Suporta React/Vue/Svelte.
- **Turbopack** — sucessor do Webpack feito pela Vercel para Next.js. Ainda amadurecendo.
- **Bun** — runtime + bundler. Muito rápido, ecossistema crescendo.
- **esbuild** — bundler em Go, usado por Vite internamente.

Webpack/Create React App = legado. Novo projeto = Vite.

## Gerenciamento de estado

- Local de componente — `useState` (React), `ref` (Vue), `$state` (Svelte 5).
- Global pequeno — Context API, Pinia, Svelte stores.
- Global complexo — Zustand, Jotai, Redux Toolkit. Redux tradicional caiu em desuso.
- Estado de servidor — TanStack Query, SWR. Cache + revalidação. Muitos projetos dispensam estado global porque TanStack Query resolve.

## Estilização

- CSS puro com tokens — suficiente para 70% dos casos.
- Tailwind CSS — utilitário, produtividade alta.
- CSS Modules — escopo automático, sem runtime.
- styled-components / Emotion — CSS-in-JS, caiu em popularidade (custo runtime).
- vanilla-extract — CSS-in-TS, zero runtime.

## Para dashboard pericial do Dr. Jesus

Recomendação: **SvelteKit SPA com TypeScript + Tailwind + TanStack Query**. Bundle pequeno, reatividade sem boilerplate, deploy estático em FTP se necessário. Alternativa ainda mais simples: **Streamlit** em Python se o foco é ingerir dados do DataJud/SQLite e mostrar tabelas/gráficos sem UI personalizada.

## Tendências 2026

- Local-first (CRDT, Replicache) — app funciona offline, sincroniza depois.
- Edge computing — código roda perto do usuário (Cloudflare Workers, Vercel Edge).
- Zero-JS por padrão (Astro, Qwik resumability).
- AI-generated UI — v0, Bolt geram componentes prontos.
