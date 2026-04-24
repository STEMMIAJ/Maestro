# Privacidade e retencao

## Base legal

Este sistema processa documentos de perícia médica judicial sujeitos ao sigilo profissional médico (CFM 1.605/2000), ao segredo de justiça e à LGPD (Lei 13.709/2018). As regras abaixo são mínimas e não substituem análise jurídica específica.

## Dados de pacientes (PII sensível)

- **NUNCA** copiar, citar, processar ou logar: nomes reais, CPFs, RGs, datas de nascimento completas, CIDs, diagnósticos, histórias clínicas, laudos, prontuários.
- Se aparecer acidentalmente em conversa colada → substituir **antes** de qualquer processamento:
  - nome real → `[PACIENTE_X]`
  - CPF → `[CPF_REDACTED]`
  - CID → `[CID_REDACTED]`
  - diagnóstico → `[DIAGNOSTICO_REDACTED]`
- Scripts do `conversation_ingestion/` devem incluir filtro de PII antes de gravar em `clean/`.

## Conversas externas (Perplexity, ChatGPT, etc.)

- Brutos em `conversations/raw/`: manter **local apenas** (excluir do `.gitignore` se necessário).
- Processados em `conversations/clean/` e `memory/`: podem ser versionados **se sem PII**.
- `_metadata.json`: nunca conter PII (apenas fonte, data, tamanho, hash).
- CNJ de processos: permitido em metadados se necessário para rastreabilidade.

## Logs

- `logs/*.log`: sem trechos de laudos, histórias clínicas ou diagnósticos reais.
- CNJ de processo: permitido quando estritamente necessário para auditoria de execução.
- Dados de paciente em log → falha de segurança; reportar imediatamente; apagar entrada.

## Retenção

| artefato | retenção mínima | retenção máxima | responsável |
|----------|----------------|----------------|-------------|
| `conversations/raw/` | 180 dias | indefinida | Dr. Jesus decide |
| `memory/YYYY-MM-DD.md` | permanente | — | nunca apagar |
| `logs/` | 1 ano | rotar anualmente (manual) | Dr. Jesus |
| `reports/` | permanente | — | nunca apagar |
| `_arquivo/backups/` | 30 backups locais | purgar manualmente | Dr. Jesus |

## Backup e armazenamento remoto

- Atual: git local no repo pai STEMMIA Dexter (com `conversations/raw/` no `.gitignore`).
- Futuro (RESEARCH): dump criptografado em `stemmia.com.br` — decisão pendente em `reports/database_options_initial.md`.
- **Nunca** subir dado não criptografado para qualquer nuvem pública.
- Chave de criptografia: `~/.config/maestro/` (modo 600, fora do git, fora do Maestro).

## Auditoria de conformidade

- FLOW 01 passo 4 valida PII antes de gerar `clean/`.
- FLOW 05 passo 4 valida PII antes de enviar Telegram.
- FLOW 07 passo 6 valida PII antes de empurrar ao DB.
- Qualquer falha de PII → gravar em `logs/pii_block_YYYY-MM-DD.log` + abortar o passo.

<!-- atualizado em 2026-04-24 -->
