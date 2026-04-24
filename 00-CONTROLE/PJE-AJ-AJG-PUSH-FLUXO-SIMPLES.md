# PJe AJ/AJG PUSH - fluxo simples

Data: 2026-04-18

## Resposta direta

Sim. É possível fazer essa automação.

O fluxo correto é este:

1. Coletar processos do AJ e do AJG.
2. Gerar uma lista única de CNJs.
3. Ler o PUSH atual do PJe.
4. Comparar:
   - se está no AJ/AJG e não está no PUSH: incluir no PUSH;
   - se está no PUSH e não tem PDF válido salvo: baixar;
   - se o PDF baixado não bate com o CNJ: separar em `_mismatch` e não considerar baixado.
5. Baixar um por um, em ordem definida.
6. Conferir relatório JSON e pasta de PDFs.

## Estado verificado agora

- Repositório operacional: `/Users/jesus/stemmia-forense`.
- Scripts principais ficam em: `/Users/jesus/stemmia-forense/src/pje`.
- PDFs baixados ficam em: `/Users/jesus/Desktop/processos-pje`.
- `processos-pje-windows` aponta para a mesma pasta do Windows/Parallels.
- A pasta atual tem 187 PDFs.
- Pelos nomes dos arquivos, há 83 CNJs únicos.
- Há PDFs avulsos sem CNJ no nome; isso não significa erro, mas precisa inventário antes de organizar.
- Não há relatório atual em `Desktop/processos-pje/_relatorios_push`.
- Últimos `relatorio-*.json` encontrados na pasta são de 2026-04-13.
- A pasta `/Users/jesus/Desktop/ANALISADOR FINAL/scripts` deu `Operation not permitted` pelo terminal; por isso a rota segura agora é usar `/Users/jesus/stemmia-forense`.

## Conferência nova dos PDFs

Relatório gerado em 2026-04-18:

```text
/Users/jesus/Desktop/processos-pje/_relatorios_primeira_pagina/RELATORIO-PRIMEIRA-PAGINA-20260418-180131.md
```

Resultado:

- PDFs principais analisados: 102.
- OK: 4.
- Possíveis repetidos: 4.
- Precisam revisão: 94.
- Sem erro de leitura.

Achado importante:

Muitos PDFs antigos estão com nome de CNJ diferente do CNJ real da primeira página.

Conclusão operacional:

Não confiar só no nome dos PDFs antigos.

Para novos downloads, manter a validação ativa em `baixar_push_pje_playwright.py`.

Não usar `--sem-validar-pdf-cnj` salvo emergência documentada.

## O que já está pronto

### 1. Consultar AJ

Arquivo: `/Users/jesus/stemmia-forense/src/pje/consultar_aj.py`

Serve para ler nomeações no AJ/TJMG.

Não aceita e não rejeita nomeação.

Comando base:

```bash
python3 /Users/jesus/stemmia-forense/src/pje/consultar_aj.py --pendentes --json
```

Requisito: Chrome com AJ logado e porta CDP 9223.

### 2. Consultar AJG

Arquivo: `/Users/jesus/stemmia-forense/src/pje/consultar_ajg.py`

Serve para ler nomeações no AJG Federal.

Não aceita e não rejeita nomeação.

Comando base:

```bash
python3 /Users/jesus/stemmia-forense/src/pje/consultar_ajg.py --pendentes --json
```

Requisito: Chrome com AJG logado e porta CDP 9223.

### 3. Contar PUSH atual

Arquivo: `/Users/jesus/stemmia-forense/src/pje/contar_push_pje.py`

Executor Windows:

```bat
\\Mac\Home\stemmia-forense\CONTAR_PJE_PUSH.bat
```

Serve para ler as páginas do PUSH e comparar com os PDFs já salvos em `Desktop\processos-pje`.

Não baixa.

Não apaga.

Não renomeia.

Gera:

- `PJE-PUSH-CNJS-*.csv`
- `FALTAM-BAIXAR-*.csv`
- `BAIXADOS-FORA-PUSH-*.csv`
- `RESUMO-PJE-PUSH-*.md`
- `RESUMO-PJE-PUSH-*.json`

Destino esperado:

```text
Desktop\processos-pje\_relatorios_push
```

### 4. Incluir processos no PUSH

Arquivo: `/Users/jesus/stemmia-forense/src/pje/incluir_push.py`

Serve para incluir CNJs no PUSH.

Lê lista de CNJ em TXT ou JSON.

Formato aceito no TXT:

```text
5000000-00.2026.8.13.0000|observação do PUSH
```

Comando base:

```bat
py -3 "\\Mac\Home\stemmia-forense\src\pje\incluir_push.py" --arquivo "CAMINHO_DA_LISTA.txt" --porta 9223
```

Se o processo já estiver no PUSH, o script marca como duplicata e segue.

### 5. Baixar processos do PUSH

Arquivo: `/Users/jesus/stemmia-forense/src/pje/baixar_push_pje_playwright.py`

Executor piloto:

```bat
\\Mac\Home\stemmia-forense\BAIXAR_PJE_PLAYWRIGHT.bat
```

Executor para até 60 novos:

```bat
\\Mac\Home\stemmia-forense\BAIXAR_60_FALTANTES_PJE.bat
```

Serve para baixar PDFs do PUSH.

Travas importantes:

