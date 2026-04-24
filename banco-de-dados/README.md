# Banco de Dados — Stemmia Dexter (Perícia Médica Judicial)

Módulo de organização e análise de perícia médica judicial do Stemmia Dexter.
Reúne taxonomia, protocolos, quesitos, laudos, contestações, sentenças e modelos
por situação pericial, agrupados em três blocos: Federal, Estadual e Banco
Transversal.

## Objetivo

> Nota: Justiça do Trabalho é ramo federal autônomo — por isso entra sob `Federal/Trabalhista/`.

Ter em um único repositório:

- Árvore estável de áreas → subáreas → situações → temas periciais.
- Protocolos oficiais (ABMLPM, AMB, CFM) e checklists de qualidade.
- Quesitos unificados (Justiça Federal, TRFs, TST, TJs).
- Laudos de referência indexados por situação.
- Contestações e padrões de ataque (omissão, contradição, falta de nexo).
- Sentenças/acórdãos que acolhem ou criticam laudos, com extração de linguagem.
- Modelos de laudo por situação, derivados do material acima.

## Estrutura de pastas (alto nível)

```
banco-de-dados/
├── Federal/               # Previdenciário, Trabalhista, Cível federal
├── Estadual/              # Cível, Acidentário, Família
└── Banco-Transversal/     # Protocolos, Quesitos, Escalas, Jurisprudência,
                           # Modelos-Laudo, Contestações, Sentenças,
                           # Glossario, CID-Referencia
```

Detalhamento completo em `PROJECT-STRUCTURE.md`.

## Arquivos de controle

| Arquivo | Função |
|---|---|
| `CLAUDE.md` | Instruções permanentes para o Claude Code neste módulo. |
| `AGENTS.md` | Times de agentes (Orquestrador + 6 equipes). |
| `WORKFLOW.md` | Fases de trabalho (taxonomia → modelos). |
| `PROJECT-STRUCTURE.md` | Árvore detalhada. |
| `NAMING-CONVENTIONS.md` | Padrões de nomeação. |
| `TASKS_TODAY.md` | Lista de tarefas da sessão atual. |
| `INTEGRACAO-BANCO-GERAL.md` | Ligação com `BANCO-DADOS/` (biblioteca de referência). |

## Relação com o banco geral

Este módulo (`banco-de-dados/`, situação pericial) consome mas **não duplica**
o banco geral (`../BANCO-DADOS/`, área de conhecimento). Regras e mapa de
dependências em `INTEGRACAO-BANCO-GERAL.md`.

## Como navegar

1. Ler `CLAUDE.md` antes de qualquer ação.
2. Consultar `WORKFLOW.md` para saber em qual fase está.
3. Usar `AGENTS.md` para acionar o time correto.
4. Seguir `NAMING-CONVENTIONS.md` ao criar/renomear arquivos.
5. Atualizar `TASKS_TODAY.md` no início e fim de cada sessão.

## Escopo explícito

- IN: perícia médica judicial (Federal/Estadual), documentação técnica.
- OUT: laudos extrajudiciais, convênios, auditoria hospitalar, assistência.
- OUT: perícia criminal (corpo de delito, insanidade mental, lesão corporal) — não atendida neste banco.
