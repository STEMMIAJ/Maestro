---
titulo: "HTML, CSS e JS — o trio"
bloco: "01_ti_foundations/internet_web_basics"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 4
---

# HTML, CSS e JS — o trio

Toda página web, simples ou complexa, é composta por três linguagens distintas, com papéis separados:

## HTML — estrutura

*HyperText Markup Language*. Define **o conteúdo e sua semântica**: o que é título, o que é parágrafo, o que é lista, o que é link. Não cuida de aparência nem de comportamento.

Exemplo mínimo:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Laudo 001/2026</title>
</head>
<body>
  <h1>Laudo pericial</h1>
  <p>Paciente: <strong>Fulano de Tal</strong></p>
  <ul>
    <li>Data: 23/04/2026</li>
    <li>Perito: Dr. Jesus</li>
  </ul>
</body>
</html>
```

## CSS — aparência

*Cascading Style Sheets*. Define **como o conteúdo HTML é exibido**: cores, fontes, tamanhos, espaçamentos, layout, animações. Regras aplicadas por seletor.

Exemplo mínimo:

```css
body { font-family: "Times New Roman", serif; max-width: 800px; margin: 40px auto; }
h1 { color: #003366; border-bottom: 2px solid #003366; }
strong { color: #a00; }
```

Cascata: várias regras podem mirar o mesmo elemento; vence a mais específica + a declarada depois.

## JavaScript — comportamento

Linguagem de programação que roda no navegador (e no servidor via Node.js). Responsável por **interatividade e lógica dinâmica**: responder a cliques, validar formulário, buscar dados via API, atualizar a página sem recarregar.

Exemplo mínimo:

```html
<button id="b">Confirmar laudo</button>
<script>
  document.getElementById('b').addEventListener('click', () => {
    alert('Laudo confirmado às ' + new Date().toLocaleTimeString());
  });
</script>
```

JS tem acesso ao DOM (pode ler e modificar o HTML ao vivo), ao CSSOM, à rede (`fetch`), ao armazenamento local (`localStorage`, IndexedDB).

## Separação de responsabilidades

Boa engenharia web separa:
- `index.html` — só estrutura.
- `style.css` — só aparência.
- `app.js` — só comportamento.

Mistura inline (`<p style="color:red" onclick="...">`) funciona mas dificulta manutenção.

## Por que importa para o perito

- **Captura de página web como prova** deve preservar os três: salvar HTML + CSS + assets. "Imprimir para PDF" perde comportamento JS e pode omitir conteúdo carregado dinamicamente. Ferramenta como SingleFile resolve.
- **Automação de PJe** (Selenium/Playwright) depende de localizar elementos por seletor CSS (`#cpfInput`, `.btn-submit`) — mesma sintaxe do CSS.
- **Perícia em fraude online** pode exigir ler o JS da página para provar que um clique enviava dados a domínio suspeito.

## Referências

- WHATWG HTML Living Standard; W3C CSS Specifications; ECMAScript (TC39) para JavaScript.
