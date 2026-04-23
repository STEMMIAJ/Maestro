---
titulo: "Da ideia ao deploy"
bloco: "01_ti_foundations/software_lifecycle"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "B"
tempo_leitura_min: 6
---

# Da ideia ao deploy

Ciclo de vida de software — fases pelas quais uma ideia vira sistema em produção. Modelos variam (Waterfall, Ágil, Lean); as fases essenciais são comuns.

## 1. Requisitos

Entender o problema antes de codar. Produto desta fase: documento que responde "o que o sistema precisa fazer, para quem, sob quais restrições".

Subdivisões:
- **Funcionais** — o que o sistema faz. "Gerar PDF de laudo com hash SHA-256".
- **Não funcionais** — como faz. Desempenho (gerar em < 5 s), segurança (LGPD), disponibilidade (99,5%).
- **Restrições** — legais, orçamentárias, técnicas. "Deve rodar em Windows 10 porque a vara exige".

Armadilha clássica: pular requisitos por ansiedade de codar. Resultado: retrabalho massivo.

## 2. Design / arquitetura

Decidir **como** o sistema será construído antes de escrever código.

- Arquitetura macro: monolito vs microserviços, SPA vs SSR, banco SQL vs NoSQL.
- Modelagem de dados: tabelas, relacionamentos, índices.
- Diagramas: C4, UML, fluxograma.
- Contratos: schema de API, formato de mensagem entre módulos.

Produto: ADR (*Architecture Decision Record*) — registro curto explicando por que cada escolha foi feita.

## 3. Código

Implementação. Ferramentas:
- **Editor/IDE** — VS Code, JetBrains, Vim.
- **Controle de versão** — Git (commits, branches, pull requests).
- **Revisão de código** — *code review* antes de integrar.
- **Padrão de estilo** — linter (ruff, eslint), formatter (black, prettier).

Boas práticas mínimas: commits pequenos e descritivos, branch por feature, não commitar segredo (`.env`), `.gitignore` correto.

## 4. Testes

Provar que o código faz o que deve e detectar regressões ao mudar.

Pirâmide de testes (do mais barato para o mais caro):
- **Unitário** — testa função isolada. Rápido (ms), em massa.
- **Integração** — testa módulo + dependência real (banco, API). Médio.
- **End-to-end** — testa fluxo completo pelo navegador (Playwright, Cypress). Lento, frágil.

Ferramentas Python: pytest, unittest. CI roda tudo automaticamente a cada push.

## 5. Deploy

Colocar o código em ambiente onde usuários reais o acessam.

- **Build** — compila/empacota artefato (Docker image, binário, `.whl`).
- **Pipeline CI/CD** — GitHub Actions, GitLab CI, Jenkins. Automatiza build → testes → deploy.
- **Ambientes** — dev → staging → produção (ver `ambientes_dev_staging_prod.md`).
- **Estratégias** — blue-green, canary, rolling update para minimizar downtime.
- **Infra** — servidores, nuvem, orquestrador (Kubernetes, ECS).

## 6. Operações (Ops / SRE)

Manter o sistema vivo em produção.

- **Monitoramento** — métricas (Prometheus, Grafana), logs (ELK, Loki), traces (Jaeger).
- **Alerta** — PagerDuty, Telegram bot que grita às 3 da manhã.
- **Backup e restauração** — testados periodicamente; backup que nunca foi restaurado é ficção.
- **Incidente e *postmortem*** — analisar falha sem culpar pessoa, corrigir causa raiz.
- **SLA / SLO / SLI** — métricas contratadas de disponibilidade e latência.

## DevOps vs SRE

- **DevOps** — cultura; equipes de dev e ops colaboram, não se jogam pela parede.
- **SRE** (*Site Reliability Engineering*) — aplicação prática do DevOps com engenheiros que tratam operação como problema de software (Google Book SRE).

## Por que importa para o perito

- **Monitor de processos** do Dexter passa por todo esse ciclo: requisito ("detectar movimentação em X"), design (async, fila, persistência), código, testes, deploy (launchd), ops (logs, alerta Telegram).
- **Perícia em falha de sistema** (e.g., e-commerce fora no Black Friday) exige entender em qual fase a falha nasceu — deploy mal planejado? teste insuficiente? requisito omitido?
- **Avaliar software de terceiro** (ex.: assinador CNJ) pede olhar maduro: tem versionamento? changelog? pipeline reproduzível?

## Referências

- Humble, J.; Farley, D. — *Continuous Delivery*, 2010.
- Google SRE Book (free.google.com.br/[TODO/RESEARCH: URL correta]).
