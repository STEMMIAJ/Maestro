# MCPs — o que são, como funcionam

## O que é (1 frase)
MCP (Model Context Protocol) = protocolo padronizado que conecta o Claude a sistemas externos (PJe, Linear, Stripe, navegador, etc).

## Analogia simples
USB-C dos modelos de IA. Plugou um servidor MCP, o Claude ganha as ferramentas dele.

---

## Diferença para Hook/Skill/Agente

| | Onde mora | Para que |
|---|-----------|----------|
| Hook | Local, dispara em evento | Forçar comportamento |
| Skill | Local, carrega em tema | Orientar como agir |
| Agente | Local, sessão isolada | Tarefa especializada |
| **MCP** | Servidor externo (local ou remoto) | Conectar a sistema externo |

---

## Onde ficam configurados
`~/.claude.json` (chave `mcpServers`) — geralmente.

Cada MCP é um servidor que roda separado e expõe "tools" para o Claude.

---

## Seus 17 MCPs ativos

### Jurídicos / brasileiros
| MCP | O que faz |
|-----|-----------|
| `pje-mcp` | Consulta processos no PJe (busca, listar, configurar certificado) |
| `mcp-brasil` | Hub com 326 ferramentas do governo brasileiro (Receita, JusBrasil, etc) |

### Pesquisa
| MCP | O que faz |
|-----|-----------|
| `claude_ai_PubMed` | Busca artigos científicos no PubMed |
| `claude_ai_Exa` | Busca semântica na web |
| `claude_ai_Context7` | Documentação oficial de bibliotecas/frameworks |
| `plugin_context7_context7` | Mesmo Context7, instalado via plugin |

### Navegador / scraping
| MCP | O que faz |
|-----|-----------|
| `playwright` | Controla navegador (Chromium/Firefox) |
| `plugin_superpowers-chrome_chrome` | Controla Chrome via DevTools |

### Memória / pensamento
| MCP | O que faz |
|-----|-----------|
| `plugin_episodic-memory_episodic-memory` | Memória de longo prazo (conversas anteriores) |
| `sequential-thinking` | Raciocínio passo-a-passo estruturado |

### Apps que precisam autenticar (você usa pouco)
| MCP | O que faz |
|-----|-----------|
| `claude_ai_Amplitude` | Analytics |
| `claude_ai_Linear` | Gestão de tarefas |
| `claude_ai_Gmail` | Email |
| `claude_ai_Google_Drive` | Drive |
| `claude_ai_Google_Calendar` | Agenda |
| `claude_ai_Stripe` | Pagamentos |
| `mercadolivre` | Catálogo de produtos |

### Outros
| MCP | O que faz |
|-----|-----------|
| `n8n` | Workflows de automação |
| `sentry` | Monitoramento de erros |

---

## Como o Claude usa MCP

```
[Você] "busca o processo 5012345-67.2025.8.13.0024 no PJe"
   ↓
[Claude] vê que tem mcp__pje-mcp__pje_buscar_processo disponível
   ↓
[Claude] chama essa tool com {numero: "5012345-67.2025.8.13.0024"}
   ↓
[Servidor pje-mcp] consulta API do PJe, devolve JSON
   ↓
[Claude] lê o JSON e te responde
```

Diferença do agente: MCP é **uma tool**, o agente é **uma sessão inteira**.

---

## Como uma MCP tool aparece para mim

Schema (um exemplo real):
```json
{
  "name": "mcp__pje-mcp__pje_buscar_processo",
  "description": "Busca processo por número CNJ",
  "parameters": {
    "numero": {"type": "string", "required": true},
    "tribunal": {"type": "string", "required": false}
  }
}
```

Eu chamo igual chamo qualquer tool: passo o JSON, recebo resposta.

---

## Como adicionar MCP novo

### Passo 1 — Achar/escolher o servidor
- Catálogo oficial: `https://github.com/modelcontextprotocol/servers`
- Tipo: Python ou Node.js, geralmente

### Passo 2 — Instalar
```bash
# Exemplo: instalar MCP do GitHub
npm install -g @modelcontextprotocol/server-github
```

### Passo 3 — Configurar em `~/.claude.json`
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_..."
      }
    }
  }
}
```

### Passo 4 — Reiniciar Claude Code
O MCP carrega no startup. Se aparece sem erro, está OK.

### Passo 5 — Testar
"Busca os meus repositórios" → eu uso `mcp__github__list_repos`.

---

## Verificar status dos MCPs
```bash
# No início da sessão, o hook SessionStart já mostra:
# "MCP: 17/17 OK"
```

Se algum estiver `FALHA`, ver log em `~/.claude/logs/`.

---

## Quando vale instalar MCP

✅ VALE:
- Sistema externo que você usa muito (PJe, Drive)
- API que precisa de autenticação cara
- Acesso a dados estruturados (banco, planilha)

❌ NÃO VALE:
- Tarefa que faço com Bash/Web (pesa mais carregar MCP)
- Sistema que você usa 1x por mês
- Coisa experimental ainda quebrando

---

## Custo
MCP local não custa nada. MCP em cloud (claude.ai/*) requer autenticação na conta Anthropic.

---

## Problemas conhecidos

| Sintoma | Causa | Solução |
|---------|-------|---------|
| MCP não responde | Servidor crashou | Reiniciar Claude Code |
| Tool não aparece | `~/.claude.json` mal formatado | Validar JSON |
| Tool falha autenticação | Token expirado | Renovar e atualizar `env` |
| Lentidão no startup | MCPs demais | Desabilitar os não usados |

---

## Sua memória sobre MCPs
- `reference_mcps_juridicos.md` — MCP Brasil + PJe MCP + escavador
- `reference_n8n_server.md` — Servidor N8N self-hosted
- `feedback_n8n_mentira.md` — N8N MCP funciona, parar de dizer que não
