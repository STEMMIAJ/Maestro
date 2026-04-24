# Fluxo Instagram para Claude

Data: 2026-04-18

## Objetivo

Transformar postagens do Instagram em material útil para Claude, sem instalar coisa desconhecida direto.

## Decisão

Postagem do Instagram não é fonte de instalação. É fonte de triagem.

O fluxo correto é:

1. Capturar link ou print.
2. Salvar no hub.
3. Eu classifico: Skill, MCP, hook, agente, prompt, ferramenta, curso ou referência.
4. Eu procuro fonte oficial, repositório, documentação e risco.
5. Só depois vira nota, prompt operacional, Skill local ou fila de instalação.

## Entrada

Arquivo principal:

```text
/Users/jesus/Desktop/STEMMIA Dexter/INBOX/instagram/links.md
```

Pasta de prints:

```text
/Users/jesus/Desktop/STEMMIA Dexter/INBOX/instagram/prints/
```

Formato mínimo por linha:

```text
2026-04-18 — @perfil — link — motivo
```

Exemplo:

```text
2026-04-18 — @leosoares.ia — https://www.instagram.com/reel/... — avaliar se vira Skill do Claude
```

Se for perfil privado, post salvo interno ou story sem link útil, usar print.

## Lote Grande

Para muitas postagens, não precisa organizar antes.

Cole em blocos de 20 a 50 links no `links.md`.

Se só houver prints, jogue todos na pasta `prints/` com qualquer nome. Eu classifico depois.

## Saída

Conteúdo processado vai para:

```text
/Users/jesus/Desktop/STEMMIA Dexter/BANCO-DADOS/TI e IA/Claude/
```

Arquivos operacionais esperados:

```text
FILA-INSTALACAO-CLAUDE.md
SKILLS-APROVADAS.md
MCPS-APROVADOS.md
DESCARTADOS.md
```

Esses arquivos só devem ser criados quando houver conteúdo real processado.

## Critério de Instalação

Nunca instalar direto por recomendação de postagem.

Antes de instalar, conferir:

1. Fonte oficial ou GitHub real.
2. Instruções de instalação.
3. Dependências `npm`, `pip`, `curl`, `bash`, `postinstall`.
4. Se pede token, senha, cookie, sessão ou permissão ampla.
5. Se altera `~/.claude`, MCP, hooks ou permissões.
6. Se existe benefício claro para processo judicial, laudo, petição, PJe ou automação local.

Se houver risco ou fonte fraca, fica em `DESCARTADOS.md`.

## Claude Web

Para Claude Web, usar Project Knowledge ou Skill customizada.

Claude Projects aceitam documentos na base de conhecimento do projeto.

Custom Skills no Claude Web entram por `Customize > Skills`, com upload de ZIP da pasta da Skill.

## Claude Code

Para Claude Code, Skill é pasta com `SKILL.md`.

Locais possíveis:

```text
~/.claude/skills/NOME/SKILL.md
.claude/skills/NOME/SKILL.md
```

Não criar nesses locais antes de triagem.

## Comando Simples

Abrir a entrada:

```zsh
open "/Users/jesus/Desktop/STEMMIA Dexter/INBOX/instagram/links.md"
open "/Users/jesus/Desktop/STEMMIA Dexter/INBOX/instagram/prints"
```

Depois de colar os links/prints, pedir:

```text
processa os links do Instagram para Claude
```

## Fontes Consultadas

- Meta Help Center: exportação de informações do Instagram pelo Accounts Center.
- Claude Help Center: Projects e Project Knowledge.
- Claude Help Center: uso e upload de Custom Skills.
- Claude Code Docs: Skills por `SKILL.md` e pastas `~/.claude/skills/` ou `.claude/skills/`.
