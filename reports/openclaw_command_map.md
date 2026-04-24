# OpenClaw — mapa fluxo -> comando (PRE-RESEARCH)

Gerado em 2026-04-22. Comandos sao PRESUMIDOS. Substituir pelos reais apos doc oficial.

## Mapa de comandos centrais (por grupo)

Comandos inferidos da conversa Perplexity. Todos marcados PRESUMIDO ate confirmacao.

### Setup e diagnostico
| Comando | Funcao presumida |
|---------|-----------------|
| `openclaw setup` | configuracao inicial do ambiente |
| `openclaw onboard` | assistente de primeiro uso |
| `openclaw configure` | ajustar parametros do projeto |
| `openclaw doctor` | verifica dependencias, configs, saude |
| `openclaw status` | estado geral do sistema |
| `openclaw health` | heartbeat detalhado |

### Agentes
| Comando | Funcao presumida |
|---------|-----------------|
| `openclaw agents` | listar agentes registrados |
| `openclaw agent run <nome>` | executar agente especifico |

### Tasks
| Comando | Funcao presumida |
|---------|-----------------|
| `openclaw tasks` | listar tarefas |
| `openclaw tasks audit` | identificar tarefas paradas/orphas |
| `openclaw tasks maintenance` | limpar tarefas concluidas antigas |

### Memoria
| Comando | Funcao presumida |
|---------|-----------------|
| `openclaw memory status` | estado do indice de memoria |
| `openclaw memory index` | reindexar MEMORY.md + memory/*.md |
| `openclaw memory search <query>` | busca semantica |
| `openclaw memory promote --apply` | elevar entradas para MEMORY.md |

### Cron
| Comando | Funcao presumida |
|---------|-----------------|
| `openclaw cron add --cmd '...'` | criar job |
| `openclaw cron list` | listar jobs |
| `openclaw cron run <id>` | executar job agora |
| `openclaw cron runs <id>` | historico de execucoes |
| `openclaw cron edit <id>` | editar job |
| `openclaw cron remove <id>` | remover job |

### Flows e sessions
| Comando | Funcao presumida |
|---------|-----------------|
| `openclaw flows` | listar fluxos definidos |
| `openclaw sessions` | historico de sessoes |

### Logs e gateway
| Comando | Funcao presumida |
|---------|-----------------|
| `openclaw logs` | ver logs do sistema |
| `openclaw gateway status` | estado do gateway (se existir) |

### Dashboard
| Comando | Funcao presumida |
|---------|-----------------|
| `openclaw dashboard` | abrir dashboard local |
| `openclaw dashboard serve` | servir dashboard via HTTP local |
| `openclaw dashboard --no-open` | iniciar sem abrir browser |

## Mapeamento fluxo -> comando

| Fluxo do Maestro | Comando OpenClaw presumido | Observacao |
|------------------|----------------------------|------------|
| FLOW 01 — Conversa externa | `openclaw memory add --from conversations/processed/<x>_clean.md` | pode nao precisar; Maestro mantem em MD |
| FLOW 02 — Auditoria Dexter | `openclaw task add "audit dexter" && openclaw agent run DEXTER-AUDITOR` | depende de leitura de AGENTS/ |
| FLOW 03 — Memoria curada | `openclaw memory search` + manual | curadoria e humana |
| FLOW 04 — Relatorio periodico | `openclaw cron add --cmd 'python3 scripts/report_daily.py'` | apos script criado |
| FLOW 05 — Notificacoes | `openclaw hook on-error notify telegram` | hook especifico |
| FLOW 06 — Backup | `openclaw cron add --cmd 'rsync ...'` | job J02 |
| FLOW 07 — Dashboard | `openclaw dashboard serve` (local) + cron de sync (remoto) | dois lados |
| FLOW 08 — Integracao | `openclaw init && openclaw status` | bootstrap |

## TODO apos confirmacao
- Trocar comandos presumidos pelos reais.
- Marcar comandos que nao existem em OpenClaw -> migrar para Python base.
- Validar que nomes de argumentos batem.
