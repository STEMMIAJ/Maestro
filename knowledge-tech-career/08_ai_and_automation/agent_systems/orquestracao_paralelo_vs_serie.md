---
titulo: Orquestração — paralelo vs série
bloco: 08_ai_and_automation
tipo: tecnica
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: tecnico-consolidado
tempo_leitura_min: 4
---

# Orquestração — paralelo vs série

## Regra geral

Paralelo sempre que possível. Série só quando há dependência real de dados. CLAUDE.md global exige: "NUNCA fazer sequencial o que pode ser paralelo".

## Quando série é obrigatória

Existe dependência: passo B precisa do output de A.

- Download do processo → extração de peças → sumário (cada passo depende do anterior).
- Busca de jurisprudência → filtrar relevantes → citar no laudo.
- Gerar plano → validar plano → executar plano.

## Quando paralelo é correto

Tarefas independentes entre si.

- Buscar jurisprudência no TJMG + STJ + TST simultaneamente (`orq-jurisprudencia` com 3 buscadores paralelos, já no Dexter).
- Ler 5 exames diferentes para extrair achados.
- Pedir opinião de 3 agentes diferentes sobre o mesmo laudo (self-consistency).
- Buscar em base local + PubMed + WebSearch ao mesmo tempo.

Ganho: tempo total = max(Ti), não soma(Ti). Se cada busca leva 20s, 3 em paralelo = 20s, em série = 60s.

## Custo de coordenação

Paralelo não é de graça. Overhead:

- Orquestrador que dispara e junta resultados (tokens + lógica).
- Possível redundância (3 agentes encontram a mesma jurisprudência).
- Debugging fica mais difícil (falha em um, demais continuam).
- Rate limit: 5 chamadas paralelas ao mesmo provedor podem bater teto.

Regra prática: paralelo compensa quando cada subtarefa leva > 5s E número de subtarefas < 10 E custo individual é previsível.

## Padrões de orquestração

### MapReduce

- **Map**: distribuir N itens iguais a N agentes idênticos em paralelo.
- **Reduce**: agregador junta resultados.

Exemplo: extrair CIDs de 20 laudos → 20 agentes paralelos extraem → agregador deduplica e ordena por frequência.

### Fanout-fanin

- **Fanout**: orquestrador distribui subtarefas DIFERENTES a especialistas.
- **Fanin**: reúne saídas heterogêneas num documento único.

Exemplo Dexter: `orq-analise-completa` dispara `extrator-partes` + `extrator-informacoes-doc` + `resumidor-fatos` + `analisador-quesitos-auto` em paralelo; junta num dossiê.

### Pipeline

Série de estágios, cada um com entrada tipada vindo do anterior. Ex.: `triador-peticao` → `classificador-tipo-acao` → `gerador-peticao-complexo` → `peticao-verificador` → `peticao-gerador-pdf`.

### Router

Orquestrador analisa entrada e decide qual especialista chamar (um só). Exemplo: classificador decide se processo é trabalhista, previdenciário ou cível; roteia para agente especializado.

### Planner + Workers

Um agente gera plano estruturado (lista de tarefas com dependências); executor rodam as tarefas respeitando dependências. Tarefas sem dependência rodam em paralelo. Padrão do GSD no Dexter (`gsd-planner` + `gsd-executor`).

## Implementação no Claude Code

- Paralelo entre tool calls: emitir várias chamadas no mesmo turn (Claude executa em paralelo nativamente).
- Paralelo entre agentes: usar SDK + `asyncio` ou `concurrent.futures` no Python. Ou N8N com nós paralelos.
- Série: um tool call por turn, cada um esperando resultado.

## Anti-padrão

- Serializar por hábito quando subtarefas são independentes.
- Paralelizar tudo quando há dependência óbvia (resultado caótico).
- Paralelizar 50 agentes sem rate limit → bloqueio na API.

## Referências

- Anthropic, "Building effective agents" (seção patterns). [TODO/RESEARCH: URL]
