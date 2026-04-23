---
titulo: "Agendamento de tarefas — cron, launchd, at, systemd timer"
bloco: "06_data_analytics/data_engineering_basics"
tipo: "referencia"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 5
---

# Agendamento de tarefas

Pipeline precisa rodar sozinho. Quatro opções por SO.

## cron (Linux/macOS — legado)

Formato clássico: `minuto hora dia mês dia_semana comando`.

```cron
# roda às 03:00 todo dia
0 3 * * *  /Users/jesus/scripts/extract_datajud.sh >> /tmp/datajud.log 2>&1

# a cada 15 minutos úteis das 8 às 18
*/15 8-18 * * 1-5  /caminho/monitorar.sh
```

- `crontab -e` edita; `crontab -l` lista.
- macOS 10.15+: cron ainda funciona, mas **launchd é preferido** (suporta wake-from-sleep, limites de recursos).

## launchd (macOS — recomendado)

Unidade é um `plist` em `~/Library/LaunchAgents/`.

Exemplo — rodar extract 3x/dia e capturar log:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key>                 <string>com.jesus.datajud-extract</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/Users/jesus/stemmia-forense/automacoes/pipeline_datajud/scripts/run.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
  </array>
  <key>StandardOutPath</key>       <string>/tmp/datajud.out.log</string>
  <key>StandardErrorPath</key>     <string>/tmp/datajud.err.log</string>
  <key>RunAtLoad</key>             <false/>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
</dict></plist>
```

Comandos:

```bash
launchctl bootstrap  gui/$(id -u) ~/Library/LaunchAgents/com.jesus.datajud-extract.plist
launchctl bootout    gui/$(id -u) ~/Library/LaunchAgents/com.jesus.datajud-extract.plist
launchctl kickstart  -k gui/$(id -u)/com.jesus.datajud-extract   # roda já
launchctl list | grep jesus                                      # ver status
```

Vantagens sobre cron:
- Se Mac estava dormindo, launchd roda ao acordar.
- Integração com keychain, notificações, LaunchDaemons vs LaunchAgents (usuário vs sistema).

## at — execução única agendada

```bash
echo "python3 /caminho/relatorio.py" | at 23:00
atq   # lista fila
atrm 3
```

Útil para tarefas pontuais. No macOS moderno, precisa habilitar: `sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.atrun.plist`.

## systemd timer (Linux moderno)

Dois arquivos: `.service` + `.timer`.

`~/.config/systemd/user/etl.service`:
```ini
[Unit]
Description=ETL DATAJUD
[Service]
Type=oneshot
ExecStart=/usr/bin/bash /home/jesus/etl/run.sh
```

`~/.config/systemd/user/etl.timer`:
```ini
[Unit]
Description=Roda ETL 3x/dia
[Timer]
OnCalendar=*-*-* 08,13,19:00:00
Persistent=true
[Install]
WantedBy=timers.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now etl.timer
systemctl --user list-timers
journalctl --user -u etl.service
```

Vantagens sobre cron: logs centralizados (`journalctl`), dependências entre units, suporte a `Persistent=true` (roda missed schedules).

## Qual escolher

| Cenário | Escolher |
|---|---|
| macOS, Mac fica desligando | launchd |
| Linux server moderno | systemd timer |
| Tarefa única agendada | at |
| Portabilidade máxima | cron (mas cuidado com sleep no macOS) |

## Armadilhas comuns

1. **Caminho**: cron/launchd não herdam PATH do shell interativo — usar caminhos absolutos ou setar env.
2. **Diretório de trabalho**: default é home. Usar `cd` explícito no script.
3. **Locale**: tarefas sem `LANG` podem quebrar em acentos. Setar `export LANG=pt_BR.UTF-8`.
4. **Overlap**: job que demora mais que o intervalo — usar flock / lockfile.
5. **Silêncio**: sempre redirecionar stdout/stderr para log, nunca deixar `2>/dev/null` em produção.
