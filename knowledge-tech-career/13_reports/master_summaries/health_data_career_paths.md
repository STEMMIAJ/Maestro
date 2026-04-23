---
titulo: Trilhas Saúde + Dados + IA
tipo: master_summary
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
---

# Trilhas que combinam Medicina + TI / Dados / IA

## Premissa

Médico que aprende TI do zero compete com dev de 22 anos em dev genérico, e perde em velocidade bruta. Mas em **interseção** (saúde + dado / IA / automação / compliance), o diferencial é a própria formação clínica. O caminho de menor resistência é entrar pela interseção.

Este documento lista 7 trilhas, cada uma com: descrição, pré-requisitos, mercado, empregadores típicos, como começar a partir do perfil atual (médico perito + Dexter + Python + Claude Code).

---

## 1. Informática médica (Medical Informatics)

- **Descrição:** disciplina formal que estuda uso de informação/tecnologia em saúde. Inclui prontuário eletrônico, interoperabilidade (HL7/FHIR), ontologias (SNOMED, CID), terminologia, UX clínico.
- **Pré-requisitos:** formação médica (já tem), noção de banco de dados, inglês técnico.
- **Mercado BR:** nichado mas crescente; SBIS (Sociedade Brasileira de Informática em Saúde) organiza a área. [TODO/RESEARCH: títulos e cursos 2026]
- **Empregadores típicos:** hospitais grandes (Einstein, Sírio, Moinhos), operadoras, govtech de saúde, fornecedores de prontuário (MV, Tasy/Philips, Soul MV).
- **Como começar:** ler livro base (Shortliffe — Biomedical Informatics), estudar FHIR, participar SBIS, conectar Dexter a API FHIR pública de teste.

## 2. Bioinformática

- **Descrição:** aplicar computação a dado biológico — genoma, proteoma, imagem microscópica.
- **Pré-requisitos:** biologia molecular sólida, Python/R, estatística, paciência com pipeline.
- **Mercado BR:** concentrado em pesquisa acadêmica (USP, Fiocruz, LNCC) e poucas empresas (Mendelics, DASA/Genomika).
- **Empregadores:** laboratórios de pesquisa, startups de diagnóstico genético, farma.
- **Como começar:** baixa aderência ao perfil pericial atual. Requer reaprender biologia molecular. **Trilha não recomendada como primeira.**

## 3. Data science em saúde

- **Descrição:** usar estatística/ML sobre dado clínico, epidemiológico, administrativo (faturamento, autorização, sinistro).
- **Pré-requisitos:** Python + pandas + scikit-learn, SQL, estatística inferencial, entendimento de desfecho clínico.
- **Mercado BR:** operadoras de saúde (Hapvida/NotreDame, Bradesco, SulAmérica), healthtechs, consultorias (Accenture Health, IQVIA).
- **Empregadores:** operadoras, hospitais de rede, healthtechs, farma (fase IV).
- **Como começar:** Google Data Analytics ou DataCamp track → projeto público: análise de base pública DATASUS (SIH, SIA, SIM) com Python, publicar no GitHub.

## 4. Real World Evidence (RWE) / farmacoepidemiologia

- **Descrição:** gerar evidência a partir de dado do mundo real (prontuário, sinistro, registro) para pergunta regulatória, de eficácia, ou de segurança.
- **Pré-requisitos:** epidemiologia, estatística (causal inference), SQL/Python, domínio de fonte de dado (DATASUS, SUS, prontuário).
- **Mercado BR:** farma (MSD, Pfizer, Roche, Novartis), CRO (IQVIA, Parexel), academia aplicada.
- **Empregadores:** farma global, CRO, consultoria health-economics, agências regulatórias.
- **Como começar:** curso de farmacoepi (FIOCRUZ EAD tem opções [TODO/RESEARCH]), replicar paper de RWE em base pública, publicar código.

## 5. Auditoria de laudos / perícia automatizada

- **Descrição:** revisar laudos em escala (operadora, judicial, seguradora) usando regra + ML + LLM.
- **Pré-requisitos:** domínio médico-pericial (já tem), Python, LLM/RAG, engenharia de prompt, LGPD.
- **Mercado BR:** operadoras de saúde (glosa), seguradoras (sinistro), escritórios de advocacia massivos (previdenciário), tribunais.
- **Empregadores:** Hapvida, Unimeds grandes, Porto Seguro/SulAmérica vida, escritórios top-50 previdência, TRFs (menos provável, via convênio).
- **Como começar:** o Dexter já é protótipo disto. Formalizar como produto/consultoria, publicar 1 caso anonimizado, montar landing page técnica.

## 6. Automação pericial (RPA + IA jurídica)

- **Descrição:** automatizar ciclo pericial — captação via DJEN/PJe, produção de laudo, entrega assinada, controle de prazo.
- **Pré-requisitos:** domínio do processo pericial (já tem), Python, Selenium/Playwright, APIs CNJ (DataJud, Comunica, DJEN), assinatura digital.
- **Mercado BR:** peritos autônomos, câmaras periciais, escritórios previdenciários. Nicho de consultoria B2B pequeno mas com pagamento bom.
- **Empregadores:** trabalhar como autônomo/CNPJ vendendo o sistema; parceria com legaltechs.
- **Como começar:** trilha em execução. Falta empacotar Dexter como produto replicável, criar documentação de onboarding, definir pricing.

## 7. Apoio à decisão clínica (CDSS)

- **Descrição:** sistema que sugere conduta, alerta interação, triagem, cálculo de risco. Inclui produtos tipo UpToDate, calculadoras, triadores de IA.
- **Pré-requisitos:** medicina + engenharia de software + regulação (ANVISA SaMD, FDA 510k) + evidência clínica.
- **Mercado BR:** healthtechs (Memed, Beep Saúde), operadoras, hospitais com P&D, indústria de software médico.
- **Empregadores:** healthtechs, prontuários, ou empresa própria.
- **Como começar:** começar por subdomínio pericial (onde já há domínio). Construir calculadora de grau de incapacidade com base em tabela, evoluir.

---

## Matriz de decisão para o perfil atual

| Trilha | Aderência | Custo entrada | Mercado BR | Já tem base? |
|---|---|---|---|---|
| Automação pericial | Máxima | Baixo (em curso) | Nicho, pagamento bom | Sim |
| Auditoria de laudos | Alta | Baixo-médio | Grande (operadoras) | Sim (Dexter) |
| Informática médica | Alta | Médio (estudo formal) | Médio, institucional | Parcial |
| Data science saúde | Alta | Médio (estatística + Python) | Grande | Parcial |
| RWE / farmacoepi | Média-alta | Alto (epi formal) | Médio (farma) | Parcial |
| CDSS | Média | Alto (regulatório) | Pequeno BR, grande global | Parcial |
| Bioinformática | Baixa | Altíssimo | Pequeno BR | Não |

## Ordem sugerida (12-24 meses)

1. Consolidar automação pericial como produto (trilha 6) — monetiza cedo.
2. Paralelo: Google Data Analytics + DATASUS (trilha 3) — base formal.
3. Avançar auditoria de laudos (trilha 5) usando LLM já dominado.
4. FHIR + SBIS (trilha 1) como base institucional.
5. RWE e CDSS apenas depois de trilhas 3 e 5 estabilizadas.

## Ver também

- `it_roles_taxonomy.md` — papéis genéricos que cada trilha mobiliza.
- `certifications_framework.md` — certificações específicas.
