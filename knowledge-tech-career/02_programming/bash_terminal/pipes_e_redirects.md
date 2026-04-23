---
titulo: Pipes e redirecionamentos
bloco: 02_programming
tipo: referencia
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 4
---

# Pipes e redirecionamentos

Todo comando tem 3 canais:
- **stdin** (0) — entrada.
- **stdout** (1) — saída normal.
- **stderr** (2) — saída de erro.

## `|` — pipe (ligar dois comandos)
Saída do esquerdo vira entrada do direito.

```bash
cat monitor.log | grep "ERROR" | wc -l
# lê log → filtra linhas com ERROR → conta quantas
```

Encadeamento típico pericial:
```bash
ls *.pdf | sort | head -5
# 5 primeiros PDFs em ordem alfabética
```

## `>` — redireciona stdout para arquivo (sobrescreve)
```bash
ls > lista.txt         # cria ou sobrescreve lista.txt com saída de ls
python3 script.py > saida.txt
```

Atenção: `>` **apaga** o conteúdo anterior do destino.

## `>>` — redireciona appending
```bash
echo "linha nova" >> log.txt
# adiciona no final, não apaga o que tinha
```

Uso pericial: acumular log de execução sem perder histórico.

## `<` — redireciona stdin
```bash
python3 script.py < dados.json
# script.py recebe conteúdo de dados.json na stdin
```

## `2>` — redireciona stderr
```bash
python3 script.py 2> erros.log
# só erros vão para erros.log. stdout continua no terminal.
```

## `2>&1` — junta stderr no stdout
```bash
python3 script.py > tudo.log 2>&1
# stdout e stderr no mesmo arquivo
```

Ordem importa. Sempre `> destino 2>&1` (primeiro redireciona stdout, depois duplica stderr para o mesmo lugar).

Notação moderna equivalente:
```bash
python3 script.py &> tudo.log
```

## `/dev/null` — descartar saída
Buraco negro do sistema. Tudo escrito lá é perdido.

```bash
comando 2>/dev/null        # esconde só erros
comando > /dev/null 2>&1   # silencia tudo (útil em cron)
```

## `tee` — bifurca: arquivo E terminal
```bash
python3 monitor.py 2>&1 | tee execucao.log
# vê no terminal ao vivo E salva em arquivo
```

`tee -a` para append.

Uso prático: rodar scraper demorado, ver andamento no terminal, ter log completo salvo para análise depois.

## Combinações úteis
```bash
# contar linhas de erro no log de ontem
grep ERROR monitor.log | wc -l

# últimos 50 logs, só warnings e erros, salvar
tail -500 monitor.log | grep -E "WARN|ERROR" > problemas.txt

# rodar script, salvar tudo, ver falhas ao vivo
python3 baixar_pje.py 2>&1 | tee execucao.log | grep -E "ERROR|Exception"
```

## Armadilha
`>` apaga silenciosamente. `python3 script.py > script.py` destrói seu próprio script. Sempre verificar o nome do destino antes de apertar Enter.
