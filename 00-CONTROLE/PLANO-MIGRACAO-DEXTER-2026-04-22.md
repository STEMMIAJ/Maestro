# PLANO — Migração do Sistema de Perícias para STEMMIA Dexter como raiz única

**Criado:** 2026-04-22
**Autor:** Claude Opus 4 (claude-opus-4-7)
**Plano-mestre em:** `~/Desktop/STEMMIA Dexter/00-CONTROLE/PLANO-MIGRACAO-DEXTER-2026-04-22.md`
**Responsável:** Dr. Jesus
**Estimativa total:** 12–18h distribuídas em 8 fases com CKPT obrigatório entre cada uma (nenhuma fase ultrapassa 2h; as longas já vêm subdivididas)

---

## 2. Contexto

Hoje o ecossistema pericial está espalhado em 43+ paths canônicos (varrido em 22/abr/2026 pelo mapeador: 42/43 existem, 921.447 arquivos). Três árvores paralelas replicam parcialmente o mesmo código — `~/Desktop/ANALISADOR FINAL/scripts/`, `~/Desktop/STEMMIA Dexter/src/`, `~/stemmia-forense/src/` — cada uma com 57–98 scripts Python, parte duplicada, parte divergente. Symlinks reversos ligam `stemmia-forense/data/*` → `ANALISADOR FINAL/*` e `Dexter/PROCESSOS|SCRIPTS` → `ANALISADOR FINAL/*`. 12 launchd jobs, 12 entries cron, 14 hooks em `settings.json` e 5 MCPs em `.mcp.json` apontam paths hardcoded dessa bagunça. 10+ arquivos `.bat` Windows referenciam `%USERPROFILE%\Desktop\chrome-pje-profile`. O assinador CNJ `.pjeoffice-pro` tem JAR com path absoluto.

Problema concreto: qualquer refactor quebra pelo menos um dos 3 pontos (launchd, hooks, .bat Windows). Dr. Jesus esquece em qual árvore o script "verdadeiro" vive. Resultado esperado em 1 frase: **Dexter vira a raiz física única do sistema pericial; tudo o que for externo ou hardcoded mantém um symlink reverso no caminho legado até que o consumidor seja atualizado.**

Se não fizer: triplicação continua a divergir, próxima alteração urgente num script vai modificar a cópia errada, fluxos quebram silenciosamente.

---

## 3. Princípios não-negociáveis

- **Zero quebra de fluxo.** Nenhum script, agente, hook ou workflow pode ficar sem encontrar o arquivo que busca. Toda movimentação física deixa symlink reverso no caminho antigo.
- **Uma tarefa por vez.** Não pular, não agrupar. Cada tarefa tem critério de verificação objetivo.
- **Nada de "feito" sem output real.** Afirmação de conclusão exige comando executado + output colado.
- **Não deletar nesta iniciativa.** Remoção só com palavra-chave LIMPAR-LIBERADO numa sessão separada.
- **Tudo reversível.** Antes de qualquer mudança destrutiva: snapshot em 00-CONTROLE/migracoes/<data>/.
- **Máximo 2 retries.** Falhou 2x → parar, diagnosticar causa raiz, não tentar 3ª vez cega.
- **Checkpoint aprovado antes de liberar próxima fase.** Sem exceção.

---

## 4. Arquitetura final (estado-alvo)

```
~/Desktop/STEMMIA Dexter/                   ← RAIZ ÚNICA
├── 00-CONTROLE/
│   ├── AGORA.md
│   ├── ORGANOGRAMA.html
│   ├── PROTOCOLO-CLAUDE-CONSISTENTE.md
│   ├── TEMPLATE-PLANO.md
│   ├── PLANO-MIGRACAO-DEXTER-2026-04-22.md  ← ESTE PLANO
│   └── migracoes/
│       └── 2026-04-22/                      ← NOVO (snapshot pré-migração)
│           ├── launchctl-list.txt
│           ├── crontab.txt
│           ├── symlinks.txt
│           ├── mcp-backup.json
│           ├── settings-backup.json
│           └── mapa-pre.json
├── src/                                     ← árvore Python unificada (consolidada)
│   ├── pipeline/
│   ├── peticoes/
│   ├── honorarios/
│   ├── pje/
│   ├── jurisprudencia/
│   ├── monitor/
│   ├── automacoes/                          ← MOVIDO de ~/stemmia-forense/automacoes/
│   └── hooks/                               ← MOVIDO de ~/stemmia-forense/hooks/
├── PJE-INFRA/                               ← NOVO (guarda perfis Chrome/Playwright + .pje-browser-data)
│   ├── chrome-pje-profile/                  ← MOVIDO (+ symlink reverso em ~)
│   ├── chrome-pje-profile-playwright/       ← MOVIDO (+ symlink reverso em ~)
│   ├── .chrome-pje/                         ← MOVIDO (sem symlink — só 2 scripts)
│   └── .pje-browser-data/                   ← MOVIDO (+ symlink reverso)
├── PROCESSOS/                               ← symlink → ANALISADOR FINAL/processos (mantido)
├── SCRIPTS-LEGADO/                          ← symlink → ANALISADOR FINAL/scripts (mantido ATÉ F5)
├── BANCO-DADOS/                             ← já unificado (consolidação 20/abr)
├── PYTHON-BASE/                             ← já unificado (consolidação 20/abr)
├── PERÍCIA FINAL/                           ← mantido; internamente remapeia para src/
├── INBOX/
├── painel/
├── memoria/
├── templates/
├── referencias/
├── n8n/
├── agents/
├── skills/
└── docs/

~/stemmia-forense/                           ← symlink → ~/Desktop/STEMMIA Dexter/src
~/.pjeoffice-pro/                            ← NÃO MOVER (JAR CNJ hardcoded)
~/Desktop/ANALISADOR FINAL/                  ← mantido físico na Fase 4 (DUPLICAR via rsync, não mover)
~/Desktop/PERÍCIA/                           ← MOVIDO fisicamente para Dexter/PERICIA-CONTEUDO/
~/Desktop/Projetos - Plan Mode/              ← MANTIDO (duplicado para Dexter/plan-mode-mirror/)
~/Library/Mobile Documents/com~apple~CloudDocs/Stemmia/  ← adaptador (20 KB) mantido
```

Symlinks reversos criados (física em Dexter, alias no path antigo):
- `~/stemmia-forense` → `~/Desktop/STEMMIA Dexter/src`
- `~/chrome-pje-profile` → `~/Desktop/STEMMIA Dexter/PJE-INFRA/chrome-pje-profile`
- `~/chrome-pje-profile-playwright` → `~/Desktop/STEMMIA Dexter/PJE-INFRA/chrome-pje-profile-playwright`
- `~/.pje-browser-data` → `~/Desktop/STEMMIA Dexter/PJE-INFRA/.pje-browser-data`

