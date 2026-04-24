# Como rodar o MONITOR-FONTES

## 1. Rodada manual (teste ou avulso)

### Passo 1 — Chrome debug aberto e logado
```
Duplo-click em ~/Desktop/MONITOR-FONTES/scripts/abrir_chrome_debug.command
```
Janela do Chrome abre com 2 abas: AJ TJMG e AJG. Logar em cada uma.

### Passo 2 — Rodar orquestrador
```bash
python3 ~/Desktop/MONITOR-FONTES/scripts/orquestrador.py
```

Saída esperada:
```
[HH:MM:SS] MONITOR-FONTES — orquestrador iniciado
[HH:MM:SS] → AJ TJMG: iniciando
[HH:MM:SS]   ✓ AJ TJMG: N itens → aj.json
[HH:MM:SS] → AJG Justica Federal: iniciando
...
[HH:MM:SS] Concluido.
```

### Passo 3 — Ver resultado
- Lista mestre: `dados/processos-consolidados.json`
- CSV: `dados/processos-consolidados.csv`
- Dashboard: abrir `dashboard/index.html`

---

## 2. Ativar cron diário (uma vez só)

```bash
ln -sf ~/Desktop/MONITOR-FONTES/config/launchd/com.stemmia.monitor-fontes.plist \
       ~/Library/LaunchAgents/com.stemmia.monitor-fontes.plist
launchctl load ~/Library/LaunchAgents/com.stemmia.monitor-fontes.plist
launchctl list | grep monitor-fontes
```

Saída esperada: linha com label `com.stemmia.monitor-fontes`.

A partir daqui, roda todo dia 7h automaticamente.

---

## 3. Forçar execução agora (sem esperar 7h)

```bash
launchctl start com.stemmia.monitor-fontes
```

---

## 4. Ver logs

```bash
# Log do dia
tail -50 ~/Desktop/MONITOR-FONTES/logs/orquestrador-$(date +%Y-%m-%d).log

# Último stderr do launchd
tail -50 ~/Desktop/MONITOR-FONTES/logs/launchd-stderr.log
```

---

## 5. Desativar cron

```bash
launchctl unload ~/Library/LaunchAgents/com.stemmia.monitor-fontes.plist
```

---

## 6. Reset completo (apaga histórico)

```bash
rm -f ~/Desktop/MONITOR-FONTES/dados/consolidado-*.json
rm -rf ~/Desktop/MONITOR-FONTES/dados/historico/*
rm -f ~/Desktop/MONITOR-FONTES/dados/processos-consolidados.*
```

Na próxima rodada, todos os CNJs serão tratados como novos (alerta Telegram
grande).
