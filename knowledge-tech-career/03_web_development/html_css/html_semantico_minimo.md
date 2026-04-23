---
titulo: HTML Semântico Mínimo
bloco: 03_web_development
tipo: referencia
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: padrao-w3c
tempo_leitura_min: 6
---

# HTML Semântico Mínimo

HTML semântico = usar a tag certa pelo significado, não pela aparência. Browser, leitor de tela e buscador entendem a estrutura.

## Esqueleto obrigatório

```html
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Laudo — Processo 1001234-56.2025</title>
</head>
<body>
  <header>...</header>
  <main>...</main>
  <footer>...</footer>
</body>
</html>
```

`lang="pt-BR"` é obrigatório para leitor de tela ler em português.

## Tags estruturais (landmarks)

- `<header>` — topo da página ou de uma seção.
- `<nav>` — menu de navegação.
- `<main>` — conteúdo único da página (1 por página).
- `<article>` — peça autocontida (um laudo, uma notícia).
- `<section>` — agrupamento temático (precisa de título interno).
- `<aside>` — conteúdo lateral (barra de filtros).
- `<footer>` — rodapé.

Leitor de tela pula direto entre landmarks. Sem elas, o usuário cego tab-a-tab percorre tudo.

## Hierarquia de títulos (h1–h6)

- `<h1>` único por página, descreve o conteúdo principal.
- `<h2>` seções diretas sob o `h1`.
- `<h3>` subseções do `h2`. Nunca pular nível (h1 → h3 quebra estrutura).
- `h4`–`h6` raros em página de dashboard; úteis em laudo longo.

Regra: hierarquia reflete sumário lógico, não tamanho visual. Estilo é com CSS.

## Formulários

```html
<label for="processo">Número do processo</label>
<input id="processo" name="processo" type="text" required
       pattern="\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"
       aria-describedby="ajuda-processo">
<small id="ajuda-processo">Formato CNJ: 0000000-00.0000.0.00.0000</small>
```

`<label for>` ligado a `id` do input = clicar no texto foca o campo + leitor de tela lê junto.

## Acessibilidade básica (a11y)

- Texto alternativo: `<img alt="Gráfico de evolução da ADM do joelho direito">`. Imagem decorativa: `alt=""`.
- Botão é `<button>`, link é `<a href>`. Não fingir com `<div onclick>`.
- Contraste mínimo 4.5:1 (WCAG AA). Ferramenta: axe DevTools.
- Foco visível: não remover `outline` sem substituir.
- ARIA só quando HTML nativo não dá conta. Primeira regra de ARIA: não usar ARIA.

## Validar

- validator.w3.org/nu — valida HTML.
- Lighthouse (Chrome DevTools) — nota de acessibilidade e SEO.
- NVDA (Windows) / VoiceOver (Mac) — testar com leitor de tela real.

## Para o contexto pericial

Laudos em HTML devem usar `<article>` com `<header>` (dados do processo), `<section>` por tópico (histórico, exame físico, conclusão), `<footer>` com assinatura. Facilita conversão PDF e leitura em qualquer dispositivo.
