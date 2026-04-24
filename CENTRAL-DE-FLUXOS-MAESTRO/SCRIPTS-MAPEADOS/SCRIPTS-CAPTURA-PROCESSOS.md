# Scripts mapeados — FLUXO 01 (Captura de processos)

Todos apenas listados. **Nenhum rodado.**

## AJ TJMG / AJG CJF

| Caminho | Descrição | Status |
|---|---|---|
| `/Users/jesus/stemmia-forense/src/pje/consultar_aj.py` | Consulta AJ TJMG via Selenium | FUNCIONA |
| `/Users/jesus/stemmia-forense/src/pje/consultar_ajg.py` | Consulta AJG CJF via Selenium | FUNCIONA |
| `/Users/jesus/stemmia-forense/src/pje/sincronizar_aj_pje.py` | Cruza lista AJ com PJe | FUNCIONA |
| `.../monitor-processos-novo-2026-04-22/02-scripts/monitor/fontes/_deferred/aj_tjmg.py` | Adapter AJ TJMG (monitor novo, adiado) | RASCUNHO |
| `.../monitor-processos-novo-2026-04-22/02-scripts/monitor/fontes/_deferred/ajg_cjf.py` | Adapter AJG CJF (adiado) | RASCUNHO |
| `.../monitor-processos-novo-2026-04-22/02-scripts/monitor/fontes/_deferred/aj_jt.py` | Adapter AJ Justiça do Trabalho | RASCUNHO |
| `.../exemplos-reais/exemplo-2-monitor-pericial/adapters/aj_tjmg.py` | Exemplo consolidado | DUVIDOSO |
| `.../exemplos-reais/exemplo-2-monitor-pericial/adapters/ajg_cjf.py` | Exemplo consolidado | DUVIDOSO |

## DJEN / DJe / Comunica PJe

| Caminho | Descrição | Status |
|---|---|---|
| `.../monitor-processos-novo-2026-04-22/02-scripts/monitor/fontes/djen.py` | Fonte DJEN CNJ | FUNCIONA |
| `.../exemplos-reais/exemplo-2-monitor-pericial/adapters/djen.py` | Adapter DJEN (exemplo) | DUVIDOSO |
| `/Users/jesus/stemmia-forense/src/pje/monitor-publicacoes/dje_tjmg.py` | DJE TJMG estadual | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/legado/BUSCADOR-PERITOS/02-INTEGRACAO-DATAJUD/comunica_pje.py` | Comunica PJe legado | LEGADO |
| `/Users/jesus/Desktop/STEMMIA Dexter/_arquivo/PROJETOS CLAUDECODE/scripts/monitor-publicacoes/comunica_pje.py` | Comunica PJe arquivado | LEGADO |
| `/Users/jesus/Desktop/STEMMIA Dexter/_arquivo/Open/analisador-final/scripts/monitor-publicacoes/comunica_pje.py` | Cópia arquivada | LEGADO |

## DataJud (API CNJ)

| Caminho | Descrição | Status |
|---|---|---|
| `/Users/jesus/stemmia-forense/src/jurisprudencia/utils/datajud_api.py` | Cliente DataJud oficial | FUNCIONA |
| `/Users/jesus/stemmia-forense/src/pje/datajud_client.py` | Outro cliente DataJud | DUVIDOSO (tem `_analise-erros/`) |
| `/Users/jesus/stemmia-forense/src/pje/monitor-publicacoes/datajud_api.py` | DataJud no monitor publicações | DUVIDOSO (.bak 23/abr) |

## Descoberta de processos

| Caminho | Descrição | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/src/pje/descoberta/descobrir_processos.py` | Descobre CNJs novos | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/src/jurisprudencia/descobrir_processos.py` | Variante pasta jurisprudência | DUVIDOSO |
| `/Users/jesus/Desktop/STEMMIA Dexter/_arquivo/PROJETOS CLAUDECODE/scripts/descobrir_processos.py` | Arquivada | LEGADO |

## Projeto monitor consolidado (22/abr/2026)

Pasta inteira: `/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/monitor-processos-novo-2026-04-22/`

Handoff em `.../04-docs/HANDOFF.md`. Objetivo: unificar DJEN + filtro de homônimo (irmão). Status: parado.

## Agentes MD relacionados

| Caminho | Papel |
|---|---|
| `/Users/jesus/stemmia-forense/agents/pericia/orq-analise-rapida.md` | Orquestrador análise rápida |
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/clusters/extracao/extrator-partes.md` | Extrator de partes |
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/clusters/extracao/detector-urgencia.md` | Detector urgência |
