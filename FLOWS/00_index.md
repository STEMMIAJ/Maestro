# FLOWS — indice

Fluxos operacionais do Maestro. Cada um mapeia: objetivo → gatilho → entradas → passos → saídas → falhas/rollback → status.

| id | arquivo | objetivo resumido | status |
|----|---------|-------------------|--------|
| 01 | 01_conversa_externa.md | Ingerir conversa externa e extrair memória operacional | planejado (1ª execução semi-manual feita) |
| 02 | 02_auditoria_dexter.md | Varredura periódica do ecossistema STEMMIA Dexter | planejado |
| 03 | 03_memoria_curada.md | Ciclo de curadoria do MEMORY.md consolidado | planejado |
| 04 | 04_relatorio_periodico.md | Geração de relatórios de progresso por rodada | operacional (manual) |
| 05 | 05_notificacoes.md | Disparo de notificações via bot Telegram | planejado |
| 06 | 06_backup.md | Backup local + remoto (camadas 1-2 disponíveis, 3 RESEARCH) | parcial |
| 07 | 07_dashboard.md | Coleta de metadados para dashboard web | planejado |
| 08 | 08_integracao_openclaw.md | Uso do OpenClaw como camada de automação | bloqueado |

## Estrutura padrão de cada flow

```
## Objetivo
## Gatilho
## Entradas
## Passos (numerados)
## Saídas
## Falhas conhecidas / Rollback
## Status
```

## Regras transversais

- Nenhum flow escreve fora de `Maestro/` sem autorização explícita.
- Nenhum flow toca `data/`, `MUTIRAO/`, `PROCESSOS-PENDENTES/`.
- Todo flow que falha grava em `logs/flow_<N>_error_YYYY-MM-DD.log`.
- Falhas de flows que dependem de rede (FTP, Telegram, DB) são toleradas sem rollback de filesystem.