---

## 5. Fases com tarefas numeradas

# FASE 0 — Pré-voo (snapshot + descarregar daemons)
**Estimativa:** 30 min (Curto)
**Risco:** Baixo
**Reversível?** Sim (nada é movido ainda)

## T00 — Criar pasta de snapshot
**Status:** [ ]
**Objetivo:** Criar diretório dedicado à migração de hoje.
**Comando exato:**
```bash
mkdir -p "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22"
```
**Output esperado:** `test -d` retorna 0; `ls` lista diretório vazio.
**Verificação:**
```bash
test -d "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22" && echo OK
```
**Se falhar:** verificar permissão em 00-CONTROLE; criar com `sudo` se necessário.

## T01 — Snapshot launchd
**Status:** [ ]
**Objetivo:** Congelar lista de jobs launchd ativos antes de qualquer unload.
**Comando exato:**
```bash
launchctl list | grep -Ei 'jesus|stemmia|pericia|dexter|pje|telegram|mesa|monitor|python-base' \
  > "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/launchctl-list.txt"
wc -l "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/launchctl-list.txt"
```
**Output esperado:** `wc -l` ≥ 10 linhas (temos ≥ 12 jobs conhecidos).
**Verificação:**
```bash
wc -l "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/launchctl-list.txt"
```
**Se falhar:** rodar `launchctl list` bruto e redirecionar sem grep.

## T02 — Snapshot crontab
**Status:** [ ]
**Objetivo:** Congelar cron entries.
**Comando exato:**
```bash
crontab -l > "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/crontab.txt" 2>&1
```
**Output esperado:** arquivo ≥ 10 linhas (12 entries conhecidas).
**Verificação:**
```bash
wc -l "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/crontab.txt"
```
**Se falhar:** aceitar "no crontab for jesus" e seguir; anotar divergência.

## T03 — Snapshot symlinks
**Status:** [ ]
**Objetivo:** Congelar mapa de todos os symlinks do ecossistema.
**Comando exato:**
```bash
{
  find "$HOME" -maxdepth 3 -type l 2>/dev/null
  find "$HOME/Desktop" -maxdepth 4 -type l 2>/dev/null
  find "$HOME/stemmia-forense" -maxdepth 4 -type l 2>/dev/null
} | sort -u > "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/symlinks.txt"
wc -l "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/symlinks.txt"
```
**Output esperado:** ≥ 60 linhas (69 symlinks conhecidos).
**Verificação:**
```bash
wc -l "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/symlinks.txt"
```
**Se falhar:** ampliar maxdepth; aceitar ≥ 40.

## T04 — Snapshot configs Claude
**Status:** [ ]
**Objetivo:** Backup `settings.json` + `.mcp.json` antes de editar.
**Comando exato:**
```bash
cp "$HOME/.claude/settings.json" "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/settings-backup.json"
cp "$HOME/.claude/.mcp.json"     "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/mcp-backup.json"
```
**Output esperado:** dois arquivos, cada um > 1 KB.
**Verificação:**
```bash
ls -l "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/"*.json
```
**Se falhar:** investigar path real do settings.json (pode estar em `~/.claude/plugins/`).

## T05 — Snapshot do mapa atual
**Status:** [ ]
**Objetivo:** Rodar mapeador e guardar JSON baseline.
**Comando exato:**
```bash
python3 "$HOME/stemmia-forense/automacoes/mapear_sistema_pericias.py" --json-only
cp "$HOME/stemmia-forense/automacoes/logs/mapa-sistema-pericias-LATEST.json" \
   "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/mapa-pre.json"
```
**Output esperado:** arquivo `mapa-pre.json` com `paths_existentes >= 42`.
**Verificação:**
```bash
python3 -c "import json; d=json.load(open('$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/mapa-pre.json')); print(sum(1 for p in d['paths'] if p['existe']))"
```
**Se falhar:** rodar com `--verbose`, corrigir o erro e repetir.

## T06 — Unload temporário de TODOS os launchd jobs pericial
**Status:** [ ]
**Objetivo:** Impedir que daemons escrevam em paths que estão sendo movidos.
**Comando exato:**
```bash
for plist in ~/Library/LaunchAgents/com.jesus.*.plist; do
  echo "unloading $plist"
  launchctl bootout gui/$(id -u) "$plist" 2>/dev/null || launchctl unload "$plist" 2>/dev/null
done
launchctl list | grep -c 'com.jesus' | awk '{print "restantes:", $0}'
```
**Output esperado:** "restantes: 0".
**Verificação:**
```bash
launchctl list | grep -c 'com.jesus'
```
**Se falhar:** unload individual usando `launchctl bootout` com caminho completo.

## CKPT0 — CHECKPOINT: Fase 0 aprovada?
**Status:** [⏸]
**Ação:** Dr. Jesus revisa o diretório `00-CONTROLE/migracoes/2026-04-22/` (6 arquivos). Confirma "ok fase 1" ou aponta ajustes.
**Gatilho para próxima fase:** mensagem explícita "ok fase 1".
**Entregáveis a revisar:**
- `launchctl-list.txt`, `crontab.txt`, `symlinks.txt`
- `settings-backup.json`, `mcp-backup.json`, `mapa-pre.json`
- Output do `grep -c com.jesus` = 0
**Se ajustes:** voltar à tarefa T<xx> correspondente.

---

# FASE 1 — Criar PJE-INFRA e mover perfis Chrome
**Estimativa:** 45 min (Curto)
**Risco:** Médio (afeta Selenium/Playwright + .bat Windows)
**Reversível?** Sim (symlink reverso preserva todo chamador legado)

## T10 — Criar PJE-INFRA
**Status:** [ ]
**Objetivo:** Nova pasta-mãe para perfis Chrome.
**Comando exato:**
```bash
mkdir -p "$HOME/Desktop/STEMMIA Dexter/PJE-INFRA"
```
**Output esperado:** dir existe, vazio.
**Verificação:**
```bash
test -d "$HOME/Desktop/STEMMIA Dexter/PJE-INFRA" && echo OK
```
**Se falhar:** verificar escrita no Dexter.

## T11 — Mover chrome-pje-profile com symlink reverso
**Status:** [ ]
**Objetivo:** Profile Selenium vai físico pro Dexter; alias em ~ mantém .bat Windows funcionando.
**Comando exato:**
```bash
set -e
mv "$HOME/chrome-pje-profile" "$HOME/Desktop/STEMMIA Dexter/PJE-INFRA/chrome-pje-profile"
ln -s "$HOME/Desktop/STEMMIA Dexter/PJE-INFRA/chrome-pje-profile" "$HOME/chrome-pje-profile"
```
**Output esperado:** `readlink ~/chrome-pje-profile` aponta para o Dexter; `test -d` OK.
**Verificação:**
```bash
readlink "$HOME/chrome-pje-profile"
test -d "$HOME/chrome-pje-profile" && echo OK
```
**Se falhar:** rollback `rm ~/chrome-pje-profile && mv "$HOME/Desktop/STEMMIA Dexter/PJE-INFRA/chrome-pje-profile" "$HOME/chrome-pje-profile"`.

