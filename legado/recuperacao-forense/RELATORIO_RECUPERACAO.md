# RELATÓRIO RECUPERAÇÃO FORENSE v3 — ARQUIVOS DELETADOS / MODIFICADOS
**Data:** 19/abr/2026 02:10  
**Escopo:** ~/.claude, ~/stemmia-forense, ~/Desktop/src/pje, ~/.Trash, snapshots APFS, npm cache, sessões jsonl  
**Coletado por:** 9 agentes paralelos (outputs em `agentes/01-*.md` ... `09-*.md`)

---

## TL;DR (3 linhas)

1. **38 skills + 3 hooks + 5 scripts PJe estão na Trash** (`~/.Trash/CLAUDE REVISADO/`) — 100% recuperáveis com `cp -R`.
2. **CLAUDE.md global atual (`~/.claude/CLAUDE.md`) tem 65 linhas, modificado em 13/mar** — versão antiga; existem 80+ outras versões em iCloud/plugins/Dexter para comparar e mesclar.
3. **NÃO há backup Time Machine, NÃO há snapshots APFS** — tudo que não está em Trash, iCloud ou git já é irrecuperável.

---

## ARQUIVOS DELETADOS LOCALIZADOS NA TRASH

### Skills do stemmia-forense (38 skills) — `~/.Trash/CLAUDE REVISADO/plugins/stemmia-forense/skills/`
| Skill | Arquivo |
|---|---|
| mapa, pipeline, conferir-peticoes, estilo, verificar, peticao, organizar, rapida, pipeline-rapido, stemmia, proposta, esforco, quesitos, nomeacao, pipeline-contestacao, adapte, pdf, requisito, aceite, correlacionar, priorizar, pipeline-batch, agendar, saude, conferir, completa, contestar, terminal-grid, documento, backup-interacoes, pipeline-laudo, verificador-portugues, triagem-pericial, cowork, justificar | SKILL.md / skill.md |

### Hooks (3) — `~/.Trash/CLAUDE REVISADO/hooks/`
- `monitor-uso-claude.sh`
- `statusline-uso-claude.sh`
- `limpar-claude.sh`

### Scripts PJe (5) — `~/.Trash/CLAUDE REVISADO/scripts/`
- `atualizar-pje.py`
- `conectar_pje.sh`
- `sincronizar_aj_pje.py`
- `monitor-publicacoes/comunica_pje.py`
- `monitor-publicacoes/__pycache__/comunica_pje.cpython-314.pyc`

### Documentos / configs
- `01-CLAUDE-GLOBAL.md`
- `02-CLAUDE-LOCAL-ANALISADOR.md`
- `config/LIMITES-USO-CLAUDE.conf`
- `config/REF-ALTERNATIVAS-CLAUDE.md`
- `MEUS-PROCESSOS.md`
- `DOLPHIN-MALL-GUIA-COMPRAS.md`

---

## CLAUDE.md ENCONTRADOS (cruzamento de versões)

Total: **80+ arquivos `CLAUDE.md`** ativos no sistema. Versões relevantes para comparação:

| Caminho | Mod | Linhas | Tipo |
|---|---|---|---|
| `~/.claude/CLAUDE.md` (symlink iCloud) | 13/mar | 65 | GLOBAL — versão ANTIGA |
| `~/Desktop/STEMMIA Dexter/CLAUDE.md` | 17/abr | 5714 bytes | HUB — versão recente |
| `~/Desktop/CLAUDE.md` | (atual) | 29 | DESKTOP fallback |
| `~/stemmia-forense/CLAUDE.md` | (presente) | — | plugin |
| `~/Library/Mobile Documents/.../Stemmia/claude-config/CLAUDE.md` | (iCloud master) | — | source-of-truth do symlink |
| `~/Desktop/STEMMIA Dexter/RECUPERACAO-CLAUDE-2026-04-17/pre-restauracao-20260416-235538/CLAUDE.md` | 16/abr 23:55 | snapshot pré-restauração |

Todas copiadas para `~/Desktop/recuperacao-forense/recuperados/claude-md/` (renomeadas com path embutido no nome do arquivo).

