# STEMMIA Dexter

Repositório central do sistema pericial do Dr. Jesus Eduardo Noleto de Souza, perito médico judicial em Governador Valadares/MG.

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
