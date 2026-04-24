# ADR-0001 — Adotar GitHub como espinha dorsal do Maestro

**Data:** 2026-04-24
**Status:** accepted
**Autor:** Dr. Jesus

## Contexto
Sistema Maestro estava em estado de fragmentação: 3 hubs paralelos (STEMMIA Dexter, ANALISADOR FINAL, stemmia-forense), scripts triplicados, CHANGELOG ausente, nenhuma forma objetiva de saber o que estava "pronto". Dr. Jesus (TEA+TDAH) perdeu controle do escopo porque o Claude Code criava arquivos sem diretriz. Necessário: externalizar memória, rastreabilidade e critério de "terminado".

## Opções consideradas
1. **Notion + Obsidian** — ótimo para notas, ruim para código; CI/CD não existe
2. **Git local puro (sem remote)** — rastreabilidade interna, sem backup externo, sem Issues
3. **GitHub (repo + Issues + Actions + PRs)** — rastreabilidade + backup + CI enforcing DOD
4. **GitLab / Codeberg** — equivalentes, mas `gh` CLI já autenticado e usuário já tem conta

## Decisão
Opção 3 — GitHub como repo oficial do Maestro, com:
- Issues como único formato de "tarefa aberta"
- PRs como único caminho para `main`
- Actions rodando `enforce-dod.yml` bloqueando merge sem DOD completo
- Repo privado (STEMMIAJ/maestro)

## Consequências

**Positivas:**
- Cada tarefa tem identidade (`#NNN`)
- Impossível "perder" trabalho: tudo vira commit + push
- Actions fazem papel de "professor" — reprovam PR sem DOD
- Backup automático no remote
- Auditoria externa já pode ler o repo (link único)

**Negativas / custos aceitos:**
- Curva de aprendizado de `gh` CLI (mínima — 5 comandos cobrem 95%)
- Requer conexão à internet para `push` (aceitável)
- Código privado fica em servidor de terceiro (aceitável — não há dado clínico de paciente no repo, apenas pipeline/scripts)

**Arquivos/módulos afetados:**
- Todo `~/Desktop/STEMMIA Dexter/Maestro/` vira repo git rastreável

## Como reverter
`git remote remove origin` + arquivar repo no GitHub. Código local intacto.
