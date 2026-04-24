---
nome: indice-biblioteca
proposito: Taxonomia completa de modelos do escritório. Cada subtipo tem pasta própria + corpus-estilo separado.
atualizado: 2026-04-20
---

# BIBLIOTECA — Catálogo de modelos

Fonte única. Nada duplicado. Cada modelo MORA aqui; tudo que usa (pipelines, skills, casos) faz referência.

## Mapa por categoria

### `peticoes/` — tudo que é protocolado como petição
| Subtipo | Pasta | Uso típico | Estado |
|---|---|---|---|
| Aceite | `aceite/` | Aceita nomeação, pode ser simples ou condicionado | vazio |
| Agendamento | `agendamento/` | Marca data/local da perícia | vazio |
| Reagendamento | `reagendamento/` | Remarca após ausência/imprevisto | vazio |
| Escusa | `escusa/` | Recusa a nomeação (impedimento/suspeição/carga) | vazio |
| Proposta honorários | `proposta-honorarios/<classe>/` | Propõe valor + justifica complexidade | **subpastas por classe** |
| Majoração honorários | `majoracao-honorarios/` | Pede aumento após alegar complexidade | vazio |
| Esclarecimento | `esclarecimento/` | Responde quesitos/dúvidas do juiz | vazio |
| Complementar | `complementar/` | Laudo complementar quando sobrevêm fatos | vazio |
| Impugnação quesitos | `impugnacao-quesitos/` | Contra-argumenta quesitos das partes | vazio |
| Resposta impugnação | `resposta-impugnacao/` | Rebate impugnação de laudo | vazio |
| Mutirão | `mutirao/` | Petição em lote em mutirão pericial | vazio |

Subclasses de `proposta-honorarios/`: **erro-medico, securitario, previdenciario, trabalhista, civel-dano-pessoal, dpvat**. Cada uma vai ter template próprio com blocos condicionais (apólice, AT, RQE do médico-réu — ver `06-APRENDIZADO/IDEIA-proposta-honorarios-por-classe.md`).

### `laudos/` — peças técnicas do perito
| Subtipo | Pasta | Particularidade |
|---|---|---|
| Erro médico | `erro-medico/` | Exige discussão de nexo, conduta esperada, dano iatrogênico |
| Securitário | `securitario/` | Cruza boletim + prontuário + apólice; tabela de invalidez SUSEP |
| Previdenciário | `previdenciario/` | CID, DID, DII, grau de incapacidade (uni/omni) |
| Trabalhista | `trabalhista/` | CAT, PPP, LTCAT, concausa |
| Cível dano pessoal | `civel-dano-pessoal/` | Boletim, AIH, temporária vs permanente |
| Psiquiátrico | `psiquiatrico/` | Quando há componente psíquico dominante |

### `respostas/` — reações a atos processuais
| Subtipo | Pasta | Quando usa |
|---|---|---|
| Quesitos suplementares | `quesitos-suplementares/` | Parte apresenta novos quesitos após laudo |
| Impugnação ao laudo | `impugnacao-laudo/` | Parte ou AT impugna conclusão |
| Esclarecimento ao juiz | `esclarecimento-juiz/` | Juiz pede esclarecimento pontual |

### `clausulas-padrao/` — blocos reutilizáveis
Toda peça é montada a partir destes tijolos:
- `preambulo/` — abertura, endereçamento, identificação do processo
- `qualificacao-perito/` — nome, CRM, RQE, endereço pericial, email
- `metodologia/` — exame físico, análise documental, critérios
- `fundamentacao-complexidade/` — justificativa para honorários/majoração
- `nexo-causal/` — cláusulas de nexo (adequada, direta, concausa)
- `avaliacao-dano/` — tabelas de invalidez, graus
- `fecho/` — nestes termos, pede deferimento, assinatura

### `quesitos/` — banco por especialidade
`ortopedia/ psiquiatria/ clinica-geral/ neurologia/ cirurgia-geral/ ginecologia/`

Cada arquivo = conjunto de quesitos-modelo + armadilhas conhecidas + CIDs correlatos.

### `jurisprudencia/` — catálogo próprio
`honorarios/ nexo-causal/ incapacidade/ erro-medico/ previdenciario/`

Cada item: ementa + tribunal + fonte + CONTEXTO ("quando cito isto").

### `doutrina/` — literatura de apoio
`pericia-medica/ responsabilidade-medica/ securitario/`

---

## Convenção de arquivos

```
<subtipo>/
├── TEMPLATE.md           # modelo ativo (gerado/curado)
├── TEMPLATE-v2.md        # se houver revisão, versionar (nunca sobrescrever)
├── placeholders.json     # lista de campos que o motor substitui
└── README.md             # quando usar, cuidados, variantes
```

E o corpus de calibração separado em `_corpus-estilo/<subtipo>/` — é onde o usuário despeja peças antigas para o extrator de padrões aprender o estilo pessoal. **NUNCA** é usado diretamente como template.

---

## Gatilho para análise do corpus (ultrathink)

Ver `06-APRENDIZADO/ANALISE-BANCO-MODELOS.md`. Quando qualquer `_corpus-estilo/<subtipo>/` atingir **30 peças**, hook notifica via Telegram "pronto para análise". Abaixo disso, análise introduz ruído.

---

## Links cruzados

- Pipelines que consomem daqui: `04-PIPELINES/_INDICE.md`
- Plano de popular corpus: `00-INDICE/PLANO-ACAO.md` seção P4
- Ideia CFM/RQE/blocos condicionais: `06-APRENDIZADO/IDEIA-proposta-honorarios-por-classe.md`
- Análise estatística futura: `06-APRENDIZADO/ANALISE-BANCO-MODELOS.md`
