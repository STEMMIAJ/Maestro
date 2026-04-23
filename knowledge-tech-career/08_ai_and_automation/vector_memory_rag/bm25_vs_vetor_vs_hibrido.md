---
titulo: BM25 vs vetor vs híbrido
bloco: 08_ai_and_automation
tipo: comparacao
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: tecnico-consolidado
tempo_leitura_min: 4
---

# BM25 vs vetor vs híbrido

## BM25 (lexical / esparso)

Algoritmo clássico de busca (IR). Baseado em frequência de termos (TF-IDF refinado). Score considera:

- Frequência do termo no documento.
- Raridade do termo no corpus (IDF).
- Normalização pelo tamanho do documento.

Implementações: Elasticsearch, OpenSearch, Tantivy, `rank_bm25` em Python. Rápido, determinístico, interpretável.

**Forte em**:
- Termos exatos, siglas, códigos (CID M54.5, CNJ completo, nome de medicamento).
- Números, datas.
- Domínios com vocabulário estável.

**Fraco em**:
- Sinônimos ("dor lombar" vs "lombalgia").
- Paráfrase ("incapaz de trabalhar" vs "limitação para atividade laboral").
- Queries mal formuladas.

## Vetor (semântico / denso)

Embedding da query + similaridade coseno (ver `embeddings_e_similaridade.md`).

**Forte em**:
- Sinônimos, paráfrase.
- Conceito implícito ("trabalho pesado" recupera doc com "atividade braçal").
- Queries em linguagem natural, conversacional.

**Fraco em**:
- Termos muito específicos sem paráfrase ("M54.5" genérico; embedding pode confundir com outras lombalgias).
- Negação (mencionado acima).
- Ordem e estrutura fina.

## Híbrido

Combinar os dois. Duas estratégias principais:

### 1. Score ponderado

`score_final = α × score_bm25 + (1 - α) × score_vetor`

α tipicamente 0.3–0.5 (mais peso no semântico). Exige normalização dos scores (BM25 e coseno estão em escalas diferentes). Min-max ou z-score.

### 2. Reciprocal Rank Fusion (RRF)

Para cada documento, somar `1 / (k + rank_bm25) + 1 / (k + rank_vetor)`, com k ≈ 60. Não precisa normalizar score; usa só ranking. Robusto e simples.

Fórmula:
```
rrf(d) = sum_over_metodos( 1 / (k + rank_m(d)) )
```

## Por que híbrido costuma vencer

Trabalhos recentes (Microsoft, Google, Anthropic "Contextual Retrieval") mostram ganho de 10–30% em recall@10 vs qualquer método isolado.

Intuição: BM25 pega o "nome certo"; vetor pega o "conceito certo". Query real normalmente precisa dos dois.

Exemplo perícia:

Query: "jurisprudência sobre artrose L4-L5 incapacidade permanente trabalhador rural".

- BM25 dispara por "L4-L5", "artrose", "rural" exatos.
- Vetor dispara por "artrose", "incapacidade", "trabalho pesado" (paráfrase de "rural"), "limitação permanente".
- Híbrido (RRF) = união ranqueada → top-10 com melhor cobertura.

## Contextual Retrieval (Anthropic, 2024)

Passo adicional antes de indexar: prefixar cada chunk com 50–100 tokens de contexto gerado por Claude (sumário do documento + posição do chunk). Embedding fica mais rico; BM25 pega mais termos. Relato: reduz falha de recuperação em ~49% vs chunking puro. [TODO/RESEARCH: confirmar números no blog Anthropic]

## Quando usar cada

| Corpus / query | Escolha |
|----------------|---------|
| Corpus pequeno (<1k docs), queries estruturadas | BM25 puro basta |
| Corpus jurídico em PT, queries mistas | Híbrido RRF |
| Corpus técnico (papers médicos), query conversacional | Vetor + rerank |
| Logs, emails, conversas, queries ambíguas | Híbrido |
| Busca de CID, CNJ, número de lei | BM25 (ou filtro exato antes) |

## Ferramentas que fazem híbrido nativo

- **Qdrant**: suporte sparse + dense.
- **Weaviate**: hybrid search nativo.
- **Elasticsearch 8+**: kNN + BM25 na mesma query.
- **Vespa**: ranking híbrido complexo.
- **Chroma**: só denso; combinar manualmente com BM25 externo.

## Referências

- Robertson & Zaragoza, "The Probabilistic Relevance Framework: BM25", 2009.
- Anthropic, "Introducing Contextual Retrieval", 2024. [TODO/RESEARCH]
- Cormack et al., "Reciprocal Rank Fusion", 2009.
