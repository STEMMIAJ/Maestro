---
titulo: Few-shot, chain-of-thought, ReAct, self-consistency
bloco: 08_ai_and_automation
tipo: tecnica
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: tecnico-consolidado
tempo_leitura_min: 6
---

# Few-shot, chain-of-thought, ReAct, self-consistency

## Zero-shot

Instrução direta sem exemplo. Funciona para tarefas comuns (sumarizar, traduzir, classificar) quando o formato de saída é trivial. Para extração estruturada ou domínio específico (perícia), costuma ser frágil.

## Few-shot

Incluir 2–8 exemplos completos (entrada → saída) antes da tarefa real. O modelo infere o padrão. Regras:

- Exemplos devem cobrir variedade relevante (caso fácil, borderline, ambíguo).
- Formato dos exemplos = formato esperado da saída.
- Mais de 10 exemplos raramente ajuda; ocupa janela.
- Em Claude, delimitar exemplos com `<exemplo>...</exemplo>` ou separadores claros.

Exemplo — extrair CID:

```xml
<exemplo>
  <entrada>Paciente com dor lombar crônica há 3 anos, RM com protrusão L4-L5.</entrada>
  <saida>{"cid": "M54.5", "descricao": "dor lombar baixa", "confianca": 0.9}</saida>
</exemplo>
<exemplo>
  <entrada>Histórico de diabetes tipo 2 descompensado, HbA1c 9.8.</entrada>
  <saida>{"cid": "E11.9", "descricao": "DM2 sem complicações especificadas", "confianca": 0.85}</saida>
</exemplo>
```

## Chain-of-thought (CoT)

Forçar o modelo a escrever o raciocínio passo a passo ANTES da conclusão. Ganho mensurável em problemas com múltiplos passos (cálculo, diagnóstico diferencial, nexo causal).

Duas formas:

1. **CoT explícito**: "Pense passo a passo. Liste hipóteses, avalie cada uma, conclua."
2. **CoT via Claude `<thinking>`**: Claude aceita tag `<thinking>` onde raciocinia sem poluir saída final. Pode-se descartar o thinking e guardar apenas a conclusão — ou manter para auditoria.

Estudos: CoT melhora 20–40% em benchmarks aritméticos e de raciocínio médico (MedQA). Pouco ganho em extração simples.

**Cuidado**: CoT aumenta tokens de saída (= custo). Para perícia, vale pela auditabilidade — o perito pode revisar o raciocínio antes de assinar.

## ReAct (Reason + Act)

Padrão para agentes com ferramentas. Loop: **Thought** (raciocina) → **Action** (chama ferramenta) → **Observation** (lê resultado) → repete até **Final Answer**.

Exemplo em perícia:

```
Thought: Preciso verificar se o CID M54.5 justifica incapacidade permanente.
Action: buscar_jurisprudencia("M54.5 incapacidade permanente TJMG")
Observation: 12 acórdãos, 8 negaram incapacidade por si só.
Thought: Isolado não basta; preciso cruzar com limitação funcional.
Action: buscar_exame_funcional(id_processo)
Observation: EMG normal, Roland-Morris 14/24.
Thought: Há limitação funcional moderada. Concluir parcial temporária.
Final Answer: Incapacidade parcial temporária, 60 dias.
```

Agentes do Dexter (`orq-analise-completa`, `gerador-peticao-complexo`) usam variantes de ReAct.

## Self-consistency

Rodar o mesmo prompt N vezes com `T > 0`, coletar N respostas, escolher a mais frequente (majority vote). Para problemas com resposta única (classificação, cálculo), melhora acurácia em 5–15%.

Custo: N× mais tokens de saída. Para perícia, uso restrito a decisões críticas de classificação (ex.: nexo causal sim/não quando há divergência entre laudos).

Variante "judge": gerar 3 respostas com `T=0.3`, depois um LLM juiz escolhe a melhor com justificativa.

## Quando cada

| Situação | Técnica |
|----------|---------|
| Extração simples, formato claro | Zero-shot + schema |
| Extração com formato incomum ou jargão | Few-shot |
| Diagnóstico diferencial, cálculo de dano, nexo | CoT |
| Tarefa com ferramentas externas (busca, cálculo) | ReAct |
| Decisão binária crítica | Self-consistency |
| Redação final de laudo | Zero-shot + template estrito |

## Referências

- Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", 2022.
- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models", 2022.
- Wang et al., "Self-Consistency Improves Chain of Thought Reasoning", 2022.
