---
titulo: O que é um agente
bloco: 08_ai_and_automation
tipo: fundamento
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: tecnico-consolidado
tempo_leitura_min: 5
---

# O que é um agente

## Definição operacional

Agente = LLM + loop + ferramentas + memória + critério de parada. Diferença fundamental do chat: um chat responde uma vez e para; um agente continua agindo até atingir objetivo ou teto (de iterações, tokens, tempo).

## Loop observar-pensar-agir

Ciclo básico (adaptação de ReAct):

1. **Observar**: ler estado atual (prompt inicial, resultados de ferramentas anteriores, arquivos lidos).
2. **Pensar**: raciocinar sobre qual próxima ação aproxima do objetivo.
3. **Agir**: chamar uma ferramenta (buscar, ler, escrever, executar código) OU emitir resposta final.
4. **Atualizar memória/contexto** com resultado da ação.
5. Voltar a 1 até critério de parada.

Claude Code é exatamente isso. O hook anti-mentira intercepta entre os passos 2 e 3 para validar antes de agir.

## Ferramentas (tools)

Função externa que o LLM pode invocar. Definida por schema (nome, descrição, parâmetros tipados). Exemplos no Dexter:

- `Bash` — executa comando shell.
- `Read` — lê arquivo.
- `Grep` — busca padrão.
- `mcp__pje-mcp__pje_buscar_processo` — consulta PJe.
- `mcp__claude_ai_PubMed__search_articles` — busca PubMed.

O modelo emite chamada em formato JSON/XML; o runtime executa e devolve resultado no próximo turn. Não é o modelo que "executa" — é o harness (Claude Code, SDK, N8N, custom).

## Memória

Três camadas:

1. **Contexto ativo**: janela atual. Volátil, some ao fim da sessão.
2. **Memória de curto prazo**: arquivos de scratchpad (`~/Desktop/_MESA/40-CLAUDE/`), TODOs, diário.
3. **Memória de longo prazo**: base vetorial (embeddings + busca), arquivos versionados, `~/.claude/projects/-Users-jesus/memory/MEMORY.md` (auto-memória).

Agente sem camada 2 ou 3 é um chat glorificado.

## Critério de parada

- Objetivo atingido (modelo emite `final_answer` ou equivalente).
- Teto de iterações (ex.: 50 tool calls).
- Teto de tokens (ex.: 100k consumidos).
- Erro irrecuperável.
- Interrupção humana.

Sem critério de parada = loop infinito caro. Hooks do Dexter impõem limites.

## Chat vs agente

| Dimensão | Chat | Agente |
|----------|------|--------|
| Turnos | Normalmente 1 resposta por input | N ações automáticas por objetivo |
| Ferramentas | Nenhuma ou uma | Várias, escolha dinâmica |
| Memória | Sessão atual | Persistente, estruturada |
| Tempo | Segundos | Minutos a horas |
| Autonomia | Sob controle humano passo a passo | Autônomo dentro de guardrails |
| Custo | Baixo | Alto (N× tokens por objetivo) |
| Falha | Resposta ruim | Ação errada com efeito real |

Perícia usa AMBOS: chat para análise interativa, agente para pipeline automatizado (triagem, download, sumário, primeira redação).

## Tipos de agente

- **Reativo** (ReAct puro): reage a observação a cada passo.
- **Planejador + executor**: primeiro gera plano completo, depois executa. Exemplos no Dexter: `orq-analise-completa`, `gsd-planner` + `gsd-executor`.
- **Multi-agente**: orquestrador distribui subtarefas a especialistas (ver `agentes_no_dexter.md`).
- **Autônomo com loop temporal**: roda em cron (ex.: monitor de processos DJEN 3x/dia).

## Por que agentes falham

- Prompt do agente vago (o role é o mesmo papel de um prompt, mas dura toda a sessão).
- Ferramentas mal descritas (modelo não sabe quando usar).
- Falta de verificação entre passos (agente "concorda consigo mesmo").
- Sem critério de parada claro.
- Memória ruim (reexecuta o que já fez).

## Referências

- Anthropic, "Building effective agents", 2024. [TODO/RESEARCH: URL]
- Schick et al., "Toolformer", 2023.
