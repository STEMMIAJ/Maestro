# PLANO DE ORGANIZAÇÃO DO SISTEMA — STEMMIA Dexter

**Criado:** 2026-04-19
**Plano-fonte:** `~/.claude/plans/enumerated-noodling-sutherland.md` (aprovado)
**Responsável:** Dr. Jesus
**Regra:** UMA tarefa por vez, em ordem. Não pular. Não executar sem ver output real.

---

## OBJETIVOS

1. Auditoria viva do sistema (o que existe, o que está parado, o que duplica).
2. Organograma visual **interativo** (HTML + Obsidian Canvas).
3. Consolidar fisicamente dentro do Dexter: Banco de Dados Geral (1,5 GB) + PYTHON-BASE (760 KB).
4. Ativar loop autoalimentável: todo script Python novo/revisado enriquece a base consultável.
5. Nada é deletado. Toda movimentação deixa symlink reverso.

---

## LEGENDA DE STATUS

- `[ ]` pendente
- `[~]` em execução
- `[x]` concluído e verificado
- `[!]` falhou — ler campo "Se falhar"
- `[⏸]` bloqueado aguardando checkpoint

---

# FASE 1 — AUDITORIA

## T01 — Snapshot do estado atual
**Status:** `[ ]`
**Objetivo:** guardar fotografia do sistema antes de qualquer mudança (rollback garantido).

**Comandos:**
```bash
mkdir -p "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/base"
cd "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/base"
DATA=$(date +%Y-%m-%d_%H%M)
ls -laR "$HOME/Desktop/STEMMIA Dexter" > dexter-ls_${DATA}.txt
du -sh "$HOME/Desktop/STEMMIA Dexter"/* > dexter-du_${DATA}.txt 2>&1
ls -laR "$HOME/Desktop/ANALISADOR FINAL/BANCO DE DADOS GERAL" > banco-geral-ls_${DATA}.txt
ls -laR "$HOME/Desktop/_MESA/01-ATIVO/PYTHON-BASE" > python-base-ls_${DATA}.txt
find "$HOME/.claude/agents" -type f -name "*.md" | sort > agentes_${DATA}.txt
ls "$HOME/.claude/settings.json" -la > settings_${DATA}.txt
cp "$HOME/.claude/settings.json" settings-copia_${DATA}.json
```

**Output esperado:** 6 arquivos criados em `migracoes/base/`, todos com tamanho > 0.

**Verificação:**
```bash
ls -la "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/base/" | grep -c "^-" 
# Deve retornar >= 6
```

**Se falhar:** iCloud pode estar sincronizando `ANALISADOR FINAL`. Aguardar 5 min, tentar de novo. Se persistir, abrir Finder > iCloud, baixar a pasta manualmente.

---

## T02 — Leitura dos 6 arquivos de controle + contagens reais
**Status:** `[ ]`
**Objetivo:** entrar na Fase 1 com números reais, não estimados.

**Arquivos a ler:**
- `STEMMIA Dexter/README.md`
- `STEMMIA Dexter/CLAUDE.md`
- `STEMMIA Dexter/MAPA-FERRAMENTAS.md`
- `STEMMIA Dexter/DECISOES.md`
- `STEMMIA Dexter/ROTINA.md`
- `STEMMIA Dexter/INVENTÁRIO.md`
- `STEMMIA Dexter/00-CONTROLE/AGORA.md`

**Contagens:**
```bash
echo "AGENTES: $(ls $HOME/.claude/agents/*.md 2>/dev/null | wc -l)"
echo "HOOKS SH: $(ls $HOME/stemmia-forense/hooks/*.sh 2>/dev/null | wc -l)"
echo "HOOKS PY: $(ls $HOME/stemmia-forense/hooks/*.py 2>/dev/null | wc -l)"
echo "SCRIPTS PJE: $(ls $HOME/stemmia-forense/src/pje/*.py 2>/dev/null | wc -l)"
echo "BAT WINDOWS: $(ls $HOME/stemmia-forense/*.bat 2>/dev/null | wc -l)"
echo "SLASH COMMANDS: $(ls $HOME/.claude/commands/*.md 2>/dev/null | wc -l)"
echo "GSD COMMANDS: $(ls $HOME/.claude/commands/gsd/*.md 2>/dev/null | wc -l)"
echo "MCPs: $(jq '.mcpServers | length' $HOME/.claude/.mcp.json 2>/dev/null)"
echo "PLUGINS: $(ls $HOME/.claude/plugins/ | grep -v cache | grep -v marketplaces | wc -l)"
```

