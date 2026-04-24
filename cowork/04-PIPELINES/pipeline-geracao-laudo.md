---
nome: pipeline-geracao-laudo
entrada: _dados/FICHA.json + exames/notas-exame.md + quesitos (em FICHA ou arquivo próprio)
saida: laudo/LAUDO-<YYYY-MM-DD>.md + laudo/LAUDO-<YYYY-MM-DD>.pdf
duracao_estimada: 8-20 min
agentes_envolvidos: [redator-laudo-pericial, revisor-laudo-pericial, peticao-gerador-pdf]
---

# Pipeline 3 — Geração de Laudo

## Objetivo

Produzir laudo pericial completo (6 seções canônicas), revisado automaticamente e entregue em PDF timbrado, a partir da FICHA do caso, notas manuscritas/ditadas do exame físico e quesitos das partes. Saída tem que ser juridicamente utilizável: sem lacunas, sem contradição entre histórico e conclusão, todos os quesitos respondidos.

## Pré-requisitos

- Pipeline 1 concluído (`_dados/FICHA.json` válido).
- `exames/notas-exame.md` preenchido — anotações do exame físico, anamnese, achados, documentos médicos periciados.
- Quesitos disponíveis em `FICHA.json` (`quesitos.juizo`, `quesitos.autor`, `quesitos.reu`) ou em `_dados/quesitos.md`.
- Templates de laudo por CID/patologia em `10-PERICIA/templates-reaproveitaveis/laudos/` (ver `project_pericias_reaproveitaveis.md`).
- Agentes `redator-laudo-pericial`, `revisor-laudo-pericial`, `peticao-gerador-pdf` disponíveis.
- Pasta `laudo/` criada no caso.

## Passos

### 1. Seleção de template por CID/patologia
- **Ação**: ler `FICHA.cid_suspeitos` + `notas-exame.md` (diagnóstico definitivo). Escolher template correspondente em `templates-reaproveitaveis/laudos/`.
- **Tool**: `Bash` (`ls`) + `Read`.
- **Regra**: CID principal da conclusão do exame tem prioridade sobre CID suspeito inicial. Se não houver template específico, usar `laudo-generico.md`.
- **Escreve**: `laudo/.tmp/template-escolhido.txt` (path + justificativa).
- **Sucesso**: template apontado existe.

### 2. Consolidação de insumos
- **Ação**: juntar em um único JSON de contexto tudo que o redator precisa: dados da FICHA, notas do exame, quesitos, documentos médicos citados.
- **Tool**: `Bash` (merge) + `Write`.
- **Escreve**: `laudo/.tmp/contexto-laudo.json`.
- **Sucesso**: JSON válido com campos `ficha`, `exame`, `quesitos`, `documentos_citados`.

### 3. Redação por seção
- **Ação**: `redator-laudo-pericial` produz as 6 seções canônicas, na ordem:
  1. **Preâmbulo** — identificação do perito, processo, partes, data de nomeação, data da perícia.
  2. **Histórico** — anamnese e história da doença, baseada em `notas-exame.md`.
  3. **Exame físico / complementares** — achados objetivos + documentos médicos periciados (com data, emissor, CID).
  4. **Discussão / fundamentação** — correlação clínica, nexo, literatura quando aplicável.
  5. **Conclusão** — CID definitivo, capacidade/incapacidade, grau, temporalidade, DII e DID.
  6. **Resposta aos quesitos** — cada quesito transcrito literalmente + resposta objetiva, agrupados por origem (juízo/autor/réu).
- **Agente**: `redator-laudo-pericial`.
- **Tool**: `Task`.
- **Lê**: `contexto-laudo.json`, template escolhido.
- **Escreve**: `laudo/.tmp/LAUDO-draft.md`.
- **Sucesso**: 6 cabeçalhos `##` presentes, nenhum quesito sem resposta.

### 4. Revisão automática
- **Ação**: `revisor-laudo-pericial` passa o draft por checklist:
  - Coerência histórico ↔ conclusão.
  - CID citado na conclusão aparece também no exame físico.
  - Todos os quesitos das 3 listas (juízo/autor/réu) respondidos; resposta em 1ª pessoa ou impessoal, nunca mista.
  - DII e DID presentes e plausíveis (DII ≤ data da perícia; DID ≤ DII).
  - Sem expressões juridicamente arriscadas (“simulação”, “má-fé” etc.) a não ser com fundamento explícito.
  - Sem lacunas de placeholder.
- **Agente**: `revisor-laudo-pericial`.
- **Tool**: `Task`.
- **Escreve**: `laudo/.tmp/revisao.json` com lista de achados (nível: bloqueante, atenção, estilo).
- **Sucesso**: zero achados `bloqueante`. Atenção/estilo são aceitáveis mas devem constar.

### 5. Aplicação de correções
- **Ação**: se houver `bloqueante`, `redator-laudo-pericial` reescreve as seções afetadas; volta ao passo 4. Máximo 2 iterações — na 3ª, abortar e escalar para Dr. Jesus revisar manualmente (feedback_max_2_retries).
- **Tool**: `Task`.
- **Escreve**: `laudo/LAUDO-<YYYY-MM-DD>.md` (versão final).
- **Sucesso**: passagem do passo 4 com zero bloqueantes.

