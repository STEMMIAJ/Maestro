# FLUXO 06 — Jurisprudência e sentenças

## Objetivo

1. Buscar precedentes para fundamentar propostas, laudos e respostas a impugnações.
2. **Baixar sentenças do estado inteiro** (começando TJMG) e montar banco local por comarca.
3. Identificar laudos elogiados por juízes (alimenta fluxo 04).

## Passos (como funciona hoje)

1. Humano decide o tema (CID, tipo de ação, comarca, juiz específico).
2. Aciona orquestrador de busca (`orq-jurisprudencia`) ou roda script direto.
3. Busca em **3 camadas paralelas**:
   - Base local (Whoosh + SQLite) — rápida.
   - Tribunais (TJMG com captcha, STJ/STF/TST via MCP).
   - Acadêmico (PubMed, SciELO — só para fundamentação médica).
4. Consolida resultados em relatório.

## SCRIPTS EXISTENTES

### Sistema autônomo de jurisprudência
| Caminho | O que faz | Captcha? | Status |
|---|---|---|---|
| `/Users/jesus/stemmia-forense/src/jurisprudencia/` | **Pasta completa.** main.py + 6 módulos (harvester, classificador, similaridade, gerador_argumentos, relatorio). Cobre STJ, STF, TJMG, DataJud, Google Scholar | NÃO | FUNCIONA (tem RELATORIO-JURISPRUDENCIA.html gerado) |
| `.../jurisprudencia/utils/datajud_api.py` | Cliente API DataJud (CNJ) | NÃO | FUNCIONA |
| `.../jurisprudencia/utils/tribunal_api.py` | Wrappers STJ/STF/TJMG + Scholar + precedentes locais | NÃO | FUNCIONA |
| `.../jurisprudencia/data/jurisprudencia.db` | **SQLite 516 KB, ATIVO** (tem WAL/SHM = em uso) | — | FUNCIONA |

### Scrapers TJMG com captcha
| Caminho | O que faz | Captcha | Status |
|---|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/src/coleta-honorarios/coletor_tjmg_jurisprudencia.py` | Playwright persistent context. reCAPTCHA + 5 dígitos. Sessão salva após 1ª resolução manual | SIM (1ª vez) | FUNCIONA |
| `.../coleta-honorarios/baixar_tjmg_v3.py` | **v3: 1 captcha inicial, N comarcas em abas paralelas** | SIM (1×) | FUNCIONA |
| `.../coleta-honorarios/coletor_tjmg_v2.py` | v2 (anterior) | SIM | FUNCIONA |
| `.../coleta-honorarios/parsear_resultados_tjmg.py` | Parseia HTMLs baixados | NÃO | FUNCIONA |
| `.../coleta-honorarios/parsear_batch_sessao.py` | Parseia lote | NÃO | FUNCIONA |
| `.../coleta-honorarios/upgrade_parciais_inteiroteor.py` | Completa resultados parciais com inteiro teor | NÃO | FUNCIONA |
| `.../coleta-honorarios/_raw_html/` | 10 HTMLs brutos TJMG (4 comarcas capturadas 20260421) | — | DADOS |

### Agentes buscadores
| Caminho | Papel | Status |
|---|---|---|
| `/Users/jesus/stemmia-forense/agents/busca/buscador-base-local.md` | Base Whoosh local (primeira busca, rápida) | FUNCIONA |
| `.../busca/buscador-tribunais.md` | Busca online STJ/STF/TJMG | FUNCIONA |
| `.../busca/buscador-academico.md` | PubMed + SciELO (fundamentação médica) | FUNCIONA |
| `/Users/jesus/stemmia-forense/agents/pericia/orq-jurisprudencia.md` | Orquestra os 3 em paralelo | FUNCIONA |

### MCPs
| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/FERRAMENTAS/jurídicas/MCPs/brlaw_mcp_server/src/brlaw_mcp_server/domain/{stj,stf,tst}.py` | **MCP server** cobrindo STJ/STF/TST sem captcha | FUNCIONA |
| MCP `claude_ai_PubMed` | Busca médica oficial | FUNCIONA |

### Downloader STJ
| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/BANCO-DADOS/GERAL/_sistema/downloader/sources/jurisprudencia_stj.py` | Script STJ | FUNCIONA (tem .pyc compilado) |

## BANCOS LOCAIS

| Caminho | O que é | Tamanho / Status |
|---|---|---|
| `/Users/jesus/stemmia-forense/src/jurisprudencia/data/jurisprudencia.db` | SQLite principal jurisprudência | 516 KB, ATIVO (WAL) |
| `/Users/jesus/Desktop/STEMMIA Dexter/BANCO-DADOS/GERAL/` | **Índice Whoosh** do buscador-base-local | ATIVO |
| `/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/.indice_whoosh/` | Whoosh secundário (Banco-Transversal) | ATIVO |
| `/Users/jesus/Desktop/STEMMIA Dexter/FERRAMENTAS/pesquisador-honorarios/dados/honorarios.db` | SQLite honorários TJMG | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/banco-local/maestro.db` | SQLite de FICHA.json indexadas | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/legado/BUSCADOR-PERITOS/01-CODIGO-ATIVO/data/oportunidades.db` | Legado | LEGADO |

## PASTAS DE SENTENÇAS/DECISÕES BAIXADAS

| Caminho | Conteúdo aproximado |
|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/Banco-Transversal/Honorarios-Periciais/Casos-Reais/` | ~40 fichas TJMG (BH, GV, Norte Mineiro, Outros-MG) em FICHA.json + PDFs |
| `.../banco-de-dados/Estadual/` | Casos TJMG (PDF + FICHA.json), dezenas |
| `.../banco-de-dados/Federal/` | Casos TRF6 (PDF + FICHA.json), dezenas |
| `.../banco-de-dados/Banco-Transversal/Contestacoes/` | TRF1/TRF5 quesitos/contestações/impugnações (~6 PDFs anonimizados) |
| `/Users/jesus/Desktop/STEMMIA Dexter/src/coleta-honorarios/_raw_html/` | 10 HTMLs brutos TJMG (4 comarcas, 20260421) |
| `/Users/jesus/Desktop/STEMMIA Dexter/legado/BUSCADOR-PERITOS/02-INTEGRACAO-DATAJUD/` | `datajud_enriquecido.json`, `tjmg_pje_bruto.json` |

## Objetivo de longo prazo

1. **Estado inteiro TJMG** — iterar todas as comarcas no `baixar_tjmg_v3.py`.
2. **Banco por comarca** — consolidar em SQLite dedicado por região.
3. **Filtro "laudo elogiado"** — regex/NLP nas sentenças buscando elogio explícito.
4. **Integração com fluxo 04** — laudos elogiados → extrator de padrões → template novo.

## O que está FUNCIONANDO

- Busca em 3 camadas paralelas via `orq-jurisprudencia`.
- Banco SQLite jurisprudência ativo.
- Scraper TJMG v3 (captcha resolvido na 1ª, sessão persistente).
- MCP brlaw cobrindo STJ/STF/TST sem captcha.

## O que FALTA

- Coleta sistemática do estado inteiro (hoje só 4 comarcas em HTML bruto).
- Filtro automático de "laudo elogiado".
- Merge das 3 bases (jurisprudencia.db + honorarios.db + maestro.db) num índice único.
