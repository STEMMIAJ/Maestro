# IDEIA PARA PRÓXIMA SESSÃO — Proposta de honorários por classe

**Anotado em:** 2026-04-20 (durante criação do cowork/)
**Fonte:** pedido explícito do usuário em sessão de criação
**Status:** PENDENTE — não executar nesta sessão, executar na próxima

---

## O pedido (palavras do usuário, síntese)

> "Proposta de honorários precisa de padrão. A depender do caso eu tenho que colocar isso no pipeline. Se for caso de erro médico não vai ter apólice de seguro. Se for caso securitário pode ser que tenha apólice, aí tem assistente técnico. Preciso justificar ao juiz a complexidade — puxar do CFM o CRM, RQE, especialidade do médico-réu para fundamentar. Cada classe eu tenho que avaliar certas coisas."

---

## Escopo do trabalho pendente

### Mapear classes processuais e o que diferencia cada uma

Para cada classe, responder: **o que precisa ser avaliado para justificar honorários?** (complexidade, nº partes, nº documentos, nº quesitos, nº apólices, existência de AT, necessidade de exame físico, deslocamento, urgência, especialidade rara).

Classes iniciais a cobrir:

| Classe | Apólice? | Assistente Técnico? | Variáveis-chave únicas |
|---|---|---|---|
| **Erro médico** | Não (em geral) | Frequente (autor e réu) | CRM/RQE do réu, especialidade, gravidade do dano, nº lesões, nexo causal contestado |
| **Securitário (DPVAT / seguro privado)** | Sim | Possível | Nº apólices, valor segurado, franquia, cláusulas discutidas, perícia em boletim + prontuário + laudo anterior |
| **Previdenciário (INSS)** | N/A | Raro | CID, DID (data de início da doença), DII (data início incapacidade), grau de incapacidade, uniprofissional vs omniprofissional |
| **Trabalhista (NTEP/acidente)** | N/A | Possível | CAT, PPP, LTCAT, nexo ocupacional, agente insalubre, concausa |
| **Cível comum (dano pessoal)** | Varia | Varia | Boletim de ocorrência, AIH, tempo de incapacidade temporária/permanente |

### Criar templates por classe

Cada template em `02-BIBLIOTECA/peticoes/proposta/<classe>.md` com placeholders e **blocos condicionais** que só aparecem se aplicável:

```markdown
{{#se:tem_apolice}}
Tratando-se de causa com {{numero_apolices}} apólice(s) de seguro, 
impõe-se análise técnica de cláusulas e eventual cobertura...
{{/se}}

{{#se:tem_assistente_tecnico}}
Há assistente técnico constituído pela parte {{parte_com_at}}, 
o que demanda diligência adicional...
{{/se}}

{{#se:medico_reu_com_rqe}}
O réu possui RQE {{rqe_numero}} — {{especialidade}} —, 
o que exige do Perito expertise equivalente...
{{/se}}
```

### Integração CFM (depende do arquivo `pipeline-integracao-cfm.md`)

Input: nome completo do médico-réu (extraído da petição inicial).
Output: JSON `{ crm, uf, rqe, especialidade, situacao, data_inscricao }`.

Esse JSON vira variável do template da proposta.

### Checklist específico por classe

Cada classe tem um checklist pré-proposta que o sistema roda automaticamente e exibe ao usuário antes de emitir. Exemplo (erro médico):

- [ ] Li petição inicial? (verificado: `documentos-recebidos/*inicial*`)
- [ ] Identifiquei médico-réu? (verificado: `_dados/FICHA.json:medico_reu`)
- [ ] Busquei no CFM? (verificado: `_dados/cfm-medico-reu.json` existe)
- [ ] Identifiquei nº quesitos? (verificado: `_dados/FICHA.json:quesitos_total`)
- [ ] Tem AT do autor? AT do réu?
- [ ] Estimei nº lesões/cirurgias/internações a analisar?

### Calculadora de complexidade

Scorer simples (0-100) que lê a FICHA e devolve um grau de complexidade → vira base de honorários:

```
score = nº_quesitos×2 + nº_documentos×0.1 + nº_apolices×5 
      + (tem_AT ? 10 : 0) + nº_partes×3 + urgencia_peso
```

Faixas: 0-30 simples (honorário base), 31-60 médio (1.5×), 61-100 alto (2-3×).

---

## Por que fica para próxima sessão

- Usuário cansado (ditado por voz, dor crônica, fim de turno cognitivo)
- Exige decisões sobre valores base e multiplicadores — só usuário decide
- Precisa material empírico: 5-10 propostas antigas **por classe** para calibrar
- Precisa testar integração CFM antes (rate limit, captcha, login?)

## O que fazer ANTES da próxima sessão (tarefa do usuário)

- [ ] Subir 5-10 propostas antigas de **cada classe** em `cowork/02-BIBLIOTECA/peticoes/_corpus-estilo/proposta/<classe>/`
- [ ] Decidir **valor-base de honorários** por classe (ou deixar que o sistema infira do histórico)
- [ ] Validar lista de classes acima — falta algum tipo de caso que você recebe?

## O que o sistema fará na próxima sessão

1. Extrair padrões das propostas antigas por classe (o extrator já está especificado em `03-IDENTIDADE/guia-extracao-estilo.md`)
2. Gerar template por classe em `02-BIBLIOTECA/peticoes/proposta/<classe>.md`
3. Criar scorer de complexidade em `05-AUTOMACOES/scripts/`
4. Ligar ao pipeline `pipeline-proposta-honorarios.md`

---

**NÃO APAGAR ATÉ EXECUTADO.** Checklist de saída desta tarefa: templates por classe criados + scorer testado em 1 caso real + CFM integrado.
