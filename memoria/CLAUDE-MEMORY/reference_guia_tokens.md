---
name: Guia de Otimização de Tokens
description: Guia completo em ~/Desktop/STEMMIA Dexter/GUIA-OTIMIZACAO-TOKENS.md — 4 níveis de estratégia para reduzir 60-70% do consumo
type: reference
originSessionId: 297a7c90-bfb2-4533-b363-3eaaf0db2e9a
---
Arquivo: `~/Desktop/STEMMIA Dexter/GUIA-OTIMIZACAO-TOKENS.md`

Criado em 16/abr/2026. Contém:
- Diagnóstico real (2B tokens/34 dias, 67K system prompt/turno)
- Nível 1: Config (plugins 56→5, MCPs 17→7, CLAUDE.md limpar, hooks)
- Nível 2: Pré-processamento (OCR, limpeza texto, segmentação peças, resumo)
- Nível 3: Arquitetura (contexto por agente, extração imagens, pipeline otimizado)
- Nível 4: Automação (inbox, auditoria semanal)
- 7 scripts a criar: limpar_texto.py, segmentar_pecas.py, resumir_processo.py, extrair_imagens.py, dispatch_agente.py, pipeline_otimizado.py, auditar_tokens.py
- Cronograma de 6 dias

**How to apply:** Consultar antes de implementar qualquer otimização de tokens. Seguir o cronograma na ordem (Nível 1 primeiro, impacto imediato).
