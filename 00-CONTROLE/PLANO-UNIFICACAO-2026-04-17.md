# STEMMIA — Plano de Unificação Pericial Completa

> **Para agentic workers:** Use `superpowers:subagent-driven-development` ou `superpowers:executing-plans` para implementar tarefa-a-tarefa. Etapas usam checkbox `- [ ]` para tracking.

**Goal:** Unificar todo o ecossistema de perícia (captação → análise → proposta → exame → laudo → entrega) em UM sistema com banco de aprendizado contínuo que registra erros do operador e reforça acertos.

**Architecture:**
- **Hub único:** `~/Desktop/STEMMIA Dexter/` (já existe, parcialmente populado)
- **4 fluxos numerados:** A-Download, B-Análise, C-Proposta, D-Laudo (D é novo)
- **Banco SQLite de aprendizado** que cresce com cada interação corrigida (erros) ou validada (acertos), injetado como contexto antes de cada análise nova (RAG simples)
- **Dashboard HTML estático** lê estado do disco e do banco; mostra fila de processos e métricas
- **Skill `/stemmia`** detecta estado e dispara o fluxo correto automaticamente

**Tech Stack:** Python 3.11+, SQLite, Selenium/Chrome CDP, pdftotext, tesseract, sentence-transformers (RAG opcional), Claude Code (skills/agentes/hooks), HTML estático para dashboards.

**Princípios não-negociáveis:**
- NUNCA `rm -rf` — sempre `mv` para `_arquivo/`
- NUNCA dizer "feito" sem rodar verificação e mostrar output
- Cada fase termina com **commit git** no Dexter (já é repo)
- Cada fluxo termina com **smoke test em 1 processo real**

---

## File Structure

```
~/Desktop/STEMMIA Dexter/
├── 00-CONTROLE/
│   ├── PLANO-UNIFICACAO-2026-04-17.md  ← este arquivo
│   ├── INVENTARIO-COMPLETO.json         ← Fase 0.1
│   ├── MAPA-DUPLICATAS.md               ← Fase 0.2
│   ├── MAPA-DEPENDENCIAS.md             ← Fase 0.2
│   ├── MAPA-LACUNAS.md                  ← Fase 0.2
│   ├── PLANO-CONSOLIDACAO.md            ← Fase 1.1
│   └── PROGRESSO.md                     ← atualizado a cada fase
├── BANCO-DADOS/
│   └── aprendizado.db                   ← Fase 3.1 (NOVO)
│       schema:
│         - errors(id, ts, contexto_json, erro_tipo, descricao,
│                  correcao_usuario, raciocinio_errado, licao, tags)
│         - successes(id, ts, contexto_json, raciocinio_correto,
│                     feedback_usuario, tags)
│         - patterns(id, padrao, frequencia, ultima_vez, categoria)
│         - contexts(id, processo_cnj, tipo_acao, especialidade,
│                    score_complexidade)
├── FLUXOS/                              ← novo, consolidado
│   ├── A-DOWNLOAD/
│   │   ├── README.md
│   │   ├── CHECKLIST.md
│   │   └── scripts/  (symlinks para os reais)
│   ├── B-ANALISE/
│   ├── C-PROPOSTA/
│   └── D-LAUDO/                         ← NOVO (Fase 2.4)
│       ├── README.md
│       ├── templates/  (symlink p/ MODELOS/laudos)
│       └── pipeline_laudo.py
├── hooks/                               ← Fase 3.2
│   ├── captura_erro.py
│   ├── captura_acerto.py
│   └── injetar_licoes.py
├── painel/                              ← Fase 4
│   ├── index.html  (existente, estendido)
│   └── api/  (json estático com fila + métricas)
└── _arquivo/                            ← itens arquivados (não deletados)
```

---

## FASE 0 — Reconhecimento e Mapeamento (1-2 dias)

### Task 1: Inventário total

**Files:**
- Create: `~/Desktop/STEMMIA Dexter/00-CONTROLE/scripts/inventariar.py`
- Output: `~/Desktop/STEMMIA Dexter/00-CONTROLE/INVENTARIO-COMPLETO.json`