## T12 — Mover chrome-pje-profile-playwright com symlink reverso
**Status:** [ ]
**Objetivo:** idem para Playwright.
**Comando exato:**
```bash
set -e
mv "$HOME/chrome-pje-profile-playwright" "$HOME/Desktop/STEMMIA Dexter/PJE-INFRA/chrome-pje-profile-playwright"
ln -s "$HOME/Desktop/STEMMIA Dexter/PJE-INFRA/chrome-pje-profile-playwright" "$HOME/chrome-pje-profile-playwright"
```
**Output esperado:** `readlink` ok; diretório acessível via path antigo.
**Verificação:**
```bash
readlink "$HOME/chrome-pje-profile-playwright" && test -d "$HOME/chrome-pje-profile-playwright" && echo OK
```
**Se falhar:** rollback análogo a T11.

## T13 — Mover .pje-browser-data com symlink reverso
**Status:** [ ]
**Objetivo:** 3º profile com env parcial `STEMMIA_PJE_PROFILE`.
**Comando exato:**
```bash
set -e
mv "$HOME/.pje-browser-data" "$HOME/Desktop/STEMMIA Dexter/PJE-INFRA/.pje-browser-data"
ln -s "$HOME/Desktop/STEMMIA Dexter/PJE-INFRA/.pje-browser-data" "$HOME/.pje-browser-data"
```
**Output esperado:** link OK.
**Verificação:**
```bash
readlink "$HOME/.pje-browser-data"
```
**Se falhar:** rollback.

## T14 — Mover .chrome-pje (sem symlink — só 2 scripts usam)
**Status:** [ ]
**Objetivo:** Esse não precisa de alias; os 2 scripts são nossos e serão atualizados na F5.
**Comando exato:**
```bash
mv "$HOME/.chrome-pje" "$HOME/Desktop/STEMMIA Dexter/PJE-INFRA/.chrome-pje"
```
**Output esperado:** `test -d "$HOME/.chrome-pje"` retorna 1 (não existe mais); destino existe.
**Verificação:**
```bash
test -d "$HOME/Desktop/STEMMIA Dexter/PJE-INFRA/.chrome-pje" && ! test -e "$HOME/.chrome-pje" && echo OK
```
**Se falhar:** rollback mv.

## T15 — Smoke-test perfis (abrir uma vez cada)
**Status:** [ ]
**Objetivo:** Verificar que Chrome/Chromium ainda acha o profile pelo caminho antigo.
**Comando exato:**
```bash
ls "$HOME/chrome-pje-profile/" | head -5
ls "$HOME/chrome-pje-profile-playwright/" | head -5
ls "$HOME/.pje-browser-data/" | head -5
```
**Output esperado:** 3 listagens não-vazias (cada uma ≥ 1 entry).
**Verificação:**
```bash
ls "$HOME/chrome-pje-profile/" | wc -l
```
**Se falhar:** symlink quebrado → refazer `ln -s` apontando corretamente.

## CKPT1 — CHECKPOINT: Fase 1 aprovada?
**Status:** [⏸]
**Ação:** Dr. Jesus confirma perfis acessíveis via path antigo.
**Gatilho para próxima fase:** "ok fase 2".
**Entregáveis a revisar:**
- `ls ~/Desktop/STEMMIA Dexter/PJE-INFRA/` lista 4 entradas
- 3 symlinks ativos em `~`
**Se ajustes:** voltar a T11–T14.

---

# FASE 2 — Consolidar stemmia-forense dentro do Dexter
**Estimativa:** 1h30 (Sessão média) — CRÍTICA
**Risco:** Alto (14 hooks + 5 MCPs + 10 launchd apontam paths hardcoded)
**Reversível?** Parcial (rollback rápido nos primeiros 7 dias via symlink reverso)

## T20 — Mover `~/stemmia-forense/automacoes` para Dexter/src/automacoes
**Status:** [ ]
**Objetivo:** Consolidar scripts de automação dentro da árvore Dexter.
**Comando exato:**
```bash
set -e
mkdir -p "$HOME/Desktop/STEMMIA Dexter/src"
mv "$HOME/stemmia-forense/automacoes" "$HOME/Desktop/STEMMIA Dexter/src/automacoes"
ln -s "$HOME/Desktop/STEMMIA Dexter/src/automacoes" "$HOME/stemmia-forense/automacoes"
```
**Output esperado:** `readlink ~/stemmia-forense/automacoes` aponta para Dexter.
**Verificação:**
```bash
readlink "$HOME/stemmia-forense/automacoes"
test -x "$HOME/stemmia-forense/automacoes/mapear_sistema_pericias.py" && echo OK
```
**Se falhar:** rollback mv + rm symlink.

## T21 — Mover `~/stemmia-forense/hooks` para Dexter/src/hooks
**Status:** [ ]
**Objetivo:** idem para hooks.
**Comando exato:**
```bash
set -e
mv "$HOME/stemmia-forense/hooks" "$HOME/Desktop/STEMMIA Dexter/src/hooks"
ln -s "$HOME/Desktop/STEMMIA Dexter/src/hooks" "$HOME/stemmia-forense/hooks"
```
**Output esperado:** `readlink` OK; arquivos do anti-mentira acessíveis.
**Verificação:**
```bash
readlink "$HOME/stemmia-forense/hooks"
ls "$HOME/stemmia-forense/hooks/" | grep -c '.py'
```
**Se falhar:** rollback.

## T22 — Rodar mapa mestre para validar integridade
**Status:** [ ]
**Objetivo:** Garantir que os 42/43 paths ainda respondem depois da F2.
**Comando exato:**
```bash
python3 "$HOME/stemmia-forense/automacoes/mapear_sistema_pericias.py" --json-only
python3 -c "import json; d=json.load(open('$HOME/stemmia-forense/automacoes/logs/mapa-sistema-pericias-LATEST.json')); ok=sum(1 for p in d['paths'] if p['existe']); print('ok:', ok)"
```
**Output esperado:** `ok: 42` (tolerância ±1 para Parallels offline).
**Verificação:** comando acima.
**Se falhar:** diff contra `mapa-pre.json` para identificar qual path caiu.

## T23 — Testar disparo de um hook anti-mentira
**Status:** [ ]
**Objetivo:** Confirmar que hook ainda é alcançado via path antigo.
**Comando exato:**
```bash
python3 "$HOME/stemmia-forense/hooks/anti_mentira_audit.py" --days 1
```
**Output esperado:** execução sem `FileNotFoundError`; output com "auditor" ou "OK".
**Verificação:**
```bash
python3 "$HOME/stemmia-forense/hooks/anti_mentira_audit.py" --days 1; echo exit=$?
```
**Se falhar:** verificar se o script tem shebang correto; se sim, paths internos podem estar hardcoded.

