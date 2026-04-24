# Dashboard stemmia.com.br — plano inicial

Gerado em 2026-04-22. Nenhuma mudanca remota feita.

## Objetivo
Painel privado para Dr. Jesus visualizar estado do Dexter, Maestro e pericias sem precisar abrir terminal.

## Area no site
Sugestao: criar pasta dedicada no projeto do site (por exemplo, `site/dashboard/`) com rotas protegidas por basic auth inicialmente; migrar para Supabase Auth quando DB adotado.

## Rotas sugeridas
- `/dashboard-dexter` — saude global do ecossistema (quantidade de processos, scripts, agentes, avisos).
- `/dashboard-pericias` — pericias em andamento com prazos.
- `/dashboard-maestro` — status das fases do Maestro, ultimas conversas ingeridas.
- `/dashboard-logs` — ultimos 50 eventos (cron, pipeline).

## Componentes minimos
- Card numerico grande (numero + rotulo).
- Lista com status colorido (verde/amarelo/vermelho) — alto contraste.
- Grafico simples (barra ou sparkline) — evitar dashboards carregados.
- Busca rapida (processo por CNJ) — prioritaria.

## Design
- Tipografia grande, espacamento generoso (acessibilidade TEA/TDAH).
- Contraste alto, sem gradientes.
- Uma acao por card.
- Reutilizar paleta e tipografia do "Planner Stemmia" existente para consistencia visual.

## Roadmap em 3 etapas

### MVP (minimo viavel)
- 1 rota: `/dashboard-maestro`.
- Dados vindos de JSON estatico gerado por cron J07.
- Basic auth local.
- Deploy manual.

### Intermediario
- 3 rotas ativas.
- Dados em Supabase ou SQLite publicado por cron.
- Auth Supabase.
- Search por CNJ.

### Completo
- 4+ rotas.
- Atualizacao em tempo "quasi-real" (5 min).
- Notificacoes push opcionais.
- Integracao bidirecional com bot Telegram.

## Tecnologia (RESEARCH)
Candidatos:
- **Astro** — estatico + ilhas interativas; ideal para dashboard predominantemente read-only.
- **Next.js** — se houver formularios/ativos mais interativos.
- **Eleventy** — se tudo for estatico e simples.
- **HTML + JS vanilla** — para MVP minimalista.

Decidir na proxima rodada (backlog B006).

## Consideracoes de acessibilidade (TEA/TDAH)
- Sem animacoes gratuitas.
- Densidade baixa (no maximo 5 cards por tela).
- Sempre mostra um unico proximo passo.
- Botoes grandes, distancia clara entre eles.
- Shortcut de teclado para busca (`/`).

## Status atual
- Planejado.
- Zero codigo.
- Zero deploy.
