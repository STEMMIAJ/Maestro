# Agent Teams Playbook — 3 prompts para disparar em 1 mensagem

**Uso:** cole os 3 blocos abaixo como 3 chamadas `Agent` tool na **mesma mensagem** para rodar em paralelo. Claude do orquestrador deve disparar os 3 sem perguntar, depois consolidar os outputs e executar Fases 3.2-3.4 + 4.2-4.3 sequencialmente.

---

## PRÉ-REQUISITO

Antes de disparar, substitua os placeholders no bloco **CONFIG**:

```yaml
CONFIG:
  origem: "Governador Valadares"        # cidade origem (default)
  uf_origem: "MG"
  destinos_arquivo: "/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/guia-tjmg-classificador/data/contatos_completo.json"
  destinos_filtro: 'tipo=="comarca"'     # ou "subsecao_jf" etc
  total_esperado: 298                    # para validação
  raio_km_filtro: 230                    # consumidor downstream
  ibge_uf: "MG"                          # para Time B
  ibge_cod_prefixo: "31"                 # prefixo IBGE da UF
```

---

## TIME A — Medidor Maps (general-purpose, 20-45 min)

```
Você é o Time A — medidor de distâncias via Google Maps headless.

## CONFIG
- Origem: {{origem}}, {{uf_origem}}
- Destinos: ler {{destinos_arquivo}}, filtrar {{destinos_filtro}}
- Total esperado: {{total_esperado}} destinos

## ANTES DO CÓDIGO

1. Ler /Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json filtrando tecnologia=="playwright". Citar IDs no código como comentário.

2. Verificar Playwright:
   python3 -c "import playwright; print(playwright.__version__)"
   Se não: pip install playwright && python3 -m playwright install chromium

## FASE 0 — RECONHECIMENTO DOM

Criar /tmp/sonda_maps.py que:
- Abre URL headless: https://www.google.com/maps/dir/?api=1&origin={{origem}}+,+{{uf_origem}},+Brazil&destination=Belo+Horizonte,+MG,+Brazil&travelmode=driving
- UA: Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 Safari/605.1.15
- Flags: --disable-blink-features=AutomationControlled
- Viewport: 1440x900
- wait_for_load_state('networkidle', 20000) + 3s
- Screenshot em logs/sonda_maps_ANCHOR.png
- Busca DOM por regex \d+\s*km, captura seletor estável
- Salva logs/reconhecimento_dom.md com seletor + regex + valor esperado

## FASE 1 — SCRIPT + 5 ÂNCORAS

Criar /Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/distancias-gv/distancias_gv_maps.py com:
- CLI: --cidades csv OR --todas --max N --origem "..."
- asyncio + Playwright Chromium headless
- 3 pages concorrentes (Semaphore)
- Delay randômico 2-5s entre goto
- Cache crash-safe em cache/maps_gv.json (write + flush + fsync por cidade)
- Retry backoff [3, 10, 30]
- Log JSONL em logs/maps_run.jsonl
- Normalização nome: lower + NFD + strip diacriticos
- Detecção captcha (keyword "recaptcha"): pausar 60s

Rodar com 5 âncoras conhecidas para a origem configurada. Validar km na faixa esperada.

## FASE 2 — SCALE {{total_esperado}}

- Filtrar destinos do JSON de contatos
- Rodar com --todas (cache pula as 5)
- Monitorar fail_ratio: se >10% em 20 consecutivas → pausar 10 min, reduzir para 2 pages + delay 5-10s
- Lotes de 50 com pause 5 min entre lotes

## SAÍDA

- output/distancias_gv_v2.json (array, schema: cidade, km, min_total, status, fonte_km, tentativas, timestamp)
- output/distancias_gv_v2.csv
- output/distancias_gv_v2.html

## RELATÓRIO FINAL (<400 palavras)

1. Hora inicio/fim/total
2. Fase 0: seletor escolhido + 1 linha
3. Fase 1: tabela 5 âncoras com km_v2 vs esperado
4. Fase 2: total/OK/fail/captcha
5. Caminhos dos 3 arquivos gerados
6. Bloqueios
7. Próxima ação

NÃO modifique distancias_gv.py antigo. NÃO modifique comarcas_proximas_gv.py. NÃO pergunte.
```

---

## TIME B — Download IBGE (general-purpose, 5-10 min)

```
Você é o Time B — download de estimativa populacional IBGE.

## CONFIG
- UF: {{ibge_uf}} (cod_prefixo {{ibge_cod_prefixo}})
- Ano: 2024 (ou último disponível)

## FONTES (em ordem)

1. SIDRA API REST:
   https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/2024?formato=json
   - Filtrar por prefixo {{ibge_cod_prefixo}} no código IBGE D1C
   - Estrutura: lista com header na primeira linha, depois registros com D1N (nome), V (valor)

2. FTP IBGE (fallback):
   https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2024/
   - arquivo .xls → converter com pandas.read_excel

3. Portal HTML (último recurso)

## OUTPUT

/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/distancias-gv/data/populacao_{{ibge_uf|lower}}_2024.json

Schema:
{
  "fonte": "IBGE SIDRA tabela 6579",
  "url": "<url usada>",
  "ano_referencia": 2024,
  "municipios": [
    {"codigo_ibge": "3127701", "nome": "...", "uf": "{{ibge_uf}}", "populacao": 263689},
    ...
  ]
}

## VALIDAÇÃO

- len(municipios) ≥ 850 (MG=853, SP=645, RJ=92, etc — ajustar)
- Todos os municipios com populacao > 0
- Cidade-canária: Belo Horizonte ~2.3M / São Paulo ~11M / Rio ~6M
- Menor cidade: Serra da Saudade (MG) ~800 hab

## RELATÓRIO (<150 palavras)

1. URL que funcionou
2. Total de municípios
3. Caminho exato do JSON + KB
4. Top-3 e bottom-3
5. Erros

Não fuzzy match. Não outros UFs. Não pergunte.
```

