# TASKS_NOW.md — Próxima rodada

Arquivo volátil. Sobrescrito a cada rodada. Contém apenas o que deve ser feito AGORA. Histórico vive em `CHANGELOG.md` e `TASKS_MASTER.md`.

Data de corte: 2026-04-23.
Contexto: rodada 1 concluiu criação de árvore (112 diretórios) e docs mestres. Próxima rodada foca em governança e primeiros blocos técnicos para destravar dependências.

## Prioridade alta (fazer na próxima rodada)

1. **KTC-001** — Redigir `00_governance/conventions.md`. Saída ≥ 40 linhas. Status alvo: `EXECUTADO`.
2. **KTC-002** — Redigir `00_governance/scope.md`. Saída ≥ 30 linhas. Status alvo: `EXECUTADO`.
3. **KTC-004** — Redigir `00_governance/promotion_rules.md`. Destrava KTC-145 e KTC-160. Status alvo: `EXECUTADO`.
4. **KTC-170** — Criar `AGENTS/README.md` catalogando os 5 agentes previstos. Status alvo: `EXECUTADO`.
5. **KTC-174** — Criar `AGENTS/auditor_status.md` (primeiro agente funcional, verifica coerência de status). Status alvo: `EXECUTADO`.

## Prioridade média (fazer se sobrar tempo)

6. **KTC-110** — Primeira versão de `11_personal_skill_mapping/current_state/snapshot.md` — inventário honesto do estado atual em 6 eixos (dev, dados, IA, infra, segurança, saúde+TI).
7. **KTC-100** — Iniciar `10_career_map/professions_taxonomy/` com lista bruta de 20 cargos TI relevantes. Fonte: roadmap.sh (marcar `TODO/RESEARCH` onde faltar).
8. **KTC-120** — Iniciar `12_sources/official_docs/index.md` com 10 entradas mínimas (MDN, docs.python.org, PostgreSQL, FHIR, etc).

## Prioridade baixa (só se rodada for longa)

9. **KTC-150** — Template `15_memory/daily/`.
10. **KTC-152** — Template `15_memory/decisions/` (ADR-lite).

## Regras desta rodada

- Nenhum arquivo `notes.md` dos blocos técnicos (01–09) deve ser preenchido ainda. Destravar governança primeiro.
- Toda tarefa concluída: mudar status em `TASKS_MASTER.md` para `EXECUTADO` e somar ao `CHANGELOG.md`.
- Ao final: reescrever este arquivo com as 5–10 próximas.