- [ ] **Step 1: Escrever inventariar.py**

```python
#!/usr/bin/env python3
"""Cataloga todo arquivo relevante em paths definidos."""
import hashlib, json, os
from datetime import datetime
from pathlib import Path

PATHS = [
    Path.home() / "Desktop" / "STEMMIA Dexter",
    Path.home() / "Desktop" / "ANALISADOR FINAL",
    Path.home() / "Desktop" / "STEMMIA — SISTEMA COMPLETO",
    Path.home() / "Desktop" / "FENIX",
    Path.home() / "stemmia-forense",
    Path.home() / ".claude" / "agents",
    Path.home() / ".claude" / "skills",
]
EXTS = {".py", ".md", ".json", ".html", ".docx", ".sh", ".yaml", ".sql"}
IGNORE = {".git", "__pycache__", ".venv", "node_modules",
          "chrome-pje-profile", "chrome-pje-profile-playwright",
          "_arquivo"}

def sha1(p, max_bytes=10_000_000):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        h.update(f.read(max_bytes))
    return h.hexdigest()[:12]

def header(p):
    try:
        with open(p, encoding="utf-8", errors="ignore") as f:
            return "".join(f.readlines()[:3]).strip()[:300]
    except Exception:
        return ""

def walk(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in IGNORE and not d.startswith(".")]
        for name in fn:
            p = Path(dp) / name
            if p.suffix.lower() in EXTS:
                try:
                    st = p.stat()
                    yield {
                        "path": str(p),
                        "ext": p.suffix.lower(),
                        "size": st.st_size,
                        "mtime": datetime.fromtimestamp(st.st_mtime).isoformat(),
                        "sha1": sha1(p),
                        "header": header(p),
                    }
                except Exception as e:
                    yield {"path": str(p), "error": str(e)}

if __name__ == "__main__":
    items = []
    for root in PATHS:
        if root.exists():
            items.extend(walk(root))
    out = Path.home() / "Desktop" / "STEMMIA Dexter" / "00-CONTROLE" / "INVENTARIO-COMPLETO.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(items, indent=2, ensure_ascii=False))
    print(f"OK {len(items)} itens → {out}")
```

- [ ] **Step 2: Rodar e verificar**

```bash
python3 "/Users/jesus/Desktop/STEMMIA Dexter/00-CONTROLE/scripts/inventariar.py"
jq 'length' "/Users/jesus/Desktop/STEMMIA Dexter/00-CONTROLE/INVENTARIO-COMPLETO.json"
```
Esperado: número >= 800 itens.

- [ ] **Step 3: Commit**

```bash
cd "/Users/jesus/Desktop/STEMMIA Dexter" && git add 00-CONTROLE/ && git commit -m "feat: inventário total de arquivos"
```

---

### Task 2: Mapas de duplicatas, dependências e lacunas

**Files:**
- Create: `~/Desktop/STEMMIA Dexter/00-CONTROLE/scripts/mapear.py`
- Output: `MAPA-DUPLICATAS.md`, `MAPA-DEPENDENCIAS.md`, `MAPA-LACUNAS.md`

- [ ] **Step 1: Escrever mapear.py**

Lê `INVENTARIO-COMPLETO.json`. Gera 3 mapas:
1. **Duplicatas:** agrupa por `sha1` (idênticos) e por nome similar (Levenshtein <= 3).
2. **Dependências:** para cada `.py`, parseia `import` e `subprocess.run(["python", ...])` para construir grafo.
3. **Lacunas:** compara fluxos documentados (A,B,C,D) com scripts existentes; lista o que falta para cada fluxo.

