# FLOW 04 — Relatorio periodico de progresso

## Objetivo

Gerar snapshots de progresso do Maestro ao final de cada rodada e/ou semanalmente, alimentando o Dr. Jesus com estado real sem que ele precise abrir múltiplos arquivos.

## Gatilho

- Fim de rodada (obrigatório, manual).
- Cron semanal J01 (diário 07h) quando ativo — hoje manual.
- Chamada explícita: "gerar relatório de progresso".

## Entradas

| artefato | caminho | observação |
|----------|---------|------------|
| TASKS_MASTER | `Maestro/TASKS_MASTER.md` | fonte de verdade de tarefas |
| TASKS_NOW | `Maestro/TASKS_NOW.md` | foco da sessão atual |
| CHANGELOG | `Maestro/CHANGELOG.md` | histórico de mudanças |
| NEXT_SESSION_CONTEXT | `Maestro/NEXT_SESSION_CONTEXT.md` | contexto a atualizar |
| Último snapshot | `reports/progress_snapshot.md` | para diff de progresso |

## Passos

1. Ler `TASKS_MASTER.md` e contar: total, concluídas, parciais, bloqueadas, planejadas.
2. Ler `TASKS_NOW.md` e extrair top 3 ações em andamento.
3. Ler `CHANGELOG.md` e listar mudanças desde último snapshot.
4. Calcular `%_panorama` = (concluídas + 0.5 × parciais) / total × 100.
5. Escrever `reports/progress_snapshot.md` (sobrescreve o anterior).
6. Escrever `reports/execution_report_roundN.md` (acumula; nunca sobrescreve rodada anterior).
7. Atualizar `NEXT_SESSION_CONTEXT.md` com próxima ação mínima.
8. Logar em `logs/flow_04_YYYY-MM-DD.log`.

## Saídas

| artefato | comportamento |
|----------|--------------|
| `reports/progress_snapshot.md` | sobrescrito a cada execução (sempre atual) |
| `reports/execution_report_roundN.md` | acumula; N incrementa por rodada |
| `NEXT_SESSION_CONTEXT.md` | atualizado |
| `logs/flow_04_YYYY-MM-DD.log` | entrada nova |

## Métricas obrigatórias (sem inventar)

- Número de tarefas: total / concluídas / parciais / bloqueadas.
- `%_panorama` calculado (não estimado).
- Blocos avançados na rodada.
- Blocos travados com motivo.
- Próximo micro-passo sugerido (1 frase).

## Falhas conhecidas / Rollback

| falha | sintoma | rollback |
|-------|---------|----------|
| `TASKS_MASTER.md` ausente | FileNotFoundError | abortar; alertar Dr. Jesus |
| % calculado > 100% | erro de contagem | fixar manualmente; não publicar |
| Sobrescrita de rodada anterior | execution_report_roundN errado | restaurar de git ou `_arquivo/` |

## Status

- Operacional (manual).
- Executado na Rodada 1 (2026-04-22).
- Automação via `scripts/report_daily.py`: pendente (backlog B009).
- Cron J01: planejado, não ativo.
