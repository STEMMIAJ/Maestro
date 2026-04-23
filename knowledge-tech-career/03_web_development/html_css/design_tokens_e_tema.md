---
titulo: Design Tokens e Tema
bloco: 03_web_development
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: padrao-w3c
tempo_leitura_min: 5
---

# Design Tokens e Tema

Design token = valor nomeado reutilizável (cor, espaçamento, raio, tipografia). Centraliza decisões de design em variáveis CSS. Trocar o tema = trocar o valor em 1 lugar.

## Sintaxe básica — variáveis CSS

```css
:root {
  /* cores */
  --cor-fundo: #ffffff;
  --cor-texto: #1a1a1a;
  --cor-primaria: #0d47a1;
  --cor-perigo: #b00020;
  --cor-borda: #e0e0e0;

  /* espaçamento (escala 4px) */
  --esp-1: 0.25rem;
  --esp-2: 0.5rem;
  --esp-3: 1rem;
  --esp-4: 1.5rem;
  --esp-5: 2rem;

  /* tipografia */
  --fonte-base: system-ui, -apple-system, sans-serif;
  --tam-texto: 1rem;
  --tam-titulo: 1.5rem;

  /* raio e sombra */
  --raio-sm: 4px;
  --raio-md: 8px;
  --sombra-md: 0 2px 8px rgba(0,0,0,0.08);
}

.botao {
  background: var(--cor-primaria);
  color: var(--cor-fundo);
  padding: var(--esp-2) var(--esp-3);
  border-radius: var(--raio-md);
}
```

## Dark mode

Duas estratégias:

**1. Automático (segue SO):**

```css
@media (prefers-color-scheme: dark) {
  :root {
    --cor-fundo: #121212;
    --cor-texto: #e0e0e0;
    --cor-borda: #333;
  }
}
```

**2. Manual (usuário escolhe):**

```css
[data-tema="escuro"] {
  --cor-fundo: #121212;
  --cor-texto: #e0e0e0;
}
```

```js
document.documentElement.dataset.tema = 'escuro';
localStorage.setItem('tema', 'escuro');
```

Combinação recomendada: detectar SO por padrão, permitir override manual, persistir em localStorage.

## Tokens para dashboard pericial

Categorias específicas da prática:

```css
:root {
  /* status de processo */
  --st-ativo: #1b5e20;
  --st-suspenso: #e65100;
  --st-arquivado: #424242;
  --st-urgente: #b71c1c;

  /* contextos clínicos */
  --c-ncf: #0d47a1;    /* nexo causal */
  --c-incapa: #6a1b9a; /* incapacidade */
  --c-dano: #b00020;   /* dano */

  /* densidade (sobrecarga sensorial: usar alta) */
  --densidade-linha: 1.4;
  --densidade-padding: var(--esp-2);
}
```

Alta densidade (padding menor, line-height 1.3–1.4) reduz rolagem em listas de 100+ processos. Baixa densidade (1.6, padding maior) em laudos longos para leitura confortável.

## Boas práticas

- Escala consistente (múltiplos de 4 ou 8). Evitar valores arbitrários (13px, 17px).
- Nome por função, não por aparência. `--cor-perigo` > `--cor-vermelha`. Trocar o vermelho não quebra sentido.
- Contraste WCAG AA: cor-texto vs cor-fundo ≥ 4.5:1. Testar em webaim.org/resources/contrastchecker.
- Limite de 30–50 tokens. Mais que isso vira bagunça; usar sistema (Tailwind, Open Props).

## Ferramentas

- Open Props — `https://open-props.style` — tokens prontos via CSS.
- Tailwind CSS — sistema de classes utilitárias baseado em tokens.
- Style Dictionary (Amazon) — tokens em JSON gerando CSS+iOS+Android.

## Migração

Refatorar projeto existente: rodar `rg '#[0-9a-f]{3,6}' --type css` para listar todas as cores hardcoded, substituir progressivamente por tokens.
