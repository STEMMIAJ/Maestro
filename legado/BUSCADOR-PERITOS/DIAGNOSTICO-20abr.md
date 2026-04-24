# Diagnóstico — Buscador de Oportunidades para Perito

**Data:** 2026-04-20
**Status geral:** 3 launchd relacionados falhando, todos pelo mesmo motivo raiz.

---

## Causa raiz única: TCC (Acesso Total ao Disco)

No macOS, processos disparados pelo launchd **precisam de permissão "Full Disk Access"** para ler `~/Desktop/`. Os 3 agents executam `python3` (system binary) que **não tem essa permissão**, logo batem em `Operation not permitted`.

Isso explica:
- monitor-datajud parou
- monitor-fontes parou
- Radar parou (20/03/2026)

---

## Detalhamento por agent

### 1. `com.stemmia.monitor-datajud` (exit 1)

**Erro exato:**
```
PermissionError: [Errno 1] Operation not permitted:
'/Users/jesus/Desktop/STEMMIA Dexter/LISTA-COMPLETA-PUSH.json'
```

**Script:** `/Users/jesus/stemmia-forense/scripts/monitor_completo.py` (linha 97)
**Log:** `/Users/jesus/stemmia-forense/logs/monitor-datajud-err.log`

**Ação recomendada:**
- Opção A: **Conceder Full Disk Access a `/usr/bin/python3`** em Ajustes > Privacidade e Segurança > Acesso Total ao Disco.
- Opção B: Mover `LISTA-COMPLETA-PUSH.json` de `~/Desktop/STEMMIA Dexter/` para `~/stemmia-forense/dados/` e atualizar path no script.
- **Recomendo B** — tira dependência de permissão.

---

### 2. `com.stemmia.monitor-fontes` (exit 2)

**Erro exato:**
```
can't open file '/Users/jesus/Desktop/MONITOR-FONTES/scripts/orquestrador.py':
[Errno 1] Operation not permitted
```

**Script:** `/Users/jesus/Desktop/MONITOR-FONTES/scripts/orquestrador.py` (existe, verificado)
**Log:** `/Users/jesus/Desktop/MONITOR-FONTES/logs/launchd.stderr.log`

**Fato adicional:** o script existe, tem código completo (orquestrador + consolidador + alerta + testes). O plano em `.claude/plans/monitor-fontes-intimacoes.md` marca 0/9 tasks mas na prática arquivos existem. Contradição entre plano e realidade.

**Ação recomendada:**
- Opção A: Full Disk Access para `/usr/bin/python3` (resolve todos de uma vez).
- Opção B: Mover `/Users/jesus/Desktop/MONITOR-FONTES/` para `/Users/jesus/stemmia-forense/src/monitor-fontes/` e atualizar plist.
- **Recomendo B** — tudo fora do Desktop para evitar TCC.

---

### 3. Radar / buscador-peritos (parou 20/03/2026)

**Erro exato:**
```
/bin/bash: /Users/jesusnoleto/Desktop/Radar/scanner.sh: Operation not permitted
```

**Problemas:**
1. Path hardcoded em `/Users/jesusnoleto/` — é o usuário do **Mac Mini antigo**. Migrou para Mac atual `/Users/jesus/` mas o plist não foi atualizado.
2. Pasta `~/Desktop/Radar/` não existe mais no Mac atual — só em iCloud (`~/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Radar/`).
3. **Nenhum plist em `~/Library/LaunchAgents/` referencia Radar** — o plist original sumiu, só ficou o log acumulando erros.

**Ação recomendada:**
- Recriar plist `com.stemmia.radar.plist` com path correto apontando para iCloud
- OU: mover pasta Radar de iCloud para `~/stemmia-forense/src/radar/` (recomendado — iCloud causa sync delay e TCC extra)

---

## Plano de reativação (ordem sugerida)

1. **Conceder Full Disk Access a `/usr/bin/python3` e `/bin/bash`**
   - Ajustes do Sistema > Privacidade e Segurança > Acesso Total ao Disco
   - Adicionar os 2 binários manualmente (Finder > Cmd+Shift+G > `/usr/bin/python3` e `/bin/bash`)
   - Isso resolve monitor-datajud e monitor-fontes imediatamente

2. **Recriar plist do Radar** (ou decidir mover pasta)

3. **Contornar bloqueio WAF JusBrasil HTTP 403** (problema separado):
   - Ver `05-DOCS-PLANOS/BLOQUEIO-JusBrasil-403.md`
   - Alternativas: JUDIT.io, Escavador API, DataJud API (foco atual do plano monitor-fontes)

4. **Executar manualmente uma vez** cada agent para confirmar funcionamento antes de depender do launchd.

---

## Verificações feitas

- `launchctl list | grep stemmia` → 10 agents listados, 3 com exit code != 0
- Plist content lido: `monitor-fontes.plist`, `monitor-datajud.plist`
- Logs de erro lidos (tail -40): 3 agents
- Estrutura `MONITOR-FONTES/scripts/` listada: 9 arquivos presentes
- Crontab verificado: scanner domingo 20h existe mas aponta para `~/Desktop/Automações/12_cron/` (não tem Radar)
- Pasta `~/Desktop/Radar/` — não existe (só em iCloud)

---

## Arquivos relevantes

| Arquivo | Propósito |
|---|---|
| `/Users/jesus/Library/LaunchAgents/com.stemmia.monitor-datajud.plist` | Agenda 7h/19h monitor DataJud |
| `/Users/jesus/Library/LaunchAgents/com.stemmia.monitor-fontes.plist` | Agenda 7h/13h/19h orquestrador 5 fontes |
| `/Users/jesus/stemmia-forense/scripts/monitor_completo.py` | Script que falha por TCC |
| `/Users/jesus/Desktop/MONITOR-FONTES/scripts/orquestrador.py` | Script que falha por TCC |
| `/Users/jesus/stemmia-forense/logs/monitor-datajud-err.log` | Log de erros |
| `/Users/jesus/Desktop/MONITOR-FONTES/logs/launchd.stderr.log` | Log de erros |