## CKPT2 — CHECKPOINT: Fase 2 aprovada?
**Status:** [⏸]
**Ação:** Dr. Jesus confirma mapa mestre 42/43 + hook ativo.
**Gatilho para próxima fase:** "ok fase 3".
**Entregáveis a revisar:**
- 2 novos symlinks (`~/stemmia-forense/automacoes`, `~/stemmia-forense/hooks`)
- mapa mestre regenerado
- anti-mentira respondendo
**Se ajustes:** voltar a T20–T23.

---

# FASE 3 — Atualizar configs Claude (settings.json + .mcp.json + CLAUDE.md global)
**Estimativa:** 1h30 (Sessão média)
**Risco:** Alto (configs mal-editadas = sessão Claude sem hooks/MCP)
**Reversível?** Sim (backups da Fase 0)

## T30 — Revisar settings.json: substituir `~/stemmia-forense` por `~/Desktop/STEMMIA Dexter/src`
**Status:** [ ]
**Objetivo:** Com symlink reverso em F2, settings.json funciona SEM alteração. Esta tarefa registra e **adia** a reescrita para depois de 30 dias. Ainda assim, gerar um rascunho da mudança para futuro uso.
**Comando exato:**
```bash
grep -n 'stemmia-forense' "$HOME/.claude/settings.json" | head -30
grep -c 'stemmia-forense' "$HOME/.claude/settings.json"
```
**Output esperado:** ≥ 10 matches (14 hooks conhecidos).
**Verificação:** comando acima.
**Se falhar:** configuração usada está em outro path (ex.: plugins); localizar com `grep -r stemmia-forense ~/.claude`.

## T31 — Gerar rascunho de substituição (não aplicar)
**Status:** [ ]
**Objetivo:** Preparar sed-ready sem executar; confirmar que symlink reverso da F2 já basta.
**Comando exato:**
```bash
cp "$HOME/.claude/settings.json" "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/settings-rewrite-draft.json"
sed -i '' 's|/Users/jesus/stemmia-forense|/Users/jesus/Desktop/STEMMIA Dexter/src|g' \
  "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/settings-rewrite-draft.json"
diff "$HOME/.claude/settings.json" "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/settings-rewrite-draft.json" | head -20
```
**Output esperado:** `diff` mostra ≥ 10 linhas alteradas.
**Verificação:**
```bash
diff "$HOME/.claude/settings.json" "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/settings-rewrite-draft.json" | grep -c '^<'
```
**Se falhar:** sed não fez nada → padrão de path diferente do esperado.

## T32 — Idem para .mcp.json
**Status:** [ ]
**Objetivo:** Rascunho da migração do `.mcp.json` (5 MCPs).
**Comando exato:**
```bash
cp "$HOME/.claude/.mcp.json" "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/mcp-rewrite-draft.json"
sed -i '' 's|/Users/jesus/stemmia-forense|/Users/jesus/Desktop/STEMMIA Dexter/src|g' \
  "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/mcp-rewrite-draft.json"
```
**Output esperado:** arquivo draft com diferenças vs original.
**Verificação:**
```bash
diff "$HOME/.claude/.mcp.json" "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/mcp-rewrite-draft.json" | grep -c '^<'
```
**Se falhar:** revisar JSON com jq; alterar manualmente.

## T33 — Adicionar no CLAUDE.md global seção "PÓS-MIGRAÇÃO 2026-04-22"
**Status:** [ ]
**Objetivo:** Registrar que o path oficial agora é Dexter; paths antigos ainda funcionam via symlink.
**Comando exato:** (usar Edit tool do Claude)
Incluir bloco no fim de `~/.claude/CLAUDE.md`:
```
# PATHS OFICIAIS PÓS-MIGRAÇÃO 2026-04-22
- Scripts: `~/Desktop/STEMMIA Dexter/src/` (aliases: `~/stemmia-forense/`, `~/Desktop/ANALISADOR FINAL/scripts/`)
- Perfis Chrome PJe: `~/Desktop/STEMMIA Dexter/PJE-INFRA/` (aliases: `~/chrome-pje-profile*`)
- Assinador CNJ: `~/.pjeoffice-pro/` (NÃO MOVER — JAR hardcoded)
```
**Output esperado:** `grep -c "PATHS OFICIAIS PÓS-MIGRAÇÃO" ~/.claude/CLAUDE.md` retorna 1.
**Verificação:**
```bash
grep -c "PATHS OFICIAIS PÓS-MIGRAÇÃO" "$HOME/.claude/CLAUDE.md"
```
**Se falhar:** edit manual via Edit tool.

## CKPT3 — CHECKPOINT: Fase 3 aprovada?
**Status:** [⏸]
**Ação:** Dr. Jesus revisa drafts settings/mcp + bloco CLAUDE.md.
**Gatilho para próxima fase:** "ok fase 4".
**Entregáveis a revisar:**
- `settings-rewrite-draft.json`, `mcp-rewrite-draft.json`
- `grep "PATHS OFICIAIS" ~/.claude/CLAUDE.md`
**Se ajustes:** reeditar drafts antes de aplicar.

---

# FASE 4 — iCloud: duplicar ANALISADOR FINAL, migrar PERÍCIA
**Estimativa:** 2–4h (Sessão longa — dividida em 3 subfases de ≤ 2h)
**Risco:** Alto (ANALISADOR FINAL 8,5 GB; PERÍCIA 3,2 GB; risco de sync remoto iCloud apagar original se fizer mv errado)
**Reversível?** Parcial (rsync mantém origem; só perigoso se usar mv direto em pasta sincronizada)

## T40 — Verificar estado iCloud (offloaded?)
**Status:** [ ]
**Objetivo:** Confirmar 0 arquivos offloaded; se > 0, baixar antes de mover.
**Comando exato:**
```bash
find "$HOME/Desktop/ANALISADOR FINAL" -name ".*.icloud" | wc -l
find "$HOME/Desktop/PERÍCIA" -name ".*.icloud" | wc -l
```
**Output esperado:** duas contagens = 0.
**Verificação:** comando acima.
**Se falhar:** baixar com `brctl download` em cada pasta antes de F4.

