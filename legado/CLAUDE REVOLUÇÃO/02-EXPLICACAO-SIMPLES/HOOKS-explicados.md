# HOOKS — o que são, como funcionam

## O que é (1 frase)
Hook = pedaço de código que dispara automaticamente em um evento específico do Claude Code.

## Para que servem
Forçar comportamentos que eu (Claude) deveria seguir mas posso esquecer. Hook é código, não interpretação — funciona 100% das vezes.

## Onde ficam
- Configuração: `~/.claude/settings.json` (chave `hooks`)
- Scripts: `~/stemmia-forense/hooks/*.py`

---

## Tipos de evento (quando dispara)

| Evento | Quando dispara | Para que usar |
|--------|----------------|---------------|
| `SessionStart` | Quando você abre uma conversa nova | Carregar contexto, mostrar últimas sessões |
| `UserPromptSubmit` | Toda vez que você manda mensagem | Detectar frustração, registrar pedido |
| `PreToolUse` | Antes de eu usar uma ferramenta | Bloquear comando perigoso (ex: `rm -rf`) |
| `PostToolUse` | Depois de eu usar uma ferramenta | Logar o resultado |
| `Stop` | Antes de eu mandar resposta final | Bloquear "Feito" sem verificação |
| `SessionEnd` | Quando a sessão fecha | Salvar resumo, limpar temporários |
| `SubagentStop` | Quando um subagente termina | Capturar resultado do subagente |

---

## Seus 7 hooks ativos hoje

### 1. `anti_mentira_stop.py` (Stop hook)
**O que faz:** Bloqueia minha resposta se eu disser "Feito", "Pronto", "Corrigido" sem ter rodado verificação antes.

**Como funciona:**
1. Lê minha resposta antes de eu mandar
2. Procura palavras-gatilho ("Feito", "Pronto", etc)
3. Conta quantos `Bash`/`Read`/`Grep` rodei nessa resposta
4. Se zero verificações + alguma palavra-gatilho → BLOQUEIA
5. Eu sou forçado a rodar `ls`/`cat`/etc para provar antes de finalizar

**Resultado prático:** você nunca mais ouve "Feito" sem prova.

### 2. `anti_mentira_user_prompt.py` (UserPromptSubmit)
**O que faz:** Detecta quando você está frustrado/com pressa.

**Gatilhos:** caps lock excessivo, "agora", "porra", "cara", "mentindo", "enrolando", "pelo amor".

**Ação:** grava em `~/.claude/projects/-Users-jesus/memory/errors.jsonl` para eu lembrar de não cometer o mesmo erro.

### 3. `anti_mentira_session_start.py` (SessionStart)
**O que faz:** No início da sessão, mostra os últimos erros não-resolvidos para eu evitar repetir.

**Output exemplo:** o bloco "[ANTI-MENTIRA] Últimos erros do usuário não-resolvidos" que apareceu nesta sessão.

### 4. `bloquear_open.py` (PreToolUse)
**O que faz:** Bloqueia comando `open` (que abre apps no Mac) — você proibiu isso.

**Por quê:** abre janelas que te tiram do foco.

### 5. `verificar_acentos.py` (Stop hook)
**O que faz:** Procura português sem acento na minha resposta. Se achar, bloqueia.

**Exemplo bloqueado:** "voce ja viu" → forçado a "você já viu".

### 6. `auto_diario.py` (SessionEnd)
**O que faz:** Atualiza `~/Desktop/DIARIO-PROJETOS.md` com resumo da sessão.

### 7. `mesa_limpa.py` (PreToolUse)
**O que faz:** Bloqueia escrita de arquivo direto na raiz `~/Desktop/`. Força usar `~/Desktop/_MESA/`.

---

## Como criar um hook novo

### Estrutura
```python
#!/usr/bin/env python3
import json, sys

# 1. Lê o evento (entra por stdin)
data = json.loads(sys.stdin.read())

# 2. Decide o que fazer
if "rm -rf" in data.get("tool_input", {}).get("command", ""):
    # 3. Bloqueia
    print("BLOQUEADO: rm -rf proibido", file=sys.stderr)
    sys.exit(2)  # exit code 2 = bloqueia ferramenta

# 4. Deixa passar
sys.exit(0)
```

### Registrar em `settings.json`
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/stemmia-forense/hooks/bloquear_rm_rf.py"
          }
        ]
      }
    ]
  }
}
```

---

## Códigos de saída (importantes)

| Exit code | Significado |
|-----------|-------------|
| `0` | Tudo OK, deixa passar |
| `1` | Erro do hook (loga mas deixa passar) |
| `2` | BLOQUEAR a ferramenta. Mensagem do stderr vai para Claude. |

---

## Limites práticos

- **Quantos hooks rodar:** máximo ~10. Mais que isso = sessão lenta.
- **Tempo de execução:** cada hook deve rodar em <500ms. Senão trava o Claude.
- **Não fazer rede:** hooks que chamam API/internet quebram a fluidez.
- **Logar separado:** se o hook faz `print()`, esse texto vai pro Claude. Logs em arquivo.

Sua memória `feedback_hooks_sobrecarga.md` registra: 7 essenciais, não mais.

---

## Como testar um hook
```bash
echo '{"tool_input":{"command":"rm -rf /"}}' | python3 ~/stemmia-forense/hooks/bloquear_rm_rf.py
echo "Exit code: $?"
```
Se imprime "BLOQUEADO" e exit 2, está funcionando.

---

## Problemas conhecidos

| Sintoma | Causa | Solução |
|---------|-------|---------|
| Hook não dispara | `settings.json` mal formatado | Validar com `python3 -m json.tool ~/.claude/settings.json` |
| Sessão lenta | Hook fazendo I/O pesado | Mover lógica pesada pra background |
| Stop hook em loop | Hook bloqueia toda resposta | Adicionar exceção para resposta vazia |
