---
name: Verificar recursos existentes ANTES de criar/sugerir
description: Quando usuário pede X, primeiro buscar se X já existe no sistema dele. Evita meses pedindo coisa que já estava pronta (caso jsonl).
type: feedback
originSessionId: 11924f1d-2075-435c-82ab-62f52b3897c2
---
REGRA: Antes de criar QUALQUER novo script, hook, skill, agente, comando ou solução, eu DEVO rodar busca para confirmar que aquilo já não existe no sistema do usuário.

**Why:** Em 19/abr/2026 o usuário descobriu que pedia há MESES "salvar conversa em txt" — e eu nunca avisei que ele já tinha 1.871 sessões salvas em jsonl + 4 scripts prontos para converter (`gerar_transcricao_html.py`, `dump-transcript-readable.ts`, etc). Ele disse: "voce vai usar ultrathink e me sugerir agora como melhorar tudo isso". Caso clássico de eu construir do zero ignorando ferramenta dele já existente.

**How to apply, ANTES de propor solução:**
1. `find ~/Desktop ~/.claude ~/stemmia-forense -name "*<palavra-chave>*"` 
2. `grep -r "<funcionalidade>" ~/.claude/projects/-Users-jesus/memory/`
3. Listar agentes em `~/.claude/agents/` e ver se já cobre
4. Listar skills em `~/stemmia-forense/skills/` e ver se já cobre
5. Conferir scripts em `~/Desktop/STEMMIA Dexter/_arquivo/Open/analisador-final/scripts/`
6. Conferir scripts em `~/.Trash/CLAUDE REVISADO/scripts/` (recuperáveis)

**Reportar SEMPRE:**
- "Você já tem X em /caminho/Y" — antes de oferecer construir.
- "Existe agente Z que faz isso" — antes de criar novo agente.
- Se NÃO existir, dizer explicitamente: "Verifiquei e não existe — vou criar."

**Inventário básico do sistema (atualizado 19/abr/2026):**
- 76 agentes em `~/.claude/agents/`
- 38 skills em `~/stemmia-forense/skills/`
- 56+ scripts Python em `~/.Trash/CLAUDE REVISADO/scripts/` (precisa restaurar)
- 17 MCPs configurados
- 1.871 sessões jsonl em `~/.claude/projects/-Users-jesus/`
- FTP configurado para stemmia.com.br/webdev/
