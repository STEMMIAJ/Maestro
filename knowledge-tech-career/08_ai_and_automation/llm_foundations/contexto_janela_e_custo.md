---
titulo: Janela de contexto e custo por token
bloco: 08_ai_and_automation
tipo: fundamento
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: tecnico-consolidado
tempo_leitura_min: 5
---

# Janela de contexto e custo por token

## O que é janela de contexto

Tamanho máximo, em tokens, que o modelo aceita de entrada + saída numa única chamada. É a "memória de trabalho". Nada fora dela existe para o modelo naquela inferência.

## Valores atuais (abr/2026) [TODO/RESEARCH: validar em docs oficiais]

- Claude Opus 4 / Sonnet 4 / Haiku 4: **200.000 tokens** (~150.000 palavras em PT).
- Gemini 2.5 Pro: **1.000.000 tokens** (experimental 2M).
- GPT-4.1: **1.000.000 tokens**.
- Llama 3.1 70B: **128.000 tokens**.

200k tokens ≈ 500 páginas de laudo; 1M ≈ um processo inteiro médio com anexos.

## Tokens de entrada vs saída

- **Entrada** (prompt + system + histórico + documentos anexados): mais barata.
- **Saída** (o que o modelo gera): 3 a 5x mais cara que entrada, porque cada token é gerado sequencialmente (custo computacional real).

Exemplo Claude Opus 4 [TODO/RESEARCH: validar tabela 2026]:

- Entrada: ~USD 15 / milhão de tokens.
- Saída: ~USD 75 / milhão de tokens.

Anexar 1 processo de 500k tokens = USD 7,50 só para o modelo "ler". Se vier 5 vezes num dia = USD 37,50 só em entrada. Por isso **prompt caching** (Anthropic cobra ~10% em cache hit) é decisivo para quem reusa o mesmo processo.

## Por que compactar importa

1. **Custo linear no tamanho da entrada**: texto redundante é dinheiro jogado fora.
2. **Qualidade cai com janela cheia** — "lost in the middle": modelos ignoram informação do meio de contextos muito longos. Benchmark needle-in-a-haystack mostra degradação acima de ~60% da janela.
3. **Latência**: 200k tokens de entrada demoram 10–40s só para processar antes do primeiro token de saída.
4. **Limite de rate**: planos Claude Max têm teto de tokens/minuto. Janela cheia = menos chamadas/dia disponíveis.

## Estratégias de compactação para perícia

- **RAG em vez de cola**: em vez de jogar o processo inteiro, buscar só os trechos relevantes (ver `vector_memory_rag/rag_minimo.md`).
- **Sumário hierárquico**: gerar sumário de cada peça uma vez, reusar.
- **Prompt caching**: marcar system prompt + documentos estáticos como cached; paga caro uma vez, 10% depois por 5 minutos.
- **Extração estruturada**: converter laudo contrário em JSON (quesitos, conclusões, contradições) uma vez; trabalhar em cima do JSON.
- **Sessões curtas**: cada nova pergunta em sessão nova com contexto mínimo relevante; não deixar histórico crescer indefinidamente.
- **Compactar em >80%**: regra do CLAUDE.md pessoal. Monitorar via `context_window.used_percentage` no statusLine.

## Regra prática

Para o perito: se o prompt passa de 50k tokens, provavelmente está errado. RAG + sumários resolvem 90% dos casos.

## Referências

- Liu et al., "Lost in the Middle: How Language Models Use Long Contexts", 2023.
- Anthropic docs: Prompt Caching. [TODO/RESEARCH: URL oficial atual]
