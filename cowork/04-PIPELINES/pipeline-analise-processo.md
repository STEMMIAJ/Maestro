---
nome: pipeline-analise-processo
entrada: 1+ PDFs em 01-CASOS-ATIVOS/<numero-cnj>/documentos-recebidos/
saida: _dados/FICHA.json + _dados/ANALISE.md + _dados/RESUMO-3-LINHAS.md
duracao_estimada: 3-8 min
agentes_envolvidos: [orq-analise-rapida, buscador-base-local]
---

# Pipeline 1 — Análise de Processo

## Objetivo

Transformar 1 ou mais PDFs de processo judicial em uma FICHA estruturada (`FICHA.json`), uma análise narrativa (`ANALISE.md`) e um resumo de 3 linhas (`RESUMO-3-LINHAS.md`). Saída determinística, auditável e reusável pelos pipelines 2 (petição) e 3 (laudo).

## Pré-requisitos

- Pasta `01-CASOS-ATIVOS/<numero-cnj>/` criada.
- Subpasta `documentos-recebidos/` contendo pelo menos 1 PDF.
- Subpasta `_dados/` criada (vazia ou contendo versão anterior para diff).
- Número CNJ no formato `NNNNNNN-DD.AAAA.J.TR.OOOO` conferido.
- `orq-analise-rapida` disponível como agente (Opus).
- OCR disponível (`ocrmypdf` ou equivalente) para PDFs digitalizados.

## Passos

### 1. Inventário dos PDFs
- **Ação**: listar arquivos em `documentos-recebidos/`, registrar nome, tamanho, hash SHA1.
- **Tool**: `Bash` (`ls -la`, `shasum`).
- **Escreve**: `_dados/INVENTARIO.md` (tabela: arquivo, tamanho, hash, digitalizado sim/não).
- **Sucesso**: tabela com ≥1 linha e todos os hashes calculados.

### 2. Detecção de PDFs digitalizados
- **Ação**: para cada PDF, contar páginas com texto extraível vs vazias.
- **Tool**: `Bash` (`pdftotext` → `wc -c`).
- **Critério**: <200 caracteres por página média ⇒ marcar como digitalizado.
- **Escreve**: coluna `digitalizado` no `INVENTARIO.md`.

### 3. OCR condicional
- **Ação**: rodar `ocrmypdf --skip-text -l por` nos PDFs marcados digitalizado.
- **Tool**: `Bash`.
- **Lê/Escreve**: `documentos-recebidos/*.pdf` → `documentos-recebidos/ocr/*.pdf`.
- **Sucesso**: todo PDF digitalizado tem par OCR em `ocr/`.

### 4. Extração bruta de texto
- **Ação**: gerar um `.txt` por PDF (original + OCR).
- **Tool**: `Bash` (`pdftotext -layout`).
- **Escreve**: `_dados/texto-bruto/<arquivo>.txt`.
- **Sucesso**: 1 `.txt` não-vazio por PDF.

### 5. Análise estruturada via `orq-analise-rapida`
- **Ação**: invocar `orq-analise-rapida` com os `.txt` de entrada. Agente orquestra sub-tarefas paralelas: identificação de partes, CID, datas, pedidos, erros materiais.
- **Tool**: `Task` (subagente Opus).
- **Escreve**: `_dados/FICHA.json` (schema abaixo), `_dados/ANALISE.md`.
- **Sucesso**: `FICHA.json` valida contra schema, `ANALISE.md` ≥ 15 linhas.

#### Schema mínimo de `FICHA.json`

```json
{
  "numero_cnj": "NNNNNNN-DD.AAAA.J.TR.OOOO",
  "vara": "",
  "comarca": "",
  "partes": { "autor": {"nome":"", "cpf":"", "idade":0}, "reu": {"nome":"", "cnpj_cpf":""} },
  "tipo_acao": "",
  "pedidos": [],
  "cid_suspeitos": [],
  "datas_criticas": { "distribuicao":"", "nomeacao_perito":"", "audiencia":"", "prazo_laudo":"" },
  "honorarios": { "valor":null, "por_extenso":"", "forma_pagamento":"" },
  "quesitos": { "juizo":[], "autor":[], "reu":[] },
  "erros_materiais_detectados": [],
  "anexos": []
}
```

