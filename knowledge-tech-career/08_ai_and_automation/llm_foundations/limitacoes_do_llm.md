---
titulo: Limitações do LLM e mitigação
bloco: 08_ai_and_automation
tipo: fundamento
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: tecnico-consolidado
tempo_leitura_min: 5
---

# Limitações do LLM e mitigação

## Alucinação

Geração de token plausível sem ancoragem factual. Não é bug — é consequência direta da next-token prediction: o modelo sempre vai gerar algo, mesmo sem informação. Tipos:

- **Alucinação factual**: inventa artigo de lei, CID, dose, autor de paper.
- **Alucinação referencial**: cita documento que não existe; inventa página, súmula, STJ REsp.
- **Alucinação de capacidade**: diz que "executou" ação quando apenas descreveu.

**Mitigação**:

1. RAG com trecho literal + citação de fonte (ver `vector_memory_rag/rag_minimo.md`).
2. Instrução explícita: "se não estiver no contexto, responder 'não consta'".
3. Verificador em segundo passo (hook anti-mentira do Dexter; agente `verificador-100`, `verificador-cids`, `verificador-medicamentos`).
4. Structured output com schema que exige `fonte: string` para cada claim.
5. Temperature 0.

## Cutoff de conhecimento

Modelo treinado com dados até uma data. Claude Opus 4 tem cutoff em janeiro de 2025 [TODO/RESEARCH: confirmar]. Nada que aconteceu depois existe no modelo.

**Mitigação**:

- Injetar data atual no system prompt.
- Buscar jurisprudência/lei atual via ferramenta (MCP jurídico, WebSearch, MCP PubMed).
- Nunca perguntar "qual a lei atual" sem passar o texto da lei.

## Confabulação

Variante de alucinação em que o modelo fabrica justificativa coerente para conclusão incorreta. Sintoma: responde com segurança e detalhe sobre algo errado. Particularmente perigoso em perícia — laudo confiante e errado é pior que laudo omisso.

**Mitigação**:

- Pedir raciocínio explícito antes da conclusão (chain-of-thought).
- Cross-check com segundo modelo (LLM-as-judge, ver `evaluation_guardrails/como_avaliar_saida_llm.md`).
- Exigir citação literal do trecho que sustenta cada conclusão.

## Vieses

Aprendidos do corpus de treino. Efeitos relevantes:

- **Viés de autoridade**: dá mais peso a fontes "prestigiadas" (USP, Harvard, STF) independente da qualidade do argumento.
- **Viés de recência no contexto**: informação no fim do prompt pesa mais que no meio.
- **Viés de confirmação**: se o usuário afirma X, modelo tende a concordar. Crítico em perícia — perito deve contestar, não concordar.
- **Viés cultural anglófono**: conceitos de common law podem contaminar raciocínio sobre direito brasileiro.

**Mitigação**:

- System prompt que exige contraponto obrigatório.
- Perguntas neutras, sem sugerir conclusão ("o que há neste laudo?" em vez de "confirma que este laudo está errado?").
- Revisar saída com foco em "onde o modelo concordou demais".

## Falta de grounding temporal

Modelo não tem noção do tempo passar entre turns. Se a sessão dura 4 horas, ele trata cada chamada como "agora". Datas em documentos precisam ser explícitas.

## Falta de meta-cognição real

Modelo não sabe o que sabe. Se perguntado "você tem certeza?", vai gerar resposta plausível sobre certeza — não é introspecção verdadeira. "Calibration" (correspondência entre confiança declarada e probabilidade real de acerto) é fraca.

**Mitigação**: não confiar em autoavaliação do próprio modelo. Usar verificadores externos.

## Context rot

Em sessões longas, qualidade degrada mesmo dentro da janela. Modelo começa a repetir, perder instruções iniciais, confundir papéis. Regra: compactar em >80% da janela; reiniciar sessão para tarefas novas.

## Referências

- Ji et al., "Survey of Hallucination in Natural Language Generation", 2023.
- Anthropic, "Measuring Faithfulness in Chain-of-Thought Reasoning", 2023.
