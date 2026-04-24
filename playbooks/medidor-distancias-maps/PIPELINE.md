# PIPELINE — 5 Fases do medidor de distâncias Maps

**Tempo total típico:** ~30 min (caminho crítico) / até 75 min (pior caso com captcha).

---

## Visão geral do fluxo

```
┌─────────────────────────────────────────────────────────┐
│ ENTRADA: lista de cidades destino (CSV ou JSON)        │
│ + cidade origem (default: Governador Valadares, MG)    │
└───────────────────┬─────────────────────────────────────┘
                    │
         ┌──────────┴──────────┬──────────────────────┐
         │                     │                      │
         ▼                     ▼                      ▼
┌────────────────┐   ┌────────────────┐   ┌─────────────────────┐
│ TIME A (Maps)  │   │ TIME B (IBGE)  │   │ TIME C (Auditoria)  │
│ Fases 0+1+2    │   │ Fase 4.1       │   │ Fase 3.1 (paralelo) │
│ ~20 min        │   │ ~5 min         │   │ ~10 min             │
└────────┬───────┘   └────────┬───────┘   └─────────┬───────────┘
         │                    │                     │
         └────────┬───────────┴─────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│ MERGE (orquestrador) — Fases 3.2-3.4 + 4.2-4.3         │
│ - Gera diffs_v1_v2.md                                  │
│ - Switch consumidor para v2                            │
│ - Fuzzy match populacao_mg × contatos                  │
│ - Score: (100_000 / max(km,10)) * log10(pop + 100)     │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│ SAÍDA: lista_priorizada_envio.csv                      │
│ + distancias_gv_v2.json (confiável, validado)          │
│ + comarcas_ateXkm.html (consumidor atualizado)         │
└─────────────────────────────────────────────────────────┘
```

---

## Fase 0 — Reconhecimento DOM (5-15 min)

**Objetivo:** descobrir seletor Playwright estável para `\d+\s*km` no painel Maps.

**Entrada:** nenhuma.
**Saída:**
- `logs/reconhecimento_dom.md` — seletor escolhido + evidência
- `logs/sonda_maps_bh.png` — screenshot
- `logs/sonda_maps.json` — amostra DOM

**Ação:**
```python
# /tmp/sonda_maps.py
url = "https://www.google.com/maps/dir/?api=1&origin=Governador+Valadares,+MG,+Brazil&destination=Belo+Horizonte,+MG,+Brazil&travelmode=driving"
# Playwright headless, viewport 1440x900, UA realista macOS
# wait_for_load_state('networkidle', 20s) + 3s
# page.locator('div[role="radio"] :text-matches("\\d+\\s*km")').first
```

**Falhas catalogadas:** PW-018 (get_by_text invisível), PW-020 (wait_for trava), PW-010 (anti-bot).

**CKPT0:** `reconhecimento_dom.md` com seletor testado + screenshot. Sem isso → bloquear.

---

## Fase 1 — Script principal + 5 âncoras (10-20 min)

**Objetivo:** validar que o extrator funciona em 5 cidades de km conhecido.

**Âncoras (GV origem):**
| Cidade | km esperado |
|---|---|
| Belo Horizonte | 310-330 |
| Itajubá | 550-650 |
| Brazópolis | 570-670 |
| Uberaba | 600-700 |
| Conselheiro Pena | 25-35 |

**Script:** `distancias_gv_maps.py`

Estrutura mínima:
```python
# ref: PW-001 PW-007 PW-010 PW-018 PW-020 PW-030 PJE-002
import asyncio, json, os, random, re, unicodedata, urllib.parse
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

ORIGEM = "Governador Valadares"  # parametrizável via CLI
UF = "MG"
CACHE = Path(__file__).parent / "cache/maps_gv.json"
LOG = Path(__file__).parent / "logs/maps_run.jsonl"
SEMAPHORE_SIZE = 3  # 3 pages concorrentes
DELAY_MIN, DELAY_MAX = 2.0, 5.0

# ... launch chromium headless=True
# args: ['--disable-blink-features=AutomationControlled']
# user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15...'
# viewport: {'width': 1440, 'height': 900}

# Per-city:
# 1. urllib.parse.quote(cidade + ", MG, Brazil")
# 2. page.goto(url, wait_until='domcontentloaded', timeout=25000)
# 3. page.wait_for_selector(<seletor Fase 0>, timeout=20000)
# 4. texto = elemento.inner_text()
# 5. m_km = re.search(r'(\d+(?:[.,]\d+)?)\s*km', texto)
# 6. m_min = re.search(r'(?:(\d+)\s*h\s*)?(\d+)?\s*min', texto)
# 7. salva em cache com write+flush+fsync

# Retry: backoff = [3, 10, 30]
# Captcha: detectar "recaptcha" no HTML/title → status="captcha", pausar 60s
```

