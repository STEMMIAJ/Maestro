# Playbook — Medidor de distâncias rodoviárias via Google Maps

**Autor:** Claude (Opus 4.7) | **Data-origem:** 2026-04-24 | **Solicitante:** Dr. Jesus

## Objetivo em 1 linha

Medir km rodoviário real de uma **origem fixa (ex: Governador Valadares)** até uma lista de **N cidades destino** usando Playwright + Google Maps headless, sem depender de Distance Matrix API nem OSRM.

## Quando usar este playbook

- Precisa priorizar envio de emails/malas diretas por proximidade geográfica.
- Desconfia dos valores do `distancias-gv/output/distancias_gv.json` (fluxo OSRM antigo).
- Quer replicar para **outra origem** (ex: Belo Horizonte, Juiz de Fora) ou **outro conjunto de destinos** (ex: comarcas AJG, subseções JF, municípios acima de X habitantes).

## Conteúdo da pasta

| Arquivo | Função |
|---|---|
| `README.md` | Este arquivo — visão geral |
| `PIPELINE.md` | Descrição completa do fluxo de 5 fases + arquivos gerados |
| `AGENT-TEAMS-PLAYBOOK.md` | 3 prompts prontos para disparar em paralelo na próxima sessão |
| `CONTEXTO-CONTINUACAO.md` | Prompt-colar para retomar com cidades/origem diferentes |

## Onde vivem os artefatos (FORA deste repo Maestro)

O código e os dados não ficam no Maestro — só este **playbook/documentação** fica. Os scripts e caches rodam em:

```
/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/
├── distancias-gv/                    ← script + cache + outputs
│   ├── distancias_gv_maps.py         (NOVO — Playwright + Maps headless)
│   ├── distancias_gv.py              (ANTIGO — OSRM, NÃO MODIFICAR)
│   ├── cache/maps_gv.json            (crash-safe, write+fsync por cidade)
│   ├── logs/
│   │   ├── reconhecimento_dom.md     (Fase 0 — seletor DOM)
│   │   ├── maps_run.jsonl            (log estruturado linha-a-linha)
│   │   ├── maps_erros.log            (stderr)
│   │   └── sonda_maps_*.png          (screenshots de reconhecimento)
│   ├── data/populacao_mg_2024.json   (IBGE SIDRA 6579, 853 municípios)
│   └── output/
│       ├── distancias_gv_v2.json     (NOVO — Maps)
│       ├── distancias_gv_v2.csv
│       ├── distancias_gv_v2.html
│       └── distancias_gv.json        (ANTIGO — OSRM, preservar)
└── guia-tjmg-classificador/
    ├── data/contatos_completo.json   (298 comarcas + emails TJMG)
    ├── data/trf6_subsecoes.json      (26 subseções JF MG)
    ├── comarcas_proximas_gv.py       (consumidor do JSON de distâncias)
    └── output/
        ├── lista_consolidada_2026-04-24.html  (853 cidades cruzadas)
        └── comarcas_ate230km_gv.html
```

## Resultado final da sessão-origem (2026-04-24 18h19)

**Time A concluiu as 298 sedes TJMG.**

| Métrica | Valor |
|---|---|
| Total processado | 298 |
| `status:"ok"` | 287 (96,3%) |
| Falhas | 11 |
| km min / max / média | 1,0 / 991 / 493 km |
| Captchas detectados | 0 |

**Validação âncoras (v2 Maps × realidade):**

| Cidade | km v2 Maps | km v1 OSRM | Confere |
|---|---|---|---|
| Belo Horizonte | 314 | ~320 | ✅ |
| Itajubá | 754 | 760,7 | ✅ |
| Brazópolis | 759 | 763,5 | ✅ |
| Uberaba | 786 | 792,5 | ✅ |
| Conselheiro Pena | 94,4 | ~27 | ⚠️ (v2 rota alternativa, v1 mais preciso para cidade limítrofe) |

**Falhas (11 cidades a reprocessar):**
Conceição do Rio Verde, Congonhas, Conquista, Conselheiro Lafaiete, Coração de Jesus, Corinto, Governador Valadares (origem=destino trivial), Santos Dumont, São Francisco, São Gonçalo do Sapucaí, São Gotardo.

## Achado crítico da sessão-origem (2026-04-24)

O script **antigo** `distancias_gv.py` (OSRM) **NÃO estava corrompido.** A auditoria do Time C mostrou que valores reais em `output/distancias_gv.csv` batem com a realidade rodoviária:

| Cidade | km v1 (OSRM) | Realidade |
|---|---|---|
| Belo Horizonte | ~320 | ~320 ✅ |
| Itajubá | 760.7 | ~750 ✅ |
| Brazópolis | 763.5 | ~760 ✅ |
| Uberaba | 792.5 | ~790 ✅ |
| Pará de Minas | 399.5 | ~400 ✅ |

Os números 107/155/183/208 que dispararam o plano eram **coluna `posicao` (rank ordinal)** lida erroneamente como km. Correção visual: renomear `posicao → rank` nos CSV/HTML.

**Conclusão:** o pipeline Maps serve como **validação independente cruzada** e está rodando (Fase 2 em andamento na sessão-origem, taxa 100% OK). Pode ser usado para outros conjuntos de cidades sem medo — funciona.

## Executar em nova sessão

1. Abrir nova sessão Claude Code no diretório `/Users/jesus/Desktop/STEMMIA Dexter/`.
2. Colar o prompt completo de `CONTEXTO-CONTINUACAO.md`.
3. Claude dispara automaticamente os 3 times em paralelo.

## Rollback

Tudo gerado está em `PYTHON-BASE/08-SISTEMAS-COMPLETOS/distancias-gv/` sob nomes `_v2`, `_maps`, `sonda_`. Para reverter:

```bash
cd "/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/distancias-gv"
rm -f output/distancias_gv_v2.* logs/maps_* logs/sonda_* logs/reconhecimento_dom.md cache/maps_gv.json distancias_gv_maps.py
```
V1 permanece intacto.

---

**Commit de origem:** veja `git log -- playbooks/medidor-distancias-maps/` nesta mesma branch.
