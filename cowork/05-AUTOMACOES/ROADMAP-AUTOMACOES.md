# Roadmap de Automações — STEMMIA Dexter

Versão: 2026-04-20. Escopo: automações para reduzir carga manual do fluxo pericial (captação → laudo → arquivo). Alvo: médico perito autista+TDAH com dor ortopédica crônica. Princípio: cada clique a menos vale mais que cada feature nova.

---

## Seção 1 — 10 automações propostas, ordenadas por ROI (impacto/esforço)

### 1. `/novo-caso <numero-cnj>`

- **Tipo**: slash-command (arquivo em `~/.claude/commands/novo-caso.md`)
- **Gatilho**: usuário digita `/novo-caso 0001234-56.2026.8.13.0024`
- **Entrada**: número CNJ; opcional: PDF inicial em `INBOX/`
- **Saída**: pasta `cowork/01-CASOS-ATIVOS/<numero>/` clonada de `_TEMPLATE-CASO/` + `FICHA.json` populada com campos básicos (autor, réu, vara, classe, assunto) via MCP PJe ou busca-processos-judiciais
- **Cola com**: `_TEMPLATE-CASO/`, MCP `pje-mcp`, MCP `mcp-brasil` (busca-processos-judiciais), agente `captador-processo` se existir
- **ROI**: 8 min economizados/caso × ~5 casos/semana = 40 min/semana
- **Complexidade**: trivial
- **Pré-requisitos**: `_TEMPLATE-CASO/` consolidado; esquema `FICHA.json` fechado; MCP PJe configurado

### 2. `/dashboard`

- **Tipo**: slash-command + script Python de leitura
- **Gatilho**: usuário digita `/dashboard`
- **Entrada**: varre `cowork/01-CASOS-ATIVOS/*/FICHA.json`
- **Saída**: tabela markdown no chat (caso, fase, próximo prazo, pendência mais antiga, dias parado)
- **Cola com**: `FICHA.json` (campo `status`, `proximo_prazo`, `ultima_acao`); opcional banco SQLite do projeto `unificacao_stemmia`
- **ROI**: evita abrir 10 pastas manualmente. 15 min/dia × 5 dias = 75 min/semana
- **Complexidade**: trivial
- **Pré-requisitos**: `FICHA.json` com schema consistente em todos os casos ativos

### 3. `/intimacao`

- **Tipo**: skill (`~/.claude/skills/intimacao/SKILL.md`)
- **Gatilho**: usuário digita `/intimacao` colando texto, ou informa caminho de PDF
- **Entrada**: texto ou PDF da intimação
- **Saída**: bloco estruturado (tipo, prazo em dias corridos/úteis, data-limite, ação sugerida, CID ou quesitos se houver); grava em `01-CASOS-ATIVOS/<num>/intimacoes/<data>.md`
- **Cola com**: Comunica PJe (quando ativo), agente `classificador-intimacao` se existir, bot Telegram para alerta
- **ROI**: 10 min/intimação × 8/semana = 80 min/semana
- **Complexidade**: média (parsing de prazos CNJ)
- **Pré-requisitos**: tabela de mapeamento tipo de ato → prazo padrão; regex para CNJ

### 4. Hook `post-write-inbox` (triagem automática)

- **Tipo**: hook PostToolUse
- **Gatilho**: qualquer Write/mv em `cowork/INBOX/**`
- **Entrada**: arquivo novo (PDF, DOCX, imagem, texto)
- **Saída**: classificação (intimação / laudo externo / exame / contrato / outro) gravada em `INBOX/_triagem.jsonl`; se intimação → dispara `/intimacao` automaticamente; se exame → move para caso correspondente se número CNJ detectado
- **Cola com**: `ocr-watchdog-inbox` (seção 2), MCP OCR se disponível
- **ROI**: elimina passo "o que é isso que caiu aqui?". 5 min × 10 itens/semana = 50 min/semana
- **Complexidade**: média
- **Pré-requisitos**: OCR funcionando para PDFs escaneados; regras de classificação em JSON

### 5. `/peticao <tipo>`

