---
titulo: Como um LLM funciona
bloco: 08_ai_and_automation
tipo: fundamento
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: tecnico-consolidado
tempo_leitura_min: 6
---

# Como um LLM funciona

## Token

Unidade mínima processada. Não é palavra nem letra. Tokenizador (BPE, SentencePiece) quebra texto em pedaços estatisticamente frequentes. "laudo pericial" pode virar 3 tokens; "hepatocarcinoma" pode virar 5. Modelos Claude usam tokenizador próprio; estimativa prática: 1 token ≈ 4 caracteres em português, ≈ 0,75 palavra. Todo custo (entrada/saída) é cobrado em tokens.

## Next-token prediction

O LLM faz UMA coisa só: dado um prefixo de tokens, prever a distribuição de probabilidade do próximo token. Em inferência, amostra um token dessa distribuição, concatena ao contexto, repete. Não há "pensamento" — há bilhões de passos desse loop. Tudo que o modelo "sabe" está comprimido nos pesos que moldam essa distribuição. Por isso raciocínio complexo exige chain-of-thought: gerar os passos explicitamente no contexto, porque só o que está no contexto pesa na próxima predição.

## Embedding

Cada token vira um vetor (tipicamente 4096 a 12288 dimensões em modelos grandes). O embedding é a representação numérica da identidade semântica do token. Tokens com significados parecidos ficam próximos em distância coseno. A primeira camada da rede converte `id_token` em vetor via lookup numa matriz de embeddings; a última camada faz o inverso (vetor para distribuição sobre vocabulário). Embeddings de sentença (sentence-transformers, `text-embedding-3`) são derivados desse processo e servem para busca semântica (ver `vector_memory_rag/embeddings_e_similaridade.md`).

## Atenção

Mecanismo que decide, a cada posição, quais tokens anteriores pesam mais na previsão. Cada token gera três vetores: query, key, value. Dot-product entre query atual e keys anteriores gera pesos (softmax); soma ponderada dos values forma a nova representação contextual. Multi-head = várias "cabeças" de atenção em paralelo, cada uma focando em relações diferentes (sintática, correferencial, semântica). É o que permite o LLM resolver "o juiz anterior" ligando a referência ao nome certo 20 parágrafos atrás. Custo: O(n²) na janela — por isso janelas enormes (1M tokens) usam atenção esparsa ou truques de memória.

## Transformer bloco

Empilhamento de blocos (atenção + MLP + normalização + residual). Claude 3/4 tem dezenas a centenas de camadas. Cada camada refina progressivamente a representação: camadas baixas capturam morfologia/sintaxe, médias capturam semântica local, altas capturam raciocínio, intenção, estilo. O treino (pretraining + RLHF + constitutional AI na Anthropic) ajusta os pesos dessas camadas via gradiente descendente em trilhões de tokens.

## Implicações práticas para perícia

- Tudo que está fora do contexto NÃO existe para o modelo (daí RAG).
- Tudo que é gerado depende do que já foi gerado (daí instruções no início do prompt pesam).
- Não há memória entre chamadas; sessão = contexto atual + system prompt.
- "Alucinação" é predição de token plausível sem ancoragem factual — comportamento esperado, não bug (ver `limitacoes_do_llm.md`).

## Referências

- Vaswani et al., "Attention is All You Need", 2017. [TODO/RESEARCH: citar paper de arquitetura específica do Claude se publicado]
- Anthropic, "Core Views on AI Safety", 2023.
