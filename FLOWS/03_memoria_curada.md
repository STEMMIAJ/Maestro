# FLOW 03 — Curadoria de MEMORY.md

## Objetivo

Consolidar memórias brutas (`memory/YYYY-MM-DD.md`) no arquivo mestre `MEMORY.md`, eliminando redundâncias, promovendo decisões de longo prazo e mantendo `open_questions` limpo.

## Gatilho

- Automático: ao final do FLOW 01 quando MEMORY.md cresceu >20 linhas.
- Manual: Dr. Jesus diz "curar memória" ou "limpar MEMORY.md".
- Cron semanal: acoplar a J03 (domingo) quando cron ativo.

## Entradas

| artefato | caminho | observação |
|----------|---------|------------|
| Memórias do dia | `memory/YYYY-MM-DD.md` (não curadas) | uma ou mais |
| MEMORY.md atual | `Maestro/MEMORY.md` | alvo de merge |
| open_questions | `reports/conversation_open_questions.md` | lista a limpar |
| RULES/ atual | `RULES/*.md` | destino de novos limites de segurança |

## Passos

1. Listar arquivos `memory/YYYY-MM-DD.md` sem marca "curado em" no rodapé.
2. Para cada arquivo não curado:
   a. Extrair bloco "Decisões de longo prazo" → append em `MEMORY.md` seção correspondente.
   b. Extrair "Limites de segurança novos" → append em `MEMORY.md` + registrar em `RULES/` (arquivo pertinente).
   c. Extrair dúvidas resolvidas → remover de `reports/conversation_open_questions.md`.
3. Deduplicar `MEMORY.md`: agrupar entradas repetidas ou contraditórias, manter a mais recente.
4. Marcar rodapé de cada `memory/YYYY-MM-DD.md` processado: `<!-- curado em YYYY-MM-DD -->`.
5. Logar em `logs/memory_curation.log` (data, arquivos processados, linhas adicionadas).

## Saídas

| artefato | mudança esperada |
|----------|-----------------|
| `MEMORY.md` | delta claro com seção e data |
| `reports/conversation_open_questions.md` | dúvidas resolvidas removidas |
| `memory/YYYY-MM-DD.md` | marca "curado em" no rodapé |
| `logs/memory_curation.log` | entrada nova |

## Falhas conhecidas / Rollback

| falha | sintoma | rollback |
|-------|---------|----------|
| MEMORY.md cresce acima de 2000 linhas | arquivo pesado para context | dividir em `MEMORY_<ano>.md` + manter `MEMORY.md` com último trimestre |
| Deduplicação apaga entrada útil | informação sumiu | restaurar de `_arquivo/backups/` ou git |
| Conflito de seção (2 entradas contraditórias) | ambiguidade | manter as duas com nota `[CONFLITO PENDENTE]`; não resolver automaticamente |
| `open_questions` corrompido | parse falha | abortar passo 2c; não apagar nada |

## Status

- Planejado.
- Primeira curadoria: após segunda conversa ingerida (pendente).
- Automação: script `generate_memory_files.py` parcialmente implementado.