---

## TIME C — Auditoria script antigo (Explore, 5-10 min)

```
Você é o Time C — auditor do script antigo para identificar causa raiz de possíveis bugs.

## READ-ONLY — NÃO MODIFIQUE NADA

Se o seu ambiente permitir Write, salve relatório em logs/causa_raiz_v1.md. Se não permitir, entregue no chat.

## ARQUIVOS A LER

1. /Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/distancias-gv/distancias_gv.py
2. /Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/distancias-gv/output/distancias_gv.json (amostrar 20)
3. cache/geocode.json, cache/distancias.json, cache/localidades.json
4. README.md (se existir)

## CHECKLIST

1. Coordenadas origem hardcoded — bate com realidade?
2. Fonte de rota: OSRM? Distance Matrix? Haversine? Fallback?
3. Se OSRM: perfil /driving? URL encoding UTF-8? Dividir metros por 1000?
4. Geocode: Nominatim? Filtro UF? Homônimos tratados?
5. Para cidades suspeitas (amostra): coordenadas no cache batem com IBGE?
6. Cache antigo prefere valor corrompido sobre chamada nova?

## HIPÓTESES

| ID | Hipótese | Status esperado |
|---|---|---|
| H1 | Homônimo fora UF alvo | CONFIRMADA / NEGADA |
| H2 | Unidade trocada m×km | |
| H3 | OSRM rota linha reta | |
| H4 | Cache corrompido persistido | |
| H5 | Coordenadas origem erradas | |
| H6 | Usuário leu coluna errada | |

## OUTPUT

logs/causa_raiz_v1.md (~500 palavras):
- Diagnóstico em 1 linha
- Evidência (linha + snippet)
- Cidades afetadas (todas? subset? ninguém?)
- Tabela hipóteses com status
- Impacto (precisa refazer v2 inteiro?)
- Recomendação pro script novo

## RELATÓRIO (<200 palavras)

1. Causa raiz em 1 frase
2. Probabilidade (alta/média/baixa)
3. % estimado de registros errados
4. Recomendação pro Time A
5. Caminho do causa_raiz_v1.md

Não execute. Não modifique (exceção: o próprio causa_raiz_v1.md).
```

---

## Após os 3 times retornarem — sequência manual do orquestrador

1. **Validar outputs dos 3 times:**
   - Time A: `cache/maps_gv.json` com N entries, `output/distancias_gv_v2.json` existe.
   - Time B: `data/populacao_UF_2024.json` com N municípios.
   - Time C: `logs/causa_raiz_v1.md` com conclusão.

2. **Fase 3.2 — diff_v1_v2.py:**
   ```python
   import json, pandas as pd
   v1 = json.load(open("output/distancias_gv.json"))
   v2 = json.load(open("output/distancias_gv_v2.json"))
   # cidade | km_v1 | km_v2 | delta | classe (ok<10% | susp 10-30% | errado>30%)
   ```

3. **Fase 3.3 — switch consumidor:**
   ```python
   # guia-tjmg-classificador/comarcas_proximas_gv.py linha ~63
   DIST_JSON = PROJ_ROOT / "distancias-gv" / "output" / "distancias_gv_v2.json"
   ```

4. **Fase 4.2 — fuzzy match:**
   ```python
   from rapidfuzz import process, fuzz
   for m in populacao["municipios"]:
       match, score, _ = process.extractOne(m["nome"], contatos.keys(), scorer=fuzz.token_sort_ratio)
       if score >= 95:
           enriched[match] = {**contatos[match], "populacao": m["populacao"]}
   ```

5. **Fase 4.3 — score e CSV final:**
   ```python
   import math
   for row in enriched.values():
       row["score"] = (100_000 / max(row["km_v2"], 10)) * math.log10(row["populacao"] + 100)
   pd.DataFrame(enriched.values()).sort_values("score", ascending=False).to_csv("lista_priorizada_envio.csv")
   ```

6. **Entregar:** caminhos dos arquivos finais + top-30 visual no chat.

---

## Tempos observados (sessão-origem 2026-04-24)

| Fase | Tempo observado |
|---|---|
| 0 — Reconhecimento DOM | ~5 min |
| 1 — 5 âncoras | ~2 min |
| 2 — 298 sedes | em andamento (~20 min projetado) |
| 3 — Diff + switch | ~5 min |
| 4 — IBGE + merge | ~5 min (Time B paralelo) |

**Total esperado:** 30 min caminho crítico.
