# FASE 7 — Cron heartbeat (ADIADA em 2026-04-23)

**Razao da adiamento:** Dr. Jesus priorizou pipeline pericial real (FASE B do HANDOFF) + preservacao da conversa Perplexity (FASE A) sobre automacao de monitoramento.

**Quando retomar:** depois de FASE 4, 8, 9 rodarem. Ou quando o sistema ja tiver 1 semana de uso real e houver dor de "descobrir que indexer quebrou sem aviso".

## O que a FASE 7 entrega
1. `~/Library/LaunchAgents/com.stemmia.maestro.heartbeat.plist`
2. Roda a cada 30 min
3. Executa `python3 Maestro/scripts/heartbeat.py`
4. heartbeat.py:
   - Confere que `maestro.db` nao foi modificado < 1h atras (indexer vivo)
   - Confere `dashboard/data.json` gerado nas ultimas 2h
   - Confere OpenClaw gateway respondendo em 127.0.0.1:18789
   - Escreve linha em `Maestro/logs/heartbeat.log`
   - Se algum check falhar: INSERT em tabela `heartbeat` com status=error
   - Opcional: se Telegram bot ativo, alerta Dr. Jesus

## Requisitos previos
- FASE 9 Telegram (se alerta automatico desejado)
- Uso real de ~1 semana para calibrar thresholds (1h? 2h? 30min?)

## Ativacao
`launchctl load ~/Library/LaunchAgents/com.stemmia.maestro.heartbeat.plist`
(permissao precisa ser liberada de DENY para ASK em `settings.json` na hora).

## Comandos para verificar quando retomar
```bash
ls ~/Library/LaunchAgents/com.stemmia.maestro.heartbeat.plist 2>/dev/null && echo "ja instalado" || echo "nao instalado"
launchctl list | grep maestro
tail -20 ~/Desktop/STEMMIA\ Dexter/Maestro/logs/heartbeat.log 2>/dev/null
```

## Lembrete criado em
2026-04-23 01:52, conforme ordem do Dr. Jesus: "a fase sete cara por enquanto me lembra isso depois".
