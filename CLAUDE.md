# STEMMIA Dexter

Repositório central do sistema pericial do Dr. Jesus Eduardo Noleto de Souza, perito médico judicial em Governador Valadares/MG.

---

## 🔒 REGRAS MAESTRO — LER ANTES DE QUALQUER AÇÃO EM Maestro/

> Obrigatório ler ANTES de criar, mover, renomear ou deletar qualquer arquivo dentro de `~/Desktop/STEMMIA Dexter/Maestro/`.
> Repo oficial: https://github.com/STEMMIAJ/Maestro

### R0 — Ler primeiro
Rodar `cd ~/Desktop/STEMMIA\ Dexter/Maestro && cat CHARTER.md RULES.md WORKFLOW.md DEFINITION_OF_DONE.md` antes de tocar em qualquer coisa.

### R1 — Uma issue por sessão
`gh issue list --repo STEMMIAJ/Maestro --state open` → escolher 1. Sem issue = sem trabalho.

### R2 — Nada fora do Maestro
Todo código/doc criado nesta sessão vai DENTRO de `~/Desktop/STEMMIA Dexter/Maestro/`. Proibido criar em `~/Desktop/`, raiz do Dexter, `_MESA/`.

### R3 — Commit a cada etapa
Cada arquivo novo/alterado vira commit imediato. Mensagem: `tipo(escopo): frase curta`.

### R4 — Definition of Done é binário
Tarefa só é "DONE" com os 5 itens: código commitado + teste passou (output colado) + CHANGELOG atualizado + issue fechada com `Closes #N` + push verde. Sem os 5 → não dizer "feito".

### R5 — Trava 2× = vira issue blocker
Falhou 2 vezes seguidas → criar issue com label `blocker`, parar, não contornar.

### R6 — Sem limpeza sem autorização
Proibido `rm`, `rm -rf`, `mv para /tmp`, renomear em massa. Exceção: usuário escreve `LIMPAR-LIBERADO` na mensagem.

### R7 — Fim de sessão sempre escreve handoff
`bash scripts/finalize.sh` cria `HANDOFFS/HANDOFF-YYYY-MM-DD-HHhMM.md` com: issue trabalhada, commits, estado (DONE/BLOCKED/PAUSED), próximo passo.

### R8 — ADR antes de decisão grande
Framework novo, schema, deletar módulo → criar `DECISIONS/ADR-NNNN-titulo.md` ANTES de implementar.

### R9 — Claude decide ou para
Faltou contexto → PARAR e fazer 1 pergunta objetiva. Proibido: "vou assumir", "deve ser", "tentar".

### R10 — Usuário tem TEA+TDAH
Resposta máx 3 linhas entre ações. Zero bajulação. Termo técnico → 1 frase + exemplo.

**Regras 100% declaradas em:** `Maestro/RULES.md`, `Maestro/WORKFLOW.md`, `Maestro/DEFINITION_OF_DONE.md`, `Maestro/CLAUDE.md`, `Maestro/docs/politica/POLITICA-SALVAMENTO.md`.

### Comandos prontos para colar em QUALQUER sessão

**Abrir sessão Maestro:**
```bash
cd "/Users/jesus/Desktop/STEMMIA Dexter/Maestro" && bash scripts/status.sh
```

**Salvar trabalho no GitHub agora:**
```bash
cd "/Users/jesus/Desktop/STEMMIA Dexter/Maestro"
git status
git add -A
git commit -m "tipo(escopo): descrição"
git push
```

**Encerrar sessão (sempre):**
```bash
cd "/Users/jesus/Desktop/STEMMIA Dexter/Maestro"
bash scripts/finalize.sh
# preencher o handoff criado, depois:
git add -A && git commit -m "chore(handoff): sessão $(date +%Y-%m-%d)" && git push
```

**Ver plano e documentação pro leigo:**
- `Maestro/docs/github/01-EXPLICACAO-LEIGA.md` — git explicado sem jargão
- `Maestro/docs/github/02-COMO-SALVAR.md` — quando/como salvar
- `Maestro/docs/github/03-FLUXO-VISUAL.md` — diagrama do fluxo
- `Maestro/docs/github/04-GLOSSARIO.md` — cola de palavras
- `Maestro/docs/politica/POLITICA-SALVAMENTO.md` — regras de commit/push

### Site público (stemmia.com.br)

Pasta `stemmia.com.br/maestro/` hospeda os mesmos 4 guias leigos (cópia espelhada). Útil para o Dr. Jesus consultar pelo celular/iPad sem abrir o Mac. Atualização via FTP deploy quando os guias mudam.

---

## Regras
1. SEMPRE ler memoria/MEMORIA.md no início da sessão
2. EXECUTAR DIRETO — não perguntar "posso executar?"
3. Português brasileiro, sem formalidades excessivas
4. Mostrar o que está fazendo, não apenas o resultado
5. NUNCA inventar dados de processos — se não tem, deixar em branco
6. NUNCA versionar PDFs, DOCXs, ou dados de pacientes
7. NUNCA apagar arquivo sem dupla confirmação
8. NUNCA dizer que algo foi feito sem verificar
9. NUNCA dizer que algo foi corrigido sem testar
10. NUNCA começar por site, Obsidian ou painel se houver processo pendente
11. Não depender da memória do Claude: salvar decisões e rotinas em arquivo

