---
titulo: JWT, OAuth2 e Cookies de Sessão
bloco: 03_web_development
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: rfc-oficial
tempo_leitura_min: 8
---

# JWT, OAuth2 e Cookies de Sessão

Três mecanismos comuns para "manter usuário logado". Não se excluem; frequentemente combinam.

## Cookie de sessão (clássico)

Servidor gera ID aleatório no login, armazena em DB/Redis junto com `user_id`. Envia cookie `sessionid=abc123; HttpOnly; Secure; SameSite=Lax`. Browser envia cookie em cada request; servidor resolve `sessionid → user`.

Prós:
- Invalidação imediata (deletar sessão do DB).
- Estado no servidor = revogar, expirar, rastrear devices fácil.
- `HttpOnly` protege contra XSS roubar sessão.
- Padrão para sites renderizados no servidor (Django, Rails, Laravel).

Contras:
- Exige store de sessão (Redis, DB). Escala horizontal precisa de store compartilhado.
- CSRF é risco (mitigar com `SameSite=Lax|Strict` + token CSRF).

## JWT (JSON Web Token)

Token auto-contido. 3 partes base64: header.payload.signature. Servidor assina com chave secreta (HS256) ou par de chaves (RS256/EdDSA).

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE3NDU0MTQ0MDB9.X8y...
```

Payload típico:

```json
{
  "sub": "123",
  "email": "perito@stemmia.com.br",
  "papeis": ["admin"],
  "iat": 1745410800,
  "exp": 1745414400
}
```

Servidor verifica assinatura + expiração. Não precisa consultar DB a cada request.

Prós:
- Stateless — bom para microserviços, serverless.
- Qualquer serviço com chave pública verifica.
- Compacto, HTTP headers.

Contras:
- **Revogação difícil** — token vale até expirar. Mitigação: expiração curta (5–15 min) + refresh token rotativo + blacklist opcional.
- Payload visível (não criptografado; só assinado). Não colocar dados sensíveis.
- Armazenamento no cliente: localStorage (XSS-vulnerável), cookie HttpOnly (melhor, mas CSRF).
- Algoritmo "none" já derrubou sistemas — sempre forçar algoritmo específico ao verificar.

### Padrão Access + Refresh

- **Access token** — curto (15 min), enviado em cada request.
- **Refresh token** — longo (7–30 dias), armazenado em cookie HttpOnly, uso único (rotação).

Quando access expira, cliente troca refresh por novo par. Refresh reutilizado = sinal de roubo → invalidar família inteira.

## OAuth 2.0 / OpenID Connect

OAuth 2.0 = protocolo de **autorização delegada**. "Usuário autoriza App A a acessar recurso do serviço B". Não é login por si; é "terceiro fala por mim".

OpenID Connect (OIDC) = camada de **autenticação** em cima de OAuth 2. Adiciona `id_token` (JWT com identidade).

### Flows

- **Authorization Code + PKCE** — recomendado hoje para SPA, mobile e web. Usuário vai ao provider, volta com código, app troca por tokens.
- **Client Credentials** — máquina-a-máquina (M2M).
- **Device Code** — CLI, TV, dispositivos sem teclado.
- **Implicit** — **obsoleto**, não usar.
- **Resource Owner Password** — **obsoleto**, não usar.

### Casos

- Login com Google/GitHub/Microsoft → OIDC.
- App do Dr. Jesus acessa Google Calendar do usuário → OAuth 2.
- Keycloak/Auth0/AWS Cognito → SSO corporativo.
- Gov.br → OIDC (padrão brasileiro).

### Fluxo simplificado (Authorization Code + PKCE)

1. App gera `code_verifier` (aleatório) e `code_challenge` (hash SHA-256).
2. Redireciona usuário para `provider/authorize?client_id=...&code_challenge=...`.
3. Usuário loga no provider, autoriza.
4. Provider redireciona de volta com `code`.
5. App troca `code` + `code_verifier` por tokens em `provider/token`.
6. Recebe `access_token`, `id_token`, `refresh_token`.

## Matriz de decisão

| Cenário | Escolha |
|---------|---------|
| Site renderizado no servidor (Django, Rails) | **Cookie de sessão** |
| SPA + API própria | **Cookie de sessão** (mesma origem) ou **JWT access+refresh** |
| Mobile nativo | **JWT access+refresh** ou **OAuth2 PKCE** |
| Microserviços | **JWT** (propagação entre serviços) |
| Login social (Google etc) | **OIDC** |
| M2M (servidor chamando servidor) | **OAuth2 Client Credentials** |
| App interno SSO corporativo | **OIDC** via Keycloak/Auth0 |

## Armadilhas comuns

- Armazenar JWT em localStorage e ser vítima de XSS → roubo.
- Não rotacionar refresh token.
- Secret JWT fraco / commitado em git.
- Confiar no `aud` ou `iss` sem validar.
- Usar `HS256` com chave compartilhada entre vários serviços (qualquer um pode forjar). Preferir `RS256`/`EdDSA` com pública/privada.
- JWT "eterno" (`exp` 1 ano). Se vazar, impossível cortar.
- Mistura JWT + cookie sem CSRF protection.

## Para o sistema pericial

Dashboard interno do Dr. Jesus com 1–3 usuários: **cookie de sessão** (Django/FastAPI+Starlette sessions). Simples, revogável, sem dor.

Se no futuro expuser API para app mobile: adicionar **JWT access+refresh** apenas para esse canal.

Se integrar com Gov.br ou CAA (Certificado Digital CNJ): **OIDC**.
