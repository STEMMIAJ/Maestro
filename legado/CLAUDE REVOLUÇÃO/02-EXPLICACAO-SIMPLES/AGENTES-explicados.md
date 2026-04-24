# AGENTES — o que são, como funcionam

## O que é (1 frase)
Agente = uma instância nova do Claude que recebe UMA tarefa, executa, devolve resultado, morre.

## Por que existe
Para isolar tarefas pesadas (busca em código, leitura de muitos arquivos) e não poluir o contexto da nossa conversa.

---

## Onde ficam
- Globais: `~/.claude/agents/[nome-do-agente].md`
- Plugin: `~/.claude/plugins/[plugin]/agents/[nome].md`

Você tem **76 agentes próprios** (criados ao longo do tempo).

---

## Como funciona na prática

```
[Você] "busca jurisprudência sobre invalidez parcial"
   ↓
[Claude principal] decide: "vou usar o agente Buscador em Tribunais"
   ↓
[Claude principal] chama Agent({subagent_type: "Buscador em Tribunais", prompt: "..."})
   ↓
[Agente novo] roda em sessão separada, faz buscas, gera relatório
   ↓
[Agente novo] devolve resultado em texto
   ↓
[Claude principal] lê o resultado e te entrega resposta
```

**Critico:** o agente NÃO vê nossa conversa. Você precisa explicar o contexto no `prompt`.

---

## Estrutura de um agente

```markdown
---
name: Nome do Agente
description: O que faz, quando usar (com exemplos)
tools: Read, Grep, Bash
---

# Instruções para o agente

Você é especialista em X.
Quando receber tarefa, faça:
1. Passo um
2. Passo dois
3. Devolva no formato Y
```

---

## Diferença Agente vs Skill vs Hook

| | Hook | Skill | Agente |
|---|------|-------|--------|
| Quando dispara | Evento (Stop, PreToolUse) | Quando relevante na conversa | Quando eu chamo `Agent()` |
| Roda como | Código bash/python | Texto no contexto | Sessão Claude separada |
| Vê nossa conversa | Sim (recebe o JSON) | Sim (texto carregado) | Não (recebe só prompt) |
| Custa tokens | Quase nada | Carrega no contexto | Roda como sessão nova (caro) |
| Usar quando | Forçar comportamento | Orientar tema | Tarefa pesada/isolada |

---

## Quando vale chamar agente

✅ **VALE:**
- Buscar em código grande (poderia poluir contexto)
- Análise paralela (vários agentes ao mesmo tempo)
- Tarefa especializada (jurisprudência, médico, perícia)
- Trabalho que pode rodar em background

❌ **NÃO VALE:**
- Tarefa simples (ler 1 arquivo)
- Algo que precisa do contexto da conversa
- Quando a resposta é rápida e direta

---

## Seus agentes principais (por categoria)

### Petição
- `Triador de Petição` — classifica tipo a partir de print
- `peticao-identificador` — identifica subtipo
- `peticao-extrator` — extrai dados do processo
- `peticao-montador` — preenche template
- `peticao-verificador` — confere CNJ, IDs, gênero
- `peticao-gerador-pdf` — converte MD → PDF
- `Gerador de Petição Simples/Médio/Complexo` — geram texto
- `Padronizador de Estilo` — aplica seu estilo

### Análise
- `Orquestrador de Análise Rápida` — 4 sub-agentes em paralelo
- `Orquestrador de Análise Completa` — 8 sub-agentes em paralelo
- `Resumidor de Fatos`
- `Mapeador de Provas`
- `Analisador de Quesitos Automático`

### Verificação (anti-erro material)
- `Verificador de CIDs` (compara com tabela DataSUS)
- `Verificador de Datas`
- `Verificador de Nomes e Números`
- `Verificador de Medicamentos e Dosagens`
- `Verificador de Exames e Anexos`
- `Detetive de Inconsistências` (cruza versões)

### Pesquisa
- `Buscador em Tribunais` (STJ/STF/TST/TJMG/TRF6/TRT3)
- `Buscador Acadêmico` (PubMed, SciELO)
- `Buscador na Base Local` (Whoosh, 196 docs)
- `Orquestrador de Jurisprudência`

### Laudo
- `Redator de Laudo Pericial`
- `Revisor de Laudo Pericial`
- `Buscador Acadêmico`

---

## Como chamar agente em paralelo (rápido)

```python
# Em uma única mensagem do Claude principal:
Agent(subagent_type="Verificador de CIDs", prompt="...")
Agent(subagent_type="Verificador de Datas", prompt="...")
Agent(subagent_type="Verificador de Nomes", prompt="...")
```

Os 3 rodam ao mesmo tempo. Resultado em ~30s em vez de 90s.

---

## Custo

- Cada agente é uma sessão nova de Claude.
- Consome tokens próprios (entrada + saída).
- Por isso: agente para tarefa que VALE A PENA isolar.

---

## Problemas conhecidos

| Sintoma | Causa | Solução |
|---------|-------|---------|
| Agente devolve nada | Prompt vago | Dar contexto + formato esperado |
| Agente erra task | Pegou agente errado | Verificar `description` correto |
| Agente repete trabalho | Não sabe o que já foi feito | Passar histórico relevante no prompt |
| Agente lento | Tarefa muito grande | Quebrar em sub-tarefas paralelas |

---

## Você decide o modelo (importante)

Sua memória `feedback_tudo_opus.md` registra: TODOS os agentes rodam **Opus**.

Variável de ambiente: `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-7`

NUNCA rebaixar para Sonnet/Haiku sem você autorizar.
