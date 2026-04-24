# MONITOR-FONTES — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automatizar (via cron) a consulta das 5 fontes onde o perito recebe citações/intimações/nomeações — AJ TJMG, AJG Justiça Federal, DJEN/Comunica PJe, Domicílio Judicial Eletrônico (email) e DataJud — consolidar numa lista única **deduplicada e em ordem cronológica**, alertar no Telegram quando aparecer novidade, e gerar dashboard único em pasta organizada na Mesa.

**Architecture:** Pasta raiz `~/Desktop/MONITOR-FONTES/` com estrutura padronizada (scripts, dados, logs, docs, dashboard). Orquestrador Python chama scripts existentes (`consultar_aj.py`, `consultar_ajg.py`, `sincronizar_aj_pje.py`, `hub.py`), consolida resultados em `dados/processos-consolidados.json` (chave = CNJ, deduplicado), gera dashboard HTML. launchd roda diariamente 7h. Se Chrome debug 9223 não estiver logado, envia lembrete Telegram em vez de falhar silencioso.

**Tech Stack:** Python 3 + Playwright (Chrome debug 9223, já usado em AJ/AJG) + requests (APIs) + imapclient (email Domicílio) + launchd (cron macOS) + Telegram Bot API.

---

## Fontes cobertas

| # | Fonte | Automação possível | Como |
|---|-------|---------------------|------|
| 1 | **AJ TJMG** (aj.tjmg.jus.br) | SIM — cron | Playwright + Chrome 9223 logado (script `consultar_aj.py` existe) |
| 2 | **AJG JF** (ajg.cjf.jus.br) | SIM — cron | Playwright + Chrome 9223 logado (script `consultar_ajg.py` existe) |
| 3 | **DJEN/Comunica PJe** | SIM — cron | API pública CNJ (launchd já ativo, só reaproveitar) |
| 4 | **Domicílio Judicial Eletrônico** | SIM — cron | Parser IMAP do email resumo diário |
| 5 | **DataJud** | SIM — cron | API pública CNJ (launchd já ativo) |
| 6 | **PJe Painel** (Windows+VidaaS) | NÃO — manual | Lembrete Telegram 2x/semana |

---

## Estrutura de pastas (na Mesa)

```
~/Desktop/MONITOR-FONTES/
├── README.md                              ← arquivo mestre (Task 1)
├── scripts/
│   ├── orquestrador.py                    ← chama todos e consolida (Task 3)
│   ├── consolidador.py                    ← dedup por CNJ + ordem cronológica (Task 4)
│   ├── alerta_telegram.py                 ← diff e envio (Task 6)
│   └── abrir_chrome_debug.command         ← atalho clicável p/ abrir Chrome 9223
├── dados/
│   ├── processos-consolidados.json        ← lista mestre deduplicada
│   ├── processos-consolidados.csv         ← mesma coisa em CSV
│   ├── historico/                         ← snapshots diários (YYYY-MM-DD.json)
│   └── por-fonte/                         ← resultado bruto de cada script
│       ├── aj.json
│       ├── ajg.json
│       ├── djen.json
│       ├── domicilio.json
│       └── datajud.json
├── logs/
│   ├── orquestrador-YYYY-MM-DD.log
│   └── erros.log
├── docs/
│   ├── COMO-RODAR.md                      ← guia manual (Task 1)
│   ├── ROTINA-PJE-MANUAL.md               ← rotina Windows 2x/semana
│   └── FONTES-E-URLS.md                   ← referência de URLs e auth
├── dashboard/
│   ├── index.html                         ← dashboard consolidado (Task 7)
│   └── assets/
│       ├── style.css
│       └── script.js
└── config/
    ├── credenciais.env.exemplo            ← modelo (real fica em ~/.stemmia/)
    └── launchd/
        └── com.stemmia.monitor-fontes.plist ← cron diário 7h
```

**Princípio:** 1 pasta = 1 tipo de arquivo. Nunca misturar script com dado com log.

---

## Task 1: Criar estrutura de pastas e README mestre

**Por que primeiro:** Todo o resto depende dessa estrutura. README detalhado substitui memória entre sessões.

**Files:**
- Create: `~/Desktop/MONITOR-FONTES/` (pasta raiz + subpastas)
- Create: `~/Desktop/MONITOR-FONTES/README.md`
- Create: `~/Desktop/MONITOR-FONTES/docs/COMO-RODAR.md`
- Create: `~/Desktop/MONITOR-FONTES/docs/FONTES-E-URLS.md`

- [ ] **Step 1: Criar árvore de pastas**

```bash
mkdir -p ~/Desktop/MONITOR-FONTES/{scripts,dados/{historico,por-fonte},logs,docs,dashboard/assets,config/launchd}
```

