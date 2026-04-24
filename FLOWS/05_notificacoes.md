# FLOW 05 — Notificacoes (bot Stemmia no Telegram)

## Objetivo

Entregar ao Dr. Jesus alertas e resumos via bot Telegram (`@stemmiapericia_bot`, chat_id: 8397602236) sem exigir que ele abra o sistema para saber o estado.

## Gatilho

- Eventos disparados por FLOWS 01, 02, 04 (fim de execução).
- Cron J01 (diário 07h) e J04 (segunda 07h) quando ativos.
- Erro em qualquer cron registrado em `logs/`.
- Manual: "enviar resumo Telegram" (com autorização explícita por rodada).

## Entradas

| artefato | caminho | observação |
|----------|---------|------------|
| Bot token | `~/.config/maestro/secrets.env` | [TODO/RESEARCH] não manipular agora |
| chat_id | `8397602236` | canal privado Dr. Jesus |
| Fonte de eventos | `reports/progress_snapshot.md`, `logs/cron_*.log` | conteúdo das mensagens |
| Template de mensagem | `reports/telegram_integration_initial.md` | formato definido |

## Passos

1. Receber evento de FLOW chamador (tipo: matinal / prazo / confirmação / erro / semanal).
2. Selecionar template de mensagem conforme tipo.
3. Preencher template com dados reais do `reports/` ou `logs/`.
4. Validar que nenhuma PII (nome paciente, CPF, CID) está na mensagem.
5. Chamar API Telegram (`POST /sendMessage`) com token de `secrets.env`.
6. Registrar em `logs/flow_05_YYYY-MM-DD.log`: status HTTP, tipo de mensagem.
7. Em caso de falha HTTP: logar e não retentar (evitar spam).

## Cenários previstos

| cenário | gatilho | conteúdo resumido |
|---------|---------|------------------|
| Relatório matinal | J01 07h | X processos com prazo, Y pendentes |
| Alerta de prazo | FLOW 04 detecta <48h | processo CNJ + prazo |
| Confirmação de job | fim de FLOW 01/02 | "pipeline OK" ou "ingestão concluída" |
| Aviso de erro | cron falhou | job, hora, log path |
| Resumo semanal | J04 segunda 07h | progresso semana + próximo passo |

## Saídas

| artefato | descrição |
|----------|-----------|
| Mensagem Telegram | entregue ao Dr. Jesus |
| `logs/flow_05_YYYY-MM-DD.log` | status HTTP + tipo |

## Falhas conhecidas / Rollback

| falha | sintoma | rollback |
|-------|---------|----------|
| Token ausente/inválido | HTTP 401 | logar; não retentar; alertar na próxima sessão Claude |
| PII detectada | bloco de segurança passo 4 | abortar envio; gravar em `logs/flow_05_pii_block.log` |
| Telegram indisponível | HTTP 5xx | logar; desistir (sem retry loop) |
| Formato de mensagem >4096 chars | truncamento | cortar em `...` + link para relatório local |

## Status

- Planejado. Nenhuma mensagem enviada nesta rodada.
- Token: [TODO/RESEARCH] — não manipular.
- Script `scripts/notify_telegram.py`: não criado (backlog B010).
