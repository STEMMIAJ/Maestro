---
nome: peticoes-proposta-honorarios
proposito: Propostas de honorários por classe processual, com blocos condicionais
---

# Proposta de honorários — por classe

Uma subpasta por classe processual. Cada uma com template próprio porque **as variáveis que justificam complexidade são diferentes** (ver `06-APRENDIZADO/IDEIA-proposta-honorarios-por-classe.md`).

## Subpastas

| Classe | Variáveis-chave únicas |
|---|---|
| `erro-medico/` | CRM/RQE do réu, especialidade, gravidade do dano, nº lesões, nexo contestado |
| `securitario/` | Nº apólices, valor segurado, franquia, cláusulas, boletim + prontuário + laudo anterior |
| `previdenciario/` | CID, DID, DII, grau incapacidade, uni vs omniprofissional |
| `trabalhista/` | CAT, PPP, LTCAT, agente insalubre, concausa |
| `civel-dano-pessoal/` | Boletim, AIH, incapacidade temporária/permanente |
| `dpvat/` | Tabela SUSEP, invalidez parcial, documentação mínima |

## Formato do TEMPLATE.md

```markdown
---
subtipo: proposta-honorarios
classe: erro-medico
variaveis_requeridas:
  - processo.cnj
  - juiz.nome_tratamento  # "Vossa Excelência", "MM. Juiz(a)"
  - medico_reu.crm
  - medico_reu.rqe
  - medico_reu.especialidade
  - complexidade.score
  - apolice.existe  # boolean
  - at.existe       # boolean
duracao_bloco: 40min
---

# [Cabeçalho timbrado gerado automaticamente]

EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA {{vara}} — {{comarca}}

Processo: {{processo.cnj}}

O PERITO signatário, já qualificado nos autos, vem respeitosamente apresentar **PROPOSTA DE HONORÁRIOS**, nos seguintes termos:

## I — DA COMPLEXIDADE DO FEITO

{{#se:medico_reu.rqe}}
Trata-se de ação indenizatória por alegado erro médico, em que o réu possui Registro de Qualificação de Especialista (RQE {{medico_reu.rqe}}) em {{medico_reu.especialidade}}, o que exige do Perito avaliação técnica equivalente à especialidade discutida.
{{/se}}

{{#se:apolice.existe}}
Há {{apolice.numero}} apólice(s) de seguro nos autos, cuja análise contratual integra o trabalho pericial.
{{/se}}

{{#se:at.existe}}
Constituído(s) assistente(s) técnico(s) pela(s) parte(s), o que demanda diligência adicional para eventuais impugnações e esclarecimentos.
{{/se}}

## II — DO VALOR

Considerando a complexidade acima e a Resolução CFM/CNJ aplicável, proponho o valor de **R$ {{honorario_valor}}** ({{honorario_valor_extenso}}), nos termos do art. 465, §3º, CPC.

[... fecho ...]
```

## Como o motor preenche

1. Pipeline `pipeline-proposta-honorarios.md` lê `FICHA.json` do caso
2. Calcula `complexidade.score` via `05-AUTOMACOES/scripts/scorer_complexidade.py` (a criar)
3. Se a classe exige CFM → chama `pipeline-integracao-cfm.md` → obtém RQE/especialidade
4. Renderiza template com bloco condicional expandido só onde houver dado
5. Aplica timbrado → PDF em `01-CASOS-ATIVOS/<CNJ>/peticoes-geradas/`

## Ordem de criação dos templates (prioridade)

1. `erro-medico/` — mais frequente, mais complexo (bom teste do motor)
2. `securitario/` — segunda frequência
3. `previdenciario/` — template mais simples, serve de baseline
4. Resto conforme casos reais chegarem
