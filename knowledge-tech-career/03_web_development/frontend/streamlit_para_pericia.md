---
titulo: Streamlit para Dashboard Pericial
bloco: 03_web_development
tipo: pratico
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 6
---

# Streamlit para Dashboard Pericial

Streamlit = framework Python que transforma script em web app. Ideal para dashboard interno, prototipagem rápida, visualização de dados periciais. Zero HTML/CSS/JS.

## Quando usar

Indicado para:
- Dashboard de processos (lista, filtros, detalhes).
- Visualização de métricas (quantos laudos no mês, tempo médio de resposta).
- Upload/processamento de PDF (laudos, intimações).
- Ferramenta interna usada por 1–5 pessoas.

Não indicado para:
- Site público com SEO.
- App com login multiusuário complexo (Streamlit tem `st.login` em alpha; autenticação séria pede outra stack).
- Interação em tempo real (chat, editor colaborativo).
- Mobile first (UI é desktop-pensada).

## Exemplo — dashboard de processos

```python
import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Dashboard Pericial", layout="wide")

@st.cache_data(ttl=300)
def carregar_processos():
    conn = sqlite3.connect("~/Desktop/STEMMIA Dexter/processos.db")
    return pd.read_sql("SELECT * FROM processos", conn)

df = carregar_processos()

st.title("Processos Periciais")

col1, col2, col3 = st.columns(3)
col1.metric("Total", len(df))
col2.metric("Ativos", (df["status"] == "ativo").sum())
col3.metric("Urgentes", (df["prazo_dias"] < 7).sum())

vara = st.sidebar.multiselect("Vara", df["vara"].unique())
if vara:
    df = df[df["vara"].isin(vara)]

st.dataframe(df, use_container_width=True)

processo = st.selectbox("Abrir processo", df["numero"])
if processo:
    linha = df[df["numero"] == processo].iloc[0]
    st.write(f"**Autor:** {linha['autor']}")
    st.write(f"**Réu:** {linha['reu']}")
```

Rodar: `streamlit run dashboard.py`. Abre em `http://localhost:8501`.

## Componentes essenciais

- `st.metric` — card de número grande.
- `st.dataframe` / `st.table` — tabela interativa.
- `st.plotly_chart` / `st.altair_chart` — gráficos interativos.
- `st.file_uploader` — upload de arquivo.
- `st.download_button` — baixar arquivo gerado.
- `st.form` — agrupar inputs, submit único.
- `st.sidebar` — filtros laterais.
- `st.tabs`, `st.expander`, `st.columns` — layout.

## Estado e cache

- `@st.cache_data` — cachear resultado de função (ex: query SQL).
- `@st.cache_resource` — cachear conexão/modelo (ex: cliente DataJud).
- `st.session_state` — estado entre reruns do script. Cada interação reexecuta o arquivo inteiro; `session_state` persiste.

## Limitações reais

- Reexecução completa a cada interação. Arquivos grandes ficam lentos. Mitigar com cache.
- Layout inflexível. Não dá para fazer UI customizada fora dos componentes nativos. Alternativa: `streamlit-elements` (MUI), componentes custom em React (curva alta).
- Autenticação nativa fraca. Usar reverse proxy (nginx + auth básica) ou `streamlit-authenticator` comunitário.
- Single-user por padrão. Cada usuário = uma sessão, mas não há multiusuário com papéis sem customização.
- Deploy: Streamlit Community Cloud (grátis, limitado), Docker próprio, Streamlit in Snowflake.

## Alternativas Python

- **Gradio** — foco em ML, interfaces simples (input→output).
- **Dash (Plotly)** — mais flexível, curva maior, baseado em Flask + React.
- **Panel (HoloViz)** — mais controle de layout, integra bem com Jupyter.
- **Shiny for Python** — port do Shiny R, reativo por design.
- **FastHTML** — HTMX + Python, HTML completo, muito leve.

## Para o Dr. Jesus

Dashboard pericial interno em Streamlit: decisão certa se o objetivo é VER dados rápido. Prototipar em 1 dia, usar por meses. Quando crescer para múltiplos usuários ou precisar mobile, migrar para FastAPI+SvelteKit.

Deploy sugerido: Docker na VPS do N8N (srv19105) com nginx reverse proxy + Basic Auth. Não expor em stemmia.com.br (WordPress fica na raiz).
