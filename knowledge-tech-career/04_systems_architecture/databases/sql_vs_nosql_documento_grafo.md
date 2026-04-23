---
titulo: SQL vs NoSQL vs Documento vs Grafo
bloco: 04_systems_architecture
tipo: comparacao
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 8
---

# SQL vs NoSQL vs Documento vs Grafo

Modelo de dados define o banco, não o contrário. Escolher pelo formato dos dados e dos acessos, não pela moda.

## Relacional / SQL (Postgres, MySQL, SQLite)

Dados em tabelas com schema rígido. Relacionamentos via chaves estrangeiras. ACID por padrão. SQL como linguagem de query.

Prós:
- Integridade referencial.
- Transações ACID.
- Joins eficientes.
- Consultas ad-hoc poderosas (agregações, window functions).
- Maduro (50 anos).
- JSON-B no Postgres: flexibilidade de documento onde precisar.
- Replicação madura, backup trivial.

Contras:
- Schema rígido (migração necessária).
- Escala horizontal difícil (sharding é complicado).
- Joins caros em volumes gigantes.

**Postgres** é o padrão-ouro 2026. Cobre 90% dos casos. Possui full-text search (`tsvector`), JSON-B, PostGIS, extensões (pgvector para embeddings, TimescaleDB para séries temporais).

**SQLite** para app local, single-writer, embarcado. Recente litestream/LiteFS permitem replicação.

## Documento (MongoDB, CouchDB, DynamoDB)

Documentos JSON/BSON aninhados. Sem schema rígido (opcional). Consulta por campo e índices.

Prós:
- Schema flexível (evolui sem migration).
- Modelo de dados casa com objetos (sem ORM).
- Aggregation pipeline poderoso.
- Escala horizontal (sharding nativo).

Contras:
- Relações duras (sem joins eficientes; fazer lookups = N+1 disfarçado).
- Sem ACID cross-document tradicional (Mongo 4+ adicionou, com limites).
- Duplicação de dados (desnormalizar = atualizar em vários lugares).
- Query rica pode exigir muito índice, memória.

Uso bom: catálogo de produtos, CMS, logs estruturados, perfis de usuário. Evento de log = documento por natureza.

## Chave-Valor (Redis, DynamoDB, Memcached)

`get(chave)` / `set(chave, valor)`. Ultra-rápido. Memória ou híbrido.

Prós:
- Latência submilisegundo.
- Cache, sessão, fila, lock distribuído, counters.
- Estruturas (Redis: list, set, sorted set, stream, hash).

Contras:
- Sem query rica (só por chave).
- Persistência opcional no Redis (RDB, AOF).

Redis = "faca suíça". Quase todo sistema tem.

## Grafo (Neo4j, ArangoDB, Amazon Neptune)

Dados são nós + arestas. Consultas percorrem relações.

Prós:
- Relacionamentos em vários níveis são baratos ("amigos de amigos de amigos").
- Modelagem natural para redes sociais, fraude, roteamento, ontologias.

Contras:
- Nicho — menor comunidade.
- Lento para consultas tabulares clássicas.
- Escala complexa.

Uso: detecção de fraude, rotas, recomendação, ontologia médica/jurídica (CID, termos). Para perícia: mapear relação entre processos/autores/advogados pode ser interessante — mas só se for pergunta frequente do sistema.

## Coluna (Cassandra, HBase, ScyllaDB)

Armazena por coluna, não por linha. Feito para escritas altíssimas distribuídas.

Uso: telemetria, time-series em escala web (Netflix, Spotify).

## Série temporal (TimescaleDB, InfluxDB, QuestDB)

Otimizado para dados com tempo como eixo principal. Compressão, downsampling, retenção automática.

Uso: métricas de servidor, IoT, cotações.

## Busca (Elasticsearch, OpenSearch, Meilisearch, Typesense)

Índice invertido para full-text. Relevância, facetas, suggest.

Uso: busca em catálogo, busca em documentos jurídicos, filtros de e-commerce.

## Vetorial (pgvector, Pinecone, Qdrant, Weaviate)

Embeddings (vetores densos) para similaridade semântica. Essencial para RAG/IA.

Uso: "buscar laudos similares ao processo atual" via embeddings.

## Matriz de decisão

| Dados / caso | Recomendação |
|-------------|--------------|
| CRUD geral com relações | **Postgres** |
| App local, single-user | **SQLite** |
| Cache / sessão / fila leve | **Redis** |
| Logs estruturados em escala | **Elasticsearch** ou **documento** |
| Busca semântica (RAG) | **pgvector** (Postgres) |
| Busca full-text em laudos | **Postgres tsvector** ou **Meilisearch** |
| Métricas do sistema | **Prometheus** (time-series) |
| Grafo de processos/partes | **Neo4j** (só se for pergunta central) |
| Séries temporais (monitor) | **TimescaleDB** |
| Perfil flexível com aninhamento | **Documento** (ou Postgres JSON-B) |

## Padrão 2026: "Postgres + Redis"

Realidade prática: **Postgres resolve quase tudo**. Adicionar Redis para cache/fila. Extensões cobrem busca vetorial, full-text, JSON, time-series. Um banco → uma conexão → uma ferramenta de backup. Evita complexidade polyglot.

Só adicionar outro banco quando Postgres não dá conta OU a ferramenta específica ganha muito.

## Para o sistema pericial

Modelagem:
- **Processos** — tabela relacional (número CNJ, autor, réu, vara, status). Postgres/SQLite.
- **Laudos** — tabela com FK para processo. Conteúdo em texto + metadados.
- **Movimentações** — tabela com FK, many-to-one.
- **Documentos (PDFs)** — metadados no DB, arquivo em FS/S3.
- **Cache DataJud** — Redis.
- **Busca em laudos antigos** — pgvector (embeddings) para "casos similares" + tsvector para busca por palavra.
- **Monitor** — pode escrever em SQLite local; sincronizar para Postgres central.

## Armadilhas

- Escolher Mongo "porque é moderno" e sofrer em cada join/join-like.
- Sharding prematuro — Postgres aguenta 100M+ linhas sem sharding.
- ORM pesado mascarando queries N+1. Ler SQL gerado, usar EXPLAIN.
- Usar DB como fila (polling de tabela). Redis/broker resolve melhor.
- Sem backup automático testado — backup só conta se restauração foi testada.
