# Estimativa de custo — inicial (qualitativa)

Gerado em 2026-04-22. Sem valores. Apenas fontes de custo.

## Fontes de custo identificadas

### Modelos LLM
- Claude Code (plano atual): custo existente — TODO/RESEARCH confirmar plano.
- Claude API (Opus/Sonnet/Haiku): por token — TODO/RESEARCH.
- Outros provedores: a avaliar apenas se necessario.

### Hospedagem e dashboard
- Dominio stemmia.com.br: ja pago (fonte: Dr. Jesus — nao confirmado aqui).
- Hospedagem atual do site: TODO/RESEARCH (compartilhada? VPS? serverless?).
- Dashboard adicional: custo depende da stack escolhida (Next, Astro, Eleventy).

### Banco de dados
- Supabase free tier: existe, limites a confirmar — TODO/RESEARCH.
- Supabase pago: preco por DB + storage + requisitos — TODO/RESEARCH.
- Postgres self-hosted: custo de VPS — TODO/RESEARCH.
- SQLite local + sync: custo proximo a zero (armazenamento).

### Bot Telegram
- Telegram bot API: gratuito.
- Custo indireto: hosting do script que chama bot.

### Backup remoto
- No proprio site: custo zero se ja incluido; senao, storage por GB.
- Em provedor (B2, S3, R2): storage + egresso — TODO/RESEARCH.

### Claude Code + MCPs
- Plano atual ja cobre (provavel).
- MCPs externos autenticados (Amplitude, Linear, etc.): nao utilizados neste projeto.

## Fontes NAO aplicaveis nesta rodada
- OpenAI / Gemini / modelos extras.
- CDN premium.
- Servicos de analytics pagos.

## Classificacao de gastos
| Categoria | Impacto | Prioridade de economizar |
|-----------|---------|--------------------------|
| Modelos LLM | alto variavel | alta (uso inteligente Opus/Haiku) |
| Hospedagem | baixo fixo | baixa |
| DB | medio variavel | media |
| Backup | baixo | media |
| Bot Telegram | zero | nao aplica |

## Classificacao: Conhecido vs TODO/RESEARCH

| Item | Status | Detalhe |
|------|--------|---------|
| Dominio stemmia.com.br | Conhecido (ja pago) | Custo zero adicional |
| Telegram bot API | Conhecido (gratuito) | Zero custo de API |
| SQLite local | Conhecido (zero custo) | Apenas armazenamento local |
| JSON files local | Conhecido (zero custo) | Ja em uso (FICHA.json) |
| Claude Code plano atual | Presumido coberto | [TODO/RESEARCH: confirmar se plano atual inclui uso previsto] |
| Claude API Opus 4.7 por token | TODO/RESEARCH | Preco por token de entrada/saida nao consultado |
| Claude API Sonnet/Haiku por token | TODO/RESEARCH | Idem |
| Hospedagem atual stemmia.com.br | TODO/RESEARCH | Compartilhada? VPS? Serverless? Plano? |
| Supabase free tier limites | TODO/RESEARCH | Linhas, storage, requests/mes — nao verificado |
| Supabase pago | TODO/RESEARCH | Preco por plano — nao verificado |
| VPS para Postgres self-hosted | TODO/RESEARCH | Preco por mes, provedor nao escolhido |
| Backup remoto (B2/S3/R2) | TODO/RESEARCH | Storage + egresso — nao calculado |
| Hosting script bot Telegram | TODO/RESEARCH | Onde rodar o polling script |

## O que decidir depois
1. Adotar Opus via API? (economia ou gasto?)
2. Supabase pago ou self-hosted?
3. Storage de backup?

Todos no backlog (B004, B005).
