---
titulo: "Prontuário eletrônico — PEP, CBHPM, TISS, TUSS, CIAP-2, CID"
bloco: "07_health_data/health_informatics"
tipo: "fundamento"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 9
---

# Prontuário eletrônico e terminologias brasileiras

PEP estrutura dado clínico; terminologias padronizam significado. Sem terminologia comum, não há interoperabilidade nem análise agregada.

## PEP — Prontuário Eletrônico do Paciente

- Define-se em **CFM 1.821/2007** como registro digital que substitui o papel.
- Requer: identificação inequívoca do paciente e do profissional, carimbo temporal, versionamento, assinatura digital, auditoria.
- **Certificação SBIS-CFM**: não é obrigatória, mas é o padrão-ouro.
  - **NGS1**: permite substituir papel para registros correntes.
  - **NGS2**: permite arquivar por tempo maior + descarte do papel.

### Estrutura mínima

- Identificação paciente (nome, CNS, CPF, data nasc., contato).
- Anamnese, exame físico, hipótese, conduta.
- Prescrições, solicitações de exame, encaminhamentos.
- Evoluções datadas.
- Exames (laudos, imagens via PACS).
- Consentimentos, termos.

## Terminologias e classificações — mapa rápido

| Sigla | Uso | Mantenedor |
|---|---|---|
| **CID-10** | Diagnóstico (morbi-mortalidade) | OMS / DATASUS |
| **CID-11** | Sucessor do CID-10, vigência BR em transição | OMS |
| **CIAP-2** | Atenção primária (motivo + problema + processo) | WONCA |
| **CBHPM** | Procedimentos médicos (suplementar) | AMB |
| **TUSS** | Tabela unificada saúde suplementar (procedimentos, insumos) | ANS |
| **TISS** | Padrão de troca saúde suplementar (mensagens) | ANS |
| **SIGTAP** | Procedimentos SUS | DATASUS |
| **CBO** | Classificação Brasileira de Ocupações | MTE |
| **CTI-BR** | Códigos insumos, materiais | - |
| **LOINC** | Exames laboratoriais (internacional) | Regenstrief |
| **SNOMED-CT** | Terminologia clínica global | SNOMED International |
| **CIAP-2 + CID** | Atenção primária brasileira (e-SUS APS) | MS |

## CID-10 vs CID-11

- **CID-10** (1993): capítulos I a XXII, códigos alfanuméricos (ex.: I21.9 = infarto do miocárdio agudo, não especificado).
- **CID-11** (vigente OMS desde 2022): estrutura linearizada, foundation ontológica, códigos novos. Brasil em transição, ainda **faturamento público usa CID-10**. `[TODO/RESEARCH: cronograma oficial de transição CID-11 no Brasil 2026]`.

## TISS — padrão de mensagens

- Padrão de **comunicação** entre operadoras e prestadores (XML/JSON).
- Versão atual: **TISS 4.01** (`[TODO/RESEARCH: confirmar versão vigente 2026]`).
- Guias: consulta, SP/SADT, internação, honorário, recurso de glosa.
- Integra: CBHPM/TUSS (procedimentos), CID-10 (diagnóstico), TNUMM (materiais), TNUME (medicamentos).

## CBHPM × TUSS

- **CBHPM** (Classificação Brasileira Hierarquizada de Procedimentos Médicos): criada pela AMB, referência de porte/valor para honorários.
- **TUSS**: padrão da ANS, obrigatório para faturamento suplementar. Códigos alinhados à CBHPM mas mantidos separadamente.
- Em auditoria pericial de honorários médicos: sempre conferir **código TUSS + porte CBHPM + tabela contratual**.

## CIAP-2

- Classificação para **atenção primária**.
- 17 capítulos por aparelho + eixo de processo (A = geral, K = cardio, L = osteomuscular, N = neuro, P = psicológica…).
- Estrutura do encontro: **motivo da consulta + problema + procedimento**.
- Base do e-SUS APS no SUS.

## RNDS — Rede Nacional de Dados em Saúde

- Plataforma nacional, **Portaria MS 1.434/2020**.
- Padrão base: **FHIR R4** com perfis brasileiros.
- Objetivo: interoperar PEP público e privado.
- Módulos ativos: vacinação COVID-19, laboratório, prescrição eletrônica, atenção primária (e-SUS APS).

## Implicações periciais

1. **Legibilidade e integridade** do PEP: versionamento, quem alterou, quando.
2. **Assinatura digital** ICP-Brasil (válida em juízo).
3. **Retenção**: 20 anos (CFM 1.821) ou conforme LGPD.
4. **Dados ausentes**: prontuário incompleto é falha de dever; registrar em laudo.
5. **Confronto TISS × guia clínico**: glosas indevidas quando procedimento não tem indicação ou código errado.

## Ferramentas para ler dado clínico

- **R**: `icd.data` (CID-10), `codelist` (TUSS).
- **Python**: `pysus` (DATASUS), `fhir.resources` (FHIR R4).
- **Base local**: tabelas SIGTAP, CBHPM, TUSS em CSV em pasta de referências.
