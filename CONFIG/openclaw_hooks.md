# CONFIG — hooks OpenClaw (planejado)

## Status

**BLOQUEADO** — depende de:
1. Confirmação oficial do Dr. Jesus sobre o que é o OpenClaw.
2. Documentação oficial em `docs/openclaw-official/` ([TODO/RESEARCH]).
3. Sintaxe real de hooks confirmada (não presumida).

OpenClaw v2026.4.21 detectado na sessão 4. 138 processos SQLite. Conversa Perplexity (4440 linhas) intacta.

## Referência de documentação

Após desbloqueio, consultar antes de configurar qualquer hook:

```
Maestro/docs/openclaw-official/          ← baixar após confirmação
Maestro/reports/openclaw_command_map.md  ← mapear sintaxe real
Maestro/reports/openclaw_capabilities_summary.md
```

## Hooks pretendidos

| evento OpenClaw | ação Maestro | destino | sintaxe | status |
|----------------|-------------|---------|---------|--------|
| `pre-commit` | validar nomes de arquivo (sem acentos, espaços, ç) | bloqueia commit com nome ruim | [TODO/RESEARCH] | planejado |
| `post-ingest` | disparar `generate_session_checkpoint.py` | atualiza `TASKS_NOW.md` | [TODO/RESEARCH] | planejado |
| `pre-cron` | checar se dry-run do job passou | evita ativar job sem teste | [TODO/RESEARCH] | planejado |
| `on-error` | logar + notificar Telegram (FLOW 05) | `logs/` + bot Telegram | [TODO/RESEARCH] | planejado |
| `post-phase` | atualizar `CHANGELOG.md` automaticamente | `Maestro/CHANGELOG.md` | [TODO/RESEARCH] | planejado |

## Integração com hooks Claude Code existentes

Os hooks abaixo já estão instalados globalmente e **devem ser preservados**:

| hook | caminho | função | preservar |
|------|---------|--------|-----------|
| anti-mentira | `~/.claude/hooks/bloquear_limpeza.py` | bloqueia rm -rf, mv abusivo | sim — nunca sobrepor |
| medidor-tokens | `~/stemmia-forense/hooks/medidor-tokens-statusline.sh` | statusLine de contexto | sim |

**Regra de coexistência:** hooks OpenClaw devem operar em eventos diferentes dos hooks Claude Code. Se houver sobreposição de evento, o hook Claude Code tem precedência.

## Perfil de modelo para chamadas via OpenClaw

| uso | modelo | justificativa |
|-----|--------|--------------|
| Subagentes do Claude Code | `claude-opus-4-7` | regra global (CLAUDE_CODE_SUBAGENT_MODEL) — não alterar |
| Chamadas API diretas via OpenClaw | Haiku 4.5 (`claude-haiku-4-5-20251001`) | atual para resumos rápidos e baixo custo |
| Validações / parsing | Python puro | sem modelo |
| Síntese e arquitetura | Opus 4 (Claude Code principal) | qualidade máxima |

**Atenção:** Haiku 4.5 é o perfil atual para chamadas em massa pelo OpenClaw. Não ativar mudança de modelo sem ordem explícita do Dr. Jesus.

## Configuração de ambiente (pretendida — não setada)

```bash
# ~/.config/maestro/env.sh (modo 600, fora do git)
# NÃO CRIAR até autorização
export MAESTRO_ROOT="$HOME/Desktop/STEMMIA Dexter/Maestro"
export MAESTRO_LOG_LEVEL=INFO
export OPENCLAW_HOOKS_ENABLED=false   # manter false até desbloqueio
```

## Status atual

- Documentado e planejado.
- Nenhum hook OpenClaw configurado.
- Nenhuma variável de ambiente setada por este projeto.

<!-- atualizado em 2026-04-24 -->
