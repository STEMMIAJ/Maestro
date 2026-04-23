---
titulo: "Taxonomia do Conhecimento"
bloco: "00_governance"
versao: "1.0"
status: "ativo"
ultima_atualizacao: 2026-04-23
---

# Taxonomia

## Hierarquia
```
dominio (bloco XX)
  └── subdominio
        └── topico
              └── artefato (arquivo .md)
```

## Domínios (blocos)
| Cód | Domínio | Time responsável |
|-----|---------|------------------|
| 01 | TI Foundations | TI-FOUNDATIONS-TEAM |
| 02 | Programming | SOFTWARE-ENGINEERING-TEAM |
| 03 | Web Development | WEB-DEVELOPMENT-TEAM |
| 04 | Systems Architecture | SYSTEMS-ARCHITECTURE-TEAM |
| 05 | Security & Governance | SECURITY-TEAM |
| 06 | Data Analytics | DATA-ANALYTICS-TEAM |
| 07 | Health Data | HEALTH-DATA-TEAM |
| 08 | AI & Automation | AI-SYSTEMS-TEAM |
| 10 | Career Map | CAREER-MAPPING-TEAM |
| 11 | Personal Skills | SKILLS-ASSESSMENT-TEAM |
| 12 | Sources | SOURCES-CURATION-TEAM |
| 14 | Automation Jobs | MAESTRO-INTEGRATION-TEAM |

## Subdomínios (exemplos)
- 01 → `so_linux`, `redes`, `git`, `shell`, `matematica_aplicada`.
- 02 → `python`, `typescript`, `go`, `sql`, `dsa`, `testes`, `engenharia`.
- 03 → `frontend`, `backend`, `api`, `deploy`, `acessibilidade`.
- 04 → `containers`, `bancos`, `mensageria`, `observabilidade`, `padroes`.
- 05 → `appsec`, `infrasec`, `cripto`, `lgpd`, `pericia_compliance`.
- 06 → `modelagem`, `sql_avancado`, `etl`, `visualizacao`, `estatistica`.
- 07 → `terminologias`, `fhir_hl7`, `dicom`, `prontuario`, `pericia_medica`.
- 08 → `ml_classico`, `deep_learning`, `llm`, `rag`, `agentes`, `avaliacao`.
- 10 → `trilhas`, `mercado_br`, `certificacoes`, `transicoes`.
- 11 → `inventario_tecnico`, `metacognicao`, `evolucao`.
- 12 → `livros`, `papers`, `docs_oficiais`, `cursos`, `roadmaps`.
- 14 → `jobs_recorrentes`, `hooks`, `integracoes_n8n`.

## Tópicos
Granularidade ~1 arquivo por tópico. Tópico excessivamente grande → dividir.

## Tipos de artefato
| Tipo | Propósito | Formato mínimo |
|------|-----------|----------------|
| `concept` | Definição rigorosa, modelo mental | definição, exemplos, contraexemplos, fontes |
| `howto` | Procedimento verificado passo a passo | pré-requisitos, passos testados, validação, rollback |
| `checklist` | Lista acionável binária | itens objetivos, critério de aprovação |
| `template` | Boilerplate pronto | placeholders documentados, exemplo preenchido |
| `summary` | Síntese periódica | escopo temporal, pontos-chave, ações |
| `report` | Relatório datado com métricas | metodologia, dados, conclusão, limitações |
| `source` | Ficha de fonte | metadados completos, nível de evidência |
| `spec` | Especificação formal | contratos, invariantes, casos de falha |
| `job` | Job Maestro/OpenClaw | gatilho, entrada, saída, SLA |

## Tags transversais
Aplicam-se através de blocos. Ex.: `pericia`, `lgpd`, `performance`, `neurodivergencia`, `economia_token`, `backup`, `datajud`, `pje`. Listar em `12_sources/tags_index.md`.

## Referência cruzada
Todo artefato deve citar ao menos 1 consumidor potencial (bloco que o usa) quando aplicável. Orquestração via Orchestrator evita órfãos.

## Ciclo do artefato
`rascunho` → revisão cruzada → `ativo` → (opcional) `depreciado` → arquivamento em `99_attic/` (nunca deletar).
