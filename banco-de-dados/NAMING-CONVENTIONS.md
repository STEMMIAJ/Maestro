# NAMING-CONVENTIONS.md — Padrões de Nomeação

Regra geral: nomes previsíveis, sem acento, sem espaço, sem caractere especial,
separador `-` para palavras e `_` para prefixos de ordem.

## Pastas

- PascalCase com hífen entre palavras internas: `Auxilio-Acidente`,
  `BPC-LOAS`, `Responsabilidade-Civil-Medica`.
- Blocos de nível 0: `Federal`, `Estadual`, `Banco-Transversal`.
- Subpastas de conteúdo dentro de uma situação: minúsculas simples —
  `casos/`, `contestacoes/`, `sentencas/`.

## Arquivos `.md` dentro de uma situação

Prefixo numérico de 2 dígitos + `_` + descrição:

```
00_Sumario.md
01_Modelo_de_Laudo.md
02_Checklist_Qualidade.md
03_Quesitos_Tipicos.md
04_Protocolos.md
05_Escalas.md
```

## Casos (laudos/processos)

Padrão: `<AAAA>_<numero-processo-resumido>_<tema-curto>.md`

Exemplos:

```
2024_0001234-56_coluna-lombar.md
2025_1122334-55_joelho-menisco.md
```

Cada caso acompanhado de `FICHA.json` com o mesmo stem:

```
2024_0001234-56_coluna-lombar.md
2024_0001234-56_coluna-lombar.FICHA.json
```

## Protocolos

Padrão: `<origem>_<tema>_<ano>.md`

```
ABMLPM_Previdenciario_2025.md
AMB_Seguro-Privado_2025.md
CFM_Nexo-Causal_2023.md
```

## Quesitos

Padrão: `<tribunal>_<area>_<ano>.md`

```
JF_Previdenciario_2024.md
TRF6_Quesitos-Medicos_2024.md
TST_Trabalhista_2023.md
```

## Escalas

Padrão: `<nome-escala>_<dominio>.md`

```
Barthel_AVD.md
VAS_Dor.md
Tinetti_Marcha-Equilibrio.md
PHQ-9_Depressao.md
```

## Jurisprudência / Sentenças

Padrão: `<tribunal>_<ano>_<numero-curto>_<tema>.md`

```
STJ_2023_123456_pericia-vinculante.md
TJMG_2024_789012_laudo-acolhido.md
```

## Contestações

Padrão: `<tipo-ataque>_<tema>_<ano>.md`

```
Omissao_Nexo_2024.md
Contradicao_Incapacidade_2025.md
Falta-Quesito_DPOC_2024.md
```

## Modelos consolidados

Em `Banco-Transversal/Modelos-Laudo/`:

```
Modelo_Previdenciario_Auxilio-Acidente_Coluna.md
Modelo_Estadual_Erro-Medico_Ortopedia.md
```

## Identificadores proibidos

- Não usar acento.
- Não usar espaço.
- Não usar `ç` — trocar por `c` (`Previdenciario`, não `Previdenciário`).
- Não usar caractere maiúsculo em sufixo de caso.
- Não usar nome genérico: `novo.md`, `laudo.md`, `final.md`, `v2.md`.

## Versionamento

- Não sufixar com `-v2`, `-final`, `-novo`. Usar git.
- Se for necessário preservar versão antiga: mover para
  `_historico/<data>_<nome-original>.md` dentro da própria pasta.

## Temas clínicos (tags, não pastas)

Temas clínicos (coluna lombar, ombro, depressão, DPOC, joelho, etc.) são
**tags** registradas em `FICHA.json` sob o array `temas_clinicos: []`, e
**nunca** viram subpasta da taxonomia. A árvore é organizada por situação
jurídica; o recorte clínico é transversal e consultado via busca/índice.

Exemplos:

```json
{ "situacao": "Auxilio-Acidente", "temas_clinicos": ["coluna-lombar", "hernia-discal"] }
{ "situacao": "BPC-LOAS", "temas_clinicos": ["depressao", "ansiedade"] }
```

Proibido criar `Auxilio-Acidente/coluna-lombar/` ou `BPC-LOAS/depressao/`.

## Campos mínimos do `FICHA.json` de caso

```json
{
  "numero_processo": "",
  "bloco": "Federal|Estadual",
  "situacao": "",
  "temas_clinicos": [],
  "cid": [],
  "quesitos_usados": [],
  "desfecho": "",
  "data_laudo": "",
  "observacoes": ""
}
```
