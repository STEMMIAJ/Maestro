---
titulo: Casos de uso de IA em perícia
bloco: 09_legal_medical_integration
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: pratica-consolidada
tempo_leitura_min: 7
---

# Casos de uso de IA em perícia

Lista priorizada por ROI real para o Dr. Jesus. Cada item: tarefa, técnica, agente Dexter associado, ganho esperado, risco a mitigar.

---

## 1. Extração de quesitos

- **Tarefa**: identificar e estruturar todos os quesitos (autor, réu, juízo) em peças processuais.
- **Técnica**: Claude Sonnet/Opus + prompt estruturado + JSON schema + few-shot com casos borderline.
- **Agente**: `analisador-quesitos-auto`.
- **Ganho**: 30–60 min por processo → 2–5 min.
- **Risco**: perder quesito formulado em forma oblíqua ("esclareça se…"). Mitigação: verificador cruzado que conta quesitos e compara com texto.

## 2. Detecção de contradições internas

- **Tarefa**: pares de afirmações contraditórias em prontuário, laudos anteriores, depoimentos.
- **Técnica**: chunking por peça + LLM juiz comparando pares + classificação (temporal, diagnóstica, terapêutica).
- **Agente**: `detetive-inconsistencias`.
- **Ganho**: descobre contradições que olho humano cansado perde em prontuário de 500 páginas.
- **Risco**: falso positivo por paráfrase inócua. Mitigação: exigir citação literal dos dois trechos.

## 3. Cálculo de dano estético / funcional

- **Tarefa**: aplicar tabelas (AACD, CNSP, STJ) a lesões descritas.
- **Técnica**: extração estruturada das lesões → regra determinística em Python → LLM valida coerência + gera justificativa.
- **Gargalo a mitigar**: LLM sozinho não confia em regra fechada; Python calcula, LLM justifica.
- **Risco**: hibridização mal feita → inconsistência. Mitigação: Python é fonte de verdade; LLM só redige.

## 4. Primeiro draft de laudo

- **Tarefa**: gerar esqueleto do laudo com anamnese, exame físico, exames complementares, discussão, conclusão.
- **Técnica**: template markdown + ficha.json + few-shot de laudos anteriores + Opus + verificadores.
- **Agente**: `redator-laudo` → `revisor-laudo`.
- **Ganho**: economiza 2–4h de redação; Dr. Jesus foca na discussão clínica.
- **Risco**: redação "bonita" sem substância. Mitigação: redator é proibido de afirmar nada sem fonte_id.

## 5. Auditoria de CID

- **Tarefa**: validar que CID citado (no laudo, no prontuário, no atestado) existe, é compatível com a descrição, está vigente (CID-10 vs CID-11).
- **Técnica**: lookup determinístico em tabela CID + LLM classifica compatibilidade texto ↔ código.
- **Agente**: `verificador-cids`.
- **Ganho**: evita CID errado em laudo assinado (erro comum, reputacionalmente custoso).
- **Risco**: LLM discordar de médico em caso sutil. Mitigação: sinalizar, não bloquear.

## 6. Busca de jurisprudência pericial

- **Tarefa**: achar acórdãos relevantes ao caso (mesmo CID + incapacidade; mesma classe + dano moral; nexo similar).
- **Técnica**: RAG híbrido (BM25 + vetor) em corpus versionado de acórdãos; rerank; LLM cita.
- **Agente**: `orq-jurisprudencia` (3 buscadores paralelos) + `buscador-tribunais`.
- **Ganho**: citação jurídica que sustenta laudo; melhora aceitação pelo juízo.
- **Risco**: alucinação de acórdão (grave). Mitigação: verificador-de-fontes obrigatório.

## 7. Triagem inicial de nomeação

- **Tarefa**: decidir em minutos se vale aceitar (especialidade compatível, prazo factível, honorários adequados).
- **Técnica**: DataJud + `orq-analise-rapida` + prompt #3.
- **Agente**: `triador-peticao` + `detector-urgencia`.
- **Ganho**: evita aceitar caso fora de escopo; evita recusar por distração.
- **Risco**: informação incompleta no DataJud. Mitigação: exigir confirmação humana antes de aceitar formalmente.