---

## FONTES DE RECUPERAÇÃO POR SISTEMA

| Fonte | Status | O que tem |
|---|---|---|
| `~/.Trash/CLAUDE REVISADO/` | ATIVO | 38 skills + 3 hooks + 5 scripts + 6 docs |
| `~/Desktop/STEMMIA Dexter/RECUPERACAO-CLAUDE-2026-04-17/pre-restauracao-20260416-235538/` | ATIVO | snapshot completo de hooks de 16/abr (incl. `bloquear-perguntas-retoricas.py`) |
| iCloud master (`~/Library/.../claude-config/`) | ATIVO | settings.json.bak-anti-mentira-20260417025657, várias backups |
| npm cache (`~/.npm`) | 8.9 GB | versões 2.1.78 → 2.1.114 do `@anthropic-ai/claude-code` para downgrade/reinstall |
| Time Machine | **AUSENTE** | sem destino, sem snapshots |
| APFS local snapshots | **AUSENTE** | `tmutil listlocalsnapshots /` vazio |
| Git reflog projetos | parcialmente útil | só caches de plugins — repos de usuário sem deleções rastreadas |
| Sessões jsonl (`~/.claude/projects/-Users-jesus/`) | ATIVO | menções históricas a hooks/skills (referência, não conteúdo) |

---

## RECUPERAÇÕES JÁ EXECUTADAS

Pasta `~/Desktop/recuperacao-forense/recuperados/`:
- `claude-md/` — 80+ versões de CLAUDE.md copiadas (renomeadas por path)
- `trash/` — `DOLPHIN-MALL-GUIA-COMPRAS.md` (único .md solto na raiz da Trash)

NÃO foi executada cópia automática de:
- skills do stemmia-forense (volume grande, exige decisão de merge)
- hooks (idem — alguns nomes conflitam com `~/stemmia-forense/hooks/` atual)
- scripts PJe (precisam ir para `~/Desktop/src/pje/scripts/`, não para `recuperados/`)

---

## COMANDOS PRONTOS PARA RESTAURAÇÃO

### A. Restaurar 38 skills do stemmia-forense
```bash
SRC="/Users/jesus/.Trash/CLAUDE REVISADO/plugins/stemmia-forense/skills"
DST="/Users/jesus/Library/Mobile Documents/com~apple~CloudDocs/Stemmia/claude-config/plugins/stemmia-forense/skills"
mkdir -p "$DST"
# Listar antes de copiar:
ls "$SRC"
# Copiar (mantém perms):
cp -Rn "$SRC/"* "$DST/"     # -n = não sobrescrever, segurança
ls "$DST"   # confirmar
```

### B. Restaurar 3 hooks (resolvendo conflito de nomes)
```bash
SRC="/Users/jesus/.Trash/CLAUDE REVISADO/hooks"
DST="/Users/jesus/stemmia-forense/hooks"
# Comparar com versão atual antes:
for f in monitor-uso-claude.sh statusline-uso-claude.sh limpar-claude.sh; do
  diff "$SRC/$f" "$DST/$f" 2>/dev/null && echo "$f: idênticos" || echo "$f: DIFEREM"
done
# Decisão: se diferem, copiar como .restaurado e revisar manualmente:
for f in monitor-uso-claude.sh statusline-uso-claude.sh limpar-claude.sh; do
  cp "$SRC/$f" "$DST/${f%.sh}.RESTAURADO.sh"
done
```

### C. Restaurar 5 scripts PJe
```bash
SRC="/Users/jesus/.Trash/CLAUDE REVISADO/scripts"
DST="/Users/jesus/Desktop/src/pje/scripts-recuperados"
mkdir -p "$DST"
cp "$SRC/atualizar-pje.py" "$DST/"
cp "$SRC/conectar_pje.sh" "$DST/"
cp "$SRC/sincronizar_aj_pje.py" "$DST/"
cp -R "$SRC/monitor-publicacoes" "$DST/"
ls -la "$DST"
```

