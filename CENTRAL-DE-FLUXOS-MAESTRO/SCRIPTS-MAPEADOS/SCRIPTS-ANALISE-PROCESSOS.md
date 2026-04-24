# Scripts mapeados — FLUXO 03 (Análise de processos)

## Pipeline principal

Raiz oficial: `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/src/pipeline/`
Cópia alternativa: `/Users/jesus/stemmia-forense/src/pipeline/`
Cópia legado: `/Users/jesus/Desktop/STEMMIA Dexter/_arquivo/Open/analisador-final/scripts/`

**Três cópias do mesmo pipeline — decisão pendente sobre qual é a oficial.**

| Caminho relativo | Função | Status |
|---|---|---|
| `pipeline_analise.py` | Orquestrador. Flags `--cnj --todos --pendentes` | FUNCIONA |
| `extrair_partes.py` | Regex CPF/CNPJ/OAB/CRM → PARTES.json + PARTES.md | FUNCIONA |
| `resumir_fatos.py` | TEXTO-EXTRAIDO.txt → TIMELINE.json/.md | FUNCIONA |
| `extrair_quesitos.py` | Quesitos por origem (juízo/autor/réu/MP) | FUNCIONA |
| `classificar_acao.py` | Tipo de ação | FUNCIONA |
| `classificar_documento.py` | Classifica cada doc do processo | FUNCIONA |
| `detectar_urgencia.py` | Flag de prazo crítico | FUNCIONA |
| `scanner_processos.py` | Varre pasta → STATUS-PROCESSOS.json | FUNCIONA |
| `inbox_processor.py` | Novo PDF em INBOX/ → cria pasta CNJ + pipeline | FUNCIONA |
| `consolidar_processos.py` | Consolida várias fichas | FUNCIONA |

## Análise profunda (Claude API)

| Caminho | Função | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/src/fases/fase4_analise_profunda.py` | Análise profunda (Anthropic SDK) | FUNCIONA |

## Extração de texto de PDF

| Caminho | Função | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/_arquivo/ANALISADOR ULTRA/core/pdf_processor.py` | `extrair_texto_pdf()` via PyMuPDF (fitz) | FUNCIONA |
| `/Users/jesus/stemmia-forense/src/pdf_processor.py` | Mesma função | FUNCIONA |

**OCR em lote: NÃO EXISTE** nos paths varridos.

## Indexação / auditoria

| Caminho | Função | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/banco-local/indexer_ficha.py` | Varre FICHA.json → upsert em `maestro.db`. Flags `--dry-run --source --db` | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/verificadores/auditar_numero_cnj_ficha.py` | CNJ pasta vs CNJ FICHA. Flag `--fix` | FUNCIONA |

## Verificadores de qualidade

Pasta: `.../pipeline/verificadores/`

| Script | O que valida |
|---|---|
| `verificador_cids_datasus.py` | CIDs contra tabela DataSUS (12.451 códigos) |
| `verificador_datas.py` | Datas impossíveis (futura, alta antes de internação, etc.) |
| `verificador_exames.py` | Exames citados vs anexados |
| `verificador_medicamentos.py` | Plausibilidade de dosagens |
| `verificador_nomes.py` | Consistência de nomes ao longo dos PDFs |
| `merge_verificadores.py` | Consolida em relatório único |

Todos FUNCIONA.

## Agentes MD relacionados

| Caminho | Papel |
|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/orquestradores/orq-analise-rapida.md` | Orquestrador principal |
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/clusters/extracao/*` | Extratores específicos |
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/clusters/verificacao/*` | Verificadores Markdown |

## Lacuna crítica

- Sem script de OCR em lote para PDFs digitalizados.
- Três cópias do pipeline — precisa consolidar.
