---
titulo: Skill "modo-sonnet" — relay de modelos com fila para Opus preservando decisões críticas
tipo: evidencia
dominio: Prompt eng.
subtopico: engenharia de skill Claude Code + arquitetura multi-modelo
nivel_demonstrado: 3
versao: 0.1
status: validada
ultima_atualizacao: 2026-04-23
fonte: /Users/jesus/.claude/skills/modo-sonnet/SKILL.md
---

## Descrição
Skill custom que rebaixa a sessão principal para Sonnet (economia Max 20x) mas enfileira tudo que exige
raciocínio profundo em `~/Desktop/_MESA/40-CLAUDE/fila-opus/{slug}/` para auditoria posterior por Opus
(skill irmã `opus-auditor`). Gatilhos incluem variações fonéticas do termo ("sonic"/"sonete"/"sonet")
e gírias operacionais ("gambiarra", "bota no caro", "segura o opus") — resolve o fato do usuário (TEA+TDAH)
não lembrar o nome técnico.

## Arquivo real
`/Users/jesus/.claude/skills/modo-sonnet/SKILL.md`

## Habilidade demonstrada
- `Prompt eng.prompts de sistema` — 3 (description com >50 variações de gatilho)
- `Agentes.arquitetura multi-agente` — 3 (skill emparelhada com opus-auditor via fila filesystem)
- `Prompt eng.context caching` — 2 (design implícito para economizar tokens pesados)
- `Python.sintaxe básica` — N/A (é markdown YAML)

## Trecho relevante
```markdown
---
name: modo-sonnet
description: |
  Rebaixa a sessão para Sonnet preservando progresso, mas ENFILEIRA para Opus tudo que
  exige raciocínio profundo. Economiza Opus no Max 20x sem perder qualidade nas decisões críticas.

  Use when Dr. Jesus says any of (linguagem coloquial dele, aceitar variações fonéticas):

  GAMBIARRA (termo preferido):
  - "ativa a gambiarra"
  - "faz a gambiarra do modelo"
  - "bota na gambiarra"
  ...
  REBAIXAR:
  - "rebaixa pra sonic"
  - "aquela habilidade de rebaixar"
  ...
  ECONOMIA:
  - "segura o caro"
  - "deixa o opus descansar"
  ...
---
```

## Data
2026-04-23 (ver `reference_relay_modelos.md` na MEMORY).

## Validação externa
**Forte** — skill listada no índice global `/Users/jesus/.claude/skills/`. Par com `opus-auditor`. Fila
em `~/Desktop/_MESA/40-CLAUDE/fila-opus/`. Economia direta contra billing Max 20x.

## Limitações conhecidas
- Description com muitas variações aumenta a chance de falso-positivo em matching.
- Não há métrica de quantas vezes gatilhou nem taxa de acerto.
- Depende de `opus-auditor` ser executado periodicamente — se o usuário esquecer, fila acumula.
