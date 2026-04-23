---
titulo: Taxonomia de Papéis em TI
tipo: master_summary
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
---

# Taxonomia de Papéis em TI

## Método

Para cada papel: missão, skills-chave, ferramentas típicas, onde cruza com saúde/perícia. Tom descritivo, sem hierarquia de prestígio.

## Desenvolvedor

- **Missão:** escrever código que implementa requisito.
- **Skills-chave:** linguagem (Python, JS, Java, Go, etc.), lógica, leitura de documentação, versionamento (Git), testes básicos.
- **Ferramentas:** VS Code/JetBrains, Git, framework da stack (Django, React, Spring), banco (Postgres/MySQL).
- **Cruza com saúde/perícia:** construir script de extração de laudo, bot Telegram pericial, integração PJe/DataJud — exatamente o que o ecossistema Dexter já faz.

## Engenheiro de software

- **Missão:** dev com visão sistêmica — qualidade, manutenção, escalabilidade.
- **Skills-chave:** tudo de dev + testes automatizados, CI/CD, design de API, leitura crítica de código, noção de performance.
- **Ferramentas:** CI (GitHub Actions, GitLab CI), contêineres (Docker), observabilidade (logs estruturados), framework de teste.
- **Cruza:** qualquer sistema pericial que precise sobreviver a 5 anos sem virar gambiarra.

## Analista de sistemas

- **Missão:** traduzir necessidade de negócio em especificação técnica; às vezes programa, às vezes só modela.
- **Skills-chave:** levantamento de requisito, modelagem (UML, BPMN), SQL, documentação, diálogo com usuário não técnico.
- **Ferramentas:** Jira, Confluence, draw.io/Miro, DBeaver.
- **Cruza:** ponte natural entre médico e dev — o perito que entende fluxo hospitalar e consegue especificar sistema.

## Analista de dados

- **Missão:** responder pergunta de negócio com dado.
- **Skills-chave:** SQL forte, Excel/Sheets, Python (pandas) ou R, visualização, estatística descritiva, storytelling com dado.
- **Ferramentas:** PostgreSQL, BigQuery, Power BI, Tableau, Looker, Metabase.
- **Cruza:** análise de base pericial, estatística de perícias por tribunal, KPI de clínica.

## Cientista de dados

- **Missão:** inferir, prever, explicar com estatística e ML.
- **Skills-chave:** estatística inferencial, ML (scikit-learn, XGBoost), validação de modelo, comunicação de incerteza.
- **Ferramentas:** Python (pandas, scikit-learn, statsmodels), Jupyter, MLflow, cloud notebook.
- **Cruza:** modelo preditivo em saúde (sobrevida, risco, diagnóstico), análise de laudo em larga escala, RWE.

## Engenheiro de dados

- **Missão:** construir as tubulações (ETL/ELT) que entregam dado limpo a analistas e cientistas.
- **Skills-chave:** SQL avançado, Python, modelagem dimensional, orquestração, cloud.
- **Ferramentas:** Airflow/Prefect/Dagster, dbt, Spark, Kafka, Snowflake/BigQuery/Redshift.
- **Cruza:** consolidar DataJud + PJe + DJEN em um warehouse pericial — exatamente o tipo de problema que o Dexter resolve hoje em escala menor.

## Arquiteto de software

- **Missão:** desenhar sistema grande — decidir o que vira serviço, como se comunica, onde está o risco.
- **Skills-chave:** anos de dev + leitura de sistemas distribuídos, padrões (DDD, event-driven), trade-off consciente, comunicação.
- **Ferramentas:** diagramas (C4, draw.io), ADRs, plataformas de nuvem.
- **Cruza:** desenhar sistema de saúde integrado (prontuário + laudo + faturamento) — raro, caro, nicho.

## DevOps / SRE

- **Missão:** tornar entrega de software confiável e automática.
- **Skills-chave:** Linux, rede básica, containers, IaC, observabilidade, incident response.
- **Ferramentas:** Docker, Kubernetes, Terraform, Ansible, Prometheus, Grafana, AWS/GCP/Azure.
- **Cruza:** baixa aderência direta ao perfil médico — alto custo de aprendizado para benefício lateral.

## Especialista em segurança

- **Missão:** identificar, defender e responder a risco de segurança.
- **Skills-chave:** redes, criptografia, sistemas, compliance (LGPD, HIPAA, ISO 27001), pensamento adversarial.
- **Ferramentas:** Burp, Nmap, Wireshark, SIEM (Splunk, Sentinel), EDR.
- **Cruza:** segurança de dado de saúde (LGPD + ANPD + CFM), auditoria de prontuário, perícia digital — nicho alto valor.

## Product manager

- **Missão:** decidir o que construir, para quem, por quê; priorizar.
- **Skills-chave:** pesquisa de usuário, métrica de produto, escrita clara, negociação, visão de negócio.
- **Ferramentas:** Jira, Figma (para ler), Amplitude/Mixpanel, roadmapping (Productboard).
- **Cruza:** PM de produto médico/jurídico — tradução entre domínio clínico e engenharia. Aderência altíssima.

## UX/UI designer

- **Missão:** desenhar experiência e interface; reduzir atrito.
- **Skills-chave:** pesquisa qualitativa, IA (arquitetura de informação), heurísticas, Figma, acessibilidade.
- **Ferramentas:** Figma, Maze, UserTesting, Notion.
- **Cruza:** design de interface médica (prontuário, laudo) — subexplorado no Brasil.

## Engenheiro de IA

- **Missão:** aplicar modelos (próprios, open-source, ou API) dentro de produto.
- **Skills-chave:** prompt engineering, fine-tuning, RAG, avaliação de modelo, custo/latência, integração (MCP, LangChain, SDK).
- **Ferramentas:** Python, PyTorch/Transformers, APIs (Anthropic/OpenAI/Google), vetor DB (Pinecone, pgvector).
- **Cruza:** direto no que o Dr. Jesus já faz — Claude Code, MCP, skills, hooks aplicados a laudo pericial.

## Resumo de aderência ao perfil médico-perito

| Papel | Aderência |
|---|---|
| Engenheiro de IA aplicada saúde | Alta |
| Cientista de dados em saúde | Alta |
| Product manager saúde/legal | Alta |
| Analista/engenheiro de dados em saúde | Alta |
| Analista de sistemas saúde | Média-alta |
| Especialista em segurança saúde | Média |
| Engenheiro de software | Média |
| Arquiteto de software | Média (longo prazo) |
| DevOps/SRE, front-end puro, sysadmin | Baixa |

## Ver também

- `ti_career_overview.md` — famílias e trilhas.
- `health_data_career_paths.md` — detalhamento saúde+TI.
