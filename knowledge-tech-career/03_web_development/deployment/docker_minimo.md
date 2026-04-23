---
titulo: Docker Mínimo
bloco: 03_web_development
tipo: pratico
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 7
---

# Docker Mínimo

Docker empacota aplicação + dependências em **imagem**; roda como **container** isolado. Resolve "funciona na minha máquina". Padrão de deploy moderno.

## Conceitos

- **Imagem** — snapshot imutável (app + libs + SO mínimo). Tem camadas (cache).
- **Container** — instância rodando de uma imagem. FS efêmero por padrão.
- **Dockerfile** — receita para construir imagem.
- **Registry** — onde imagens moram (Docker Hub, GitHub Container Registry, GHCR).
- **Volume** — storage persistente fora do container.
- **Network** — bridge virtual entre containers.

Analogia: imagem = classe; container = instância.

## Dockerfile — FastAPI Python

```dockerfile
# estágio de build (opcional, para projetos compilados)
FROM python:3.12-slim AS base
WORKDIR /app

# deps primeiro (cache)
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev

# código depois (invalida cache só quando código muda)
COPY app/ ./app/

# usuário não-root
RUN useradd -m app && chown -R app:app /app
USER app

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build: `docker build -t pericia-api:0.1 .`
Run: `docker run -p 8000:8000 --env-file .env pericia-api:0.1`

## Boas práticas

- **Imagem base slim/alpine** — `python:3.12-slim` (~50 MB) vs `python:3.12` (~900 MB). Alpine é menor ainda, mas libc diferente (musl) quebra algumas libs com binários C.
- **Multi-stage** — estágio de build instala compiladores; imagem final copia só artefatos. Reduz MBs enorme.
- **COPY ordenado** — dependências antes de código. Alteração no código não invalida cache de deps.
- **`.dockerignore`** — excluir `.git`, `node_modules`, `__pycache__`, `.env`. Reduz contexto e evita vazar segredos.
- **Usuário não-root** — container rodando como root é risco.
- **Healthcheck** — `HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1`.
- **Tag versionada** — `:0.1.0`, não só `:latest`. Reprodutível.
- **Secrets via env/secret mount**, nunca COPY.

## docker-compose — múltiplos serviços

```yaml
# compose.yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [db, redis]
    volumes:
      - ./app:/app/app  # dev: bind mount para hot-reload

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: pericia
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports: ["5432:5432"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

volumes:
  pgdata:
```

Comandos:
```bash
docker compose up -d        # sobe tudo em background
docker compose logs -f api  # segue log do serviço
docker compose down         # derruba (volumes preservam)
docker compose down -v      # derruba E apaga volumes
```

## Comandos essenciais

| Comando | O quê |
|---------|-------|
| `docker ps` | containers rodando |
| `docker ps -a` | incluindo parados |
| `docker images` | imagens locais |
| `docker logs <id>` | log stdout/stderr |
| `docker exec -it <id> sh` | shell dentro do container |
| `docker stop <id>` | para graceful |
| `docker rm <id>` | remove container |
| `docker rmi <img>` | remove imagem |
| `docker system prune -a` | limpa tudo não usado |
| `docker stats` | CPU/mem ao vivo |

## Debugging

- App quebra no container mas funciona local: variável de ambiente faltando, path relativo, libc diferente (alpine).
- Container reinicia em loop: `docker logs` + verificar CMD.
- Muito pesado: `docker history <img>` mostra tamanho por camada.

## Registry

```bash
# Docker Hub
docker tag pericia-api:0.1 drjesus/pericia-api:0.1
docker push drjesus/pericia-api:0.1

# GHCR (GitHub)
docker login ghcr.io -u usuario
docker tag pericia-api:0.1 ghcr.io/drjesus/pericia-api:0.1
docker push ghcr.io/drjesus/pericia-api:0.1
```

## Para o sistema pericial

Candidatos a container na VPS srv19105:
- **FastAPI pericial** — imagem própria.
- **Streamlit dashboard** — `python:3.12-slim + streamlit`.
- **Postgres** — imagem oficial.
- **Redis** (cache de DataJud) — oficial.
- **nginx** (reverse proxy + TLS) — oficial.

Compose sobe tudo num arquivo. Backup = `pg_dump` em volume + sync para S3/Backblaze.

## Armadilhas

- `latest` em produção — deploy não reproduzível.
- Commitar `Dockerfile` com `pip install` sem pin de versão — build quebra em 6 meses.
- Logs em arquivo dentro do container — perde ao reiniciar. Logar para stdout.
- DB em volume local — sumiu = perdeu tudo. Backup fora.
- Executar como root — vulnerabilidade escapa host (historicamente várias CVEs).
- Ignorar camada/context size — push demora, CI lento.
