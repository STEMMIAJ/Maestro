---
name: Pesquisador de Produtos N8N
description: Workflow N8N para buscar produtos em lojas brasileiras com análise estatística via Gemini
type: project
---

## Workflow "STEMMIA Pesquisador Produtos"
- **ID N8N**: 72q2y9SCnUwI442B
- **Status**: Ativo e FUNCIONANDO (testado 2026-04-04)
- **URL**: https://n8n.srv19105.nvhm.cloud
- **Webhook**: POST https://n8n.srv19105.nvhm.cloud/webhook/pesquisar
- **Body**: `{"produto": "nome", "cep": "35020270"}`

## Arquitetura
Webhook → Preparar → Gemini 2.5 Flash → Analisar (estatísticas + parser robusto) → Telegram + Respond

## Correções feitas em 2026-04-04
- Modelo trocado de gemini-2.0-flash (descontinuado) para gemini-2.5-flash
- Cidade corrigida de "Juiz de Fora" para "Governador Valadares MG"
- Parser JSON tornado tolerante a respostas truncadas (regex + brace-matching fallback)
- maxOutputTokens aumentado de 4096 para 8192
- Prompt ajustado de 15-25 para 8-12 resultados

## CEP frete
35020-270 — Governador Valadares/MG

## Bot Telegram
@stemmiacompras_bot (token: 8643368629:AAHeFMpNbfhHAJlAniWZZ8CF2TCu36Q1BRw)

## Lista de compras
Arquivo ativo: ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/STEMMIA/Pessoal/LISTA-COMPRAS.md
NOTA: ~/Desktop/LISTA-COMPRAS.md NÃO EXISTE — referência no plugin precisa ser corrigida

## Pendências remanescentes
- [ ] Google Sheets — precisa configurar credencial OAuth no N8N UI
- [ ] PDF com links clicáveis — salvar em ~/Desktop/Pesquisas Produtos/
- [x] Gemini modelo atualizado para 2.5-flash (2026-04-04)
- [x] Fluxo completo testado e funcionando (2026-04-04)

**Why:** Dr. Jesus precisa comparar preços rapidamente sem pesquisar manualmente em cada loja.
**How to apply:** Usar `/buscar-produto` no Claude ou mandar POST para o webhook.
