# Modelos LLM — opcoes iniciais (qualitativo)

Gerado em 2026-04-22. Sem numeros. Rever apos pesquisa de precos em USD/BRL.

## Modelos considerados

### Claude Opus 4 / Opus 4.6 / Opus 4.7
- Pros: maior qualidade em sintese longa, arquitetura, decisoes ambiguas; aderencia a regras (CLAUDE.md).
- Contras: latencia maior; custo maior por token de saida; pode ser excessivo em tarefas repetitivas.
- Uso recomendado: arquitetura, sintese de conversa, revisao cruzada, laudos complexos.

### Claude Sonnet 4 / 4.6
- Pros: equilibrio qualidade/velocidade; bom em codigo e prosa media.
- Contras: perde precisao em ambiguidade alta.
- Uso recomendado: redacao ordinaria, revisao, refatoracao.

### Claude Haiku 4.5
- Pros: muito rapido; barato; bom em chunking, classificacao, extracao determinista.
- Contras: falha em sintese longa, argumentos juridicos complexos.
- Uso recomendado: ingestao em massa, chunk/extract_action_items, tagging.

### Outros
- GPT-4 / GPT-4.1: comparavel a Opus em alguns casos; diferente aderencia a personas.
- Gemini 2.x: forca em rede/context longo; nao testado aqui.
- Modelos locais (Llama, Mistral): privacidade; depende de hardware; qualidade inferior para laudos.

## Mapeamento de uso
| Tarefa | Modelo sugerido | Motivo |
|--------|-----------------|--------|
| Laudo pericial inicial (draft) | Opus 4/4.7 | qualidade critica |
| Revisao de laudo | Sonnet 4.6 | rapido, custo menor, pega erros evidentes |
| Chunk/extract (pipeline) | Haiku 4.5 | volume, determinismo |
| Classificacao de documento | Haiku 4.5 | baixo custo |
| Sintese de conversa longa | Opus 4.7 | cobertura e coerencia |
| Triagem de urgencia | Haiku 4.5 | velocidade |

## Vale Opus 4.7 via API para este projeto?
### Vantagens previstas
- Acesso programatico fora do Claude Code (scripts, cron, bot Telegram).
- Controle fino de temperatura, max_tokens, cache.
- Integra com dashboard (sumarizacao on-demand).

### Pontos de atencao
- Custo por token (precos nao avaliados aqui — RESEARCH).
- Gerenciamento de chaves (secrets).
- Limites de rate.
- Necessidade real: boa parte do uso ja e coberto pelo Claude Code + subagentes.

### Dependencia
- pesquisa de precos (RESEARCH).
- volume esperado (RESEARCH — depende de quantas rodadas/dia).
- comparar contra: apenas Claude Code; apenas Haiku API + Claude Code para Opus; hibrido.

## Decisao sugerida (para validacao do Dr. Jesus)
Manter Opus 4.7 via Claude Code como motor principal. Adotar API Claude direto apenas quando:
- houver fluxo programatico sem interacao humana;
- ou o valor da automacao justificar pagar por tokens.

Nao decidir nesta rodada.