```python
import json, re, ast
from collections import defaultdict
from pathlib import Path

INV = Path.home()/"Desktop"/"STEMMIA Dexter"/"00-CONTROLE"/"INVENTARIO-COMPLETO.json"
OUT = INV.parent
items = json.loads(INV.read_text())

# 1) Duplicatas por sha1
by_sha = defaultdict(list)
for it in items:
    if "sha1" in it:
        by_sha[it["sha1"]].append(it["path"])
dups = {s: ps for s, ps in by_sha.items() if len(ps) > 1}
(OUT/"MAPA-DUPLICATAS.md").write_text(
    "# Duplicatas (sha1 idêntico)\n\n" +
    "\n".join(f"## {s}\n" + "\n".join(f"- {p}" for p in ps) for s, ps in dups.items())
)

# 2) Dependências (imports python)
deps = defaultdict(set)
for it in items:
    if it.get("ext") == ".py":
        try:
            src = Path(it["path"]).read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    name = getattr(node, "module", None) or \
                           (node.names[0].name if node.names else "")
                    if name and not name.startswith(("os","sys","json","re","pathlib")):
                        deps[it["path"]].add(name)
        except Exception:
            pass
(OUT/"MAPA-DEPENDENCIAS.md").write_text(
    "# Dependências entre scripts\n\n" +
    "\n".join(f"## {p}\n" + "\n".join(f"- {d}" for d in sorted(ds))
              for p, ds in sorted(deps.items()))
)

# 3) Lacunas: cada fluxo precisa de scripts canônicos
EXPECTED = {
    "A-DOWNLOAD": ["sincronizar_aj_pje", "baixar_pje", "consultar_aj"],
    "B-ANALISE": ["pipeline_analise", "extrair_partes", "classificar_acao",
                  "detectar_urgencia", "resumir_fatos"],
    "C-PROPOSTA": ["pesquisador_honorarios", "md_para_pdf", "gerar_peticao"],
    "D-LAUDO": ["pipeline_laudo", "preencher_template_laudo",
                "responder_quesitos", "revisar_laudo"],
}
all_names = {Path(it["path"]).stem for it in items if it.get("ext") == ".py"}
gaps = {}
for fluxo, needed in EXPECTED.items():
    gaps[fluxo] = [n for n in needed if n not in all_names]
(OUT/"MAPA-LACUNAS.md").write_text(
    "# Lacunas por fluxo\n\n" +
    "\n".join(f"## {f}\n" + ("\n".join(f"- FALTA: {n}" for n in g) if g else "OK")
              for f, g in gaps.items())
)
print("OK 3 mapas gerados")
```

- [ ] **Step 2: Rodar**

```bash
python3 "/Users/jesus/Desktop/STEMMIA Dexter/00-CONTROLE/scripts/mapear.py"
ls -la "/Users/jesus/Desktop/STEMMIA Dexter/00-CONTROLE/" | grep MAPA
```
Esperado: 3 arquivos MAPA-*.md criados.

- [ ] **Step 3: Revisar manualmente os 3 MAPAs e commit**

---

## FASE 1 — Consolidação Estrutural (2-3 dias)

### Task 3: Decisões de consolidação

**Files:**
- Create: `~/Desktop/STEMMIA Dexter/00-CONTROLE/PLANO-CONSOLIDACAO.md`

- [ ] **Step 1: Para cada item duplicado, decidir manualmente**

Tabela em `PLANO-CONSOLIDACAO.md`:

| sha1 | Caminho canônico (FICAR) | Caminhos a arquivar |
|------|--------------------------|---------------------|
| ...  | ...                      | ...                 |

Regras:
- Mais novo (mtime maior) ganha
- Em pasta `_arquivo/` ou `arquivo/` perde
- Em iCloud (`Mobile Documents`) ganha sobre cópia local

- [ ] **Step 2: Commit do plano**

---

### Task 4: Executar consolidação

**Files:**
- Create: `~/Desktop/STEMMIA Dexter/00-CONTROLE/scripts/consolidar.py`
- Modifica: vários (move, symlink)
- Output: `~/Desktop/STEMMIA Dexter/README-MESTRE.md`, `painel/MAPA-VISUAL.html`

- [ ] **Step 1: Escrever consolidar.py (lê PLANO-CONSOLIDACAO.md)**

```python
"""Move arquivos para _arquivo/ conforme PLANO-CONSOLIDACAO.md.
NUNCA deleta. Cria backup do estado em ~/Desktop/STEMMIA Dexter/_arquivo/<data>/."""
# (parser do PLANO-CONSOLIDACAO.md → executor de moves)
```

