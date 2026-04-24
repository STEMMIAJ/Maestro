---
name: MCPs jurídicos instalados
description: MCP Brasil (326 tools, DataJud+STF+STJ), PJe MCP (acesso PJe com certificado A1), N8N MCP, escavador (pip)
type: reference
---

## MCPs jurídicos (instalados 06/abr/2026)

### mcp-brasil (PRINCIPAL)
- **Pacote**: `uvx --from mcp-brasil python -m mcp_brasil.server`
- **O que faz**: 326 ferramentas, 41 APIs públicas brasileiras
- **Jurídico**: DataJud (processos, movimentações), STF, STJ, TST (jurisprudência, súmulas)
- **Grátis**: sim, APIs públicas do governo
- **Variáveis opcionais**: `DATAJUD_API_KEY` (portal DataJud CNJ), `TRANSPARENCIA_API_KEY`
- **Status**: registrado em ~/.claude.json (project /Users/jesus)

### pje-mcp (COMPLEMENTAR)
- **Pacote**: node ~/stemmia-forense/tools/pje-mcp/build/index.js
- **O que faz**: acesso direto ao PJe com certificado digital A1/A3
- **Tribunais**: TJCE, TRF5, TJMG, TJSP, TJRJ
- **Requer**: certificado digital PFX + URL do tribunal
- **Status**: registrado em ~/.claude.json, build em ~/stemmia-forense/tools/pje-mcp/

### Pacotes pip instalados
- `escavador 0.11.2` — busca por CPF/nome em todos os tribunais (R$0,10/processo)
- `busca-processos-judiciais` (npm) — API pública CNJ

### Como listar TODOS os processos
Nenhuma API filtra "processos onde sou perito" diretamente. Combinar:
1. AJ TJMG (consultar_aj.py --listar --json) — estadual
2. AJG CJF (consultar_ajg.py --listar --json) — federal
3. Escavador (busca por CPF) — todos os tribunais, pago
4. DataJud via mcp-brasil — enriquecer com movimentações
