---
titulo: "Papéis na Interseção Saúde, Dados e Perícia"
bloco: "10_career_map"
tipo: "referencia"
nivel: "junior-pleno"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 8
---

# Papéis em Saúde, Dados e Perícia

Nicho pequeno, alta barreira de entrada (exige domínio clínico + técnico), baixa competição. Para médico que aprende tech, vantagem competitiva real.

## 1. Bioestatístico

Profissional que aplica estatística a dados biomédicos.

- Formação típica: estatística, matemática, ou médico/biólogo com pós em bioestatística.
- Contexto: pesquisa clínica, ensaios randomizados, epidemiologia, saúde pública.
- Ferramentas: R (padrão), SAS, Stata, Python (pandas, statsmodels).
- Produto: análise de desfecho, modelo de sobrevida, metanálise.

Médico perito tem ponte: epidemiologia + análise de desfecho são usados em laudos de nexo causal.

## 2. Cientista de Dados Clínico (Clinical Data Scientist)

Aplica ML a dados de saúde.

- Formação: ciência da computação + domínio clínico, ou médico + reskill.
- Contexto: hospital, healthtech, farmacêutica, academia.
- Ferramentas: Python, SQL, FHIR, OMOP CDM, PyTorch.
- Produto: modelo de triagem, predição de readmissão, imagem médica, NLP de prontuário.

Nicho crescente em healthtechs brasileiras. Requer entender privacidade (LGPD art. 11) + FDA/CE marking para dispositivos.

## 3. Health Informatics Specialist (Informaticista em Saúde)

Arquitetura de sistemas de saúde.

- Contexto: HIS, EHR, interoperabilidade.
- Padrões: HL7, FHIR, SNOMED CT, LOINC, ICD-10, TUSS, TISS.
- Certificações: CAHIMS, CPHIMS (HIMSS).
- Produto: integração entre sistemas, dicionário de dados, terminologia clínica.

No Brasil: papel ainda subdimensionado. Demanda crescerá com Meu Prontuário Eletrônico (CONEP/CNS) e RNDS (Rede Nacional de Dados em Saúde).

## 4. Perito-Tech / Perito Digital Forense

Dois subtipos relevantes:

### 4.1. Perito forense digital

- Prova digital: discos, memória, nuvem, celular.
- Certificações: CCE, EnCE, GCFA, CFCE.
- Ferramentas: EnCase, FTK, Autopsy, Volatility, X-Ways.
- Produto: laudo técnico em processos cível/criminal/corporativo.

### 4.2. Perito médico com automação técnica (caso Dr. Jesus)

Médico nomeado judicialmente que usa pipelines próprios para:

- Análise de grande volume documental (laudos com centenas de páginas).
- Busca em jurisprudência via API (DataJud, Jusbrasil).
- Transcrição/sumarização de anamnese com IA local.
- Base própria de perícias reaproveitáveis.

Papel híbrido raro no Brasil. Valor agregado: entregar laudo mais rápido, mais fundamentado, com menor custo cognitivo.

## 5. Real-World Evidence (RWE) Analyst

Análise de dados de mundo real (fora de ensaio clínico).

- Fonte: claims, prontuário, registros, wearables.
- Uso: farmacovigilância, farmacoeconomia, HTA.
- Ferramentas: SAS, R, Python, OMOP.
- Cliente: farmacêutica, ANS, ANVISA.

## 6. Epidemiologist Data Engineer

Epidemiologista que constrói/mantém pipelines de vigilância.

- Contexto: Ministério da Saúde, SMS, centros acadêmicos, bigtech.
- Ferramentas: Python, SQL, Airflow, PostGIS para espacial.
- Produto: dashboards de vigilância (dengue, COVID, arbovírus).

## 7. Engenheiro de Prompt Clínico / AI Safety em Saúde

Emergente. Constrói e avalia prompts para LLMs em contexto médico.

- Atividade: criar evals clínicas, detectar alucinação, red team de LLM.
- Demanda: healthtechs com copilot clínico, hospitais com assistente LLM.

## 8. Consultor em Privacidade Médica (DPO clínico)

DPO especializado em saúde.

- Formação: direito ou medicina + curso DPO (IAPP, ENCE).
- Atividade: RIPD para hospital, treinamento, auditoria, resposta a incidente.
- Demanda: crescente após multas ANPD em saúde.

## Síntese — afinidade para Dr. Jesus

| Papel | Afinidade | Custo de transição |
|-------|-----------|-------------------|
| Perito médico com automação (atual) | já exerce | zero |
| Consultor DPO clínico | alta | médio — certificação + portfólio |
| Real-World Evidence Analyst | média-alta | médio — aprender R e estudos observacionais |
| Clinical Data Scientist | média | alto — ML aplicado |
| Health Informaticist | média | médio — padrões técnicos |
| Perito forense digital | média | alto — reskill técnico + certificação |

## Referência cruzada

- `familias_profissionais_detalhadas.md`
- `../learning_paths/trilha_medico_para_tech.md`
- `../certifications/mapa_certificacoes_por_trilha.md`
