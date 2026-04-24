---
nome: respostas
proposito: Reações a atos processuais pós-laudo (quesitos suplementares, impugnação, esclarecimento)
---

# Respostas — reações processuais

Todo ato aqui pressupõe **laudo já entregue** e **alguma movimentação sobre ele**.

## `quesitos-suplementares/`

Parte (autor, réu ou AT) apresenta novos quesitos após a entrega do laudo. O perito responde.

**Gatilho:** intimação "manifestar-se sobre quesitos suplementares em X dias".

**Estrutura:**
1. Retomada breve do caso (2 linhas)
2. Quesitos suplementares (reproduzir na íntegra)
3. Respostas item a item
4. Observações (se algum quesito for impertinente, prejudicado, repetido)
5. Fecho

**Armadilha:** quesito que **muda a premissa** do caso (ex: traz dado novo) exige cuidado — se o dado muda a conclusão, o laudo vira complementar, não resposta.

## `impugnacao-laudo/`

Parte impugna a conclusão pericial. Geralmente vem com parecer de AT.

**Gatilho:** intimação "manifestar-se sobre impugnação em X dias".

**Estrutura:**
1. Resumo dos pontos de impugnação (numerar)
2. Resposta técnica a cada ponto
3. Eventual retificação (se impugnação tem razão parcial — admitir é força, não fraqueza técnica)
4. Reafirmação da conclusão (ou modificação fundamentada, se o caso)
5. Fecho

**Princípio:** impugnação bem feita merece resposta técnica. Impugnação com má-fé/especulativa merece resposta seca e curta.

## `esclarecimento-juiz/`

Juiz pede esclarecimento pontual, geralmente sobre um trecho específico do laudo.

**Gatilho:** despacho "esclareça o ponto X em Y dias".

**Estrutura:**
- Resposta direta e curta ao que foi perguntado
- Se o juiz não compreendeu terminologia, explicar em linguagem leiga **mantendo o rigor técnico**
- Fecho mínimo

**Regra:** aqui brevidade é qualidade. Juiz pediu 1 ponto, responde 1 ponto.

## Gatilho automático (futuro)

Hook no pipeline de triagem de intimações (`pipeline-intimacao.md`) detecta estas 3 situações e:
1. Pergunta ao usuário qual classe
2. Copia template da subpasta correta para `01-CASOS-ATIVOS/<CNJ>/peticoes-geradas/`
3. Pré-preenche com dados do caso + trecho pertinente do laudo próprio

## Integração com aprendizado

Toda resposta a impugnação bem-sucedida vira caso de estudo em `06-APRENDIZADO/respostas-impugnacao-sucesso.md` (se o juiz acatou sem novas idas e vindas). Respostas que o juiz pediu novo esclarecimento → `erros-clarificacao.md` (aprender onde foi mal explicado).
