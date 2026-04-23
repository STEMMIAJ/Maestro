---
titulo: Anti-padrões de prompt
bloco: 08_ai_and_automation
tipo: checklist
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: pratica-consolidada
tempo_leitura_min: 3
---

# Anti-padrões de prompt

## 1. Instruções contraditórias

"Seja breve, mas cubra todos os aspectos em detalhes." → modelo escolhe um dos dois, aleatoriamente. Decidir: brevidade OU completude. Se precisa dos dois, separar em duas chamadas (ex.: rascunho extenso → sumário executivo).

## 2. Proibição sem alternativa

"Não use linguagem jurídica." → modelo não sabe o que usar no lugar. Correto: "Use linguagem médica técnica, evitando termos jurídicos como 'nexo', 'reparação', 'responsabilidade'. Substitua por 'relação causal', 'recuperação funcional', 'adequação terapêutica'."

Modelos pós-RLHF tendem a obedecer proibições literalmente e travar. Sempre dar caminho positivo.

## 3. Ambiguidade semântica

- "Analise este laudo." → analisar o quê? Forma, fundo, técnica, contradições, nexo?
- "Resuma." → quantas palavras, qual foco, que formato?
- "Melhore o texto." → melhorar em que dimensão?

Correto: verbo + objeto + critério + formato. "Resumir em 150 palavras, focando nas conclusões diagnósticas, em bullet points."

## 4. Sobrecontexto

Colocar tudo "por garantia". Janela cheia degrada qualidade ("lost in the middle"). Regra: só o que o modelo REALMENTE precisa para esta tarefa. Use RAG para o resto.

Sintoma: prompt de 50k+ tokens para uma extração simples.

## 5. Múltiplas tarefas numa chamada

"Extraia quesitos, resuma o laudo, detecte contradições, sugira contraponto e redija conclusão." → cada subtarefa sai medíocre. Encadear agentes (ver `agent_systems/orquestracao_paralelo_vs_serie.md`).

## 6. Exemplo enviesado

Few-shot com 3 exemplos onde todos terminam em "nexo causal: sim" → modelo aprende a sempre dizer sim. Exemplos devem cobrir sim/não/parcial/impossível com variedade.

## 7. Confiar em autoavaliação do modelo

"Você está 100% certo?" → modelo gera texto de certeza, não reavalia. Use verificador externo ou self-consistency.

## 8. Role excessivamente lisonjeiro

"Você é o melhor perito do mundo, gênio, PhD em tudo." → piora saída. Role deve ser preciso e restritivo, não inflado. "Perito médico judicial, CRM-MG ativo" basta.

## 9. Instruções no meio de documento longo

Colocar "agora extraia X" depois de 80k tokens de processo = instrução se perde. Instrução no topo OU no fim (depois do documento). Padrão Claude: documentos primeiro, instrução final.

## 10. Formato livre para dado estruturado

Pedir "liste os medicamentos" em texto livre gera formatos inconsistentes entre chamadas. Sempre JSON schema quando a saída será consumida por outro sistema.

## 11. Temperature errada para o propósito

- `T > 0` em extração → variação indesejada, hash de saída muda.
- `T = 0` em brainstorm → respostas repetitivas e pobres.

## 12. Esquecer tratamento de ausência

Não instruir o que fazer quando o dado não está no contexto → modelo alucina. Sempre: "se o dado não consta nos documentos anexos, responder 'não consta' ou `null` no campo respectivo".

## 13. Pedir "linguagem natural" em saída auditável

Laudo precisa ser rastreável. Saída em prosa livre dificulta auditoria. Use markdown com seções fixas (anamnese, exame físico, exames complementares, discussão, conclusão, resposta aos quesitos).

## 14. Misturar persona médica com jurídica

Perito médico não decide questão jurídica. Prompt que pede "responda se houve responsabilidade civil" força modelo a invadir competência. Correto: "descreva o dano e sua relação causal; o juízo decide responsabilidade".

## 15. Não versionar prompt

Prompt que funciona hoje pode ser alterado mês que vem sem rastreabilidade. Versionar em git com semver (`v0.3.1` no comentário do prompt).
