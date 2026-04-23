---
titulo: Backlog de importadores futuros
tipo: backlog
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
---

# Future Imports — Backlog

Importadores planejados mas não especificados. Prioridade P1 (proxima onda), P2 (medio prazo), P3 (nice to have).

## P1 — próxima onda

- **Cursor chat history** — `~/Library/Application Support/Cursor/User/workspaceStorage/**/state.vscdb` (SQLite). Extrair prompts + respostas por workspace. TODO mapear schema.
- **Claude Code JSONL sessions** — `~/.claude/projects/<slug>/<sessao>.jsonl`. Já existe, apenas formalizar ingestão para `16_inbox/raw_conversations/claude_code/`.
- **Telegram bot logs** — `@stemmiapericia_bot` (chat_id 8397602236). Exportar via Bot API ou `tdl`; ingerir como conversas com humano.

## P2 — médio prazo

- **Slack/Discord** — se aderir a comunidade pericial/tech, exportar canais relevantes.
- **Email threads** — MBOX do Gmail (Takeout) filtrando por remetentes de interesse (CFM, CNJ, tribunais). Parse com `mailbox` stdlib.
- **Notion export** — Markdown/CSV ZIP. Baixa prioridade (uso migrando para Obsidian).
- **Kagi Assistant / You.com / Copilot** — exports manuais; baixo volume.

## P3 — nice to have

- **Podcasts transcritos** — Whisper sobre episódios selecionados (ex: Lex Fridman, Two Doc Talk), ingestão como notas de aprendizado.
- **YouTube transcripts** — via `youtube-transcript-api`. Saída: Markdown com timestamps.
- **PDFs acadêmicos** — via `pypdf` + `unstructured`. Pipeline diferente (não é conversa). Pode viver em `14_automation/ingestion_pipelines/papers/` (TODO).
- **Git commit messages próprios** — minerar ~/Desktop/STEMMIA Dexter/ para narrativa de evolução. Output: `13_reports/historical/`.

## Critério de priorização

1. Volume de conhecimento recuperável.
2. Custo de implementação (formato estruturado > não-estruturado).
3. PII e risco de vazar dados clínicos/processuais.
4. Frequência de uso real — não importar o que não vai ser consultado.

## TODO transversal

- Política unificada de PII scrubbing **antes** de qualquer ingestão.
- Registro de provenance em `_meta/index.jsonl` padronizado entre fontes.
- Decidir se embeddings ficam no OpenClaw ou em store externo (RESEARCH).
