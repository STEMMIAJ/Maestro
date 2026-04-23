---
titulo: Performance Web — Básico
bloco: 03_web_development
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: padrao-w3c
tempo_leitura_min: 7
---

# Performance Web — Básico

Performance web importa para UX, SEO e conversão. Google mede três métricas (Core Web Vitals) que influenciam ranking.

## Core Web Vitals (2026)

### LCP (Largest Contentful Paint)

Tempo até o MAIOR elemento visível aparecer. Normalmente imagem hero, banner, título.

- **Bom**: ≤ 2.5 s
- **Ruim**: > 4 s

Causas típicas de LCP ruim:
- Imagem hero sem `preload`.
- CSS ou JS bloqueando render.
- Servidor lento (TTFB alto).
- Fonte web bloqueando texto.

Soluções:
- `<link rel="preload" as="image" href="/hero.webp">`.
- `fetchpriority="high"` na tag `<img>`.
- Inline CSS crítico, lazy do resto.
- CDN perto do usuário.

### INP (Interaction to Next Paint)

Substituiu FID (First Input Delay) em março/2024. Mede **resposta a interação** (clique, tap, tecla). Observa todas as interações da sessão, pega a pior.

- **Bom**: ≤ 200 ms
- **Ruim**: > 500 ms

Causas:
- JS pesado na thread principal.
- Handlers caros (re-render grande).
- Event loop bloqueado (sincronização forçada).

Soluções:
- `requestIdleCallback` / `scheduler.postTask`.
- Quebrar trabalho longo em chunks (`yield to main thread`).
- Debounce/throttle em eventos frequentes.
- Workers (Web Worker) para CPU-pesado.

### CLS (Cumulative Layout Shift)

Soma de deslocamentos visuais inesperados (elemento pula enquanto você lê/clica).

- **Bom**: ≤ 0.1
- **Ruim**: > 0.25

Causas:
- `<img>` sem `width`/`height` (reserva espaço só quando carrega).
- Anúncio/iframe inserido dinamicamente.
- Fonte web trocando tamanho no load (FOUT/FOIT).

Soluções:
- `<img width height>` sempre. Browser calcula aspect-ratio.
- `aspect-ratio: 16/9` em CSS para containers de mídia.
- `font-display: optional` ou `swap` + `size-adjust` para matching da fonte fallback.

## Técnicas transversais

### Lazy loading

```html
<img src="/imagem.webp" loading="lazy" width="800" height="600" alt="...">
<iframe src="..." loading="lazy"></iframe>
```

Navegador carrega só quando próximo da viewport. Não usar em imagens acima da dobra (vai atrasar LCP).

### Code splitting

Quebra JS em chunks que carregam sob demanda. Vite/Next fazem por rota automaticamente. Manual:

```js
const Dashboard = await import("./dashboard.js");
```

Usuário que só vê home não baixa código do dashboard.

### Compressão

- **gzip** — universal, ~70% economia em texto.
- **brotli** — ~15% melhor que gzip. Suporte universal (2017+).
- Servir `.br` se `Accept-Encoding: br`. Nginx: `brotli on`.

### Imagens

- **Formato**: AVIF > WebP > JPEG > PNG. AVIF ~50% menor que JPEG.
- **Responsive**: `srcset` + `sizes` carrega tamanho certo por viewport.
- **Lazy** abaixo da dobra.

```html
<img
  src="/img-800.webp"
  srcset="/img-400.webp 400w, /img-800.webp 800w, /img-1600.webp 1600w"
  sizes="(max-width: 600px) 400px, 800px"
  width="800" height="600" alt="...">
```

### Cache HTTP

```
Cache-Control: public, max-age=31536000, immutable
```

Para assets com hash no nome (`app.a1b2c3.js`). HTML principal: `max-age=0, must-revalidate` + `ETag`.

### Font loading

```html
<link rel="preload" href="/font.woff2" as="font" type="font/woff2" crossorigin>
```

```css
@font-face {
  font-family: 'X';
  src: url('/font.woff2') format('woff2');
  font-display: swap;
  size-adjust: 97%;  /* casa com fallback para evitar CLS */
}
```

### HTTP/2 e HTTP/3

- HTTP/2 — multiplexing, cabeçalhos comprimidos.
- HTTP/3 (QUIC) — sem head-of-line blocking, recupera melhor em rede ruim.
- Ativar em nginx/Cloudflare. Ganho mensurável em mobile 4G.

## Ferramentas de medição

- **Chrome DevTools** → Lighthouse → nota + recomendações.
- **PageSpeed Insights** — mesmo Lighthouse + dados reais (CrUX).
- **WebPageTest** — cenários detalhados, multi-localização.
- **web-vitals JS** — coletar RUM (Real User Monitoring) e enviar para analytics.

## Para o dashboard pericial

Dashboard interno = prioridade INP (interações rápidas com tabelas de 100+ processos).

- Virtualizar tabelas grandes (react-virtual, tanstack-virtual).
- Debounce em filtros.
- Paginação no servidor (não baixar 1000 processos de uma vez).
- Cache agressivo de dados estáticos (varas, tipos de processo) via TanStack Query.
- Service Worker para offline (se usar em audiência sem net).

## Armadilhas

- Otimizar antes de medir. 80% do ganho está em 20% das mudanças.
- Obsessão com Lighthouse 100. Dados reais (CrUX/RUM) importam mais.
- Remover libs grandes (moment.js → date-fns/dayjs, lodash completo → imports pontuais).
- Font self-hosted > Google Fonts (privacidade + TTFB).