- **Tipo**: skill
- **Gatilho**: usuário digita `/peticao manifestacao-quesitos` dentro da pasta do caso
- **Entrada**: `FICHA.json` do caso corrente + template em `02-BIBLIOTECA/templates-peticoes/<tipo>.md`
- **Saída**: arquivo timbrado em `peticoes-geradas/<data>-<tipo>.md` com placeholders substituídos; opcional PDF via pandoc
- **Cola com**: agente `peticao-montador` existente (NÃO duplicar lógica — chamar), identidade visual em `03-IDENTIDADE/`
- **ROI**: 30 min/petição × 4/semana = 120 min/semana (maior ROI da lista)
- **Complexidade**: média
- **Pré-requisitos**: biblioteca de templates; `peticao-montador` com contrato de entrada definido

### 6. `/laudo`

- **Tipo**: skill
- **Gatilho**: usuário digita `/laudo` dentro da pasta do caso
- **Entrada**: `FICHA.json` (CID, queixa, histórico, exame físico ditado), templates em `_MESA/10-PERICIA/templates-reaproveitaveis/`, quesitos do processo
- **Saída**: esqueleto de laudo em `laudo/<data>-draft.md` com seções pré-preenchidas; modo "continuar" detecta draft existente e retoma do ponto
- **Cola com**: script `usar_template_pericia.py` existente, agente `laudo-revisor`, hook anti-mentira
- **ROI**: 60 min de setup/laudo × 3 laudos/semana = 180 min/semana (co-maior ROI)
- **Complexidade**: média
- **Pré-requisitos**: templates por CID em versão final; contrato com `usar_template_pericia.py`

### 7. Hook `post-write-peticao` (verificação automática)

- **Tipo**: hook PostToolUse
- **Gatilho**: Write em `**/peticoes-geradas/*.md`
- **Entrada**: arquivo recém-gravado
- **Saída**: roda agente `peticao-verificador` (checa timbre, CNJ correto, partes corretas, data, CID, ausência de placeholders `{{...}}` sobrando); grava parecer em `peticoes-geradas/_verificacao-<arquivo>.md`
- **Cola com**: agente `peticao-verificador`, hook anti-mentira
- **ROI**: evita enviar petição com placeholder. 1 acidente evitado/mês = muito alto (custo reputacional)
- **Complexidade**: trivial (só amarrar evento → agente)
- **Pré-requisitos**: agente verificador existente

### 8. `/arquivar <numero>`

- **Tipo**: slash-command
- **Gatilho**: usuário digita `/arquivar 0001234-...`
- **Entrada**: pasta do caso em `01-CASOS-ATIVOS/`
- **Saída**: move para `07-ARQUIVO/<ano-sentença>/<numero>/`; gera `_resumo-encerramento.md`; atualiza índice; registra em banco SQLite
- **Cola com**: `/dashboard` (para o caso sumir da lista ativa), hook anti-limpeza (confirmar antes de mover)
- **ROI**: 10 min/caso × 2 encerramentos/semana = 20 min/semana + higiene mental
- **Complexidade**: trivial
- **Pré-requisitos**: confirmação dupla (não deletar); estrutura `07-ARQUIVO/` por ano

### 9. Cron diário 08:00 — resumo de prazos no Telegram

- **Tipo**: launchd + script Python
- **Gatilho**: diário 08:00
- **Entrada**: `FICHA.json` de todos os casos ativos, campo `proximo_prazo`
- **Saída**: mensagem no bot `@stemmiapericia_bot` (chat_id 8397602236) listando prazos de hoje, amanhã, +3 dias, +7 dias, vencidos
- **Cola com**: bot Telegram existente, `/dashboard`
- **ROI**: prevenção de perda de prazo. Valor assimétrico (1 prazo perdido > 100 horas economizadas)
- **Complexidade**: trivial
- **Pré-requisitos**: `proximo_prazo` populado em `FICHA.json`; launchd funcionando

### 10. Agente semanal `extrator-padroes`

- **Tipo**: agente (rodado por cron semanal)
- **Gatilho**: domingo 22:00
- **Entrada**: casos encerrados na semana em `07-ARQUIVO/`
- **Saída**: relatório em `06-APRENDIZADO/padroes-<semana>.md` (CIDs recorrentes, quesitos repetidos, tempo médio por fase, templates candidatos a atualização)
- **Cola com**: projeto `unificacao_stemmia` (banco SQLite de aprendizado contínuo), biblioteca de templates
- **ROI**: compounding — cada semana melhora templates. 0 min/semana inicialmente, 10-20 min/semana de melhoria composta
- **Complexidade**: alta
- **Pré-requisitos**: banco SQLite operacional; casos encerrados com metadados completos

