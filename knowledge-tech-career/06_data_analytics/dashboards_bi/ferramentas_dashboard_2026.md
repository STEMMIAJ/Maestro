---
titulo: "Ferramentas de dashboard 2026 — Metabase, Superset, Grafana, Streamlit"
bloco: "06_data_analytics/dashboards_bi"
tipo: "comparativo"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "maduro"
tempo_leitura_min: 8
---

# Ferramentas de dashboard em 2026

Foco em **código aberto** ou gratuito, rodando local ou em VPS própria. Evita lock-in e mantém dado sensível (saúde, judicial) sob controle.

## Comparativo rápido

| Ferramenta | Alvo | Curva | Ponto forte | Ponto fraco |
|---|---|---|---|---|
| **Metabase** | Negócio / analista leve | Baixa | Setup 10 min, "perguntas" no-code | Limitado em visualizações customizadas |
| **Superset** | Analista / BI sério | Média | SQL Lab, Jinja templating, RBAC maduro | Deploy mais pesado (Docker + DB meta) |
| **Grafana** | Métricas time-series | Média | Alertas, painéis em tempo real | Tabelas/narrativa mais fracas |
| **Streamlit** | Python dev | Baixa p/ quem programa | Código Python puro, deploy 1 arquivo | Sem RBAC nativo, não é BI multi-usuário |

## Metabase

- **Quando usar**: perito que quer dashboard só para si + 2-3 pessoas da equipe. Liga direto em Postgres/MySQL/SQLite.
- **Deploy**: `docker run -p 3000:3000 metabase/metabase`.
- **Diferencial**: "Ask a question" (no-code), gráficos padrão bons, alertas por e-mail / Slack.
- **Limites**: cálculos complexos em SQL custom; templating fraco.

## Apache Superset

- **Quando usar**: BI sério com múltiplos datasets, RBAC por papel, templating SQL Jinja.
- **Deploy**: `docker compose` oficial, precisa metastore (Postgres).
- **Diferencial**: SQL Lab para exploração, mais de 40 tipos de gráficos, filtros globais robustos, integração com Druid/Presto.
- **Limites**: curva inicial mais íngreme, UI menos intuitiva que Metabase.

## Grafana

- **Quando usar**: observabilidade, monitor de processo (CPU, filas, latência de script), dados time-series (Prometheus, InfluxDB).
- **Deploy**: nativo em qualquer VPS; plugins para Postgres/MySQL/SQLite.
- **Diferencial**: **alertas** configuráveis por limiar, integração com Telegram/e-mail, painéis anelados e heatmaps temporais.
- **Limites**: relatórios longos e narrativos não são o forte; focar em séries temporais.

## Streamlit

- **Quando usar**: desenvolvedor Python quer dashboard rápido customizado 100%; não precisa de multi-usuário robusto.
- **Deploy**: `streamlit run app.py`; Streamlit Community Cloud (grátis) ou VPS.
- **Diferencial**: widgets Python, fácil integrar matplotlib/plotly, combina ML + visualização.
- **Limites**: re-executa script a cada interação (gerenciar estado com `st.session_state`); sem autenticação nativa (usar OAuth proxy).

## Alternativas adjacentes

- **Dash (Plotly)**: parecido com Streamlit, mais flexível e mais complexo.
- **Looker Studio** (ex-Data Studio): gratuito Google, fácil para dados em Sheets/BigQuery; cuidado com dado sensível.
- **Power BI Desktop**: gratuito localmente (Windows), pago para publicar. Boa experiência visual.
- **Tableau Public**: só para dashboards públicos; inadequado para dado pericial.
- **Evidence.dev**: markdown + SQL, gera site estático.

## Seleção para o caso Dexter (perícia)

1. **Metabase** para dashboard operacional (processos ativos, prazos, receita) ligado ao `pericia.db` (SQLite) ou Postgres local.
2. **Grafana** para monitor de pipelines (DJEN, DataJud, scrapers) — alerta quando falha.
3. **Streamlit** para ferramentas pontuais (calculadora de honorários, revisor de laudo com LLM).
4. **Superset** só se houver equipe ≥ 5 analistas e necessidade de governança.

## Checklist de segurança

- HTTPS obrigatório (Caddy/Nginx + Let's Encrypt).
- Autenticação (login Google/OIDC ou básica com 2FA).
- Rede privada (VPN/Tailscale) para acesso administrativo.
- Backup do metastore (Superset/Metabase perdem painéis se o banco-meta cai).
- Anonimizar dados de pacientes antes de subir para qualquer dashboard compartilhado.