- [ ] **Step 2: Criar `README.md` mestre (arquivo detalhado, substitui memória)**

Conteúdo obrigatório:

```markdown
# MONITOR-FONTES

## O que é
Sistema que consulta automaticamente todos os lugares onde recebo citações,
intimações e nomeações como perito médico judicial, consolida numa lista única
(deduplicada, em ordem cronológica) e me avisa no Telegram quando aparece algo novo.

## Fontes monitoradas
1. AJ TJMG — aj.tjmg.jus.br (nomeações estaduais MG)
2. AJG Justiça Federal — ajg.cjf.jus.br (nomeações federais)
3. DJEN/Comunica PJe — comunica.pje.jus.br (publicações oficiais CNJ)
4. Domicílio Judicial Eletrônico — domicilio-eletronico.pdpj.jus.br (citações pessoais por email)
5. DataJud — api pública CNJ (movimentações)
6. PJe TJMG Painel — pje.tjmg.jus.br (manual, só Windows+VidaaS)

## Estrutura de pastas
- scripts/ — códigos Python que rodam as consultas
- dados/ — resultados (JSON + CSV + histórico diário)
- logs/ — logs de cada execução
- docs/ — esta documentação e guias manuais
- dashboard/ — HTML do painel consolidado (abre no browser)
- config/ — configuração (launchd plist, .env)

## Como rodar manualmente
Ver docs/COMO-RODAR.md

## Como funciona o cron
launchd roda scripts/orquestrador.py todo dia às 7h.
Plist em config/launchd/com.stemmia.monitor-fontes.plist.

## Arquivos principais
- dados/processos-consolidados.json — LISTA MESTRE. Lê isso se quiser ver tudo.
- dashboard/index.html — abre no browser para visualização.
- logs/erros.log — se algo der errado, olha aqui.

## Pré-requisitos
- Chrome debug rodando na porta 9223 (para AJ/AJG funcionarem)
  - Abrir com: `scripts/abrir_chrome_debug.command`
  - Logar em aj.tjmg.jus.br E ajg.cjf.jus.br (abas separadas)
  - Deixar Chrome aberto
- Credenciais IMAP em ~/.stemmia/credenciais.env (para Domicílio)
- Python 3 + pip install playwright imapclient requests python-dotenv

## Se Chrome deslogar
O cron detecta e me avisa no Telegram: "Chrome deslogado — abrir e logar".
Abrir scripts/abrir_chrome_debug.command, logar em AJ e AJG, pronto.

## Próximos passos
Ver .claude/plans/monitor-fontes-intimacoes.md

## Última atualização
2026-04-17 — Criação inicial.
```

- [ ] **Step 3: Criar `docs/COMO-RODAR.md`**

```markdown
# Como rodar o MONITOR-FONTES

## Rodar uma vez, manual
1. Abrir Chrome debug: duplo-click em scripts/abrir_chrome_debug.command
2. Logar em aj.tjmg.jus.br e ajg.cjf.jus.br (duas abas)
3. No Terminal: `python3 ~/Desktop/MONITOR-FONTES/scripts/orquestrador.py`
4. Ver resultado em dados/processos-consolidados.json
5. Abrir dashboard/index.html no browser

## Ativar cron diário
```bash
launchctl load ~/Library/LaunchAgents/com.stemmia.monitor-fontes.plist
```

## Desativar cron
```bash
launchctl unload ~/Library/LaunchAgents/com.stemmia.monitor-fontes.plist
```

## Ver logs do dia
```bash
tail -f ~/Desktop/MONITOR-FONTES/logs/orquestrador-$(date +%Y-%m-%d).log
```

## Forçar execução agora
```bash
launchctl start com.stemmia.monitor-fontes
```
```

- [ ] **Step 4: Criar `docs/FONTES-E-URLS.md`**

Copiar de `~/Desktop/STEMMIA Dexter/docs/comunica-pje/URLS-E-ACESSOS.md` e adicionar seção para AJ/AJG com URLs de login.

- [ ] **Step 5: Commit (se usar git nessa pasta — se não, só registrar em MEMORIA.md)**

```bash
cd ~/Desktop/MONITOR-FONTES && git init -q && git add . && git commit -q -m "feat: estrutura inicial MONITOR-FONTES"
```

---

## Task 2: Atalho clicável para abrir Chrome debug 9223

**Por que:** Pré-requisito do AJ/AJG é Chrome debug 9223 aberto e logado. Usuário precisa de 1 clique, não de comando manual.

**Files:**
- Create: `~/Desktop/MONITOR-FONTES/scripts/abrir_chrome_debug.command`

- [ ] **Step 1: Criar o .command**

