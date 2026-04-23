---
titulo: Arquitetura em Camadas
bloco: 04_systems_architecture
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 5
---

# Arquitetura em Camadas

Modelo clássico para organizar código de aplicação monolítica. Separa responsabilidades em camadas verticais. Variantes: Layered, Clean Architecture (Uncle Bob), Hexagonal (Ports & Adapters), Onion.

## Quatro camadas padrão

```
┌─────────────────────────────────┐
│  Apresentação (HTTP, CLI, UI)   │  ← adaptadores de entrada
├─────────────────────────────────┤
│  Aplicação (casos de uso)       │  ← orquestra, transação
├─────────────────────────────────┤
│  Domínio (entidades, regras)    │  ← puro, sem framework
├─────────────────────────────────┤
│  Infra (DB, APIs externas, fila)│  ← adaptadores de saída
└─────────────────────────────────┘
```

Regra de ouro: **dependência aponta para dentro**. Domínio não importa HTTP, DB, nada de framework. Infra depende de domínio, nunca o contrário.

## Responsabilidades

### Apresentação

HTTP controllers, CLI commands, websocket handlers. Traduz input externo em chamada de caso de uso. Retorna resposta.

```python
# presentation/http/processos.py
@router.get("/processos/{numero}")
def obter(numero: str, caso_uso: ObterProcesso = Depends()):
    try:
        processo = caso_uso.executar(numero)
    except ProcessoNaoEncontrado:
        raise HTTPException(404)
    return ProcessoDTO.from_domain(processo)
```

### Aplicação (casos de uso)

Orquestra domínio + infra. Cada caso de uso = 1 classe/função (ex: `CriarLaudo`, `VincularProcessoAoPerito`). Define transação.

```python
# application/laudos/criar_laudo.py
class CriarLaudo:
    def __init__(self, repo: RepositorioLaudos, publicador: PublicadorEventos):
        self.repo = repo
        self.publicador = publicador

    def executar(self, dados: CriarLaudoDados) -> LaudoId:
        laudo = Laudo.novo(...)  # domínio valida
        self.repo.salvar(laudo)
        self.publicador.publicar(LaudoCriado(laudo.id))
        return laudo.id
```

### Domínio

Entidades, value objects, regras de negócio. Puro Python/TS/Java. Zero import de framework/DB.

```python
# domain/laudo.py
@dataclass
class Laudo:
    id: LaudoId
    numero_processo: NumeroCNJ
    perito_id: PeritoId
    conteudo: str
    entregue_em: datetime | None = None

    def entregar(self):
        if self.entregue_em:
            raise LaudoJaEntregue()
        self.entregue_em = datetime.now()
```

### Infra

Implementação concreta das interfaces definidas em domínio/aplicação. SQLAlchemy, HTTPX, boto3.

```python
# infra/db/repositorio_laudos.py
class RepositorioLaudosSQL(RepositorioLaudos):  # implementa interface
    def __init__(self, session): ...
    def salvar(self, laudo: Laudo): ...
    def buscar(self, id: LaudoId) -> Laudo | None: ...
```

## Inversão de dependência

Camada de aplicação define **interface** (port); infra fornece **implementação** (adapter). Tipagem estrutural (Python Protocol, Go interface implícita) ou explícita (TS interface, Java interface).

Benefício: trocar Postgres por SQLite, trocar email real por mock em teste, sem tocar no domínio.

## Estrutura de pastas

```
src/
  domain/
    laudo.py
    processo.py
    value_objects.py
  application/
    laudos/
      criar_laudo.py
      entregar_laudo.py
    processos/
      listar_processos.py
  infra/
    db/
    http/
    fila/
  presentation/
    http/
      routers/
    cli/
  composition/
    container.py   # injeta deps
    main.py
```

## Quando vale a pena

- Sistema com regras de negócio reais (não só CRUD fino).
- Testes de domínio rápidos (sem DB, sem HTTP).
- Probabilidade de trocar componente (banco, provedor de email).
- Time > 1 pessoa.

Overkill quando:
- Prototipagem.
- Script de automação.
- CRUD 100% sem regra.

## Alternativas

- **Active Record / anemic** — entidade tem `.save()` embutido. Simples, acopla domínio a ORM.
- **Clean Architecture** — 4+ camadas, exagero para time pequeno.
- **Hexagonal (Ports & Adapters)** — versão mais enxuta da Clean. Domínio no centro, adapters em volta.
- **Vertical Slice** — cada feature = pasta autocontida (controller + handler + validador). Menos abstração, ótimo em CQRS.

## Para o sistema pericial

Módulos já identificados: `processos`, `laudos`, `datajud`, `pje`, `notificacoes`.

Dentro de cada módulo, aplicar camadas. Exemplo `laudos/`:

```
laudos/
  domain/laudo.py            # entidade
  application/
    criar_laudo.py           # caso de uso
    entregar_laudo.py
  infra/
    repositorio_sql.py
  presentation/
    http/router.py
```

Integração DataJud → infra do módulo `processos`, com interface em `domain` (`FonteProcessos`). Swap fácil se DataJud quebrar e precisar fallback Escavador.

## Armadilhas

- Domínio importando SQLAlchemy = morte. Vira ORM puro.
- Casos de uso "gordos" fazendo HTTP direto = regra de negócio misturada com infra.
- DTO em todo lugar. Definir fronteiras claras (apresentação traduz entre DTO e domínio).
- Sobre-abstração. 3 interfaces para 1 implementação provável = ruído.
- Seguir Clean Architecture livro-texto em script de 200 linhas.
