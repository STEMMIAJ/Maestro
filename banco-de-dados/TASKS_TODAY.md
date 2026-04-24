# TASKS_TODAY.md — Sessao de 2026-04-20 (CONSOLIDADA pos-wave-4)

## Estado atual

- Fase corrente: **3 — Coleta de laudos reais** — FECHADA (4 ondas)
- Ultima atualizacao: 2026-04-20 (pos-wave-4 + 3 indices transversais)
- Bloqueios: 6 situacoes permanecem sem caso disponivel (UFPR + tribunais esgotados)
- Trindade PDF+MD+FICHA em 100% dos 41 casos (auditoria automatica OK)

## Concluido hoje

### Infraestrutura
- Taxonomia consolidada (46 diretorios, 211 scaffolds)
- `INTEGRACAO-BANCO-GERAL.md` criado
- `MAPA-DE-FONTES.md` com contra-referencia
- 12 `.gitkeep` em situacoes ainda vazias (preservacao da taxonomia)

### Coleta de laudos (4 ondas)
- **Wave 1**: 18 casos (5 agents paralelos, UFPR+TJMG+Perspectivas)
- **Wave 2**: 12 casos (4 agents, UFPR temas nao cobertos)
- **Wave 3**: 9 novos + 1 duplicata detectada (3 agents, UFPR neuro/cardio/oftalmo)
- **Wave 4**: 6 novos casos (4 agents, tribunais federais TRF2/TRF4/CJF)
- **Revisoes teoricas**: 2 movidas para `Banco-Transversal/Doutrina/Capacidade-Civil/`

### Casos novos da wave 4
| Caso | Situacao | Fonte |
|---|---|---|
| alzheimer-grande-invalidez-tema275 | Federal/Previdenciario/Majoracao-25-Grande-Invalidez | CJF acordao |
| neoplasia-prostata-isencao-ir | Federal/Previdenciario/Isencao-IR-Doenca-Grave | TRF2/TRF4 |
| esquizofrenia-paranoide-reforma-militar (8/8) | Federal/Civel/Militar-Reforma-Invalidez | TRF4 |
| transtorno-bipolar-servidora-federal-ufsm | Federal/Civel/Servidor-Federal-Invalidez | TRF4 |
| lad-pos-acidente-homecare-operadora | Estadual/Civel/Seguro-Privado | TJ (Perspectivas) |
| insuficiencia-aortica-pericia-previdenciaria-crianca | Federal/Previdenciario/APIP | UFPR |

### Download + conversao de arquivos-fonte
- 22 PDFs UFPR-EPM baixados direto
- 1 PDF TJMG direto + 4 PDFs de acordaos TRF2/TRF4/CJF
- 8 HTMLs convertidos para PDF via Chrome headless
- HTMLs originais arquivados em `_arquivo_htmls_convertidos/`
- **Resultado**: TODOS os 41 casos tem PDF (usuario prefere PDF para leitura)

### Dedupe + normalizacao
- 3 grupos de duplicatas movidos para `_duplicados/` (preservam historico)
- 1 duplicata cross-agent detectada (FELIPE-SABBAG) e resolvida
- 10 `.json` simples renomeados para `.FICHA.json`
- 2 FICHA.json orfaos movidos para `_orfaos/`
- PDFs 0-byte de cupsfilter movidos para `_orfaos_pdf_vazios/`

### Indices transversais (Banco-Transversal/)
- `INDICE-CASOS.md` — 333 linhas, 7 secoes (resumo, tabela mestre, CID, tema, situacao, score, CNJ)
- `INDICE-CIDS.md` — 316 linhas, 60 CIDs unicos cruzados com situacao + casos
- `QUESITOS-EXTRAIDOS.md` — 181 linhas, 24 quesitos, 5 modelares, 6 padroes de vicio

## Estado consolidado do banco

### Totais
| Metrica | Valor |
|---|---|
| Casos unicos | **41** |
| PDFs (trindade completa) | 41 |
| FICHAs (1:1 com MD) | 41 |
| Revisoes doutrinarias em `Banco-Transversal/Doutrina/` | 2 |
| Situacoes cobertas | **20** / 27 |
| CIDs unicos indexados | 60+ |
| Scores >= 7/8 | 13+ casos |
| Casos com CNJ publico | 9 individuais + 1 agregado |
| Indices transversais | 3 (casos, CIDs, quesitos) |

