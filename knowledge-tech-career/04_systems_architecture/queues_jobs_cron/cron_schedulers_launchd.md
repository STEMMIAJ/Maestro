---
titulo: Cron, launchd, Celery Beat e Airflow
bloco: 04_systems_architecture
tipo: comparacao
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: estado-da-arte
tempo_leitura_min: 5
---

# Cron, launchd, Celery Beat e Airflow

Executar tarefa "toda noite às 3h", "a cada 15 min", "segunda a sexta às 8h" é recorrente em qualquer sistema. Ferramenta certa varia com o contexto.

## cron (Linux, macOS)

Padrão Unix. Um arquivo `crontab` por usuário. Linha = 5 campos de tempo + comando.

```cron
# m  h  dom mon dow  comando
  0  3  *   *   *   /home/user/backup.sh
  */15 * *   *   *   /home/user/poll_djen.py
  0  8  *   *   1-5  /home/user/relatorio_diario.sh
```

Prós: universal, zero deps, simples.
Contras:
- Sem retry nativo.
- Sem log estruturado (cuidar com `>> /var/log/...`).
- Silenciosamente para se máquina dormir na hora (comum em laptop).
- Variáveis de ambiente mínimas (problema em jobs que precisam PATH custom).
- Se job anterior ainda rodando quando próximo dispara → sobreposição.

## launchd (macOS)

Substituto do cron no macOS. Mais poderoso: executa ao conectar, a cada N segundos, no login, com recuperação de falha.

```xml
<!-- ~/Library/LaunchAgents/com.stemmia.monitor.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
  <key>Label</key><string>com.stemmia.monitor</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/jesus/stemmia-forense/automacoes/monitor.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Hour</key><integer>3</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
  </array>
  <key>StandardOutPath</key><string>/tmp/monitor.out</string>
  <key>StandardErrorPath</key><string>/tmp/monitor.err</string>
  <key>RunAtLoad</key><true/>
</dict>
</plist>
```

Carregar: `launchctl load ~/Library/LaunchAgents/com.stemmia.monitor.plist`
Listar: `launchctl list | grep stemmia`

Prós: se máquina estava off na hora, executa ao acordar (com `StartCalendarInterval`). Integra com login do usuário (LaunchAgent) ou sistema (LaunchDaemon).
Contras: XML verboso. Só macOS.

Dr. Jesus já tem `com.jesus.mesa-sweep` rodando 3h diário. Sistema pericial usa launchd para monitor 3x/dia.

## systemd timers (Linux moderno)

Alternativa robusta ao cron em distros recentes.

```ini
# /etc/systemd/system/monitor.service
[Service]
ExecStart=/usr/bin/python3 /opt/monitor.py

# /etc/systemd/system/monitor.timer
[Timer]
OnCalendar=*-*-* 03,12,18:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

`systemctl enable --now monitor.timer`. Com `Persistent=true`, executa ao bootar se horário foi perdido.

## Celery Beat (Python)

Scheduler do Celery. Dispara tarefas Celery em cron-like. Celery worker executa.

```python
from celery import Celery
from celery.schedules import crontab

app = Celery("app", broker="redis://localhost")

app.conf.beat_schedule = {
    "consulta-datajud": {
        "task": "tasks.consultar_datajud",
        "schedule": crontab(minute="*/15"),
    },
    "relatorio-diario": {
        "task": "tasks.relatorio",
        "schedule": crontab(hour=8, minute=0),
    },
}
```

Prós: integrado ao app Python, retry, distribuído, monitor (Flower).
Contras: operar Celery é peso (broker, worker, beat separados); Dramatiq + APScheduler é alternativa mais simples.

Alternativas Python:
- **APScheduler** — in-process, simples. Bom para monólito.
- **Dramatiq** + cron externo — clean.
- **RQ Scheduler** — extensão do RQ.
- **Temporal** / **Prefect** / **Dagster** — workflow orchestration moderno, overkill para script simples.

## Airflow

Orquestrador de workflow. DAGs (Directed Acyclic Graphs) Python. Cada DAG = tarefas com dependências + schedule.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

with DAG(
    "pipeline_pericia",
    start_date=datetime(2026, 1, 1),
    schedule="0 3 * * *",
    catchup=False,
) as dag:
    extract = PythonOperator(task_id="extract", python_callable=baixar_datajud)
    transform = PythonOperator(task_id="transform", python_callable=parse)
    load = PythonOperator(task_id="load", python_callable=salvar_db)
    extract >> transform >> load
```

Prós: UI web, dependências complexas, retry granular, histórico, sensores (esperar arquivo chegar).
Contras: peso gigante (Postgres + scheduler + webserver + worker). Overkill para < 10 DAGs.

Alternativas modernas: **Prefect** (Python, mais leve), **Dagster** (data engineering), **Temporal** (workflows de longa duração com estado).

## Matriz de decisão

| Caso | Ferramenta |
|------|-----------|
| 1-5 tarefas simples, 1 servidor | **cron** (Linux) / **launchd** (Mac) |
| Script Python único, in-process | **APScheduler** |
| App Python com jobs, 1 servidor | **Dramatiq** + cron |
| App Python distribuído, fila | **Celery Beat** |
| Pipeline ETL/ML com dependências | **Airflow** / **Prefect** / **Dagster** |
| Workflow longo com estado (billing) | **Temporal** |
| Automação de OS (backup, sweep) | **cron** / **launchd** / **systemd timer** |
| Trigger remoto (webhook) | **não é cron — usar fila** |

## Monitoração

Cron silencioso = cron morto. Em produção:
- **Cronitor**, **Healthchecks.io** — ping de sucesso a cada run; alerta se falhar.
- **dead man's switch**: job envia "vivo" a cada run; se n runs passam sem ping, alerta.

Script exemplo:

```bash
#!/bin/bash
/path/to/job.sh && curl -fsS https://hc-ping.com/UUID
```

## Para o sistema pericial

Já em uso (descrito em memória):
- `com.jesus.mesa-sweep` — 3h diário, launchd.
- Monitor processos — launchd 3x/dia (segundo `project_monitor_fontes.md`).

Recomendado adicionar:
- **Healthchecks.io** free tier — cada launchd faz curl no fim. Alerta no Telegram se falhar.
- **Script `/Users/jesus/stemmia-forense/automacoes/monitorar_launchds.sh`** — lista launchctl, compara com esperado, avisa faltantes.

Não migrar para Airflow. Escala atual não justifica.

## Armadilhas

- Cron no laptop que dorme — falhas invisíveis. launchd lida; cron não.
- PATH/env diferente em cron — script roda "manualmente" ok, falha em cron. Usar `env` absoluto.
- Jobs sobrepondo — próximo começa antes do anterior terminar. Usar `flock` ou lock no app.
- Sem log — quando falhar, ninguém sabe. Redirecionar stdout+stderr para arquivo rotacionado.
- Timezone confuso — cron em UTC vs app em BRT. Padronizar UTC; converter só na UI.
