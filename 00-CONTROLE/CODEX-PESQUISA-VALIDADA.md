# CODEX — Pesquisa Validada

Data da validação: 2026-04-14.
Máquina validada: Mac do usuário.
Versão instalada: `codex-cli 0.118.0`.

# Veredito

O arquivo `~/Desktop/CODEX-PESQUISA-COMPLETA.md` não deve ser usado como manual operacional.

Ele serve como rascunho de pesquisa, mas contém erros que podem causar configuração errada e perda de tempo.

# Erros objetivos encontrados

1. Diz que `codex review` não existe.
   - Errado.
   - Nesta máquina, `codex review --help` funciona.

2. Diz que skills ficam em `~/.agents/skills/`.
   - Errado para esta instalação.
   - Nesta máquina, as skills reais estão em `~/.codex/skills/`.

3. Diz para não colocar skills em `~/.codex/skills/`.
   - Errado.
   - Essa é exatamente a pasta em uso.

4. Diz que `memories` e `enable_fanout` não existem.
   - Errado.
   - `codex features list` mostra:
     - `memories = true`
     - `enable_fanout = true`
     - `multi_agent = true`
     - `codex_hooks = true`

5. Mistura pesquisa, comparação com Claude, comandos, arquitetura e plano.
   - Isso aumenta carga cognitiva.
   - Para uso diário, precisa virar checklist curto.

6. Tem muitos trechos sem acentos.
   - Isso viola sua regra operacional.

# O que está correto ou aproveitável

- Usar `AGENTS.md` para instruções persistentes.
- Usar `config.toml` para modelo, sandbox, profiles e MCPs.
- Usar `codex exec` para lote.
- Usar profiles `fast`, `careful` e `batch`.
- Usar `codex mcp list` para verificar MCPs.
- Usar `codex features list` para verificar features.
- Não instalar plugin sem necessidade.
- Não começar por GitHub Action, Codex Cloud ou marketplace.

# Estado real validado nesta máquina

Comandos verificados:

```bash
codex --version
codex features list
codex mcp list
codex review --help
codex exec --help
```

Resultado operacional:

```text
Codex CLI: 0.118.0
Skills reais: ~/.codex/skills/
Config real: ~/.codex/config.toml
Memória real do Codex: ~/.codex/memory.md
Regras globais: ~/AGENTS.md
Hub: ~/Desktop/STEMMIA Dexter/
```

# MCPs ativos no Codex

```text
filesystem
pdf-reader
sqlite
dadosbr
healthcare-mcp
word-document-server
semantic-scholar
telegram-notify
```

O `filesystem` já inclui:

```text
/Users/jesus/Desktop/ANALISADOR FINAL/processos
/Users/jesus/Desktop/ANALISADOR FINAL/scripts
/Users/jesus/Desktop/PERÍCIA
/Users/jesus/Desktop/STEMMIA Dexter
/Users/jesus/Desktop/processos-pje-windows
```

# Uso correto para sua rotina

## Consulta rápida

```bash
codex -p fast
```

## Trabalho cuidadoso

```bash
codex -p careful
```

## Processamento em lote

```bash
codex exec -p batch --skip-git-repo-check "TAREFA"
```

## Ver MCPs

```bash
codex mcp list
```

## Ver features

```bash
codex features list
```

## Revisão

```bash
codex review --uncommitted
```

# Decisão operacional

Não mexer mais em configuração agora.

Próxima tarefa real:

```text
Triar os 71 PDFs baixados em ~/Desktop/processos-pje-windows/
```

Ordem:

1. Separar por CNJ.
2. Copiar para `~/Desktop/ANALISADOR FINAL/processos/CNJ/`.
3. Extrair `TEXTO-EXTRAIDO.txt`.
4. Gerar `FICHA.json`.
5. Gerar `URGENCIA.json`.
6. Ordenar por prazo e tipo de resposta.

