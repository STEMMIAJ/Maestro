---
name: Obsidian e Notion — definições simples
description: Definição em linguagem direta de Obsidian/Notion para usuário com TEA+TDAH+anomia. Recomendação: Obsidian para a prática pericial.
type: reference
originSessionId: 11924f1d-2075-435c-82ab-62f52b3897c2
---
## Obsidian
- O que é: programa que guarda notas em arquivos `.md` (markdown = texto puro com formatação) numa pasta do computador chamada "vault".
- Onde: você escolhe a pasta, exemplo `~/Documentos/Obsidian-Pericia/`
- Diferencial: notas se LIGAM entre si com `[[nome-da-nota]]`, formando rede visual.
- Custo: GRÁTIS para uso pessoal.
- Online?: NÃO por padrão (offline). Sync = US$4/mês opcional.
- Plugin Claude Code MCP existe: https://github.com/iansinnott/obsidian-claude-code-mcp

## Notion
- O que é: programa de notas + banco de dados, hospedado na nuvem da Notion.
- Onde: tudo no servidor deles, acesso por navegador/app.
- Diferencial: tabelas relacionais embutidas (tipo Excel + Word junto).
- Custo: free OK para pessoa física, planos pagos US$8+/mês.
- Online?: SIM sempre. Funciona offline parcial.
- Acesso celular: SIM, app oficial.

## Recomendação para Dr. Jesus (médico perito autista+TDAH+anomia)
**OBSIDIAN.** Motivos técnicos:
1. Dados no controle dele (pasta local, sem servidor de terceiros)
2. Funciona offline (importante em fórum sem wifi)
3. Já existe plugin `obsidian-skills` instalado no sistema
4. Markdown integra direto com o resto do workflow (laudos já são MD)
5. Sem mensalidade
6. Plugin Claude Code MCP permite Claude ler/escrever notas direto

**Estrutura proposta da vault:**
```
~/Documentos/Obsidian-Pericia/
├── Processos/        ← uma nota por processo (5001234-89.2026.md)
├── Conhecimento/     ← CIDs, súmulas, escalas, jurisprudência
├── Templates/        ← modelos de laudo, quesitos, aceite
├── Diário/           ← log diário
└── _index.md         ← mapa visual
```
