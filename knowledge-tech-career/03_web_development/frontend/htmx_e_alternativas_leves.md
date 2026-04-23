---
titulo: HTMX e Alternativas Leves
bloco: 03_web_development
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 5
---

# HTMX e Alternativas Leves

Nem todo projeto precisa de React. HTMX e Alpine.js trazem interatividade sem framework pesado, sem build tool, sem estado client. Servidor devolve HTML, browser troca pedaço da página.

## HTMX

Filosofia: HTML é suficiente como hipermídia. Interações via atributos.

```html
<script src="https://unpkg.com/htmx.org@2"></script>

<button hx-get="/api/processos/123" hx-target="#detalhe" hx-swap="innerHTML">
  Ver detalhes
</button>
<div id="detalhe"></div>
```

Clique → GET `/api/processos/123` → servidor retorna HTML → HTMX substitui conteúdo de `#detalhe`.

Atributos principais:
- `hx-get` / `hx-post` / `hx-put` / `hx-delete` — método HTTP.
- `hx-target` — seletor CSS do destino.
- `hx-swap` — como inserir (`innerHTML`, `outerHTML`, `beforeend`, etc.).
- `hx-trigger` — evento disparador (`click`, `change`, `every 5s` para polling).
- `hx-indicator` — elemento de loading.

Caso de uso: CRUD com backend Python/Go, formulários, tabelas com paginação, busca incremental. Bundle: ~14 KB gzip. Zero dependência.

## Alpine.js

Reatividade client-side pequena, sintaxe Vue-like via atributos.

```html
<script defer src="https://unpkg.com/alpinejs@3"></script>

<div x-data="{ aberto: false }">
  <button @click="aberto = !aberto">Menu</button>
  <nav x-show="aberto" x-transition>...</nav>
</div>
```

Diretivas:
- `x-data` — estado local.
- `x-show` / `x-if` — visibilidade.
- `@click` / `@input` — eventos.
- `x-model` — binding bidirecional.

Bundle: ~15 KB gzip. Combina bem com HTMX (Alpine para estado UI, HTMX para comunicação servidor).

## Quando dispensar framework pesado

Usar HTMX/Alpine quando:
- Backend já renderiza HTML (Django, Flask, Rails, Laravel, Phoenix).
- Time pequeno, sem especialista frontend.
- App CRUD com pouca interação complexa.
- Latência aceitável (ida e volta ao servidor por interação).

Usar React/Svelte quando:
- Interação complexa client-side (arrastar-soltar, editor rich-text).
- Offline-first, PWA.
- Estado client complexo (formulário multi-step, wizard).
- App tipo SPA genuíno (Figma, Notion).

## Outras alternativas leves

- **Unpoly** — similar ao HTMX, mais opinativo, navegação completa de páginas.
- **Hotwire (Turbo + Stimulus)** — padrão do Rails. Turbo faz navegação parcial, Stimulus adiciona JS.
- **Preact** — React com 3 KB. Mesma API, compatível.
- **petite-vue** — Vue compacto (6 KB) com mesma ideia de Alpine.

## Para o sistema pericial

Dashboard que puxa dados do DataJud, exibe lista de processos, abre detalhes ao clicar: **HTMX + Flask/FastAPI** entrega em 1 dia, sem build, sem npm. Deploy via FTP no stemmia.com.br. Só migrar para SPA se aparecer interação impossível (ex: editor visual de laudo com preview ao vivo).

## Armadilhas

- HTMX sem cuidado vira waterfall (muitos requests sequenciais). Agrupar respostas.
- Alpine para estado global não escala. Usar store (Alpine.store) limitado a UI.
- SEO em SPA é problema; em HTMX é zero (HTML vem do servidor).
