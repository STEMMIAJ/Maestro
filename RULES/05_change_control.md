# Controle de mudanca

## Antes de editar um arquivo existente

1. `Read` do arquivo (verificar conteúdo atual).
2. Verificar se é gerado automaticamente (marker `<!-- auto-atualizado -->` ou `# auto-generated`).
3. Se gerado: preferir reexecutar o script gerador; não editar manualmente.
4. Se manual: editar via `Edit` (não reescrever do zero) e registrar no `CHANGELOG.md`.
5. Marcar `<!-- atualizado em YYYY-MM-DD -->` no rodapé quando aplicável.

## Antes de criar arquivo novo

1. Verificar se já existe arquivo com finalidade equivalente (`ls`, `grep`).
2. Confirmar que o caminho respeita `RULES/01_naming.md` e `RULES/02_scope.md`.
3. Registrar no `CHANGELOG.md` após criação.

## Antes de apagar

- **NUNCA** apagar sem dupla confirmação do Dr. Jesus (duas mensagens explícitas).
- Preferir mover para `_arquivo/` local: `mv arquivo.md Maestro/_arquivo/arquivo_YYYY-MM-DD.md`.
- Registrar no `CHANGELOG.md`: o que foi movido e por quê.
- Hook `bloquear_limpeza.py` ativo globalmente: rm -rf bloqueado por padrão.

## Rollback por fase

| situação | procedimento |
|----------|-------------|
| Com git local | `git checkout -- <caminho>` ou `git revert <commit>` |
| Sem git | mover arquivos da fase para `_arquivo/fase_N_rollback_YYYY-MM-DD/` |
| Fase inteira | arquivos são isolados por fase; desfazer = mover pasta da fase |

Cada fase do `INTEGRATION-PLAN.md` gera artefatos isolados (não sobrescreve fases anteriores).

## Backup antes de renomear em lote

1. Listar afetados: `find Maestro/ -name "*.py" | tee logs/rename_YYYY-MM-DD.txt`.
2. Salvar lista em `logs/rename_YYYY-MM-DD.txt`.
3. Aplicar renomeação.
4. Verificar: `ls` + diff da lista antes/depois.
5. Registrar no `CHANGELOG.md`.

## Git

- Este projeto opera dentro do repo pai `~/Desktop/STEMMIA Dexter/` (sem repo próprio).
- Convenção de commit: `maestro(<área>): <ação> <artefato>`.
  - Exemplos: `maestro(flows): expande flow 01-08`, `maestro(rules): adiciona critérios completude`.
- Não fazer push sem ordem explícita ("pode fazer push" / "sobe para o remote").
- `conversations/raw/` deve estar no `.gitignore` do repo pai.

## Registro no CHANGELOG

Toda mudança de arquivo fora do fluxo automático deve gerar entrada em `CHANGELOG.md`:

```
## YYYY-MM-DD
- [EDIT] FLOWS/01_conversa_externa.md — adicionadas seções Objetivo, Entradas, Falhas
- [CREATE] FLOWS/00_index.md — tabela de status por flow
- [MOVE] scripts/old_report.py → _arquivo/old_report_2026-04-24.py
```

<!-- atualizado em 2026-04-24 -->
