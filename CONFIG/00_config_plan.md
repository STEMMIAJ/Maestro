# CONFIG — plano de configuracao

## Perfis de modelo (estado atual e pretendido)

Ajustar após `reports/model_options_initial.md`. Não alterar sem ordem explícita do Dr. Jesus.

| uso | modelo atual | modelo pretendido | status |
|-----|-------------|------------------|--------|
| Subagentes Claude Code | `claude-opus-4-7` | `claude-opus-4-7` | ativo (global) |
| Claude Code principal | Opus 4 | Opus 4 | ativo |
| Chamadas API diretas via OpenClaw | Haiku 4.5 (`claude-haiku-4-5-20251001`) | [TODO/RESEARCH] | Haiku ativo; escopo a confirmar |
| Resumos rápidos em massa | Haiku 4.5 | Haiku 4.5 | configurável |
| Validações / parsing determinista | Python puro | Python puro | sem modelo |

## Documentação fonte (hierarquia de leitura)

1. `~/.claude/CLAUDE.md` — regras globais (sempre prevalece).
2. `~/Desktop/STEMMIA Dexter/CLAUDE.md` — regras do projeto Dexter.
3. `Maestro/CLAUDE.md` — regras específicas do Maestro.
4. `docs/openclaw-official/` — após confirmação do Dr. Jesus ([TODO/RESEARCH]).
5. `reports/model_options_initial.md` — análise de custo/qualidade (Fase 6).

## Variáveis de ambiente pretendidas

Nenhuma setada por este projeto nesta rodada. Apenas documentação.

| variável | valor pretendido | onde setar | status |
|----------|----------------|-----------|--------|
| `CLAUDE_CODE_SUBAGENT_MODEL` | `claude-opus-4-7` | `~/.claude/settings.json` (global) | já ativa |
| `MAESTRO_ROOT` | `$HOME/Desktop/STEMMIA Dexter/Maestro` | `~/.config/maestro/env.sh` | pretendida |
| `MAESTRO_LOG_LEVEL` | `INFO` | `~/.config/maestro/env.sh` | pretendida |
| `OPENCLAW_HOOKS_ENABLED` | `false` | `~/.config/maestro/env.sh` | pretendida; manter false |

## Credenciais

- **Nunca** armazenar no repo ou em qualquer arquivo versionado.
- Arquivo futuro: `~/.config/maestro/secrets.env` (modo `chmod 600`; fora do `.git`).
- Conteúdo: bot token Telegram, credenciais DB, chave de criptografia de backup.
- Não criar até autorização do Dr. Jesus.

## Paths de configuração do Claude Code (referência)

| arquivo | função | alterado por este projeto |
|---------|--------|--------------------------|
| `~/.claude/settings.json` | permissões, modelo, env vars | não — gerenciado globalmente |
| `~/.claude/CLAUDE.md` | regras globais | não |
| `Maestro/.claude/settings.json` | permissões locais do Maestro | não nesta rodada |
| `Maestro/PERMISSOES.md` | escopo de permissões do Maestro | não nesta rodada |

## Status atual

- Documentado.
- Nenhuma variável setada por este projeto.
- Nenhuma credencial criada.
- Haiku 4.5 é o modelo para chamadas em massa (não ativado nesta rodada).

<!-- atualizado em 2026-04-24 -->
