---
titulo: Escalabilidade Básica
bloco: 04_systems_architecture
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 7
---

# Escalabilidade Básica

Escalar = aguentar mais carga sem degradar latência ou disponibilidade. Antes de escalar, **medir o gargalo real** — CPU? Memória? I/O? Rede? Banco? Escala errada não resolve nada.

## Vertical vs Horizontal

### Escala vertical (scale-up)

Aumentar recursos da mesma máquina: mais CPU, RAM, disco NVMe.

Prós:
- Simples — sem mudar arquitetura.
- Sem consistência distribuída.
- Postgres/Redis escalam muito vertical (dezenas de cores, TB de RAM).

Contras:
- Teto físico.
- Custo cresce não-linear (máquina monstro custa muito mais que 10 médias).
- Single point of failure.

### Escala horizontal (scale-out)

Adicionar réplicas. Mais nós processam em paralelo.

Prós:
- Sem teto prático.
- Alta disponibilidade nativa (1 cai, outras absorvem).
- Custo linear (ou melhor).

Contras:
- Exige stateless na camada web (ou sessão externa, sticky session).
- DB distribuído é difícil.
- Consistência eventual em vários cenários.
- Operação complexa (k8s, service discovery, lb).

## Stateless e state

Regra: **camada web stateless**. Estado (sessão, cache, dados) em storage externo (Redis, Postgres). Qualquer réplica atende qualquer request.

Armadilhas:
- FS local — upload de arquivo num nó não existe no outro. Usar S3/GCS.
- Session em memória — usuário "desloga" ao ir para outro nó. Usar Redis/cookie assinado.
- Worker com estado — se fila é externa, workers são trocáveis.

## Cache — alavanca #1

Cache reduz hit no DB/API externa. Cada camada possível:

1. **Browser** — `Cache-Control: public, max-age=...` em assets.
2. **CDN** (Cloudflare, CloudFront) — cacheia respostas HTTP geograficamente.
3. **Reverse proxy** — Varnish, nginx `proxy_cache`.
4. **Application cache** — memória do processo (LRU em Python `functools.lru_cache`).
5. **Cache compartilhado** — Redis/Memcached.
6. **Query cache** — materialized view, cache de query.

Estratégias:
- **Cache-aside** — app lê cache; miss → consulta DB, grava cache.
- **Write-through** — escrita vai a cache + DB juntos.
- **Write-behind** — escrita no cache, flush async ao DB.
- **Refresh-ahead** — renova cache antes de expirar.

TTL e invalidação = problema difícil. "There are only two hard things in Computer Science: cache invalidation and naming things." Chaves de cache com versão em deploy (`v2:processos:123`) e eventos de invalidação ("processo 123 mudou → DELETE").

## CDN

Servir estáticos (JS/CSS/img) de PoP próximo ao usuário. Latência cai de 200ms (origem no sudeste) para 20ms (PoP em SP).

Cloudflare grátis cobre muito. Regras básicas:
- `Cache-Control: public, max-age=31536000, immutable` em assets com hash.
- Purgar em deploy (API Cloudflare).
- SSL automático (Let's Encrypt).

## Banco — onde mora o gargalo

Banco é quase sempre o gargalo final.

Otimizações:
1. **Índices certos** (ver `indexacao_e_query_plan.md`).
2. **Eliminar N+1** — usar JOIN ou select_related.
3. **Pool de conexões** — pgbouncer, pgcat. Evita "max connections exceeded".
4. **Read replicas** — queries de leitura na réplica.
5. **Sharding** — por user_id, por região. Último recurso.
6. **Cache de queries** — Redis na frente do Postgres.
7. **Materialized view** — agregações pré-calculadas.
8. **Partitioning** — tabela por mês/ano; drop rápido de dados antigos.

Regra: se query > 50ms, investigar. Se > 500ms, corrigir.

## Load balancing

Distribuir requests entre réplicas.

Algoritmos:
- **Round-robin** — alternado.
- **Least connections** — réplica com menos requests em andamento.
- **Consistent hashing** — mesmo cliente vai sempre para mesma réplica (ajuda cache local).
- **Weighted** — pesos diferentes por capacidade.

Ferramentas: nginx, HAProxy, Traefik, AWS ALB, Cloudflare Load Balancer.

Health check obrigatório — LB para de mandar request para réplica doente.

## Fila como amortecedor

Pico de requests > capacidade de processar → enfileirar. Fila absorve; workers processam conforme capacidade. Degradação graciosa: UI mostra "em fila, pronto em 2 min" em vez de 500 Internal Server Error.

## Autoscaling

Escala réplicas automaticamente pela métrica (CPU, RPS, fila pendente).

- **Kubernetes HPA** — baseado em CPU/mem ou custom metrics.
- **AWS ASG, Cloud Run** — cloud nativos.
- **Fly.io, Railway** — simples.

Cuidado: autoscaling sem DB preparado = escala app, mata banco.

## SLA / SLO

- **SLO** — "99.9% das requests < 500ms nos últimos 30 dias". Alvo mensurável.
- **Error budget** — (1 - SLO) = tempo permitido de erro. 99.9% → 43 min/mês.
- **SLA** — compromisso com cliente (geralmente contratual, externo).

SLO serve para **decidir prioridade**: estouro do budget → pausar features, focar em estabilidade. Budget sobrando → OK investir em features.

Google SRE book: alvo realista é ~99.9%; 99.99% é caro e raramente compensa sistema interno.

## 12 regras para escalar barato

1. Medir antes de otimizar (profiler, EXPLAIN).
2. Índice certo no DB.
3. Cache em Redis/CDN onde couber.
4. Async/fila para jobs lentos.
5. Paginação — nunca retornar 10k linhas.
6. Resposta HTTP comprimida (brotli/gzip).
7. Assets com hash e cache imutável.
8. Imagens otimizadas (WebP/AVIF, tamanhos responsivos).
9. HTTP/2 ou HTTP/3.
10. Read replica para analytics.
11. Health check em tudo + LB inteligente.
12. Observabilidade desde o dia 1.

## Para o sistema pericial

Escala atual: 1 usuário (Dr. Jesus), tráfego baixíssimo. Foco **não é capacidade**, é **confiabilidade** + **baixo custo operacional**.

Recomendações:
- Vertical (VPS srv19105 já existente; se apertar, subir plano).
- **Cache Redis** na frente de DataJud — processo consultado 1x/hora, não 50x.
- Paginação em listas grandes (futuro: 1000+ processos).
- Postgres pool (pgbouncer) se migrar de SQLite.
- Cloudflare na frente do stemmia.com.br (grátis) — cache + DDoS + TLS.
- Healthcheck em todo launchd → Telegram.

Quando escalar horizontal: só se virar produto multi-perito SaaS.

## Armadilhas

- "Prematura optimization is the root of all evil" — escalar para tráfego hipotético.
- Cache muito agressivo sem invalidação = usuário vê dado velho.
- Scale-out com session em memória = bug intermitente.
- DB único como gargalo final ignorado até cair.
- Infra elástica com DB fixo pequeno = app escala, banco trava.
