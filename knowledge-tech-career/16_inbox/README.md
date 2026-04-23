---
titulo: Caixa de Entrada — Material Bruto
bloco: 16_inbox
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 16 — Inbox

## Definição do domínio
Caixa de entrada para material bruto aguardando triagem. Tudo que não foi classificado ainda cai aqui: conversas de outras IAs, notas soltas, transcrições de áudio, PDFs colados sem contexto. Objetivo: zero perda de sinal na captação, triagem assíncrona depois.

## Subdomínios
- `raw_conversations/` — exports de ChatGPT, Gemini, Perplexity, Grok (JSON/MD)
- `imported_notes/` — notas soltas (Apple Notes, Obsidian, WhatsApp)
- `transcripts/` — transcrições de áudio/vídeo (Whisper, Otter)
- `to_process/` — já lido, aguardando decisão de destino

## Perguntas que este bloco responde
- Tenho algo não processado sobre tema X?
- Que conversa com outra IA ainda não foi integrada?
- O que entrou hoje/esta semana?

## Como coletar conteúdo
- Export semanal de conversas de IAs em formato cru
- Dump de áudios transcritos
- Cola-e-esquece: qualquer coisa vai para `raw_conversations/` com timestamp
- Pipeline de ingestão (`14_automation/ingestion_pipelines/inbox_to_block.md`) processa e move para bloco-alvo

## Critérios de qualidade
- Arquivo sempre com timestamp (`YYYY-MM-DD_HHMM_titulo.md`)
- Zero filtragem na entrada (princípio: nunca perder sinal)
- Triagem semanal obrigatória (senão vira depósito morto)
- Item processado é movido ou apagado, não duplicado

## Exemplos de artefatos
- `raw_conversations/2026-04-23_1400_chatgpt_carreira_data_saude.md`
- `imported_notes/2026-04_notas_livro_designing_data_intensive.md`
- `transcripts/2026-04-22_audiencia_pje_123456.txt`
- `to_process/2026-04-21_artigo_ia_forense_jama.md`

## Interseções
- `14_automation/ingestion_pipelines` (lê daqui)
- `15_memory/daily` (nota rápida pode ir direto para memory sem passar por inbox)
- Todos os blocos 01–13 (destino final dos itens triados)
- `00_governance` (cadência de triagem semanal)
