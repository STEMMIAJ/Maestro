---
titulo: Maestro vs Claude Code vs Git — responsabilidades
tipo: relatorio_governanca
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-23
---

# Maestro vs Claude Code vs Git

Três ferramentas, três papéis. Confundi-las gera retrabalho. Este relatório fixa o contrato.

## Tese

- **Claude Code constrói.** Gera código, Markdown, specs, relatórios, diffs.
- **Maestro (OpenClaw) lembra.** Indexa, busca, promove, revisa memória Markdown.
- **Git preserva.** Versiona estado, permite voltar, serve backup remoto.

Nenhuma das três substitui as outras. Usar Maestro para construir código é perder ferramenta. Usar Claude sem commit é perder trabalho. Usar Git como memória semântica é ingênuo — diff não é busca.

## Tabela — quando usar qual

| Situação | Ferramenta primária | Secundária |
|---|---|---|
| Escrever novo script/README/spec | Claude Code | Git (commit ao fim) |
| "Onde eu tinha anotado X?" | Maestro (`memory search`) | — |
| "Quero ver o que mudou desde quarta" | Git (`git log`, `git diff`) | Maestro para contexto semântico |
| "Importei 300 conversas, preciso promover as relevantes" | Maestro (review queue) | Claude Code (escreve extrações) |
| Backup remoto / recuperação | Git (remote) | — |
| Refatorar código existente | Claude Code | Git (branch) |
| Revisão trimestral de conhecimento | Maestro (knowledge_refresh job) | Claude Code (aplica sugestões) |
| Detectar stale/lacunas de skill | Maestro | Claude Code (redige update) |
| Resolver conflito de versões | Git (merge/rebase) | Claude Code (escreve resolução) |
| "Me explica o que a base diz sobre prompt caching" | Maestro (search + summarize) | Claude Code para expandir |
| Bootstrap de projeto novo | Claude Code | Git (init + remote) |

## Anti-padrões

1. **Usar Maestro para construir.** OpenClaw não gera código de qualidade — ele indexa. Pedir a ele que "crie o script X" desperdiça fluxo.
2. **Usar Claude entre sessões como memória.** Sem Markdown persistido, Claude esquece. Toda decisão relevante precisa virar arquivo, ser indexada pelo Maestro, versionada pelo Git. Caso contrário: déjà vu eterno.
3. **Tratar Git como motor de busca.** `git grep` não acha "ideias parecidas". Maestro sim (semântico).
4. **Commit gigante sem mensagem.** Destrói a capacidade do Git de responder "quando e por quê". Commits atômicos, mensagens em português técnico seco.
5. **Ignorar o Maestro porque o projeto é pequeno.** Pequeno hoje, 2.000 arquivos em 6 meses. Começar indexado evita dívida.
6. **Duplicar memória em múltiplas ferramentas.** Obsidian + Notion + Maestro = três verdades. Aqui a verdade é Markdown no repo; Obsidian é leitor; Notion não participa.

## Contrato operacional

1. Claude Code escreve → salva → Maestro indexa → Git commita.
2. Dúvida factual primeiro tenta `openclaw memory search`. Se não achar, Claude responde + cria nota.
3. Toda nota criada por Claude pertence a um bloco (00–11); pastas 12–16 são suporte/output.
4. Promoção (`16_inbox` → `15_memory/promoted`) é **sempre humana**. Ferramentas sugerem, Jesus aprova.
5. Backup remoto é não-opcional. Sem remote, Git é só undo local.

## Métricas de saúde (TODO medir)

- Tempo médio para achar uma nota antiga via Maestro < 30s.
- % de commits com mensagem >20 caracteres > 95%.
- Arquivos em `16_inbox` > 30 dias sem promoção < 10.
- Dias sem `openclaw memory index` < 2.

## Ver também

- `maestro_operational_model.md`
- `when_to_use_what.md`
