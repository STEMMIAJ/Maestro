---
titulo: "Convenções de Nomenclatura"
bloco: "00_governance"
versao: "1.0"
status: "ativo"
ultima_atualizacao: 2026-04-23
---

# Convenções de Nomenclatura

## Regra geral
- Caminhos e nomes de arquivo: **ASCII puro**, `snake_case`, **sem acento, sem cedilha, sem espaço, sem maiúscula** (exceção: pastas `AGENTS/` de governança).
- Conteúdo interno do Markdown: **português com acentuação correta**.

## Estrutura de blocos
Prefixo numérico de dois dígitos para ordenar blocos de topo:
- `00_governance/`, `01_ti_foundations/`, `02_programming/`, `03_web_development/`, `04_systems_architecture/`, `05_security_and_governance/`, `06_data_analytics/`, `07_health_data/`, `08_ai_and_automation/`, `10_career_map/`, `11_personal_skill_mapping/`, `12_sources/`, `14_automation/`.
- Gaps numéricos (09, 13) reservados para expansão sem renumeração.

## Nome de arquivo
Formato: `<tipo>_<slug>.md`

Sufixos/prefixos de tipo (obrigatório):
- `concept_*` — definição, teoria, modelo.
- `howto_*` — procedimento verificado.
- `checklist_*` — lista acionável.
- `template_*` — boilerplate pronto para uso.
- `summary_*` — síntese periódica.
- `report_*` — relatório datado.
- `source_*` — ficha de fonte em `12_sources/`.
- `*_spec.md` — especificação técnica.
- `*_job.md` / `*_job.yaml` — job OpenClaw.

Exemplos:
- `concept_idempotencia.md`
- `howto_postgres_backup.md`
- `template_laudo_pericial_base.md`
- `summary_trilha_health_data.md`
- `report_mercado_br_ti_ia_2026_q2.md`
- `source_kleppmann_ddia.md`
- `indexador_python_base_job.md`

## Slug
- Minúsculo, `snake_case`, ASCII.
- Máximo 60 caracteres.
- Substituir caracteres acentuados (á→a, ç→c, ã→a, etc.).
- Sem stopwords desnecessárias (`de`, `da`, `do`, `e`) exceto quando indispensável.

## Frontmatter YAML (obrigatório em todo `.md`)
```yaml
---
titulo: "Título humano com acentuação correta"
bloco: "<nome_do_bloco>"
tipo: "concept|howto|checklist|template|summary|report|source|spec|job"
versao: "x.y"
status: "rascunho|ativo|depreciado"
nivel_evidencia: "A|B|C|D|E|F"
tags: ["tag1", "tag2"]
fontes: ["source_xxx.md"]
autor_time: "NOME-TEAM"
ultima_atualizacao: AAAA-MM-DD
proxima_revisao: AAAA-MM-DD
---
```

## Pastas
- Sempre `snake_case`. Ex.: `openclaw_jobs/`, não `OpenclawJobs/`.
- Evitar aninhamento maior que 4 níveis dentro do bloco.

## Versionamento de artefato
SemVer adaptado: `major.minor`. Incremento `major` quando quebra de conceito; `minor` quando complemento.

## Links internos
Relativos: `[texto](../02_programming/concept_big_o.md)`. Nunca absolutos no repositório.

## Proibições
- Acento, espaço, cedilha, maiúscula aleatória em nome de arquivo/pasta.
- `readme.md` em minúscula (usar `README.md` apenas na raiz).
- Arquivo sem frontmatter.
- Alteração retroativa de slug sem redirect/changelog.
