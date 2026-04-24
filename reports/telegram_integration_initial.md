# Integracao Telegram — inicial (planejamento, zero envio)

Gerado em 2026-04-22. Nenhuma mensagem sera enviada nesta rodada.

## Cenarios

### C01 — Relatorio matinal (07:00)
- Disparador: cron J01.
- Conteudo: "N processos com prazo em 48h; M pendentes; ultima ingestao de conversa: DD/MM".
- Formato: texto curto + bullet list.
- Frequencia: diaria, so dias uteis.

### C02 — Alerta de prazo pericial iminente
- Disparador: detector no Dexter (URGENCIA.json).
- Conteudo: CNJ + prazo + link local ao FICHA.
- Frequencia: imediata quando detecta; rate limit 1 por CNJ por dia.

### C03 — Confirmacao de job
- Disparador: fim bem-sucedido de pipeline (ingestao, backup, auditoria).
- Conteudo: "J02 OK. 124 arquivos, 58MB. Duracao 12s."
- Frequencia: baixa, ignora se silencioso nao for valioso.

### C04 — Aviso de erro
- Disparador: excecao em qualquer cron.
- Conteudo: job id + erro resumido + arquivo de log.
- Frequencia: imediata, sem rate.

### C05 — Resumo semanal (dom 20:00)
- Disparador: cron J04.
- Conteudo: tarefas concluidas, progresso %, novos bloqueios, 3 insights.
- Frequencia: semanal.

### C06 — Comandos bot (interacao)
- `/status` -> estado geral
- `/urgencias` -> top 5 prazos
- `/ingerir` -> instruir pipeline (gatilho)
- `/silencio 2h` -> pausa notificacoes

## Arquitetura sugerida
- Polling (getUpdates) — mais simples, nao exige servidor publico.
- Webhook — exige URL HTTPS (stemmia.com.br); considerar so apos C06 ativo.

## Origem dos dados
- FLOW 01 (ingestoes).
- FLOW 02 (auditoria).
- FLOW 04 (relatorios).
- FLOW 07 (dashboard) — espelho para bot ter dados mais recentes.

## Dependencias
- Token do bot (RESEARCH, nao tocar nesta rodada).
- Chat ID privado do Dr. Jesus.
- Python script ou OpenClaw hook.

## Riscos
- Spam ao Dr. Jesus — mitigar com dedup + rate + horario.
- Vazamento de PII — nunca enviar dados clinicos; so metadados / CNJ.

## Fluxos documentados (sem implementacao)

Abaixo os fluxos de dados que existem apenas no papel. Nenhuma linha de codigo foi escrita. Nenhum token de bot foi configurado.

### Fluxo: relatorio matinal (C01)
```
cron J01 (07:00 dias uteis)
  -> scripts/report_daily.py
     -> le TASKS_NOW.md + URGENCIA.json dos processos
     -> formata mensagem (N prazos, M pendentes, ultima ingestao)
  -> telegram_notify.py --chat-id <ID> --msg "<texto>"
     -> Telegram API (getUpdates polling)
        -> Dr. Jesus recebe no celular
```

### Fluxo: alerta de prazo (C02)
```
detector no Dexter (cronjob ou file-watch)
  -> le URGENCIA.json de cada processo
     -> se prazo <= 48h e nao notificado hoje
        -> formata alerta (CNJ + prazo + path FICHA)
  -> telegram_notify.py
     -> deduplica por CNJ (arquivo de controle local)
```

### Fluxo: confirmacao de job (C03)
```
qualquer script cron (J02..J07)
  -> ao terminar bem: telegram_notify.py --level=info --msg "J0X OK. <stats>"
  -> ao falhar: telegram_notify.py --level=error --msg "J0X FALHOU. <resumo> <log_path>"
```

### Fluxo: resumo semanal (C05)
```
cron J04 (dom 20:00)
  -> scripts/report_weekly.py
     -> le CHANGELOG.md + TASKS_MASTER.md + logs/
     -> calcula: tarefas concluidas, % progresso, novos bloqueios
     -> extrai 3 insights (heuristico: tasks mais velhas)
  -> telegram_notify.py
```

### Fluxo: comandos bot (C06) — mais complexo, somente apos C01 ativo
```
polling loop (getUpdates a cada 5s)
  -> parse /status -> retorna openclaw status (texto)
  -> parse /urgencias -> retorna top 5 de URGENCIA.json
  -> parse /silencio Xh -> grava flag local; suprime envios por X horas
  -> parse /ingerir -> dispara pipeline conversation_ingestion (dry-run apenas)
```

**Dependencia bloqueante para todos os fluxos:**
- Token do bot Stemmia (nao configurado, nao tocar nesta rodada).
- Chat ID privado do Dr. Jesus (nao armazenado aqui — TODO/RESEARCH).
- Scripts `report_daily.py`, `report_weekly.py`, `telegram_notify.py` (esqueletos existem em conversation_ingestion, implementacao real — backlog B007).

## Status atual
Documentado. Zero envios. Zero codigo de bot implementado.
