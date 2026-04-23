---
titulo: Plugin DJEN async com tenacity (backoff exponencial correto) e filtro de homônimo
tipo: evidencia
dominio: Python
subtopico: async/await + retry/backoff
nivel_demonstrado: 3
versao: 0.1
status: validada
ultima_atualizacao: 2026-04-23
fonte: /Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/monitor-processos-novo-2026-04-22/02-scripts/monitor/fontes/djen.py
---

## Descrição
Fonte do monitor de processos que consome a API pública DJEN (Diário de Justiça Eletrônico Nacional, CNJ)
de forma assíncrona com `httpx.AsyncClient`. Aplica retry com `tenacity` (wait_exponential 2–20s, 3
tentativas), itera 24 variações de grafia do nome do perito, pagina resultados com sleep entre páginas
e delega filtro de homônimo (irmão do Dr. Jesus) a `HomonimoFilter` — resolve o problema PW do
falso-positivo por sobrenome comum.

## Arquivo real
`/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/monitor-processos-novo-2026-04-22/02-scripts/monitor/fontes/djen.py`

## Habilidade demonstrada
- `Python.async/await` — 3 (AsyncClient + loop async + yield implícito via tenacity)
- `APIs.consumir REST` — 3 (paginação, User-Agent custom, content-negotiation, timeout)
- `Python.Playwright / Selenium` — N/A aqui (puro HTTP)
- `InfoSec.gestão de segredos` — 2 (sem credencial, fonte pública; User-Agent identificando perito)

## Trecho relevante
```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

ENDPOINT = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
USER_AGENT = "monitor-processos/0.1 (+perito medico judicial; stemmia)"

class Fonte(FonteBase):
    nome = "djen"
    tipo = "api"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=20))
    async def _pagina(self, client, termo, pagina, ini, fim):
        params = {
            "texto": termo,
            "dataDisponibilizacaoInicio": ini,
            "dataDisponibilizacaoFim": fim,
            "itensPorPagina": 100,
            "pagina": pagina,
        }
        r = await client.get(ENDPOINT, params=params,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            timeout=30)
        r.raise_for_status()
        return r.json()
```

## Data
2026-04-22 (pasta do sistema completo nova). Ativa.

## Validação externa
**Média** — parte de sistema com `pytest.ini`, `requirements.txt` e `tests/` (há testes — e.g. `test_export.py`). Evolução consciente do script ingênuo do descobrir_processos (dívida resolvida aqui).

## Limitações conhecidas
- Depende de `monitor.core.homonimos.HomonimoFilter` — se config de variações estiver vazia, pula tudo.
- Sem circuit breaker: se DJEN ficar offline 1h, re-tenta a cada execução.
- `score_min_confirmado=2` é heurístico (CRM-MG + sobrenome discriminante + tribunal).
