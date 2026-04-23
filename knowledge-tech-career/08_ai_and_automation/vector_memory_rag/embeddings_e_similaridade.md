---
titulo: Embeddings e similaridade
bloco: 08_ai_and_automation
tipo: fundamento
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: tecnico-consolidado
tempo_leitura_min: 4
---

# Embeddings e similaridade

## Embedding

Vetor de números reais (floats) que representa um trecho de texto em espaço multidimensional. Dimensões típicas: 384, 768, 1536, 3072. Dois textos semanticamente próximos geram vetores próximos nesse espaço; dois textos sobre assuntos diferentes geram vetores distantes.

Embeddings são DIFERENTES de embeddings de token internos do LLM (aqueles alimentam a atenção; estes são output final de um modelo dedicado a representação de sentença).

## Modelos de embedding relevantes

- **OpenAI `text-embedding-3-small`**: 1536 dims, USD 0,02/milhão de tokens, multilíngue razoável.
- **OpenAI `text-embedding-3-large`**: 3072 dims, USD 0,13/milhão, melhor qualidade.
- **Sentence-transformers** (open-source):
  - `all-MiniLM-L6-v2`: 384 dims, rápido, inglês forte, PT mediano.
  - `paraphrase-multilingual-MiniLM-L12-v2`: 384 dims, multilíngue.
  - `BAAI/bge-m3`: 1024 dims, excelente em PT, open-source, roda local.
- **Voyage AI** (`voyage-2`, `voyage-law-2`): modelos especializados; `voyage-law-2` é treinado em texto jurídico. [TODO/RESEARCH: preços 2026]
- **Cohere embed-multilingual-v3**: 1024 dims, bom em PT.

Para perícia brasileira (texto médico + jurídico em PT): `bge-m3` local ou `voyage-law-2` se for usar API paga.

## Similaridade coseno

Métrica padrão. Fórmula:

`cos(A, B) = (A · B) / (||A|| × ||B||)`

Varia de -1 (oposto) a 1 (idêntico). Embeddings normalizados (`||A|| = 1`) reduzem para produto escalar — mais rápido.

Outras métricas: produto escalar (equivalente se normalizado), distância euclidiana (raramente usada em embeddings), distância de Manhattan (idem).

## Como são treinados

- **Contrastive learning**: modelo aprende a aproximar pares semanticamente similares e afastar pares distintos.
- **Dataset**: milhões de pares (pergunta, resposta), (parágrafo, resumo), (query, documento relevante).
- **Loss**: InfoNCE ou triplet loss.

## Chunking (preparação antes de embedar)

Texto longo é quebrado em pedaços (chunks) antes de embedar. Regras:

- Tamanho: 200–800 tokens por chunk. Muito pequeno = sem contexto. Muito grande = embedding diluído.
- Overlap: 10–20% entre chunks vizinhos para preservar contexto na borda.
- Chunking semântico (quebrar em parágrafo, seção) costuma vencer chunking por caracteres.
- Para laudo/processo: quebrar por seção (anamnese, exames, conclusão) faz mais sentido que por contagem fixa.

## Armazenamento

Vetores vão para banco vetorial:

- **Local**: FAISS, Chroma, LanceDB, SQLite + sqlite-vss.
- **Managed**: Pinecone, Weaviate Cloud, Qdrant Cloud, Supabase pgvector.

Para uso pessoal/perícia: Chroma ou LanceDB locais bastam. Sem custo, sem latência de rede, privacidade preservada (crítico para dado processual).

## Limitações

- Embedding é "bag of concepts" — perde ordem fina. "Autor pagou réu" e "réu pagou autor" podem ficar próximos.
- Negação é mal capturada ("incapaz" e "capaz" ficam similares em muitos modelos).
- Dependente do domínio de treino — modelo treinado em web genérica tem recall pior em jargão médico/jurídico.

Daí a importância de híbrido (ver `bm25_vs_vetor_vs_hibrido.md`).

## Referências

- Reimers & Gurevych, "Sentence-BERT", 2019.
- Anthropic docs: "Embeddings". [TODO/RESEARCH: URL]
- Voyage AI, docs `voyage-law-2`. [TODO/RESEARCH]
