# HANDOFF 2026-04-23 01h31

## Estado atual
- Plano ativo: nenhum — sessão livre (construção de infraestrutura Claude)
- Fase/passo: n/a
- Git (`~/`): branch `main`, 1 modificado (`.claude/CLAUDE.md`), muitos `.claude/plans/*.md` deletados/untracked
- Pasta de trabalho: `~/.claude/` + `~/stemmia-forense/hooks/`

## Feito nesta sessão
1. Auditoria Dexter (sessão anterior, compactada): arquivo `/Users/jesus/Desktop/STEMMIA Dexter/audit/inventario-atual.md` (20 KB, 7 fases, parecer "PODE REORGANIZAR COM ÁREAS CRÍTICAS A ISOLAR").
2. Persistidas 2 memórias novas corrigindo comportamento:
   - `feedback_panorama_contexto.md` — gatilho "onde eu to?" → 4 blocos (panorama/feito/falta/errado).
   - `feedback_nao_diagnosticar_sobrecarga.md` — proibido diagnosticar estado emocional.
3. Criada base oficial `~/.claude/docs/BASE-CLAUDE/` com 8 arquivos:
   - `INDICE.md`, `context-management.md`, `statusline.md`, `hooks-referencia.md`, `comandos-builtin.md`, `quando-compactar.md`, `monitoramento-qualidade.md`, `estado-local.md`.
4. StatusLine ativado em `~/.claude/settings.json` apontando para `~/stemmia-forense/hooks/medidor-tokens-statusline.sh` (refresh 30s). Backup: `~/.claude/settings.json.bak-pre-statusline` (35 KB).
5. Adicionado bloco no `~/.claude/CLAUDE.md` exigindo consulta à BASE-CLAUDE antes de criar/alterar qualquer coisa do Claude Code.
6. Memória `reference_base_claude.md` indexada em `MEMORY.md`.

## Falta (ordenado por dependência)
1. Reiniciar Claude Code pra statusLine aparecer na UI (config lida só no startup).
2. Verificar na UI se `ctx: XX% [ICON] ~N turnos` aparece corretamente.
3. (Opcional) Criar `~/stemmia-forense/automacoes/analisar_qualidade_sessao.py` — lê JSONL da sessão, conta perguntas ao user, tool re-calls, claims não-verificados; complementa o medidor quantitativo de tokens.
4. (Legado auditoria Dexter) commit git baseline + tag `pre-reorganizacao-2026-04-22` no Dexter.
5. (Legado auditoria Dexter) grep-map completo das 15+ referências `"STEMMIA Dexter"` em `~/stemmia-forense/` (arquivo + linha).
6. (Legado auditoria Dexter) decidir fonte-de-verdade: `memoria/` (Obsidian vault) vs raiz (`MEMORIA.md`, `DECISOES.md`, `ROTINA.md`).
7. (Legado auditoria Dexter) corrigir launchds com ERRO: `com.stemmia.relatorio-fluxos` (ERRO 2) e `com.jesus.python-base-digest` (ERRO 1).

## Plano de ação próxima sessão — execução PARALELA

### Onda 1 — disparar em 1 única mensagem
- [ ] Bash: `launchctl list | grep -E 'com.stemmia|com.jesus'` — diagnosticar launchds com erro.
- [ ] Bash: `cd "$HOME/Desktop/STEMMIA Dexter" && git status && git log --oneline -5` — preparar baseline pra commit+tag.
- [ ] Agent `Explore` (Opus, thorough) → mapear TODAS as ocorrências de `STEMMIA Dexter` e `stemmia-forense` em `~/stemmia-forense/` com path:linha:contexto. Output em arquivo `/Users/jesus/Desktop/STEMMIA Dexter/audit/grep-map-stemmia-forense.md`.
- [ ] Bash: `diff -rq "$HOME/Desktop/STEMMIA Dexter/memoria/" "$HOME/Desktop/STEMMIA Dexter/" 2>/dev/null | head -40` — comparar duplicação memoria/ vs raiz.

### Onda 2 — depende da Onda 1
- [ ] Decisão consciente: fonte-de-verdade = `memoria/` OU raiz. Registrar em memória + atualizar CLAUDE.md do Dexter.
- [ ] Commit baseline + tag `pre-reorganizacao-2026-04-22` no Dexter.
- [ ] Corrigir os 2 launchds com erro (ler plist, testar manualmente, reinstalar).

### Onda 3 — se houver
- [ ] Implementar `analisar_qualidade_sessao.py` conforme spec em `~/.claude/docs/BASE-CLAUDE/monitoramento-qualidade.md`.
- [ ] Plano de migração por fases para a reorganização conservadora (baseado no audit).

## Arquivos-chave para reler
- `/Users/jesus/Desktop/STEMMIA Dexter/audit/inventario-atual.md` — parecer completo da auditoria.
- `~/.claude/docs/BASE-CLAUDE/INDICE.md` — ponto de entrada da base Claude.
- `~/.claude/docs/BASE-CLAUDE/quando-compactar.md` — protocolo de compactação.
- `~/.claude/docs/BASE-CLAUDE/monitoramento-qualidade.md` — limiares e sinais.
- `~/.claude/CLAUDE.md:74-79` — bloco novo exigindo consulta à BASE-CLAUDE.
- `~/.claude/CLAUDE.md:81-89` — paths oficiais pós-migração 2026-04-22 (escrito pelo usuário/linter).
- `~/stemmia-forense/hooks/medidor-tokens-statusline.sh` — script do statusLine.

## Decisões já tomadas (não reabrir)
- StatusLine usa script existente `medidor-tokens-statusline.sh` (não recriar).
- Campo oficial de contexto = `context_window.used_percentage` (confirmado em docs oficiais).
- `/status`, `/tokens`, `/usage` NÃO existem como builtin — só `/context`, `/cost`, `/mcp`.
- `stats-cache.json` NÃO é oficial — não confiar como fonte de verdade.
- Auto-compact: compactar ANTES dele disparar, em >80% uso. `/compact focus on X` > auto-compact.
- Parecer da auditoria Dexter: "PODE REORGANIZAR, MAS COM ÁREAS CRÍTICAS A ISOLAR" — não revisitar.
- Regra comportamental: proibido diagnosticar sobrecarga emocional do usuário.

## Armadilhas conhecidas
- `refreshInterval` do statusLine é em ms. Usei 30000 (30s); se quiser mais rápido, diminuir — <1000ms trava UI.
- Script statusLine depende de `jq` no PATH.
- `jesusnoleto` é path obsoleto — usuário é `jesus`, qualquer script com `/Users/jesusnoleto/` está quebrado.
- Usuário é autista + TDAH; janela nova = falta de contexto, não emoção. Responder com protocolo de 4 blocos (panorama/feito/falta/errado).
- NUNCA "feito/rodando/pronto" sem verificar (hook anti-mentira bloqueia na Stop).
- NUNCA rm -rf, mv ../tmp sem token `LIMPAR-LIBERADO`.

---

## PROMPT DE RETOMADA — colar na nova sessão

```
Leia /Users/jesus/Desktop/_MESA/40-CLAUDE/handoffs/HANDOFF-2026-04-23-01h31.md
e execute a ONDA 1 imediatamente, em paralelo, disparando todos os itens
da Onda 1 numa única mensagem. Zero perguntas antes de agir.
```
