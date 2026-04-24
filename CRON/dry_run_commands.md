# CRON — comandos em modo seco (dry-run apenas)

**NAO EXECUTAR sem autorização. Todos os comandos abaixo são apenas para validação de sintaxe e paths.**

Executar sempre com `--dry-run` ou flags equivalentes. Logar saída em `logs/dry_run/` antes de qualquer ativação real.

---

## J01 — Relatório matinal (diário 07h)

```bash
# dry-run: gera saída em logs/dry_run/j01_YYYY-MM-DD.md sem enviar Telegram
mkdir -p "$HOME/Desktop/STEMMIA Dexter/Maestro/logs/dry_run"
python3 "$HOME/Desktop/STEMMIA Dexter/Maestro/scripts/report_daily.py" \
  --dry-run \
  --output "$HOME/Desktop/STEMMIA Dexter/Maestro/logs/dry_run/j01_$(date +%Y-%m-%d).md"
```

**Pré-condição:** `scripts/report_daily.py` — ainda não criado (backlog B009).

---

## J02 — Backup local (diário 23h)

```bash
# dry-run: lista o que seria copiado sem copiar nada
rsync -av --dry-run \
  --exclude 'data/' \
  --exclude '.git/' \
  "$HOME/Desktop/STEMMIA Dexter/Maestro/" \
  "$HOME/Desktop/STEMMIA Dexter/_arquivo/backups/maestro_$(date +%Y-%m-%d)/"
```

**Verificar:** destino não deve incluir `data/`. Confirmar com `grep 'data/'` na saída do dry-run.

---

## J03 — Auditoria Dexter (semanal domingo 20h)

```bash
# dry-run: gera relatório sem alterar filesystem
python3 "$HOME/Desktop/STEMMIA Dexter/Maestro/scripts/audit_dexter.py" \
  --report-only \
  --output-dir "$HOME/Desktop/STEMMIA Dexter/Maestro/logs/dry_run/"
```

**Pré-condição:** `scripts/audit_dexter.py` — ainda não criado (backlog B008).

---

## J04 — Resumo semanal Telegram (segunda 07h)

```bash
# dry-run: imprime mensagem que seria enviada, sem chamar API Telegram
python3 "$HOME/Desktop/STEMMIA Dexter/Maestro/scripts/notify_telegram.py" \
  --tipo semanal \
  --dry-run
```

**Pré-condição:** `scripts/notify_telegram.py` — ainda não criado (backlog B010).  
**Verificar:** saída não deve conter PII.

---

## J05 — Detecção de projetos parados >30d (mensal dia 1)

```bash
# dry-run: lista pastas sem modificação há 30+ dias
find "$HOME/Desktop/STEMMIA Dexter/" \
  -maxdepth 3 \
  -type d \
  -not -path '*/data/*' \
  -not -path '*/MUTIRAO/*' \
  -not -path '*/PROCESSOS-PENDENTES/*' \
  -not -path '*/.git/*' \
  | while read d; do
      last=$(stat -f '%m' "$d" 2>/dev/null)
      now=$(date +%s)
      diff=$(( (now - last) / 86400 ))
      if [ "$diff" -gt 30 ]; then
        echo "$diff dias | $d"
      fi
    done \
  | sort -rn \
  | tee "$HOME/Desktop/STEMMIA Dexter/Maestro/logs/dry_run/j05_$(date +%Y-%m-%d).txt"
```

**Observação:** este comando pode ser executado como dry-run sem risco (somente leitura).

---

## J06 — Ingestão de novas conversas coladas (horário)

```bash
# dry-run: lista arquivos novos em conversations/raw/ sem processar
find "$HOME/Desktop/STEMMIA Dexter/Maestro/conversations/raw/" \
  -name '*_full.md' \
  -newer "$HOME/Desktop/STEMMIA Dexter/Maestro/logs/flow_01_last_run.marker" \
  2>/dev/null \
  | tee "$HOME/Desktop/STEMMIA Dexter/Maestro/logs/dry_run/j06_$(date +%Y-%m-%d).txt"
```

**Pré-condição:** `logs/flow_01_last_run.marker` criado pelo script de ingestão após cada run.

---

## J07 — Sync dashboard web (diário 06h55)

```bash
# dry-run: monta payload JSON sem empurrar ao DB
python3 "$HOME/Desktop/STEMMIA Dexter/Maestro/scripts/sync_dashboard.py" \
  --dry-run \
  --output "$HOME/Desktop/STEMMIA Dexter/Maestro/logs/dry_run/j07_$(date +%Y-%m-%d).json"
```

**Pré-condição:** `scripts/sync_dashboard.py` — ainda não criado. DB: [TODO/RESEARCH].  
**Verificar:** JSON gerado não deve conter PII.

---

## Procedimento de ativação de job

Antes de ativar qualquer job em cron/launchd/OpenClaw:

1. Executar dry-run acima e salvar saída em `logs/dry_run/`.
2. Verificar saída: sem PII, sem `data/`, sem paths inesperados.
3. Apresentar ao Dr. Jesus para aprovação.
4. Ativar **um job por vez**.
5. Observar por 7 dias antes de ativar o próximo.
6. Logar em `logs/cron_<id>.log` desde o primeiro dia.

## Status

- Todos os comandos: dry-run validados em design.
- Scripts Python J01/J03/J04/J06/J07: ainda não criados.
- J02 (rsync) e J05 (find): prontos para dry-run real assim que autorizado.
- Nenhum job ativo.
