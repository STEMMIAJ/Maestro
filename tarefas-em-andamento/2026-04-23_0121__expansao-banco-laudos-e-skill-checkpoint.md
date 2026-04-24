---
id: 2026-04-23_0121__expansao-banco-laudos-e-skill-checkpoint
criado_em: 2026-04-23 01:21
sessao_id: opus-4-7-rename-expansao-banco-de-dados-antiga
tema: Expansao banco laudos MG + skill enviar-tarefas-em-andamento
status: pausado
tags: [banco-laudos, skill-checkpoint, plan-mode-aprovado, dois-planos-paralelos]
working_dir: /Users/jesus/Desktop/STEMMIA Dexter
prioridade: alta
prazo: sem prazo fixo
---

# Expansao banco laudos MG + skill `enviar-tarefas-em-andamento`

## Objetivo

Continuar dois planos APROVADOS em sessao anterior, agora em paralelo:

- **Plano A** — popular banco de laudos reais comecando por GV (TJMG + TRF6) e expandindo concentricamente por MG.
- **Plano B** — implementar skill `enviar-tarefas-em-andamento` com ativacao semantica que cria checkpoints individuais por tarefa pausada (este arquivo aqui e o primeiro uso real da pasta — antes mesmo da skill existir).

## Estado atual

| Plano | Arquivo | Fase concluida | Aguardando |
|-------|---------|----------------|------------|
| A — banco laudos | `~/.claude/plans/populacao-banco-laudos-mg.md` (520 linhas) | F0 nao iniciada | "ok fase 0" |
| B — skill checkpoint | `~/.claude/plans/playful-pondering-rabbit.md` | F0 baseline verificada (PASTA OK + SEM CONFLITO) | "ok fase 1" |

Ambos os planos seguem TEMPLATE-PLANO.md (11 blocos + CKPT por fase + rollback).

## Arquivos relevantes (paths absolutos)

### Planos-mae
- `/Users/jesus/.claude/plans/populacao-banco-laudos-mg.md` — plano A, 7 fases (F0 diagnostico → F6 verificacao)
- `/Users/jesus/.claude/plans/playful-pondering-rabbit.md` — plano B, 3 fases (F0 baseline → F2 trigger global)

### Pipeline existente (NAO modificar — reaproveitar)
- `/Users/jesus/Desktop/STEMMIA Dexter/src/coleta-honorarios/baixar_tjmg_v3.py` (8129B)
- `/Users/jesus/Desktop/STEMMIA Dexter/src/coleta-honorarios/parsear_batch_sessao.py` (2046B)
- `/Users/jesus/Desktop/STEMMIA Dexter/src/coleta-honorarios/upgrade_parciais_inteiroteor.py` (8651B)

### Pastas-destino
- `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/tarefas-em-andamento/` — onde checkpoints da skill B vivem (este arquivo aqui)
- `/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/Banco-Transversal/Honorarios-Periciais/` — handoff PID 19869 + base de laudos

### Referencias
- `/Users/jesus/Desktop/STEMMIA Dexter/00-CONTROLE/TEMPLATE-PLANO.md` — formato obrigatorio dos planos
- `/Users/jesus/.claude/docs/SISTEMA-PERICIAS-MAPA-MESTRE.md` — mapa do sistema (341 linhas)
- `/Users/jesus/.claude/skills/refino-7/SKILL.md` — template de skill a imitar
- `/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/Banco-Transversal/Honorarios-Periciais/_HANDOFF-20260421-0600.md`

## Comandos executados nesta sessao (verificacao baseline)

```bash
# F0 do plano B — confirmacao que fizemos
test -d "/Users/jesus/Desktop/STEMMIA Dexter/Maestro/tarefas-em-andamento" && echo "PASTA OK"
ls /Users/jesus/.claude/skills/ | grep -i "tarefas\|checkpoint\|pausar" || echo "SEM CONFLITO"
# Ambos retornaram OK

# Verificacao scripts v3 do plano A
ls -la "/Users/jesus/Desktop/STEMMIA Dexter/src/coleta-honorarios/"baixar_tjmg_v3.py \
       "/Users/jesus/Desktop/STEMMIA Dexter/src/coleta-honorarios/"parsear_batch_sessao.py \
       "/Users/jesus/Desktop/STEMMIA Dexter/src/coleta-honorarios/"upgrade_parciais_inteiroteor.py
```

## Task list no momento da pausa

### Plano A — banco laudos
- [ ] T00 inventario PDFs honorarios (Fase 0)  > **proxima quando der "ok fase 0"**
- [ ] T01 criar `anel_geografico.json` mapeando 853 comarcas MG em 8 aneis
- [ ] T02 baseline relatorio
- [ ] CKPT0 aprovacao
- [ ] F1..F6 (minerar PDFs → coletor TJMG → coletor TRF6 → expansao concentrica → indexacao → verificacao)

