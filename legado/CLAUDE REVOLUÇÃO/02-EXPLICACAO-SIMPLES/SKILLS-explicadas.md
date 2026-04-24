# SKILLS — o que são, como funcionam

## O que é (1 frase)
Skill = pasta com instruções (em markdown) que o Claude carrega automaticamente quando o tema da conversa bate.

## Diferença para Hook e Agente
- **Hook:** código que dispara em evento (preto-no-branco)
- **Skill:** instrução que o Claude lê quando relevante (orientação)
- **Agente:** instância nova do Claude para uma tarefa isolada

---

## Onde ficam
- Globais: `~/.claude/skills/[nome-da-skill]/SKILL.md`
- Plugin: `~/.claude/plugins/[plugin]/skills/[nome]/SKILL.md`

Sua MATRIZ v2.0 está em `~/.claude/skills/comunicacao-neurodivergente/SKILL.md`.

---

## Estrutura mínima de uma skill

```markdown
---
name: nome-curto-sem-espaco
description: Quando usar essa skill (frase que o Claude lê pra decidir se carrega)
---

# Conteúdo da skill

Instruções, regras, exemplos, checklists.
Pode ter quantos parágrafos quiser.
```

**Crítico:** o `description` é o gatilho. Se a frase não bater com a tarefa, eu não carrego a skill.

---

## Exemplo: sua skill `comunicacao-neurodivergente`

```yaml
---
name: comunicacao-neurodivergente
description: Como me comunicar com Jésus (autista TEA + TDAH + sobrecarga). Carregar SEMPRE.
---
```

`description: ... Carregar SEMPRE` faz com que eu sempre carregue, em qualquer tarefa.

---

## Quando o Claude carrega uma skill

1. Você manda mensagem
2. Eu vejo a lista de skills disponíveis (vem nos system reminders)
3. Comparo o tema da sua mensagem com o `description` de cada skill
4. Se >1% de chance de aplicar → carrego com `Skill` tool
5. Sigo as instruções dela durante toda a resposta

---

## Modos de carregar

### Auto (default)
Eu decido se carrega.

### Forçado pelo description
"Carregar SEMPRE" no description = eu carrego em toda conversa.

### Forçado pelo usuário
Você digita `/nome-da-skill` no prompt. Skill é carregada na hora.

---

## Skills úteis que você TEM hoje

| Skill | O que faz | Quando carrega |
|-------|-----------|----------------|
| `comunicacao-neurodivergente` | MATRIZ v2.0 (tom, limites, modos) | sempre |
| `python-base` | Consulta 90 falhas catalogadas antes de gerar Python | antes de qualquer Python |
| `using-superpowers` | Carrega outras skills automaticamente | sempre |

---

## Como criar uma skill nova

### Passo 1 — Escolher tema
Skill é para tema RECORRENTE. Se é uma coisa única, não vale a pena.

### Passo 2 — Criar pasta
```bash
mkdir -p ~/.claude/skills/minha-skill
```

### Passo 3 — Criar SKILL.md
```bash
cat > ~/.claude/skills/minha-skill/SKILL.md << 'EOF'
---
name: minha-skill
description: Quando o usuário pedir X, fazer Y
---

# Instruções

1. Sempre fazer assim
2. Nunca fazer assado
3. Exemplo concreto: ...
EOF
```

### Passo 4 — Testar
Reinicia o Claude Code. Manda mensagem que casa com `description`. Verifica se eu menciono a skill.

---

## Limites

- **Tamanho máximo:** ~5KB para SKILL.md (mais que isso pesa o contexto)
- **Quantas skills:** sem limite teórico, mas só ~10 carregam por sessão
- **Sub-arquivos:** uma skill pode ter `references/` com docs que carrego sob demanda

---

## Problemas conhecidos

| Sintoma | Causa | Solução |
|---------|-------|---------|
| Skill não carrega | `description` ruim | Reescrever com palavras-chave do uso real |
| Skill conflita com outra | Duas dizem coisa oposta | Resolver hierarquia (qual sobrepõe) |
| Skill esquece detalhe | Conteúdo grande | Quebrar em sub-skills ou usar `references/` |

---

## Diferença prática vs CLAUDE.md

| | CLAUDE.md | Skill |
|---|-----------|-------|
| Quando carrega | Sempre | Quando relevante |
| Tamanho | Pequeno (regras gerais) | Grande (instruções específicas) |
| Onde | `~/.claude/CLAUDE.md` | `~/.claude/skills/X/SKILL.md` |
| Exemplo | "tom seco, sem disclaimer" | "para análise pericial, fazer assim..." |

Use CLAUDE.md para regras universais. Use Skill para fluxos especializados.
