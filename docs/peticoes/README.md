# Petições — catálogo

Documentação por tipo de petição que o perito envia ao juízo. Cada arquivo explica: o que é, quando usar, placeholders obrigatórios, exemplo real, comando para gerar.

**Fonte dos templates**: `cowork/02-BIBLIOTECA/peticoes/{subtipo}/TEMPLATE.md`.
**Motor de preenchimento**: `cowork/05-AUTOMACOES/scripts/aplicar_template.py` (lê FICHA.json, substitui `{{placeholders}}`, escreve `.md` final).

---

## Tipos documentados (com TEMPLATE.md real)

| Subtipo | Duração | Quando usar em 1 linha | Doc |
|---|---|---|---|
| **Aceite** | 15 min | Juiz nomeou o perito, aguarda confirmação. | [aceite.md](aceite.md) |
| **Agendamento** | 15 min | Comunicar data/horário/local da perícia ao juízo. | [agendamento.md](agendamento.md) |
| **Escusa** | 10 min | Recusar nomeação por impedimento/suspeição/motivo técnico (CPC 157). | [escusa.md](escusa.md) |
| **Proposta de honorários** | 5 min | Juiz pediu proposta de valor em petição separada do aceite (CPC 465 §2º I). | [proposta-honorarios.md](proposta-honorarios.md) |

---

## Tipos ainda sem TEMPLATE.md (pendentes de criação)

Estes subtipos foram mencionados como úteis mas **não têm** `TEMPLATE.md` em `cowork/02-BIBLIOTECA/peticoes/`. Até existirem, não há o que documentar aqui. Criar o TEMPLATE primeiro, depois o doc correspondente em `Maestro/docs/peticoes/`.

| Subtipo | Quando seria usada | Prioridade sugerida |
|---|---|---|
| `complementar` | Juiz pede laudo complementar (dúvida sanada sem nova perícia). | média |
| `esclarecimento` | Parte/juiz pede esclarecimento pontual sobre trecho do laudo. | alta (recorrente) |
| `impugnacao-quesitos` | Perito impugna quesitos das partes (vagos, impertinentes, fora do escopo). | média |
| `majoracao-honorarios` | Perito pede aumento do valor já fixado (complexidade não prevista, diligência extra). | alta |
| `mutirao` | Petições em lote para perícias em regime de mutirão. | baixa |
| `reagendamento` | Remarcar data da perícia (ausência da parte, incompatibilidade). | média (recorrente) |
| `resposta-impugnacao` | Perito responde a impugnação de parte contra o laudo. | alta |

### Variantes por classe (dentro de `proposta-honorarios/`)
Também pendentes — ver `cowork/02-BIBLIOTECA/peticoes/proposta-honorarios/README.md`:
- `erro-medico/`
- `securitario/`
- `previdenciario/`
- `trabalhista/`
- `civel-dano-pessoal/`
- `dpvat/`

---

## Fluxo padrão (ordem cronológica num processo típico)

```
Nomeação do juiz
   │
   ├── aceite (simples OU condicionado)   ← perito confirma
   │     OU
   └── escusa                             ← perito recusa (fim)

Após aceite:
   │
   ├── proposta-honorarios                ← se juiz ainda não fixou
   │
   ├── agendamento                        ← data/local
   │
   ├── [reagendamento]                    ← se necessário (PENDENTE)
   │
   ├── perícia realizada → LAUDO
   │
   ├── [esclarecimento]                   ← resposta a pedido (PENDENTE)
   ├── [resposta-impugnacao]              ← resposta a impugnação (PENDENTE)
   ├── [complementar]                     ← se juiz determinar (PENDENTE)
   │
   └── [majoracao-honorarios]             ← se diligência extra justificar (PENDENTE)
```

---

## Como usar o motor

```bash
python3 "/Users/jesus/Desktop/STEMMIA Dexter/cowork/05-AUTOMACOES/scripts/aplicar_template.py" \
  --template "/Users/jesus/Desktop/STEMMIA Dexter/cowork/02-BIBLIOTECA/peticoes/<subtipo>/TEMPLATE.md" \
  --ficha "<path>/FICHA.json" \
  --saida "<path>/peticoes-geradas/<subtipo>.md"
```

FICHA.json exemplo: `cowork/05-AUTOMACOES/scripts/FICHA-EXEMPLO.json`.
