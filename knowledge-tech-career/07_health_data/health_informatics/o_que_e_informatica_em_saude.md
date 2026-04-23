---
titulo: "O que é informática em saúde — definição, SBIS, subáreas"
bloco: "07_health_data/health_informatics"
tipo: "fundamento"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 6
---

# O que é informática em saúde

Campo que aplica ciência da informação e computação à saúde: captura, armazenamento, processamento, comunicação e uso de dados biomédicos para decisão clínica, gestão e pesquisa.

## Definição operacional

- **AMIA** (American Medical Informatics Association): "uso de dados, informação e conhecimento para melhorar a saúde humana e a entrega de cuidados".
- **Não é** apenas "colocar computador no hospital". Envolve ontologias, padrões, cognição clínica, fluxo de trabalho.

## SBIS (Sociedade Brasileira de Informática em Saúde)

- Fundada em 1986.
- Publica **Manual de Certificação para Sistemas de Registro Eletrônico em Saúde (SBIS/CFM)** — referência nacional para PEP.
- Emite certificação SBIS-CFM em duas categorias (NGS1, NGS2) com requisitos de segurança, auditoria, assinatura digital.
- Organiza o CBIS (congresso brasileiro bienal).
- Site: sbis.org.br.

## Subáreas

### 1. Informática clínica (clinical informatics)

- Prontuário Eletrônico do Paciente (PEP/EHR).
- Sistemas de apoio à decisão clínica (CDSS).
- Prescrição eletrônica, bulas, alertas de interação medicamentosa.
- Integração de dispositivos (monitores, ventiladores, imagem).

### 2. Informática de enfermagem

- NANDA, NIC, NOC como vocabulários.
- Prescrição de enfermagem e registros estruturados.

### 3. Bioinformática

- Análise de sequências genômicas (DNA, RNA, proteínas).
- Ferramentas: BLAST, Bioconductor (R), Biopython.
- Liga-se a medicina de precisão, oncologia, farmacogenética.

### 4. Imagem médica / radioinformática

- PACS (Picture Archiving and Communication System), DICOM.
- Reconhecimento por IA (detecção, segmentação).

### 5. Saúde pública / informática populacional

- Vigilância epidemiológica (SIM, SINAN, SINASC).
- DATASUS, dashboards de indicadores.
- Geoprocessamento (QGIS + dados IBGE).

### 6. Informática translacional

- Integra prontuário + ômicas + registros para descoberta clínica.
- Ex.: identificar coortes para recrutamento em ensaios clínicos.

### 7. Telessaúde

- Teleconsulta, telelaudo, telemonitoramento.
- CFM: Resolução 2.314/2022 regulamenta telemedicina no Brasil.

### 8. Informática jurídica em saúde (área híbrida)

- Perícia digital em prontuários.
- Auditoria de glosas, análise de conformidade TISS.
- Aplicação direta para o perito que cruza PEP com DATAJUD.

## Conhecimentos-base do informaticista em saúde

- **Domínio clínico** (terminologias, fluxo assistencial).
- **Ciência da computação** (estruturas de dados, BD, redes).
- **Estatística / epidemiologia** básica.
- **Gestão de projeto** (PMBOK, ágil).
- **Privacidade e ética** (LGPD, CFM, Declaração de Helsinque).

## Marco regulatório brasileiro

- **LGPD (Lei 13.709/2018)**: dado de saúde = sensível; base legal própria para tratamento.
- **Portaria GM/MS 2.073/2011**: interoperabilidade no SUS.
- **Resolução CFM 1.821/2007**: diretrizes para PEP.
- **Portaria 1.434/2020**: RNDS (Rede Nacional de Dados em Saúde).
- **CFM 2.299/2021**: assinatura eletrônica no prontuário.

## Onde estudar

- AMIA: cursos 10×10 (online).
- SBIS: trilhas do CBIS.
- Livros: *Biomedical Informatics* (Shortliffe, Cimino); *Prontuário Eletrônico* (SBIS).
- Kaggle para prática com datasets públicos (MIMIC-III/IV).
