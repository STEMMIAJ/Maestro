---
titulo: Backend Python com FastAPI
bloco: 03_web_development
tipo: pratico
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 8
---

# Backend Python com FastAPI

FastAPI = framework web Python assíncrono, tipado, com OpenAPI automático. Padrão para APIs em 2026. Rápido (comparável a Go para IO-bound), curva suave.

## Por que FastAPI

- **Async nativo** — ASGI (Asynchronous Server Gateway Interface), permite I/O concorrente. Mil requests ao DataJud sem criar mil threads.
- **Type hints = validação** — Pydantic valida entrada/saída automaticamente.
- **OpenAPI grátis** — `/docs` gera Swagger UI; `/redoc` gera ReDoc; cliente pode ser gerado em qualquer linguagem.
- **Dependency injection** — `Depends()` para sessão DB, autenticação, etc.

## Stack mínima

```bash
pip install fastapi uvicorn[standard] pydantic
```

- `fastapi` — framework.
- `uvicorn` — servidor ASGI (roda o app).
- `pydantic` — validação (vem como dependência).

## ASGI vs WSGI

- **WSGI** (Flask, Django tradicional) — síncrono, 1 request = 1 thread bloqueada.
- **ASGI** (FastAPI, Starlette) — assíncrono, 1 thread atende milhares de conexões I/O-bound.

Quando chamar DataJud (I/O externo), ASGI ganha. Quando calcular CPU-bound (parse de PDF pesado), igual — mover para worker (Celery, RQ).

## Exemplo — endpoint que lista processos

```python
from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import date
from typing import Literal
import sqlite3

app = FastAPI(title="Pericia API", version="0.1.0")

class Processo(BaseModel):
    numero: str = Field(..., pattern=r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$")
    autor: str
    reu: str
    vara: str
    status: Literal["ativo", "suspenso", "arquivado"]
    prazo: date | None = None

def get_db():
    conn = sqlite3.connect("processos.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@app.get("/processos", response_model=list[Processo])
def listar(
    vara: str | None = None,
    status: Literal["ativo", "suspenso", "arquivado"] | None = None,
    limit: int = Query(50, ge=1, le=500),
    db: sqlite3.Connection = Depends(get_db),
):
    sql = "SELECT * FROM processos WHERE 1=1"
    params: list = []
    if vara:
        sql += " AND vara = ?"
        params.append(vara)
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += " LIMIT ?"
    params.append(limit)
    rows = db.execute(sql, params).fetchall()
    return [dict(r) for r in rows]

@app.get("/processos/{numero}", response_model=Processo)
def detalhe(numero: str, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT * FROM processos WHERE numero = ?", (numero,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return dict(row)
```

Rodar: `uvicorn main:app --reload`. Swagger em `http://localhost:8000/docs`.

## Validação Pydantic

Pydantic transforma type hint em validação runtime. `Field(..., pattern=...)` aplica regex. Se o cliente manda número fora do padrão CNJ, FastAPI responde 422 automaticamente com erro estruturado.

Modelos separados para entrada e saída:

```python
class ProcessoEntrada(BaseModel):
    numero: str
    autor: str
    reu: str

class ProcessoSaida(ProcessoEntrada):
    id: int
    criado_em: datetime
```

## Async real

```python
import httpx

@app.get("/datajud/{numero}")
async def consultar_datajud(numero: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://api-publica.datajud.cnj.jus.br/...")
        return r.json()
```

Várias chamadas em paralelo:

```python
import asyncio

async def buscar_varios(numeros: list[str]):
    async with httpx.AsyncClient() as client:
        tasks = [client.get(f"/processo/{n}") for n in numeros]
        respostas = await asyncio.gather(*tasks)
    return [r.json() for r in respostas]
```

## Autenticação básica — JWT

```python
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2 = OAuth2PasswordBearer(tokenUrl="token")
SECRET = "..."  # ler de env var

def usuario_atual(token: str = Depends(oauth2)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(401, "Token inválido")

@app.get("/me")
def me(user: str = Depends(usuario_atual)):
    return {"user": user}
```

## Estrutura de projeto

```
app/
  main.py          # cria FastAPI()
  routers/
    processos.py
    laudos.py
  models/          # Pydantic
  db/
    conn.py
  services/        # regra de negócio
  core/
    config.py      # settings via env
    auth.py
tests/
```

`app.include_router(processos.router, prefix="/processos", tags=["processos"])` em `main.py`.

## Deploy

- **Dev** — `uvicorn app.main:app --reload`.
- **Prod** — `uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000` atrás de nginx/traefik.
- **Container** — imagem `python:3.12-slim` + `uv` ou `pip`, `CMD uvicorn`.
- **Serverless** — AWS Lambda via Mangum, Cloud Run, Vercel Python.

## Armadilhas

- Função sync dentro de endpoint async bloqueia o loop. Usar `run_in_threadpool` ou virar async.
- Conexão SQLite em async = complicado. Usar `aiosqlite` ou `databases`.
- CORS — importar `CORSMiddleware` e configurar origens.
- Segredo hardcoded — sempre via `os.environ` ou `pydantic-settings`.
