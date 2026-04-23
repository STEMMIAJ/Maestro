---
titulo: Estático vs Servidor vs Serverless
bloco: 03_web_development
tipo: comparacao
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 5
---

# Estático vs Servidor vs Serverless

Três modelos de deploy. Trade-offs entre custo, latência, operação, escalabilidade.

## Estático (Static / JAMstack)

HTML/CSS/JS pré-gerados, servidos de CDN. Nada roda no servidor; dados dinâmicos vêm de APIs.

**Onde** — Cloudflare Pages, Vercel (plano estático), Netlify, GitHub Pages, S3+CloudFront, FTP em hospedagem tradicional.

**Custo** — quase zero. Cloudflare Pages: ilimitado requests grátis.

**Latência** — mínima (CDN próxima ao usuário).

**Bom para** — landing, blog, docs, dashboard sem backend próprio (consome APIs externas), portfolio.

**Limitações** — nada de lógica server-side. Precisa rebuild para trocar conteúdo (exceto conteúdo vindo de API).

## Servidor dedicado (VPS / bare metal / container 24/7)

Processo rodando sempre — Node/Python/Go escutando em porta.

**Onde** — DigitalOcean Droplet, Hetzner, AWS EC2, Linode, Fly.io, Render, Railway. Self-host em VPS própria (já tem srv19105 com N8N).

**Custo** — fixo (servidor paga mesmo parado). VPS básica ~$5–20/mês.

**Latência** — 0 cold start.

**Bom para** — app stateful (websocket, long polling), CPU-pesado, cron interno, precisa de FS persistente, quer custo previsível.

**Operação** — manter SO, atualizações, monitoramento, backup, reinício em crash. Usar PM2, systemd, Docker Compose + Watchtower.

## Serverless (FaaS + edge)

Função roda sob demanda; provedor aloca/desaloca. Você paga só pelo que executar.

**Onde**:
- **AWS Lambda / Google Cloud Functions / Azure Functions** — minutos de CPU, memória configurável.
- **Cloudflare Workers / Vercel Edge / Deno Deploy** — edge (roda próximo do usuário), limites mais curtos.
- **AWS Fargate / Cloud Run** — container serverless (mais longa duração que Lambda).

**Custo** — proporcional ao uso. Pode ser $0 se tráfego baixo. Pode virar caro em tráfego alto (Lambda cobra por invocação + duração).

**Latência** — cold start (150ms–3s) se função "dormida". Warm mitiga. Edge Workers: cold start ~5ms.

**Bom para** — picos irregulares, API interna de baixo tráfego, webhook, cron agendado (EventBridge + Lambda), transformação de eventos.

**Limitações** — timeout (Lambda: 15min; Workers: 30s CPU), FS efêmero, conexões DB precisam de pooler (RDS Proxy, Neon, Supabase pgbouncer), frio em idioma pesado (Java, .NET). Node/Python/Go têm cold start curtos.

## Matriz de decisão

| Projeto | Recomendação |
|---------|--------------|
| Blog, landing, docs | **Estático** (Cloudflare Pages) |
| Dashboard interno baixo tráfego | **Serverless** (Cloud Run) ou **Servidor** pequeno |
| App com websocket (chat, colab) | **Servidor** |
| Cron que roda 3x/dia | **Serverless** (EventBridge) ou **launchd local** |
| API pública alta demanda | **Servidor escalável** (k8s, Fargate) ou **Serverless** bem dimensionado |
| Prototipagem rápida | **Serverless** (Vercel, Cloud Run) |
| Integração com DB legado no mesmo DC | **Servidor** (rede privada) |
| Edge com múltiplas regiões | **Edge Workers** |

## Híbridos

- Estático para frontend + Serverless para funções (`/api/*` em Vercel Functions).
- Servidor principal + Lambda para tarefas pontuais (resize de imagem, geração de PDF).
- Cloud Run (container serverless) = compromisso: container Docker, escala a zero, sem gerenciar cluster.

## Custo — exemplo hipotético

Dashboard pericial com 100 visitas/dia, 10 consultas ao DataJud/visita:
- **Servidor** (VPS $5) = $5/mês fixo.
- **Serverless** (100k invocações/mês Lambda) = ~$0.02/mês.
- **Estático + Worker** (Cloudflare Pages + Worker) = $0.

Para tráfego altíssimo inverte-se: servidor dedicado fica mais barato que Lambda cobrando por invocação.

## Para o sistema pericial

- **stemmia.com.br** (site informativo) → **estático** (migrar WordPress para Astro/Hugo, deploy FTP ou Cloudflare Pages).
- **Dashboard interno Streamlit** → **Servidor** (Docker na VPS srv19105 junto com N8N).
- **Webhook de intimação DJEN** → **Serverless** (Cloudflare Worker) ou endpoint FastAPI no mesmo servidor.
- **Monitor 3x/dia de processos** → **launchd local** (já existe) ou Lambda agendada (se quiser redundância cloud).

## Armadilhas

- Vercel/Netlify ficam caros em tráfego alto com funções.
- Lambda com DB tradicional = explosão de conexões. Usar Neon/Supabase/pooler.
- Serverless "sem operação" é mentira. Observabilidade, distributed tracing, retry, DLQ — tudo pago (em tempo ou dinheiro).
- Servidor "grátis" esconde custo de manutenção (atualizar, patch de segurança, backup).
