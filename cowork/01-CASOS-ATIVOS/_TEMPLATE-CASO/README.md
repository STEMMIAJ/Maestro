# _TEMPLATE-CASO — estrutura padrão de caso ativo

Copiar esta pasta INTEIRA para `01-CASOS-ATIVOS/<CNJ>/` quando abrir um caso novo.

## Pastas

| Pasta | Conteúdo |
|---|---|
| `_dados/` | Inputs brutos: PDFs do PJe, prints, áudios, anotações soltas. Não editar — fonte de verdade. |
| `documentos-recebidos/` | Documentos enviados pelas partes (laudos anteriores, atestados, prontuários, contratos). |
| `exames/` | Exames complementares (imagem, laboratório) citados ou anexados no processo. |
| `peticoes-geradas/` | Output do motor `aplicar_template.py`. Nomear `<AAAA-MM-DD>-<subtipo>.md`. |
| `laudo/` | Laudo pericial em construção + versões. Formato MD → DOCX → PDF timbrado. |
| `revisao/` | Rascunhos, notas de revisão, apontamentos para próxima versão. |

## Arquivos-raiz

- `FICHA.json` — **fonte única** de dados estruturados do caso. Todo template lê daqui.
- `README.md` (este) — remover ou sobrescrever com resumo do caso após abrir.

## Fluxo mínimo por caso

1. `cp -R _TEMPLATE-CASO <CNJ>` e renomear pasta
2. Extrair texto dos PDFs → popular `FICHA.json`
3. Gerar petições conforme demandas do PJe: `skill peticao-cowork` + `aplicar_template.py`
4. Fazer perícia → popular `laudo/` com notas
5. Gerar laudo final → entregar
6. Ao encerrar: mover para `07-ARQUIVO/<ano>/<CNJ>/`

## Campos críticos da FICHA

Sem estes, o motor não gera petição:
- `processo.cnj`
- `juizo.numero_vara`, `juizo.materias`, `juizo.comarca`, `juizo.uf`
- `atos_anteriores.ids` (ao menos 1 para referenciar no aceite/agendamento)

Campos específicos por tipo de petição estão no frontmatter `variaveis_requeridas` de cada `TEMPLATE.md`.