### D. Restaurar settings.json com hooks anti-mentira
```bash
SRC="/Users/jesus/Library/Mobile Documents/com~apple~CloudDocs/Stemmia/claude-config/settings.json.bak-anti-mentira-20260417025657"
DST="/Users/jesus/Library/Mobile Documents/com~apple~CloudDocs/Stemmia/claude-config/settings.json"
# Salvar atual antes:
cp "$DST" "$DST.PRE-RESTAURO-19042026"
# Restaurar:
cp "$SRC" "$DST"
# Verificar:
python3 -c "import json; d=json.load(open('$DST')); print('hooks:', list(d.get('hooks', {}).keys()))"
```

### E. Configurar Time Machine para evitar perda futura
```bash
# Listar discos disponíveis:
diskutil list
# Configurar destino (substituir pelo seu disco):
sudo tmutil setdestination -a /Volumes/SEU_DISCO_BACKUP
sudo tmutil enable
sudo tmutil startbackup --auto
tmutil destinationinfo
```

### F. Buscar arquivos PJe ausentes em iCloud
```bash
# baixar_push_pje.py
mdfind -name "baixar_push_pje.py"
# iniciar_chrome.bat
mdfind -name "iniciar_chrome.bat"
# Buscar em iCloud com find direto (Spotlight pode ignorar iCloud):
find "/Users/jesus/Library/Mobile Documents" -type f -name "baixar_push_pje.py" 2>/dev/null
find "/Users/jesus/Library/Mobile Documents" -type f -name "iniciar_chrome.bat" 2>/dev/null
```

---

## ARQUIVOS IRRECUPERÁVEIS (motivo técnico)

| Arquivo | Motivo |
|---|---|
| `~/Desktop/src/pje/baixar_push_pje.py` | Não está na Trash, sem TM, sem snapshot APFS, sem git history (projeto não está versionado). Só recuperável se cópia em iCloud (busca pendente) |
| `~/Desktop/src/pje/iniciar_chrome.bat` | Mesma situação |
| `~/Desktop/src/pje/CLAUDE.md` original | Mesma situação — pode ser reconstruído com base em `~/Desktop/STEMMIA Dexter/RECUPERACAO-CLAUDE-2026-04-17/` |
| `~/Desktop/src/pje/.claude/` original | Diretório não está na Trash; reconstruir copiando de outro projeto-modelo |
| Hooks que estavam em `settings.json` antes do upgrade nativo | Backup `settings.json.bak-anti-mentira-20260417025657` é a fonte mais recente disponível |

---

## PRÓXIMOS PASSOS RECOMENDADOS (ORDEM)

1. Rodar comando **F** para tentar achar `baixar_push_pje.py` e `iniciar_chrome.bat` em iCloud.
2. Rodar comando **D** para devolver hooks anti-mentira ao settings.json.
3. Rodar comando **A** para restaurar 38 skills.
4. Rodar comando **B** revisando diffs antes de aceitar.
5. Rodar comando **C** para devolver scripts PJe.
6. Rodar comando **E** para ativar Time Machine (sem isso, próxima perda é definitiva).
7. **NÃO esvaziar a Trash** até confirmar que tudo foi restaurado e validado.

---

## ARQUIVOS DE EVIDÊNCIA

- `~/Desktop/recuperacao-forense/agentes/01-git-reflog.md` (30KB)
- `~/Desktop/recuperacao-forense/agentes/02-trash.md`
- `~/Desktop/recuperacao-forense/agentes/03-timemachine.md`
- `~/Desktop/recuperacao-forense/agentes/04-npm-cache.md`
- `~/Desktop/recuperacao-forense/agentes/05-skills-hooks.md`
- `~/Desktop/recuperacao-forense/agentes/06-claudemd.md` (44KB)
- `~/Desktop/recuperacao-forense/agentes/07-deletions-14d.md`
- `~/Desktop/recuperacao-forense/agentes/08-modifications-14d.md` (1.9MB)
- `~/Desktop/recuperacao-forense/agentes/09-sessao-mentions.md` (133MB)
- `~/Desktop/recuperacao-forense/recuperados/claude-md/` — 80+ CLAUDE.md
- `~/Desktop/recuperacao-forense/recuperados/trash/` — md soltos