```bash
#!/bin/bash
# Abre Chrome com perfil dedicado para automação AJ/AJG
# Duplo-click para executar

PERFIL="$HOME/Library/Application Support/Google/Chrome-Monitor-Fontes"
mkdir -p "$PERFIL"

# Mata instâncias anteriores do perfil (libera lock)
pkill -f "Chrome-Monitor-Fontes" 2>/dev/null
sleep 1

open -na "Google Chrome" --args \
  --remote-debugging-port=9223 \
  --user-data-dir="$PERFIL" \
  --no-first-run \
  --no-default-browser-check \
  "https://aj.tjmg.jus.br/aj/internet" \
  "https://ajg.cjf.jus.br/ajg2/internet"

echo "Chrome debug 9223 aberto."
echo "Logar em AJ TJMG e AJG na janela que abriu."
echo "Pode fechar este terminal."
```

- [ ] **Step 2: Tornar executável**

```bash
chmod +x ~/Desktop/MONITOR-FONTES/scripts/abrir_chrome_debug.command
```

- [ ] **Step 3: Testar duplo-click**

Fazer duplo-click no Finder. Chrome deve abrir em AJ e AJG, porta 9223 responder.

Verificar: `curl -s http://127.0.0.1:9223/json/version | head -c 200`
Expected: JSON com `"Browser": "Chrome/..."`

---

## Task 3: Orquestrador que chama AJ + AJG + DJEN + Domicílio + DataJud

**Por que:** Hoje usuário roda manual os 3 (AJ, AJG, PJe). O orquestrador faz isso + adiciona DJEN + Domicílio + DataJud + consolidação automática.

**Files:**
- Create: `~/Desktop/MONITOR-FONTES/scripts/orquestrador.py`
- Test: `~/Desktop/MONITOR-FONTES/scripts/test_orquestrador.py`

- [ ] **Step 1: Escrever teste smoke (não de API real, só de estrutura)**

```python
# test_orquestrador.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from orquestrador import FONTES, rodar_fonte, _caminho_saida

def test_fontes_configuradas():
    ids = {f["id"] for f in FONTES}
    assert ids == {"aj", "ajg", "djen", "domicilio", "datajud"}

def test_caminho_saida_por_fonte():
    for fid in ["aj", "ajg", "djen", "domicilio", "datajud"]:
        p = _caminho_saida(fid)
        assert p.name == f"{fid}.json"
        assert "por-fonte" in str(p)

def test_rodar_fonte_inexistente_retorna_erro():
    r = rodar_fonte({"id": "nao_existe", "cmd": ["python3", "-c", "import sys; sys.exit(1)"]})
    assert r["status"] == "erro"
```

- [ ] **Step 2: Rodar teste — deve falhar (orquestrador.py não existe)**

Run: `cd ~/Desktop/MONITOR-FONTES/scripts && python3 -m pytest test_orquestrador.py -v`
Expected: FAIL com ModuleNotFoundError.

- [ ] **Step 3: Implementar `orquestrador.py`**

