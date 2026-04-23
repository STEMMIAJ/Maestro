---
titulo: DOM e eventos em JavaScript
bloco: 02_programming
tipo: referencia
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 4
---

# DOM e eventos

## DOM — o que é
DOM (Document Object Model) é a representação da página HTML como árvore de objetos JavaScript. Cada `<div>`, `<button>`, `<p>` vira um nó manipulável via código.

Exemplo: quando o PJe mostra a lista de processos, o que você vê é o DOM. O Selenium/Playwright mexe nesse DOM para clicar e extrair texto.

## Selecionar elementos
```javascript
// por id (único)
const botao = document.getElementById("enviar");
// CSS selector — mais versátil
const botao = document.querySelector("#enviar");
const primeiroLink = document.querySelector("a.link-processo");
// todos os que batem
const todosLinks = document.querySelectorAll("a.link-processo");
```

`querySelector` aceita qualquer seletor CSS (`.classe`, `#id`, `tag`, `[atributo=valor]`).

## Ler/alterar conteúdo
```javascript
const titulo = document.querySelector("h1");
console.log(titulo.textContent);      // lê texto
titulo.textContent = "Novo título";    // altera

// atributos
const link = document.querySelector("a");
link.href = "https://exemplo.com";
link.setAttribute("target", "_blank");

// classes CSS
titulo.classList.add("destaque");
titulo.classList.remove("oculto");
titulo.classList.toggle("ativo");
```

`textContent` é seguro (só texto). `innerHTML` aceita HTML bruto — **cuidado com XSS** se o conteúdo vem de usuário.

## Eventos — `addEventListener`
Evento = coisa que acontece na página (clique, digitar, carregar).

```javascript
const botao = document.querySelector("#enviar");

botao.addEventListener("click", (event) => {
    event.preventDefault();               // cancela ação padrão
    console.log("clicou");
});

// tecla digitada em input
const campo = document.querySelector("#cnj");
campo.addEventListener("input", (e) => {
    console.log("digitou:", e.target.value);
});

// submeter formulário sem recarregar
const form = document.querySelector("form");
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const dados = new FormData(form);
    const r = await fetch("/api", { method: "POST", body: dados });
    ...
});
```

Eventos comuns: `click`, `submit`, `input`, `change`, `load`, `DOMContentLoaded`, `keydown`.

## Criar elementos
```javascript
const li = document.createElement("li");
li.textContent = "Novo processo";
li.classList.add("item");
document.querySelector("ul.lista").appendChild(li);
```

## Armadilhas
- Script no `<head>` roda antes do HTML existir → `querySelector` retorna `null`. Solução: colocar script antes de `</body>` ou usar `DOMContentLoaded`.
- `innerHTML = userInput` → vulnerabilidade XSS. Usar `textContent`.
- Esquecer `event.preventDefault()` em `submit` → página recarrega e perde estado.
