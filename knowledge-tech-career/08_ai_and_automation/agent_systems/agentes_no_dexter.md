---
titulo: Inventário de agentes no Dexter
bloco: 08_ai_and_automation
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: inventario-local
tempo_leitura_min: 7
---

# Inventário de agentes no Dexter

Diretório canônico: `~/.claude/agents/`. Total atual: ~85 agentes (CLAUDE.md).

Convenção: todos rodam Opus 4 por padrão (`CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-7`). Jamais rebaixar sem autorização.

## Orquestradores (`orq-*`)

Disparam subagentes em paralelo ou série. Coração do sistema.

- `orq-analise-completa.md` — dossiê completo de processo. Combina extração + resumo + quesitos.
- `orq-analise-documento.md` — análise focada em um documento isolado.
- `orq-analise-rapida.md` — triagem em menos de 1 min.
- `orq-erros-materiais.md` — varredura de erros ortográficos, numéricos, de citação.
- `orq-jurisprudencia.md` — 3 buscadores paralelos (TJMG + STJ + outros).
- `orquestrador-verificacao-proposta.md` — valida proposta antes de executar.

## Buscadores (`buscador-*`)

- `buscador-academico.md` — PubMed + Google Scholar.
- `buscador-base-local.md` — PRIMEIRO a ser chamado (regra CLAUDE.md).
- `buscador-tribunais.md` — jurisprudência em tribunais BR.

## Classificadores (`classificador-*`)

- `classificador-documento.md` — tipo de peça processual.
- `classificador-intencoes.md` — o que o usuário quer.
- `classificador-recursos.md` — categoria de recurso no filesystem.
- `classificador-tipo-acao.md` — classe processual.

## Extratores

- `extrator-informacoes-doc.md` — campos estruturados de documento.
- `extrator-partes.md` — autor, réu, advogados, juiz.
- `analisador-quesitos-auto.md` — detecta e lista quesitos.
- `resumidor-fatos.md` — sumário factual do processo.

## Verificadores (`verificador-*`) — núcleo anti-mentira

- `verificador-100.md` — verificação de 100% dos claims.
- `verificador-cids.md` — CID-10 correto e compatível.
- `verificador-cruzado.md` — bate dado X contra dado Y.
- `verificador-datas.md` — consistência temporal.
- `verificador-de-fontes.md` — fontes citadas existem e dizem o que se afirma.
- `verificador-exames.md` — exame citado existe, tem data, resultado bate.
- `verificador-medicamentos.md` — dose, via, posologia.
- `verificador-nomes-numeros.md` — grafia e numeração.
- `peticao-verificador.md` — auditoria completa de petição/laudo.
- `detetive-inconsistencias.md` — mapeia contradições internas.

## Geradores

- `gerador-peticao-simples.md` / `gerador-peticao-medio.md` / `gerador-peticao-complexo.md` — escala por complexidade.
- `gerador-roteiro-pericial.md` — roteiro para entrevista presencial.
- `redator-laudo.md` — redação do corpo do laudo.
- `revisor-laudo.md` — revisão final.

## Petição (pipeline dedicada)

`peticao-extrator`, `peticao-identificador`, `peticao-montador`, `peticao-conferidor`, `peticao-verificador`, `peticao-gerador-pdf`, `nomeador-peticao`.

## GSD (framework de planejamento) — 20+ agentes

`gsd-planner`, `gsd-executor`, `gsd-verifier`, `gsd-debugger`, `gsd-phase-researcher`, etc. Pipeline completo de gerar-plano → pesquisar → executar → verificar.

## Triagem e roteamento

- `triador-peticao.md`
- `detector-urgencia.md`
- `concierge.md` — ponto de entrada humano.

## Auditoria de estilo

- `auditor-copias-md.md`, `auditor-espacamento.md`, `auditor-estrutura.md`, `auditor-tipografia.md`
- `padronizador-estilo.md`
- `revisor-texto-ditado.md` — corrige transcrições por voz.

## Especializados

- `analista-neurocomportamental.md` — perfil TEA/TDAH do Dr. Jesus aplicado à redação.
- `coach-cognitivo.md` — suporte para gestão cognitiva.
- `capturador-ideias.md` — inbox de ideias.
- `mapeador-provas.md` — quais provas sustentam qual fato.
- `mapeador-habilidades.md` — mantém `MAPEAMENTO-HABILIDADES.md`.
- `diagnosticador-sistema.md` — debug do próprio Dexter.
- `indexador-python-base.md` — indexa PYTHON-BASE/03-FALHAS-SOLUCOES.
- `medidor-tokens.md` — consumo de tokens.
- `supervisor-sistema.md` — supervisiona execução longa.

## Operação de sessão

- `resumo-sessao.md` — gera síntese ao fim.
- `transicao-sessao.md` — handoff entre sessões.

## Design e utilitários

`designer-brief`, `designer-juridico`, `designer-musical`, `designer-nicho`, `bug-hunter-sites`, `clinica-minas-dev`, `pesquisador-produtos`, `tradutor-tecnico`, `transformador-requisitos`.

## Onde ler o fonte

Cada agente é um `.md` com frontmatter YAML (`model`, `description`, `tools`) + system prompt. Editar direto em `~/.claude/agents/<nome>.md`.

## [TODO/RESEARCH]

- Gerar lista completa com count real via `ls ~/.claude/agents/ | wc -l` e sincronizar com este documento automaticamente.
- Criar registro de agentes ÓRFÃOS (criados e não usados há >30 dias) para revisão.
- Mapear quais orquestradores chamam quais subagentes (grafo de dependências).

## Referências

- `~/.claude/docs/SISTEMA-PERICIAS-MAPA-MESTRE.md`
- `~/Desktop/STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA.html`