### Distribuicao final por ramo

**Federal (26 casos, +4 da wave 4):**
- Trabalhista/Acidente-Trabalho: 2
- Trabalhista/Doenca-Ocupacional: 6
- Trabalhista/Insalubridade-Periculosidade: 1
- Previdenciario/BPC-LOAS: 4
- Previdenciario/Auxilio-Incapacidade-Temporaria: 2
- Previdenciario/APIP: 5 (+1 wave 4: insuficiencia aortica pediatrica)
- Previdenciario/Pensao-Morte-Invalidez-Dependente: 1
- Previdenciario/Auxilio-Acidente: 1
- Previdenciario/Revisional-Incapacidade: 1
- Previdenciario/Isencao-IR-Doenca-Grave: 1 (NOVO wave 4)
- Previdenciario/Majoracao-25-Grande-Invalidez: 1 (NOVO wave 4)
- Civel/Militar-Reforma-Invalidez: 1 (NOVO wave 4)
- Civel/Servidor-Federal-Invalidez: 1 (NOVO wave 4)

**Estadual (14 casos, +1 wave 4):**
- Civel/Erro-Medico: 5
- Civel/Dano-Moral-Estetico: 1
- Civel/DPVAT: 1
- Civel/Responsabilidade-Civil-Medica: 1
- Civel/Plano-Saude: 1
- Civel/Seguro-Privado: 1 (NOVO wave 4)
- Familia/Curatela: 3 (+ 2 revisoes em Doutrina)

### Fontes consolidadas
- UFPR-EPM (TCC especializacao): 26 casos
- TJMG (acordaos publicos): 4 casos
- TRF2/TRF4/CJF (acordaos federais): 4 casos (novos wave 4)
- Perspectivas ABMLPM: 6 casos
- MP-SC (parecer administrativo): 1 caso

## Alta prioridade (proxima sessao) — max 5

- [ ] Popular 7 situacoes AINDA vazias (busca esgotada nas fontes atuais):
  - Estadual/Acidentario/Acidente-Domestico
  - Estadual/Acidentario/Acidente-Transito
  - Estadual/Civel/Servidor-Estadual-Invalidez
  - Estadual/Familia/Guarda-Incapacidade
  - Federal/Civel/DPVAT
  - Federal/Civel/Responsabilidade-Civil-Medica
  - Federal/Trabalhista/Nexo-Tecnico-Epidemiologico-NTEP
- [ ] Quinta onda: UnB-EPM, UERJ-PEPM, UEL-ICS, BDTD, Lume/UFRGS (ou anonimizar casos proprios)
- [ ] Iniciar Fase 4: contestacoes e padroes de ataque (PJe + Escavador)
- [ ] Iniciar Fase 5: modelos derivados (ja tem >= 2 casos em 7 situacoes)
- [ ] Converter PDFs em TXT para busca full-text (pdftotext)

## Se sobrar energia — max 5

- [ ] Gerar dashboard HTML visual do banco
- [ ] Extrair quesitos dos 30 laudos sem secao formal (pdftotext + regex)
- [ ] Buscar caso criminal Perspectivas ABMLPM (imputabilidade)
- [ ] Criar INDICE-SCORES.md (ranking qualidade por caso)
- [ ] Criar INDICE-FONTES.md (rastreamento origem)

## Nao fazer hoje

- Automacao de ingestao (fase 6 — depois de banco ter massa critica >= 50 casos)
- Apagar `_duplicados/`, `_orfaos/`, `_arquivo_*` (preservam historico)
- Popular scaffolds teoricos (protocolos, quesitos) sem caso concreto de base

## Estrutura trindade por caso (regra consolidada)

Cada caso DEVE ter 3 arquivos com mesmo name-base:
```
<slug>.pdf              (fonte original, prioridade max para leitura)
<slug>.md               (analise estruturada + checklist 8 pontos)
<slug>.FICHA.json       (metadados para indexacao)
```

Auditoria rapida:
```bash
cd banco-de-dados
find . -name "*.md" -not -path "*_duplicados*" -not -path "*_orfaos*" \
  -not -path "*_arquivo*" -not -path "*Doutrina*" -path "*/casos/*" | while read md; do
  base="${md%.md}"
  [ -f "${base}.pdf" ] && [ -f "${base}.FICHA.json" ] && echo OK || echo FALTA: ${md#./}
done
```

