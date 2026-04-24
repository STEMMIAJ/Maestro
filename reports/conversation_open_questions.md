# Duvidas abertas — 2026-04-22

Fonte: `conversations/raw/perplexity_conversation_2026-04-22_full.md`.

Tudo que ficou explicitamente em aberto ou depende de pesquisa posterior.

## 1. Modelos

- Qual modelo usar como padrao no Claude Code para o Maestro?
  - Opus 4.7 via API vale a pena para este projeto?
    - Vantagens previstas: qualidade em raciocinio arquitetural.
    - Pontos de atencao: custo, volume de uso com cron, paralelismo de
      agentes.
  - Como comparar com Sonnet/Haiku ou outros provedores para tarefas
    recorrentes de auditoria? Nao mencionado em detalhe na conversa —
    TODO/RESEARCH.
- Qual modelo para cada tipo de job (orquestracao x execucao x resumo x
  busca)? Nao mencionado na conversa — TODO/RESEARCH.

## 2. Custos

- Custo estimado de:
  - API Claude Opus 4.7 no volume previsto.
  - Hospedagem da dashboard em `stemmia.com.br`.
  - DB (Supabase vs alternativas).
  - Eventual OpenAI/outros como fallback.
- Todos marcados como TODO/RESEARCH. Nao inventar numeros.

## 3. Banco de dados

- Supabase vs alternativas (Postgres gerenciado, SQLite local, Turso,
  Neon, etc.). A conversa pede comparacao preliminar, sem numeros.
- Backup local + backup no site: como e onde fazer?
- Integracao com dashboard em `stemmia.com.br`.
- Esquema de tabelas (laudos, memorias, tarefas, agentes, logs) — nao
  definido. TODO/RESEARCH.

## 4. Arquitetura da dashboard

- Rotas sugeridas: `/dashboard-dexter`, `/dashboard-pericias`. Falta
  definir as demais.
- Componentes minimos: cards, listas, filtros — nao detalhados.
- Como reaproveitar design do Planner Stemmia — TODO.
- Autenticacao: nao mencionado — TODO/RESEARCH.
- Como a dashboard consome dados do Maestro local: JSON exportado? API?
  sincronizacao? Nao fechado — TODO/RESEARCH.

## 5. Telegram / bot Stemmia

- Stack do bot (python-telegram-bot? aiogram? n8n?) — nao mencionado na
  conversa — TODO/RESEARCH.
- Hospedagem do bot — nao mencionado — TODO/RESEARCH.
- Quais mensagens o bot recebe primeiro: relatorios de cron, avisos de
  job com falha, resumo diario/semanal. Definicao fina — TODO.
- Politica de privacidade do canal (tem dados de paciente passando?) —
  TODO/RESEARCH.

## 6. Backup

- Backup local: frequencia, formato, destino. Nao definido.
- Backup no site `stemmia.com.br`: como, sem usar FTP agora. TODO.
- Retencao (quanto tempo manter logs, memoria, conversas brutas).
  TODO/RESEARCH.

## 7. Integracao com ecossistema Claude

- Mapear quais artefatos Claude sao uteis indexar (exports, logs,
  prompts, memorias). A conversa decide que isso exige inventario,
  classificacao e politica de retencao antes. Falta concluir cada etapa.
- Privacidade: que memorias podem ser tratadas por automacao?

## 8. Projeto paralelo — banco de laudos periciais

- Como financiar tempo/atencao para isso ao mesmo tempo que o Maestro?
- Que volume inicial buscar (Perplexity sugere 20–30 por categoria).
- Como armazenar PDFs grandes no banco sem violar privacidade.
- Como cruzar laudo com sentenca correspondente.
- Integracao desse banco com OpenClaw memory.

## 9. Nomenclatura final

- Projeto: hoje `Maestro`, previsto `Maestro`. Momento da renomeacao
  definitiva nao esta fechado — TODO.
- OpenClaw pode ser codinome interno; o nome exato do produto/ferramenta
  nao foi confirmado — TODO/RESEARCH.

## 10. Infraestrutura local

- Pasta Python base exata para `conversation_ingestion/` — a conversa
  pede ao Claude Code "localizar automaticamente" e escolher com
  justificativa em log. A decisao final nao foi tomada — TODO.
- Integracao com GSD (ja usado no repo) — nao mencionada na conversa —
  TODO/RESEARCH.

## 11. OpenClaw como produto

- Funciona 100% offline? Necessita servico externo?
- Como autenticar providers de modelo no onboarding?
- `openclaw memory promote --apply` em producao: e seguro hoje? TODO.
- Lista completa de plugins/hooks que se aplicam — precisa dos docs
  oficiais baixados em `docs/openclaw-official/`.