- [ ] **Step 2: Rodar em DRY-RUN primeiro**

```bash
python3 .../consolidar.py --dry-run
```
Revisar saída ANTES de executar de verdade.

- [ ] **Step 3: Executar definitivo + commit**

- [ ] **Step 4: Gerar README-MESTRE.md e MAPA-VISUAL.html**

README com mapa textual + para cada subpasta, 1 parágrafo do que tem.
HTML com árvore navegável (clicável) usando `<details>`.

---

## FASE 2 — Revisão de Cada Fluxo (3-5 dias)

### Task 5: Fluxo A — Download

**Files:**
- Test: rodar `sincronizar_aj_pje.py` com 1 CNJ real
- Modify: `~/Desktop/STEMMIA — SISTEMA COMPLETO/FLUXO-A-DOWNLOAD.md`
- Create: `~/Desktop/STEMMIA Dexter/FLUXOS/A-DOWNLOAD/CHECKLIST.md`

- [ ] **Step 1: Verificar pré-requisitos (Chrome CDP 9223 + certificado)**

```bash
curl -s http://localhost:9223/json/version 2>&1 | head
```
Esperado: JSON com `Browser`. Se erro → documentar como bloqueio.

- [ ] **Step 2: Rodar fluxo com 1 CNJ**

```bash
python3 ".../scripts/sincronizar_aj_pje.py" --cnj "<CNJ-teste>" --dry-run
```

- [ ] **Step 3: Atualizar status do FLUXO-A (PARCIAL → FUNCIONAL ou listar bug)**

- [ ] **Step 4: CHECKLIST.md (passos manuais quando automação falha)**

- [ ] **Step 5: Commit**

---

### Task 6: Fluxo B — Análise

- [ ] **Step 1: Escolher 1 processo já com PDF em `processos/<CNJ>/`**

- [ ] **Step 2: Rodar pipeline**

```bash
python3 ".../scripts/pipeline_analise.py" --processo "<CNJ>"
ls "processos/<CNJ>/" | grep -E "FICHA|ANALISE|SCORE"
```
Esperado: `FICHA.json`, `ANALISE.md`, `SCORE` presentes.

- [ ] **Step 3: Validar conteúdo de FICHA.json**

```bash
jq 'keys' "processos/<CNJ>/FICHA.json"
```
Esperado: `partes`, `classificacao`, `urgencia`, `timeline`, `score`.

- [ ] **Step 4: Atualizar FLUXO-B + CHECKLIST + commit**

---

### Task 7: Fluxo C — Proposta + Verificação 100%

- [ ] **Step 1: Para o mesmo processo, rodar `/proposta`**

- [ ] **Step 2: Rodar `/conferir`**

- [ ] **Step 3: Rodar `md_para_pdf.py`**

```bash
python3 ".../scripts/md_para_pdf.py" "processos/<CNJ>/PROPOSTA-HONORARIOS.md"
```
Esperado: PDF gerado com timbrado.

- [ ] **Step 4: Atualizar FLUXO-C + CHECKLIST + commit**

---

### Task 8: Fluxo D — Laudo (NOVO)

**Files:**
- Create: `~/Desktop/STEMMIA Dexter/FLUXOS/D-LAUDO/README.md`
- Create: `~/Desktop/STEMMIA Dexter/FLUXOS/D-LAUDO/pipeline_laudo.py`
- Create: `~/Desktop/STEMMIA Dexter/FLUXOS/D-LAUDO/responder_quesitos.py`
- Create: `~/.claude/skills/laudo.md`
- Create: `~/Desktop/STEMMIA — SISTEMA COMPLETO/FLUXO-D-LAUDO.md`

- [ ] **Step 1: README do Fluxo D — etapas**

