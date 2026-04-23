---
titulo: "Trilha Médico para Tech — Dr. Jesus"
bloco: "10_career_map"
tipo: "plano"
nivel: "todos"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 14
---

# Trilha Médico para Tech — Dr. Jesus

Trilha customizada para médico perito com TEA + TDAH, CRM ativo, já executando automação Python avançada (Dexter, monitor de processos, download PJe). Objetivo: consolidar pleno em tech + consultor DPO clínico em 18-24 meses, sem abandonar prática pericial.

## Princípios operacionais

- **Máximo 1 tópico novo por mês.** TDAH + TEA não toleram paralelismo de aprendizado.
- **Aprender fazendo.** Cada fase produz artefato no Dexter ou portfólio.
- **Sessão curta e regular.** 45 min, 4x/semana, > 4h uma vez/semana.
- **Documentar tudo.** Cada aprendizado vira nota no knowledge-tech-career.
- **Sem certificação prematura.** Certifica só depois de ter construído.

## Fase 0 — Estabilização da base (já em andamento)

**Objetivo**: infraestrutura pessoal estável.

- [x] Hardware (Mac) + Time Machine funcional + backup 3-2-1.
- [x] Git + GitHub + chaves SSH ed25519 por contexto.
- [x] 1Password/Bitwarden + MFA em tudo crítico.
- [ ] Consolidar `~/Desktop/STEMMIA Dexter/` como hub único (em curso).
- [ ] CLAUDE.md global revisado e lean.

Saída: ambiente que não perde trabalho por falha técnica.

## Fase 1 — Python pericial consolidado (mês 1-2)

**Objetivo**: subir Python de "funcional" para "bem estruturado".

- Tipagem com `mypy` no Dexter.
- `pyproject.toml` + `uv` para cada pacote interno.
- Testes pytest em 3 módulos core (downloader PJe, monitor, template de laudo).
- Refatorar 1 script antigo para módulo instalável.

Artefato: Dexter com testes rodando + badge CI verde.

## Fase 2 — Git, GitHub, CI/CD (mês 2-3)

**Objetivo**: fluxo dev profissional.

- Conventional Commits + PR próprio.
- GitHub Actions: lint + mypy + pytest.
- CHANGELOG automatizado via `cz` ou `release-please`.
- 1 repositório público de portfólio com README forte.

Artefato: `stemmia-forense-toolkit` público (partes não-sensíveis do Dexter).

## Fase 3 — SQL e dados clínicos/periciais (mês 3-5)

**Objetivo**: SQL sólido + modelar dados periciais.

- SQLite já em uso. Consolidar schema do Dexter.
- Aprender CTE, window function, `EXPLAIN` via SQLBolt + Mode Analytics.
- Migrar análise ad-hoc para views e materialized views.
- Introduzir dbt local ou DuckDB para análises pesadas.

Artefato: dashboard de produção pericial (quantos laudos, prazos, tempo médio).

## Fase 4 — LGPD aplicada + DPO (mês 5-7)

**Objetivo**: formalizar competência DPO em saúde.

- Estudar Lei 13.709/2018 + resoluções ANPD 2024-2026.
- Curso Exin Privacy & Data Protection Foundation.
- Escrever RIPD real para a própria prática pericial.
- Publicar artigo: "LGPD na prática pericial médica".

Artefato: RIPD assinado + artigo no site.

## Fase 5 — IA aplicada à perícia (mês 7-10)

**Objetivo**: integrar LLM com segurança e avaliação.

- Uso de Anthropic API com prompt caching no fluxo pericial.
- RAG local (LLM + Qdrant ou pgvector) sobre própria base de laudos anonimizados.
- Eval framework: `promptfoo` ou `ragas` para validar sumarizações.
- Guardrail: nunca mandar dado identificável para API externa.

Artefato: ferramenta de rascunho de laudo com eval documentada.

## Fase 6 — Certificação DPO + portfólio público (mês 10-13)

**Objetivo**: credenciais formais + marketing silencioso.

- IAPP CIPM ou CIPP/E (decidir em função de mercado BR).
- Site pessoal com portfólio: perito + DPO clínico.
- 4 artigos técnicos publicados (LGPD, sigilo, IA em saúde, cadeia de custódia digital).

Artefato: primeira proposta comercial de consultoria DPO clínico.

## Fase 7 — Cloud básico (mês 13-15)

**Objetivo**: entender nuvem para rodar serviços próprios e avaliar clientes.

- AWS Cloud Practitioner (conceitual) OU GCP ACE.
- Deploy de N8N/monitor próprio em EC2/Lightsail cifrado.
- IAM com menor privilégio.

Artefato: infraestrutura pessoal em nuvem documentada.

## Fase 8 — Observabilidade e confiabilidade (mês 15-16)

**Objetivo**: monitorar o que está em produção.

- Prometheus + Grafana no monitor de processos.
- Alertas via Telegram.
- SLO mínimo: monitor de processos com 99% de sucesso mensal.

Artefato: dashboard Grafana + runbook de incidente.

## Fase 9 — Dados sensíveis em escala (mês 16-18)

**Objetivo**: lidar com clientes com volume maior de dados.

- Estudar anonimização, pseudonimização, differential privacy básica.
- Modelo OMOP CDM para RWE [TODO: decidir se vai investir].
- Políticas de retenção automatizadas.

## Fase 10 — Liderança técnica em nicho (mês 18-21)

**Objetivo**: posicionamento sênior no nicho saúde+dados+perícia.

- Palestra em congresso médico-jurídico.
- Curso próprio: "Tecnologia para perito médico".
- Mentoria 1:1 paga.

## Fase 11 — Avaliação e pivô (mês 21-24)

**Objetivo**: revisar trilha com dados concretos.

- Comparar tempo investido × receita adicional × satisfação.
- Decidir: aprofundar em consultoria, migrar para CTO healthtech, manter dual?
- Reescrever trilha com base nos dados reais.

## Fase 12 — Formalização do conhecimento

**Objetivo**: knowledge-tech-career deste diretório evolui para obra publicável.

- Revisar todos os artefatos: remover `status: rascunho`, promover para `validado`.
- Site MkDocs ou Hugo com o conteúdo.
- Livro/PDF vendável sobre "Tech para Médico Perito".

## Cadência sugerida

- **Diária (4 dias/semana)**: 45 min de estudo + 15 min de registro no knowledge-tech-career.
- **Semanal (sábado manhã)**: 3-4h de implementação em projeto.
- **Mensal**: revisão do que funcionou, reclassificar fase se necessário.
- **Trimestral**: teste de backup + revisão de portfólio público.

## Riscos conhecidos e mitigação

| Risco | Mitigação |
|-------|-----------|
| Sobrecarga (TEA/TDAH) | Máximo 1 tópico/mês, sessão curta |
| Perda de foco pericial | Sempre conectar tópico a caso real |
| Certificação antes da prática | Regra: só certifica após projeto completo |
| Queima de dinheiro em curso raso | Preferir doc oficial + fonte primária |
| Isolamento social | Mentoria paga ou comunidade técnica (Discord) |

## Métrica de progresso

- Nº de PRs em repositórios próprios.
- Nº de artigos no knowledge-tech-career promovidos para `validado`.
- Nº de laudos entregues usando a automação.
- Receita adicional de consultoria técnica.

## Referência cruzada

- `../certifications/mapa_certificacoes_por_trilha.md`
- `../portfolios_projects/portfolio_projeto_eficaz.md`
- `../role_expectations/expectativas_por_papel.md`
- `../professions_taxonomy/papeis_em_saude_dados_e_pericia.md`
