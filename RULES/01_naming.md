# Regras de nomeacao

## Proibido em paths automatizados

- Acentos (á, é, í, ó, ú, ã, õ, â, ê, etc.).
- Espaços (usar `_` ou `-`).
- C-cedilha (ç).
- Caracteres especiais (!, ?, $, %, &, @, #, etc.).
- Letras maiúsculas em nomes de arquivo Python.
- Nomes com espaço em argumentos de linha de comando (sem aspas = quebra).

## Permitido

- ASCII: letras a-z, dígitos 0-9, `_`, `-`, `.`.
- Datas em ISO: `YYYY-MM-DD`.
- Scripts Python: `snake_case.py`.
- Documentos Markdown: `MAIUSCULAS.md` OU `snake_case.md` (consistente por pasta).
- Diretórios estruturais do Maestro: `MAIUSCULAS/` (ver Exceções).

## Padrões por tipo de artefato

| tipo | padrão | exemplo |
|------|--------|---------|
| Script Python | `snake_case.py` | `ingest_conversation.py` |
| Relatório Markdown | `snake_case_YYYY-MM-DD.md` | `dexter_audit_2026-04-22.md` |
| Conversa bruta | `<fonte>_conversation_YYYY-MM-DD_full.md` | `perplexity_conversation_2026-04-22_full.md` |
| Metadados | `<fonte>_YYYY-MM-DD_metadata.json` | `perplexity_2026-04-22_metadata.json` |
| Log | `<flow>_YYYY-MM-DD.log` | `flow_01_2026-04-22.log` |
| Backup | `maestro_YYYY-MM-DD/` | `maestro_2026-04-22/` |
| Checkpoint Python | `generate_session_checkpoint.py` | — |

## Exemplos corretos / incorretos

| correto | incorreto | motivo |
|---------|-----------|--------|
| `perplexity_conversation_2026-04-22_full.md` | `conversa perplexity 22-04.md` | espaço, sem ISO |
| `ingest_conversation.py` | `Ingest_Conversa.py` | maiúscula, acento |
| `reports/conversation_master_summary.md` | `reports/Relatório_Execução.md` | acento, maiúscula |
| `dexter_audit_2026-04-22.md` | `auditoria-dexter.md` | sem data; dificulta ordenação |

## Exceções documentadas

- Diretórios estruturais do Maestro (`AGENTS/`, `RULES/`, `FLOWS/`, `CONFIG/`, `CRON/`): maiúsculas por convenção visual.
- Pastas do Dexter com acento já existentes: **não renomear** (risco de quebrar scripts legados que usam o nome com acento como string literal).
- `CLAUDE.md`, `README.md`, `MEMORY.md`, `CHANGELOG.md`: maiúsculas por convenção de projeto.

<!-- atualizado em 2026-04-24 -->
