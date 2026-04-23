---
titulo: Quando usar o quê — decisão rápida
tipo: relatorio_governanca
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
---

# When to Use What

Uma página. Decisão em segundos. Imprimir se preciso.

## Matriz de decisão

| Eu quero... | Ferramenta | Como |
|---|---|---|
| **Construir algo novo** (script, README, spec, relatório) | Claude Code | editor + prompt |
| **Refatorar/consertar código** | Claude Code | prompt + diff review |
| **Salvar estado atual** | Git | `git add -A && git commit -m "..."` |
| **Backup remoto** | Git | `git push origin main` |
| **Voltar a um estado anterior** | Git | `git checkout <sha>` ou `git revert` |
| **Lembrar de uma decisão antiga** | Maestro | `openclaw memory search "<tema>"` |
| **Achar onde anotei X** | Maestro | `openclaw memory search "X"` |
| **Revisar o que está estagnado** | Maestro | job `knowledge-refresh-quarterly` |
| **Promover conversa/rascunho a memória** | Maestro (sugere) + humano (aprova) + Git (commit) | ciclo promote |
| **Importar material externo** | Pipeline em `14_automation/ingestion_pipelines/` | spec → script → inbox |
| **Listar skills que tenho evidência** | Maestro + pipeline skill_mapping | spec em `14_automation/scripts/` |
| **Validar links de fontes** | Pipeline source_validation | spec em `14_automation/scripts/` |
| **Ver o que mudou desde sexta** | Git | `git log --since="friday"` |
| **Comparar duas notas** | Git ou editor | `git diff` / diff visual |
| **Pesquisar biblioteca/API atual** | Context7 MCP | dentro do Claude Code |
| **Pesquisar jurisprudência BR** | orq-jurisprudencia | conforme CLAUDE.md global |
| **Pesquisar artigo médico** | PubMed MCP + buscador-academico | paralelo |

## Regras de atalho

1. **"Onde eu..."** → Maestro.
2. **"Quero criar..."** → Claude Code.
3. **"Antes de quebrar, salva."** → Git commit.
4. **"Antes de perder, sobe."** → Git push.
5. **"Sumiu do meu radar."** → Maestro review queue.
6. **Nunca** editar arquivo crítico sem commit prévio.
7. **Nunca** depender da memória do Claude entre sessões — converter em Markdown.

## Sinais de que estou usando a ferramenta errada

- Tentando "pesquisar" no Git grep → era Maestro.
- Pedindo Claude para "lembrar" o que decidi → era Maestro (e memória não existia; criar agora).
- Pedindo Maestro para "criar" código → era Claude Code.
- Confiando no undo do editor ao invés de commit → era Git.
- Importando conversa externa direto em `15_memory/promoted/` sem passar por `16_inbox/` → é pipeline de ingestão; passa pelo staging.

## Ver também

- `maestro_vs_claude_vs_git.md`
- `maestro_operational_model.md`