Resultado 2026-04-20: 41 OK / 0 FALTA.

## Duplicatas preservadas (historico)

1. `Federal/Trabalhista/Acidente-Trabalho/casos/_duplicados/` — 1 arquivo (Julianna CNJ-longo)
2. `Federal/Trabalhista/Acidente-Trabalho/casos/_anonimizados/_duplicados/` — 2 arquivos (Julianna anonimizada)
3. `Estadual/Familia/Curatela/casos/_anonimizados/_duplicados/` — 2 arquivos (Palhares generico)
4. `Federal/Trabalhista/Doenca-Ocupacional/casos/_anonimizados/_duplicados/` — 3 arquivos (Felipe-Sabbag mesmo caso em APIP)

## Orfaos preservados

1. `Federal/Trabalhista/Acidente-Trabalho/casos/_orfaos/FICHA.json`
2. `Estadual/Familia/Curatela/casos/_anonimizados/_orfaos/FICHA.json`

## Arquivos fonte secundarios

- `_orfaos_pdf_vazios/` — 8 PDFs 0-byte de cupsfilter (antes da migracao p/ Chrome headless)
- `_arquivo_htmls_convertidos/` — 8 HTMLs originais das fontes HTML (ja convertidos em PDF)

## Falta (mapeamento para tarefas relacionadas)

### Populacao do banco (Fase 3 — 4 ondas concluidas, 5a pendente)
- 7 situacoes vazias (fontes UFPR/TJ/TRF esgotadas para esses temas)
- Proximas fontes: UnB-EPM, UERJ-PEPM, UEL-ICS, BDTD, Lume/UFRGS
- Alternativa: anonimizar casos proprios do usuario (requer autorizacao + LGPD)

### Indexacao (Banco-Transversal) — 3/5 concluidos
- [X] INDICE-CASOS.md
- [X] INDICE-CIDS.md
- [X] QUESITOS-EXTRAIDOS.md
- [ ] INDICE-SCORES.md
- [ ] INDICE-FONTES.md

### Fase 4 — Contestacoes
- Nao iniciada. Requer coletar peticoes iniciais + impugnacoes + quesitos das partes
- Fonte provavel: PJe (ja baixa) + Escavador + Projudi

### Fase 5 — Modelos derivados por situacao
- Nao iniciada. Ja ha >= 2 casos em 7 situacoes (base suficiente para iniciar)
- Situacoes com massa critica: Erro-Medico (5), Doenca-Ocupacional (6), BPC-LOAS (4),
  APIP (5), Curatela (3), Aux-Incap-Temporaria (2), Acidente-Trabalho (2)

### Fase 6 — Automacao
- Nao iniciada. So apos banco ter massa critica (sugerido minimo 50 casos — faltam 9)

## Wave 5A — TJMG jurisprudencia estadual (2026-04-20)

Nova fonte explorada: acordaos publicos TJMG com transcricao literal/parcial de laudos.

### Casos novos wave 5A
| Caso | Situacao | Fonte | Score | Classif |
|---|---|---|---|---|
| tjmg-1020514001717-moto-vs-caminhonete-encurtamento-mi | Estadual/Acidentario/Acidente-Transito | TJMG 15a Camara Civel | 3/8 + 3 parciais | REAL_COM_CNJ |
| tjmg-1000022054232-professor-transtorno-esquizoafetivo-f25 | Estadual/Civel/Servidor-Estadual-Invalidez | TJMG 2a Camara Civel | 5/8 + 3 parciais | REAL_COM_CNJ |

### Situacoes ainda INDISPONIVEIS (wave 5A)
- **Estadual/Acidentario/Acidente-Domestico** — 30min de busca (BDTD, UFPR, TJMG) sem retorno. Casos de queda/queimadura domesticos encontrados sao em sua maioria: (a) acidentes de trabalho domesticos em cuidadores (foro trabalhista, nao estadual), (b) casos de vizinhanca/condominio (responsabilidade civil, mas sem laudo medico individual), (c) casos de choque eletrico em rede publica (foro consumidor). Recomendacao: prosseguir para Wave 5B com BDTD direto + USP teses + Lume UFRGS ou aceitar que acidente domestico puro sem envolvimento trabalhista e raro na literatura pericial publicada.

