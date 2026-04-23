---
titulo: Terminal Mac — básico
bloco: 02_programming
tipo: tutorial
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 6
---

# Terminal Mac — básico

Shell no Mac (zsh por padrão). Todos comandos abaixo funcionam em bash também.

## Navegação

### `pwd` — mostra pasta atual
```bash
pwd
# /Users/jesus/Desktop/STEMMIA Dexter
```

### `ls` — lista conteúdo
```bash
ls                   # só nomes
ls -l                # detalhado (permissão, tamanho, data)
ls -la               # inclui ocultos (iniciam com .)
ls -lh               # tamanho humano (KB, MB)
ls *.pdf             # só PDFs
```

### `cd` — trocar de pasta
```bash
cd ~/Desktop                 # home + caminho
cd ~/Desktop/STEMMIA\ Dexter # espaço escapado com \
cd "~/Desktop/STEMMIA Dexter"# ou aspas
cd ..                         # pasta acima
cd -                          # volta pra última
cd                            # vai pra home
```

## Manipulação

### `mkdir` — cria pasta
```bash
mkdir laudos
mkdir -p 2026/abril/pericias   # -p cria aninhadas
```

### `mv` — move ou renomeia
```bash
mv laudo.pdf ~/Desktop/_MESA/10-PERICIA/laudos/
mv laudo.pdf laudo-final.pdf    # renomeia
```

### `cp` — copia
```bash
cp laudo.pdf backup-laudo.pdf
cp -r pasta_a pasta_b            # -r recursivo (pasta inteira)
```

### `rm` — APAGA (cuidado)
```bash
rm arquivo.txt        # apaga 1 arquivo
rm *.log              # apaga todos .log da pasta
rm -r pasta/          # apaga pasta inteira
rm -rf pasta/         # força sem confirmar — PERIGOSO
```

**Avisos**:
- `rm` no terminal **não vai para Lixeira**. É permanente.
- Regra local: `rm -rf` está bloqueado por hook. Usar `mv` para `/tmp/` quando quiser "apagar" com segurança.
- Testar com `ls` o glob antes: `ls *.log` → só então `rm *.log`.

### `cat`, `less`, `head`, `tail` — ler arquivo
```bash
cat laudo.txt            # imprime tudo
less laudo.txt           # paginado (q sai)
head -20 laudo.txt       # primeiras 20 linhas
tail -20 laudo.txt       # últimas 20
tail -f monitor.log      # segue em tempo real (ctrl+C sai)
```

## Canalizar com `|`
`|` (pipe) = saída do comando da esquerda vira entrada da direita.

```bash
ls ~/Desktop/_MESA/10-PERICIA/laudos/ | wc -l
# conta quantos arquivos tem na pasta

cat monitor.log | grep "ERROR" | tail -20
# filtra linhas de erro, mostra últimas 20

ps aux | grep python
# todos processos Python rodando
```

Por que importa: combina comandos simples para resolver problema complexo sem script. Filosofia Unix.

## Expansão de caminho
- `~` = home do usuário (`/Users/jesus`).
- `.` = pasta atual.
- `..` = pasta acima.
- `*` = qualquer coisa (glob). `*.pdf` bate todos PDFs.
- `?` = 1 caractere qualquer.

## Autocompletar e histórico
- `Tab` completa nome parcial. `Tab Tab` lista opções.
- `↑` / `↓` percorre histórico.
- `Ctrl+R` busca no histórico.
- `history | grep datajud` procura comando antigo.

## Atalhos úteis
- `Ctrl+C` mata comando em execução.
- `Ctrl+D` encerra sessão (logout).
- `Ctrl+L` limpa tela (= `clear`).
- `Ctrl+A` / `Ctrl+E` início/fim da linha.

## Armadilhas
- Caminho com espaço precisa de `\` ou aspas.
- `rm -rf /` apaga tudo. `rm -rf ~` apaga sua home. Hesitar sempre.
- `*` em pasta errada pode ser catastrófico. `ls <glob>` antes de `rm <glob>`.
