---
titulo: "Como um site carrega"
bloco: "01_ti_foundations/internet_web_basics"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 7
---

# Como um site carrega

Sequência detalhada do que acontece entre digitar `https://stemmia.com.br` e ver a página renderizada.

## 1. Resolução DNS

Navegador verifica cache local. Se não há entrada válida:
1. Pergunta ao *resolver* configurado (roteador → provedor → `8.8.8.8`).
2. Resolver consulta hierarquia: root (`.`) → TLD (`.br`) → autoritativo (`stemmia.com.br`).
3. Retorna IP, ex.: `203.0.113.42`.
4. Cache armazena com TTL.

Erros típicos: `DNS_PROBE_FINISHED_NXDOMAIN` (domínio inexistente), `SERVFAIL` (zona quebrada).

## 2. TCP handshake

Navegador abre socket TCP para `203.0.113.42:443`:

1. Cliente envia `SYN` (sincronize).
2. Servidor responde `SYN-ACK`.
3. Cliente confirma `ACK`.

3 pacotes, 1,5 RTT (round-trip time). Em link de 50 ms de latência, ~75 ms só para estabelecer conexão.

## 3. TLS handshake

Sobre o TCP aberto, negocia criptografia:

1. **Client Hello** — cliente envia versões TLS suportadas, cifras, SNI (`stemmia.com.br`).
2. **Server Hello** — servidor escolhe versão/cifra, envia certificado X.509 + chave pública.
3. **Validação** — cliente verifica cadeia do certificado contra CAs confiáveis do SO, data, domínio, OCSP/CRL.
4. **Key exchange** — deriva chave simétrica de sessão via ECDHE.
5. **Finished** — ambos provam que têm a chave; sessão criptografada começa.

TLS 1.3 faz isso em 1 RTT; TLS 1.2 em 2 RTT. Keep-alive e session resumption reduzem em visitas seguintes.

## 4. Requisição HTTP

Dentro do túnel TLS, o cliente envia:

```
GET / HTTP/1.1
Host: stemmia.com.br
User-Agent: Mozilla/5.0 ...
Accept: text/html,application/xhtml+xml
Cookie: session=abc123
```

Servidor processa (roteamento, autenticação, consulta a banco, renderização) e responde:

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 45321
Set-Cookie: session=xyz789; HttpOnly; Secure

<!DOCTYPE html>
<html>...
```

Cabeçalhos relevantes para perito: `Set-Cookie` (rastreamento), `Strict-Transport-Security` (HSTS), `Content-Security-Policy` (CSP).

## 5. Parse e descoberta de recursos

Navegador recebe o HTML e começa a parsear. Ao encontrar `<link rel="stylesheet" href="/style.css">`, `<script src="/app.js">`, `<img src="/logo.png">`, dispara novas requisições — em paralelo, até 6 por origem em HTTP/1.1, ilimitadas em HTTP/2/3 sobre a mesma conexão.

Cada recurso pode exigir nova resolução DNS + TCP + TLS se for domínio diferente (CDN, fontes do Google, analytics).

## 6. Render

1. **DOM** (*Document Object Model*) — árvore em memória representando o HTML.
2. **CSSOM** — árvore de regras de estilo.
3. **Render tree** = DOM + CSSOM (apenas elementos visíveis).
4. **Layout** — calcula posição e tamanho de cada caixa.
5. **Paint** — pinta pixels na tela.
6. **Composite** — junta camadas (GPU, transições).

JavaScript pode bloquear essa etapa (`<script>` síncrono) ou rodar depois (`defer`, `async`, módulos). Páginas modernas fazem *hidration* (React/Vue) depois do primeiro paint.

## 7. Interação contínua

Após carga inicial, clicar pode disparar:
- Nova requisição HTTP (link comum).
- Fetch AJAX que atualiza parte da página (SPA).
- WebSocket aberto para tempo real (chat, notificações).

## Métricas que importam

- **TTFB** (*Time to First Byte*) — chegada do primeiro byte da resposta. Mede servidor+rede.
- **FCP** (*First Contentful Paint*) — primeiro pixel renderizado.
- **LCP** (*Largest Contentful Paint*) — maior elemento visível carregado. Meta: < 2,5 s.
- **CLS** (*Cumulative Layout Shift*) — quanto o layout pula. Meta: < 0,1.

Chrome DevTools → aba Network + Performance expõe tudo.

## Por que importa para o perito

- **Perícia em conteúdo online** exige capturar *timestamp*, URL, IP resolvido, hash HTML e screenshot — idealmente com ferramenta que preserve headers e certificado.
- **Prova de autoria** em rede social depende de entender cookies, sessão e User-Agent — perfil falso cria pegada diferente.
- **Pagamento por clique fraudado** (Google Ads, Meta) exige saber que clique dispara requisição HTTP com *referrer*; ausência de referrer legítimo é indício de bot.

## Referências

- RFC 9110 (HTTP Semantics), RFC 9113 (HTTP/2), RFC 9114 (HTTP/3), RFC 8446 (TLS 1.3).
- web.dev/metrics (Core Web Vitals).
