# RULES — indice

Regras operacionais do Maestro. Cada arquivo cobre um domínio. Estas regras são complementares a `~/.claude/CLAUDE.md` e `~/Desktop/STEMMIA Dexter/CLAUDE.md` — não as substituem.

| arquivo | domínio | princípio central |
|---------|---------|------------------|
| 01_naming.md | Nomenclatura de arquivos e paths | sem acento / espaço / ç em automação |
| 02_scope.md | Escopos de leitura/escrita por diretório | escrever só em Maestro/ sem autorização |
| 03_privacy_retention.md | Privacidade, retenção, dados de pacientes | nunca processar PII em memória/logs |
| 04_completeness.md | Critérios de conclusão de fase/tarefa | evidência verificável obrigatória |
| 05_change_control.md | Controle de mudança, rollback, backup | read antes de editar; nunca apagar sem confirmação |

## Hierarquia de precedência

1. `~/.claude/CLAUDE.md` (global — sempre prevalece).
2. `~/Desktop/STEMMIA Dexter/CLAUDE.md` (projeto Dexter).
3. `Maestro/CLAUDE.md` (este projeto).
4. `Maestro/RULES/*.md` (regras operacionais desta pasta).

## Atualização

Novas regras operacionais surgidas em conversas ou sessões devem ser adicionadas no arquivo de domínio pertinente. Marcar `<!-- atualizado em YYYY-MM-DD -->` no rodapé do arquivo editado.
