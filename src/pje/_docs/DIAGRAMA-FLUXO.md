# Diagrama do Fluxo Completo PJe

Representação ASCII de ponta-a-ponta: desde a varredura de fontes públicas até a intimação chegar
no bolso do Dr. Jesus. Atualizado em 2026-04-19.

---

## Visão geral

```text
   ┌────────────────────────────┐
   │  descobrir_processos.py    │   (src/pje/descoberta/)
   │  6 fontes em paralelo      │
   │  DJe + DataJud + PJe TJMG  │
   │  + Portal + DJEN + AJ/AJG  │
   └──────────────┬─────────────┘
                  │ produz 3 CSVs em consolidado/
                  │
                  ├─▶ PERITO_CONFIRMADO.csv   ──▶  [baixar_push_pje.py]   (Windows/Parallels)
                  │                                        │
                  ├─▶ INDETERMINADO.csv       ──▶  revisão manual do Dr. Jesus
                  │                                  (move para PERITO ou PARTE)
                  │
                  └─▶ DESCARTE_PARTE.csv      ──▶  arquivo (não tocar)
                                                          │
                                                          │ PDFs em
                                                          │ ~/Desktop/processos-pje-windows/
                                                          ▼
                                            ┌─────────────────────────────┐
                                            │  mapear_paginas_push.py     │  (src/pje/cadastro/)
                                            │  varre aba PUSH do PJe      │
                                            │  e gera mapa JSON dos CNJs  │
                                            │  já cadastrados             │
                                            └──────────────┬──────────────┘
                                                           │ mapa JSON em _mapa/
                                                           ▼
                                            ┌─────────────────────────────┐
                                            │  incluir_push.py            │  (src/pje/cadastro/)
                                            │  cadastra lote de CNJs      │
                                            │  via Playwright no PJe TJMG │
                                            └──────────────┬──────────────┘
                                                           │
                                                           ▼
                                    (intimações futuras passam a chegar
                                     no DJe / Comunica CNJ / PUSH do PJe
                                     e voltam pro topo do ciclo)
```

---

## Explicação de cada seta

### Seta 1 — `descobrir_processos.py` → 3 CSVs

`descobrir_processos.py` consulta 6 fontes em paralelo (ThreadPoolExecutor max_workers=6):

- **DJe TJMG** (jornal oficial): `fonte_dje_tjmg`
- **DataJud CNJ** (enriquecimento de metadados): `consultar_datajud_cnj`
- **PJe Consulta Pública TJMG**: `fonte_pje_consulta_publica`
- **Portal TJMG Unificado**: `fonte_portal_tjmg`
- **DJEN API CNJ** (comunicações unificadas): `fonte_comunica_pje`
- **AJ TJMG + AJG Federal** (com login): `fonte_aj_ajg` — opcional via `--com-browser`

Cada CNJ passa pelo `filtro_perito.py` (core/), que classifica em três buckets usando:

1. `auxiliaresDaJustica` == PERITO no DataJud → **PERITO_CONFIRMADO**
2. CNJ presente em `blacklist_manual.txt` → **DESCARTE_PARTE**
3. Resto (ambíguo) → **INDETERMINADO**

### Seta 2 — `PERITO_CONFIRMADO.csv` → `baixar_push_pje.py`

O script de download (rodado no Windows/Parallels pelo Chrome debug porta 9223) lê:

- A fila do PUSH direto do PJe TJMG
- O `PERITO_CONFIRMADO.csv` como fonte auxiliar para priorização

Para cada CNJ:

1. Consulta dedup em 3 camadas (`_CNJS_BAIXADOS_SESSAO`, `_DEDUP_INDEX`, conteúdo do PDF)
2. Clica "Autos Digitais" → "Download autos do processo"
3. Aguarda PDF completo (sem `.crdownload`)
4. Verifica CNJ na primeira página (detecta bug de cache do PJe)
5. Renomeia para `<CNJ>__<comarca>.pdf` e salva em `~/Desktop/processos-pje-windows/`

### Seta 3 — `INDETERMINADO.csv` → revisão manual

Lista curta (5-15 CNJs/dia tipicamente) que o Dr. Jesus revisa em 5 min:

- Se é processo dele como perito → move para `PERITO_CONFIRMADO.csv` manualmente ou roda descoberta com o CNJ forçado
- Se é processo dele como parte → adiciona CNJ ao `blacklist_manual.txt` (próxima descoberta descarta)

### Seta 4 — `DESCARTE_PARTE.csv` → arquivo

CSV de auditoria. Não entra no download nem no cadastro. Serve só como evidência de que o filtro
funcionou (rastreabilidade caso algo escape).

### Seta 5 — PDFs baixados → `mapear_paginas_push.py`

Antes de cadastrar, o `mapear_paginas_push.py` varre todas as páginas da aba PUSH do PJe e gera um
JSON com os CNJs que JÁ estão lá (`_mapa/push_atual.json` aprox.). Evita tentar cadastrar duplicata
(que retornaria erro visual do PJe).

### Seta 6 — Mapa JSON → `incluir_push.py`

`incluir_push.py` lê:

- `~/Desktop/STEMMIA Dexter/LISTA-COMPLETA-PUSH.json` (prioridade)
- Fallback: `~/Desktop/STEMMIA Dexter/AUTOMAÇÃO/lista-inclusao-push.txt`

Subtrai os já presentes no mapa JSON, cadastra só o delta. Para cada CNJ:

- Preenche campo `input[id*='numeroProcesso']`
- Clica `input[value='Incluir']`
- Lê resposta do PJe: `ok` / `duplicata` / `erro`
- Em erro: screenshot em `_analise-erros/erro_push_<CNJ>_<ts>.png`

### Seta 7 — Cadastro → intimações futuras

Após o cadastro, sempre que o processo tiver movimentação, o PJe dispara:

- **PUSH interno** (aba PUSH do painel do perito)
- **DJe TJMG** (diário oficial)
- **Comunica CNJ** (API DJEN, chega em dias úteis)

Esses canais são lidos na próxima rodada de `descobrir_processos.py`, fechando o ciclo de
monitoramento contínuo.

---

## Janela operacional

- **Descoberta:** qualquer hora (APIs públicas 24/7, exceto rate-limit da DJEN)
- **Download e Cadastro:** evitar 13h–19h (PJe TJMG instável). Guarda `janela_disponivel()` em
  `pje_verificacao.py` força pausa nesse período
- **Launchd agendado:** 21h diário para descoberta + relatório consolidado

---

Gerado em 2026-04-19 | Atualizar se uma seta mudar de significado.