### 6. Geração de PDF timbrado
- **Ação**: converter MD em PDF com timbrado pericial (cabeçalho: nome + CRM + título “Laudo Pericial”; rodapé: CNJ + página X de Y).
- **Agente**: `peticao-gerador-pdf` (reuso — gera qualquer PDF timbrado do sistema).
- **Tool**: `Task`.
- **Escreve**: `laudo/LAUDO-<YYYY-MM-DD>.pdf`.
- **Sucesso**: PDF existe, ≥3 páginas, timbrado em todas as páginas, texto extraível.

### 7. Registro e notificação
- **Ação**: registrar em `_dados/HISTORICO-LAUDOS.md` + atualizar `DIARIO-PROJETOS.md`.
- **Tool**: `Edit`.
- **Sucesso**: linha nova em ambos os arquivos.

## Pontos de verificação

| # | Checagem | Comando | Esperado |
|---|----------|---------|----------|
| V1 | MD tem as 6 seções canônicas | `grep -c '^## ' LAUDO.md` | ≥6 |
| V2 | Sem placeholders órfãos | `grep -c '{{' LAUDO.md` | 0 |
| V3 | CID da conclusão aparece no exame físico | `grep <cid> LAUDO.md \| wc -l` | ≥2 |
| V4 | Todos os quesitos do juízo respondidos | contagem em FICHA vs respostas | igual |
| V5 | Todos os quesitos do autor respondidos | idem | igual |
| V6 | Todos os quesitos do réu respondidos | idem | igual |
| V7 | DII e DID presentes | `grep -Ei '(DII|data.?do.?in[ií]cio.?da.?incapacidade)' LAUDO.md` | ≥1 cada |
| V8 | PDF ≥3 páginas, texto extraível | `pdfinfo PDF; pdftotext PDF - \| wc -c` | páginas≥3, chars≥2000 |
| V9 | Revisão sem bloqueantes | `jq '.[] \| select(.nivel=="bloqueante")' revisao.json` | vazio |
| V10 | `HISTORICO-LAUDOS.md` atualizado | `tail -1 _dados/HISTORICO-LAUDOS.md` | contém data+CNJ |

Só declarar “feito” após V1–V10 OK. Qualquer falha ⇒ laudo não sai da pasta `.tmp/`.

## Erros comuns + fix

1. **Quesito do réu não respondido** (o réu às vezes protocola quesitos depois) → `redator-laudo-pericial` deve varrer `_dados/` por `quesitos*.md` e `FICHA.quesitos.reu`. Se aparecerem após o laudo pronto, gerar laudo complementar (não reabrir o original).
2. **Contradição histórico ↔ conclusão** (ex.: histórico fala em dor lombar, conclusão cita ombro) → revisor bloqueia. Causa típica: `notas-exame.md` incompleto. Voltar ao exame, completar notas, reprocessar.
3. **CID definitivo ≠ CID suspeito da FICHA** → normal após exame. Atualizar `FICHA.json` com `cid_definitivo` (campo adicional) e documentar mudança na discussão.
4. **DII anterior à DID** (impossível) → bloqueio automático. Revisar datas nas notas do exame e documentos médicos.
5. **Template específico inexistente para a patologia** → usar `laudo-generico.md` + registrar em `templates-reaproveitaveis/REGISTRO.md` como template faltante (para criar depois).

## Exemplo executado — caso 0000000-00.0000.0.00.0000

1. `FICHA.cid_suspeitos=["M54.5","F33.1"]`. Após exame, diagnóstico definitivo: M54.5 (lombalgia crônica) como principal, F33.1 (depressão recorrente) como secundário. `notas-exame.md` preenchido com anamnese, exame físico (Lasègue +, amplitude reduzida), RM lombar (hérnia L4-L5), PHQ-9 = 17.
2. Template escolhido: `templates-reaproveitaveis/laudos/lombalgia-cronica-M54.md`. Justificativa: CID principal da conclusão.
3. `contexto-laudo.json` montado com FICHA + notas + 3 quesitos do juízo + 5 do autor + 2 do réu.
4. `redator-laudo-pericial` produz draft com 6 seções, 11 páginas estimadas.
5. `revisor-laudo-pericial` aponta 2 achados de atenção (estilo) e 0 bloqueantes. OK.
6. PDF gerado: `laudo/LAUDO-2026-04-20.pdf`, 9 páginas, 412 KB, timbrado OK, texto extraível 18.234 chars.
7. V1–V10 passam. Conclusão do laudo: “Incapacidade parcial e permanente para atividade habitual (motorista de caminhão), DII em 12/01/2025, DID em 10/2024.”
8. `HISTORICO-LAUDOS.md` recebe: `2026-04-20 | 0000000-00.0000.0.00.0000 | LAUDO-2026-04-20.pdf | incapacidade-parcial-permanente`.
9. Pipeline 3 concluído em 11 min 47 s (1 iteração de revisão).
