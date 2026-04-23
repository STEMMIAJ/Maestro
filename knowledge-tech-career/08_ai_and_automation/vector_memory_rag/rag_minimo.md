---
titulo: RAG mínimo
bloco: 08_ai_and_automation
tipo: receita
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: tecnico-consolidado
tempo_leitura_min: 5
---

# RAG mínimo

RAG = Retrieval-Augmented Generation. Em vez de colar o corpus inteiro no prompt (caro, degrada), buscar só os pedaços relevantes e injetar.

## Pipeline canônico: 4 estágios

### 1. Retrieve

Dada uma query (pergunta do usuário ou tarefa do agente), buscar os N chunks mais relevantes numa base indexada.

- Query vira embedding (mesmo modelo usado para indexar — obrigatório).
- Busca por similaridade coseno no banco vetorial.
- Retorna top-K (tipicamente K = 10–50).

### 2. Rank (rerank)

Reordenar os K candidatos com um modelo mais caro e preciso. Dois motivos:

- Embedding é aproximado; rerank cross-encoder compara query+chunk juntos (mais custo, mais precisão).
- Filtrar ruído: dos 50 recuperados, os 5 melhores são o que realmente vai ao prompt.

Ferramentas: Cohere Rerank, Voyage Rerank, BGE reranker open-source.

### 3. Augment

Montar o prompt final com os chunks selecionados:

```xml
<contexto_recuperado>
  <doc fonte="jurisprudencia_TJMG_2024_xxx" relevancia="0.89">
  {texto_chunk}
  </doc>
  <doc fonte="PubMed_PMID_12345678" relevancia="0.82">
  {texto_chunk}
  </doc>
</contexto_recuperado>

<pergunta>{query}</pergunta>

<task>
Responder usando APENAS o contexto recuperado. Se a resposta não estiver
no contexto, responder "não consta nas fontes disponíveis".
Citar a fonte (id) para cada afirmação.
</task>
```

Sempre manter o identificador da fonte para auditabilidade.

### 4. Generate

LLM responde. `temperature: 0`. Instrução clara de grounding (só usar o contexto).

## Exemplo concreto: buscar jurisprudência pericial

Cenário: perito precisa apoiar conclusão "incapacidade permanente em artrose L4-L5 moderada".

1. **Base indexada** (offline, uma vez):
   - Corpus: acórdãos TJMG + STJ + TST sobre artrose + incapacidade (10k docs).
   - Chunk por ementa + fundamentação (300 tokens, overlap 50).
   - Embedding com `voyage-law-2` ou `bge-m3`.
   - Metadata: tribunal, ano, classe, CNJ, CID mencionado.
   - Armazenar em Chroma local.

2. **Query em tempo real**:
   - Query: "artrose L4-L5 moderada incapacidade permanente 50 anos trabalhador braçal".
   - Filtro de metadata: `tribunal in ['TJMG', 'STJ']`, `ano >= 2020`.
   - Top 30 por coseno.

3. **Rerank** com cross-encoder: top 30 → top 5.

4. **Augment** com os 5 trechos + metadata completa.

5. **Generate**: Claude Opus produz fundamentação citando cada acórdão por CNJ.

6. **Verificar**: `verificador-de-fontes` do Dexter confere se cada citação existe e contém o texto reproduzido.

## Erros comuns

- **Usar modelo de embedding diferente no indexing e na query** → similaridade quebra. Mesmo modelo, mesma versão.
- **Chunk grande demais** (2000+ tokens) → top-K traz contexto diluído.
- **Chunk pequeno demais** (50 tokens) → sem contexto, modelo alucina preenchendo lacunas.
- **Não filtrar por metadata** → retorna jurisprudência irrelevante (outra vara, outro tema).
- **Não reranking** → top-10 do embedding puro traz ruído; LLM gasta tokens com chunk errado.
- **Colar chunks sem identificador** → saída sem rastreabilidade; não dá para auditar.
- **Retrievar com BM25 sozinho em domínio denso** → perde sinônimo.

## Quando NÃO usar RAG

- Corpus cabe inteiro na janela (< 50k tokens) E é usado uma vez → colar direto é mais simples.
- Query exige raciocínio agregado sobre TODO o corpus ("quantos acórdãos de 2023?") → RAG top-K não vê tudo. Use agregação estruturada ou SQL.

## Referências

- Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", 2020.
- Anthropic, "Contextual Retrieval", 2024. [TODO/RESEARCH: URL]
- LlamaIndex docs.