- pula PDF que já existe;
- confere se a página aberta contém o CNJ esperado;
- confere se a primeira página do PDF contém o CNJ esperado;
- PDF divergente vai para `_mismatch`;
- relatório final vai para `relatorio-*.json`;
- logs vão para `_logs`.

Opções importantes:

```text
--cnjs-file LISTA.txt       baixa só os CNJs da lista
--limite-novos 60          para depois de 60 PDFs novos
--retry                    tenta de novo erros do último relatório
--parar-hora 23:59         não começa novo processo depois desse horário
--sem-validar-pdf-cnj      NÃO usar salvo emergência documentada
```

### 6. Baixar Taiobeiras primeiro

Lista curta atual:

```text
/Users/jesus/stemmia-forense/src/pje/taiobeiras-faltantes-hoje.txt
```

Executor completo:

```bat
\\Mac\Home\stemmia-forense\TAIOBEIRAS_INCLUIR_E_BAIXAR.bat
```

Esse executor:

1. inclui/garante os 6 processos de Taiobeiras no PUSH;
2. baixa somente esses 6;
3. pula o que já existir.

Atalho na Mesa:

```bat
/Users/jesus/Desktop/TAIOBEIRAS_INCLUIR_E_BAIXAR.bat
```

### 7. Conferir PDFs baixados

Mais rápido e seguro:

```bash
python3 /Users/jesus/stemmia-forense/src/pje/inventariar_primeira_pagina_pje.py --pasta /Users/jesus/Desktop/processos-pje
```

Lê só a primeira página dos PDFs.

Não renomeia.

Não apaga.

Gera relatório em:

```text
Desktop/processos-pje/_relatorios_primeira_pagina
```

### 8. Analisar limpeza da pasta PJe

Executor Windows:

```bat
\\Mac\Home\stemmia-forense\ANALISAR_PROCESSOS_PJE.bat
```

Arquivo:

```text
/Users/jesus/stemmia-forense/src/pje/organizar_processos_pje.py
```

Modo padrão: só relatório.

Não renomeia.

Não apaga.

Só propõe renomeações.

## O que não deve ser usado agora como fluxo principal

### `sincronizar_aj_pje.py`

Arquivo:

```text
/Users/jesus/stemmia-forense/src/pje/sincronizar_aj_pje.py
```

Ele tenta fazer tudo em um script só, mas hoje não é a rota mais segura.

Problemas encontrados:

- usa caminho antigo para baixador PJe;
- compara PDF em estrutura antiga;
- não usa a validação nova de CNJ do PDF feita por `baixar_push_pje_playwright.py`.

Pode ser usado como referência de lógica, não como executor principal do fim de semana.

### `descobrir_processos.py`

Arquivo:

```text
/Users/jesus/stemmia-forense/src/pipeline/descobrir_processos.py
```

É amplo demais para a urgência atual.

Serve para descoberta geral por várias fontes.

Não deve substituir o fluxo simples de baixar PDFs do PUSH.

### Scripts antigos de Selenium

Exemplos:

```text
/Users/jesus/stemmia-forense/src/pje/baixar_push_pje.py
/Users/jesus/stemmia-forense/BAIXAR_PJE_17042026.bat
```

Não são a primeira escolha agora.

A primeira escolha é Playwright:

```text
/Users/jesus/stemmia-forense/src/pje/baixar_push_pje_playwright.py
```

## Ordem prática para o fim de semana

### Se o objetivo for baixar o que já está no PUSH

1. No Windows/Parallels, rodar:

```bat
\\Mac\Home\stemmia-forense\CONTAR_PJE_PUSH.bat
```

2. Conferir:

```text
Desktop\processos-pje\_relatorios_push\RESUMO-PJE-PUSH-*.md
```

3. Se Taiobeiras ainda for prioridade:

```bat
\\Mac\Home\stemmia-forense\TAIOBEIRAS_INCLUIR_E_BAIXAR.bat
```

4. Depois baixar lote geral:

```bat
\\Mac\Home\stemmia-forense\BAIXAR_60_FALTANTES_PJE.bat
```

5. Conferir:

```text
Desktop\processos-pje\relatorio-*.json
Desktop\processos-pje\_logs
Desktop\processos-pje\_mismatch
```

6. Rodar de novo:

```bat
\\Mac\Home\stemmia-forense\CONTAR_PJE_PUSH.bat
```

O número importante é `Faltam baixar`.

### Se o objetivo for coletar AJ/AJG antes

1. Coletar AJ.
2. Coletar AJG.
3. Gerar lista única.
4. Rodar contagem do PUSH.
5. Comparar lista AJ/AJG com lista PUSH.
6. Incluir no PUSH só o que estiver fora.
7. Baixar só a fila final, em ordem definida.

As peças existem, mas o wrapper único AJ/AJG -> PUSH -> fila ainda precisa ser consolidado para evitar variação.

## Decisão operacional

Não usar IA como memória do que falta baixar.

A fonte de verdade precisa ser arquivo:

- lista AJ/AJG exportada;
- relatório atual do PUSH;
- lista de PDFs baixados;
- relatório JSON do download.

## Validação feita neste documento

Foram verificados:

- existência dos arquivos principais;
- contagem local da pasta `Desktop/processos-pje`;
- inventário de primeira página dos PDFs principais;
- link `processos-pje-windows`;
- compilação Python dos scripts principais;
- `--help` dos scripts `baixar_push_pje_playwright.py`, `contar_push_pje.py` e `incluir_push.py`.

Não foi executado login no PJe/AJ/AJG nesta verificação.
