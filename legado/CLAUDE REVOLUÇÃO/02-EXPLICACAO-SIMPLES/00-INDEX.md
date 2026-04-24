# 02-EXPLICACAO-SIMPLES — Índice

Cada arquivo aqui explica UMA coisa do seu sistema, como se você nunca tivesse visto.

Estrutura padrão de cada arquivo:
1. **O que é** (1 frase)
2. **Para que serve** (1 frase)
3. **Onde fica no computador** (caminho)
4. **Como rodar** (comando exato)
5. **Raciocínio do começo ao fim** (passo a passo numerado)
6. **Exemplo concreto** (caso real)
7. **O que dar errado pode acontecer** (problemas conhecidos)

---

## Arquivos

| Arquivo | Tópico |
|---------|--------|
| `PJE-baixar_push_pje.md` | Script principal de download de processos |
| `HOOKS-explicados.md` | O que é hook, quando dispara, exemplo dos 7 ativos |
| `SKILLS-explicadas.md` | O que é skill, como o Claude chama, quando usar |
| `AGENTES-explicados.md` | O que é subagente, diferença pra skill, quando vale |
| `MEMORIAS-como-funcionam.md` | Sistema MEMORY.md + ~/.claude/projects/-Users-jesus/memory/ |
| `MCPs-explicados.md` | O que são os 17 MCPs, o que cada um adiciona |

---

## Glossário rápido (vai crescer)

| Termo | Tradução simples | Exemplo |
|-------|------------------|---------|
| **jsonl** | "WhatsApp do Claude" — cada linha = uma mensagem | `11924f1d-...jsonl` tem essa conversa inteira |
| **hook** | "Sentinela" — código que dispara em certo evento | `Stop hook` me bloqueia se eu disser "feito" sem verificar |
| **skill** | "Receita" — instruções que o Claude carrega quando precisa | `comunicacao-neurodivergente` é sua MATRIZ |
| **agente** | "Estagiário especializado" — uma instância nova do Claude pra UMA tarefa | `Explore` busca em código sem poluir nosso contexto |
| **MCP** | "Tomada USB" — protocolo que conecta Claude a sistema externo | `pje-mcp` deixa o Claude consultar o PJe |
| **memória** | "Caderno permanente" — fica entre sessões | `feedback_avisar_recursos_existentes.md` |
| **MEMORY.md** | "Índice do caderno" — lista todas as memórias | sempre carregado no início |
| **settings.json** | "Painel de controle" — configurações do Claude Code | `~/.claude/settings.json` |
| **CLAUDE.md** | "Sua bíblia" — instruções globais | `~/.claude/CLAUDE.md` |
| **slash command** | "Atalho de teclado" — `/comando` aciona algo | `/commit` faz commit semântico |
| **plugin** | "Pacote" — junto: skills + hooks + commands + agentes | `stemmia-forense` é seu plugin principal |