**Output esperado:** 9 linhas com números > 0.

**Se falhar:** `jq` ausente → `brew install jq`.

---

## T03 — Escrever AUDITORIA-2026-04-19.md
**Status:** `[ ]`
**Objetivo:** relatório-curadoria em 6 seções (A–F), não inventário seco.

**Estrutura obrigatória:**
```
# AUDITORIA — Sistema Pericial STEMMIA — 2026-04-19

## A. Inventário por camada
  A.1 Controle e docs    A.2 Fluxos   A.3 Ferramentas
  A.4 Dados e memória    A.5 Externos A.6 Arquivo

## B. 11 fluxos ponta-a-ponta (tabela: nome | entrada | etapas | saída | arquivo-chave | STATUS)

## C. Duplicações a resolver (RELATORIOS vs RELATÓRIOS, MEMORIA.md raiz vs memoria/, etc.)

## D. Symlinks e dependências externas

## E. Scoreboard por fluxo (doc? teste? agente orquestrador? % cobertura)

## F. Recomendações priorizadas (ordem sugerida para próximas fases)
```

**Saída:** `STEMMIA Dexter/00-CONTROLE/AUDITORIA-2026-04-19.md`

**Verificação:**
```bash
wc -l "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/AUDITORIA-2026-04-19.md"
# Esperado: >= 500 linhas (meta 1000, mínimo 500)
grep -c "^## " "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/AUDITORIA-2026-04-19.md"
# Esperado: >= 6
```

**Se falhar (menos de 500 linhas):** não passou na curadoria — reescrever com mais detalhe na Seção B e E.

---

## T04 — CHECKPOINT 1: Dr. Jesus lê auditoria
**Status:** `[⏸]`
**Ação:** abrir `AUDITORIA-2026-04-19.md`, ler, anotar ajustes em comentários `<!-- AJUSTE: … -->`.

**Saída da conversa:** "Fase 1 OK, seguir para Fase 2" OU "ajustar X, Y, Z antes".

---

# FASE 2 — ORGANOGRAMA VISUAL

## T05 — Montar ORGANOGRAMA-dados.json
**Status:** `[ ]`
**Objetivo:** fonte única de verdade do grafo.

**Estrutura (exemplo mínimo):**
```json
{
  "gerado_em": "2026-04-19",
  "camadas": [
    {"id": "controle", "label": "Controle & Docs", "cor": "#1e3a8a"},
    {"id": "fluxos",   "label": "Fluxos operacionais", "cor": "#065f46"},
    {"id": "agentes",  "label": "Agentes & Skills", "cor": "#7c2d12"},
    {"id": "dados",    "label": "Dados & Memória", "cor": "#4c1d95"},
    {"id": "externos", "label": "Symlinks externos", "cor": "#991b1b"}
  ],
  "nos": [
    { "id": "fluxo-pje",
      "camada": "fluxos",
      "label": "Download PJe",
      "entrada": "lista CNJ",
      "saida": "PDFs + OCR",
      "arquivos": ["src/pje/baixar_push_pje.py", "BAIXAR_PJE.bat"],
      "status": "ATIVO",
      "docs": "DOCS/FLUXO-01-PJE.md",
      "tags": ["download","selenium","windows"]
    }
  ],
  "ligacoes": [
    {"de": "fluxo-pje", "para": "fluxo-analise-rapida", "tipo": "dispara"}
  ]
}
```

**Meta:** ≥ 11 nós de fluxo + ≥ 85 nós de agente + ligações entre orquestradores e seus filhos.

**Saída:** `STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA-dados.json`

**Verificação:**
```bash
jq '.nos | length' "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA-dados.json"
# Esperado: >= 96 (11 fluxos + 85 agentes)
jq '.ligacoes | length' "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA-dados.json"
# Esperado: >= 30
```

---

## T06 — Baixar D3.js v7 local (offline-first)
**Status:** `[ ]`
**Objetivo:** o organograma abre sem internet.

**Comando:**
```bash
mkdir -p "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/assets"
curl -L https://d3js.org/d3.v7.min.js \
  -o "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/assets/d3.v7.min.js"
```

**Verificação:**
```bash
wc -c "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/assets/d3.v7.min.js"
# Esperado: >= 250000 bytes
head -c 50 "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/assets/d3.v7.min.js"
# Esperado: começar com '// https://d3js.org'
```