**Falhas catalogadas:** PW-001 (install chromium), PW-003 (click timeout), PW-007 (AJAX timeout), PW-010, PW-018, PW-020, PW-030 (unicode).

**CKPT1:** 5 cidades no `cache/maps_gv.json` com `status:"ok"` e km na faixa. Dr. Jesus confere 1 no celular.

---

## Fase 2 — Scale (17-45 min)

**Objetivo:** rodar em todas as N cidades destino.

**Entrada padrão:** 298 sedes de comarca TJMG (`contatos_completo.json` → `tipo=="comarca"`).
**Flag CLI:** `--todas` usa cache, não refaz as 5 da Fase 1.

**Monitoramento:**
- Taxa de erro >10% em 20 consecutivas → pausar 10 min, reduzir para 2 pages + delay 5-10s, retomar.
- Lotes de 50 com pause 5 min entre lotes (mitigação anti-bot).

**Saída:**
- `output/distancias_gv_v2.json` (array, schema compatível com consumidor v1)
- `output/distancias_gv_v2.csv` (colunas: `cidade, km, min_total, status, fonte_km`)
- `output/distancias_gv_v2.html`

**CKPT2:** ≥95% com `status:"ok"`. `jq type` retorna `"array"`.

---

## Fase 3 — Diff v1 × v2 + switch consumidor (5-10 min)

**Objetivo:** relatório de divergência + atualizar pipeline downstream.

**Tarefas:**
1. **3.1 Auditoria do script antigo** (Time C paralelo) — ler `distancias_gv.py`, identificar causa raiz dos bugs.
2. **3.2** Script `diff_v1_v2.py` gera `logs/diffs_v1_v2.md` com tabela `cidade | km_v1 | km_v2 | delta | classe`.
3. **3.3** Atualizar `guia-tjmg-classificador/comarcas_proximas_gv.py` linha 63:
   ```python
   # antes: DIST_JSON = PROJ_ROOT / "distancias-gv" / "output" / "distancias_gv.json"
   # depois: DIST_JSON = PROJ_ROOT / "distancias-gv" / "output" / "distancias_gv_v2.json"
   ```
4. **3.4** Regenerar `comarcas_ate230km_gv.html/csv` com v2.

**CKPT3:** `diffs_v1_v2.md` publicado; novo HTML sem cidades obviamente erradas.

---

## Fase 4 — População IBGE + score (5-30 min)

**Objetivo:** enriquecer com população e gerar lista priorizada.

**Tarefas:**
1. **4.1 (Time B paralelo)** — download IBGE SIDRA tabela 6579:
   ```
   https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/2024?formato=json
   ```
   Filtrar por prefixo `31` no código IBGE (MG). Salvar em `data/populacao_mg_2024.json` (853 municípios).

2. **4.2** Fuzzy match (RapidFuzz ≥95) entre nomes IBGE e chaves de `contatos_completo.json`.

3. **4.3** Gerar `output/lista_priorizada_envio.csv`:
   ```
   comarca, km_v2, min_v2, populacao_2024, email_admin, telefone, n_varas, entrancia, score
   ```

4. **4.4** Fórmula score (ajustável):
   ```python
   score = (100_000 / max(km, 10)) * math.log10(pop + 100)
   ```

**CKPT4:** CSV ordenado por score desc, top-30 = cidades próximas E populosas.

---

## Fase 5 — OUT OF SCOPE

Envio automatizado de emails (Gmail API, template jinja2, rate limit) — plano separado após Fases 0-4 validadas.

---

## Arquivos de configuração que mudam entre execuções

Para rodar com **outra origem** ou **outros destinos**:

| Variável | Onde mudar |
|---|---|
| Origem (ex: Belo Horizonte em vez de GV) | argumento CLI `--origem "Belo Horizonte"` |
| Lista de destinos | `--cidades-csv path.csv` ou `--contatos-json path.json` |
| Radius filter (se usar consumidor) | `comarcas_proximas_gv.py --raio N` |
| Score weights | editar fórmula na Fase 4.4 |

---

## Dependências

```bash
pip install playwright rapidfuzz httpx pandas openpyxl
python3 -m playwright install chromium
```

Playwright catalogado em `PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json` (PW-001 a PW-030).