---

## Seção 2 — Sugestões extras (não pedidas)

### A. `voice-to-ficha` — ditado durante exame físico

- **O que faz**: captura áudio durante exame físico (botão físico ou palavra-chave), transcreve (Whisper local ou MCP), mapeia frases faladas em campos do `FICHA.json` (amplitude de movimento, dor, palpação, testes especiais)
- **Por que importa**: TDAH + dor ortopédica crônica tornam datilografia durante exame insustentável. Voz libera as mãos e reduz quebra de atenção entre observar e escrever

### B. `ocr-watchdog-inbox`

- **O que faz**: fsevents em `INBOX/`; todo PDF escaneado passa por OCR (ocrmypdf) antes de qualquer outro hook rodar
- **Por que importa**: perito recebe muito documento escaneado. Sem OCR, classificação automática falha silenciosamente e o caso estagna

### C. `timeline-global`

- **O que faz**: varre todos os casos, extrai datas-chave (distribuição, nomeação, aceite, laudo, esclarecimentos, sentença), renderiza HTML D3 com linha do tempo por caso
- **Por que importa**: autismo beneficia de visualização espacial. Ver "onde eu estou" em cada caso reduz ansiedade e sobrecarga

### D. `comparador-laudo-processo`

- **O que faz**: após gerar laudo, agente lê peças principais do processo e sinaliza contradições (ex.: laudo diz "sem trauma prévio" mas petição inicial menciona acidente em 2019)
- **Por que importa**: memória comprometida + sobrecarga = risco real de contradição involuntária. Catch antes de protocolar preserva credibilidade pericial

### E. `calendar-prazos-cnj`

- **O que faz**: toda vez que `proximo_prazo` muda em qualquer `FICHA.json`, cria/atualiza evento no Google Calendar via MCP, com alerta -48h e -24h
- **Por que importa**: redundância. Telegram + Calendar + dashboard = 3 canais para o mesmo prazo. TDAH exige redundância

### F. `modo-ferias`

- **O que faz**: `/ferias <data-retorno>` consolida todos os casos, gera resumo por caso, identifica prazos que cairão no período, sugere peticionamento de adiamento ou delegação, gera pacote PDF para levar
- **Por que importa**: reduz ansiedade pré-viagem. Checklist objetivo substitui ruminação

### G. `modo-reentrada`

- **O que faz**: `/reentrada` lê último diário, JSONL da última sessão, casos ativos, produz briefing de 10 linhas: "você parou em X, os 3 casos que esfriaram são Y, o prazo mais próximo é Z"
- **Por que importa**: perda de contexto após pausa (fim de semana, férias, pico sensorial) é o maior custo oculto. Briefing de reentrada é o ROI silencioso mais alto

---

## Seção 3 — Integração com sistema existente

| Automação nova | Recurso existente | Onde plugar | Contrato de dados | Cuidados |
|---|---|---|---|---|
| `/novo-caso` | MCP pje-mcp, busca-processos-judiciais | chamada no início do comando | entrada: CNJ string; saída: JSON com autor/réu/vara/classe/assunto | não sobrescrever `FICHA.json` existente; checar duplicata |
| `/peticao` | agente `peticao-montador` | skill apenas orquestra, lógica fica no agente | entrada: `{caso, tipo, ficha}`; saída: path do MD gerado | NÃO duplicar lógica de montagem; skill = wrapper fino |
| `/laudo` | script `usar_template_pericia.py`, agente `laudo-revisor` | skill chama script para esqueleto, depois agente para revisão | entrada: `{ficha, cid, template}`; saída: path do draft | reaproveitar parser de placeholders existente |
| `/intimacao` | bot Telegram, Comunica PJe | skill grava local + aciona bot se urgência alta | entrada: texto ou PDF; saída: JSON estruturado + MD | evitar duplicação com Comunica PJe quando ambos ativos |
| `post-write-peticao` | agente `peticao-verificador` | hook em `settings.json` PostToolUse + matcher de path | entrada: path do MD; saída: parecer MD | hook não pode bloquear — roda async |
| `post-write-inbox` | OCR, agente `classificador-intimacao` | hook PostToolUse + matcher INBOX | entrada: path; saída: classificação + roteamento | depende de OCR concluir antes — encadear via fila |
| `resumo-prazos-8h` | bot Telegram, `FICHA.json` | launchd → script → API Telegram | entrada: leitura de FICHAs; saída: mensagem única consolidada | não enviar se vazio; evitar spam |
| `extrator-padroes` | banco SQLite unificacao_stemmia, templates | agente roda query + gera relatório | entrada: SELECT casos encerrados última semana; saída: MD relatório | não auto-atualizar templates — só propor |
| `/arquivar` | hook anti-limpeza | comando pede confirmação dupla | entrada: CNJ; saída: novo path | palavra-chave `LIMPAR-LIBERADO` não se aplica aqui (mv, não rm) mas pedir confirmação |
| `/dashboard` | `FICHA.json` schema | leitura read-only | entrada: varredura; saída: tabela MD | cache de 60s para não reler tudo a cada chamada |

