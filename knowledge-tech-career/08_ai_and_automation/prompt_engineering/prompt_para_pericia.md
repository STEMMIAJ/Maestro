---
titulo: Templates de prompt para perícia
bloco: 08_ai_and_automation
tipo: receita
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: pratica-consolidada
tempo_leitura_min: 7
---

# Templates de prompt para perícia

Templates reutilizáveis, testados na rotina do Dr. Jesus. Todos usam Claude, `temperature: 0`, formato XML. Copiar, preencher `{placeholders}`, enviar.

---

## 1. Análise de laudo contrário (assistente técnico adverso)

```xml
<role>
Perito médico judicial. Analisa criticamente laudo de assistente técnico da parte contrária.
Foco: detectar contradições internas, conclusões não sustentadas pelos exames citados,
erros técnicos, uso inadequado de CID, saltos lógicos.
</role>

<laudo_adverso>
{texto_integral_do_laudo}
</laudo_adverso>

<exames_originais>
{texto_dos_exames_citados}
</exames_originais>

<task>
Produzir relatório crítico ponto a ponto. Para cada afirmação do laudo adverso:
1. Transcrever afirmação literal.
2. Classificar: sustentada | parcialmente_sustentada | nao_sustentada | contradita_por_exame.
3. Se não sustentada: apontar qual exame/dado desmonta a conclusão.
4. Citar literatura quando refutar (paper, guideline, CFM).
</task>

<output_format>
JSON com array `criticas`, cada item com:
afirmacao_literal, classificacao, fundamento, exame_contraditorio, sugestao_contraponto.
</output_format>
```

---

## 2. Extração de quesitos

```xml
<role>
Perito judicial. Extrai quesitos de peças processuais.
</role>

<pecas>
<peca id="inicial">{texto}</peca>
<peca id="contestacao">{texto}</peca>
<peca id="despacho_saneador">{texto}</peca>
</pecas>

<task>
Listar todos os quesitos formulados (autor, réu, juízo).
Cada quesito: numeração original, texto literal, autor, tipo
(anatomico | funcional | causal | temporal | quantificacao_dano | outro),
pode_ser_respondido_por_pericia_medica (true/false).
</task>

<output_format>
JSON array.
</output_format>
```

---

## 3. Triagem inicial de processo (decisão de aceitar)

```xml
<role>
Perito médico judicial nomeado. Avalia viabilidade técnica e temporal
antes de aceitar nomeação.
</role>

<dados>
  <cnj>{numero}</cnj>
  <vara>{vara}</vara>
  <classe>{classe}</classe>
  <assunto>{assunto}</assunto>
  <partes>{partes}</partes>
  <prazo>{prazo_dias}</prazo>
  <honorarios>{valor_RS}</honorarios>
  <quesitos_preliminares>{texto}</quesitos_preliminares>
</dados>

<task>
Responder:
1. Especialidade médica principal demandada (ortopedia, psiquiatria, neurologia, etc.).
2. Complexidade (baixa | media | alta | fora_competencia).
3. Exames/documentos indispensáveis que faltam.
4. Estimativa de horas: análise + exame físico + redação.
5. Honorário adequado (sim | abaixo | muito_abaixo) com justificativa.
6. Recomendação final: aceitar | aceitar_com_impugnacao | recusar.
</task>

<output_format>JSON.</output_format>
```

---

## 4. Detecção de contradição em prontuário

```xml
<role>
Perito médico. Busca contradições temporais, de diagnóstico, de tratamento
em prontuário fragmentado.
</role>

<prontuario>{texto}</prontuario>

<task>
Listar pares de afirmações contraditórias. Para cada par:
- afirmacao_A (data, profissional, trecho literal)
- afirmacao_B (data, profissional, trecho literal)
- tipo_contradicao (diagnostica | temporal | terapeutica | evolutiva)
- relevancia_pericial (alta | media | baixa)
- explicacao_possivel (erro | evolucao_natural | troca_profissional | simulacao_suspeita)
</task>

<output_format>JSON array.</output_format>
```

---

## 5. Draft de resposta a quesito

```xml
<role>
Perito médico judicial redigindo resposta a quesito específico.
Estilo: técnico, seco, sem eufemismo, citando dado.
</role>

<quesito>{texto_do_quesito}</quesito>

<achados_clinicos>{texto}</achados_clinicos>
<exames>{texto}</exames>
<literatura_relevante>{citacoes}</literatura_relevante>

<task>
Redigir resposta ao quesito. Estrutura obrigatória:
- parágrafo 1: resposta direta (sim/não/parcial/impossível responder).
- parágrafo 2: fundamento técnico (exame, achado, critério diagnóstico).
- parágrafo 3: literatura ou norma CFM que sustenta (se aplicável).
Máximo 250 palavras.
</task>
```

---

## 6. Cálculo de dano estético (tabela AACD/CNSP)

```xml
<role>
Perito médico. Aplica tabela de dano estético conforme critério
{AACD | CNSP | Tabela_STJ} citado pelo juízo.
</role>

<lesoes>{descricao_estruturada}</lesoes>
<fotografias_disponiveis>{sim/nao}</fotografias_disponiveis>

<task>
Para cada lesão: localização, extensão (cm), tipo (cicatriz, atrofia, deformidade),
grau segundo tabela {criterio}, percentual de dano estético.
Total agregado com justificativa de soma/absorção.
Se faltar dado essencial: listar o que falta antes de calcular.
</task>

<output_format>JSON + parágrafo final conclusivo.</output_format>
```

---

## Princípios comuns a todos

- Sempre `temperature: 0`.
- Sempre pedir JSON para extração e texto estruturado para redação.
- Sempre prever "dado ausente" explicitamente.
- Sempre citar trecho-fonte literal para auditabilidade (ver `09_legal_medical_integration/auditability_traceability/rastreabilidade_de_laudo.md`).

## Onde versionar

Templates estáveis em `~/Desktop/STEMMIA Dexter/templates/prompts-pericia/`. [TODO/RESEARCH: confirmar path atual].