**Se falhar:** sem internet agora → deixar T06 pendente e pular para T08 (Canvas não precisa de lib).

---

## T07 — Gerar ORGANOGRAMA.html
**Status:** `[ ]`
**Objetivo:** single-file HTML auto-contido (apenas `<script src="assets/d3.v7.min.js">` + CSS inline).

**Funcionalidades obrigatórias:**
1. Grafo force-directed.
2. Zoom/pan (roda + arrastar).
3. Busca (campo no topo, `Ctrl+F`).
4. Filtros por camada (5 toggles).
5. Clique em nó → painel lateral direito (descrição, arquivos, status, link `file://`).
6. Legenda fixa (cores das camadas).
7. Cor por status: verde = ATIVO, amarelo = PARADO, vermelho = QUEBRADO.
8. Botão "Exportar PNG".
9. Responsivo (tela cheia).

**Saída:** `STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA.html`

**Verificação manual:**
```bash
open "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA.html"
```
- [ ] carrega sem erro no console
- [ ] aparecem pelo menos 90 bolinhas
- [ ] clicar em "Download PJe" abre painel com `baixar_push_pje.py`
- [ ] digitar "laudo" na busca destaca ≥ 3 nós
- [ ] toggle "Agentes" oculta os 85 nós de agente

---

## T08 — Gerar ORGANOGRAMA.canvas (Obsidian)
**Status:** `[ ]`
**Objetivo:** backup editável no Obsidian Canvas (formato JSON Canvas).

**Estrutura JSON Canvas:**
```json
{
  "nodes": [
    {"id": "fluxo-pje", "x": 0, "y": 0, "width": 250, "height": 100,
     "type": "text", "text": "**Download PJe**\nbaixar_push_pje.py"}
  ],
  "edges": [
    {"id": "e1", "fromNode": "fluxo-pje", "toNode": "fluxo-analise-rapida"}
  ]
}
```

**Saída:** `STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA.canvas`

**Verificação:**
```bash
jq '.nodes | length' "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA.canvas"
# Esperado: >= 11 (ao menos os fluxos; agentes opcionais aqui)
```

---

## T09 — CHECKPOINT 2: abrir organograma
**Status:** `[⏸]`
**Ação:** Dr. Jesus abre o HTML, navega, confirma "serve" ou pede ajustes.

---

# FASE 3 — MIGRAÇÃO DO BANCO DE DADOS GERAL (1,5 GB)

## T10 — Snapshot + grep de referências ao Banco Geral
**Status:** `[ ]`

**Comandos:**
```bash
DATA=$(date +%Y-%m-%d)
DIR="$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/banco-geral-${DATA}"
mkdir -p "$DIR"

# Inventário
find "$HOME/Desktop/ANALISADOR FINAL/BANCO DE DADOS GERAL" -type f \
  > "$DIR/arquivos-antes.txt"
du -sh "$HOME/Desktop/ANALISADOR FINAL/BANCO DE DADOS GERAL" \
  > "$DIR/tamanho-antes.txt"

# Referências
grep -r "BANCO DE DADOS GERAL" \
  "$HOME/Desktop/STEMMIA Dexter" \
  "$HOME/stemmia-forense" \
  "$HOME/.claude/agents" \
  "$HOME/.claude/plugins" 2>/dev/null \
  > "$DIR/referencias-md.txt"

grep -rn "BANCO-GERAL-LINK\|ANALISADOR FINAL/BANCO" \
  "$HOME/Desktop/STEMMIA Dexter" \
  "$HOME/stemmia-forense" 2>/dev/null \
  > "$DIR/referencias-symlink.txt"
```

**Verificação:**
```bash
wc -l "$DIR"/*.txt
# Todos os 4 arquivos > 0 linhas
```

---

## T11 — rsync Banco Geral para Dexter
**Status:** `[ ]`
**⚠ PEDIR CONFIRMAÇÃO ANTES DE RODAR.** Move 1,5 GB.

