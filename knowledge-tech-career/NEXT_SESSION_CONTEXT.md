# NEXT_SESSION_CONTEXT.md

Última atualização: 2026-04-23 (pós-rodada 2, durante rodada 3 paralela).

## Onde a base está

- Raiz: `/Users/jesus/Desktop/STEMMIA Dexter/knowledge-tech-career/`.
- **190 arquivos Markdown** em **112 diretórios** (17 blocos numerados + `AGENTS/`).
- 9 documentos mestres na raiz (agora inclui `logs_round1.md`).
- Checkpoint e snapshot de rodada 2 gravados em `15_memory/checkpoints/` e `13_reports/snapshots/`.
- Rodada 3 em execução paralela por outros agentes (não tocar blocos 03, 04, 05, 10, 16 durante a rodada).

## O que está pronto (EXECUTADO)

- Estrutura física completa.
- Documentos mestres + governança (00) + contratos de agente (AGENTS/).
- **Blocos densos:** 01_ti_foundations (23), 02_programming (25), 06_data_analytics (16), 07_health_data (13), 08_ai_and_automation (21), 11_personal_skill_mapping (16 — 9 evidências reais).
- Symlink `02_programming/python/python-base` acopla PYTHON-BASE (179 MB, 90 falhas catalogadas).
- Rodada 2 documentada em `CHANGELOG.md` (bloco `[0.2.0]`).

## Blocos ainda esqueleto (folha vazia)

- `03_web_development` (5 arquivos — README + 4 parciais)
- `04_systems_architecture` (1 — só README)
- `05_security_and_governance` (4 — README + 3 parciais)
- `10_career_map` (1 — só README)
- `16_inbox` (1 — só README)

Rodada 3 em curso está resolvendo esses blocos.

## Arquivo a abrir primeiro na próxima sessão

1. Este arquivo.
2. `TASKS_NOW.md` (reescrito pós-rodada 2).
3. `15_memory/checkpoints/checkpoint_2026-04-23_round2.md`.
4. `13_reports/snapshots/progress_snapshot_round2.md`.

## Próximo passo mínimo

Rodar `find knowledge-tech-career -type f -name "*.md" | wc -l` para confirmar término da rodada 3 (esperado > 190). Depois executar item 1 de `TASKS_NOW.md`: `openclaw memory index --path <root>`.

## O que NÃO fazer na próxima sessão

- Não promover rascunhos para `vigente` sem revisão humana explícita.
- Não renomear blocos numerados.
- Não executar destrutivos sem `LIMPAR-LIBERADO`.
- Não tocar `PYTHON-BASE/` via symlink sem ler `SKILL.md` antes.

## Estado de dependências críticas

- Promoção de rascunhos depende de revisão humana.
- OpenClaw index depende da rodada 3 terminar.
- Repositório GitHub privado depende de decisão sobre escopo (subpasta vs repo próprio).

## Lembretes operacionais

- Fila de trabalho oficial: `~/Desktop/_MESA/40-CLAUDE/fila-opus/dexter-maestro/fila.md`.
- Rodar agentes em paralelo quando independentes.
- Atualizar `TASKS_MASTER.md`, `CHANGELOG.md` e este arquivo ao final de cada rodada.
- Toda afirmação sem fonte → `TODO/RESEARCH`.
- Hook anti-mentira ativo: declarar "feito/pronto" exige output de verificação.