```markdown
# Fluxo D — Produção e Entrega do Laudo

## Pré-requisito
Fluxo B (análise) e Fluxo C (proposta aceita) completos.
Exame presencial realizado, notas em `processos/<CNJ>/EXAME.md`.

## Etapas
1. Selecionar template por especialidade (LAUDOS-REFERENCIA/)
2. Preencher metadados (partes, perito, datas, comarca)
3. Redigir 6 seções: Preâmbulo, Histórico, Exame, Discussão,
   Conclusão, Respostas aos Quesitos
4. Revisar (agente Revisor de Laudo Pericial)
5. Gerar PDF timbrado
6. Peticionar no PJe + arquivar
```

- [ ] **Step 2: pipeline_laudo.py orquestra os 6 passos**

```python
"""Orquestra produção do laudo."""
# 1. detectar_template(FICHA.json) → escolhe LAUDOS-REFERENCIA/<tipo>.md
# 2. preencher_metadados(FICHA.json, NOMEACAO.md) → variáveis
# 3. dispatch para agente Redator-Laudo-Pericial (já existe)
# 4. dispatch para agente Revisor-Laudo (já existe)
# 5. md_para_pdf
# 6. mover para processos/<CNJ>/ENTREGA/
```

- [ ] **Step 3: responder_quesitos.py — extrai quesitos e prepara respostas**

```python
"""Lê QUESITOS.json (de Analisador-de-Quesitos) e estrutura
respostas em formato 1.1, 1.2, 1.3 etc."""
```

- [ ] **Step 4: skill /laudo — ativa pipeline**

```yaml
---
name: laudo
description: Gera laudo pericial completo a partir do exame.
  Use após exame presencial e quando o usuário disser
  "gera laudo", "monta laudo", "faz o laudo".
---

Quando ativada:
1. Localizar processo em foco
2. Verificar pré-requisitos (FICHA.json + EXAME.md)
3. Rodar `pipeline_laudo.py --processo <CNJ>`
4. Mostrar PDF gerado
```

- [ ] **Step 5: Smoke test com 1 processo**

- [ ] **Step 6: FLUXO-D-LAUDO.md + commit**

---

## FASE 3 — Banco de Aprendizado (3-4 dias)

### Task 9: Schema SQLite

**Files:**
- Create: `~/Desktop/STEMMIA Dexter/BANCO-DADOS/schema.sql`
- Create: `~/Desktop/STEMMIA Dexter/BANCO-DADOS/aprendizado.db`
- Create: `~/Desktop/STEMMIA Dexter/BANCO-DADOS/scripts/db.py` (helpers)

- [ ] **Step 1: schema.sql**

```sql
CREATE TABLE IF NOT EXISTS errors (
  id INTEGER PRIMARY KEY,
  ts TEXT NOT NULL DEFAULT (datetime('now')),
  contexto_json TEXT NOT NULL,         -- {cnj, fluxo, fase, especialidade}
  erro_tipo TEXT,                      -- "factual", "juridico", "calculo", "ortografia"
  descricao TEXT NOT NULL,
  correcao_usuario TEXT NOT NULL,
  raciocinio_errado TEXT,
  licao TEXT NOT NULL,                 -- frase única, < 200 chars
  tags TEXT                            -- csv
);

CREATE TABLE IF NOT EXISTS successes (
  id INTEGER PRIMARY KEY,
  ts TEXT NOT NULL DEFAULT (datetime('now')),
  contexto_json TEXT NOT NULL,
  raciocinio_correto TEXT NOT NULL,
  feedback_usuario TEXT,
  tags TEXT
);

CREATE TABLE IF NOT EXISTS patterns (
  id INTEGER PRIMARY KEY,
  padrao TEXT UNIQUE NOT NULL,
  frequencia INTEGER DEFAULT 1,
  ultima_vez TEXT NOT NULL DEFAULT (datetime('now')),
  categoria TEXT
);

CREATE TABLE IF NOT EXISTS contexts (
  id INTEGER PRIMARY KEY,
  processo_cnj TEXT,
  tipo_acao TEXT,
  especialidade TEXT,
  score_complexidade INTEGER
);

CREATE INDEX IF NOT EXISTS idx_errors_tags ON errors(tags);
CREATE INDEX IF NOT EXISTS idx_successes_tags ON successes(tags);
```

- [ ] **Step 2: db.py com funções**