### 6. Verificação de erros materiais
- **Ação**: cruzar CNJ, nome das partes, datas, valores em cada documento. Divergência ⇒ registrar.
- **Tool**: `Grep` + `Task` (sub-tarefa do `orq-analise-rapida`).
- **Escreve**: campo `erros_materiais_detectados` em `FICHA.json`.
- **Sucesso**: lista explícita (pode ser vazia, mas deve existir).

### 7. Resumo de 3 linhas
- **Ação**: condensar em 3 linhas: (1) quem é o autor + patologia, (2) o que se pede, (3) próxima ação do perito.
- **Tool**: sub-tarefa do `orq-analise-rapida`.
- **Escreve**: `_dados/RESUMO-3-LINHAS.md`.
- **Sucesso**: arquivo com exatamente 3 linhas não-vazias.

### 8. Verificação final
- **Ação**: rodar checagens automáticas (ver seção seguinte).
- **Tool**: `Bash` + `Read`.
- **Sucesso**: todas as checagens retornam OK.

## Pontos de verificação

Antes de declarar o pipeline concluído, executar e confirmar cada item:

| # | Checagem | Comando | Esperado |
|---|----------|---------|----------|
| V1 | `FICHA.json` existe e é JSON válido | `python3 -m json.tool _dados/FICHA.json > /dev/null` | exit 0 |
| V2 | CNJ no FICHA bate com pasta | `grep numero_cnj _dados/FICHA.json` | bate |
| V3 | `ANALISE.md` ≥ 15 linhas | `wc -l _dados/ANALISE.md` | ≥15 |
| V4 | `RESUMO-3-LINHAS.md` com 3 linhas | `wc -l _dados/RESUMO-3-LINHAS.md` | =3 |
| V5 | Campo `cid_suspeitos` preenchido OU justificativa em `ANALISE.md` | `grep cid_suspeitos FICHA.json` | não-vazio |
| V6 | `erros_materiais_detectados` existe (pode ser `[]`) | `grep erros_materiais FICHA.json` | presente |

Só declarar “feito” após V1–V6 passarem. Sem esse check, resposta deve ser “análise incompleta”.

## Erros comuns + fix

1. **PDF protegido por senha** → `qpdf --decrypt` antes de OCR. Se falhar, registrar em `PENDENCIAS.md` e abortar.
2. **OCR devolve português ruim (acentos quebrados)** → adicionar `-l por+eng`, reprocessar. Se persistir, pedir PDF nativo ao juízo.
3. **CNJ divergente entre capa e intimação** → registrar em `erros_materiais_detectados`, usar CNJ da distribuição como canônico, sinalizar em `ANALISE.md`.
4. **Nomeação do perito não encontrada** → buscar nos últimos 20 documentos por `nomeia\|nomear\|perito`. Se ausente, marcar `datas_criticas.nomeacao_perito` como `null` e avisar.
5. **Múltiplos autores/litisconsórcio** → transformar `partes.autor` em array. Schema permite.

## Exemplo executado — caso 0000000-00.0000.0.00.0000

1. Pasta `01-CASOS-ATIVOS/0000000-00.0000.0.00.0000/documentos-recebidos/` contém 3 PDFs: `inicial.pdf` (nativo), `laudo-inss.pdf` (digitalizado), `nomeacao.pdf` (nativo).
2. Inventário gerado; `laudo-inss.pdf` marcado digitalizado.
3. OCR roda em `laudo-inss.pdf` → `ocr/laudo-inss.pdf`.
4. `pdftotext` gera 3 `.txt` em `_dados/texto-bruto/`.
5. `orq-analise-rapida` produz:
   ```json
   { "numero_cnj": "0000000-00.0000.0.00.0000",
     "partes": { "autor": {"nome":"Fulano de Tal","cpf":"000.000.000-00","idade":47} },
     "tipo_acao":"Auxílio-doença/aposentadoria por incapacidade",
     "cid_suspeitos":["M54.5","F33.1"],
     "datas_criticas":{"nomeacao_perito":"2026-04-10","prazo_laudo":"2026-05-10"},
     "honorarios":{"valor":600,"por_extenso":"seiscentos reais"},
     "erros_materiais_detectados":[] }
   ```
6. `ANALISE.md` com 28 linhas; `RESUMO-3-LINHAS.md`:
   > Fulano, 47 anos, lombalgia crônica (M54.5) + depressão (F33.1).
   > Pede auxílio-doença via perícia judicial.
   > Próxima ação: emitir petição de aceite e agendar exame em até 30 dias.
7. V1–V6 passam. Pipeline 1 concluído em 4 min 12 s.
