# FLUXO 05 — Honorários

## Regra ferro

**Nunca misturar os dois mundos.**

1. **TABELA AJG (justiça gratuita)** — governo paga. Valor fixo pela portaria (TJMG 6607/2024, 7231/2025, TRF6 Res CJF 305, CSJT Res 66). **NÃO existe proposta.** Pode majorar até 5x com justificativa técnica.
2. **PROPOSTA (parte custeia)** — autor ou réu paga. Valor livre, fundamentado em complexidade + mercado + histórico. **Sujeito a impugnação e arbitramento.**

## Como decidir qual caminho (regra operacional)

1. Abrir FICHA.json do caso.
2. Procurar flag `justica_gratuita` ou ler petição inicial.
3. Se AJG/gratuidade deferida → **TABELA**. Rodar `pesquisar_honorarios.py --modo tabelas_oficiais`.
4. Se custeado → **PROPOSTA**. Rodar `pesquisar_honorarios.py --modo honorarios_coletados` + usar `aplicar_template.py` com template da classe.

## Base Taiobeiras (TABELA AJG)

6 processos de curatela, Vara Única Taiobeiras, R$ 612,00 uniforme, base Portaria TJMG 6607/2024 → 7231/2025. Período 2021-2025.

**Serve como referência para AJG, NÃO como base de proposta.**

| Caminho | O que é |
|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/Banco-Transversal/Honorarios-Periciais/Casos-Reais/Norte-Mineiro/taiobeiras-vara-unica-consolidado-0680.md` | Consolidado MD |
| `.../taiobeiras-vara-unica-consolidado-0680.FICHA.json` | FICHA |
| `/Users/jesus/Desktop/STEMMIA Dexter/PYTHON-BASE/08-SISTEMAS-COMPLETOS/taiobeiras-status/taiobeiras_status.py` | Script de status dos 6 casos |
| `/Users/jesus/Desktop/_MESA/10-PERICIA/aceites-taiobeiras-22abr/_README.md` | Contexto operacional |
| `/Users/jesus/Desktop/STEMMIA Dexter/memoria/base-conhecimento/honorarios.md` | Doc consolidada |

## Tabelas oficiais (AJG)

Raiz: `/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/Banco-Transversal/Honorarios-Periciais/Tabelas-Oficiais/`

| Tabela | PDF | FICHA |
|---|---|---|
| TJMG Portaria 6180/2023 | `tjmg-portaria-6180-2023-honorarios.pdf` | `.FICHA.json` |
| TJMG Portaria 6607/2024 | `tjmg-portaria-6607-2024-tabela-honorarios.pdf` | `.FICHA.json` |
| TJMG Portaria 7231/2025 **(vigente)** | `tjmg-portaria-7231-2025.pdf` | `.FICHA.json` |
| TJMG Tabela I DJe 21/06/2024 | `tjmg-tabela-i-honorarios-dje-21-6-2024.pdf` | — |
| CJF Res 305/2014 (JF/TRF6) | `federal-cjf-res305-2014.pdf` + anexo | `Federal-CJF-Res305.FICHA.json` |
| CSJT Res 66/2010 (trabalhista) | `trabalhista-csjt-res66-2010.pdf` | — |
| CNJ 424/2021 (cadastro peritos) | `cnj-res424-2021-cadastro-peritos.pdf` | — |

TRF6 por comarca: `Por-Quem-Paga/Uniao-Justica-Federal/trf6-muriae-*.FICHA.json`, `trf6-bh-*`, `trf6-jef-*`.

## Templates de proposta (custeado)

| Caminho | Classe | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/cowork/02-BIBLIOTECA/peticoes/proposta-honorarios/TEMPLATE.md` | Base genérico com `{{honorarios.valor_numerico}}`, cita Portaria TJMG 7231/2025 | PRONTO (genérico) |
| `.../proposta-honorarios/placeholders.json` | Schema de placeholders | PRONTO |
| `.../proposta-honorarios/civel-dano-pessoal/INVENTADO-NAO-USAR-TEMPLATE.md` | Cível dano pessoal | **NÃO USAR** (marcado inventado) |
| erro-medico/ | Erro médico | **FALTA** |
| securitario/ | Securitário | **FALTA** |
| previdenciario/ | Previdenciário | **FALTA** |
| trabalhista/ | Trabalhista | **FALTA** |

Ramificação documentada em `cowork/04-PIPELINES/pipeline-proposta-honorarios.md`.

## SCRIPTS EXISTENTES

### Gerador de proposta
| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/cowork/05-AUTOMACOES/scripts/aplicar_template.py` | **Motor.** FICHA + TEMPLATE → proposta preenchida | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/cowork/05-AUTOMACOES/orquestrador/orquestrador.py` | Roteia FICHA para template certo (lê `regras_classificacao.json`) | FUNCIONA |
| `.../orquestrador/regras_classificacao.json` | Regras de roteamento | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/src/peticoes/gerar_peticao.py` | Gera qualquer petição a partir de FICHA | FUNCIONA |

### Pesquisa de honorários (consulta base)
| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/src/honorarios/pesquisar_honorarios.py` | Busca decisões de honorários por comarca/tipo/valor | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/FERRAMENTAS/pesquisador-honorarios/pesquisar_honorarios.py` | Duplicata | DUVIDOSO |
| `/Users/jesus/Desktop/STEMMIA Dexter/FERRAMENTAS/pesquisador-honorarios/dados/honorarios.db` | SQLite com decisões TJMG | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/_arquivo/PESQUISADOR-HONORARIOS/dados/importar_fichas.py` | Importador legado | LEGADO |

### Verificador de proposta
| Caminho | O que faz |
|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/orquestradores/orquestrador-verificacao-proposta.md` | Orquestrador MD para verificar proposta antes de emitir |
| `/Users/jesus/Desktop/STEMMIA Dexter/verificadores/verificador_peticao_pdf.py` | Verifica petição gerada em PDF |

## Engenharia reversa (pedido do Dr. Jesus)

1. Coletar as propostas boas já feitas (PDFs emitidos).
2. Extrair estrutura comum: cabeçalho, fundamentação, tabela de complexidade, valor final, forma de pagamento.
3. Parametrizar → template novo por classe.
4. Plugar PERFIL-ESTILO.json (88KB, 68 petições analisadas — hoje no iCloud, não local).

## O que está FUNCIONANDO

- Gerar proposta genérica a partir do TEMPLATE.md + FICHA via `aplicar_template.py`.
- Consultar tabelas oficiais em PDF + FICHA.json indexadas.
- Caso Taiobeiras (AJG R$612) totalmente documentado.

## O que está RASCUNHO

- Templates por classe (só cível dano pessoal e marcado NÃO USAR).
- PERFIL-ESTILO.json desconectado.
- `pesquisar_honorarios.py` tem 2 cópias — qual é oficial?

## O que FALTA

- Templates: erro-médico, securitário, previdenciário, trabalhista.
- `scorer-complexidade.py` (mencionado no pipeline, não existe).
- Agente `cfm-buscador` (para erro-médico).
- Geração automática de PDF timbrado a partir do MD.