**Comando:**
```bash
mkdir -p "$HOME/Desktop/STEMMIA Dexter/BANCO-DADOS/GERAL"

# Remover symlinks que atrapalhariam
rm "$HOME/Desktop/STEMMIA Dexter/BANCO-DADOS/BANCO-GERAL-LINK" 2>/dev/null
rm "$HOME/Desktop/ANALISADOR FINAL/BANCO DE DADOS GERAL/DEXTER-LINK" 2>/dev/null

# Rsync com preservação total
rsync -aHv --info=progress2 \
  "$HOME/Desktop/ANALISADOR FINAL/BANCO DE DADOS GERAL/" \
  "$HOME/Desktop/STEMMIA Dexter/BANCO-DADOS/GERAL/"
```

**Verificação:**
```bash
DU_ORIG=$(du -sk "$HOME/Desktop/ANALISADOR FINAL/BANCO DE DADOS GERAL" | cut -f1)
DU_DEST=$(du -sk "$HOME/Desktop/STEMMIA Dexter/BANCO-DADOS/GERAL" | cut -f1)
echo "ORIG=$DU_ORIG  DEST=$DU_DEST  DIFF=$((DU_ORIG - DU_DEST))"
# DIFF esperado: 0 (ou <5 KB tolerando .DS_Store)

N_ORIG=$(find "$HOME/Desktop/ANALISADOR FINAL/BANCO DE DADOS GERAL" -type f | wc -l)
N_DEST=$(find "$HOME/Desktop/STEMMIA Dexter/BANCO-DADOS/GERAL" -type f | wc -l)
echo "ORIG=$N_ORIG  DEST=$N_DEST"
# Igual
```

**Se falhar:** não prosseguir para T12. Investigar com `rsync --dry-run`.

---

## T12 — Renomear origem + symlink reverso + ajustar BANCO-GERAL-LINK
**Status:** `[ ]`
**⚠ SÓ EXECUTAR SE T11 PASSOU NA VERIFICAÇÃO.**

**Comandos:**
```bash
# Renomear origem (NÃO deletar)
mv "$HOME/Desktop/ANALISADOR FINAL/BANCO DE DADOS GERAL" \
   "$HOME/Desktop/ANALISADOR FINAL/BANCO DE DADOS GERAL.migrado"

# Symlink reverso
ln -s "$HOME/Desktop/STEMMIA Dexter/BANCO-DADOS/GERAL" \
      "$HOME/Desktop/ANALISADOR FINAL/BANCO DE DADOS GERAL"

# Ajustar symlink interno do Dexter
ln -sfn "./GERAL" \
        "$HOME/Desktop/STEMMIA Dexter/BANCO-DADOS/BANCO-GERAL-LINK"
```

**Verificação:**
```bash
ls -la "$HOME/Desktop/ANALISADOR FINAL/" | grep "BANCO DE DADOS"
# Esperado:
#   BANCO DE DADOS GERAL -> .../STEMMIA Dexter/BANCO-DADOS/GERAL
#   BANCO DE DADOS GERAL.migrado (vazio ou com arquivo marcador)

ls "$HOME/Desktop/ANALISADOR FINAL/BANCO DE DADOS GERAL/medicina/" | head -3
# Esperado: retorna conteúdo (via symlink)

ls -la "$HOME/Desktop/STEMMIA Dexter/BANCO-DADOS/BANCO-GERAL-LINK"
# Esperado: -> ./GERAL
```

---

## T13 — Teste funcional do Banco Geral
**Status:** `[ ]`

**Testes:**
```bash
# Teste 1: buscador-base-local enxerga?
# (invocar agente via Task tool em contexto Claude — não script puro)
# Prompt-teste: "Busque jurisprudência sobre 'auxílio-doença' na base local"
# Esperado: retorna pelo menos 1 hit

# Teste 2: gerar_indices.py
cd "$HOME/Desktop/STEMMIA Dexter/BANCO-DADOS"
python3 gerar_indices.py --dry-run 2>&1 | tail -5
# Esperado: sem erro de path; conta arquivos

# Teste 3: acesso pelo path antigo (via symlink)
ls "$HOME/Desktop/ANALISADOR FINAL/BANCO DE DADOS GERAL/direito/" | head -3
# Esperado: lista pastas
```

**Se falhar:** executar T12 reverso — renomear `.migrado` de volta + remover symlink.

---

## T14 — CHECKPOINT 3: 48 horas sem regressão
**Status:** `[⏸]`
**Ação:** usar o sistema normalmente por 48 h. Se nada quebrar, Fase 3 é considerada fechada. `.migrado` fica mais 28 dias antes de ser listado para arquivo.

---

# FASE 4 — PYTHON-BASE + AUTOAPRENDIZAGEM

