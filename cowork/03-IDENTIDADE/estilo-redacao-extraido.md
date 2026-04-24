---
nome: estilo-redacao-extraido
proposito: Estilo real do Dr. Jésus, extraído dos 3 originais preservados em `_fonte-originais-perito/`
fonte: 3 .docx do perito (Aceite-Mantena x2 + Agendamento-MODELO)
atualizado: 2026-04-20
---

# Estilo de redação — padrões extraídos dos originais

Regra: todo template ativo deve respeitar estes padrões. Divergir só com motivo técnico declarado.

## 1. Estrutura esqueleto (petição de perito)

```
[HEADER TIMBRADO]

AO JUÍZO DA {{N}}ª VARA {{MATERIA}} DA COMARCA DE {{CIDADE}} – {{UF}}

Processo nº: {{CNJ}}

MANIFESTAÇÃO – {{TIPO}}

Meritíssimo Juiz,

Em atenção {{REFERENCIA_ATO_ANTERIOR}}, {{CORPO_DA_MANIFESTACAO}}

{{CONTEUDO_ESPECIFICO}}

Termos em que,
Pede deferimento.

Dr. Jésus Eduardo Nolêto da Penha
Médico - Perito Judicial – CRM-MG 92.148
Membro da ABMLPM - Associação Brasileira de Medicina Legal e Perícia Médica

{{DATA_POR_EXTENSO}}, Governador Valadares - MG.

[FOOTER TIMBRADO]
```

## 2. Tratamento

- Juiz: `Meritíssimo Juiz,` (virgula, linha isolada)
- NÃO usa "Vossa Excelência" no corpo (observado nos 3 docs)
- Autorreferência: `meu aceite`, `minha atuação`, `em meu consultório` (1ª pessoa, direto)
- NÃO usa "este Perito" / "o signatário" / "o subscritor" (no corpus atual)

## 3. Caixa alta

- Endereçamento ao juízo: TUDO CAIXA ALTA (`AO JUÍZO DA ...`)
- Título da manifestação: TUDO CAIXA ALTA com travessão (`MANIFESTAÇÃO – ACEITE DE ENCARGO E HONORÁRIOS`)
- Rótulos de campo no agendamento: TUDO CAIXA ALTA (`DATA E HORÁRIO:`, `LOCAL:`)
- Corpo: caixa normal

## 4. Referências a atos anteriores

Sempre por **ID do PJe**, não por data:
- `às decisões de ID 10637932621 e ID 10639375978`
- `à intimação de ID XXXXXXX`

Importante: sistema deve extrair IDs do ato que motivou a petição e inserir aqui.

## 5. Referência ao endereço da perícia (texto completo usado)

> `Rua João Pinheiro, número 531, Centro, Edifício Empresarial Maria Costa – Sala – 207 2º andar (última sala do corredor à esquerda) – Governador Valadares – MG`
>
> Referências: `prédio de esquina entre a Rua Artur Bernardes (onde se encontra o ponto de ônibus) e a Rua João Pinheiro (sendo o prédio em frente ao muro lateral do Colégio Imaculada).`

## 6. Data

Formato por extenso, com vírgula + cidade - UF:
- `17 de março de 2026, Governador Valadares - MG.`

## 7. Fecho textual (literal, preservar)

```
Termos em que,
Pede deferimento.
```

## 8. Assinatura (literal, 3 linhas)

```
Dr. Jésus Eduardo Nolêto da Penha
Médico - Perito Judicial – CRM-MG 92.148
Membro da ABMLPM - Associação Brasileira de Medicina Legal e Perícia Médica
```

## 9. Observações

- Travessão usado: `–` (EN DASH, U+2013), NÃO `-` (hífen) nas linhas de assinatura/título
- Separador em datas: `-` hífen comum
- "perícia" sem acento circunflexo, "periciais" idem
- "Meritíssimo" (2 S, acento agudo)
- Nome com acentos: **Jésus Eduardo Nolêto** (ê em Nolêto)

## 10. O que AINDA não tem padrão extraído

Corpus atual = 3 peças (todas aceite/agendamento). Estilo de petição complexa (proposta honorários, esclarecimento, impugnação, laudo complementar) precisa de mais peças para extrair — ver `cowork/06-APRENDIZADO/ANALISE-BANCO-MODELOS.md`.
