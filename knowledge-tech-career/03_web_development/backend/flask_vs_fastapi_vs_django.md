---
titulo: Flask vs FastAPI vs Django
bloco: 03_web_development
tipo: comparacao
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 5
---

# Flask vs FastAPI vs Django

Três frameworks Python dominantes. Escolha depende de: tipo de projeto, async, bateria-incluída vs montagem própria.

## Flask (2010)

Microframework. WSGI (síncrono). Começa minúsculo, cresce com extensões.

```python
from flask import Flask, jsonify
app = Flask(__name__)

@app.get("/processos")
def listar():
    return jsonify([{"numero": "123"}])
```

Prós: curva mínima, flexível, ecossistema maduro, Jinja2 templates.
Contras: async em retrofit (2.0+ via ASGI adapter), sem validação embutida, monta tudo à mão (ORM, auth, admin).

## FastAPI (2018)

Framework async-first, tipado, OpenAPI automático. ASGI nativo.

Prós: async real, validação Pydantic, docs auto, performance, DX moderna.
Contras: jovem (menos tutoriais antigos), não tem admin/ORM próprio (usa SQLModel/SQLAlchemy+Alembic), sem templating integrado (mas aceita Jinja2).

## Django (2005)

Batteries-included. ORM próprio, admin, auth, migrations, templates, forms.

```python
# models.py
class Processo(models.Model):
    numero = models.CharField(max_length=25, unique=True)
    autor = models.CharField(max_length=200)
    vara = models.CharField(max_length=100)
```

Com `django-admin` e `python manage.py runserver` tem-se CRUD completo via admin.

Prós: produtividade enorme para CRUD + painel admin, ORM excelente, segurança padrão, comunidade grande, Django REST Framework (DRF) para APIs.
Contras: monolito opinativo, curva maior, async ainda parcial (views async OK, ORM async em evolução), overkill para API pequena.

## Matriz de decisão

| Necessidade | Flask | FastAPI | Django |
|-------------|:-----:|:-------:|:------:|
| API REST pequena/média | Bom | **Ótimo** | OK (DRF) |
| API com OpenAPI automático | — | **Ótimo** | DRF + drf-spectacular |
| Alta concorrência I/O | — | **Ótimo** | OK (parcial) |
| Admin panel grátis | — | — | **Ótimo** |
| CRUD rápido com DB | OK | OK | **Ótimo** |
| Site com templates | Bom | OK | **Ótimo** |
| ML/Data apps | OK | **Ótimo** | OK |
| Microserviços | Bom | **Ótimo** | — |
| Monolito grande corporativo | — | OK | **Ótimo** |
| Equipe júnior | **Ótimo** | Bom | OK |

## Performance (aproximada)

- FastAPI ~ 2–3x throughput de Flask em I/O-bound.
- Django sync ~ Flask sync.
- Diferença irrelevante abaixo de 100 req/s (gargalo será DB ou API externa).

## Ecossistema complementar

- **Flask** + SQLAlchemy + Flask-Login + Flask-Migrate + Marshmallow.
- **FastAPI** + SQLModel/SQLAlchemy + Alembic + python-jose + httpx.
- **Django** já vem com tudo; DRF para API.

## Para o Dr. Jesus

- **Dashboard pericial com admin (CRUD de processos, laudos, templates)** → Django. Admin grátis economiza semanas.
- **API para consumir DataJud + servir frontend SvelteKit** → FastAPI. Async ajuda nas chamadas paralelas.
- **Automação pontual com endpoint simples** → Flask. Um arquivo, sem overhead.

Combinação possível: Django para CRUD administrativo + FastAPI separado para API async de alto volume. Banco compartilhado (Postgres).

## Em declínio

- Flask como framework primário em projeto novo corporativo. FastAPI come o espaço.
- Django REST Framework tradicional — ainda vivo, mas OpenAPI/tipagem do FastAPI atrai mais.

## Ainda relevantes

Django para CMS, e-commerce (Django Oscar, Wagtail), admin interno pesado. FastAPI para microserviços, ML-serving, APIs modernas. Flask para scripts leves e legado.
