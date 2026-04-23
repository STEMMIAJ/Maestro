---
titulo: Acessibilidade Essencial (a11y)
bloco: 03_web_development
tipo: referencia
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: padrao-w3c-wcag
tempo_leitura_min: 5
---

# Acessibilidade Essencial (a11y)

A11y (11 letras entre "a" e "y") = acessibilidade web. Não é opcional em sistema público, e no contexto pericial afeta litigantes com deficiência. WCAG é o padrão.

## WCAG 2.2 (atual)

Quatro princípios (POUR):
- **Perceptível** — informação apresentável aos sentidos do usuário.
- **Operável** — componentes e navegação usáveis.
- **Compreensível** — informação e interface entendíveis.
- **Robusto** — interpretável por diferentes agentes (leitor de tela, tradutor).

Níveis: **A** (mínimo), **AA** (padrão prático; lei brasileira LBI exige), **AAA** (aspiracional).

WCAG 2.2 (out/2023) adicionou 9 critérios novos — foco em mobile e cognição.

## Os 10 itens que resolvem 80%

### 1. Texto alternativo em imagem

```html
<img src="radiografia.jpg" alt="Radiografia AP do joelho direito com sinal de derrame articular">
<img src="decoracao.svg" alt="">  <!-- alt vazio = decorativa -->
```

Gráfico complexo → `alt` resumido + descrição longa em `<figcaption>` ou `aria-describedby`.

### 2. Contraste de cor

- Texto normal: **4.5:1**.
- Texto grande (≥18pt ou 14pt bold): **3:1**.
- Componentes UI (borda de input, ícone): **3:1**.

Testar: DevTools Chrome → elemento → color picker mostra contraste.

### 3. Navegação por teclado

Tudo que mouse faz, teclado faz. Tab percorre na ordem lógica. `Esc` fecha modal. `Enter`/`Espaço` ativa botões.

Testar: desconectar mouse, usar só teclado por 5 minutos.

Esconder outline = **proibido** sem substituir. `:focus-visible` mostra só quando navega por teclado:

```css
:focus-visible {
  outline: 2px solid var(--cor-primaria);
  outline-offset: 2px;
}
```

### 4. Rótulo em formulário

```html
<label for="cpf">CPF</label>
<input id="cpf" type="text" autocomplete="off">
```

Nunca só placeholder. Placeholder some ao digitar, não é lido bem por leitor de tela.

### 5. Hierarquia de títulos

`h1 → h2 → h3` em ordem. Não pular. Usar CSS para estilizar, não mudar tag pela aparência.

### 6. Idioma declarado

```html
<html lang="pt-BR">
```

Trecho em outro idioma:

```html
<span lang="en">knowledge</span>
```

### 7. Link com texto descritivo

Ruim: "Clique aqui", "Leia mais".
Bom: "Baixar laudo do processo 1001234-56".

Leitor de tela extrai lista de links. "Clique aqui" 50 vezes é inútil.

### 8. Landmarks

`<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>` — leitor de tela pula direto. Substitui `<div class="header">`.

### 9. ARIA — quando nativo não basta

Regra #1 de ARIA: **não usar ARIA se HTML nativo resolve**.

`<button>` > `<div role="button">`. Mas para widgets custom (accordion, tabs, combobox) ARIA é necessário.

```html
<button aria-expanded="false" aria-controls="menu-1">Menu</button>
<ul id="menu-1" hidden>...</ul>
```

`aria-live="polite"` para regiões que atualizam (ex: "salvando...", "salvo").

### 10. Movimento e animação

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

Algumas pessoas têm vestibular disorder; animação exagerada causa náusea.

## Novos em WCAG 2.2

- **Target Size 2.5.8** — alvo de toque ≥ 24×24 px (AA).
- **Focus Not Obscured 2.4.11** — barra fixa no topo não pode esconder elemento focado.
- **Consistent Help 3.2.6** — ajuda (chat, email) no mesmo lugar em todas as páginas.
- **Accessible Authentication 3.3.8** — não exigir que usuário memorize/digite captcha complexo (autofill é aceitável).

## Leitores de tela

Testar com leitor real:
- **NVDA** (Windows, grátis).
- **VoiceOver** (Mac, `Cmd+F5`).
- **TalkBack** (Android).
- **JAWS** (Windows, pago, padrão corporativo).

Cada um interpreta ARIA ligeiramente diferente. Testar em pelo menos 2.

## Ferramentas automáticas

- **axe DevTools** (extensão Chrome) — flags ~30% dos problemas WCAG.
- **Lighthouse** — nota A11y.
- **WAVE** (WebAIM) — visualiza issues na página.
- **Pa11y CI** — rodar em pipeline.

Automático pega ~30–40%. Resto exige teste manual (teclado, leitor de tela, zoom 200%).

## Para o sistema pericial

- Contraste AA obrigatório em dashboard (usuários leem longos períodos).
- `prefers-reduced-motion` respeitado (Dr. Jesus autista, TEA + sensibilidade sensorial — usuário alvo).
- Tabelas com `<th scope="col">` e `<caption>`.
- PDFs gerados (laudos) também precisam a11y — usar `WeasyPrint` ou `ReportLab` com tags.

## Armadilhas

- `alt="imagem"` ou nome do arquivo — inútil.
- Apenas cor transmitindo informação (verde=ativo, vermelho=urgente). Adicionar ícone/texto.
- Modal sem `role="dialog"` + foco trap. Tab escapa do modal e navega no fundo.
- Ícone-botão sem texto (`<button><svg>...</svg></button>` sem `aria-label`).
- Skip link ausente (`<a href="#main">Pular para conteúdo</a>` no topo).
