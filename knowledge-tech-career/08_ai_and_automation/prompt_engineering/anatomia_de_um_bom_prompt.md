---
titulo: Anatomia de um bom prompt
bloco: 08_ai_and_automation
tipo: tecnica
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: pratica-consolidada
tempo_leitura_min: 5
---

# Anatomia de um bom prompt

## Cinco componentes obrigatórios

1. **Papel (role)** — identidade profissional e postura. Ex.: "Você é perito médico judicial, CRM ativo, atua em Varas da Fazenda Pública de MG."
2. **Contexto (context)** — fatos do caso. Processo, partes, fase, documentos disponíveis.
3. **Objetivo (task)** — UMA ação clara e mensurável.
4. **Restrições (constraints)** — o que não fazer, limites, escopo.
5. **Formato de saída (output format)** — JSON schema, markdown com seções fixas, tabela, XML.

Faltando qualquer um = prompt ambíguo = saída inconsistente.

## Template base (Claude XML)

Claude responde melhor a estruturação em XML tags. Template para perícia:

```xml
<role>
Perito médico judicial, CRM-MG ativo, nomeado em Vara Cível.
Atua em danos pessoais, nexo causal, incapacidade laborativa.
Tom técnico seco, sem eufemismo. Sem disclaimer.
</role>

<context>
Processo: {numero_cnj}
Vara: {vara}
Partes: autor {autor}, réu {reu}
Fase: {fase}
Documentos anexos:
  - Laudo médico assistente: <doc id="laudo_assistente">{texto}</doc>
  - Exames: <doc id="exames">{texto}</doc>
  - Prontuário: <doc id="prontuario">{texto}</doc>
</context>

<task>
Extrair todos os quesitos formulados pelas partes e pelo juízo.
Para cada quesito, indicar: autor, número, texto literal, tipo
(técnico / jurídico / misto), viabilidade de resposta pelo perito médico.
</task>

<constraints>
- Não inventar quesitos. Só extrair o que consta literalmente.
- Se um quesito aparecer em mais de uma peça, agrupar e listar todas as ocorrências.
- Não responder os quesitos nesta etapa.
- Se texto ambíguo: marcar {viabilidade: "ambiguo"} e transcrever trecho.
</constraints>

<output_format>
JSON conforme schema:
{
  "quesitos": [
    {
      "id": "Q01",
      "autor": "autor | reu | juizo",
      "numero_original": "string",
      "texto_literal": "string",
      "tipo": "tecnico | juridico | misto",
      "viabilidade": "responde | ambiguo | fora_escopo",
      "trecho_fonte": "citação literal com referência de peça"
    }
  ]
}
</output_format>
```

## Princípios de redação

- **Imperativo direto**: "Extrair X." > "Por favor, você poderia tentar extrair X?"
- **Uma tarefa por chamada**: prompts que pedem 5 coisas produzem 5 respostas medíocres. Encadear agentes.
- **Especificidade vence verbosidade**: "listar medicamentos com dose e via" > "descrever tratamento".
- **Exemplo > descrição** quando a saída é complexa (ver `few_shot_e_chain_of_thought.md`).
- **Restrições negativas sempre com alternativa positiva**: em vez de "não use adjetivos", "use apenas substantivos e verbos". (ver `anti_padroes_prompt.md`).
- **Ordem importa**: Claude respeita mais instruções no topo e no fim do prompt. Documentos no meio, instruções finais no fim.

## Lista de verificação antes de enviar

- [ ] Papel definido?
- [ ] Contexto completo ou há RAG ligado?
- [ ] Objetivo singular e mensurável?
- [ ] Formato de saída estrito (schema, seções fixas)?
- [ ] Tratamento de ausência previsto ("se não consta, responder X")?
- [ ] Temperature adequada (0 para extração, 0.1–0.2 para redação)?

## Referências

- Anthropic, "Prompt engineering overview". [TODO/RESEARCH: URL atual]
- White et al., "A Prompt Pattern Catalog", 2023.
