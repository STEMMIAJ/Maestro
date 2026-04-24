# Scripts mapeados — FLUXO 06 (Jurisprudência e sentenças)

## Sistema autônomo de jurisprudência

Raiz: `/Users/jesus/stemmia-forense/src/jurisprudencia/`

| Arquivo | Função | Captcha | Status |
|---|---|---|---|
| `main.py` | Entry point | NÃO | FUNCIONA |
| `harvester/` | Coletor | NÃO | FUNCIONA |
| `classificador/` | Classifica decisões | NÃO | FUNCIONA |
| `similaridade/` | Busca por similaridade | NÃO | FUNCIONA |
| `gerador_argumentos/` | Gera argumentos de fundamentação | NÃO | FUNCIONA |
| `relatorio/` | Gera relatório HTML | NÃO | FUNCIONA |
| `utils/datajud_api.py` | Cliente DataJud CNJ | NÃO | FUNCIONA |
| `utils/tribunal_api.py` | Wrappers STJ/STF/TJMG + Scholar | NÃO | FUNCIONA |
| `data/jurisprudencia.db` | SQLite 516 KB ativo (WAL) | — | DADOS |

Há `descobrir_processos.py` também nessa raiz (duplicata do `src/pje/descoberta/`).

## Scraping TJMG (com captcha)

Raiz: `/Users/jesus/Desktop/STEMMIA Dexter/src/coleta-honorarios/`

| Arquivo | Função | Captcha | Status |
|---|---|---|---|
| `coletor_tjmg_jurisprudencia.py` | Playwright persistent context. reCAPTCHA + 5 dígitos | SIM (1ª) | FUNCIONA |
| `baixar_tjmg_v3.py` | **v3: 1 captcha inicial, N comarcas em abas** | SIM (1×) | FUNCIONA |
| `coletor_tjmg_v2.py` | v2 anterior | SIM | FUNCIONA |
| `parsear_resultados_tjmg.py` | Parseia HTMLs baixados | NÃO | FUNCIONA |
| `parsear_batch_sessao.py` | Parseia lote de sessão | NÃO | FUNCIONA |
| `upgrade_parciais_inteiroteor.py` | Completa parciais com inteiro teor | NÃO | FUNCIONA |
| `_raw_html/` | 10 HTMLs brutos TJMG (4 comarcas, 20260421) | — | DADOS |

## MCPs (sem captcha)

| Caminho | Tribunais | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/FERRAMENTAS/jurídicas/MCPs/brlaw_mcp_server/src/brlaw_mcp_server/domain/stj.py` | STJ | FUNCIONA |
| `.../brlaw_mcp_server/domain/stf.py` | STF | FUNCIONA |
| `.../brlaw_mcp_server/domain/tst.py` | TST | FUNCIONA |
| MCP `claude_ai_PubMed` | Medicina/fundamentação | FUNCIONA |

## Downloader STJ avulso

| Caminho | Função | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/BANCO-DADOS/GERAL/_sistema/downloader/sources/jurisprudencia_stj.py` | Downloader STJ direto | FUNCIONA (tem .pyc) |

## Monitor de publicações

| Caminho | Função | Status |
|---|---|---|
| `/Users/jesus/stemmia-forense/src/pje/monitor-publicacoes/dje_tjmg.py` | DJE TJMG | FUNCIONA |
| `.../monitor-publicacoes/datajud_api.py` | DataJud no monitor | DUVIDOSO |

## Bancos locais (dados, não scripts)

| Caminho | Tipo | Estado |
|---|---|---|
| `/Users/jesus/stemmia-forense/src/jurisprudencia/data/jurisprudencia.db` | SQLite | 516 KB, ATIVO (WAL/SHM) |
| `/Users/jesus/Desktop/STEMMIA Dexter/BANCO-DADOS/GERAL/` | Whoosh index | ATIVO |
| `/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/.indice_whoosh/` | Whoosh secundário | ATIVO |
| `/Users/jesus/Desktop/STEMMIA Dexter/FERRAMENTAS/pesquisador-honorarios/dados/honorarios.db` | SQLite | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/banco-local/maestro.db` | SQLite FICHAs | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/legado/BUSCADOR-PERITOS/01-CODIGO-ATIVO/data/oportunidades.db` | Legado | LEGADO |

## Pastas de sentenças/decisões baixadas

| Caminho | Aproximadamente |
|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/Banco-Transversal/Honorarios-Periciais/Casos-Reais/` | ~40 fichas TJMG (BH, GV, Norte Mineiro, Outros-MG) |
| `.../banco-de-dados/Estadual/` | Casos TJMG (PDF + FICHA.json), dezenas |
| `.../banco-de-dados/Federal/` | Casos TRF6 (PDF + FICHA.json), dezenas |
| `.../banco-de-dados/Banco-Transversal/Contestacoes/` | TRF1/TRF5 quesitos/contestações/impugnações (~6) |
| `/Users/jesus/Desktop/STEMMIA Dexter/legado/BUSCADOR-PERITOS/02-INTEGRACAO-DATAJUD/` | `datajud_enriquecido.json`, `tjmg_pje_bruto.json` |

## Agentes MD relacionados

| Caminho | Papel |
|---|---|
| `/Users/jesus/stemmia-forense/agents/busca/buscador-base-local.md` | Base Whoosh local |
| `.../busca/buscador-tribunais.md` | Busca online |
| `.../busca/buscador-academico.md` | PubMed / SciELO |
| `.../agents/pericia/orq-jurisprudencia.md` | Orquestra os 3 em paralelo |

## Lacuna

- Coleta sistemática do estado inteiro TJMG (hoje só 4 comarcas em HTML bruto).
- Filtro "laudo elogiado" — não existe.
- Índice único juntando jurisprudencia.db + honorarios.db + maestro.db.
