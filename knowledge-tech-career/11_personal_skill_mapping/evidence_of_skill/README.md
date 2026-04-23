---
titulo: Índice de Evidências de Habilidade
bloco: 11_personal_skill_mapping
arquivo: evidence_of_skill/README.md
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
---

# Evidências de Habilidade — Índice

Cada entrada aponta para artefato real no ecossistema STEMMIA Dexter, validado por leitura
de 30–80 linhas de código antes do registro. Nível na escala 0–4 da matriz (`skill_matrix/current_skills_matrix.md`).

## Catálogo

| # | Arquivo | Domínio / Subtópico | Nível | Fonte primária |
|---|---|---|---|---|
| 01 | `evidence_01_pje_playwright_cdp.md` | Python / Playwright + CDP | 3 | `src/pje/emergencia/baixar_documentos_processo_aberto.py` |
| 02 | `evidence_02_datajud_descoberta.md` | APIs / REST + ThreadPool | 2 | `src/jurisprudencia/descobrir_processos.py` |
| 03 | `evidence_03_djen_async_tenacity.md` | Python / async + retry | 3 | `PYTHON-BASE/08-SISTEMAS-COMPLETOS/monitor-processos-novo-2026-04-22/02-scripts/monitor/fontes/djen.py` |
| 04 | `evidence_04_anti_mentira_stop_hook.md` | Agentes / hooks Claude Code | 3 | `~/stemmia-forense/hooks/anti_mentira_stop.py` |
| 05 | `evidence_05_verificador_peticao_pdf.md` | Python / NLP fuzzy + CLI gate | 3 | `Maestro/verificadores/verificador_peticao_pdf.py` |
| 06 | `evidence_06_template_laudo_placeholders.md` | Automação doc. / templates | 3 | `src/automacoes/usar_template_pericia.py` |
| 07 | `evidence_07_skill_modo_sonnet_relay.md` | Prompt eng. / skill multi-modelo | 3 | `~/.claude/skills/modo-sonnet/SKILL.md` |
| 08 | `evidence_08_distiller_feedback_auto.md` | Python / clustering + ETL | 2 | `~/stemmia-forense/hooks/anti_mentira_distiller.py` |

## Regras de curadoria

1. Uma evidência por arquivo. Nome: `evidence_{nn}_{slug}.md`.
2. Frontmatter YAML obrigatório com `nivel_demonstrado` (0–4) honesto.
3. Validação externa classificada como **Forte / Média / Fraca** (critério no template).
4. Limitações conhecidas sempre listadas — honestidade técnica bate inflação de currículo.
5. Trecho de código real colado dentro de bloco ```` ```python ```` ou equivalente; nunca paráfrase.

## Lacunas identificadas (sem evidência ainda)

- `Python.pytest / testes` — nível 0; único vestígio de teste real é `02-scripts/tests/` no monitor novo.
- `SQL.JOIN / CTE` — zero evidência.
- `DevOps.Docker / CI/CD` — zero evidência.
- `Databases.SQLite` — matriz diz 2, mas não achei script de schema próprio em tempo de triagem (candidato: `Maestro/banco-local/indexer_ficha.py`).
- `Automação doc.geração PDF/DOCX` — matriz diz 2, sem arquivo demonstrativo no catálogo atual.

## Próxima rodada sugerida

- Cobrir SQLite via leitura de `Maestro/banco-local/indexer_ficha.py`.
- Rastrear evidência de geração PDF/DOCX (provável em `src/pipeline/` ou `FERRAMENTAS/`).
- Ler `hub.py` para documentar o orquestrador como evidência de `Agentes.arquitetura multi-agente` nível 3.