## T15 — Snapshot + rsync PYTHON-BASE
**Status:** `[ ]`

```bash
DATA=$(date +%Y-%m-%d)
DIR="$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/python-base-${DATA}"
mkdir -p "$DIR"
find "$HOME/Desktop/_MESA/01-ATIVO/PYTHON-BASE" -type f > "$DIR/arquivos-antes.txt"
grep -rn "_MESA/01-ATIVO/PYTHON-BASE\|PYTHON-BASE/03-FALHAS-SOLUCOES" \
  "$HOME/.claude" "$HOME/stemmia-forense" 2>/dev/null > "$DIR/referencias.txt"

mkdir -p "$HOME/Desktop/STEMMIA Dexter/PYTHON-BASE"
rsync -aHv "$HOME/Desktop/_MESA/01-ATIVO/PYTHON-BASE/" \
           "$HOME/Desktop/STEMMIA Dexter/PYTHON-BASE/"
```

**Verificação:** mesmo número de arquivos origem ↔ destino.

---

## T16 — Symlink reverso + atualizar CLAUDE.md global + skill python-base
**Status:** `[ ]`

```bash
mv "$HOME/Desktop/_MESA/01-ATIVO/PYTHON-BASE" \
   "$HOME/Desktop/_MESA/01-ATIVO/PYTHON-BASE.migrado"

ln -s "$HOME/Desktop/STEMMIA Dexter/PYTHON-BASE" \
      "$HOME/Desktop/_MESA/01-ATIVO/PYTHON-BASE"
```

**Editar:** `~/.claude/CLAUDE.md` — seção "# PYTHON DE AUTOMAÇÃO".
Trocar `~/Desktop/_MESA/01-ATIVO/PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json`
por `~/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json`.

**Editar:** `~/.claude/skills/python-base/SKILL.md` — atualizar mesmo path + adicionar regra "após gerar, chamar `indexador-python-base`".

---

## T17 — Criar agente `indexador-python-base`
**Status:** `[ ]`
**Arquivo:** `~/.claude/agents/indexador-python-base.md`

**Frontmatter:**
```yaml
---
name: indexador-python-base
description: Indexa scripts Python em PYTHON-BASE após criação/revisão. Extrai bibliotecas, padrão, snippet, tags. Atualiza falhas.json e _INDICE-CONSULTAVEL.md.
tools: Read, Write, Edit, Bash, Grep
---
```

**Protocolo interno (escrito no corpo do agente):**
1. Recebe path do `.py`.
2. Lê arquivo, extrai imports, docstring, funções top-level, trechos com `try/except`.
3. Calcula SHA256 do conteúdo.
4. Se hash já existe em `falhas.json` → pula.
5. Se não: gera nova entrada `{id, path, hash, libs, pattern, snippet, tags, data}`.
6. Append em `PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json`.
7. Regenera `PYTHON-BASE/_INDICE-CONSULTAVEL.md` (tabela ordenada por data desc).

---

## T18 — Criar hook + launchd
**Status:** `[ ]`
**Arquivo:** `~/stemmia-forense/hooks/python_base_indexer.py`

**Modos:**
- `--enqueue <path>` (chamado por PostToolUse via stdin JSON)
- `--process-queue` (chamado pelo launchd)

**Registrar hook em `~/.claude/settings.json`:**
```json
"PostToolUse": [{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "python3 ~/stemmia-forense/hooks/python_base_indexer.py --enqueue-from-stdin"
  }]
}]
```

**Launchd:** `~/Library/LaunchAgents/com.jesus.python-base-digest.plist` rodando 1x/hora.

**Proteção anti-loop:** o hook ignora paths que casam `PYTHON-BASE/_*` ou `PYTHON-BASE/**/*.md`.

**Verificação:**
```bash
launchctl load ~/Library/LaunchAgents/com.jesus.python-base-digest.plist
launchctl list | grep python-base
# Esperado: uma linha com PID
```

---

## T19 — Gerar primeiro índice + dashboard
**Status:** `[ ]`

**Comandos:**
```bash
python3 ~/stemmia-forense/hooks/python_base_indexer.py --process-queue
python3 ~/stemmia-forense/hooks/python_base_indexer.py --build-dashboard
```

**Saídas:**
- `STEMMIA Dexter/PYTHON-BASE/_INDICE-CONSULTAVEL.md` (tabela com 90+ entradas)
- `STEMMIA Dexter/PYTHON-BASE/_RELATORIO-CRESCIMENTO.html` (3 gráficos)

