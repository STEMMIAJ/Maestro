---
titulo: Desenvolvimento Web
bloco: 03_web_development
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 03 — Desenvolvimento Web

## Definição do domínio

Este bloco cobre a stack web de ponta a ponta: marcação e estilo (HTML/CSS), frontend (renderização, estado, componentes), backend (servidor, rotas, banco), APIs (REST, GraphQL), autenticação/autorização, deploy e operação, e os requisitos transversais de performance e acessibilidade.

Objetivo prático: dominar o suficiente para especificar, auditar e, quando necessário, construir aplicações web — especialmente os painéis internos, portais de laudo e integrações com sistemas jurídicos (PJe, DJEN) e de saúde.

Não é um curso de framework da moda. É o mapa das peças duráveis: o que é HTTP, o que é um cookie, como um token JWT funciona, o que é um CDN, o que um deploy quebra.

## Subdomínios

- `html_css/` — marcação semântica, layout (flexbox, grid), especificidade, responsivo.
- `frontend/` — JS no navegador, SPA vs. MPA, frameworks (React/Next, Svelte), estado, roteamento.
- `backend/` — servidor HTTP, rotas, middleware, ORM, renderização server-side.
- `apis/` — REST, GraphQL, OpenAPI, versionamento, idempotência.
- `authentication/` — sessão, cookie, JWT, OAuth2, OIDC, MFA.
- `deployment/` — build, variáveis de ambiente, container, reverse proxy, certificado, CI/CD.
- `performance_accessibility/` — Core Web Vitals, WCAG, lazy loading, cache HTTP.

## Perguntas que este bloco responde

1. Qual a diferença entre sessão e JWT, e quando usar cada um?
2. O que é CORS e por que ele "quebra" chamadas entre domínios?
3. Como estruturar uma API REST que não vira bagunça em 6 meses?
4. O que acontece no build de uma SPA e por que ela demora para abrir?
5. O que é um reverse proxy (nginx, Caddy) e por que quase todo deploy usa um?
6. Como adicionar login com Google sem reinventar OAuth?
7. Quais são os Core Web Vitals e como medi-los?
8. O que torna um site acessível segundo WCAG 2.2?

## Como coletar conteúdo para este bloco

- MDN Web Docs como referência-mestre de HTML/CSS/JS e protocolos.
- web.dev (Google) para performance e Core Web Vitals.
- Documentação oficial dos frameworks em uso (React, Next, Svelte).
- RFCs: HTTP (9110), JWT (7519), OAuth2 (6749), OIDC.
- WCAG 2.2 (W3C) para acessibilidade.
- Repositórios dos próprios portais/painéis do sistema como caso real.

## Critérios de qualidade das fontes

Seguir `00_governance/source_quality_rules.md`. Para web, fonte primária é MDN, W3C, WHATWG e RFCs. Framework muda rápido: registrar sempre versão e data. Descartar tutorial que não declara versão.

## Exemplos de artefatos que podem entrar

- Diagrama "request HTTP do clique ao banco" com pontos de falha.
- Template de API REST com OpenAPI + autenticação JWT.
- Checklist de deploy (env vars, healthcheck, rollback).
- Guia de autenticação OAuth2 com Google em 20 minutos.
- Matriz WCAG 2.2 nível AA com exemplos PT-BR.
- Fluxo de CI/CD com GitHub Actions + container + servidor.

## Interseções com outros blocos

- `02_programming` — JS/TS e Python backend vêm de lá.
- `04_systems_architecture` — APIs, bancos e filas são arquitetura.
- `05_security_and_governance` — autenticação e deploy são superfície crítica.
- `06_data_analytics` — dashboards web puxam daqui.
- `08_ai_and_automation` — integrações via API com LLMs usam este bloco.
- `14_automation` — scripts de deploy e monitoramento consomem este bloco.
