# Teste do motor aplicar_template.py

## Rodada 1 — 2026-04-20, v0.1 (placeholders simples + lista + data)

| Template | RC | Saída vs. original |
|---|---|---|
| `peticoes/aceite/TEMPLATE.md` | 0 | **IDÊNTICA** ao Aceite-Mantena.docx |
| `peticoes/aceite/TEMPLATE-condicionado.md` | 0 | **IDÊNTICA** ao Petição-de-Aceite-Mantena.docx (inclui R$ 1.500,00) |
| `peticoes/agendamento/TEMPLATE.md` | 0 | Data/hora/dia preenchidos; referências do prédio mantidas |

### Evidência (aceite simples, saída exata)

```
AO JUÍZO DA 2ª VARA CÍVEL, CRIMINAL E DA INFÂNCIA E DA JUVENTUDE DA COMARCA DE MANTENA – MG

Processo nº: 0038122-07.2012.8.13.0396

MANIFESTAÇÃO – ACEITE DE ENCARGO E HONORÁRIOS

Meritíssimo Juiz,

Em atenção à(s) decisão/intimação de ID 10637932621 e ID 10639375978, venho ratificar meu aceite dos encargos e honorários periciais. Aguardo os trâmites necessários para prosseguir com o agendamento da perícia médica, caso não haja suspeição ou impedimento sobre minha atuação.

Termos em que,
Pede deferimento.

Dr. Jésus Eduardo Nolêto da Penha
Médico - Perito Judicial – CRM-MG 92.148
Membro da ABMLPM - Associação Brasileira de Medicina Legal e Perícia Médica

17 de março de 2026, Governador Valadares - MG.
```

## Rodada 2 — 2026-04-20, v0.2 (+ condicional + rastreabilidade)

Motor estendido com `{{#se:path}}...{{/se}}`, `{{#se-nao:path}}...{{/se-nao}}` e comentário HTML de rastreabilidade ao fim do output.

**Comando base:**
```
python3 aplicar_template.py --template <tpl> --ficha <ficha> --data "20 de abril de 2026"
```

### Bateria completa — 6/6 RC=0

| # | Template | Ficha | RC | bytes | stderr | `[[FALTA]]` |
|---|---|---|---|---|---|---|
| 1 | aceite/TEMPLATE.md | FICHA-EXEMPLO.json | 0 | 950 | 0 linhas | 0 |
| 2 | aceite/TEMPLATE-condicionado.md | FICHA-EXEMPLO.json | 0 | 1019 | 0 linhas | 0 |
| 3 | agendamento/TEMPLATE.md | FICHA-EXEMPLO.json | 0 | 1332 | 0 linhas | 0 |
| 4 | escusa/TEMPLATE.md | FICHA-EXEMPLO-escusa.json | 0 | 1533 | 0 linhas | 0 |
| 5 | proposta-honorarios/civel-dano-pessoal/TEMPLATE.md | FICHA-EXEMPLO-civel-simples.json | 0 | 1629 | 0 linhas | 0 |
| 6 | proposta-honorarios/civel-dano-pessoal/TEMPLATE.md | FICHA-EXEMPLO-civel-complexo.json | 0 | 2159 | 0 linhas | 0 |

### Verificação semântica dos condicionais (proposta cível)

Ficha "simples" (sem `honorarios.justificativa_complexidade`, `partes.autor.beneficio_justica_gratuita=false`):
- Output contém `"depositar o valor em juízo"` (1x) — bloco `{{#se-nao:gratuidade}}` ativado ✓
- Output NÃO contém `"Justificativa de complexidade"` — `{{#se:complexidade}}` inibido ✓
- Output NÃO contém `"Tratando-se de beneficiário"` — `{{#se:gratuidade}}` inibido ✓

Ficha "complexo" (com `justificativa_complexidade` preenchido, `beneficio_justica_gratuita=true`):
- Output NÃO contém `"depositar o valor em juízo"` — `{{#se-nao:gratuidade}}` inibido ✓
- Output contém `"Justificativa de complexidade"` (1x) — `{{#se:complexidade}}` ativado ✓
- Output contém `"Tratando-se de beneficiário"` (1x) — `{{#se:gratuidade}}` ativado ✓

### Rastreabilidade confirmada

Exemplo do comentário injetado ao fim:
```
<!-- gerado por aplicar_template.py v0.2.0 em 2026-04-20T20:19:27-0300 | template=<path> | ficha=<path> -->
```

### Testes unitários do condicional

7/7 passaram:
1. `{{#se:x}}YES{{/se}}` com `x=True` → `YES` ✓
2. Com `x=False` → vazio ✓
3. Com chave ausente → vazio ✓
4. Multilinha dentro de `{{#se:}}` ✓
5. `{{#se-nao:x}}` inverso de `{{#se:x}}` ✓
6. `{{#se:nome}}Olá, {{nome}}!{{/se}}` compõe ✓
7. `_truthy`: None/False/""/[]/{}/0 → False; resto → True ✓

## Cobertura atual

- Placeholders simples `{{a.b.c}}` ✅
- Lista com prefixo/separador `{{#lista:path:prefixo="...":separador="..."}}` ✅
- Data do sistema `{{data.por_extenso}}` ✅
- Bloco condicional `{{#se:cond}}...{{/se}}` e `{{#se-nao:cond}}...{{/se-nao}}` ✅
- Rastreabilidade automática (HTML comment com versão, timestamp, paths) ✅
- Detecção de placeholder faltante → vira `[[FALTA:path]]` + aviso no stderr ✅
- Frontmatter YAML removido automaticamente ✅

## Pendente

- Condicionais aninhados (MVP atual não suporta)
- Conversão MD → DOCX com timbrado (pandoc ou python-docx)
- Integração com o pipeline CFM (pega RQE do médico-réu e injeta em FICHA)
- Templates ainda não criados: majoracao-honorarios, impugnacao-quesitos, esclarecimento, complementar, mutirao, laudos/*, respostas/*
