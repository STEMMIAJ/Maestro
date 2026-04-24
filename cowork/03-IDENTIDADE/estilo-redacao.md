# Estilo de Redação — Jurídico/Pericial

> Template de escolhas. Marque `[x]` na opção desejada. Enquanto não marcar, vale o DEFAULT indicado. O agente de redação consulta este arquivo antes de gerar qualquer peça.

> Este arquivo complementa `perfil-estilo.json` (extraído do corpus real). Quando há conflito, a escolha manual aqui prevalece.

---

## 1. Tratamento ao juiz (vocativo da petição)

- [ ] A) Excelentíssimo Senhor Doutor Juiz de Direito da {{VARA}}
- [ ] B) Excelentíssimo(a) Senhor(a) Doutor(a) Juiz(a) Federal da {{VARA}}
- [ ] C) MM. Juiz(a)
- [ ] D) Meritíssimo(a)
- [x] DEFAULT: A para Estadual, B para Federal, até escolher outro

## 2. Forma de referência ao juiz no corpo do texto

- [ ] A) Vossa Excelência
- [ ] B) V. Exa.
- [ ] C) esse Juízo
- [x] DEFAULT: B (V. Exa.) em primeira menção; "esse Juízo" nas demais

## 3. Vocativo e referência aos advogados das partes

- [ ] A) ilustre patrono / ilustre patrona
- [ ] B) douto advogado / douta advogada
- [ ] C) nobre causídico
- [ ] D) apenas "advogado(a) da parte autora/ré"
- [x] DEFAULT: D (neutro e sem adjetivo)

## 4. Pessoa verbal usada pelo perito

- [ ] A) 1ª pessoa do singular ("analisei", "concluí")
- [ ] B) 1ª pessoa do plural de modéstia ("analisamos")
- [ ] C) 3ª pessoa técnica: "o Perito signatário", "o subscritor", "este Perito"
- [ ] D) impessoal ("foi analisado", "constatou-se")
- [x] DEFAULT: C em laudo, D em quesitos, A vedada

## 5. Auto-designação preferida (escolher 1 principal)

- [ ] A) "o Perito"
- [ ] B) "o Perito signatário"
- [ ] C) "o subscritor"
- [ ] D) "este Perito"
- [ ] E) "o Perito nomeado"
- [x] DEFAULT: B em abertura, A no corpo, E quando reforçar investidura

## 6. Numeração de parágrafos

- [ ] A) Todos numerados (1., 2., 3., ...)
- [ ] B) Apenas tópicos principais numerados, subparágrafos sem número
- [ ] C) Sem numeração, apenas quebras
- [x] DEFAULT: B

## 7. Títulos de seção em laudo

- [ ] A) CAIXA ALTA, negrito, numerado romano (I. IDENTIFICAÇÃO)
- [ ] B) Title Case, negrito, numerado arábico (1. Identificação)
- [ ] C) minúsculo, negrito, sem numeração
- [x] DEFAULT: A

## 8. Citação de jurisprudência — formato

- [ ] A) Tribunal, órgão, número do processo, relator, data de julgamento, data de publicação
- [ ] B) Tribunal, número do processo, relator, data de julgamento
- [ ] C) Ementa integral + referência completa em nota de rodapé
- [x] DEFAULT: A no corpo; ementa só quando central ao argumento

## 9. Citação de doutrina

- [ ] A) Autor, obra em itálico, edição, editora, ano, página
- [ ] B) Autor (ano, p. X), referência completa em bibliografia final
- [ ] C) Apenas citação em nota de rodapé
- [x] DEFAULT: A em laudo; B em parecer acadêmico

## 10. Uso de latim (ex vi, data venia, in casu, mutatis mutandis)

- [ ] A) Permitido sem restrição
- [ ] B) Permitido com moderação (máx. 2 ocorrências por peça)
- [ ] C) Proibido
- [x] DEFAULT: B, sempre em itálico

## 11. Uso de grifos e destaques

- [ ] A) Negrito para tese, itálico para latim, sublinhado proibido
- [ ] B) Negrito para conclusões, sem itálico
- [ ] C) Sem grifos no corpo; destaque só em conclusão
- [x] DEFAULT: A

## 12. Conectores preferidos (marcar todos que usa naturalmente)

- [ ] isto posto
- [ ] ante o exposto
- [ ] diante do exposto
- [ ] nesse sentido
- [ ] nesse diapasão
- [ ] destarte
- [ ] outrossim
- [ ] cumpre salientar
- [ ] cumpre registrar
- [ ] impende observar
- [ ] não obstante
- [ ] com efeito
- [x] DEFAULT: usar apenas os marcados; nunca "diapasão", "destarte", "outrossim" sem marcação

## 13. Termos PROIBIDOS (nunca aparecem na peça)

- "salvo melhor juízo" (fragiliza conclusão pericial)
- "acreditamos que", "pensamos que" (perito não acredita, constata)
- "parece-me", "ao que tudo indica" (vago)
- "muito embora"
- emojis, exclamação, interrogação retórica
- adjetivos valorativos sobre a parte ("infeliz", "coitado", "flagrante má-fé")
- gerundismo ("vou estar analisando")
- Incluir termos adicionais a evitar: {{TERMOS_ADICIONAIS_EVITAR}}

## 14. Fecho padrão

- [ ] A) "Nestes termos, pede deferimento."
- [ ] B) "Termos em que, pede deferimento."
- [ ] C) "Nestes termos, aguarda deferimento."
- [ ] D) "É o laudo. Submete-se à apreciação de V. Exa."
- [x] DEFAULT: D em laudo, B em petição simples

## 15. Bloco de assinatura

- [x] DEFAULT (editável em `dados-profissionais.md`):

```
{{CIDADE}}, {{DATA_POR_EXTENSO}}.


{{NOME_PROFISSIONAL}}
Médico — CRM/{{CRM_UF_NUMERO}} — RQE {{RQE_NUMERO}}
Perito judicial nomeado
```

## 16. Assinatura digital vs. manuscrita

- [ ] A) Sempre certificado ICP-Brasil (PAdES)
- [ ] B) Manuscrita digitalizada colada em PDF
- [ ] C) Ambas (ICP no PDF + manuscrita visual)
- [x] DEFAULT: A para peças protocoladas; C quando o juízo exige imagem

## 17. Linguagem médica no laudo

- [ ] A) Termos técnicos sempre com tradução entre parênteses na primeira menção
- [ ] B) Termos técnicos sem tradução (destinatário é operador do Direito)
- [ ] C) Glossário ao final
- [x] DEFAULT: A no corpo + C ao final quando há mais de 10 termos

## 18. CID e códigos

- [ ] A) CID-10 sempre
- [ ] B) CID-11 sempre
- [ ] C) CID-10 principal + CID-11 entre parênteses
- [x] DEFAULT: A até migração oficial do Brasil para CID-11

## 19. Referência a exames

- [ ] A) Nome do exame, data, laboratório, número de registro, achado relevante
- [ ] B) Nome do exame, data, achado
- [x] DEFAULT: A (rastreabilidade máxima)

## 20. Comprimento de parágrafo (regra)

- [ ] A) Máx. 3 linhas, ideia única
- [ ] B) Máx. 5 linhas
- [ ] C) Sem limite
- [x] DEFAULT: A (leitura rápida pelo juízo)
