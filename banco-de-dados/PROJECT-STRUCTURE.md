# PROJECT-STRUCTURE.md — Árvore do Banco de Dados Pericial

Árvore detalhada do módulo `banco-de-dados/`. Qualquer mudança aqui exige
passagem pela Equipe de Taxonomia (`AGENTS.md`).

## Nível 0 — blocos

```
banco-de-dados/
├── Federal/
├── Estadual/
└── Banco-Transversal/
```

## Federal/

Perícias em ações de competência federal.

```
Federal/
├── Previdenciario/
│   ├── Auxilio-Incapacidade-Temporaria/
│   ├── Aposentadoria-Por-Incapacidade-Permanente/
│   ├── Auxilio-Acidente/
│   ├── BPC-LOAS/
│   ├── Isencao-IR-Doenca-Grave/
│   ├── Revisional-Incapacidade/
│   ├── Pensao-Morte-Invalidez-Dependente/
│   └── Majoracao-25-Grande-Invalidez/
├── Trabalhista/                    # Justiça do Trabalho (ramo federal autônomo)
│   ├── Doenca-Ocupacional/
│   ├── Acidente-Trabalho/
│   ├── Insalubridade-Periculosidade/
│   └── Nexo-Tecnico-Epidemiologico-NTEP/
└── Civel/
    ├── DPVAT/
    ├── Responsabilidade-Civil-Medica/
    ├── Militar-Reforma-Invalidez/
    └── Servidor-Federal-Invalidez/
```

## Estadual/

Perícias em ações de competência estadual.

```
Estadual/
├── Civel/
│   ├── Erro-Medico/
│   ├── Plano-Saude/
│   ├── Seguro-Privado/
│   ├── Dano-Moral-Estetico/
│   └── Servidor-Estadual-Invalidez/
├── Acidentario/
│   ├── Acidente-Transito/
│   └── Acidente-Domestico/
└── Familia/
    ├── Curatela/
    │   └── _historico-interdicao/   # referência histórica (Lei 13.146/2015)
    └── Guarda-Incapacidade/
```

## Banco-Transversal/

Conteúdo reutilizável entre Federal e Estadual.

```
Banco-Transversal/
├── Protocolos/            # ABMLPM, AMB, CFM, diretrizes clínicas
├── Quesitos/              # Unificados JF, TRFs, TST, TJs
├── Escalas/               # AVD, Barthel, VAS, Tinetti, Katz, etc
├── Jurisprudencia/        # Decisões indexadas por tema
├── Modelos-Laudo/         # Modelos por situação pericial
├── Contestacoes/          # Impugnações de laudo por tipo de ataque
├── Sentencas/             # Sentenças/acórdãos que citam laudos
├── Glossario/             # Termos técnicos médico-jurídicos
└── CID-Referencia/        # CID-10/CID-11 indexado para uso pericial
```

## Níveis abaixo de cada situação

Dentro de qualquer situação pericial (ex.: `Previdenciario/Auxilio-Acidente/`):

```
<Situacao>/
├── 00_Sumario.md              # resumo técnico da situação
├── 01_Modelo_de_Laudo.md      # modelo consolidado
├── 02_Checklist_Qualidade.md  # itens mínimos obrigatórios
├── 03_Quesitos_Tipicos.md     # quesitos unificados aplicáveis
├── 04_Protocolos.md           # protocolos médicos aplicáveis
├── 05_Escalas.md              # escalas e testes aplicáveis
├── casos/                     # laudos reais/anonimizados
├── contestacoes/              # impugnações recebidas neste tema
└── sentencas/                 # decisões envolvendo esse tema
```

## Temas clínicos transversais (indexação)

**AVISO — Temas clínicos são TAGS em `FICHA.json` (`temas_clinicos: []`). Não criar subpasta por tema.**

Tags aplicáveis a qualquer situação, para busca cruzada:

- Coluna (cervical/lombar/torácica)
- Ombro / Joelho / Quadril / Pé
- Cardio / Pneumo / Nefro
- Oncologia
- Neurologia (AVC, Parkinson, demências)
- Psiquiatria (transtornos de humor, ansiosos, TEPT, esquizofrenia)
- Oftalmo / ORL
- Doenças ocupacionais (LER/DORT, PAIR, pneumoconioses)

## Regras de colocação

- Conteúdo específico de uma situação federal/estadual → dentro da situação.
- Conteúdo reutilizável entre mais de uma situação → `Banco-Transversal/`.
- Dúvida → `Banco-Transversal/` e referenciar nas situações.

## OUT (fora de escopo)

- `Criminal/` — NÃO será criado em Federal nem em Estadual. Perícia criminal
  segue fluxo próprio e não entra neste banco.
- Subpastas por tema clínico — ver aviso acima. Tema clínico é tag, não pasta.
