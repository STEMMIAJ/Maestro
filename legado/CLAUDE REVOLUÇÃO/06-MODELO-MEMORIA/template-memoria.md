# Modelo de Memória — como o Claude salva e como você lê

## O que é uma memória do Claude (linguagem simples)

Memória = arquivo `.md` que fica em `~/.claude/projects/-Users-jesus/memory/`.

**Diferença para conversa:**
- Conversa (jsonl) = só nessa sessão. Some quando fecha o Claude.
- Memória (md) = sobrevive entre sessões. Carrega no `MEMORY.md` quando abro.

**Quem lê:** o Claude carrega o `MEMORY.md` automaticamente em toda sessão. Memórias específicas eu leio quando relevante.

---

## Estrutura mínima obrigatória

Toda memória PRECISA ter:

```markdown
---
name: Nome curto e específico
description: Uma frase explicando o que tem aqui (vai aparecer no índice)
type: user | feedback | project | reference
---

[Conteúdo aqui]
```

### Tipos (`type`)

| Tipo | Quando usar | Exemplo |
|------|-------------|---------|
| `user` | Algo sobre você (papel, conhecimento, preferência) | "Médico perito CRM-MG 92148, autista" |
| `feedback` | Regra de comportamento que eu devo seguir | "NUNCA escrever sem acentos" |
| `project` | Estado de um projeto em andamento | "Pipeline aceite em construção, fase 3 de 8" |
| `reference` | Informação que eu vou buscar de novo | "Senha FTP é X, host é Y" |

---

## Modelo COMPLETO (com data e contexto)

```markdown
---
name: Nome do que você está salvando
description: O que vai encontrar aqui (1 linha pro índice)
type: feedback
data_criacao: 2026-04-19
data_ultima_revisao: 2026-04-19
contexto_origem: "Sessão de madrugada onde Jésus pediu X"
revisar_em: 2026-05-19  (opcional, se for algo temporal)
---

# Título visível (igual ao name)

## O QUE
[1 frase do que é]

## POR QUÊ (importante para feedback/project)
[Por que isso virou regra/projeto]
Citação direta do usuário: "..."
Data do incidente: 19/abr/2026

## COMO APLICAR
[Quando e como o Claude usa isso]
- Gatilho: "quando o usuário fizer X"
- Ação: "fazer Y"
- Não fazer: "Z"

## EVIDÊNCIA
- Arquivo: `caminho/do/arquivo.py`
- Comando que confirma: `ls -lh /caminho`
- Output esperado: ...

## EXEMPLO CONCRETO
Antes (errado):
> "Sim, claro, vou fazer isso já."

Depois (correto):
> [executa o comando]
> [mostra resultado]
> "Feito: arquivo X criado, 12KB."

## RELACIONADO
- Outras memórias: [link1.md], [link2.md]
- Skill correspondente: ~/.claude/skills/xxx/

## HISTÓRICO DE MUDANÇAS
- 19/abr/2026: criado por Claude após incidente Y
- (futuras revisões aqui)
```

---

## Modelo MÍNIMO (quando você está com pressa)

```markdown
---
name: NomeRapido
description: Frase
type: feedback
---

REGRA: o que é
Why: por que (citação ou data)
How to apply: quando e como
```

---

## Como pedir pro Claude criar memória

Você fala: **"salva isso como memória [tipo]: [conteúdo]"**

Exemplos:
- "salva isso como memória feedback: nunca abrir Chrome do Mac pro PJe"
- "salva isso como memória project: pipeline de aceite começou hoje, fase 3 de 8"
- "salva isso como memória reference: meu telefone do escritório é XXX-XXXX"

Eu confirmo com:
1. Caminho do arquivo criado
2. Linha adicionada no MEMORY.md
3. ls -lh do arquivo

---

## Como você LÊ uma memória

```bash
# Ver lista
cat ~/.claude/projects/-Users-jesus/memory/MEMORY.md

# Ver memória específica
cat ~/.claude/projects/-Users-jesus/memory/feedback_explicar_simples_exemplo.md
```

Ou peça pro Claude: "**me mostra o conteúdo da memória X**".

---

## Sobre Obsidian (já decidido em `reference_obsidian_notion.md`)

**Recomendação ativa:** Obsidian, não Notion.

Motivos:
1. Suas memórias JÁ são markdown — Obsidian abre direto
2. Plugin Obsidian-Claude-Code-MCP existe (`iansinnott/obsidian-claude-code-mcp`)
3. Funciona offline (importante em fórum sem wifi)
4. Sem mensalidade
5. Você controla os arquivos (pasta local)

**Vault sugerido:**
```
~/Documentos/Obsidian-Stemmia/
├── 00-mestre.md           ← lista de tudo, abre primeiro
├── Memorias-Claude/       ← link simbólico para ~/.claude/projects/-Users-jesus/memory/
├── Processos/             ← um arquivo por processo
├── Conhecimento/          ← CIDs, súmulas, escalas
├── Templates/             ← modelos
└── Diario/                ← log diário automático
```

**Para configurar (próxima sessão dedicada, ~30 min):**
1. Baixar Obsidian (grátis em obsidian.md)
2. Criar vault em `~/Documentos/Obsidian-Stemmia/`
3. Symlink: `ln -s ~/.claude/projects/-Users-jesus/memory/ ~/Documentos/Obsidian-Stemmia/Memorias-Claude`
4. Instalar plugin claude-code-mcp dentro do Obsidian
5. Pronto: você vê suas memórias com formatação bonita, links visuais, busca rápida

---

## Backup das memórias

Já incluído no backup de hoje (`~/Desktop/BACKUP CLAUDE/2026-04-19_03h40/02-claude-home/projects/`). Sempre que rodar backup novo, vai junto.

Adicionalmente, você pode subir só as memórias para o site:
```bash
rsync -av ~/.claude/projects/-Users-jesus/memory/ deploy@stemmia.com.br:/teste/memorias/
```
(precisa adicionar `.htaccess` antes — está em `project_camada_seguranca_planner.md`)
