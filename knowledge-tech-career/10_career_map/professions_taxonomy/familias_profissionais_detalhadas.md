---
titulo: "Famílias Profissionais em Tech — Taxonomia Detalhada"
bloco: "10_career_map"
tipo: "referencia"
nivel: "junior"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 12
---

# Famílias Profissionais em Tech

Organização por família permite ver caminhos, identificar afinidade e mapear certificações/competências.

## 1. Desenvolvimento de Software

Construção de aplicações e sistemas.

| Papel | Descrição | Stack típica |
|-------|-----------|--------------|
| Frontend Developer | UI/UX técnico, navegador | React, Vue, Svelte, TS, CSS |
| Backend Developer | APIs, regra de negócio, BD | Python, Go, Node, Java, SQL |
| Full-stack Developer | Ambos os lados | TS + Next.js + Postgres |
| Mobile Developer | iOS/Android nativo ou híbrido | Swift, Kotlin, Flutter, RN |
| Game Developer | Jogos | Unity, Unreal, Godot |
| Embedded / IoT | Dispositivos, firmware | C, C++, Rust, microcontroladores |

## 2. Dados

Extração, organização, análise, entrega de insight.

| Papel | Descrição | Stack típica |
|-------|-----------|--------------|
| Data Analyst | Análise descritiva, dashboards | SQL, Excel, Power BI, Looker |
| Data Engineer | Pipelines, ingestão, DW | Airflow, dbt, Spark, Python, SQL |
| Analytics Engineer | Camada modelada entre eng e analista | dbt, SQL, Git |
| Data Scientist | Estatística, modelagem, experimento | Python, R, sklearn, notebook |
| Machine Learning Engineer | ML em produção | Python, MLOps, Docker, K8s |
| BI Developer | Relatórios corporativos | SSAS, Tableau, Qlik |

## 3. Infraestrutura e Operações

Sustentação, automação, confiabilidade.

| Papel | Descrição | Stack típica |
|-------|-----------|--------------|
| SysAdmin | Administração de SO | Linux, Windows Server, scripts |
| DevOps Engineer | Automação dev↔ops | Docker, K8s, Terraform, CI/CD |
| SRE (Site Reliability Engineer) | Confiabilidade em escala | SLI/SLO, observabilidade, IaC |
| Cloud Engineer | Projeto em nuvem | AWS/GCP/Azure |
| Platform Engineer | Plataforma interna para dev | K8s, Crossplane, Backstage |
| Network Engineer | Rede corporativa | Switching, routing, firewall |
| Database Administrator | BD em produção | Oracle, Postgres, MongoDB |

## 4. Segurança

Proteção de ativos, resposta a ameaças, compliance.

| Papel | Descrição | Stack típica |
|-------|-----------|--------------|
| Security Analyst (SOC) | Monitoramento, resposta inicial | SIEM, EDR, runbooks |
| Security Engineer | Controles, arquitetura | IAM, cripto, hardening |
| Pentester / Offensive | Simular ataque | Kali, Burp, Metasploit |
| Red Team | Campanha adversarial completa | OPSEC, C2, lateral movement |
| Blue Team | Defesa ativa, caça a ameaça | Detection engineering, threat hunt |
| GRC Analyst (Governance, Risk, Compliance) | Política, auditoria | ISO 27001, LGPD, SOC 2 |
| DPO / Encarregado LGPD | Privacidade | LGPD, GDPR, RIPD |
| AppSec / DevSecOps | Segurança em dev | SAST, DAST, SCA, threat model |
| Forensic Analyst | Resposta a incidente, prova | Volatility, Autopsy, cadeia custódia |

## 5. Produto e Design

Definir o quê, como, para quem.

| Papel | Descrição |
|-------|-----------|
| Product Manager | Prioridade, roadmap, descoberta |
| Product Owner (ágil) | Backlog, requisito detalhado |
| UX Researcher | Pesquisa com usuário |
| UX/UI Designer | Interface, interação |
| Product Designer | UX + UI + estratégia |
| Product Marketing | Mensagem, posicionamento |

## 6. IA e LLM

Explosão desde 2022. Papéis ainda se consolidando.

| Papel | Descrição | Stack típica |
|-------|-----------|--------------|
| AI Engineer | Integrar LLM em produto | Python, OpenAI/Anthropic SDK, LangChain |
| Prompt Engineer | Prompting, avaliação | eval frameworks, prompt libs |
| ML Research Engineer | Modelos de fronteira | PyTorch, JAX, HPC |
| RAG Engineer | Retrieval + generation | embeddings, vetor DB, ranking |
| Applied Scientist | Ponte pesquisa↔produto | papers, experimentos |
| AI Safety / Alignment | Redução de risco | evals, red teaming |
| AI Product Manager | Produto de IA | descoberta + técnica LLM |

## 7. Testes e Qualidade

| Papel | Descrição |
|-------|-----------|
| QA Analyst | Teste manual, documentação |
| QA Engineer | Teste automatizado, framework |
| SDET (Software Dev Engineer in Test) | Dev com foco em testabilidade |
| Performance Engineer | Carga, stress, profiling |

## 8. Suporte e Customer-Facing Technical

| Papel | Descrição |
|-------|-----------|
| Technical Support | Atendimento L1/L2 |
| Customer Success Engineer | Onboarding técnico, retenção |
| Solutions Engineer / Sales Engineer | Pré-venda técnica |
| Developer Advocate / DevRel | Comunidade dev |
| Technical Writer | Documentação |

## Como ler a tabela

- **Vizinhos horizontais:** transição natural com retrabalho médio (ex: Data Analyst → Analytics Engineer).
- **Vizinhos verticais (entre famílias):** transição com ponte temática (ex: Security Engineer ↔ DevOps via DevSecOps).
- **Pulo entre famílias distantes:** requer 1-2 anos de reskill (ex: Frontend → Data Scientist).

## Aplicação a Dr. Jesus

Médico perito tem afinidade alta com:

- **Dados clínicos + Analytics**: familiar com evidência, laudo, estatística.
- **Segurança + Compliance**: LGPD, sigilo, perícia digital.
- **IA aplicada à perícia**: transcrição, sumarização, RAG sobre jurisprudência.

Afinidade baixa (custo alto):

- Frontend puro, game dev, embedded.

Próximo passo: `papeis_em_saude_dados_e_pericia.md`.

## Referência cruzada

- `papeis_em_saude_dados_e_pericia.md`
- `../junior_pleno_senior/sinais_concretos_de_cada_nivel.md`
- `../role_expectations/expectativas_por_papel.md`
- `../certifications/mapa_certificacoes_por_trilha.md`
