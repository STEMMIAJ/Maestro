# PROMPT PARA CLAUDE CODE — MEMÓRIA CLAUDE

Você está no Mac do Dr. Jesus, médico perito judicial, TEA/TDAH, com sobrecarga e memória operacional comprometida.

Responda em português brasileiro, com tom técnico, direto e seco.
Faça. Não explique demais. Não apague nada. Não mova nada. Não hospede nada.

# OBJETIVO

Criar dentro do hub:

```text
~/Desktop/STEMMIA Dexter/MEMORIA-CLAUDE/
```

Essa pasta será a memória reaproveitável do Claude Code.

Ela deve:

1. Copiar de forma segura os acervos locais do Claude/Superpowers para dentro do `STEMMIA Dexter`.
2. Criar índice pesquisável de tudo.
3. Atualizar o índice sempre que eu mandar rodar o atualizador.
4. Extrair resumos úteis por tema.
5. Provar com contagens, caminhos e amostras que salvou.
6. Criar plano de ação curto para uso diário.

# FONTES A REAPROVEITAR

Usar estas fontes:

```text
~/.claude/plans
~/.claude/projects
~/.claude/sessions
~/.claude/todos
~/.claude/file-history
~/.claude/history.jsonl
~/.claude/knowledge-graph.jsonl
~/.config/superpowers/conversation-archive
~/.config/superpowers/conversation-index/db.sqlite
```

Não apagar, não mover e não editar as fontes originais.

# ESTRUTURA OBRIGATÓRIA DE SAÍDA

Criar:

```text
~/Desktop/STEMMIA Dexter/MEMORIA-CLAUDE/
├── README.md
├── COMO-USAR.md
├── PLANO-DE-ACAO.md
├── INDICE-GERAL.md
├── INDICE-ARQUIVOS.csv
├── INDICE-CONVERSAS.csv
├── RELATORIO-VALIDACAO.md
├── scripts/
│   ├── atualizar_memoria_claude.py
│   └── buscar_memoria_claude.py
├── originais/
│   ├── claude-plans/
│   ├── claude-sessions/
│   ├── claude-todos/
│   ├── claude-file-history/
│   ├── claude-history.jsonl
│   ├── claude-knowledge-graph.jsonl
│   └── superpowers/
├── extraidos/
│   ├── codex.md
│   ├── pje.md
│   ├── processos.md
│   ├── pericia.md
│   ├── stemmia.md
│   ├── dexter.md
│   ├── memoria.md
│   └── instagram.md
└── logs/
```

# REGRA SOBRE CÓPIA

Fazer cópia local usando ferramenta segura (`rsync` ou `cp -R`).

Antes da cópia:

1. Medir tamanho das fontes com `du -sh`.
2. Medir espaço livre com `df -h`.
3. Registrar isso em `RELATORIO-VALIDACAO.md`.

Se o espaço livre for insuficiente, não copiar tudo.
Nesse caso:

1. Copiar primeiro:
   - `~/.claude/plans`
   - `~/.claude/sessions`
   - `~/.claude/todos`
   - `~/.claude/file-history`
   - `~/.claude/history.jsonl`
   - `~/.claude/knowledge-graph.jsonl`
   - `~/.config/superpowers/conversation-index/db.sqlite`
2. Não copiar `~/.claude/projects` nem `conversation-archive` integralmente.
3. Criar índice apontando para os originais.
4. Explicar objetivamente no relatório.

# ÍNDICE OBRIGATÓRIO

O script:

```text
~/Desktop/STEMMIA Dexter/MEMORIA-CLAUDE/scripts/atualizar_memoria_claude.py
```

deve:

1. Varrer `MEMORIA-CLAUDE/originais/`.
2. Indexar arquivos `.md`, `.txt`, `.json`, `.jsonl`, `.csv`, `.html`, `.xml`.
3. Gerar `INDICE-ARQUIVOS.csv` com:
   - caminho;
   - nome;
   - extensão;
   - tamanho;
   - data de modificação;
   - fonte;
   - quantidade de linhas;
   - termos encontrados.
4. Ler o banco:

```text
~/.config/superpowers/conversation-index/db.sqlite
```

5. Gerar `INDICE-CONVERSAS.csv` com:
   - timestamp;
   - projeto;
   - sessão;
   - caminho do arquivo original;
   - linha inicial;
   - linha final;
   - termos encontrados;
   - trecho da pergunta;
   - trecho da resposta.
6. Gerar `INDICE-GERAL.md` com resumo humano.
7. Gerar arquivos temáticos em `extraidos/`.

# TEMAS OBRIGATÓRIOS

Indexar e extrair:

