# Tabelas Oficiais de Honorários Periciais — 2026

Fonte: SQLite `src/honorarios/dados/honorarios.db`, tabela `tabelas_oficiais`.
Total de registros: 9 (8 ativos + 1 revogada).
Ordenação: vigentes primeiro, revogadas no final.

| ID | Fonte | Tipo | Valor Base (R$) | Valor Máximo (R$) | Vigência Início | Vigência Fim | Observações |
|----|-------|------|-----------------|-------------------|-----------------|--------------|-------------|
| 3  | CNJ Resolução 232/2016 | Pericia Geral | 370,00 | 1.850,00 | 2016 | atual | Até 5x se fundamentado |
| 1  | TJMG Portaria 7231/2025 | Pericia Medica | 585,66 | 2.928,30 | 26/05/2025 | atual | Até 5x se complexa (autorização Corregedoria) |
| 9  | TRF/JEF | BPC/LOAS | 362,00 | 1.000,00 | 2024 | — | Previdenciário |
| 4  | TRT3 | Simples | 1.000,00 | 2.500,00 | 2024 | — | Quando empresa paga |
| 5  | TRT3 | Media | 2.500,00 | 3.500,00 | 2024 | — | Múltiplas patologias |
| 6  | TRT3 | Complexa | 3.500,00 | 5.000,00 | 2024 | — | Nexo causal |
| 7  | TRT3 | Ação Coletiva | 5.000,00 | 21.600,00 | 2024 | — | Casos excepcionais |
| 8  | TRT3 | Gratuidade | 1.000,00 | 1.000,00 | 2024 | — | Limite União (Res 247/2019 CSJT) |
| 2  | TJMG Portaria 6607/2024 | Pericia Medica | 585,66 | 2.928,30 | 21/06/2024 | 25/05/2025 | ⚠️ REVOGADA |

## Notas

- **vigencia_fim = "atual"** → norma vigente declarada explicitamente.
- **vigencia_fim = ""** (vazio) → registros TRT3/TRF tratados como vigentes (sem data de revogação no DB).
- **vigencia_fim = "25/05/2025"** → TJMG Portaria 6607/2024 revogada pela 7231/2025.

## Arquivos individuais (fontes ativas)

Gerados em `src/honorarios/tabelas/`:

- `cnj-resolucao-232-2016.json`
- `tjmg-portaria-7231-2025.json`
- `trf-jef.json`
- `trt3.json` (5 entradas: Simples, Media, Complexa, Ação Coletiva, Gratuidade)
