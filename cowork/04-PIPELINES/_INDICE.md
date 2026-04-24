---
nome: indice-pipelines
versao: 1.0
atualizado: 2026-04-20
---

# Índice de Pipelines — Cowork Pericial

Mapa operacional dos pipelines do fluxo pericial. Um pipeline = uma transformação determinística com entrada, saída, agentes e critérios de verificação.

## Pipelines ativos

| # | Pipeline | Entrada | Saída | Duração | Arquivo |
|---|----------|---------|-------|---------|---------|
| 1 | Análise de processo | PDFs em `documentos-recebidos/` | `FICHA.json` + `ANALISE.md` + `RESUMO-3-LINHAS.md` | 3–8 min | [`pipeline-analise-processo.md`](pipeline-analise-processo.md) |
| 2 | Geração de petição | `FICHA.json` + tipo | `peticoes-geradas/<data>-<tipo>.md` + `.pdf` timbrado | 1–3 min | [`pipeline-geracao-peticao.md`](pipeline-geracao-peticao.md) |
| 3 | Geração de laudo | `FICHA.json` + `notas-exame.md` + quesitos | `laudo/LAUDO-<data>.md` + `.pdf` | 8–20 min | [`pipeline-geracao-laudo.md`](pipeline-geracao-laudo.md) |

## Ordem natural de execução

```
[PDFs recebidos]
      │
      ▼
Pipeline 1 (análise) ──► FICHA.json ──┬──► Pipeline 2 (petição: aceite, agendamento, etc.)
                                      │
                                      └──► Pipeline 3 (laudo, após exame físico)
```

## Convenções

- Todo caso vive em `01-CASOS-ATIVOS/<numero-cnj>/`.
- Todo artefato gerado por pipeline é escrito dentro do caso, nunca na raiz.
- Todo pipeline termina com verificação explícita antes de declarar sucesso (anti-mentira).
- Pipelines não fazem redação livre: usam templates e dados da FICHA.

## Regras absolutas

1. Nunca pular pré-requisitos. Se falta dado, abortar e registrar em `_dados/PENDENCIAS.md`.
2. Nunca declarar “feito” sem o comando de verificação correspondente ter retornado OK.
3. Nunca alterar `FICHA.json` fora do pipeline de análise. Correções vão em `FICHA.json` via diff versionado.