---

## T20 — Teste end-to-end do autoaprendizado
**Status:** `[ ]`

```bash
# 1. Criar script dummy
cat > /tmp/teste_auto_indexer.py <<'EOF'
"""Teste: indexador automático de python-base."""
import requests
from pathlib import Path

def baixar(url: str, destino: Path) -> None:
    r = requests.get(url, timeout=10)
    destino.write_bytes(r.content)
EOF

# 2. Copiar para dentro do PYTHON-BASE (simula Edit/Write)
cp /tmp/teste_auto_indexer.py \
   "$HOME/Desktop/STEMMIA Dexter/PYTHON-BASE/06-TEMPLATES/"

# 3. Enfileirar manualmente
python3 ~/stemmia-forense/hooks/python_base_indexer.py \
  --enqueue "$HOME/Desktop/STEMMIA Dexter/PYTHON-BASE/06-TEMPLATES/teste_auto_indexer.py"

# 4. Processar
python3 ~/stemmia-forense/hooks/python_base_indexer.py --process-queue

# 5. Verificar nova entrada
jq '.[-1]' "$HOME/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json"
# Esperado: objeto com path contendo "teste_auto_indexer.py"

# 6. Processar de novo — não deve duplicar
python3 ~/stemmia-forense/hooks/python_base_indexer.py --process-queue
jq '[.[] | select(.path | contains("teste_auto_indexer"))] | length' \
  "$HOME/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json"
# Esperado: 1
```

---

# FASE 5 — CONSOLIDAÇÃO E DOCUMENTAÇÃO

## T21 — Atualizar docs do Dexter
**Status:** `[ ]`

**Editar:**
- `STEMMIA Dexter/README.md` — adicionar seção "Banco Geral e PYTHON-BASE migrados (local atual)".
- `STEMMIA Dexter/MAPA-FERRAMENTAS.md` — nova entrada `indexador-python-base` em AGENTES.
- `STEMMIA Dexter/INVENTÁRIO.md` — recontar pastas após migração.
- `STEMMIA Dexter/DECISOES.md` — bloco:
  ```markdown
  ## 2026-04-XX — Consolidação no Dexter
  Movido para dentro: Banco de Dados Geral (1,5 GB) e PYTHON-BASE (760 KB).
  Symlinks reversos mantidos nos caminhos antigos.
  Motivo: hub único físico, autoaprendizagem.
  Rollback: `mv .../GERAL .../ANALISADOR FINAL/BANCO\ DE\ DADOS\ GERAL` + remover symlinks.
  ```

**Memory:** criar `~/.claude/projects/-Users-jesus/memory/project_consolidacao_dexter.md` + entrada em `MEMORY.md`.

---

## T22 — Regenerar ORGANOGRAMA com estrutura final
**Status:** `[ ]`

```bash
# Atualizar ORGANOGRAMA-dados.json com os novos paths
# (Banco Geral e Python-Base agora dentro do Dexter)
# Regenerar HTML
# Regenerar Canvas
```

**Verificação manual:** abrir HTML → nó "Banco Geral" aparece dentro da camada "Dados" (não mais "Externos").

---

# APÊNDICE — CRITÉRIOS DE PRONTO PARA CADA FASE

| Fase | Pronto quando… |
|------|----------------|
| 1 | `AUDITORIA-2026-04-19.md` existe, ≥ 500 linhas, 6 seções, Dr. Jesus aprovou |
| 2 | `ORGANOGRAMA.html` abre offline e passa os 5 checks do T07 |
| 3 | Banco Geral acessível por 2 caminhos, 48 h sem erro, buscador-base-local funciona |
| 4 | Script teste entra no índice em ≤ 1 h, dashboard abre, não duplica |
| 5 | README + MAPA + INVENTÁRIO + DECISOES + MEMORY atualizados, Organograma v2 gerado |

---

# REGRAS DE PROTEÇÃO

- `rm -rf` **proibido** em toda esta operação. Use `mv /tmp/` como padrão.
- Todo comando com `mv` numa pasta > 100 MB exige confirmação explícita na sessão.
- Toda tarefa que falhar 2x → parar, diagnosticar causa raiz, não tentar 3ª vez cega.
- Se Dr. Jesus pedir pausa a qualquer momento: salvar estado em `AGORA.md` e fechar.
