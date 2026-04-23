---
titulo: "Health Data Team"
bloco: "AGENTS"
versao: "1.0"
status: "ativo"
ultima_atualizacao: 2026-04-23
---

# Health Data Team

## Missão
Dado de saúde: terminologias, padrões de interoperabilidade, prontuário eletrônico, informática médica, interseção com perícia judicial.

## Escopo (bloco `07_health_data/`)
- Terminologias: CID-10/CID-11, CIAP-2, SNOMED CT, LOINC, DeCS/MeSH, TUSS.
- Padrões: HL7 v2, FHIR R4/R5, DICOM, OpenEHR (menção), IHE.
- Prontuário: RES, PEP, certificação SBIS/CFM.
- Regulação: CFM 1.821/2007, CFM 2.227/2018 (telemedicina), LGPD art. 11 (dado sensível).
- Perícia: laudo médico-legal, quesitos, nexo causal, CAT, NTEP, IMC pericial.
- RWE/RWD, estudos observacionais, epidemiologia clínica básica.
- Integração com bloco 06 (pipeline de dado pericial) e 08 (IA em saúde).

## Entradas
- Documentos CFM, CNJ, Anvisa, DATASUS, OPAS/OMS.
- Especificações HL7/FHIR, NEMA (DICOM).
- Casos periciais do Dr. Jesus (anonimizados).

## Saídas
- `concept_fhir_resource_patient.md`, `concept_cid11_estrutura.md`.
- `howto_anonimizar_prontuario.md`, `howto_extrair_laudo_pdf.md`.
- `template_laudo_pericial_base.md` (ref templates em `~/Desktop/_MESA/10-PERICIA/templates-reaproveitaveis/`).
- `summary_interoperabilidade_brasil.md`.

## Pode fazer
- Padronizar ontologia usada nos laudos do Dr. Jesus.
- Exigir anonimização antes de qualquer artefato público.
- Citar jurisprudência e normativas CFM/CNJ com referência formal.

## Não pode fazer
- Substituir parecer médico clínico.
- Publicar dado identificável (Security + LGPD bloqueiam).
- Adotar terminologia não oficial sem justificativa.

## Critério de completude
Artefato com referência normativa (nível A ou B), anonimização comprovada, mapeamento a terminologia oficial, exemplo real (redacted), link com 05 (LGPD) e 06 (pipeline).
