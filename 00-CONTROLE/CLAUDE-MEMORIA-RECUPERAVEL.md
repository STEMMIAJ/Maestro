# CLAUDE — Memória Recuperável

Data: 2026-04-14.

# Veredito

Sim: Claude Code salva muitos rastros locais.

Não é uma memória perfeita que ele relê sozinho em toda sessão.
Mas é reaproveitável.

# Fontes encontradas

```text
~/.claude/plans
```

- 118 arquivos Markdown.
- Tamanho aproximado: 1,0 MB.
- Conteúdo: planos do UltraPlan e agentes.
- Uso: muito útil para recuperar decisões, arquitetura, tarefas propostas e raciocínios já feitos.
- Limitação: não é conversa completa.

```text
~/.claude/projects
```

- 3915 arquivos.
- Tamanho aproximado: 1,3 GB.
- Conteúdo: sessões em JSONL, subagentes, resultados de ferramentas e arquivos auxiliares.
- Uso: fonte principal para recuperar conversas e trabalhos.
- Limitação: grande, sensível e barulhento.

```text
~/.claude/sessions
```

- 8 arquivos JSON.
- Tamanho aproximado: 32 KB.
- Uso: metadados de sessões.

```text
~/.claude/todos
```

- 352 arquivos.
- Tamanho aproximado: 1,4 MB.
- Uso: tarefas internas, checklists e estados.

```text
~/.claude/file-history
```

- 898 arquivos.
- Tamanho aproximado: 10 MB.
- Uso: histórico de arquivos tocados.

```text
~/.claude/history.jsonl
```

- 1836 linhas.
- Tamanho aproximado: 588 KB.
- Uso: histórico geral.

```text
~/.claude/knowledge-graph.jsonl
```

- 25 linhas.
- Uso: conhecimento estruturado pequeno.

```text
~/.config/superpowers
```

- 1843 arquivos encontrados no primeiro nível analisado.
- 2539 arquivos `.jsonl`.
- Tamanho aproximado: 1,2 GB.
- Contém `conversation-archive` e `conversation-index/db.sqlite`.
- Uso: provavelmente o melhor acervo para reaproveitar conversas antigas.

```text
~/.config/superpowers/conversation-index/db.sqlite
```

- Banco SQLite encontrado.
- Tabela principal: `exchanges`.
- Total indexado: 4816 trocas.
- Período: 2026-03-11 a 2026-04-14.
- Campos úteis:
  - `timestamp`
  - `user_message`
  - `assistant_message`
  - `archive_path`
  - `line_start`
  - `line_end`
  - `project`
  - `session_id`

# Contagem por tema no índice SQLite

```text
codex:      20 trocas
stemmia:   899 trocas
dexter:    93 trocas
memória:   383 trocas
processo:  1289 trocas
perícia:   967 trocas
PJe:       832 trocas
```

# Achado importante

Arquivo citado dentro de sessão do Claude:

```text
~/.config/superpowers/conversation-archive/-Users-jesus/91adf3a1-062a-4c1b-b227-016788bdc737.jsonl
```

- Tamanho: aproximadamente 714 KB.
- Linhas: 404.
- Conteúdo provável: pesquisa grande sobre Codex CLI.
- Status: fonte reaproveitável.
- Confirmado no SQLite: contém a pesquisa principal sobre Codex entre as linhas 8 e 398.

# Como reaproveitar

Não jogar tudo no Obsidian agora.
Não hospedar.
Não copiar tudo para site.

Fazer em etapas:

1. Buscar por tema nos acervos:
   - `processo`
   - `perícia`
   - `stemmia`
   - `dexter`
   - `memória`
   - `codex`
   - `claude`
   - `PJe`
   - `laudo`

2. Para cada tema, extrair:
   - decisão operacional;
   - comando útil;
   - caminho de arquivo;
   - script citado;
   - erro já resolvido;
   - plano ainda válido.

3. Salvar resultado limpo em:

```text
~/Desktop/STEMMIA Dexter/CONVERSAS/claude-code/recuperado/
```

4. Transformar só o que for estável em:

```text
~/Desktop/STEMMIA Dexter/DECISOES.md
~/Desktop/STEMMIA Dexter/ROTINA.md
~/Desktop/STEMMIA Dexter/BANCO-DADOS/
```

# Regra de segurança

Esses arquivos podem conter:

- dados de processos;
- nomes de partes;
- documentos;
- caminhos locais;
- chaves ou tokens referenciados;
- estratégia jurídica/pericial.

Portanto:

- não hospedar;
- não mandar para site;
- não sincronizar publicamente;
- não colar tudo em IA sem filtragem.

# Decisão

A memória do Claude existe como arquivo local.
A prioridade agora é transformar esse acervo em memória limpa e curta.

Mas a triagem dos PDFs judiciais continua sendo prioridade operacional.
