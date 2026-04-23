---
titulo: JavaScript mínimo para desenvolvimento web
bloco: 02_programming
tipo: referencia
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 7
---

# JavaScript mínimo

Base para entender qualquer front-end moderno (React, Vue, scripts de página).

## Variáveis — `let` e `const`
```javascript
const CNJ_REGEX = /\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}/;   // nao reatribui
let tentativas = 0;                                          // reatribui
tentativas += 1;
```

**Nunca usar `var`**. Escopo de `var` vaza para fora do bloco — gera bug. `let` e `const` têm escopo de bloco (igual Python).

Regra: `const` por padrão. Só vira `let` se precisar reatribuir.

## Tipos
```javascript
42              // number (int e float juntos)
"texto"         // string
true / false    // boolean
null            // vazio intencional
undefined       // nao atribuído
[1, 2, 3]       // array
{cnj: "0001"}   // objeto (igual dict Python)
```

## Funções
```javascript
// declaração clássica
function extrairCnj(texto) {
    return texto.match(CNJ_REGEX)?.[0] ?? null;
}

// arrow function — mais curta
const extrairCnj = (texto) => texto.match(CNJ_REGEX)?.[0] ?? null;

// arrow com corpo
const processar = (p) => {
    const cnj = extrairCnj(p.texto);
    return { ...p, cnj };
};
```

Arrow function é preferida hoje. Mais curta e não redefine `this`.

`?.` encadeamento opcional — se `match()` retorna `null`, não quebra.
`??` nullish coalescing — retorna direita só se esquerda for `null`/`undefined`.

## Condicional e loop
```javascript
if (idade >= 18) {
    status = "adulto";
} else if (idade >= 12) {
    status = "adolescente";
} else {
    status = "crianca";
}

// for-of — preferir a for clássico
for (const processo of lista) {
    console.log(processo.cnj);
}

// métodos funcionais — mais idiomáticos
lista.forEach(p => console.log(p.cnj));
const cnjs = lista.map(p => p.cnj);
const pendentes = lista.filter(p => p.status === "pendente");
const total = lista.reduce((acc, p) => acc + p.valor, 0);
```

## Promise — valor futuro
Promise representa operação assíncrona (rede, arquivo, timer). Estados: pending → fulfilled (resolve) ou rejected (reject).

```javascript
const promessa = fetch("/api/processos");
promessa
    .then(r => r.json())
    .then(dados => console.log(dados))
    .catch(err => console.error(err));
```

Por que importa: rede é lenta. JS não bloqueia — continua, volta depois que a resposta chega.

## `async / await` — sintaxe limpa
```javascript
async function buscarProcessos() {
    try {
        const r = await fetch("/api/processos");
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const dados = await r.json();
        return dados;
    } catch (err) {
        console.error("falha:", err);
        return [];
    }
}

// chamar
const dados = await buscarProcessos();
```

`async` marca função como assíncrona (retorna Promise).
`await` pausa até a Promise resolver — só pode ser usado dentro de `async`.

Por que importa: código assíncrono fica parecido com síncrono. Sem `await`, cai em "callback hell".

## Módulos
```javascript
// arquivo utils.js
export const extrairCnj = (t) => ...;
export default class Processo { ... }

// arquivo main.js
import Processo, { extrairCnj } from "./utils.js";
```

## Armadilhas
- `==` vs `===` — sempre `===` (estrito). `==` converte tipos: `"0" == false` é `true` (absurdo).
- `null` e `undefined` são diferentes. Testar com `== null` pega os dois.
- `this` em função normal depende de como é chamada. Arrow não tem `this` próprio.