### Plano B — skill checkpoint
- [x] T00 confirmar pasta e ausencia de conflito (PASTA OK + SEM CONFLITO)
- [x] CKPT0 baseline aprovado (implicito — pasta criada e plano aprovado via ExitPlanMode)
- [ ] T10 criar diretorio da skill  > **proxima quando der "ok fase 1"**
- [ ] T11 criar SKILL.md com frontmatter + ≥10 aliases + workflow 6 passos
- [ ] T12 criar templates/checkpoint-template.md (12 secoes)
- [ ] T13 criar helpers/criar_checkpoint.py (CLI + stdin JSON + slugify ASCII + atualiza _INDICE.md + append TASKS_NOW.md)
- [ ] T14 criar _README.md na pasta de checkpoints
- [ ] T15 criar _INDICE.md inicial
- [ ] CKPT1 aprovacao
- [ ] T20 adicionar bloco-trigger no `~/.claude/CLAUDE.md` global
- [ ] T21 smoke test em conversa real
- [ ] T22 smoke test do helper standalone
- [ ] CKPT2 final

## Proximo passo concreto

Em nova sessao, dar UM dos dois comandos:

**Para destrancar plano B (recomendado — mais rapido, valida a propria pasta):**
> "ok fase 1 do playful-pondering-rabbit, executa em time paralelo"

**Para destrancar plano A:**
> "ok fase 0 do populacao-banco-laudos-mg, executa em time paralelo"

**Para destrancar AMBOS em paralelo (se houver tempo):**
> "executa em paralelo: ok fase 1 do plano B + ok fase 0 do plano A. Time A faz a skill, Time B faz o inventario do banco. Reporta quando ambos terminarem para CKPT."

## Bloqueios

- Nenhum bloqueio tecnico. Aguarda apenas autorizacao explicita ("ok fase N") por enforcement do TEMPLATE-PLANO.md (regra "Claude NAO inicia proxima fase sem aprovacao explicita").
- ATENCAO concorrente: ha tambem o trabalho do `Maestro/CHECKPOINT-2026-04-23.md` (OpenClaw + Telegram + FTP) que esta aguardando 4 credenciais via `PROMPT-DR-JESUS-PARALELO.md`. Esse trabalho e SEPARADO destes dois planos — nao misturar.

## Processos rodando em background

Nenhum nesta sessao. (Sessao anterior tinha PID 19869 do pipeline coleta-honorarios — verificar se ainda esta vivo antes de iniciar plano A para evitar lock no perfil Playwright.)

```bash
# Verificacao recomendada antes de comecar plano A
ps aux | grep -E "baixar_tjmg|playwright" | grep -v grep
```

## Decisoes tomadas (com motivo)

1. **Pasta `tarefas-em-andamento/` em vez de reusar `NEXT_SESSION_CONTEXT.md`** — NEXT_SESSION_CONTEXT e singular (sobrescrito a cada rodada), checkpoints sao multiplos (1 por tarefa pausada).
2. **Skill = orquestracao + helper Python = I/O deterministico** — separa responsabilidades; helper enforca slug ASCII per regra Maestro/CLAUDE.md.
3. **Trigger duplo (description rica na skill + bloco no CLAUDE.md global)** — mesmo padrao do "SISTEMA DE PERICIAS — PORTA DE ENTRADA UNICA" recem-adicionado em 22/abr.
4. **Reaproveitar v3 no plano A em vez de novo pipeline** — ROI maior, ja testado, ja resolveu cache stale.
5. **Expansao concentrica em 8 aneis** — garante valor mesmo se abortar cedo (anel 1 = GV ja resolve casos imediatos).

## Plano de acao com agentes em time paralelo

Ao retomar e dar autorizacao, despachar **DOIS times** num unico turno (multiplas `Agent` calls em paralelo):

