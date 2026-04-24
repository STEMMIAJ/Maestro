# WORKFLOW.md — Fluxo de Trabalho

Ordem das fases do módulo. Não pular fase. Orquestrador controla progressão.

## Fase 1 — Taxonomia

**Equipe.** Taxonomia Pericial.

**Entrada.** `PROJECT-STRUCTURE.md` atual.

**Saída.** Árvore validada de Federal/Estadual/Banco-Transversal e situações
periciais, com pastas criadas vazias.

**Critério de saída.** Nenhuma situação pericial alvo fica sem pasta. Nenhum
nome viola `NAMING-CONVENTIONS.md`.

## Fase 2 — Protocolos e Quesitos

**Equipe.** Protocolos e Quesitos.

**Entrada.** Taxonomia fechada.

**Saída.** `Banco-Transversal/Protocolos/` e `Banco-Transversal/Quesitos/`
populados com material oficial. `02_Checklist_Qualidade.md` por situação.

**Critério de saída.** Toda situação tem pelo menos 1 protocolo aplicável
referenciado e conjunto de quesitos unificados vigentes.

## Fase 3 — Escalas e Instrumentos

**Equipe.** Protocolos e Quesitos (subfase).

**Saída.** `Banco-Transversal/Escalas/` com escalas validadas (AVD, Barthel,
VAS, Tinetti, Katz, PHQ-9, etc.) e orientações de uso por situação.

## Fase 4 — Coleta de Laudos e Processos

**Equipe.** Coleta.

**Saída.** `<Situacao>/casos/` com laudos reais/anonimizados indexados por
`FICHA.json`.

**Critério de saída.** Situação tem massa mínima (≥ 3 casos) ou é marcada como
"pendente de massa".

## Fase 5 — Contestações

**Equipe.** Contestação.

**Saída.** Matriz de padrões de ataque por situação + arquivos de impugnação
classificados.

## Fase 6 — Sentenças e Valoração

**Equipe.** Sentenças.

**Saída.** Corpus de decisões classificadas e vocabulário recorrente extraído.

## Fase 7 — Modelagem por Situação

**Equipe.** Modelagem de Laudo.

**Entrada.** Fases 2–6 com base mínima.

**Saída.** `01_Modelo_de_Laudo.md` por situação + `Banco-Transversal/Modelos-
Laudo/` consolidado.

**Critério de saída.** Modelo cita fontes internas (protocolos, quesitos,
casos, sentenças) e passa no checklist de qualidade da situação.

## Fase 8 — Automação (opcional, último)

Só depois de 1–7 estabilizados:

- Índices automáticos (`INDEX.md` gerado por script).
- Validadores (estrutura, nomes, campos de `FICHA.json`).
- Consumo pelos agentes de análise de processo do Dexter.

## Regra de progressão

- Só avança de fase quando o critério de saída está verificável por arquivo.
- Retrocesso é permitido e deve ser registrado em `TASKS_TODAY.md`.
- Cada fase fechada vira nota no diário do projeto-pai.
