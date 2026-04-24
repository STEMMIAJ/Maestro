# CRON — plano (NAO ATIVO)

Todos os jobs abaixo são **planejados**. Nenhum está configurado em `crontab`, `launchd` ou OpenClaw.  
Para dry-runs testáveis, ver `CRON/dry_run_commands.md`.

## Jobs previstos

| id | frequência | horário | descrição | flow disparado | script | status |
|----|-----------|---------|-----------|---------------|--------|--------|
| J01 | diário | 07:00 | Relatório matinal de perícias | FLOW 04 + FLOW 05 | `scripts/report_daily.py` | planejado |
| J02 | diário | 23:00 | Backup local Maestro/ | FLOW 06 | `rsync` (built-in) | planejado |
| J03 | semanal dom | 20:00 | Auditoria Dexter | FLOW 02 | `scripts/audit_dexter.py` | planejado |
| J04 | semanal seg | 07:00 | Resumo semanal Telegram | FLOW 05 | `scripts/notify_telegram.py` | planejado |
| J05 | mensal dia 1 | 06:00 | Detectar projetos parados >30d | FLOW 02 | `find` (built-in) | planejado |
| J06 | horário | :00 | Ingestão de novas conversas coladas | FLOW 01 | `ingest_conversation.py` | planejado |
| J07 | diário | 06:55 | Sync payload dashboard web | FLOW 07 | `scripts/sync_dashboard.py` | planejado |

## Dependências por job

| id | pré-condição | bloqueio atual |
|----|-------------|---------------|
| J01 | `scripts/report_daily.py` criado | backlog B009 |
| J02 | nenhuma (rsync disponível) | sem bloqueio técnico; aguarda autorização |
| J03 | `scripts/audit_dexter.py` criado | backlog B008 |
| J04 | `scripts/notify_telegram.py` criado + token configurado | backlog B010 + RESEARCH |
| J05 | nenhuma (find disponível) | sem bloqueio técnico; aguarda autorização |
| J06 | `ingest_conversation.py` implementado (não só esqueleto) | backlog B006 |
| J07 | `scripts/sync_dashboard.py` criado + DB confirmado | backlog + RESEARCH |

## Ativação (quando decidir)

### Via launchd (Mac — preferido)

```
~/Library/LaunchAgents/com.jesus.maestro.<id>.plist
```

Exemplo de estrutura plist (NÃO ATIVAR — apenas referência):

```xml
<!-- NÃO ATIVAR — apenas referência de estrutura -->
<key>Label</key>
<string>com.jesus.maestro.j02</string>
<key>ProgramArguments</key>
<array>
  <string>/bin/bash</string>
  <string>-c</string>
  <string>rsync -av --exclude 'data/' "$HOME/Desktop/STEMMIA Dexter/Maestro/" ...</string>
</array>
<key>StartCalendarInterval</key>
<dict>
  <key>Hour</key><integer>23</integer>
  <key>Minute</key><integer>0</integer>
</dict>
```

Ver `Maestro/futuro/B1-resolucao.md` para proposta de plist B1 (resolução de B1 — manual).

### Via OpenClaw (quando desbloqueado)

```bash
# sintaxe presumida — confirmar após docs/openclaw-official/
openclaw cron add --id J02 --schedule "0 23 * * *" --cmd "rsync ..."
```

## Regras de ativação

1. **Um job por vez**: ativar, observar 7 dias, só então ativar o próximo.
2. **Dry-run antes de ativar**: executar `CRON/dry_run_commands.md` e logar resultado.
3. **Log obrigatório**: cada job loga em `logs/cron_<id>.log` desde o dia 1.
4. **Falhas**: notificar via FLOW 05 (Telegram) + gravar em `logs/cron_<id>_errors.log`.
5. **PII**: nenhum job toca `data/`, `MUTIRAO/` ou documentos de pacientes.
6. **Rollback de job**: `launchctl unload` (launchd) ou `openclaw cron remove --id <id>`.

## Status atual

- Documentado e planejado.
- **ZERO jobs ativos.**
- Próximo passo: criar `scripts/audit_dexter.py` (B008) e testar J05 (`find`) como dry-run.