```python
#!/usr/bin/env python3
"""Orquestrador MONITOR-FONTES.
Roda todas as fontes, salva resultado bruto em dados/por-fonte/<id>.json
e dispara consolidador ao final.
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path.home() / "Desktop" / "MONITOR-FONTES"
POR_FONTE = RAIZ / "dados" / "por-fonte"
HISTORICO = RAIZ / "dados" / "historico"
LOGS = RAIZ / "logs"

# Scripts existentes no stemmia-forense
STEMMIA = Path.home() / "stemmia-forense" / "src" / "pje"
AJ_PY = STEMMIA / "consultar_aj.py"
AJG_PY = STEMMIA / "consultar_ajg.py"
HUB_PY = Path.home() / "stemmia-forense" / "automacoes" / "hub.py"
DOMICILIO_PY = Path.home() / "stemmia-forense" / "src" / "pipeline" / "fontes" / "domicilio_eletronico.py"

FONTES = [
    {
        "id": "aj",
        "nome": "AJ TJMG",
        "cmd": ["python3", str(AJ_PY), "--listar", "--json", "--porta", "9223"],
        "timeout": 180,
    },
    {
        "id": "ajg",
        "nome": "AJG Justica Federal",
        "cmd": ["python3", str(AJG_PY), "--listar", "--json", "--porta", "9223"],
        "timeout": 180,
    },
    {
        "id": "djen",
        "nome": "DJEN / Comunica PJe",
        "cmd": ["python3", str(HUB_PY), "--discovery-only", "--json"],
        "timeout": 300,
    },
    {
        "id": "domicilio",
        "nome": "Dominio Judicial Eletronico",
        "cmd": ["python3", str(DOMICILIO_PY), "--cron", "--json"],
        "timeout": 120,
    },
    {
        "id": "datajud",
        "nome": "DataJud CNJ",
        "cmd": ["python3", str(HUB_PY), "--status-only", "--json"],
        "timeout": 600,
    },
]

def _caminho_saida(fid: str) -> Path:
    return POR_FONTE / f"{fid}.json"

def _log(msg: str):
    linha = f"[{datetime.now():%H:%M:%S}] {msg}"
    print(linha)
    (LOGS / f"orquestrador-{datetime.now():%Y-%m-%d}.log").parent.mkdir(parents=True, exist_ok=True)
    with open(LOGS / f"orquestrador-{datetime.now():%Y-%m-%d}.log", "a") as f:
        f.write(linha + "\n")

def rodar_fonte(fonte: dict) -> dict:
    _log(f"→ {fonte['nome']}: iniciando")
    try:
        r = subprocess.run(
            fonte["cmd"],
            capture_output=True,
            text=True,
            timeout=fonte.get("timeout", 300),
        )
        if r.returncode != 0:
            _log(f"  ✗ {fonte['nome']}: exit {r.returncode} — {r.stderr[:200]}")
            return {"status": "erro", "erro": r.stderr[:500], "retorno": r.returncode}
        try:
            dados = json.loads(r.stdout) if r.stdout.strip() else []
        except json.JSONDecodeError:
            dados = r.stdout
        saida = _caminho_saida(fonte["id"])
        saida.parent.mkdir(parents=True, exist_ok=True)
        saida.write_text(json.dumps(dados, ensure_ascii=False, indent=2))
        count = len(dados) if isinstance(dados, list) else "?"
        _log(f"  ✓ {fonte['nome']}: {count} itens → {saida.name}")
        return {"status": "ok", "itens": count, "arquivo": str(saida)}
    except subprocess.TimeoutExpired:
        _log(f"  ✗ {fonte['nome']}: TIMEOUT")
        return {"status": "timeout"}
    except FileNotFoundError as e:
        _log(f"  ✗ {fonte['nome']}: script nao encontrado — {e}")
        return {"status": "erro", "erro": str(e)}

def main():
    _log("=" * 50)
    _log("MONITOR-FONTES — orquestrador iniciado")
    resultados = {}
    for f in FONTES:
        resultados[f["id"]] = rodar_fonte(f)
    # Snapshot do dia
    HISTORICO.mkdir(parents=True, exist_ok=True)
    snap = HISTORICO / f"{datetime.now():%Y-%m-%d}.json"
    snap.write_text(json.dumps(resultados, ensure_ascii=False, indent=2))
    _log(f"Snapshot: {snap.name}")
    # Chama consolidador
    subprocess.run(["python3", str(Path(__file__).parent / "consolidador.py")])
    # Chama alerta
    subprocess.run(["python3", str(Path(__file__).parent / "alerta_telegram.py")])
    _log("Concluido.")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Rodar teste — deve passar**

Run: `cd ~/Desktop/MONITOR-FONTES/scripts && python3 -m pytest test_orquestrador.py -v`
Expected: PASS (3/3).

- [ ] **Step 5: Rodar manual com Chrome debug aberto**

1. Duplo-click em `abrir_chrome_debug.command`
2. Logar em AJ e AJG
3. `python3 ~/Desktop/MONITOR-FONTES/scripts/orquestrador.py`

Expected: 5 arquivos em `dados/por-fonte/` (aj.json, ajg.json, djen.json, domicilio.json, datajud.json). Cada um com array de CNJs.

---

## Task 4: Consolidador — dedup por CNJ + ordem cronológica

**Files:**
- Create: `~/Desktop/MONITOR-FONTES/scripts/consolidador.py`
- Test: `~/Desktop/MONITOR-FONTES/scripts/test_consolidador.py`

- [ ] **Step 1: Teste com dados sintéticos**

```python
# test_consolidador.py
from pathlib import Path
import json, sys, tempfile
sys.path.insert(0, str(Path(__file__).parent))

def test_consolidar_deduplica_mesmo_cnj(tmp_path, monkeypatch):
    import consolidador
    monkeypatch.setattr(consolidador, "POR_FONTE", tmp_path)
    monkeypatch.setattr(consolidador, "SAIDA_JSON", tmp_path / "out.json")
    monkeypatch.setattr(consolidador, "SAIDA_CSV", tmp_path / "out.csv")
    (tmp_path / "aj.json").write_text(json.dumps([
        {"cnj": "5001-01.2025.8.13.0105", "data": "2026-04-10", "fonte": "aj"},
    ]))
    (tmp_path / "djen.json").write_text(json.dumps([
        {"cnj": "5001-01.2025.8.13.0105", "data": "2026-04-15", "fonte": "djen"},
        {"cnj": "5002-02.2025.8.13.0105", "data": "2026-04-12", "fonte": "djen"},
    ]))
    lista = consolidador.consolidar()
    # Deduplicado: 2 CNJs unicos
    assert len(lista) == 2
    # Ordem cronologica (mais recente primeiro)
    assert lista[0]["cnj"] == "5001-01.2025.8.13.0105"  # 2026-04-15
    assert lista[1]["cnj"] == "5002-02.2025.8.13.0105"  # 2026-04-12
    # CNJ repetido junta fontes
    assert set(lista[0]["fontes"]) == {"aj", "djen"}
