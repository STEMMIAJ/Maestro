---
titulo: Integração Médico-Legal + TI/IA/Dados
bloco: 09_legal_medical_integration
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 09 — Legal Medical Integration

## Definição do domínio
Interseção entre perícia médico-judicial e tecnologia: automação documental, estruturação de dados periciais, apoio à decisão por IA, rastreabilidade processual, LGPD aplicada à perícia. Foco na prática real do perito: laudo, quesitos, intimações, processos, audiência.

## Subdomínios
- `pericia_judicial_and_data/` — modelos de dados do processo, CNJ, DataJud, classes/assuntos, movimentações
- `pericial_workflows/` — fluxos ponta-a-ponta (captação → exame → laudo → entrega)
- `ai_for_forensic_medical_work/` — LLMs, RAG, agentes, extração de evidência, confronto quesito↔laudo
- `document_automation/` — templates, placeholders, geração PDF/DOCX, assinatura digital CNJ
- `auditability_traceability/` — logs, hashes, versionamento, cadeia de custódia digital

## Perguntas que este bloco responde
- Como transformar um processo PJe/eproc em dados estruturados?
- Quais garantias técnicas um laudo automatizado precisa ter para não ser impugnado?
- Como usar IA sem violar sigilo médico nem a LGPD?
- Como rastrear cada afirmação do laudo até a fonte primária (exame, anamnese, norma)?
- Onde termina automação e começa ato pericial indelegável?

## Como coletar conteúdo
- Casos reais do Dexter (anonimizados)
- CNJ: Resoluções, DataJud, Atos Normativos sobre perícia
- CFM, CRM-MG: resoluções sobre telemedicina, prontuário, sigilo
- LGPD e ANPD: guias de dados sensíveis de saúde
- Literatura: artigos em medicina legal digital, forensic informatics
- Código e specs dos pipelines já existentes (STEMMIA Dexter)

## Critérios de qualidade
- Cada afirmação jurídica cita norma (Lei, Resolução CFM/CNJ, súmula)
- Cada afirmação médica cita diretriz ou literatura indexada
- Automação sempre marca o que é decisão humana vs sugestão de máquina
- Logs demonstram quem/quando/com-qual-versão

## Exemplos de artefatos
- Mapa do ciclo de vida de um processo pericial no Dexter
- Checklist de conformidade LGPD para pipeline pericial
- Taxonomia de "evidência" (documento, imagem, exame, testemunho)
- Diagrama de rastreabilidade quesito → trecho do laudo → fonte

## Interseções
- `05_security_and_governance` (LGPD, auditoria)
- `07_health_data` (padrões clínicos, FHIR, CID)
- `08_ai_and_automation` (LLM, RAG, agentes)
- `14_automation` (jobs OpenClaw, pipelines)
- `00_governance` (regras de qualidade, versionamento)
