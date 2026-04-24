---
name: Gemini API Key + N8N IDs
description: Chave Gemini, API Key N8N, IDs dos workflows e hierarquia de modelos com fallback
type: reference
---

## Gemini API Key
`AIzaSyA9Gh9JYW4VEiKVlmCR0ziUD3umK9pJYWQ`

**Onde está:** ~/Desktop/PLUGINS CLAUDE/instalar-tudo.sh (variável CLAUDE_MEM_GEMINI_API_KEY)

## Hierarquia de modelos gratuitos (fallback automático)
1. **gemini-2.5-flash** — 10 RPM, 250 RPD (padrão)
2. **gemini-2.5-flash-lite** — 15 RPM, 1.000 RPD (backup)
3. **gemini-2.5-pro** — 5 RPM, 100 RPD (último recurso)

Quando um modelo retorna 429, o nó Code troca automaticamente e notifica no Telegram.
Quota reseta meia-noite horário do Pacífico.

**NOTA:** gemini-2.0-flash foi descontinuado em março 2026. NÃO usar.

## N8N API Key
Fonte: ~/.claude/.mcp.json → mcpServers.n8n.env.N8N_API_KEY
(JWT com iat 1771507941)

## IDs dos workflows no N8N (atualizado 16/mar/2026)
| Workflow | ID | Endpoint |
|----------|----|----------|
| Aceite Simples | 1puXca03wQSqjTt3 | POST /webhook/aceite-simples |
| Análise + Proposta | KHKFkL7dFI9GAz9b | POST /webhook/analise-proposta |
| Verificador | tDnoxMoWVShC6USh | POST /webhook/verificar |
| Monitor DataJud | (recriando) | Cron domingo 20h |
| Alerta Nomeação | (recriando) | Cron 6h seg-sáb |
| Pesquisador Produtos | 72q2y9SCnUwI442B | — |
| TJMG Extrator | AJpgeL2cDoub-b_3Wo6o0 | — (inativo) |

## Script de atualização
`python3 ~/Desktop/ANALISADOR\ FINAL/scripts/atualizar_modelos_n8n.py --deploy --ativar`
