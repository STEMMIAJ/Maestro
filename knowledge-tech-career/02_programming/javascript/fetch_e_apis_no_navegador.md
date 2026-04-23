---
titulo: Fetch e APIs no navegador
bloco: 02_programming
tipo: referencia
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 4
---

# Fetch e APIs no navegador

## `fetch` — cliente HTTP nativo
Substituiu `XMLHttpRequest`. Funciona em todos navegadores modernos.

```javascript
const r = await fetch("/api/processos");
if (!r.ok) throw new Error(`HTTP ${r.status}`);
const dados = await r.json();
console.log(dados);
```

`r.ok` é `true` se status for 200–299. `r.status` é o código (200, 404, 500...).

## POST com JSON
```javascript
const r = await fetch("/api/processos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cnj: "0001-2024", autor: "João" }),
});
const criado = await r.json();
```

`JSON.stringify` converte objeto JS em string JSON.

## Enviar formulário (multipart)
```javascript
const form = document.querySelector("form");
const dados = new FormData(form);          // pega todos campos automaticamente

const r = await fetch("/upload", {
    method: "POST",
    body: dados,                            // navegador seta Content-Type certo
});
```

Não colocar `Content-Type` manual com `FormData` — o navegador adiciona o `boundary` correto.

## Tratamento de erro
```javascript
async function buscar(url) {
    try {
        const r = await fetch(url, { signal: AbortSignal.timeout(10000) });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return await r.json();
    } catch (err) {
        if (err.name === "TimeoutError") {
            console.error("demorou mais de 10s");
        } else {
            console.error("falhou:", err);
        }
        return null;
    }
}
```

`AbortSignal.timeout` é o equivalente a `timeout=` do Python `requests`. Sem ele, requisição pode ficar pendurada.

## CORS — o básico
CORS (Cross-Origin Resource Sharing) é regra de segurança do navegador: JS rodando em `site-a.com` **não pode** chamar API em `site-b.com` por padrão.

Quem libera é o **servidor** — deve responder com header `Access-Control-Allow-Origin: site-a.com` (ou `*` para público).

Erro típico no console:
```
Access to fetch at 'https://api.b.com' from origin 'https://a.com'
has been blocked by CORS policy
```

Soluções:
1. Servidor envia header CORS correto (caminho certo).
2. Proxy no seu próprio back-end: JS chama `/api/proxy`, seu servidor chama a API externa (servidor não tem CORS).
3. Nunca: desligar CORS no navegador — quebra segurança.

Exemplo pericial: DataJud bloqueia chamada direta do navegador. Solução: script Python no servidor chama DataJud, expõe resultado em endpoint próprio, JS consome.

## Armadilhas
- `fetch` **não levanta** erro em HTTP 4xx/5xx. Só em falha de rede. Sempre testar `r.ok`.
- Sem `await` antes de `fetch` → recebe Promise crua, não a resposta.
- `response.json()` só pode ser chamado uma vez por resposta.
