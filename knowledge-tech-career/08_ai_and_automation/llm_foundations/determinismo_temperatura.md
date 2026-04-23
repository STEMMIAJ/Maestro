---
titulo: Determinismo, temperatura, top_p, seed
bloco: 08_ai_and_automation
tipo: fundamento
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: tecnico-consolidado
tempo_leitura_min: 4
---

# Determinismo, temperatura, top_p, seed

## O problema

O LLM emite, a cada passo, uma distribuição de probabilidade sobre todos os tokens do vocabulário. Como escolher o próximo token determina o comportamento. Três parâmetros controlam isso: `temperature`, `top_p`, `seed`.

## Temperature

Escala os logits (pontuações pré-softmax) antes do softmax. Fórmula: `p_i = softmax(logits_i / T)`.

- `T = 0`: greedy decoding — sempre escolhe o token de maior probabilidade. Determinístico (em teoria). Saída repetível.
- `T = 0.3–0.7`: amostragem balanceada. Levemente criativo, mantém coerência.
- `T = 1.0`: distribuição original do modelo. Já bastante variável.
- `T > 1.0`: achata a distribuição, aumenta aleatoriedade. Útil para brainstorm; péssimo para precisão.

**Para perícia: T = 0 quase sempre.** Exceção: geração de múltiplas hipóteses diagnósticas para depois filtrar.

## Top_p (nucleus sampling)

Em vez de amostrar de todo o vocabulário, amostra só do conjunto mínimo cuja soma de probabilidades atinge `p`. `top_p = 0.9` = amostra dos tokens que juntos somam 90% da probabilidade; ignora cauda.

- Complementa temperature. `T = 0.7 + top_p = 0.9` é combinação comum para redação criativa.
- Com `T = 0`, top_p é irrelevante (só o top-1 é escolhido).

## Top_k

Corta o vocabulário nos k tokens mais prováveis antes de amostrar. Menos usado em modelos modernos; top_p é mais adaptativo.

## Seed

Inicializa o gerador pseudoaleatório da amostragem. Mesmo `seed` + mesma entrada + mesmo `T > 0` = saída idêntica. Anthropic API aceita `seed` em alguns endpoints [TODO/RESEARCH: confirmar disponibilidade atual no Claude API]. OpenAI tem `seed` oficial; Gemini também.

Atenção: determinismo "perfeito" com T=0 não é garantido em produção — batching no servidor, hardware diferente, atualizações do modelo introduzem variação mínima.

## Quando usar cada

| Tarefa | Temperature | top_p |
|--------|-------------|-------|
| Extração de campos de laudo | 0 | — |
| Verificação de fato (verificador anti-mentira) | 0 | — |
| Redação de texto de laudo | 0.2 | 0.9 |
| Brainstorm de hipóteses diagnósticas | 0.7 | 0.95 |
| Tradução técnica | 0 | — |
| Resumo de processo | 0.1 | 0.9 |

## Regra para o Dexter

Todo agente que toma decisão factual (verificadores, classificadores, extratores) usa `T=0`. Todo agente gerador de texto final (redator-laudo, tradutor-tecnico) usa `T=0.1–0.2` para legibilidade sem criatividade descontrolada.

## Referências

- Holtzman et al., "The Curious Case of Neural Text Degeneration" (nucleus sampling), 2019.
- Anthropic API Reference: parâmetros `temperature`, `top_p`. [TODO/RESEARCH: URL]