### Time A — Skill checkpoint (Fase 1 do plano B)
- **Subagente:** `general-purpose` (ou `agent-creator` se preferir especializacao)
- **Modelo:** Opus 4.7 (default)
- **Tarefa:** Executar T10..T15 do `~/.claude/plans/playful-pondering-rabbit.md`
- **Briefing self-contained:**
  > Voce e um agente executor. Leia o plano em `/Users/jesus/.claude/plans/playful-pondering-rabbit.md` e execute APENAS as tarefas T10 a T15 (Fase 1). Crie estes 6 arquivos exatamente como especificado:
  >   1. `/Users/jesus/.claude/skills/enviar-tarefas-em-andamento/SKILL.md` (frontmatter rico + ≥10 aliases + workflow 6 passos)
  >   2. `/Users/jesus/.claude/skills/enviar-tarefas-em-andamento/templates/checkpoint-template.md` (12 secoes)
  >   3. `/Users/jesus/.claude/skills/enviar-tarefas-em-andamento/helpers/criar_checkpoint.py` (CLI: `--tema --slug [--prioridade] [--working-dir] [--dry-run]`, stdin JSON, slugify ASCII strict, nome `YYYY-MM-DD_HHMM__<slug>.md`, atualiza `_INDICE.md`, append em `TASKS_NOW.md` na secao `## Tarefas pausadas (checkpoints)`)
  >   4. `/Users/jesus/.claude/skills/enviar-tarefas-em-andamento/README.md` (doc humana)
  >   5. `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/tarefas-em-andamento/_README.md`
  >   6. `/Users/jesus/Desktop/STEMMIA Dexter/Maestro/tarefas-em-andamento/_INDICE.md` (header tabular)
  >
  > Para cada arquivo, rode o comando de verificacao especificado em "Output esperado" e cole o output literal. NAO toque em `~/.claude/CLAUDE.md` (e Fase 2). NAO ative a skill. Reporte ao final: arquivos criados (ls -la), saida das verificacoes, exit codes do helper em --dry-run com JSON minimo.

### Time B — Banco laudos (Fase 0 do plano A)
- **Subagente:** `general-purpose`
- **Modelo:** Opus 4.7
- **Tarefa:** Executar T00, T01 e T02 do `~/.claude/plans/populacao-banco-laudos-mg.md`
- **Briefing self-contained:**
  > Voce e um agente executor. Leia o plano em `/Users/jesus/.claude/plans/populacao-banco-laudos-mg.md` e execute APENAS a Fase 0 (T00 + T01 + T02). Trabalhe em modo READ-ONLY exceto pelos 2 arquivos que voce DEVE criar:
  >   - `/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/Banco-Transversal/Honorarios-Periciais/_INVENTARIO-BASELINE-2026-04-23.json` (T00 — inventario quantitativo dos PDFs ja baixados, agrupado por comarca/tipo de pericia/instancia)
  >   - `/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/Banco-Transversal/Honorarios-Periciais/anel_geografico.json` (T01 — 853 comarcas MG mapeadas em 8 aneis a partir de GV; usar IBGE 2022; cada entry: `{"comarca": "...", "anel": 1..8, "distancia_km": int, "tribunal_competente": "TJMG|TRF6"}`)
  >
  > NAO baixe novos PDFs. NAO toque em scripts existentes (baixar_tjmg_v3.py etc — apenas leia para entender output format). NAO toque em `data/` ou `MUTIRAO/`.
  >
  > Reporte ao final: contagens (PDFs por comarca, comarcas por anel), validacao JSON com `python3 -m json.tool`, e o relatorio T02 em texto seco com top-5 comarcas com mais material e top-5 com lacunas.

### Time C — Smoke test (sequencial, SO depois do CKPT1 do Time A)
Despachar so apos Dr. Jesus aprovar com "ok CKPT1":
- **Subagente:** `general-purpose`
- **Tarefa:** T20 (adicionar bloco no CLAUDE.md global) + T21 (smoke trigger semantico) + T22 (smoke helper standalone com JSON do exemplo do plano).

### Regras de coordenacao para os times paralelos
- Time A toca SO em `~/.claude/skills/enviar-tarefas-em-andamento/` + `Maestro/tarefas-em-andamento/`. Time B toca SO em `banco-de-dados/Banco-Transversal/Honorarios-Periciais/`. Zero overlap → seguro paralelizar.
- Cada time entrega relatorio estruturado: arquivos criados, comandos de verificacao + output, contagens. Sem prosa motivacional.
- Limite de retries por tarefa: 2. Falhou 2x → parar e diagnosticar.
- Anti-mentira: NUNCA declarar "feito/pronto/funcionando" sem colar output literal de comando.

## Como retomar (prompt copy-pasteable para nova sessao)

```
Continua o trabalho pausado em:
/Users/jesus/Desktop/STEMMIA Dexter/Maestro/tarefas-em-andamento/2026-04-23_0121__expansao-banco-laudos-e-skill-checkpoint.md

Le esse arquivo + os 2 planos referenciados. Despacha Time A (Fase 1 do plano B) e Time B (Fase 0 do plano A) em paralelo num unico turno. Aguarda ambos terminarem antes de pedir CKPT. Anti-mentira ativo: cada output verificavel.
```

## Historico de pausas

| Data | Hora | Por que pausou | Quem pausou |
|------|------|----------------|-------------|
| 2026-04-23 | 01:21 | Pedido explicito do user "me da o contexto e um plano de acao com agentes em time em paralelo para continuar em outra sessao" | Dr. Jesus |