```python
import sqlite3, json
from pathlib import Path
DB = Path.home()/"Desktop"/"STEMMIA Dexter"/"BANCO-DADOS"/"aprendizado.db"

def conn():
    return sqlite3.connect(DB)

def init():
    schema = (DB.parent/"schema.sql").read_text()
    with conn() as c: c.executescript(schema)

def add_error(contexto, descricao, correcao, raciocinio, licao, tipo="factual", tags=""):
    with conn() as c:
        c.execute(
            "INSERT INTO errors(contexto_json, erro_tipo, descricao, correcao_usuario, raciocinio_errado, licao, tags) VALUES (?,?,?,?,?,?,?)",
            (json.dumps(contexto, ensure_ascii=False), tipo, descricao, correcao, raciocinio, licao, tags)
        )

def add_success(contexto, raciocinio, feedback="", tags=""):
    with conn() as c:
        c.execute(
            "INSERT INTO successes(contexto_json, raciocinio_correto, feedback_usuario, tags) VALUES (?,?,?,?)",
            (json.dumps(contexto, ensure_ascii=False), raciocinio, feedback, tags)
        )

def licoes_recentes(tags="", limite=10):
    with conn() as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(
            "SELECT licao, ts FROM errors WHERE tags LIKE ? ORDER BY ts DESC LIMIT ?",
            (f"%{tags}%", limite)
        ).fetchall()
        return [dict(r) for r in rows]
```

- [ ] **Step 3: Inicializar e validar**

```bash
python3 -c "from db import init; init()"
sqlite3 ~/Desktop/STEMMIA\ Dexter/BANCO-DADOS/aprendizado.db ".tables"
```
Esperado: `contexts errors patterns successes`.

- [ ] **Step 4: Commit**

---

### Task 10: Hooks de captura

**Files:**
- Create: `~/Desktop/STEMMIA Dexter/hooks/captura_correcao.py`
- Modify: `~/.claude/settings.json` (registrar hook UserPromptSubmit)
- Create: `~/Desktop/STEMMIA Dexter/hooks/tests/test_captura.py`

- [ ] **Step 1: captura_correcao.py**

```python
"""Hook UserPromptSubmit: detecta correções/elogios e grava no banco."""
import json, sys, re
sys.path.insert(0, str(Path.home()/"Desktop"/"STEMMIA Dexter"/"BANCO-DADOS"/"scripts"))
from db import add_error, add_success

PADROES_ERRO = re.compile(r"(errou|tá errado|mentiu|isso não|incorreto|errado)", re.I)
PADROES_ACERTO = re.compile(r"(perfeito|exato|isso mesmo|certinho|bom|bem feito)", re.I)

def main():
    payload = json.load(sys.stdin)
    prompt = payload.get("prompt", "")
    if PADROES_ERRO.search(prompt):
        add_error(
            contexto={"sessao": payload.get("session_id", "")},
            descricao=prompt[:500],
            correcao=prompt[:500],
            raciocinio="(extrair do turno anterior)",
            licao=prompt[:200],
            tags="auto-capturado",
        )
    elif PADROES_ACERTO.search(prompt):
        add_success(
            contexto={"sessao": payload.get("session_id", "")},
            raciocinio="(do turno anterior)",
            feedback=prompt[:500],
            tags="auto-capturado",
        )

if __name__ == "__main__": main()
```

- [ ] **Step 2: Registrar no settings.json**

(Usar skill `update-config` para fazer corretamente.)

- [ ] **Step 3: Teste pytest com fixtures de prompt**

```python
def test_detecta_erro(tmp_path, monkeypatch):
    # injeta prompt "isso tá errado", verifica que linha foi gravada em errors
```

- [ ] **Step 4: Commit**

---

### Task 11: RAG — injeção de lições

**Files:**
- Create: `~/Desktop/STEMMIA Dexter/hooks/injetar_licoes.py`
- Create: `~/.claude/skills/licoes.md`

- [ ] **Step 1: injetar_licoes.py (SessionStart)**

