---
titulo: Backup, Réplica e Migrations
bloco: 04_systems_architecture
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 5
---

# Backup, Réplica e Migrations

Três pilares de operação de banco. Sem eles: perda de dados, downtime alto, schema bagunçado.

## Backup

### Tipos

- **Lógico** (`pg_dump`, `mysqldump`) — SQL + dados em arquivo. Restauração: `psql < dump.sql`.
  - Prós: portável entre versões, legível, seletivo.
  - Contras: lento em TB, não captura estado consistente online sem `-F c` + `--serializable-deferrable`.

- **Físico** (`pg_basebackup`, snapshot de disco) — cópia binária dos arquivos. Mais rápido, casa com WAL/PITR.
  - Prós: rápido restaurar, permite PITR.
  - Contras: específico da versão, arquivo grande.

- **Continuous / PITR** (Point-In-Time Recovery) — base + archive dos WAL (write-ahead logs). Pode restaurar para qualquer segundo entre backups.

### Estratégia 3-2-1

- **3** cópias.
- **2** mídias diferentes.
- **1** offsite.

Ex: disco local + bucket S3 + outro provedor (Backblaze B2).

### Rotina Postgres

```bash
# dump diário comprimido
pg_dump -Fc -U postgres pericia > backup_$(date +%F).dump

# restaurar
pg_restore -d pericia backup_2026-04-22.dump
```

Automatizar via launchd/cron + sincronizar para bucket com `rclone` ou `aws s3`.

### Testar restauração

Backup não testado = backup imaginário. Mensal: restaurar em ambiente de teste, rodar queries de sanidade.

## Réplica

Cópia sincronizada do DB. Motivos:

1. **Alta disponibilidade (HA)** — primário cai → réplica assume (failover).
2. **Escala de leitura** — queries pesadas vão para réplica.
3. **Backup sem impacto** — dump feito na réplica.
4. **Analítica** — ETL de réplica sem travar produção.
5. **Geo-distribuição** — réplica perto do usuário.

### Modelos

- **Streaming replication (Postgres)** — réplica assina WAL. Síncrona (commit espera réplica) ou assíncrona (lag de milissegundos).
- **Logical replication** — replica por tabela, permite versão diferente. Bom para migração entre major versions ou entre DBs distintos.
- **Multi-master** — escrita em múltiplos nós (Postgres BDR, CockroachDB, Galera para MySQL). Complexo; conflitos.

### Failover

- Manual — operador promove réplica (`pg_ctl promote`).
- Automático — **Patroni** + etcd/Consul, **repmgr**, **Stolon**. Managed services (RDS, Supabase, Neon) fazem sozinhos.

### Lag

Monitorar lag da réplica (`pg_stat_replication.replay_lag`). Alerta se > X segundos.

## Migrations

Schema evolui; mudanças precisam ser versionadas, reproduzíveis, reversíveis.

### Ferramentas

- **Alembic** (Python / SQLAlchemy) — mais usada em Python.
- **Flyway** (Java / multi-DB) — simples, SQL puro ou Java.
- **Liquibase** (Java) — YAML/XML, potente, curva maior.
- **Prisma Migrate** (Node/TS).
- **Atlas** — declarativo moderno, multi-DB.
- **Django migrations** — nativo Django.
- **Ecto migrations** — Elixir.

### Fluxo Alembic

```bash
alembic init migrations
alembic revision -m "criar tabela processos" --autogenerate
alembic upgrade head     # aplica
alembic downgrade -1     # reverte última
```

Cada migration = arquivo Python com `upgrade()` e `downgrade()`, versionado em git.

### Regras de ouro

1. **Migrations são append-only em produção** — nunca editar migration já aplicada. Criar nova.
2. **Backwards compatible** — passo 1 deploy código tolerante a schema novo E velho; passo 2 migrar schema; passo 3 remover tolerância. Padrão expand-contract:
   - **Expand** — adicionar coluna nova nullable.
   - **Migrate** — código escreve nas duas; lê da nova.
   - **Contract** — remover coluna antiga.
3. **Testar em cópia de prod** — volume real pega problemas que dev com 100 linhas esconde.
4. **Migrations grandes em chunks** — `ALTER TABLE` em 100M linhas trava. Usar `CREATE INDEX CONCURRENTLY`, `ALTER TABLE ... NOT VALID` + `VALIDATE CONSTRAINT`.
5. **Separar DDL de DML** — DDL (alter schema) em migration; DML (atualizar dados) em job batch.

### Downtime-zero patterns

- **Renomear coluna** → adicionar nova, copiar dados, código escreve nas duas, parar de usar antiga, dropar.
- **Mudar tipo** → idem, coluna nova.
- **Remover coluna** → código parar de usar; depois de deploy, dropar.

## Para o sistema pericial

Configuração sugerida (Postgres na VPS ou SQLite local):

- **SQLite (fase atual)** — backup = copiar arquivo. Fazer via launchd 3x/dia para pasta backups + rclone para B2. Migrations: Alembic mesmo com SQLite, prepara para migrar.
- **Postgres (fase futura)** — réplica streaming em segunda VPS. `pg_dump` diário + PITR via WAL archive para B2. Failover manual (tráfego baixo, 10min downtime aceitável).

Migrations: Alembic desde o primeiro schema. Nomes descritivos (`add_prazo_to_processos`, não `revision_a1b2`).

## Armadilhas

- "Bancamos o SQL direto em produção" — mudanças não versionadas, não reproduzíveis.
- Backup na mesma máquina que DB. Fogo/ransomware acaba com ambos.
- Réplica usada para relatório; sem monitor de lag; relatório desatualizado.
- Migration irreversível (dropar coluna) sem backup — sem rollback.
- Schema divergente entre ambientes (dev ≠ stage ≠ prod). Sempre aplicar mesma sequência.
