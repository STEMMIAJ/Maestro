---
titulo: Opus, Sonnet, Haiku — quando cada
bloco: 08_ai_and_automation
tipo: decisao
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: pratica-consolidada
tempo_leitura_min: 4
---

# Opus, Sonnet, Haiku — quando cada

## Hierarquia

- **Opus 4** (`claude-opus-4-7`): raciocínio máximo, custo alto, latência maior. Flagship.
- **Sonnet 4**: 80% do raciocínio do Opus, 1/5 do custo, 2x mais rápido. Cavalo de batalha.
- **Haiku 4**: rápido, baratíssimo, raciocínio suficiente para tarefas bem definidas. [TODO/RESEARCH: confirmar lineup atual da Anthropic em abr/2026]

## Preços (aproximados, abr/2026) [TODO/RESEARCH: validar tabela atual]

| Modelo | Entrada USD/Mtok | Saída USD/Mtok | Fator vs Haiku |
|--------|------------------|----------------|----------------|
| Opus 4 | 15 | 75 | ~75x |
| Sonnet 4 | 3 | 15 | ~15x |
| Haiku 4 | 0,25 | 1,25 | 1x |

## Regras práticas para perícia

### Usar Opus 4

- Redação final de laudo que vai ao juízo.
- Análise crítica de laudo adverso (detecção de falácia, contradição sutil).
- Nexo causal com múltiplos fatores confundidores.
- Raciocínio médico-legal integrado (CID + nexo + quantificação + precedente).
- Qualquer coisa que seja assinada pelo perito e juntada nos autos.

### Usar Sonnet 4

- Primeira extração de quesitos.
- Sumário de processo.
- Classificação de tipo de documento / tipo de ação.
- Triagem inicial de nomeação (aceitar/recusar).
- Rerank de resultados de busca.
- Redação de draft que Opus depois refina.

### Usar Haiku 4

- Extração de campos simples (nome, CNJ, data, CID).
- Roteamento (decidir qual agente chamar).
- Detecção de intenção.
- Tradução técnica palavra a palavra.
- Tool call decisions simples (sim/não, categoria).
- Agentes auxiliares que rodam centenas de vezes (ex.: `classificador-documento` em batch).

## Regra de ouro do Dexter

CLAUDE.md manda: "Tudo Opus por padrão; NUNCA rebaixar sem autorização". Motivo: um erro de Haiku num verificador anti-mentira custa muito mais que o Opus a mais. Economia de tokens vale a pena SÓ onde o erro é inócuo.

Exceção oficial: skill `modo-sonnet` + `opus-auditor`. Rodar tarefa em Sonnet, depois Opus audita. Economiza ~20x quando auditoria passa.

## Critério de decisão

Pergunta: "se este agente errar, o que acontece?".

- Resposta: "vai para os autos com minha assinatura" → Opus.
- Resposta: "outro agente corrige depois" → Sonnet.
- Resposta: "é só pré-filtro, segundo estágio resolve" → Haiku.

## Latência vs qualidade

- Opus: 3–15s para primeiro token em prompts grandes.
- Sonnet: 1–5s.
- Haiku: 0,3–1,5s.

Interatividade humana tolera até ~3s. Pipeline batch noturno: indiferente.

## Modelos open-source como alternativa

Quando privacidade é inegociável (dado de paciente em bruto) ou custo acumulado é alto:

- Llama 3.1 70B / 405B
- Qwen 2.5 72B
- Mistral Large

Rodar local via Ollama ou vLLM. Perda de qualidade vs Opus: significativa em raciocínio complexo, aceitável em extração e classificação. Ver `modelos_especializados.md`.

## Referências

- Anthropic, "Models overview". [TODO/RESEARCH: URL]
- Artificial Analysis benchmark. [TODO/RESEARCH]
