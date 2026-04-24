# Decisoes tomadas na conversa — 2026-04-22

Fonte: `conversations/raw/perplexity_conversation_2026-04-22_full.md`.

Decisoes efetivamente acordadas durante a conversa (nao propostas soltas).

## 1. Estrutura de pastas

- Criar projeto em `~/Desktop/STEMMIA Dexter/openclaw-control-center/`
  (hoje renomeado para `Maestro`, futuro `Maestro`).
- Arvore oficial:

```
Maestro/
  README.md
  CLAUDE.md
  OPENCLAW-ARCHITECTURE.md
  INTEGRATION-PLAN.md
  TASKS_NOW.md
  TASKS_MASTER.md
  MEMORY.md
  NEXT_SESSION_CONTEXT.md
  CHANGELOG.md
  CHECKLISTS/
  AGENTS/
  RULES/
  FLOWS/
  CRON/
  SCRIPTS/
  CONFIG/
  DATA/
  WEB-UI/
  conversations/{raw,processed}/
  memory/
  logs/
  reports/
  docs/openclaw-official/
```

- Pipeline Python de ingestao em subprojeto `conversation_ingestion/` dentro
  da pasta Python base de `STEMMIA Dexter`.

## 2. Papel de cada ferramenta

- Perplexity = arquiteto, taxonomia, prompts, auditoria de sistema. Nao
  executa no sistema de arquivos.
- Claude Code = executor local, cria arquivos, agentes, scripts, dentro do
  escopo do projeto, obedecendo CLAUDE.md e settings.
- OpenClaw = supervisao, cron, memoria indexada (`memory index`,
  `memory search`, `memory promote`), tasks, dashboard, logs, health.
- Dr. Jesus = validador, decisor de prioridade, corretor de rumo. Nao faz
  execucao de baixo nivel.

## 3. Filosofia de memoria

- `MEMORY.md` = memoria estavel, curada, durable.
- `memory/YYYY-MM-DD.md` = nota de sessao, corrente.
- `conversations/raw/*` = fontes brutas, nao editar.
- `conversations/processed/*` = derivados estruturados.
- `reports/*` = snapshots e analises.
- OpenClaw indexa `MEMORY.md` + `memory/*.md` para busca semantica.
- Regra: memoria util, nao acumulo. Promover o que for recorrente.

## 4. Convencoes de nomes

- Paths de automacao em ASCII: sem acento, sem espaco, sem ç.
- Markdown para: regras, agentes, fluxos, checklists, relatorios.
- Python para: scripts de transformacao, sumarizacao, indexacao.
- Arquivos de memoria diaria: `memory/YYYY-MM-DD.md`.
- Conversas brutas: `conversations/raw/<origem>_<data>_full.md`.

## 5. Filosofia de auditoria

- O sistema pode ler, indexar, resumir; nao pode apagar nem mover sem
  proposta explicita.
- Todo agente tem escopo de diretorio e proibicoes claras.
- Toda rodada diferencia: executado, planejado, pendente, bloqueado.
- Todo plano grande e dividido em fases com criterio de completude.

## 6. Seguranca (decisoes de limite)

- Nao instalar nada sem necessidade.
- Nao configurar cron real sem aprovacao.
- Nao publicar em Telegram, site ou bot.
- Nao usar credenciais FTP automaticamente.
- Nao modificar producao de `stemmia.com.br`.
- Nao inventar dados/custos/metricas — marcar TODO/RESEARCH.
- "Baixar tudo do Claude" nao e uma decisao; e politica com inventario,
  classificacao e retencao antes de qualquer coleta.

## 7. Formato obrigatorio de ordens ao Claude

Toda ordem deve conter:

- PAPEL
- OBJETIVO
- ESCOPO (diretorios, leitura x escrita)
- ENTRADAS
- SAIDAS esperadas
- PROIBICOES
- CRITERIO DE COMPLETUDE

Saidas em blocos padronizados (tabela + listas), nunca texto solto.

## 8. Ordem de execucao (fases 0–8)

0. Plano de acao + time de agentes.
1. Captura da conversa em `conversations/raw/`.
2. Estrutura de memoria operacional (MEMORY.md, memory/*.md, reports/*).
3. Subprojeto Python `conversation_ingestion/`.
4. Revisao de arquivos do projeto com base na conversa.
5. Documentacao oficial do OpenClaw em `docs/openclaw-official/`.
6. Relatorios iniciais: modelos, custo, DB, Telegram, dashboard.
7. Task list mestra + progresso.
8. Relatorio final + checkpoint.

## 9. UI e integracoes (decisoes de ordem)

- Primeiro usar `openclaw dashboard` nativo.
- Depois desenhar dashboard propria.
- So entao integrar a `stemmia.com.br`.
- Telegram/bot Stemmia entra depois, como canal de relatorios.
- Banco de dados (Supabase x alternativas) avaliado por relatorio, nao
  instalado nesta rodada.

## 10. Projeto paralelo de banco de laudos periciais

Decisoes estruturais (eixo 1 da conversa):

- Taxonomia em arvore: ramo -> situacao pericial -> tema clinico -> tipo
  documental -> ficha de metadados -> avaliacao tecnica -> avaliacao
  judicial -> utilidade pratica.
- 6 categorias iniciais: previdenciaria incapacidade, previdenciaria
  auxilio-acidente, trabalhista nexo/incapacidade, securitaria invalidez,
  civel dano/erro medico, interdicao/capacidade civil.
- Comecar por 1 nicho: Previdenciario > Auxilio-acidente > Coluna.
- Fontes: repositorios academicos, sites de peritos/institutos, sentencas,
  normativos, protocolos AMB/ABMLPM, Justica Federal.
- Diferenciar sempre: laudo real completo, laudo parcial, modelo
  academico, protocolo, quesitos, sentenca sobre laudo, texto explicativo.
- Esse projeto e separado do Maestro, mas compartilha a infra de memoria.
