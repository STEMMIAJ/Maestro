---
titulo: N8N, Zapier, Make — comparação
bloco: 08_ai_and_automation
tipo: comparacao
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: pratica-consolidada
tempo_leitura_min: 5
---

# N8N, Zapier, Make — comparação

Três orquestradores visuais de automação (no-code / low-code). Todos conectam "triggers" a "actions" em nós encadeados. Diferem em preço, flexibilidade e autohospedagem.

## N8N

- **Self-hosted grátis** (Docker, VPS) ou cloud pago.
- **Open-source** (fair-code, license semi-livre).
- **Custom code nodes**: JavaScript e Python nativamente.
- **Sem limite de execuções** no self-hosted.
- **Nodes community**: ampla biblioteca, integra APIs esotéricas.
- **LangChain integrado**: nós para LLM, embeddings, vector store, agente.

Dr. Jesus já tem N8N self-hosted em `https://n8n.srv19105.nvhm.cloud` (reference_n8n_server.md).

**Forte em**: lógica complexa, controle total, privacidade, custo fixo.
**Fraco em**: curva de aprendizado maior, exige operar VPS.

## Zapier

- **SaaS puro**, sem self-hosted.
- **Mais integrações prontas** (6000+ apps).
- **Simplicidade máxima**: UX polida, triggers em 2 cliques.
- **Preço por task — Dado (2026-04-23):** fonte: https://zapier.com/pricing
  - Free: 100 tasks/mês, Zaps 2 steps.
  - Starter: **USD 19,99/mês** (anual) — 750 tasks, multi-step.
  - Professional: **USD 49/mês** — 2.000 tasks, apps premium exclusivos.
  - Team: **USD 69,50/user/mês** (anual) — 2.000 tasks compartilhadas.
  - Company: custom. Mensal custa 30–40% mais que anual. Cada task = 1 action executada.
- **Limite de multi-step** em planos baratos.

**Forte em**: rápido de montar, boa para gatilhos de SaaS comum (Gmail → Sheets → Slack).
**Fraco em**: caro em volume, lógica condicional complexa é desconfortável, sem código customizado real.

## Make (antigo Integromat)

- **SaaS**, visual tipo "grafo" (vs linha do Zapier).
- **Mais barato que Zapier em volume**.
- **Modules** ricos, suporta iteradores e arrays nativamente (Zapier sofre com isso).
- **Preço por crédito — Dado (2026-04-23):** Make migrou de operations para credits em ago/2025. 1 op comum = 1 crédito. Fonte: https://www.make.com/en/pricing
  - Free: 1.000 créditos/mês.
  - Core: **USD 10,59/mês** — 10.000 créditos, cenários ativos ilimitados.
  - Pro: **USD 18,82/mês** — execução prioritária, full-text search.
  - Extra credits: +25% sobre o preço-base (auto ou manual).
- Permite HTTP genérico, JSON parse, data manipulation.

**Forte em**: custo-benefício, manipulação de estruturas, visual intuitivo.
**Fraco em**: algumas integrações menos polidas que Zapier, sem self-hosted.

## Quando rodar custom Python

Nenhum dos três é melhor que Python puro quando:

- Lógica envolve muitos estados ou transações complexas.
- Precisa de bibliotecas científicas (pandas, NumPy, scikit, PyTorch).
- Performance importa (batch de 10k+ itens).
- Dado é sensível (LGPD, segredo de justiça) e não pode trafegar em SaaS externo.
- Integração com ferramentas caseiras (scripts Dexter, Selenium PJe, DataJud client).
- Custo de plano de automação > USD 50/mês e você domina Python.

O Dexter usa Python puro (`~/Desktop/STEMMIA Dexter/src/automacoes/`) + launchd + N8N self-hosted em paralelo. Cada um para o que é melhor.

## Tabela de decisão

| Situação | Escolha |
|----------|---------|
| Gmail → Sheets simples | Zapier ou Make (5 min) |
| Webhook → LLM → webhook | N8N (free, com node LLM) |
| Pipeline de perícia com 10+ passos, dados sensíveis | Python + launchd |
| Trigger por watch em pasta iCloud | Python + `fswatch` / launchd |
| Batch noturno de 500 processos | Python + N8N dispara o script |
| Fluxo visual para cliente não-dev | Make |
| Integrar PJe + DataJud + Telegram | Python (PJe-MCP) + N8N (Telegram) |

## Regra prática do Dexter

- Script determinístico local (download, verificação, backup) → Python + launchd.
- Orquestração com triggers externos e nós visuais → N8N.
- Nunca pagar Zapier em volume crescente — N8N paga 1/10.

## Pendente

- Validar novas features N8N v2 (agentes nativos, LangChain integrado) — checar CHANGELOG oficial.
- Testar n8n-mcp para controlar N8N via Claude.

## Referências

- N8N docs, Zapier pricing page, Make pricing page.
