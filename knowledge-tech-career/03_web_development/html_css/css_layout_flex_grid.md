---
titulo: Layout CSS — Flexbox vs Grid
bloco: 03_web_development
tipo: referencia
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: padrao-w3c
tempo_leitura_min: 8
---

# Layout CSS — Flexbox vs Grid

Dois sistemas modernos. Ambos substituem `float` e tabelas de layout. Decisão simples: **uma dimensão = Flex, duas dimensões = Grid**.

## Flexbox (1D)

Distribui itens em linha OU coluna. Ideal para barra de navegação, lista de botões, cards numa linha.

```css
.barra {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
}
```

Propriedades-chave no pai:
- `flex-direction: row | column`
- `justify-content` — eixo principal (horizontal se row).
- `align-items` — eixo cruzado.
- `flex-wrap: wrap` — quebra linha quando não cabe.
- `gap` — espaço entre itens (substitui margin).

No filho:
- `flex: 1` — cresce para ocupar sobra.
- `flex: 0 0 200px` — largura fixa 200px, não cresce nem encolhe.

## Grid (2D)

Linhas E colunas simultâneas. Ideal para layout de página inteira, dashboard com painéis, galeria.

```css
.dashboard {
  display: grid;
  grid-template-columns: 240px 1fr;
  grid-template-rows: 64px 1fr;
  grid-template-areas:
    "sidebar header"
    "sidebar main";
  gap: 1rem;
  min-height: 100vh;
}
.sidebar { grid-area: sidebar; }
.header  { grid-area: header; }
.main    { grid-area: main; }
```

Unidade `fr` = fração do espaço disponível. `1fr 2fr` = primeira coluna 1/3, segunda 2/3.

Layout responsivo de cards sem media query:

```css
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}
```

Cada card tem no mínimo 280px; o grid calcula quantas colunas cabem.

## Quando cada

| Situação | Escolha |
|----------|---------|
| Barra de menu horizontal | Flex |
| Lista vertical de itens | Flex (column) |
| Dashboard com sidebar+header+main | Grid |
| Galeria de cards responsiva | Grid com auto-fill |
| Formulário label-input alinhado | Grid (2 colunas) |
| Alinhar ícone+texto dentro de botão | Flex |

Pode combinar: página com Grid, cada célula com Flex por dentro. Esse é o padrão em dashboard pericial.

## Exemplo prático — ficha do processo

```html
<article class="ficha">
  <header class="ficha-head">...</header>
  <dl class="ficha-dados">
    <dt>Autor</dt><dd>João Silva</dd>
    <dt>Réu</dt><dd>INSS</dd>
    <dt>Vara</dt><dd>1ª Vara Federal</dd>
  </dl>
</article>
```

```css
.ficha { display: grid; gap: 1rem; padding: 1rem; }
.ficha-head { display: flex; justify-content: space-between; }
.ficha-dados {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 0.25rem 1rem;
}
.ficha-dados dt { font-weight: 600; }
```

## Erros comuns

- Usar `float` em código novo. Desuso desde 2017.
- Fixar altura em px. Deixar conteúdo ditar altura + `min-height` quando necessário.
- `margin` para espaçar filhos de Flex/Grid. Usar `gap`.
- Grid com `grid-template-columns` fixo em px sem `fr` — não responsivo.

## Debug

Chrome DevTools → aba Elements → ícone `grid` ou `flex` ao lado do elemento mostra linhas guia.

## Suporte

Flex e Grid: 100% dos browsers modernos (2017+). Sem polyfill, sem prefixos.
