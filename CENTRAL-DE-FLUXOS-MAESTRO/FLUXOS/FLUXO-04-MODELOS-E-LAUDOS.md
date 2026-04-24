# FLUXO 04 — Modelos e laudos

## Objetivo duplo

1. **Construir modelos** — encontrar laudos reais, laudos elogiados por juízes, sentenças que citam bons laudos (especialmente em Governador Valadares e comarcas próximas). Extrair o que eles têm em comum. Montar templates reaproveitáveis por tipo de perícia.
2. **Gerar laudo novo** — a partir de FICHA.json + notas do exame + quesitos, produzir LAUDO.md + PDF timbrado.

## Estrutura canônica do laudo (6 seções)

1. **Preâmbulo** — identificação do perito, processo, partes, data da nomeação e da perícia.
2. **Histórico** — anamnese, história da doença.
3. **Exame físico / complementares** — achados objetivos + documentos médicos periciados.
4. **Discussão / fundamentação** — correlação clínica, nexo, literatura.
5. **Conclusão** — CID definitivo, capacidade/incapacidade, grau, DII e DID.
6. **Resposta aos quesitos** — quesito literal + resposta objetiva, por origem (juízo/autor/réu).

Documentado em `cowork/04-PIPELINES/pipeline-geracao-laudo.md`.

## Templates reaproveitáveis existentes

### Formato de laudo (estrutura completa)
| Caminho | Tipo de perícia | Status |
|---|---|---|
| `/Users/jesus/Desktop/_MESA/10-PERICIA/templates-reaproveitaveis/formatos-laudo/acidente-trabalho.md` | Acidente de trabalho | PRONTO |
| `/Users/jesus/Desktop/_MESA/10-PERICIA/templates-reaproveitaveis/formatos-laudo/securitario-invalidez.md` | Securitário (invalidez) | PRONTO |

**Outros tipos (previdenciário, erro-médico, trabalhista, cível dano pessoal, psiquiátrico): FALTAM.**

### Blocos reaproveitáveis (exame físico por região)
| Caminho | Região |
|---|---|
| `/Users/jesus/Desktop/_MESA/10-PERICIA/templates-reaproveitaveis/exames-fisicos/coluna-lombar.md` | Coluna lombar |
| `/Users/jesus/Desktop/_MESA/10-PERICIA/templates-reaproveitaveis/exames-fisicos/joelho.md` | Joelho |

(Outros — ombro, cervical, quadril, psiquiátrico, cardíaco — faltam.)

### Índice
| Caminho | O que é |
|---|---|
| `/Users/jesus/Desktop/_MESA/10-PERICIA/templates-reaproveitaveis/INDEX.md` | Catálogo dos templates disponíveis |

### Biblioteca cowork (ainda vazia)
| Caminho | Estado |
|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/cowork/02-BIBLIOTECA/laudos/` | Só symlinks + README. **Sem templates próprios.** |

## SCRIPTS EXISTENTES

| Caminho | O que faz | Status |
|---|---|---|
| `/Users/jesus/Desktop/STEMMIA Dexter/cowork/05-AUTOMACOES/scripts/aplicar_template.py` | **Motor oficial.** Lê TEMPLATE.md + FICHA.json, substitui `{{placeholders}}` e blocos `{{#lista:}}` / `{{#se:}}`. stdlib only | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/src/peticoes/laudo_pipeline.py` | Pipeline laudo FICHA → laudo.md | DUVIDOSO (tem cópia legado) |
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/clusters/geral/redator-laudo.md` | Agente redator | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/clusters/geral/revisor-laudo.md` | Agente revisor | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/clusters/redacao/gerador-roteiro-pericial.md` | Gera roteiro HTML para exame presencial | FUNCIONA |
| `/Users/jesus/Desktop/STEMMIA Dexter/agents/clusters/redacao/padronizador-estilo.md` | Agente padronizador (consulta PERFIL-ESTILO) | PARCIAL (PERFIL-ESTILO.json não está local) |

## Checklist de etapas futuras (coleta de laudos reais)

1. **Coletar laudos** — a partir do fluxo 06 (jurisprudência e sentenças), filtrar decisões que tenham laudo anexado ou citado.
2. **Filtrar laudos elogiados** — buscar nas sentenças termos como "laudo bem fundamentado", "perícia minuciosa", "quesitos exaustivamente respondidos", "conclusão clara".
3. **Extrair características comuns** — estrutura (quantas páginas média, quantas seções), linguagem (formal/técnica/mista), citação de literatura (sim/não, quantas fontes), DII/DID explicitadas.
4. **Gerar modelo-base por tipo** — 1 template novo por classe faltante (previdenciário, erro-médico, trabalhista, cível dano pessoal, psiquiátrico).
5. **Validar modelo com 1 caso real** antes de virar template oficial.
6. **Plugar PERFIL-ESTILO.json** — copiar iCloud → local → agente padronizador → laudo gerado fica com "voz" do Dr. Jesus.

## Saída esperada

```
laudo/
├── LAUDO-YYYY-MM-DD.md      # texto estruturado
├── LAUDO-YYYY-MM-DD.pdf     # timbrado
└── .tmp/
    ├── contexto-laudo.json  # FICHA + notas + quesitos
    ├── LAUDO-draft.md       # draft antes da revisão
    └── revisao.json         # lista de achados do revisor
```

## O que trava hoje

1. **Só 2 formatos de laudo prontos** (AT + securitário). Faltam 4-5 tipos.
2. **PERFIL-ESTILO.json não está local** — agente padronizador roda sem ele.
3. **Laudos elogiados não foram coletados ainda** — depende de fluxo 06 funcionando.
4. **laudo_pipeline.py tem 2 cópias** — decidir qual é a oficial.