```

- [ ] **Step 2: Implementar `consolidador.py`**

```python
#!/usr/bin/env python3
"""Consolida resultados de todas as fontes em lista única deduplicada por CNJ."""
import csv
import json
from datetime import datetime
from pathlib import Path

RAIZ = Path.home() / "Desktop" / "MONITOR-FONTES"
POR_FONTE = RAIZ / "dados" / "por-fonte"
SAIDA_JSON = RAIZ / "dados" / "processos-consolidados.json"
SAIDA_CSV = RAIZ / "dados" / "processos-consolidados.csv"

def _data_iso(raw) -> str:
    if not raw:
        return ""
    if isinstance(raw, str):
        # Tenta vários formatos
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(raw[:19], fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
    return str(raw)[:10]

def consolidar() -> list:
    merged = {}
    for arq in POR_FONTE.glob("*.json"):
        fonte_id = arq.stem
        try:
            dados = json.loads(arq.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(dados, list):
            continue
        for item in dados:
            cnj = item.get("cnj") or item.get("numero_processo") or item.get("numeroProcesso")
            if not cnj:
                continue
            cnj = cnj.strip()
            data = _data_iso(item.get("data") or item.get("data_intimacao") or item.get("dataDisponibilizacao"))
            if cnj not in merged:
                merged[cnj] = {
                    "cnj": cnj,
                    "data_mais_recente": data,
                    "fontes": [],
                    "detalhes": [],
                }
            entry = merged[cnj]
            if fonte_id not in entry["fontes"]:
                entry["fontes"].append(fonte_id)
            entry["detalhes"].append({"fonte": fonte_id, "data": data, "item": item})
            if data > entry["data_mais_recente"]:
                entry["data_mais_recente"] = data
    lista = list(merged.values())
    lista.sort(key=lambda x: x["data_mais_recente"], reverse=True)
    SAIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_JSON.write_text(json.dumps(lista, ensure_ascii=False, indent=2))
    with open(SAIDA_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cnj", "data_mais_recente", "fontes", "n_intimacoes"])
        for p in lista:
            w.writerow([p["cnj"], p["data_mais_recente"], "+".join(p["fontes"]), len(p["detalhes"])])
    return lista

if __name__ == "__main__":
    lista = consolidar()
    print(f"{len(lista)} processos únicos consolidados em {SAIDA_JSON.name}")
```

- [ ] **Step 3: Rodar teste — deve passar**

Run: `cd ~/Desktop/MONITOR-FONTES/scripts && python3 -m pytest test_consolidador.py -v`
Expected: PASS.

- [ ] **Step 4: Rodar manual com dados reais**

Run: `python3 ~/Desktop/MONITOR-FONTES/scripts/consolidador.py`
Expected: `dados/processos-consolidados.json` criado, ordenado por data desc, sem CNJs duplicados. Conferir 3 exemplos manualmente.

---

## Task 5: Fixtures AJ + AJG e teste de integração com Chrome mockado

**Por que:** Playwright real exige Chrome logado. Para CI/teste repetível, capturar 1 resposta real como fixture.

**Files:**
- Create: `~/Desktop/MONITOR-FONTES/scripts/fixtures/aj_resposta.json`
- Create: `~/Desktop/MONITOR-FONTES/scripts/fixtures/ajg_resposta.json`

- [ ] **Step 1: Rodar AJ real uma vez e salvar saída**

```bash
python3 ~/stemmia-forense/src/pje/consultar_aj.py --listar --json --porta 9223 > ~/Desktop/MONITOR-FONTES/scripts/fixtures/aj_resposta.json
python3 ~/stemmia-forense/src/pje/consultar_ajg.py --listar --json --porta 9223 > ~/Desktop/MONITOR-FONTES/scripts/fixtures/ajg_resposta.json
```

- [ ] **Step 2: Validar fixture manualmente**

Abrir cada JSON e confirmar que é array, cada item tem `cnj` ou `numeroProcesso`, pelo menos 1 registro. Se fixture tiver 0 itens, rodar de novo quando tiver nomeações.

- [ ] **Step 3: Commit das fixtures (sem dados sensíveis)**

Antes de commitar, inspecionar: nenhum CPF, nenhum nome completo desnecessário. Anonimizar se houver.

---

## Task 6: Alerta Telegram para novidades

**Files:**
- Create: `~/Desktop/MONITOR-FONTES/scripts/alerta_telegram.py`
- Test: `~/Desktop/MONITOR-FONTES/scripts/test_alerta.py`

- [ ] **Step 1: Teste diff**

```python
# test_alerta.py
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from alerta_telegram import detectar_novos

def test_sem_cnjs_anteriores_tudo_e_novo():
    anterior = []
    atual = [{"cnj": "A"}, {"cnj": "B"}]
    novos = detectar_novos(anterior, atual)
    assert {n["cnj"] for n in novos} == {"A", "B"}

def test_cnj_ja_visto_nao_alerta():
    anterior = [{"cnj": "A"}]
    atual = [{"cnj": "A"}, {"cnj": "B"}]
    novos = detectar_novos(anterior, atual)
    assert [n["cnj"] for n in novos] == ["B"]

def test_chrome_deslogado_gera_alerta_especial():
    from alerta_telegram import precisa_relogin
    snapshot = {"aj": {"status": "erro", "erro": "Not logged in"}}
    assert precisa_relogin(snapshot) is True
```

- [ ] **Step 2: Implementar `alerta_telegram.py`**

```python
#!/usr/bin/env python3
"""Compara consolidado atual vs ultimo snapshot do historico e alerta no Telegram."""
import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path.home() / "Desktop" / "MONITOR-FONTES"
CONSOLIDADO = RAIZ / "dados" / "processos-consolidados.json"
HISTORICO = RAIZ / "dados" / "historico"
CHAT_ID = "8397602236"
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # carregar de ~/.stemmia/credenciais.env

def detectar_novos(anterior: list, atual: list) -> list:
    cnjs_ant = {p["cnj"] for p in anterior}
    return [p for p in atual if p["cnj"] not in cnjs_ant]

def precisa_relogin(snapshot_fontes: dict) -> bool:
    for fid in ("aj", "ajg"):
        info = snapshot_fontes.get(fid, {})
        if info.get("status") == "erro":
            erro = str(info.get("erro", "")).lower()
            if any(k in erro for k in ["logi", "auth", "sess", "not found"]):
                return True
    return False

def enviar(msg: str):
    if not TOKEN:
        print("TELEGRAM_BOT_TOKEN ausente — pulando envio")
        return
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
        timeout=10,
    )

def _ultimo_consolidado_anterior() -> list:
    # Busca o snapshot de ontem ou mais antigo
    ontem = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    anterior_path = RAIZ / "dados" / f"consolidado-{ontem}.json"
    if anterior_path.exists():
        return json.loads(anterior_path.read_text())
    return []

def main():
    from dotenv import load_dotenv
    load_dotenv(os.path.expanduser("~/.stemmia/credenciais.env"))
    global TOKEN
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    atual = json.loads(CONSOLIDADO.read_text()) if CONSOLIDADO.exists() else []
    anterior = _ultimo_consolidado_anterior()
    novos = detectar_novos(anterior, atual)
    # Salva snapshot de hoje para comparar amanha
    hoje = datetime.now().strftime("%Y-%m-%d")
    (RAIZ / "dados" / f"consolidado-{hoje}.json").write_text(json.dumps(atual, ensure_ascii=False, indent=2))
    # Checa relogin
    snapshot_path = HISTORICO / f"{hoje}.json"
    if snapshot_path.exists():
        snapshot = json.loads(snapshot_path.read_text())
        if precisa_relogin(snapshot):
            enviar("⚠️ *MONITOR-FONTES*: Chrome deslogado em AJ/AJG. Abrir `scripts/abrir_chrome_debug.command` e logar novamente.")
            return
    if novos:
        linhas = [f"🔔 *{len(novos)} processo(s) novo(s)*:"]
        for n in novos[:15]:
            fontes = "+".join(n.get("fontes", []))
            linhas.append(f"• `{n['cnj']}` [{fontes}] — {n.get('data_mais_recente', '?')}")
        if len(novos) > 15:
            linhas.append(f"…e mais {len(novos)-15}")
        linhas.append(f"\n📂 `~/Desktop/MONITOR-FONTES/dashboard/index.html`")
        enviar("\n".join(linhas))

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Rodar teste — PASS**

Run: `cd ~/Desktop/MONITOR-FONTES/scripts && python3 -m pytest test_alerta.py -v`

- [ ] **Step 4: Testar envio real**

Run: `python3 -c "from alerta_telegram import enviar, TOKEN; import os; from dotenv import load_dotenv; load_dotenv(os.path.expanduser('~/.stemmia/credenciais.env')); import alerta_telegram; alerta_telegram.TOKEN = os.getenv('TELEGRAM_BOT_TOKEN'); alerta_telegram.enviar('teste monitor-fontes, ignorar')"`
Expected: mensagem no Telegram.

---

## Task 7: Dashboard HTML

**Por que:** Usuário tem esboço de dashboard antigo. Vamos aproveitar padrão de `~/stemmia-forense/automacoes/gerar_dashboard_hub.py` ou `DASHBOARD-PUBLICACOES.html` e adaptar.

**Files:**
- Create: `~/Desktop/MONITOR-FONTES/scripts/gerar_dashboard.py`
- Create: `~/Desktop/MONITOR-FONTES/dashboard/index.html` (gerado)
- Create: `~/Desktop/MONITOR-FONTES/dashboard/assets/style.css`

- [ ] **Step 1: Localizar esboço antigo**

Run: `ls -la ~/stemmia-forense/automacoes/DASHBOARD-HUB.html ~/stemmia-forense/output/publicacoes/DASHBOARD-PUBLICACOES.html ~/Desktop/STEMMIA\ Dexter/RELATÓRIOS/PAINEL-PROCESSOS-01ABR2026.html`

Escolher o que tem layout mais próximo do desejado. Usar como template.

- [ ] **Step 2: Implementar `gerar_dashboard.py`**

Template mínimo: tabela ordenada por `data_mais_recente`, colunas `CNJ | Data | Fontes (chips coloridas) | Detalhes`. Filtros por fonte (AJ/AJG/DJEN/Domicílio/DataJud). Contagem total no topo.

```python
#!/usr/bin/env python3
"""Gera dashboard/index.html a partir de dados/processos-consolidados.json."""
import json
from datetime import datetime
from pathlib import Path

RAIZ = Path.home() / "Desktop" / "MONITOR-FONTES"
CONSOLIDADO = RAIZ / "dados" / "processos-consolidados.json"
DASH = RAIZ / "dashboard" / "index.html"

CORES_FONTE = {
    "aj": "#3b82f6",
    "ajg": "#8b5cf6",
    "djen": "#10b981",
    "domicilio": "#ef4444",
    "datajud": "#f59e0b",
}

def gerar():
    lista = json.loads(CONSOLIDADO.read_text()) if CONSOLIDADO.exists() else []
    linhas_html = []
    for p in lista:
        chips = " ".join(
            f'<span class="chip" style="background:{CORES_FONTE.get(f, "#888")}">{f.upper()}</span>'
            for f in p["fontes"]
        )
        linhas_html.append(
            f'<tr><td><code>{p["cnj"]}</code></td>'
            f'<td>{p["data_mais_recente"]}</td>'
            f'<td>{chips}</td>'
            f'<td>{len(p["detalhes"])}</td></tr>'
        )
    html = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>MONITOR-FONTES — {len(lista)} processos</title>
<link rel="stylesheet" href="assets/style.css"></head>
<body>
<h1>MONITOR-FONTES</h1>
<p>{len(lista)} processos únicos · atualizado {datetime.now():%d/%m/%Y %H:%M}</p>
<table>
<thead><tr><th>CNJ</th><th>Última data</th><th>Fontes</th><th>Intimações</th></tr></thead>
<tbody>{''.join(linhas_html)}</tbody>
</table>
</body></html>"""
    DASH.parent.mkdir(parents=True, exist_ok=True)
    DASH.write_text(html)
    print(f"Dashboard gerado: {DASH}")

if __name__ == "__main__":
    gerar()
```

- [ ] **Step 3: Criar `assets/style.css`**

```css
body { font-family: -apple-system, sans-serif; padding: 20px; max-width: 1200px; margin: 0 auto; background: #0f172a; color: #e2e8f0; }
h1 { border-bottom: 2px solid #1e293b; padding-bottom: 10px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px; text-align: left; border-bottom: 1px solid #1e293b; }
th { background: #1e293b; position: sticky; top: 0; }
tr:hover { background: #1e293b; }
code { font-size: 0.9em; color: #60a5fa; }
.chip { display: inline-block; padding: 2px 8px; border-radius: 4px; color: white; font-size: 0.75em; margin: 0 2px; font-weight: bold; }
```

- [ ] **Step 4: Plugar no orquestrador**

No final de `orquestrador.py main()`, adicionar:
```python
subprocess.run(["python3", str(Path(__file__).parent / "gerar_dashboard.py")])
```

- [ ] **Step 5: Testar abertura**

Run: `python3 ~/Desktop/MONITOR-FONTES/scripts/gerar_dashboard.py && open ~/Desktop/MONITOR-FONTES/dashboard/index.html`
Expected: browser abre com tabela correta.

---

## Task 8: launchd cron diário 7h

**Files:**
- Create: `~/Desktop/MONITOR-FONTES/config/launchd/com.stemmia.monitor-fontes.plist`
- Symlink: `~/Library/LaunchAgents/com.stemmia.monitor-fontes.plist`

- [ ] **Step 1: Criar plist**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.stemmia.monitor-fontes</string>
<key>ProgramArguments</key>
<array>
  <string>/usr/bin/python3</string>
  <string>/Users/jesus/Desktop/MONITOR-FONTES/scripts/orquestrador.py</string>
</array>
<key>StartCalendarInterval</key><dict>
  <key>Hour</key><integer>7</integer><key>Minute</key><integer>0</integer>
</dict>
<key>StandardOutPath</key><string>/Users/jesus/Desktop/MONITOR-FONTES/logs/launchd-stdout.log</string>
<key>StandardErrorPath</key><string>/Users/jesus/Desktop/MONITOR-FONTES/logs/launchd-stderr.log</string>
<key>RunAtLoad</key><false/>
</dict></plist>
```

- [ ] **Step 2: Linkar e carregar**

```bash
ln -sf ~/Desktop/MONITOR-FONTES/config/launchd/com.stemmia.monitor-fontes.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.stemmia.monitor-fontes.plist
launchctl list | grep monitor-fontes
```
Expected: label listado com PID ou "-".

- [ ] **Step 3: Rodar agora para validar**

```bash
launchctl start com.stemmia.monitor-fontes
sleep 30
tail -20 ~/Desktop/MONITOR-FONTES/logs/launchd-stderr.log
```
Expected: sem erros críticos. Se AJ/AJG falharem (Chrome deslogado), Telegram recebe aviso de relogin.

---

## Task 9: E2E + atualizar MEMORIA.md

- [ ] **Step 1: Execução completa manual**

```bash
# Chrome debug aberto e logado
python3 ~/Desktop/MONITOR-FONTES/scripts/orquestrador.py
```

Conferir:
- [ ] `dados/por-fonte/` tem 5 arquivos JSON
- [ ] `dados/processos-consolidados.json` criado, CNJs únicos, ordenado por data desc
- [ ] `dados/processos-consolidados.csv` legível no Excel
- [ ] `dashboard/index.html` abre e mostra tabela correta
- [ ] `logs/orquestrador-YYYY-MM-DD.log` tem 1 linha por fonte com status
- [ ] Telegram recebeu alerta (se havia diff)

- [ ] **Step 2: Atualizar MEMORIA.md**

Adicionar em `~/Desktop/STEMMIA Dexter/MEMORIA.md`:

```
## 2026-04-17 — MONITOR-FONTES criado
- Pasta: ~/Desktop/MONITOR-FONTES/
- Roda cron diário 7h (launchd com.stemmia.monitor-fontes)
- Consolida AJ + AJG + DJEN + Domicílio + DataJud em dados/processos-consolidados.json
- Dashboard: ~/Desktop/MONITOR-FONTES/dashboard/index.html
- Pré-requisito: Chrome debug 9223 aberto e logado em AJ/AJG
  - Atalho: scripts/abrir_chrome_debug.command (duplo-click)
- Se Chrome deslogar, Telegram avisa
- README completo em ~/Desktop/MONITOR-FONTES/README.md
```

- [ ] **Step 3: Salvar entrada de memória Claude**

Criar `~/.claude/projects/-Users-jesus/memory/project_monitor_fontes.md` descrevendo: objetivo, pasta raiz, como rodar, pré-requisitos. Adicionar linha em `MEMORY.md`.

---

## Self-review

- **Cobertura:** AJ (T3), AJG (T3), DJEN (T3), Domicílio (T3, depende do plano anterior ter criado parser — se não, fazer em paralelo), DataJud (T3), PJe Painel (manual documentado em docs/), dedup cronológica (T4), alerta (T6), dashboard (T7), cron (T8). ✅
- **Estrutura de pastas:** criada na T1 com subpastas padrão, README mestre detalhado, guia de execução, referência de URLs. ✅
- **Regra nova (sempre estrutura organizada):** salva em feedback de memória. Plano aplica em T1. ✅
- **Domicílio Eletrônico parser:** depende de ter fixture de email. Se não tiver, T3 vai falhar nessa fonte com status `erro`; não bloqueia resto.
- **Placeholders:** nenhum. Todo código está escrito.
- **Consistência:** `rodar_fonte`, `consolidar`, `detectar_novos`, `precisa_relogin` definidos e referenciados corretamente.

---

## Handoff de execução

Plano salvo em `~/.claude/plans/monitor-fontes-intimacoes.md`.

Duas opções:

1. **Subagent-Driven (recomendado)** — dispatcho 1 subagent por task, revisão entre tasks — `superpowers:subagent-driven-development`
2. **Inline Execution** — eu executo tudo em sequência aqui com checkpoints — `superpowers:executing-plans`

Qual?