## T41 — Subfase A: DUPLICAR `ANALISADOR FINAL` para `Dexter/AF-ESPELHO/`
**Status:** [ ]
**Objetivo:** Cópia completa, **não** mv. Origem permanece intacta.
**Comando exato:**
```bash
mkdir -p "$HOME/Desktop/STEMMIA Dexter/AF-ESPELHO"
rsync -a --progress --info=stats2 \
  "$HOME/Desktop/ANALISADOR FINAL/" \
  "$HOME/Desktop/STEMMIA Dexter/AF-ESPELHO/"
```
**Output esperado:** `rsync` exit 0; contagem de arquivos ≥ 27000.
**Verificação:**
```bash
find "$HOME/Desktop/STEMMIA Dexter/AF-ESPELHO" -type f | wc -l
```
**Se falhar:** `rsync` com `--exclude='*.pdf.crdownload'`; reverificar espaço em disco.

## T42 — Subfase B: MIGRAR FÍSICO `PERÍCIA` para `Dexter/PERICIA-CONTEUDO/`
**Status:** [ ]
**Objetivo:** PERÍCIA tem 2 mod30d (praticamente arquivo morto) → mover físico + symlink reverso.
**Comando exato:**
```bash
mv "$HOME/Desktop/PERÍCIA" "$HOME/Desktop/STEMMIA Dexter/PERICIA-CONTEUDO"
ln -s "$HOME/Desktop/STEMMIA Dexter/PERICIA-CONTEUDO" "$HOME/Desktop/PERÍCIA"
```
**Output esperado:** `readlink ~/Desktop/PERÍCIA` OK; `find` conta ≥ 24000 arquivos.
**Verificação:**
```bash
readlink "$HOME/Desktop/PERÍCIA"
find "$HOME/Desktop/PERÍCIA" -type f | wc -l
```
**Se falhar:** rollback `rm symlink && mv back`.

## T43 — Subfase C: DUPLICAR `Projetos - Plan Mode` para `Dexter/plan-mode-mirror/`
**Status:** [ ]
**Objetivo:** Registros de sessão ficam com cópia dentro do Dexter; origem preservada.
**Comando exato:**
```bash
mkdir -p "$HOME/Desktop/STEMMIA Dexter/plan-mode-mirror"
rsync -a --progress "$HOME/Desktop/Projetos - Plan Mode/" "$HOME/Desktop/STEMMIA Dexter/plan-mode-mirror/"
```
**Output esperado:** contagem ≥ 48000 arquivos.
**Verificação:**
```bash
find "$HOME/Desktop/STEMMIA Dexter/plan-mode-mirror" -type f | wc -l
```
**Se falhar:** reservar mais espaço em disco; aceitar parcial se necessário.

## CKPT4 — CHECKPOINT: Fase 4 aprovada?
**Status:** [⏸]
**Ação:** Dr. Jesus confirma espelhos criados + PERÍCIA migrada + contagens coincidem.
**Gatilho para próxima fase:** "ok fase 5".
**Entregáveis a revisar:**
- `Dexter/AF-ESPELHO/` (≥ 27000 arquivos)
- `Dexter/PERICIA-CONTEUDO/` (≥ 24000)
- `Dexter/plan-mode-mirror/` (≥ 48000)
- 3 contagens no terminal
**Se ajustes:** refazer subfase problemática.

---

# FASE 5 — Migrar diretórios menores do Desktop + .bat Windows
**Estimativa:** 1h30 (Sessão média)
**Risco:** Médio
**Reversível?** Sim (mv + alias)

## T50 — Mover `Automações` (01–09) com symlinks reversos
**Status:** [ ]
**Objetivo:** 8 pastas `Automações/0X-*` que são symlinks para `stemmia-forense/src/*` — agora `stemmia-forense/src/` já aponta para Dexter. Apenas atualizar se necessário.
**Comando exato:**
```bash
ls -la "$HOME/Desktop/Automações/" | grep '^l' | awk '{print $9, "->", $11}'
```
**Output esperado:** 8 linhas de symlinks válidos resolvendo para Dexter via stemmia-forense.
**Verificação:**
```bash
for l in "$HOME/Desktop/Automações/"*; do test -e "$l" && echo "OK $l" || echo "BROKEN $l"; done
```
**Se falhar:** recriar symlink apontando para Dexter diretamente.

## T51 — Mover pastas-raiz menores para Dexter como subpastas
**Status:** [ ]
**Objetivo:** Mover `CLAUDE REVOLUÇÃO`, `MONITOR-FONTES`, `BUSCADOR-PERITOS`, `FENIX` (já pasta), `recuperacao-forense`, `PROCESSOS FINAIS`, `Processos Atualizados`, `TODOS OS PROCESSOS` → cada uma para `Dexter/legado/<nome>` + symlink reverso.
**Comando exato:** (executar em sequência, uma por vez com CKPT visual)
```bash
set -e
mkdir -p "$HOME/Desktop/STEMMIA Dexter/legado"
for d in "CLAUDE REVOLUÇÃO" "MONITOR-FONTES" "BUSCADOR-PERITOS" "recuperacao-forense" "PROCESSOS FINAIS" "Processos Atualizados" "TODOS OS PROCESSOS"; do
  src="$HOME/Desktop/$d"
  dst="$HOME/Desktop/STEMMIA Dexter/legado/$d"
  if [ -d "$src" ] && [ ! -L "$src" ]; then
    mv "$src" "$dst"
    ln -s "$dst" "$src"
    echo "moved+linked: $d"
  fi
done
```
**Output esperado:** ≥ 5 linhas "moved+linked".
**Verificação:**
```bash
ls -la "$HOME/Desktop/" | grep -c '^l'
```
**Se falhar:** identificar qual pasta travou; rollback individual.

## T52 — Atualizar 10+ `.bat` Windows (paths do profile)
**Status:** [ ]
**Objetivo:** `.bat` files usam `%USERPROFILE%\Desktop\chrome-pje-profile`. Com symlink reverso no `~`, **nada a mudar**. Verificar.
**Comando exato:**
```bash
find "$HOME/Desktop" -name '*.bat' -exec grep -l 'chrome-pje-profile' {} \; | tee "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/bats-afetados.txt"
wc -l "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/bats-afetados.txt"
```
**Output esperado:** lista com ≥ 10 `.bat` (todos funcionam pelo symlink).
**Verificação:**
```bash
wc -l "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/bats-afetados.txt"
```
**Se falhar:** se algum `.bat` usar path absoluto de Mac, isso precisa ser corrigido manualmente; listar para Dr. Jesus.

## CKPT5 — CHECKPOINT: Fase 5 aprovada?
**Status:** [⏸]
**Ação:** Dr. Jesus verifica Desktop + `bats-afetados.txt`.
**Gatilho para próxima fase:** "ok fase 6".
**Entregáveis a revisar:**
- `ls ~/Desktop/` — pastas antigas viraram symlinks
- `bats-afetados.txt`
**Se ajustes:** voltar a T51/T52.

---

# FASE 6 — Reload launchd + regenerar ORGANOGRAMA + mapa mestre
**Estimativa:** 45 min (Curto)
**Risco:** Médio (daemons precisam voltar a funcionar)
**Reversível?** Sim (launchctl unload/load)