```text
codex
claude
stemmia
dexter
memória
memoria
processo
processos
perícia
pericia
pje
laudo
petição
peticao
honorários
honorarios
obsidian
instagram
automação
automacao
```

# EXTRAÇÃO TEMÁTICA

Cada arquivo em `extraidos/` deve ter:

```text
# Tema

## Resumo operacional

## Decisões úteis

## Comandos úteis

## Caminhos importantes

## Scripts citados

## Riscos

## Próxima ação recomendada

## Fontes
```

Não copiar conversa inteira para esses arquivos.
Extrair só o que for útil.

# BUSCA

Criar:

```text
~/Desktop/STEMMIA Dexter/MEMORIA-CLAUDE/scripts/buscar_memoria_claude.py
```

Uso:

```bash
python3 ~/Desktop/STEMMIA\ Dexter/MEMORIA-CLAUDE/scripts/buscar_memoria_claude.py pje
python3 ~/Desktop/STEMMIA\ Dexter/MEMORIA-CLAUDE/scripts/buscar_memoria_claude.py codex
python3 ~/Desktop/STEMMIA\ Dexter/MEMORIA-CLAUDE/scripts/buscar_memoria_claude.py processo
```

Saída:

```text
top 20 resultados
arquivo
linha
tema
trecho curto
```

# PROVA OBRIGATÓRIA

No final, provar com comandos e resultados:

```bash
du -sh ~/Desktop/STEMMIA\ Dexter/MEMORIA-CLAUDE
find ~/Desktop/STEMMIA\ Dexter/MEMORIA-CLAUDE -type f | wc -l
wc -l ~/Desktop/STEMMIA\ Dexter/MEMORIA-CLAUDE/INDICE-ARQUIVOS.csv
wc -l ~/Desktop/STEMMIA\ Dexter/MEMORIA-CLAUDE/INDICE-CONVERSAS.csv
ls -lh ~/Desktop/STEMMIA\ Dexter/MEMORIA-CLAUDE
sed -n '1,80p' ~/Desktop/STEMMIA\ Dexter/MEMORIA-CLAUDE/INDICE-GERAL.md
sed -n '1,80p' ~/Desktop/STEMMIA\ Dexter/MEMORIA-CLAUDE/RELATORIO-VALIDACAO.md
```

Também testar buscas:

```bash
python3 ~/Desktop/STEMMIA\ Dexter/MEMORIA-CLAUDE/scripts/buscar_memoria_claude.py codex
python3 ~/Desktop/STEMMIA\ Dexter/MEMORIA-CLAUDE/scripts/buscar_memoria_claude.py pje
python3 ~/Desktop/STEMMIA\ Dexter/MEMORIA-CLAUDE/scripts/buscar_memoria_claude.py processo
```

# PLANO DE AÇÃO

Criar:

```text
~/Desktop/STEMMIA Dexter/MEMORIA-CLAUDE/PLANO-DE-ACAO.md
```

Ele deve conter:

1. Como atualizar a memória.
2. Como buscar assunto.
3. Como transformar achado em decisão.
4. Como transformar achado em rotina.
5. O que não fazer.
6. Próximo passo real: triagem dos PDFs judiciais.

# REGRAS DE SEGURANÇA

- Não hospedar nada.
- Não enviar para site.
- Não apagar nada.
- Não mover nada.
- Não alterar arquivos originais em `~/.claude` ou `~/.config/superpowers`.
- Não expor tokens, senhas, cookies ou chaves.
- Se encontrar segredo, mascarar no índice.
- Se houver erro, registrar no relatório e continuar com o que for seguro.

# EXECUÇÃO

Faça agora, em etapas:

1. Ler os arquivos de memória do hub:

```text
~/Desktop/STEMMIA Dexter/MEMORIA.md
~/Desktop/STEMMIA Dexter/DECISOES.md
~/Desktop/STEMMIA Dexter/ROTINA.md
~/Desktop/STEMMIA Dexter/00-CONTROLE/AGORA.md
~/Desktop/STEMMIA Dexter/00-CONTROLE/CLAUDE-MEMORIA-RECUPERAVEL.md
```

2. Criar estrutura.
3. Medir tamanho e espaço.
4. Copiar ou espelhar com segurança.
5. Criar scripts.
6. Rodar atualização.
7. Gerar índices.
8. Gerar extrações temáticas.
9. Gerar relatório de validação.
10. Gerar plano de ação.
11. Mostrar provas.

Não encerrar dizendo apenas “pronto”.
Encerrar com:

```text
CAMINHO CRIADO:
ARQUIVOS GERADOS:
CONTAGENS:
TESTES FEITOS:
COMO ATUALIZAR:
COMO BUSCAR:
PRÓXIMA AÇÃO:
```

