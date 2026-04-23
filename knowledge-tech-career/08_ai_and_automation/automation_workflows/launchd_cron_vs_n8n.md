---
titulo: launchd / cron vs N8N
bloco: 08_ai_and_automation
tipo: decisao
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: pratica-consolidada
tempo_leitura_min: 3
---

# launchd / cron vs N8N

Todos agendam tarefas. A diferença está em onde rodam, o que orquestram e a interface.

## cron (Linux / macOS legado)

Agendador nativo Unix. Sintaxe `* * * * *` (min, hora, dia, mês, dia_semana). Edita com `crontab -e`. Cada linha dispara um comando shell.

**Forte em**: simplicidade, zero dependência, roda qualquer coisa.
**Fraco em**: falha silenciosamente, sem UI, sem retry, sem log estruturado, precisa de terminal para depurar.

## launchd (macOS)

Substituto oficial do cron no macOS. Agenda via arquivos `.plist` em `~/Library/LaunchAgents/`. Aceita:

- `StartCalendarInterval` (cron-like).
- `StartInterval` (a cada N segundos).
- `WatchPaths` (roda quando arquivo muda).
- `RunAtLoad` (roda ao boot / login).
- `KeepAlive` (mantém processo vivo).
- `StandardOutPath` / `StandardErrorPath` (log nativo).

Dexter usa launchd extensivamente:
- `com.jesus.mesa-sweep`: sweep diário 03h da `~/Desktop/_MESA/`.
- Monitor de processos 3x/dia.
- Digest da PYTHON-BASE 1x/hora.

**Forte em**: nativo macOS, triggers por arquivo (além de tempo), sobrevive a reboot, sem servidor extra.
**Fraco em**: sintaxe XML plist é chata; sem UI; sem observabilidade além do log; sem orquestração (1 job = 1 comando).

## cron/launchd funcionam quando

- Tarefa é **um script único** (shell, Python, JS).
- Não há dependência de múltiplos serviços externos coordenados.
- Logs em arquivo bastam.
- Falha não precisa de alerta sofisticado (ou o próprio script manda Telegram).

Boa parte da automação pericial do Dexter cabe aqui.

## N8N

Orquestrador visual de nós. Cada workflow é um grafo: trigger → nós → decisão → nós → output. Ver `n8n_zapier_make_comparacao.md`.

## N8N é necessário quando

- Há **múltiplos sistemas coordenados** (PJe + Telegram + Planner + email).
- Lógica condicional complexa com ramificações visuais.
- Equipe não-dev precisa editar o fluxo.
- Retry + backoff + alertas nativos importam.
- UI e histórico de execução são requisito (auditoria).
- Você quer disparar fluxo via webhook externo.

## Tabela de decisão

| Situação | launchd / cron | N8N |
|----------|:---:|:---:|
| Script Python roda 3x/dia | Sim | Overkill |
| Sweep de pasta diário | Sim (launchd WatchPaths ou interval) | Overkill |
| Monitorar DJEN → filtrar → notificar Telegram → atualizar planilha | Possível mas feio | Natural |
| Cadeia com retry + backoff + alert | Gambiarra | Nativo |
| Gatilho por webhook externo | Impossível direto | Nativo |
| Ver histórico das últimas 50 execuções | grep em log | UI completa |
| Dependência só do macOS | Perfeito | Precisa server |
| Compartilhar fluxo com cliente não-dev | Não | Sim |

## Padrão híbrido (melhor dos dois)

Usar launchd para dispara **entrada** no N8N:

- launchd 08h → `curl -X POST https://n8n.srv19105.nvhm.cloud/webhook/monitor-processos`.
- N8N recebe, executa grafo, coordena chamadas.
- launchd mantém autonomia do Mac; N8N coordena a lógica.

Esse é o padrão usado no monitor de processos do Dexter.

## Anti-padrões

- Cron rodando script que depende de 5 serviços externos → falha silenciosa. Migrar para N8N.
- N8N rodando "salvar arquivo em pasta" a cada minuto → overkill. launchd WatchPaths é mais simples.
- cron no macOS moderno → usar launchd, cron está deprecated (funciona, mas sem garantias).

## Referências

- Apple, `man launchd.plist`.
- N8N docs, section "Schedule Trigger".