## T60 — Reload launchd jobs
**Status:** [ ]
**Objetivo:** Recarregar os 10–12 jobs descarregados em T06.
**Comando exato:**
```bash
for plist in ~/Library/LaunchAgents/com.jesus.*.plist; do
  launchctl bootstrap gui/$(id -u) "$plist" 2>/dev/null || launchctl load "$plist" 2>/dev/null
done
sleep 3
launchctl list | grep -c 'com.jesus'
```
**Output esperado:** contagem ≥ 10 (= baseline da T01).
**Verificação:**
```bash
launchctl list | grep 'com.jesus'
```
**Se falhar:** comparar contra `launchctl-list.txt`; unload + load individual do job faltante.

## T61 — Regenerar ORGANOGRAMA D3
**Status:** [ ]
**Objetivo:** Atualizar `00-CONTROLE/ORGANOGRAMA.html` com novo estado.
**Comando exato:**
```bash
test -x "$HOME/Desktop/STEMMIA Dexter/src/automacoes/gerar_organograma.py" && \
  python3 "$HOME/Desktop/STEMMIA Dexter/src/automacoes/gerar_organograma.py" || \
  echo "sem script de organograma — atualizar manualmente"
```
**Output esperado:** arquivo `ORGANOGRAMA.html` com `mtime` recente.
**Verificação:**
```bash
stat -f '%m %N' "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA.html"
```
**Se falhar:** marcar como pendência pós-migração (não bloqueia CKPT6).

