---
titulo: Fontes de conversa de IA — formatos típicos
tipo: catalogo_fontes
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
---

# AI Conversation Sources

Catálogo das fontes possíveis de conversas/registros de IA que podem alimentar `16_inbox/raw_conversations/`. Formato típico documentado para que o parser saiba o que esperar.

## 1. ChatGPT (OpenAI export)

- **Como obter**: Settings → Data Controls → Export Data. Email com ZIP.
- **Formato**: ZIP com `conversations.json`, `chat.html`, `message_feedback.json`, `model_comparisons.json`, `user.json`.
- **Esquema `conversations.json`**: array de objetos `{title, create_time, update_time, mapping{node_id: {message{author.role, content.parts[], create_time}}}}`.
- **Particularidade**: mensagens são uma árvore (regenerate cria branches). Linearizar pelo path main → último leaf.

## 2. Claude (Anthropic export)

- **Como obter**: Settings → Privacy → Export Data.
- **Formato**: JSON por conversa, estrutura `{uuid, name, created_at, updated_at, chat_messages: [{sender, text, created_at, attachments}]}`.
- **Particularidade**: artifacts aparecem como mensagens com `content_type` específico. Preservar separado.

## 3. Gemini (Google Takeout)

- **Como obter**: takeout.google.com → selecionar "Bard/Gemini".
- **Formato**: HTML por conversa + metadados JSON. Menos estruturado.
- **Particularidade**: parsing via BeautifulSoup; títulos não são estáveis. TODO testar com export real.

## 4. Perplexity

- **Como obter**: não há export oficial nativo (RESEARCH — verificar em 2026). Hoje: copy/paste manual ou scrape da URL pública.
- **Formato**: Markdown quando copiado; HTML da página quando scraped.
- **Particularidade**: citações numeradas `[1] [2]` apontam para fontes — preservar como referências em `12_sources/`.

## 5. Transcrições Whisper

- **Como obter**: `whisper` local ou API; gera `.txt`, `.srt`, `.vtt`, `.json`.
- **Formato preferido**: `.json` com timestamps por segmento.
- **Particularidade**: sem autor explícito. Atribuir `speaker_0`, `speaker_1` via diarização (TODO — pyannote).

## 6. Obsidian exports

- **Como obter**: pasta `.md` direta ou Obsidian Publish export.
- **Formato**: Markdown com wikilinks `[[nota]]`. Converter para links relativos ao importar.
- **Particularidade**: frontmatter YAML já presente — preservar e mesclar.

## 7. Cursor/Windsurf/Codex CLI histories (RESEARCH)

- TODO verificar se há export estruturado. Atualmente: sessões em `~/.claude/projects/` (JSONL) e `~/.cursor/`.

## Mapeamento fonte → confiança

| Fonte | Evidence level padrão |
|---|---|
| Claude/ChatGPT export | `experiencia` |
| Gemini/Perplexity | `experiencia` (citações de Perplexity viram `inferencia` até validar fonte primária) |
| Whisper (consulta com especialista) | `experiencia` |
| Obsidian (notas próprias) | `experiencia` ou `inferencia` conforme nota |
