---
titulo: Raciocínio computacional
bloco: 02_programming
tipo: conceito
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 6
---

# Raciocínio computacional

Forma de pensar problemas para que uma máquina (ou outra pessoa) execute a solução sem ambiguidade. Quatro pilares.

## 1. Decomposição
Quebrar problema grande em partes pequenas e independentes.

Exemplo pericial — "gerar laudo" decomposto:
1. Ler `FICHA.json` do processo.
2. Baixar PDF do PJe.
3. Extrair texto do PDF.
4. Casar quesitos com trechos do prontuário.
5. Preencher template DOCX.
6. Assinar e salvar.

Por que importa: cada subtarefa vira uma função Python testável isolada. Erro em `extrair_texto_pdf()` não derruba o resto.

## 2. Reconhecimento de padrão
Ver o que se repete entre problemas diferentes para reusar solução.

Exemplo: extração de número CNJ, CPF, CID-10 — todos são regex em texto. Escreve-se um módulo `extratores.py` com uma função por padrão; o laudo, a petição inicial e o relatório do DJEN usam o mesmo módulo.

Por que importa: menos código duplicado, menos bug.

## 3. Abstração
Esconder detalhe irrelevante. Expor só o essencial.

Exemplo: `baixar_processo(numero_cnj)` — quem chama não precisa saber se usa Selenium, requests ou MCP PJe. A assinatura da função é o contrato; o miolo pode mudar.

Por que importa: muda-se a implementação sem quebrar quem depende. O script de laudo não é refeito quando o PJe troca de layout.

## 4. Algoritmo
Sequência finita, determinística, de passos que resolve o problema.

Exemplo — filtrar processos com movimentação nova:
```
para cada processo em lista_processos:
    ultima_mov = ler_data_ultima_movimentacao(processo)
    se ultima_mov > data_ultima_verificacao:
        adiciona processo em novos
retorna novos
```

Por que importa: um algoritmo escrito assim (pseudo-código) traduz-se direto em Python, Bash ou JavaScript. A linguagem é detalhe; o algoritmo é o valor.

## Aplicação prática
Antes de abrir editor, escrever em papel:
- O que entra (input).
- O que sai (output).
- Passos intermediários (algoritmo).
- Onde cada passo é uma função (decomposição).

Só depois codar. Economiza horas.

## Referências
- [TODO/RESEARCH] livro "Pensamento Computacional" — Jeannette Wing (2006, Communications of the ACM).
