---
titulo: IA e Automacao
bloco: 08_ai_and_automation
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 08 — IA e Automação

## Definição do domínio

Cobre o que é necessário para usar LLMs e automações de forma técnica e responsável: fundamentos de modelos de linguagem, engenharia de prompt, sistemas de agentes (ferramentas, loop, estado), memória vetorial e RAG, seleção de modelo (custo, latência, capacidade), workflows de automação (N8N, scripts, hooks, cron) e práticas de avaliação e guardrails.

Não é bloco sobre "futuro da IA". É sobre operação: como medir se um prompt funciona, como versionar um agente, quanto um pipeline custa por rodada, como detectar regressão após troca de modelo, e como evitar que um agente execute ação destrutiva sem confirmação.

Aplicações imediatas: extração estruturada de laudos, triagem de processos, geração assistida de minutas, RAG sobre jurisprudência e literatura médica, automação do pipeline DJEN → análise → resposta.

## Subdomínios

- `llm_foundations/` — tokens, contexto, atenção, temperatura, top-p, custo, limitações intrínsecas (alucinação, contexto longo).
- `prompt_engineering/` — instrução de sistema, few-shot, chain-of-thought, estrutura, XML/JSON output, versionamento de prompt.
- `agent_systems/` — loop agente, tool use, planejamento, sub-agentes, orquestração (Claude Code, LangGraph, CrewAI).
- `vector_memory_rag/` — embeddings, vector DB (pgvector, Qdrant, Chroma), chunking, reranking, avaliação de RAG.
- `model_selection/` — trade-off custo/latência/qualidade, Opus vs. Sonnet vs. Haiku, modelos abertos (Llama, Qwen), local vs. API.
- `automation_workflows/` — N8N, cron/launchd, hooks Claude Code, webhooks, padrões de idempotência.
- `evaluation_guardrails/` — eval sets, regression test, LLM-as-judge, limites de ação, confirmação humana, anti-mentira.

## Perguntas que este bloco responde

1. Quando RAG resolve e quando fine-tune é necessário?
2. Como medir se um prompt novo é realmente melhor que o antigo?
3. Qual modelo usar para tarefa X considerando custo/qualidade?
4. Como evitar que agente apague arquivo sem confirmação?
5. O que é chunking e por que o tamanho quebra a recuperação?
6. Como versionar prompt como código?
7. Qual a diferença entre orquestração e coreografia de agentes?
8. Como construir eval set para agente pericial?

## Como coletar conteúdo para este bloco

- Documentação oficial Anthropic (docs.claude.com) e OpenAI.
- Papers: "Attention is All You Need", "Retrieval-Augmented Generation", "Constitutional AI", "Chain-of-Thought".
- Engineering blogs com métrica publicada (Anthropic, OpenAI, Mistral, LangChain).
- Context7 MCP para documentação de libs (já configurado).
- Livros: "AI Engineering" (Chip Huyen), "Building LLMs for Production".
- Casos internos: agentes do sistema pericial, relay Opus-auditor, hooks anti-mentira.

## Critérios de qualidade das fontes

Seguir `00_governance/source_quality_rules.md`. Campo instável: toda afirmação precisa data e versão de modelo. Preferir doc oficial e paper sobre Twitter thread. Benchmark sem eval set público descartado.

## Exemplos de artefatos que podem entrar

- Template de prompt com frontmatter (modelo, versão, eval score, data).
- Eval set de extração de laudo com gabarito.
- Diagrama de agente com tools, memória e guardrails.
- Comparativo Opus 4.7 × Sonnet × GPT-5 × Gemini em tarefa pericial real.
- Runbook do RAG jurisprudencial (ingestão, chunking, avaliação).
- Checklist de guardrail para agente com acesso a filesystem.

## Interseções com outros blocos

- `02_programming` — scripts e agentes consomem padrões de lá.
- `04_systems_architecture` — agentes e RAG têm arquitetura própria.
- `05_security_and_governance` — guardrails, segredos de API, dado sensível em prompt.
- `06_data_analytics` — eval, métricas, dashboards de custo e qualidade.
- `07_health_data` — RAG médico, extração de prontuário, apoio à decisão.
- `09_legal_medical_integration` — agentes para tarefa pericial e jurídica.
- `14_automation` — workflows operacionais são a aplicação concreta.
- `15_memory` — memória de longo prazo dos agentes vive lá.
