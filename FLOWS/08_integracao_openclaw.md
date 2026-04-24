# FLOW 08 — Integracao com OpenClaw

## Objetivo

Usar o OpenClaw como camada de automação (cron, dashboard local, queue de agentes), mantendo o Maestro como fonte de verdade textual e de memória.

## Gatilho

- Desbloqueio manual após confirmação oficial do Dr. Jesus sobre o que é o OpenClaw.
- Dependência: docs em `docs/openclaw-official/` existentes e validados.

## Entradas

| artefato | caminho | observação |
|----------|---------|------------|
| Documentação oficial OpenClaw | `docs/openclaw-official/` | [TODO/RESEARCH] baixar após confirmação |
| Versão instalada | `openclaw --version` | v2026.4.21 detectada na sessão 4 |
| CRON/00_plan.md | `Maestro/CRON/00_plan.md` | jobs a migrar para OpenClaw |
| AGENTS/*.md | `Maestro/AGENTS/` | agentes a expor |

## Passos (quando desbloqueado)

1. Dr. Jesus confirma: nome oficial, repo/URL, versão em uso.
2. Baixar/copiar documentação oficial para `docs/openclaw-official/` (8 páginas mínimas).
3. Atualizar:
   - `reports/openclaw_capabilities_summary.md`
   - `reports/openclaw_command_map.md`
   - `reports/openclaw_for_this_project.md`
4. Mapear comandos reais (memória, cron, agentes, dashboard) substituindo sintaxe presumida abaixo.
5. Configurar hooks em `CONFIG/openclaw_hooks.md` após validação de sintaxe.
6. Migrar jobs de `CRON/00_plan.md` para OpenClaw cron (um por um, com 1 semana de observação cada).
7. Expor agentes do Maestro via `openclaw agent run <nome>` (sintaxe a confirmar).
8. Ativar dashboard local em `http://localhost:<PORT>` (porta a confirmar).

## Integrações previstas

| área | como integra | sintaxe | status |
|------|-------------|---------|--------|
| Memória | importar `memory/` para OpenClaw | `openclaw memory add --from Maestro/memory/` | sintaxe PRESUMIDA |
| Cron | jobs J01–J07 gerenciados pelo OpenClaw | `openclaw cron add ...` | sintaxe PRESUMIDA |
| Agentes | agentes Maestro expostos | `openclaw agent run <nome>` | sintaxe PRESUMIDA |
| Dashboard local | visão interna (≠ stemmia.com.br público) | `http://localhost:<PORT>` | porta RESEARCH |
| Hooks Claude Code | hook pre-Stop registra evento | integração via `CONFIG/openclaw_hooks.md` | planejado |

## Saídas esperadas

- Maestro continua como fonte de verdade (texto, memória, markdown).
- OpenClaw vira a camada de execução (cron, dashboard local, fila).
- Dashboard público `stemmia.com.br` consome do DB remoto via FLOW 07 (independente do OpenClaw).

## Falhas conhecidas / Rollback

| falha | sintoma | rollback |
|-------|---------|----------|
| Sintaxe OpenClaw diferente do presumido | comandos falham | corrigir `reports/openclaw_command_map.md` antes de ativar |
| OpenClaw sobrepõe hooks Claude Code | conflito hook pre-Stop | desativar hook OpenClaw; manter hook anti-mentira |
| Dashboard porta em conflito | `address already in use` | configurar porta alternativa |
| Jobs migrados disparam em duplicata | cron + launchd ativos | desativar launchd antes de ativar OpenClaw cron |

## Status

- BLOQUEADO até confirmação oficial.
- OpenClaw v2026.4.21 detectado: 138 processos SQLite, conversa Perplexity (4440 linhas) intacta.
- Docs oficiais: pendentes em `docs/openclaw-official/` ([TODO/RESEARCH]).
- Nenhuma configuração ativa. Nenhum hook ativado.
