# Resumo mestre da conversa — 2026-04-22

Fonte: `conversations/raw/perplexity_conversation_2026-04-22_full.md`
(4440 linhas, ~140k chars, lida integralmente em 22/04/2026).

## Objetivo geral da conversa

Dr. Jesus (perito medico judicial, TEA + TDAH) buscou com o Perplexity:

1. Ajuda para criar um banco de dados de laudos periciais medicos judiciais
   reais (fontes, taxonomia, prompts para Claude, avaliacao de qualidade).
2. Desenho de um sistema integrado de governanca pessoal: Claude Code +
   OpenClaw + Dexter, com memoria, auditoria, automacao e dashboard.

A conversa evolui do eixo 1 (banco de laudos) para o eixo 2 (governanca
integrada) e termina com um comando-mestre pronto para colar no Claude Code
que cria o projeto hoje chamado `Maestro`.

## Visao do sistema integrado

- Dexter = universo local (pasta-mae `STEMMIA Dexter` no desktop).
- Claude Code = executor local forte, com CLAUDE.md e settings por escopo.
- OpenClaw = supervisao, cron, memoria indexada, tasks, dashboard, logs.
- Perplexity = arquiteto externo, taxonomia, prompts, auditoria.
- Dr. Jesus = validador/decisor, nao executor.
- `stemmia.com.br` = site e futura dashboard web.
- Bot Stemmia = canal de relatorios/avisos no Telegram (planejado).
- Banco de dados = projeto paralelo (laudos) + infra para o Maestro.

## Objetivos do projeto para o Dr. Jesus (perito medico)

- Parar de perder ideias entre sessoes.
- Reduzir sobrecarga cognitiva com interface visual e passos pequenos.
- Automatizar auditoria da pasta Dexter (projetos parados, duplicacoes,
  arquivos orfaos, markdowns obsoletos).
- Indexar memoria pesquisavel (semantica) sobre seu proprio trabalho.
- Criar pipeline para transformar qualquer conversa importante em memoria
  operacional reutilizavel.
- Futuramente: dashboard web para operar tudo sem depender do terminal.
- Futuramente: receber relatorios do sistema via Telegram.
- Estudar laudos periciais reais para aprender por reconstrucao (afinidade
  autistica por estrutura pronta) e otimizar proprios laudos.

## O que esta solido

- Divisao de papeis entre Perplexity, Claude Code, OpenClaw, Dr. Jesus.
- Estrutura de pastas do projeto Maestro (AGENTS, RULES, FLOWS, CRON,
  SCRIPTS, CONFIG, DATA, WEB-UI, conversations, memory, logs, reports,
  docs/openclaw-official).
- Lista de agentes com missao, escopo, entradas, saidas, proibicoes,
  criterio de completude.
- Filosofia de memoria: `MEMORY.md` + `memory/YYYY-MM-DD.md` + reports.
- Regras de seguranca: sem acento em paths, sem instalar sem necessidade,
  sem publicar nada, sem inventar dados.
- Ordem de execucao por fases (0–8) para a primeira rodada.
- Formato obrigatorio de ordens ao Claude (papel, objetivo, escopo,
  entradas, saidas, proibicoes, completude).
- Pipeline de ingestao de conversas (`conversation_ingestion/`).

## O que esta em aberto

- Modelo ideal (Opus 4.7 via API vale a pena?) — nao decidido.
- Custos — nao quantificados, marcados como TODO/RESEARCH.
- Banco de dados (Supabase x alternativas + backup no site) — a comparar.
- Arquitetura concreta da dashboard em `stemmia.com.br` — so principios.
- Stack e hospedagem do bot Stemmia — nao mencionados.
- Integracao com projeto GSD pre-existente no repo — nao mencionada na
  conversa, TODO/RESEARCH.
- Como o projeto paralelo de banco de laudos periciais se conecta ao
  Maestro — eixo 1 da conversa ficou esbocado, sem roadmap proprio.
- Baixar artefatos do ecossistema Claude: politica de retencao ainda nao
  fechada; so principios.

## Linha de raciocinio reaproveitavel

- Decomposicao em tarefas curtas rende melhor que pedir tudo de uma vez ao
  Claude.
- Saida do Claude deve ser em blocos padronizados (tabela + listas), nunca
  texto solto, para reduzir bagunca mental.
- Comecar por 1 nicho (ex.: Previdenciario > Auxilio-acidente > Coluna) no
  eixo do banco de laudos, antes de generalizar.
- Primeiro fundacao, depois regras, depois inventario, depois OpenClaw,
  depois Claude Code acoplado, depois cron, depois UI.

## Principio final da conversa

Utilidade real, continuidade entre sessoes, reaproveitamento de contexto,
minimizar a necessidade do Dr. Jesus reexplicar tudo.