## Estrutura
- src/ — código fonte (pipeline, petições, honorários, pje, jurisprudência)
- memoria/ — sistema de memória persistente (também vault Obsidian)
- agents/ — agentes de perícia organizados por cluster
- skills/ — skills Claude Code
- templates/ — modelos de documentos (laudo, petição, roteiro)
- referencias/ — base pericial (escalas, protocolos, checklist)
- hooks/ — hooks Claude Code
- n8n/ — workflows N8N exportados
- docs/ — documentação do sistema
- painel/ — dashboards HTML
- data/ — dados (NÃO VERSIONADO)

## Paths externos
- Processos: ~/Desktop/ANALISADOR FINAL/processos/
- PDFs PJe: ~/Desktop/processos-pje-windows/
- Perícias: ~/Desktop/PERÍCIA/
- Scripts legados: ~/Desktop/ANALISADOR FINAL/scripts/

## Prioridade
1. Processos judiciais reais e prazos
2. Petições, laudos, respostas a quesitos
3. Organização mínima para executar
4. Configurações, site, Obsidian e estética

## Leitura obrigatória no início da sessão
- memoria/MEMORIA.md
- memoria/DECISOES.md
- 00-CONTROLE/AGORA.md
- 00-CONTROLE/PROTOCOLO-CLAUDE-CONSISTENTE.md quando a tarefa envolver Claude, contexto, produtividade, recusa, lentidão ou comportamento inconsistente

Se algum arquivo não existir, criar.

## PROCESSOS
Cada processo deve terminar neste formato:

```text
~/Desktop/ANALISADOR FINAL/processos/CNJ/
├── PDFs/
├── TEXTO-EXTRAIDO.txt
├── FICHA.json
└── URGENCIA.json
```

Primeiro triagem de urgência. Depois análise. Depois laudo ou petição.

## INSTAGRAM
Não tentar acessar conta privada automaticamente.
Aceitar apenas link público, print, texto copiado ou arquivo fornecido.

Entrada:
```text
~/Desktop/STEMMIA Dexter/INBOX/instagram/links.md
~/Desktop/STEMMIA Dexter/INBOX/instagram/prints/
```

Saída processada:
```text
~/Desktop/STEMMIA Dexter/BANCO-DADOS/TI e IA/Claude/
```

Cada conteúdo útil deve virar nota Markdown com: título, link original, resumo, aplicação prática, comandos se houver, riscos e tags.

## Após cada sessão importante
Atualizar memoria/MEMORIA.md com estado atual e pendências.
Se houve decisão arquitetural, registrar em memoria/DECISOES.md.

## ENFORCEMENT DE PLANOS (obrigatório, sem exceção)

Todo plano novo criado em `~/.claude/plans/` **OU** em `STEMMIA Dexter/00-CONTROLE/` deve seguir **exatamente** o formato de `STEMMIA Dexter/00-CONTROLE/TEMPLATE-PLANO.md`.

Regras:
1. Plano sem os 11 blocos do template → **rejeitado** antes de executar.
2. Tarefa sem "Output esperado" verificável (regex, contagem, diff, texto literal) → **proibida**.
3. Fase sem tarefa `CKPT<N>` (checkpoint explícito) → **proibida**. Claude NÃO inicia próxima fase sem aprovação explícita do Dr. Jesus ("ok fase N+1").
4. Plano sem bloco "Princípios não-negociáveis" literal → **rejeitado**.
5. Plano sem tabela de Riscos (mínimo 3 com mitigação) e sem "Rollback por fase" → **rejeitado**.
6. Plano que ultrapassa 2h numa fase sem subdividir → **rejeitado**.
7. Afirmação no plano sobre existência de arquivos/scripts sem grep/ls recente como evidência → **rejeitada**.

Se o Dr. Jesus identificar um plano fora do padrão: reescrever no template — NÃO executar o plano fora do padrão.

Documento completo: `STEMMIA Dexter/00-CONTROLE/TEMPLATE-PLANO.md`.

<!-- GSD:project-start source:PROJECT.md -->
## Project

**Sistema Pericial Stemmia — Integração Final**

Hub central do ecossistema de perícia médica judicial do Dr. Jesus. Sistema BROWNFIELD com 5 anos de acumulação: 64 scripts Python funcionais, 85 agentes Claude especializados, 17 MCPs, 25 plugins, 5 workflows N8N, 7 hooks. Tudo funciona ISOLADO; nada está integrado num fluxo único.

**Esta iniciativa NÃO cria coisas novas.** Faz a **cola** entre o que já existe + popula o banco de dados (vazio na prática, 12 arquivos em 100 pastas estruturadas) + cria UM ponto de entrada operacional.

**Core Value:** **O ÚNICO comportamento que precisa funcionar:**
Dr. Jesus digita `/perícia [CNJ]` e o sistema dispara TUDO sequencialmente sem ele precisar lembrar qual script chamar: download → análise leve → análise profunda → busca no banco → geração de petição → verificação → entrega.

Tudo o resto é secundário.

### Constraints

- **Tempo do usuário:** mínimo (sobrecarga, autismo, TDAH). Cada interação custa.
- **Hardware:** Mac M-series, 16GB+ RAM. Roda local. PJe SÓ no Windows/Parallels.
- **Modelos:** Opus 4.7 obrigatório (CLAUDE_CODE_SUBAGENT_MODEL).
- **MCPs caídos:** playwright, browser-mcp — NÃO usar nesses MCPs nesta iniciativa.
- **Permissões:** Bash(*), Edit(*), Write(*), WebFetch(*), WebSearch — zero fricção.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->
## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
