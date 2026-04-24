---
nome: fonte-originais-perito
proposito: Originais .docx do próprio perito — fonte do timbrado, dados pessoais e estilo de redação
origem: copiados de `STEMMIA Dexter/_arquivo/Modelos Petições/` em 2026-04-20
---

# Originais do perito — preservados

**ATENÇÃO:** estes arquivos são a **fonte-de-verdade** de timbrado, dados profissionais e estilo do Dr. Jésus. Nunca editar aqui. Para criar template ativo, copiar para subpasta da classe (`../aceite/`, `../agendamento/`) e trabalhar lá.

## Inventário

| Arquivo | Tipo | Contém timbrado? | Uso |
|---|---|---|---|
| `Petição de Aceite - 0038122-07.2012.8.13.0396 - Mantena.docx` | Aceite condicionado (cita honorários já fixados) | SIM — header+footer textuais | Fonte de dados profissionais e fecho padrão |
| `Aceite - 0038122-07.2012.8.13.0396 - Mantena.docx` | Aceite simples (sem valor) | SIM — header+footer textuais | Variante do anterior |
| `Agendamento de Perícia - MODELO - cópia.docx` | Agendamento genérico (com placeholders XXXX) | SIM — header gráfico (image1.png, image2.png) | Fonte do timbrado gráfico; base do template de agendamento |

## Extrações feitas em 2026-04-20

1. Timbrado textual (header) → `cowork/03-IDENTIDADE/dados-profissionais.md` seção 10
2. Footer (endereço/contato) → `cowork/03-IDENTIDADE/dados-profissionais.md` seção 6
3. Imagens do timbrado → `cowork/03-IDENTIDADE/timbrado/agendamento_image1.png` e `agendamento_image2.png`
4. Estilo de redação → `cowork/03-IDENTIDADE/estilo-redacao.md`

## Padrão extraído

- Endereçamento: `AO JUÍZO DA {{N}}ª VARA {{MATERIA}} DA COMARCA DE {{CIDADE}} – {{UF}}`
- Linha processo: `Processo nº: {{CNJ}}`
- Título: `MANIFESTAÇÃO – {{TIPO_PETICAO}}` (em caixa alta)
- Saudação: `Meritíssimo Juiz,`
- Abertura: `Em atenção à(s) decisão/intimação de ID {{ID}} [e ID {{ID2}}], ...`
- Fecho: `Termos em que,\nPede deferimento.`
- Assinatura: `Dr. Jésus Eduardo Nolêto da Penha\nMédico - Perito Judicial – CRM-MG 92.148\nMembro da ABMLPM - Associação Brasileira de Medicina Legal e Perícia Médica`
- Data: `{{DATA_POR_EXTENSO}}, Governador Valadares - MG.`

## Pendências do usuário

- [ ] Subir mais 5-10 .docx originais (propostas, esclarecimentos, impugnações) para enriquecer o extrator de estilo
- [ ] Confirmar se a imagem do timbrado ainda é a atual (extraídas 2 PNGs do Agendamento — abrir e revisar)
- [ ] Verificar se telefone (33) 99900-1122 ainda é ativo
