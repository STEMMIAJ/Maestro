---
titulo: Variáveis e scripts shell
bloco: 02_programming
tipo: tutorial
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 5
---

# Variáveis e scripts shell

## Variável — definir e ler
```bash
NOME="Jesus"          # sem espaço em volta do =
CNJ="0001-2024"
echo "$NOME"          # Jesus
echo "${NOME}-dados"  # Jesus-dados
```

**Sempre aspear** `"$VAR"`. Sem aspas, espaço no conteúdo quebra tudo.

```bash
# RUIM
PASTA=~/Desktop/STEMMIA\ Dexter
cd $PASTA             # quebra no espaço — interpreta 2 args

# BOM
PASTA=~/Desktop/STEMMIA\ Dexter
cd "$PASTA"
```

## `export` — variável vira de ambiente
Sem `export`, a variável vive só no shell atual. Com `export`, é herdada por comandos filhos (scripts que você chama).

```bash
export DATAJUD_API_KEY="abc123"
python3 monitor.py     # enxerga DATAJUD_API_KEY via os.environ
```

Variáveis persistentes vão no `~/.zshrc` (ou `~/.bash_profile`).

## Argumentos de script
Ao chamar `./script.sh foo bar`, dentro do script:
- `$0` = nome do script.
- `$1`, `$2`, ... = argumentos posicionais.
- `$#` = quantidade de argumentos.
- `$@` = todos os argumentos.

```bash
#!/bin/bash
echo "recebi $# argumentos: $@"
echo "primeiro: $1"
```

## Shebang — primeira linha
Shebang (`#!`) diz ao sistema qual interpretador usar.

```bash
#!/bin/bash           # script bash
#!/usr/bin/env python3 # script Python (portátil)
```

`/usr/bin/env python3` acha o `python3` do PATH — funciona em venv também.

## `chmod +x` — dar permissão de execução
Script recém-criado não roda direto. Precisa virar executável.

```bash
chmod +x monitor.sh
./monitor.sh
```

Sem `+x`, `./monitor.sh` dá "Permission denied". Alternativa: rodar via `bash monitor.sh` (não precisa de `+x`).

## Estrutura mínima de script
```bash
#!/bin/bash
set -euo pipefail       # modo seguro (ver abaixo)

# constantes
PASTA_LAUDOS="$HOME/Desktop/_MESA/10-PERICIA/laudos"
HOJE="$(date +%Y-%m-%d)"

# funções
contar_laudos() {
    local pasta="$1"
    find "$pasta" -name "*.pdf" | wc -l
}

# main
total=$(contar_laudos "$PASTA_LAUDOS")
echo "[$HOJE] total de laudos: $total" >> relatorio.log
```

### `set -euo pipefail` — modo seguro
Colocar **sempre** no topo de script sério:
- `-e` aborta no primeiro erro (sem isso, segue e quebra depois).
- `-u` aborta se usar variável não definida (evita typo silencioso).
- `-o pipefail` erro em qualquer etapa de pipe conta como falha (sem isso, só o último conta).

## Substituição de comando — `$(...)`
```bash
HOJE=$(date +%Y-%m-%d)
TOTAL=$(ls ~/Desktop/laudos | wc -l)
echo "$HOJE tem $TOTAL laudos"
```

Antigo: `` `comando` `` (backticks). Usar `$(...)` — aninha e é legível.

## Condicional
```bash
if [ -f "$ARQUIVO" ]; then
    echo "existe"
else
    echo "nao existe"
fi
```

Testes comuns: `-f` arquivo existe, `-d` pasta existe, `-z` string vazia, `"$a" = "$b"` igualdade, `"$a" != "$b"` diferença.

## Exemplo pericial — rodar script diário
```bash
#!/bin/bash
set -euo pipefail

cd "$HOME/Desktop/STEMMIA Dexter/src/automacoes"
source .venv/bin/activate
python3 monitorar_movimentacao.py 2>&1 | tee "logs/monitor-$(date +%Y%m%d).log"
```

Torna executável: `chmod +x rodar_monitor.sh`. Agendar via `launchd` (macOS) ou `cron`.