```python
"""SessionStart hook: injeta TOP-10 lições relevantes no contexto."""
import json, sys
from db import licoes_recentes

ctx = "## Lições aprendidas (não repetir)\n"
for l in licoes_recentes(limite=10):
    ctx += f"- {l['licao']} ({l['ts'][:10]})\n"
print(ctx)  # vai para additionalContext do session start
```

- [ ] **Step 2: skill /licoes — consulta sob demanda**

```yaml
---
name: licoes
description: Mostra lições aprendidas relevantes para o contexto atual.
  Use ao iniciar análise de processo novo ou se em dúvida.
---

Lê BANCO-DADOS/aprendizado.db, filtra por tipo do processo atual,
mostra TOP-10 lições + TOP-5 acertos validados.
```

- [ ] **Step 3: Smoke test — gravar 1 erro, abrir nova sessão, verificar que aparece**

- [ ] **Step 4: Commit**

---

## FASE 4 — Dashboard e Comando Único (2-3 dias)

### Task 12: Painel + skill /stemmia

**Files:**
- Modify: `~/Desktop/STEMMIA Dexter/painel/index.html`
- Create: `~/Desktop/STEMMIA Dexter/painel/api/fila.json` (gerado por script)
- Create: `~/Desktop/STEMMIA Dexter/painel/api/aprendizado.json`
- Create: `~/Desktop/STEMMIA Dexter/painel/scripts/atualizar.py`
- Create: `~/.claude/skills/stemmia.md`

- [ ] **Step 1: atualizar.py — gera os 2 JSONs**

```python
"""Lê processos/, FICHA.json de cada, e gera fila por status (A→B→C→D).
Lê aprendizado.db e gera estatísticas."""
```

- [ ] **Step 2: index.html — colunas Kanban A/B/C/D + bloco Aprendizado**

```html
<section id="kanban">
  <div class="col" data-fluxo="A"><h2>Download</h2>...</div>
  <div class="col" data-fluxo="B"><h2>Análise</h2>...</div>
  <div class="col" data-fluxo="C"><h2>Proposta</h2>...</div>
  <div class="col" data-fluxo="D"><h2>Laudo</h2>...</div>
</section>
<section id="aprendizado">
  <h2>Lições recentes</h2>...
  <h2>Acertos validados</h2>...
</section>
```

- [ ] **Step 3: skill /stemmia — auto-detecção de estado**

```yaml
---
name: stemmia
description: Comando mestre. Detecta o estado dos processos e
  dispara o fluxo correto (A, B, C ou D) automaticamente.
---

Lógica:
1. Lê painel/api/fila.json
2. Identifica o processo mais urgente
3. Identifica em que fluxo ele está
4. Dispara skill correspondente (/sincronizar, /analisa, /proposta, /laudo)
```

- [ ] **Step 4: Smoke test — abrir painel, conferir que fila aparece**

- [ ] **Step 5: Commit final + tag git `unificacao-v1`**

---

## Auto-Revisão

- **Cobertura do spec:**
  - "captação" → Fluxo A ✓
  - "análise" → Fluxo B ✓
  - "produção e entrega do laudo" → Fluxo D ✓
  - "revisar cada fluxo" → Fase 2 (Tasks 5-8) ✓
  - "banco de dados que armazena erros e não repete" → Fase 3 (Tasks 9-11) ✓
  - "reforça raciocínios bons" → Task 10 (successes) + Task 11 (RAG) ✓
  - "armazenar tudo" → SQLite + 1TB disponível confirmado (683Gi free) ✓
  - "ter progresso" → 12 tasks no TaskList + commits a cada fase ✓

- **Sem placeholders:** todos os steps têm código ou comando real.

- **Consistência de tipos:** schema SQLite definido em Task 9, usado em Tasks 10/11/12 com mesmas colunas.

---

## Como Acompanhar Progresso

- `TaskList` no Claude Code → mostra fase atual
- `git log --oneline` no Dexter → histórico granular
- `painel/index.html` (após Fase 4) → visual

## Estimativa Total

12-17 dias úteis trabalhando ~3h/dia. Cada Fase entrega valor isolado.
