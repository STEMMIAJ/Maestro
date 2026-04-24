# INTEGRACAO-BANCO-GERAL.md

Mapeamento bidirecional entre este módulo (`banco-de-dados/`) e o banco de
dados de referência (`~/Desktop/STEMMIA Dexter/BANCO-DADOS/`).

## Por que dois bancos

| Módulo | Eixo | Finalidade |
|---|---|---|
| `BANCO-DADOS/` (banco geral) | Área de conhecimento | Biblioteca — estudar, consultar matéria. |
| `banco-de-dados/` (este) | Situação pericial | Operação — resolver um caso concreto. |

Os dois NÃO devem duplicar arquivos. Este módulo **aponta** para o banco geral
quando precisa de protocolo, legislação ou jurisprudência de base.

## Regra de ouro

- Arquivo-fonte (PDF oficial, lei, protocolo bruto) → `BANCO-DADOS/`.
- Ficha pericial aplicada à situação (resumo, checklist, quesitos traduzidos,
  laudo de referência) → `banco-de-dados/`.
- Nunca baixar o mesmo PDF em ambos. Referenciar caminho relativo.

## Mapa de dependências

### Banco-Transversal/Protocolos/
Consome `BANCO-DADOS/PERÍCIA/Perícia_Médica_Judicial/` e
`BANCO-DADOS/MEDICINA/<especialidade>/` (PCDTs CONITEC, diretrizes de
sociedades, resoluções CFM).

- ABMLPM → `BANCO-DADOS/PERÍCIA/Tabelas_e_Baremos/` (Tabela ABMLPM 2024).
- AMB → `BANCO-DADOS/MEDICINA/<especialidade>/` (diretrizes AMB/sociedades).
- CFM → `BANCO-DADOS/PERÍCIA/Perícia_Médica_Judicial/` (Res. 2.430/2025, 2.056/2013,
  2.297/2021, 2.183/2018, 2.381/2024).

### Banco-Transversal/Quesitos/
Consome `BANCO-DADOS/DIREITO/Jurisprudência/` (súmulas, enunciados, teses) e
`BANCO-DADOS/PERÍCIA/Quesitos_e_Laudos/` (quesitos unificados JF/TRFs/TST).

### Banco-Transversal/Escalas/
Consome `BANCO-DADOS/MEDICINA/Psiquiatria/` (PHQ-9, GAD-7),
`BANCO-DADOS/MEDICINA/Ortopedia_e_Traumatologia/` (VAS),
`BANCO-DADOS/MEDICINA/Neurologia/Dor/` (escalas funcionais).

### Banco-Transversal/CID-Referencia/
Consome `BANCO-DADOS/MEDICINA/` (tabelas CID-10 DataSUS + CID-11 WHO listadas em
`MAPA-DE-FONTES.md`).

### Banco-Transversal/Jurisprudencia/
Consome `BANCO-DADOS/DIREITO/Jurisprudência/` (STJ, STF, TST, TNU, CNJ, CJF).

### Federal/Previdenciario/
Legislação: `BANCO-DADOS/DIREITO/Previdenciário/` (Lei 8.213/91, Lei 8.212/91,
Decreto 3.048/99). Normas operacionais: manuais INSS em
`BANCO-DADOS/PERÍCIA/Manuais_INSS/`.

### Federal/Trabalhista/
Legislação: `BANCO-DADOS/DIREITO/Trabalhista/` (CLT, Lei 6.514/77). NRs:
`BANCO-DADOS/PERÍCIA/` (NR-7, NR-9, NR-15, NR-17).

### Federal/Civel/ e Estadual/Civel/
Legislação: `BANCO-DADOS/DIREITO/Civil/`, `BANCO-DADOS/DIREITO/Processual Civil/`,
`BANCO-DADOS/DIREITO/Consumidor/`. Tabela de dano corporal em
`BANCO-DADOS/PERÍCIA/Tabelas_e_Baremos/`.

### Estadual/Familia/Curatela/
Legislação: `BANCO-DADOS/DIREITO/Civil/` (Lei 13.146/2015 — Estatuto da Pessoa
com Deficiência), `BANCO-DADOS/DIREITO/Constitucional/`.

## Formato do cross-reference dentro dos scaffolds

Em qualquer arquivo deste módulo que precise de fonte, usar bloco literal:

```
## Fonte
- Arquivo bruto: `../../BANCO-DADOS/<area>/<pasta>/<arquivo>`
- URL oficial: <https://...>
- Data de verificação: AAAA-MM-DD
```

NUNCA referenciar por caminho absoluto (quebra se o hub mudar de lugar).

## Atualização

- Quando o banco geral ganhar conteúdo novo (via `MAPA-DE-FONTES.md`), atualizar
  esta ligação no ponto correspondente.
- Quando este módulo receber nova situação pericial, verificar se o banco geral
  tem a área-suporte e registrar aqui.

## Contra-referência

O banco geral tem entrada apontando para cá em:
`../BANCO-DADOS/MAPA-DE-FONTES.md` (seção "Consumo operacional").