---

## Seção 4 — Ordem de implementação recomendada

Critério: (a) dependências primeiro, (b) ROI rápido com baixo esforço antes, (c) infraestrutura antes de consumidores.

1. **Schema `FICHA.json` fechado** (pré-requisito transversal). Sem isso, 7 das 10 automações quebram.
2. **`/dashboard`** (trivial, valida schema na prática, ROI imediato).
3. **`/novo-caso`** (trivial, popula o ecossistema com casos bem-formados).
4. **Cron `resumo-prazos-8h`** (trivial, reutiliza bot existente, previne perda de prazo desde o dia 1).
5. **`/arquivar`** (trivial, fecha o ciclo do caso; alimenta `07-ARQUIVO/`).
6. **`/intimacao`** (média, mas alimenta `FICHA.json` com prazos — amplifica ROI do item 4).
7. **Hook `post-write-inbox`** (média, depende de OCR estar OK).
8. **`/peticao`** (média, ROI mais alto da lista; requer biblioteca de templates consolidada).
9. **Hook `post-write-peticao`** (trivial, mas só faz sentido depois que `/peticao` existe).
10. **`/laudo`** (média-alta, depende de `FICHA.json` rica + templates por CID).
11. **Agente `extrator-padroes`** (alta, depende de ter dados acumulados — mínimo 4 semanas de casos encerrados).

Extras na ordem: `modo-reentrada` (2), `voice-to-ficha` (entre 3 e 4 se hardware/API OK), `ocr-watchdog-inbox` (antes do hook 7), `calendar-prazos-cnj` (depois do 4), `timeline-global` (qualquer momento, standalone), `comparador-laudo-processo` (depois do 10), `modo-ferias` (último, depende de tudo anterior).

---

## Seção 5 — Red flags: o que NÃO automatizar

1. **Escolha de CID**. Classificação diagnóstica é ato médico pericial indelegável. Automação pode SUGERIR com base em queixa + exame, nunca decidir.
2. **Interpretação de imagem (RX, RM, TC)**. Mesmo com IA disponível, o laudo pericial depende de correlação clínica que só o perito faz. Automação pode extrair achados do laudo radiológico existente, nunca reinterpretar a imagem.
3. **Nexo causal**. Decisão jurídico-médica. Automação pode montar o raciocínio, perito decide.
4. **Grau de incapacidade / percentual**. Decisão pericial sujeita a sindicância. Nunca deixar automação fixar número.
5. **Envio de petição/laudo ao PJe**. Protocolo é ato que gera efeitos processuais irreversíveis. Exige confirmação humana explícita sempre.
6. **Movimentação/deleção de arquivos de caso**. Hook anti-limpeza já cobre. Reforçar: `/arquivar` move, nunca deleta.
7. **Resposta a quesitos**. Automação pode pré-preencher com base em achados, perito revisa cada um. Nunca publicar sem revisão.
8. **Decisão de aceite/recusa de nomeação**. Envolve agenda, conflito de interesse, complexidade. Humano decide.
9. **Cálculo de honorários**. Vinculado a tabela e resolução CNJ; mudanças frequentes. Automação pode sugerir, perito valida.
10. **Comunicação direta com partes ou advogados fora do processo**. Nunca automatizar. Risco ético.

**Princípio geral**: automação opera nas bordas (captação, preenchimento, verificação, arquivamento, lembrete). O núcleo do ato pericial (diagnóstico, nexo, grau, quesitos) permanece humano com automação como copiloto, nunca piloto.