## T62 — Regenerar mapa mestre + PATHS_CANONICOS
**Status:** [ ]
**Objetivo:** Atualizar `mapear_sistema_pericias.py::PATHS_CANONICOS` para incluir novos paths do Dexter (PJE-INFRA, AF-ESPELHO, PERICIA-CONTEUDO, legado/*) e remover os que viraram symlinks redundantes.
**Comando exato:** (editar via Edit tool)
Adicionar em PATHS_CANONICOS:
```
"~/Desktop/STEMMIA Dexter/PJE-INFRA"
"~/Desktop/STEMMIA Dexter/AF-ESPELHO"
"~/Desktop/STEMMIA Dexter/PERICIA-CONTEUDO"
"~/Desktop/STEMMIA Dexter/legado"
"~/Desktop/STEMMIA Dexter/plan-mode-mirror"
```
Depois rodar:
```bash
python3 "$HOME/stemmia-forense/automacoes/mapear_sistema_pericias.py"
```
**Output esperado:** mapa mestre atualizado, `paths_existentes` ≥ 47.
**Verificação:**
```bash
grep -c '^- ' "$HOME/.claude/docs/SISTEMA-PERICIAS-MAPA-MESTRE.md"
```
**Se falhar:** ajustar PATHS_CANONICOS e rerodar.

## CKPT6 — CHECKPOINT: Fase 6 aprovada?
**Status:** [⏸]
**Ação:** Dr. Jesus confirma daemons ativos + mapa e organograma atualizados.
**Gatilho para próxima fase:** "ok fase 7".
**Entregáveis a revisar:**
- `launchctl list | grep com.jesus | wc -l` ≥ baseline
- `ORGANOGRAMA.html` com mtime recente
- Mapa mestre com novos paths
**Se ajustes:** voltar a T60–T62.

---

# FASE 7 — Verificação end-to-end (smoke test funcional)
**Estimativa:** 1h (Sessão média)
**Risco:** Baixo (só leitura/dry-run)
**Reversível?** N/A (não muda nada)

## T70 — hub.py dry-run
**Status:** [ ]
**Objetivo:** Rodar hub em modo dry.
**Comando exato:**
```bash
python3 "$HOME/Desktop/STEMMIA Dexter/src/hub.py" --dry 2>&1 | tail -20
```
**Output esperado:** exit 0; nenhuma linha com `FileNotFoundError`.
**Verificação:**
```bash
python3 "$HOME/Desktop/STEMMIA Dexter/src/hub.py" --dry > /tmp/hub.out 2>&1; echo exit=$?; grep -c FileNotFoundError /tmp/hub.out
```
**Se falhar:** se `hub.py` não existir nesse path, procurar com `find` e atualizar PATHS_CANONICOS.

## T71 — briefing_diario dry-run
**Status:** [ ]
**Objetivo:** Verificar briefing diário.
**Comando exato:**
```bash
python3 "$HOME/Desktop/STEMMIA Dexter/src/automacoes/briefing_diario.py" --dry 2>&1 | tail -10
```
**Output esperado:** exit 0.
**Verificação:** `echo $?` após o comando.
**Se falhar:** mesma estratégia T70.

## T72 — Monitor-fontes smoke
**Status:** [ ]
**Objetivo:** Orquestrador 5 fontes sem enviar Telegram.
**Comando exato:**
```bash
python3 "$HOME/Desktop/STEMMIA Dexter/legado/MONITOR-FONTES/orquestrador.py" --dry 2>&1 | tail -10
```
**Output esperado:** exit 0.
**Verificação:** idem T70.
**Se falhar:** marcar pendência.

## T73 — Script PJe (sem abrir Chrome — só import)
**Status:** [ ]
**Objetivo:** Verificar que o script de download PJe carrega módulos sem erro.
**Comando exato:**
```bash
python3 -c "import sys; sys.path.insert(0, '$HOME/Desktop/STEMMIA Dexter/src/pje'); import download_pje_139" 2>&1 | tail -5
echo exit=$?
```
**Output esperado:** exit 0.
**Verificação:** exit code.
**Se falhar:** ajustar `sys.path` ou localizar módulo.

## T74 — Mapa mestre final
**Status:** [ ]
**Objetivo:** Rodar mapeador uma última vez e comparar com baseline.
**Comando exato:**
```bash
python3 "$HOME/stemmia-forense/automacoes/mapear_sistema_pericias.py" --json-only
python3 - <<'PY'
import json
pre  = json.load(open('/Users/jesus/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/mapa-pre.json'))
post = json.load(open('/Users/jesus/stemmia-forense/automacoes/logs/mapa-sistema-pericias-LATEST.json'))
pre_ok  = sum(1 for p in pre['paths']  if p['existe'])
post_ok = sum(1 for p in post['paths'] if p['existe'])
print(f"pre={pre_ok} post={post_ok} delta={post_ok - pre_ok}")
PY
```
**Output esperado:** `post >= pre` (tolerância ±1). `delta >= 0`.
**Verificação:** comando acima.
**Se falhar:** algum path essencial quebrou; consultar diff detalhado.

## CKPT7 — CHECKPOINT: Fase 7 aprovada?
**Status:** [⏸]
**Ação:** Dr. Jesus revisa 5 outputs (hub, briefing, monitor, pje, mapa).
**Gatilho para finalização:** "ok encerrar migração" (ou próxima sessão se encontrar problema).
**Entregáveis a revisar:**
- 5 exit codes = 0
- delta do mapa ≥ 0
**Se ajustes:** voltar à fase onde quebrou.

---

## 7. Riscos e mitigação

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| launchd job não recarrega após F2/F6 | Média | Alto (daemons param) | T06 snapshot + reload sistemático em T60 + comparação contra `launchctl-list.txt` |
| MCP `.mcp.json` aponta path morto e Claude perde servidores | Média | Alto | Mantemos `~/stemmia-forense` como symlink reverso (F2); draft de edit em T32 só aplicado depois de 30 dias estáveis |
| iCloud sincronização remota apaga original depois de mv | Baixa | Crítico | F4 usa `rsync` (cópia) para ANALISADOR FINAL e plan-mode; PERÍCIA usa `mv` só porque está fora de iCloud |
| `.bat` Windows quebra (path hardcoded `%USERPROFILE%\Desktop\chrome-pje-profile`) | Baixa | Médio | Symlink reverso em `~/chrome-pje-profile` cobre; T15+T52 validam |
| `.pjeoffice-pro` JAR CNJ hardcoded quebra | Baixa | Alto | Plano promete **NÃO MOVER** `.pjeoffice-pro` (Block 10 — Não tocar) |
| Hooks anti-mentira param de funcionar (caminho para errors.jsonl muda) | Média | Médio | Symlink reverso em `~/stemmia-forense/hooks` mantém path; T23 valida |
| Daemon Telegram bot (PID KeepAlive) fica zumbi | Média | Médio | F0 descarrega via `bootout`; F6 recarrega; verificar PID novo em `launchctl list` |
| 3 árvores (AF/scripts, Dexter/src, stemmia-forense/src) continuam divergindo | Alta | Alto (longo prazo) | Esta iniciativa NÃO consolida scripts — só reduz pontos físicos de origem. Consolidação real fica para sessão futura (fase 8 fora deste plano) |
| PJe MCP trava sessão Claude se path mudou | Baixa | Alto | Symlink reverso em F2 cobre; usuário pode `--mcp-config` fallback |
| Rollback impossível após 30d (iCloud reconciliou) | Média | Médio | Backup rsync em `AF-ESPELHO/` persiste; origem só é apagada numa sessão futura LIMPAR-LIBERADO |

---

## 8. Rollback por fase

### Rollback Fase 0
Até 7 dias: nada a desfazer — F0 só cria snapshots (leitura + backup).
Para recarregar launchd em caso de abort:
```bash
for plist in ~/Library/LaunchAgents/com.jesus.*.plist; do launchctl load "$plist" 2>/dev/null; done
```

### Rollback Fase 1
Até 7 dias:
```bash
for name in chrome-pje-profile chrome-pje-profile-playwright .pje-browser-data .chrome-pje; do
  rm -f "$HOME/$name"
  mv "$HOME/Desktop/STEMMIA Dexter/PJE-INFRA/$name" "$HOME/$name"
done
rmdir "$HOME/Desktop/STEMMIA Dexter/PJE-INFRA"
```

### Rollback Fase 2
Até 7 dias:
```bash
for sub in automacoes hooks; do
  rm -f "$HOME/stemmia-forense/$sub"
  mv "$HOME/Desktop/STEMMIA Dexter/src/$sub" "$HOME/stemmia-forense/$sub"
done
```

### Rollback Fase 3
Até 30 dias:
```bash
cp "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/settings-backup.json" "$HOME/.claude/settings.json"
cp "$HOME/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/mcp-backup.json"      "$HOME/.claude/.mcp.json"
# CLAUDE.md global: remover bloco "PATHS OFICIAIS PÓS-MIGRAÇÃO 2026-04-22" via Edit.
```

### Rollback Fase 4
Até 7 dias:
```bash
# ANALISADOR FINAL: só apagar espelho (origem intacta)
rm -rf "$HOME/Desktop/STEMMIA Dexter/AF-ESPELHO"
# PERÍCIA:
rm -f "$HOME/Desktop/PERÍCIA"
mv "$HOME/Desktop/STEMMIA Dexter/PERICIA-CONTEUDO" "$HOME/Desktop/PERÍCIA"
# plan-mode-mirror: só apagar espelho
rm -rf "$HOME/Desktop/STEMMIA Dexter/plan-mode-mirror"
```
Depois de 30 dias: não reverter — considerar integrado.

### Rollback Fase 5
Até 7 dias:
```bash
for d in "CLAUDE REVOLUÇÃO" "MONITOR-FONTES" "BUSCADOR-PERITOS" "recuperacao-forense" "PROCESSOS FINAIS" "Processos Atualizados" "TODOS OS PROCESSOS"; do
  rm -f "$HOME/Desktop/$d"
  mv "$HOME/Desktop/STEMMIA Dexter/legado/$d" "$HOME/Desktop/$d"
done
```

### Rollback Fase 6
Até 7 dias:
```bash
# Reverter PATHS_CANONICOS via git (se controlado) ou editar manualmente.
# Reverter ORGANOGRAMA.html: restaurar de migracoes/2026-04-22/ se copiado antes.
```

### Rollback Fase 7
N/A — só verificação.

Depois de 30 dias: já integrado, corrigir pontualmente, não reverter.

---

## 9. Verificação end-to-end

```bash
# 1. Filesystem: mapa mestre conta ≥ 47 paths existentes
python3 "$HOME/stemmia-forense/automacoes/mapear_sistema_pericias.py" --json-only
python3 -c "import json; d=json.load(open('$HOME/stemmia-forense/automacoes/logs/mapa-sistema-pericias-LATEST.json')); print(sum(1 for p in d['paths'] if p['existe']))"
# Esperado: >= 47

# 2. launchd: ao menos 10 jobs 'com.jesus' carregados
launchctl list | grep -c 'com.jesus'
# Esperado: >= 10

# 3. Execução: hub.py carrega sem FileNotFoundError
python3 "$HOME/Desktop/STEMMIA Dexter/src/hub.py" --dry > /tmp/hub.out 2>&1
echo "exit=$?"
grep -c FileNotFoundError /tmp/hub.out
# Esperado: exit=0, FileNotFoundError count=0

# 4. Integração: anti-mentira audit responde
python3 "$HOME/stemmia-forense/hooks/anti_mentira_audit.py" --days 1
# Esperado: exit 0

# 5. Chrome profile: acessível via path antigo
ls "$HOME/chrome-pje-profile/" | wc -l
# Esperado: >= 1

# 6. iCloud: espelhos ok
find "$HOME/Desktop/STEMMIA Dexter/AF-ESPELHO" -type f | wc -l
# Esperado: >= 27000

# 7. mcp.json válido JSON
python3 -c "import json; json.load(open('$HOME/.claude/.mcp.json')); print('ok')"
# Esperado: "ok"

# 8. settings.json válido JSON
python3 -c "import json; json.load(open('$HOME/.claude/settings.json')); print('ok')"
# Esperado: "ok"
```

---

## 10. Arquivos afetados

### Criar (10)
| # | Caminho | O que é |
|---|---------|---------|
| 1 | `STEMMIA Dexter/00-CONTROLE/migracoes/2026-04-22/` | Pasta de snapshot |
| 2 | `.../launchctl-list.txt` | Baseline de daemons |
| 3 | `.../crontab.txt` | Baseline de cron |
| 4 | `.../symlinks.txt` | Baseline de symlinks |
| 5 | `.../settings-backup.json` | Backup config Claude |
| 6 | `.../mcp-backup.json` | Backup MCP |
| 7 | `.../mapa-pre.json` | Baseline mapa mestre |
| 8 | `.../settings-rewrite-draft.json` | Rascunho pós-migração (só draft) |
| 9 | `.../mcp-rewrite-draft.json` | Rascunho pós-migração (só draft) |
| 10 | `STEMMIA Dexter/PJE-INFRA/` | Nova pasta-mãe de perfis Chrome |

### Editar (4)
| Caminho | Mudança específica |
|---------|-------------------|
| `~/.claude/CLAUDE.md` | Adicionar bloco "PATHS OFICIAIS PÓS-MIGRAÇÃO 2026-04-22" |
| `~/stemmia-forense/automacoes/mapear_sistema_pericias.py` | Ampliar `PATHS_CANONICOS` com 5 novos paths Dexter |
| `~/.claude/docs/SISTEMA-PERICIAS-MAPA-MESTRE.md` | Regenerado por mapeador (bloco BEGIN/END-ESTADO-ATUAL) |
| `STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA.html` | Regenerar via script |

### Mover/renomear (14)
| De | Para | Tamanho aprox. |
|----|------|----------------|
| `~/chrome-pje-profile` | `Dexter/PJE-INFRA/chrome-pje-profile` | médio |
| `~/chrome-pje-profile-playwright` | `Dexter/PJE-INFRA/chrome-pje-profile-playwright` | médio |
| `~/.pje-browser-data` | `Dexter/PJE-INFRA/.pje-browser-data` | médio |
| `~/.chrome-pje` | `Dexter/PJE-INFRA/.chrome-pje` | pequeno |
| `~/stemmia-forense/automacoes` | `Dexter/src/automacoes` | médio |
| `~/stemmia-forense/hooks` | `Dexter/src/hooks` | pequeno |
| `~/Desktop/PERÍCIA` | `Dexter/PERICIA-CONTEUDO` | 3,2 GB / 24635 arq |
| `~/Desktop/CLAUDE REVOLUÇÃO` | `Dexter/legado/CLAUDE REVOLUÇÃO` | ~290 KB |
| `~/Desktop/MONITOR-FONTES` | `Dexter/legado/MONITOR-FONTES` | médio |
| `~/Desktop/BUSCADOR-PERITOS` | `Dexter/legado/BUSCADOR-PERITOS` | médio |
| `~/Desktop/recuperacao-forense` | `Dexter/legado/recuperacao-forense` | médio |
| `~/Desktop/PROCESSOS FINAIS` | `Dexter/legado/PROCESSOS FINAIS` | médio |
| `~/Desktop/Processos Atualizados` | `Dexter/legado/Processos Atualizados` | médio |
| `~/Desktop/TODOS OS PROCESSOS` | `Dexter/legado/TODOS OS PROCESSOS` | médio |

### Duplicar (2 — rsync, origem preservada)
| De | Para | Tamanho |
|----|------|---------|
| `~/Desktop/ANALISADOR FINAL/` | `Dexter/AF-ESPELHO/` | 8,5 GB / 27827 arq |
| `~/Desktop/Projetos - Plan Mode/` | `Dexter/plan-mode-mirror/` | 196 MB / 48208 arq |

### Não tocar (guarda explícita)
- `~/.pjeoffice-pro/` — JAR CNJ hardcoded path. **PROIBIDO MOVER.**
- `~/Library/Mobile Documents/com~apple~CloudDocs/Stemmia/` — adaptador iCloud 20 KB.
- `~/Desktop/ANALISADOR FINAL/` (origem) — permanece física; F4 só duplica.
- `~/Desktop/Projetos - Plan Mode/` (origem) — permanece física; F4 só duplica.
- `~/.claude/plugins/`, `~/.claude/agents/`, `~/.claude/skills/` — não tocar nesta migração.
- Qualquer arquivo de processo em `~/Desktop/ANALISADOR FINAL/processos/` — nunca mover/deletar nesta iniciativa.

---

## 11. Metadados de fechamento

## Aprovação
- [ ] Plano revisado por Dr. Jesus em 2026-04-22
- [x] Princípios não-negociáveis presentes
- [x] Todas as tarefas têm Output esperado verificável
- [x] Todas as fases têm CKPT
- [x] Riscos ≥ 3 com mitigação (10 riscos)
- [x] Rollback por fase presente (7 fases + nota)
- [x] Verificação end-to-end com comandos exatos (8 testes)

## Histórico
| Data | Versão | Mudança |
|------|--------|---------|
| 2026-04-22 | 1.0 | Criação inicial; síntese de 5 agentes paralelos (deps hunter, launchd/cron/hooks, symlinks, Chrome/PJe, iCloud risk) |

---

## Notas de execução

- **Paralelismo dentro das fases**: F0 tarefas T01–T04 podem rodar em paralelo (read-only). F4 subfases A, B e C podem rodar em paralelo se o disco aguentar 3 rsyncs simultâneos; preferir sequencial com monitor de I/O.
- **Não-paralelizável**: F1 → F2 → F3 (dependência forte) e F5 → F6 → F7 (verificação depende do reload).
- **Times de agentes sugeridos durante execução** (quando Dr. Jesus aprovar cada CKPT):
  - Fase 0: 1 agente general-purpose para snapshots (T01–T04 em paralelo interno).
  - Fase 1: 1 agente por pasta (4 em paralelo) — cada um move + symlink + verifica.
  - Fase 2: 1 agente por subpasta (automacoes, hooks) — 2 em paralelo.
  - Fase 3: 1 agente de edição (sequencial — ordem importa).
  - Fase 4: 1 agente por subfase (A, B, C — potencial paralelo).
  - Fase 5: 1 agente por pasta legada (7 em paralelo).
  - Fase 6: 1 agente (sequencial).
  - Fase 7: 4 agentes paralelos (hub/briefing/monitor/pje).
- **Critério de abort**: qualquer falha em T02 (launchd baseline) ou T05 (mapa baseline) — não prosseguir.