## 8. Extração de quesitos implícitos / mal formulados

- **Tarefa**: quando juiz ou parte formula pergunta ambígua, interpretar múltiplas leituras.
- **Técnica**: CoT + self-consistency (3 interpretações) + nota de ambiguidade.
- **Ganho**: evita responder à pergunta errada.
- **Risco**: pareceres divergentes. Mitigação: devolver ao juízo pedido de esclarecimento.

## 9. Sumarização de processo gigante

- **Tarefa**: processo de 5000+ páginas virou dossiê de 5 páginas com cronologia, partes, pedidos, teses.
- **Técnica**: Gemini 2.5 Pro (janela 1M) para leitura bruta; Opus refina; dossiê estruturado em markdown.
- **Agente**: `resumidor-fatos` + `orq-analise-completa`.
- **Ganho**: entendimento do caso em 15 min vs 4 horas.
- **Risco**: perder peça crítica. Mitigação: indexação completa em RAG para consulta pontual posterior.

## 10. Transcrição estruturada do exame presencial

- **Tarefa**: áudio da consulta → texto → preenchimento automático de campos da ficha.json.
- **Técnica**: Whisper local (ou API) para transcrição; Claude extrai campos.
- **Ganho**: elimina a etapa manual mais cansativa pós-exame.
- **Risco**: terminologia médica mal transcrita. Mitigação: prompt com glossário + validação contra lista de CIDs/medicamentos conhecidos.

## 11. Resposta a impugnação de laudo

- **Tarefa**: impugnação chega da parte contrária; responder ponto a ponto com fundamento.
- **Técnica**: `orq-analise-documento` na impugnação + `verificador-cruzado` do laudo original vs pontos impugnados + redação de resposta.
- **Ganho**: horas de análise → 30 min com revisão.
- **Risco**: resposta defensiva demais (tom). Mitigação: role enfatizar "técnico seco, sem defensividade".

## 12. Draft de manifestação aos quesitos complementares

- **Tarefa**: juiz ou partes formulam novos quesitos; responder com base no laudo já entregue + exames.
- **Técnica**: RAG no próprio processo + prompt #5 (resposta a quesito).
- **Ganho**: resposta rápida antes do prazo curto.
- **Risco**: contradizer laudo anterior sem perceber. Mitigação: `verificador-cruzado` roda sempre.

## 13. Geração de roteiro pericial personalizado

- **Tarefa**: antes do exame presencial, gerar checklist de anamnese e exame físico específico àquele caso.
- **Técnica**: ficha.json + quesitos + literatura específica → roteiro em markdown imprimível.
- **Agente**: `gerador-roteiro-pericial`.
- **Ganho**: exame mais focado, menos esquecimento.

## 14. Busca semântica no próprio acervo

- **Tarefa**: "já vi caso parecido com este CID + perfil ocupacional?".
- **Técnica**: RAG em base local com laudos passados (anonimizados se necessário) + filtros por CID/vara.
- **Agente**: `buscador-base-local`.
- **Ganho**: reuso de raciocínio já produzido.
- **Risco**: copy-paste inadequado a caso diferente. Mitigação: usar como referência, não template direto.

## Priorização

| # | Caso | Impacto | Implementação | Status |
|---|------|---------|---------------|--------|
| 1 | Extração quesitos | Alto | Feito | Produção |
| 9 | Sumarização | Alto | Feito | Produção |
| 6 | Jurisprudência | Alto | Feito | Produção |
| 4 | Draft laudo | Alto | Parcial | Refinar discussão |
| 2 | Contradições | Médio | Feito | Calibrar |
| 5 | Auditoria CID | Médio | Feito | OK |
| 10 | Transcrição exame | Alto | Iniciar | Pendente |
| 11 | Resposta impugnação | Médio | Parcial | Iterar |

## Referências

- `~/.claude/agents/` — lista completa.
- `agent_systems/agentes_no_dexter.md`.
