---
titulo: Como avaliar saída de LLM
bloco: 08_ai_and_automation
tipo: tecnica
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: tecnico-consolidado
tempo_leitura_min: 6
---

# Como avaliar saída de LLM

## Por que avaliar

LLM falha de forma silenciosa e plausível (ver `llm_foundations/limitacoes_do_llm.md`). Um laudo confiante e errado é o cenário mais perigoso da perícia. Avaliação sistemática separa pipeline confiável de roleta.

## Três famílias de avaliação

### 1. Reference-based

Há uma resposta de referência (gold standard). Métrica compara saída do modelo com referência.

- **Exact match**: igual caractere a caractere. Útil para extração de campo fechado (CID, CNJ, data).
- **F1 em spans**: sobreposição de tokens. Extração de trechos.
- **ROUGE / BLEU**: sumário vs sumário humano. Pouco usado hoje (mede forma, não fato).
- **Embedding similarity**: coseno entre embedding da saída e da referência. Captura paráfrase.

Aplicação em perícia: você tem 50 laudos redigidos pelo Dr. Jesus manualmente; roda LLM nos mesmos casos; compara. Bom para regressão ("o novo prompt degradou?").

### 2. Reference-free

Não há gold standard. Avalia-se pela presença de propriedades desejadas.

- **Structured output validation**: saída é JSON válido? Passa em JSON schema?
- **Rules / regex**: CID tem formato `[A-Z]\d{2}(\.\d)?`? Data é ISO 8601? CNJ tem 20 dígitos?
- **Consistency check**: resposta ao quesito bate com seção "conclusão" do laudo?
- **Groundedness**: cada claim tem citação de fonte existente no contexto?
- **Refusal check**: modelo recusou quando dado faltava (comportamento esperado)?

Para perícia, reference-free é o pão com manteiga — gold standard é caro de produzir.

### 3. LLM-as-judge

Um LLM (idealmente Opus) avalia a saída de outro LLM contra uma rubrica estruturada.

Formato típico:

```xml
<rubrica>
Avaliar resposta do perito quanto a:
1. Acurácia médica (1-5)
2. Fundamentação com exames (1-5)
3. Linguagem técnica adequada (1-5)
4. Ausência de eufemismo / disclaimer (binário)
5. Rastreabilidade de citações (1-5)
</rubrica>

<resposta_avaliada>{texto}</resposta_avaliada>
<contexto_original>{laudo, exames, quesito}</contexto_original>

<task>
Para cada critério: nota + justificativa com trecho literal.
Conclusão: aceitar | revisar | rejeitar.
</task>
```

Relato empírico: LLM-as-judge correlaciona ~0.7–0.85 com avaliação humana em tarefas estruturadas. Degrada em tarefas subjetivas. Usar Opus como juiz sobre saída de Sonnet/Haiku é padrão custo-eficiente (ver skill `opus-auditor` do Dexter).

## Rubrica — anatomia

Rubrica boa é:

- **Específica do domínio** (não "a resposta é boa?"; "a resposta cita exame com data correta?").
- **Discreta** (1-5 ou binária; evitar contínuo que humano não consegue replicar).
- **Múltiplos critérios independentes** (não agregar prematuramente).
- **Exemplos de cada nota** no prompt do juiz (few-shot de rubrica).
- **Obrigada a citar trecho** para cada nota (reduz alucinação do juiz).

## Consistency check (auto-check)

Rodar o mesmo prompt N vezes, medir estabilidade. Se a resposta varia muito em `temperature: 0`, há ambiguidade no prompt ou no dado. Acionar revisão humana.

Para decisão crítica (sim/não), self-consistency com N=5 e majority vote. Divergência → sinal vermelho.

## Golden set — como construir

Para uma tarefa pericial (ex.: "extrair quesitos"):

1. Pegar 30–50 processos reais de diferentes classes/varas.
2. Dr. Jesus produz resposta manual (gold).
3. Salvar em CSV: `processo_id, input_completo, gold_answer`.
4. Versionar em git.
5. Rodar nova versão do prompt sobre golden set → gerar saídas.
6. Comparar com gold via métrica apropriada.
7. Registrar taxa de acerto por versão do prompt.

30 casos = mínimo para ter sinal; 100+ = confiável.

## Pipeline de avaliação no Dexter

Proposta:

```
saida_agente
    ↓
guardrails (schema JSON, regex)  ← falha → rejeitar, rerun
    ↓
verificador automático (datas, CIDs, fontes)  ← falha → marcar [REVISAR]
    ↓
LLM-as-judge (Opus auditor)  ← nota baixa → revisão humana
    ↓
revisão humana (só amostra ou casos críticos)
    ↓
saída final assinada
```

Já existe parcialmente: hooks anti-mentira + verificadores especializados + skill opus-auditor.

## Erros comuns

- Avaliar só pela forma (gramática, tamanho) e não pelo fato.
- Rubrica subjetiva que o juiz interpreta diferente a cada chamada.
- Golden set pequeno demais (< 20) → variância domina.
- LLM-as-judge sem few-shot → rubrica interpretada soltamente.
- Avaliar em dev e não monitorar produção — regressão passa despercebida.

## Referências

- Zheng et al., "Judging LLM-as-a-Judge", 2023.
- Liu et al., "G-Eval: NLG Evaluation using GPT-4", 2023.
- Anthropic, "Strengthening and automating AI safety via evaluations". [TODO/RESEARCH]
