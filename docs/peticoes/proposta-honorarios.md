# Petição: Proposta de Honorários Periciais

## O que é
Petição em que o perito propõe ao juiz o valor que quer receber pela perícia. É o pedido formal de pagamento — o juiz intima as partes para se manifestarem e, depois, fixa o valor (igual, maior ou menor). Base legal: art. 465, §2º, I, do CPC + Resolução CNJ 232/2016. Variante atual disponível: `avulsa` (genérica). Outras classes (erro médico, securitário, previdenciário, trabalhista, cível, DPVAT) estão planejadas no README da pasta mas ainda sem TEMPLATE.

## Quando usar
- Juiz pede proposta em petição separada do aceite (é o caso mais comum).
- Perito já aceitou o encargo e agora precisa formalizar o valor.
- **Não usar** se o juiz já fixou os honorários na decisão — nesse caso, usar `aceite/TEMPLATE-condicionado.md`.

## Placeholders obrigatórios
| Placeholder | Fonte (FICHA.json) | Exemplo |
|---|---|---|
| `juizo.numero_vara` | `processo.vara.numero` | `2` |
| `juizo.materias` | `processo.vara.materias` | `CÍVEL` |
| `juizo.comarca` | `processo.comarca` | `GOVERNADOR VALADARES` |
| `juizo.uf` | `processo.uf` | `MG` |
| `juizo.vocativo` | `processo.vocativo` | `Meritíssimo Juiz,` |
| `processo.cnj` | `processo.cnj` | `5008297-73.2025.8.13.0105` |
| `processo.id_decisao` | `processo.id_decisao` | `10637932621` |
| `honorarios.valor_numerico` | `honorarios.valor_numerico` | `612,00` |
| `honorarios.valor_extenso` | `honorarios.valor_extenso` | `seiscentos e doze reais` |
| `honorarios.fundamentacao` | `honorarios.fundamentacao` | `Valor fundamentado no piso da Portaria TJMG 7231/2025...` |
| `honorarios.faixa_tabela` | `honorarios.faixa_tabela` | `R$ 400,00 a R$ 3.060,00` |
| `pericia.tipo` | `pericia.tipo` | `perícia médica cível` |
| `data.por_extenso` | `sistema:data_hoje_por_extenso` | `24 de abril de 2026` |

## Exemplo real preenchido
```
AO JUÍZO DA 2ª VARA CÍVEL DA COMARCA DE GOVERNADOR VALADARES – MG

Processo nº: 5008297-73.2025.8.13.0105

MANIFESTAÇÃO – PROPOSTA DE HONORÁRIOS PERICIAIS

Meritíssimo Juiz,

Em atenção à decisão de ID 10637932621, venho, nos termos do art. 465, §2º, I, do CPC, apresentar proposta de honorários periciais.

I — DO VALOR
Proponho honorários periciais no valor de R$ 612,00 (seiscentos e doze reais).

II — FUNDAMENTAÇÃO
Valor fundamentado no piso da Portaria TJMG 7231/2025 para perícia médica de baixa-média complexidade, considerando deslocamento, tempo e responsabilidade técnica.
```

## Regras de valor/estilo
- Vocativo: parametrizado via `juizo.vocativo` (permite "Meritíssimo Juiz,", "Excelência,", etc.).
- **Faixa TJMG (Portaria 7231/2025, perícia médica)**: R$ 400,00 a R$ 3.060,00.
- Dados bancários do perito estão hardcoded no TEMPLATE (Santander 033, agência 2960, CC 01035135-5, PIX perito@drjesus.com.br). Se mudar → editar TEMPLATE, não placeholder.
- Estrutura fixa: I — Valor, II — Fundamentação, III — Referências Normativas, IV — Dados Bancários.
- Duração do bloco: 5 min.
- Fundamentação deve citar: Resolução CNJ 232/2016 + tabela TJMG vigente + fator de complexidade (se aplicável).
- Fonte-original: `MODELOS PETIÇÕES PLACEHOLDERS/proposta/proposta-honorarios.md`.

## Como gerar
```bash
python3 "/Users/jesus/Desktop/STEMMIA Dexter/cowork/05-AUTOMACOES/scripts/aplicar_template.py" \
  --template "/Users/jesus/Desktop/STEMMIA Dexter/cowork/02-BIBLIOTECA/peticoes/proposta-honorarios/TEMPLATE.md" \
  --ficha <path-do-FICHA.json> \
  --saida <path-de-saida.md>
```

## Variantes por classe processual (planejadas, sem TEMPLATE ainda)
Ver `cowork/02-BIBLIOTECA/peticoes/proposta-honorarios/README.md`. Ordem de prioridade sugerida pelo próprio README:
1. `erro-medico/` — mais frequente e complexo
2. `securitario/`
3. `previdenciario/` — baseline simples
4. `trabalhista/`, `civel-dano-pessoal/`, `dpvat/` — conforme casos reais chegarem

Enquanto essas subpastas não tiverem TEMPLATE próprio, usar o `TEMPLATE.md` genérico (variante `avulsa`).
