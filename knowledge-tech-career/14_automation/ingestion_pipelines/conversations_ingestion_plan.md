---
titulo: Plano de ingestão de conversas de IA
tipo: spec_pipeline
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
---

# Conversations Ingestion Plan

Importar conversas de ChatGPT, Claude, Gemini, Perplexity (export JSON/HTML) e transcrições Whisper para dentro deste repositório, **sem implementar ainda**. Spec declarativa.

## Estrutura alvo

```
16_inbox/raw_conversations/
  chatgpt/YYYY-MM-DD_<slug>.json        # export original, imutavel
  claude/YYYY-MM-DD_<slug>.json
  gemini/YYYY-MM-DD_<slug>.json
  perplexity/YYYY-MM-DD_<slug>.json
  whisper/YYYY-MM-DD_<slug>.txt
  _meta/
    index.jsonl                         # um registro por conversa ingerida
    hashes.txt                          # sha256 para dedupe
```

Após processamento:

```
15_memory/promoted/<bloco>/
  <YYYY-MM-DD>_<slug>.md                # decisoes/fatos extraidos, com frontmatter
```

## Etapas

### 1. Parse

- Detecta formato por extensão + assinatura (ChatGPT export tem `conversations.json` root array; Claude export tem `conversation` dict).
- Normaliza para **esquema interno**:
  ```yaml
  id: str
  source_tool: chatgpt | claude | gemini | perplexity | whisper
  started_at: iso8601
  ended_at: iso8601
  participants: [user, assistant]
  messages: [{role, ts, text, attachments?}]
  tags: []
  ```

### 2. Dedupe

- Hash sha256 do conteúdo canonicalizado (ordem, whitespace normalizados).
- Consulta `16_inbox/raw_conversations/_meta/hashes.txt`.
- Se existe — log e pula. Se não — registra.

### 3. Extração de decisões/fatos

- Regras heurísticas (TODO refinar):
  - blocos de código → candidatos a snippet
  - linhas começando com "vou", "decidi", "confirmo" → decisão
  - linhas com URL + verbo citativo → fonte
  - menções a nomes próprios (tribunais, classes Python, libs) → entidades
- Saída intermediária: `.extracted.json` adjacente ao raw.

### 4. Promoção para `15_memory/promoted/`

- Humano revisa extrações (`maestro review`).
- Ao aprovar, gera Markdown com frontmatter:
  ```yaml
  titulo:
  tipo: conversa_promovida
  fonte: chatgpt
  data_origem:
  bloco: 02_programming | 08_ai_and_automation | ...
  evidence_level: experiencia
  source_path: 16_inbox/raw_conversations/chatgpt/...
  source_hash:
  ```
- Move para bloco correspondente dentro de `15_memory/promoted/`.

### 5. Indexação

- `openclaw memory index 15_memory/promoted/`.
- Registro em `13_reports/ingestion_logs/YYYY-MM-DD.md`.

## Riscos / TODO

- **PII**: exports podem conter nomes de pacientes/partes. TODO definir scrub obrigatório antes de promover.
- **Volume**: export ChatGPT pode ter milhares de conversas. Processar em lotes.
- **Ambiguidade de bloco**: classificador por keywords; fallback humano.
- **Tokens Whisper**: transcrições longas — TODO definir chunking.

## Não implementar agora

Apenas spec. Implementação futura via script em `~/stemmia-forense/automacoes/ingest_conversations.py` (TODO).
