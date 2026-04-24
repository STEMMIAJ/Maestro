# FLOW 01 — Conversa externa -> memoria

## Objetivo

Transformar uma conversa externa bruta (Perplexity, ChatGPT, Claude.ai, etc.) em memória operacional estruturada: decisões, entidades, ações e contexto de próxima sessão.

## Gatilho

- Dr. Jesus cola conversa em `conversations/raw/<fonte>_YYYY-MM-DD_full.md`.
- OU captura automática via MCP chrome (browser já logado) quando possível.
- OU FLOW chamado manualmente: "ingerir conversa".

## Entradas

| artefato | caminho | obrigatório |
|----------|---------|-------------|
| Conversa bruta | `conversations/raw/<fonte>_YYYY-MM-DD_full.md` | sim |
| Metadados | `conversations/raw/<fonte>_YYYY-MM-DD_metadata.json` | gerado no passo 2 |
| MEMORY.md atual | `Maestro/MEMORY.md` | sim (leitura) |
| TASKS_MASTER atual | `Maestro/TASKS_MASTER.md` | sim (leitura) |

## Passos

1. Verificar que `conversations/raw/<fonte>_YYYY-MM-DD_full.md` existe e não está vazio (`wc -l`).
2. Gravar `conversations/raw/<fonte>_YYYY-MM-DD_metadata.json` (fonte, data, tamanho, sha256).
3. Rodar `conversation_ingestion/ingest_conversation.py` → `conversations/clean/<fonte>_YYYY-MM-DD_clean.md`.
4. Rodar `chunk_conversation.py` → `conversations/chunks/<fonte>_YYYY-MM-DD_chunks.json`.
5. Rodar `extract_action_items.py` → `conversations/processed/<fonte>_YYYY-MM-DD_actions.json`.
6. Rodar `generate_memory_files.py` → `memory/YYYY-MM-DD.md` + `reports/conversation_*.md` (5 arquivos).
7. Rodar `generate_session_checkpoint.py` → `NEXT_SESSION_CONTEXT.md` + `TASKS_NOW.md`.
8. Atualizar `TASKS_MASTER.md` e `CHANGELOG.md` manualmente (Claude ou Dr. Jesus).
9. Disparar FLOW 03 (curadoria) se MEMORY.md cresceu mais de 20 linhas.

## Saídas

| artefato | caminho |
|----------|---------|
| Conversa limpa | `conversations/clean/<fonte>_YYYY-MM-DD_clean.md` |
| Chunks | `conversations/chunks/<fonte>_YYYY-MM-DD_chunks.json` |
| Ações extraídas | `conversations/processed/<fonte>_YYYY-MM-DD_actions.json` |
| Memória do dia | `memory/YYYY-MM-DD.md` |
| Relatórios (5) | `reports/conversation_master_summary.md` etc. |
| MEMORY.md | delta claro com data |
| TASKS_NOW.md | refletindo top ações |
| NEXT_SESSION_CONTEXT.md | ação mínima da próxima sessão |

## Falhas conhecidas / Rollback

| falha | sintoma | rollback |
|-------|---------|----------|
| Conversa vazia ou truncada | `wc -l` < 10 | abortar no passo 1; não gerar artefatos |
| PII detectada em bruto | nomes reais no texto | substituir `[PACIENTE_X]` antes de prosseguir (RULES/03) |
| Script Python falha | traceback em stderr | logar em `logs/flow_01_error_YYYY-MM-DD.log`; não apagar clean/ |
| MEMORY.md corrompido | leitura falha | restaurar de `_arquivo/backups/` ou git |

## Status

- Fluxo definido e documentado.
- Scripts em esqueleto funcional (`conversation_ingestion/`).
- Primeira execução feita semi-manualmente (Rodada 1, 2026-04-22).
- Automação completa: pendente (backlog B006).
