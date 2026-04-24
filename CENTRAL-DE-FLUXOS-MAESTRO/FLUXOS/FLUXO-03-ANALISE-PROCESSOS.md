# FLUXO 03 — Análise de processos

## Objetivo

A partir dos PDFs baixados, gerar **FICHA.json** (dados estruturados) + **ANALISE.md** (narrativa) + **RESUMO-3-LINHAS.md**. Essas saídas alimentam os fluxos 04 (laudo) e 05 (honorários).

## Requisitos de dados (o que a FICHA precisa conter)

1. **Identificação** — `numero_cnj`, `vara`, `comarca`, `tipo_acao`.
2. **Partes** — autores, réus (CPF/CNPJ/idade), advogados com OAB, juiz(es).
3. **Datas críticas** — distribuição, nomeação do perito, audiência, prazo do laudo.
4. **CID suspeitos** — lista de códigos médicos mencionados.
5. **Honorários** — valor, quem paga, forma de pagamento, **justiça gratuita (AJG) ou custeado**.
6. **Quesitos** — do juízo, do autor, do réu (separados).
7. **Pedidos** — lista dos pedidos da inicial.
8. **Resumo por peça** — petição inicial, contestação, despachos, laudos prévios (com linguagem simples, sem omitir fatos).
9. **Erros materiais detectados** — CNJ divergente, data impossível, nome grafado errado, CID inexistente.
10. **Anexos** — lista dos PDFs que alimentaram a análise.

Schema canônico documentado em `cowork/04-PIPELINES/pipeline-analise-processo.md`.

## Passos (fluxo ideal, como deveria rodar)

1. **Inventário** — listar PDFs da pasta `documentos-recebidos/`, hash SHA1 de cada um.
2. **Detectar digitalizados** — PDFs com menos de 200 chars/página ⇒ marcar para OCR.
3. **OCR** — `ocrmypdf -l por` nos digitalizados. **HOJE NÃO EXISTE SCRIPT EM LOTE.**
4. **Extração de texto** — `pdftotext -layout` ou PyMuPDF (fitz) em cada PDF.
5. **Análise estruturada** — agente `orq-analise-rapida` produz FICHA.json + ANALISE.md.
6. **Verificação de erros materiais** — cruzar CNJ, nomes, datas, valores em cada documento.
7. **Resumo de 3 linhas** — quem é o autor, o que se pede, próxima ação do perito.
8. **Indexação** — `indexer_ficha.py` coloca FICHA no `maestro.db` (SQLite).

## SCRIPTS EXISTENTES

### Pipeline principal (`src/pipeline/`)
| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/src/pipeline/pipeline_analise.py` | **Orquestrador.** Flags `--cnj`, `--todos`, `--pendentes`. Roda paralelo | FUNCIONA |
| `.../pipeline/extrair_partes.py` | Regex CPF/CNPJ/OAB/CRM → PARTES.json + PARTES.md. Atualiza FICHA | FUNCIONA |
| `.../pipeline/resumir_fatos.py` | TEXTO-EXTRAIDO.txt → TIMELINE.json + TIMELINE.md | FUNCIONA |
| `.../pipeline/extrair_quesitos.py` | Agrupa quesitos por origem (juízo/autor/réu/MP) | FUNCIONA |
| `.../pipeline/classificar_acao.py` | Tipo de ação (erro-médico, previdenciário, trabalhista, etc.) | FUNCIONA |
| `.../pipeline/classificar_documento.py` | Classifica cada doc individual (inicial, contestação, laudo, receita) | FUNCIONA |
| `.../pipeline/detectar_urgencia.py` | Flag de prazo crítico | FUNCIONA |
| `.../pipeline/scanner_processos.py` | Varre pasta `~/Desktop/ANALISADOR FINAL/processos/` → STATUS-PROCESSOS.json | FUNCIONA |
| `.../pipeline/inbox_processor.py` | PDFs em INBOX/ → cria pasta CNJ + roda pipeline | FUNCIONA |
| `.../pipeline/consolidar_processos.py` | Consolida múltiplas fichas | FUNCIONA |
| `.../fases/fase4_analise_profunda.py` | Análise profunda usando Claude API | FUNCIONA |

(Há cópia em `~/stemmia-forense/src/pipeline/` e `_arquivo/Open/analisador-final/scripts/` — **três versões do mesmo pipeline**. Decisão pendente: qual é a oficial.)

### Verificadores (qualidade da FICHA)
| Caminho | O que faz |
|---|---|
| `.../pipeline/verificadores/verificador_cids_datasus.py` | Valida CIDs contra tabela DataSUS (12.451 códigos) |
| `.../pipeline/verificadores/verificador_datas.py` | Detecta datas impossíveis |
| `.../pipeline/verificadores/verificador_exames.py` | Cruza exames citados vs anexados |
| `.../pipeline/verificadores/verificador_medicamentos.py` | Plausibilidade de dosagens |
| `.../pipeline/verificadores/verificador_nomes.py` | Consistência de nomes ao longo dos PDFs |
| `.../pipeline/verificadores/merge_verificadores.py` | Junta todos em relatório único |

### OCR e extração de texto
| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/_arquivo/ANALISADOR ULTRA/core/pdf_processor.py` | PyMuPDF (fitz) — extrai texto nativo | FUNCIONA |
| `/Users/jesus/stemmia-forense/src/pdf_processor.py` | Mesma função | FUNCIONA |

**OCR em lote com `ocrmypdf`/`tesseract`: NÃO ENCONTRADO.** Hoje só texto nativo é extraído.

### Indexação no banco
| Caminho | O que faz |
|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/banco-local/indexer_ficha.py` | Varre todas FICHA.json → upsert em `maestro.db`. Flags `--dry-run --source --db` |
| `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/verificadores/auditar_numero_cnj_ficha.py` | Compara CNJ da FICHA vs CNJ da pasta. Flag `--fix` corrige |

### Agentes (Markdown)
| Caminho | Papel |
|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/orquestradores/orq-analise-rapida.md` | Orquestrador |
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/clusters/extracao/extrator-*.md` | Extratores específicos |
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/clusters/verificacao/*.md` | Verificadores |

## A IMPLEMENTAR DEPOIS (sem código agora)

1. **OCR em lote** — script que varre pasta e roda `ocrmypdf --skip-text -l por` nos digitalizados.
2. **Decidir qual pipeline é oficial** — Maestro vs stemmia-forense vs _arquivo. Hoje são 3 cópias.
3. **Auditor de FICHA contra schema** — validar todas as FICHA.json existentes contra o schema canônico (bugs já corrigidos no pipeline novo estão documentados em `project_bugs_aquisicao_consertados.md`).
4. **Conectar verificadores ao pipeline principal** — hoje rodam separados.
5. **Detecção automática de justiça gratuita** — já é campo na FICHA, mas extração manual ainda.

## Saídas esperadas (por CNJ)

```
01-CASOS-ATIVOS/<CNJ>/
├── documentos-recebidos/*.pdf
├── _dados/
│   ├── FICHA.json              # dados estruturados
│   ├── ANALISE.md              # narrativa
│   ├── RESUMO-3-LINHAS.md      # 3 linhas
│   ├── PARTES.json / PARTES.md
│   ├── TIMELINE.json / TIMELINE.md
│   ├── QUESITOS.json / QUESITOS.md
│   ├── CLASSIFICACAO.json / CLASSIFICACAO.md
│   ├── URGENCIA.json
│   ├── INVENTARIO.md
│   └── texto-bruto/*.txt
```
