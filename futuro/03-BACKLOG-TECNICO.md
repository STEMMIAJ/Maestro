# Backlog tecnico — Maestro

## 2026-04-23

### Alta prioridade (desbloqueiam fluxo operacional)
- [ ] B003 Implementar scripts reais: `ingest_conversation.py`, `chunk_conversation.py`, `extract_action_items.py`, `generate_memory_files.py`, `generate_session_checkpoint.py`.
- [ ] B011 Instalar OpenClaw via npm (`npm i -g openclaw`) — ACEITO pelo Dr. Jesus em 2026-04-23.
- [ ] B012 Rodar `openclaw onboard` para configurar backend (Claude/OpenAI/local).
- [ ] B013 Conectar OpenClaw aos arquivos do Maestro (MEMORY.md, tasks, agents).

### Media
- [ ] B005 Escolher DB definitivo (hoje: SQLite+JSON hibrido como recomendacao).
- [ ] B006 Implementar dashboard MVP (HTML vanilla, 1 rota, JSON estatico).
- [ ] B007 Ativar bot Telegram — aguardando TOKEN + CHAT_ID.

### Baixa
- [ ] B002 Baixar doc oficial OpenClaw (agora que URL confirmado: https://openclaw.ai e https://github.com/openclaw/openclaw).
- [ ] B008 Rodar agente DEXTER-AUDITOR.
- [ ] B009 Migrar dados para Supabase (so quando dashboard exigir queries dinamicas).
- [ ] B010 Integrar com banco-de-dados existente (pasta banco-de-dados/ em Dexter).

### Script taiobeiras_status.py — refino pendente (sessao Taiobeiras)
- [ ] B014 Refinar score do `taiobeiras_status.py`: restringir busca de marcadores de aceite a janela de +/- 40 linhas ao redor do nome do perito (JESUS EDUARDO NOLETO DA PENHA) — hoje 14 processos caem em ACEITE-PROVAVEL por falso positivo (ex: despacho judicial mencionando "aceite" e "mutirao" conta como aceite). (contexto: sessao 23/abr, rodada 1 retornou 8 OK / 14 PROVAVEL / 2 SEM / 0 falha — PROVAVEL alto demais)
- [ ] B015 Cruzar resultado do script com aceites ja REDIGIDOS fora dos autos (raiz `~/Desktop/ANALISADOR FINAL/ACEITE-TAIOBEIRAS-*.{pdf,docx}`, `~/Desktop/STEMMIA Dexter/AUTOMACAO/PROTOCOLAR-AGORA/ACEITE-TAIOBEIRAS-*.pdf`, `FERRAMENTAS/analisador-novo/04-modelos-peticao/ACEITE-*.md`) — gerar 3 niveis: `ACEITE-NOS-AUTOS` (ja protocolado) / `ACEITE-REDIGIDO-FALTA-PROTOCOLAR` / `SEM-ACEITE-REDIGIR`. (contexto: 5001309-57.2025.8.13.0680 saiu como SEM-ACEITE mas tem PDF redigido na raiz — PDF dos autos foi baixado antes do protocolo)
- [ ] B016 Confirmar manualmente os 2 casos SEM-ACEITE: 5001309-57.2025.8.13.0680 e 5002175-65.2025.8.13.0680 — verificar se precisam de peticao nova ou se o aceite ja foi protocolado apos o download dos autos. (contexto: sessao 23/abr)
- [ ] B017 Apos refinar (B014+B015), reprocessar os 14 ACEITE-PROVAVEL e listar somente os que realmente precisam de peticao nova. (contexto: objetivo final da sessao 23/abr que nao foi fechado)
- [ ] B018 Integrar o script no `gerar_visao_unificada.py` (AUTOMACAO/) para que `MEUS-PROCESSOS.md` inclua bloco Taiobeiras detalhado. (contexto: hoje MEUS-PROCESSOS.md usa estados genericos, nao distingue "redigido-falta-protocolar")

### Sessao pausada — expansao banco laudos + skill checkpoint (2026-04-23 01:21)
- [ ] B019 Retomar handoff em `Maestro/tarefas-em-andamento/2026-04-23_0121__expansao-banco-laudos-e-skill-checkpoint.md` — despachar Time A (Fase 1 do `playful-pondering-rabbit.md`, cria skill `enviar-tarefas-em-andamento` com 6 arquivos) e Time B (Fase 0 do `populacao-banco-laudos-mg.md`, gera `_INVENTARIO-BASELINE-2026-04-23.json` + `anel_geografico.json` mapeando 853 comarcas MG em 8 aneis a partir de GV) em paralelo num unico turno. (contexto: dois planos aprovados via ExitPlanMode na sessao 23/abr 01h, ambos travados aguardando "ok fase N" por enforcement TEMPLATE-PLANO.md; pastas disjuntas → seguro paralelizar)

### Criar templates de peticoes a partir de pecas reais (sessao 20-23/abr 2026)
- [ ] B020 Quando Dr. Jesus subir pecas reais em `cowork/05-AUTOMACOES/orquestrador/INBOX/`, rodar `python3 orquestrador.py --workers 4` e validar classificacao automatica. Orquestrador v0.1 ja testado com 3 DOCX reais (aceite 6.0, aceite 6.0, agendamento 5.0), idempotencia SHA-256 verificada. (contexto: sessao 20/abr — pipeline pronto, aguardando pecas)
- [ ] B021 Apos ingestao, criar as 6 clausulas-padrao INVARIANTES (enderecamento, identificador-processo, vocativo, fecho, assinatura, data-local) em `cowork/02-BIBLIOTECA/clausulas-padrao/` a partir dos 3 DOCX originais ja no corpus. Fase 6 do PLANO-EXTRACAO-TEMPLATES.md. (contexto: extraivel hoje, nao depende de pecas novas)
- [ ] B022 Decidir Opcao A (clausulas-padrao inline no TEMPLATE.md, zero infra extra) vs Opcao B (sintaxe `{{#incluir:clausulas-padrao/X}}` estendendo motor). Recomendacao atual: comecar com A. (contexto: decisao pendente do Dr. Jesus — ver PLANO-EXTRACAO-TEMPLATES.md Fase 4)
- [ ] B023 Refazer templates marcados `INVENTADO-NAO-USAR-*` com base em pecas reais: `peticoes/escusa/`, `peticoes/proposta-honorarios/civel-dano-pessoal/`, mais 3 FICHAs de exemplo em `scripts/`. REGRA ZERO: nenhum template sem peca real como base. (contexto: erro cometido em 20/abr — templates inventados a partir de CPC generico violaram regra do projeto; user identificou e exigiu segregacao)
- [ ] B024 Subtipos pendentes de template (aguardando pecas): proposta-honorarios (erro-medico, securitario, previdenciario, trabalhista, dpvat), esclarecimento, majoracao-honorarios, impugnacao-quesitos, manifestacao-complementar, mutirao, laudo-pericial, respostas-quesitos. (contexto: Dr. Jesus tem que subir ≥2 DOCX/PDF de cada antes de criar template — ideal 3+)
- [ ] B025 Scripts auxiliares a criar apos ingestao: `extrair_texto_docx.py` reusavel, `extrair_texto_pdf.py`, `analisar_subtipo.py` (diff entre 2+ pecas do mesmo subtipo), `docx_para_template_esqueleto.py`. (contexto: hoje extracao DOCX esta embutida no orquestrador, precisa virar util chamavel)
- [ ] B026 Integracao MD→DOCX com timbrado automatico (pandoc ou python-docx) + MD→PDF. Skill `/novo-caso <CNJ>` que copia `_TEMPLATE-CASO/` para `01-CASOS-ATIVOS/<CNJ>/`. (contexto: TIER 2 infra solo, nao bloqueia extracao de templates)

### Sessao propostas-honorarios Taiobeiras — mapeamento 24 processos + pipeline audit (2026-04-23)
Mapeamento consolidado em `~/Desktop/_MESA/30-DOCS/planos-acao/MAPEAMENTO-FLUXOS-TAIOBEIRAS-2026-04-22.md` (172 linhas). Classificacao: Grupo A (21) interdicao AJ-TJMG tabela R$ 612 piso / Grupo B (1) interdicao custeada partes valor livre / Grupo C (1) securitaria Mongeral sem JG valor livre / Grupo D (1) seguro vida Mongeral JG contestada proposta condicional.
- [ ] B027 Gerar proposta Grupo C — CNJ 5000416-08.2021.8.13.0680 (cobranca securitaria Mongeral, valor causa R$ 137.973,97, sem JG, CID M23.3 joelho, quesitos IMEP juntados) — valor LIVRE R$ 3.500-6.000, template `PERICIA FINAL/templates/proposta/proposta-securitaria.md` (pronto), agente `gerador-peticao-complexo`, verificador `orquestrador-verificacao-proposta`. (contexto: prioridade 1 — maior valor livre)
- [ ] B028 Gerar proposta Grupo D — CNJ 5003080-41.2023.8.13.0680 (seguro vida Mongeral Apolice 106085372 OURO VIDA GRUPO, R$ 118.653, autor alegou JG, re impugnou — decisao pendente) — proposta CONDICIONAL 2 faixas: tabela R$ 612 + majoracao CGJ OU livre R$ 3.000-5.000. Verificar ultimo despacho JG antes de entregar. (contexto: prioridade 2)
- [ ] B029 Gerar proposta Grupo B — CNJ 5003293-13.2024.8.13.0680 (interdicao CUSTEADA PELAS PARTES, GRCTJ paga) — valor LIVRE R$ 2.000-4.000 fundamentado por dimensoes (hora tecnica AMB/CBHPM, deslocamento, horas estimadas leitura+exame+laudo+quesitos, possibilidade impugnacao re). Template: adaptar proposta-securitaria removendo clausulas apolice. (contexto: prioridade 3)
- [ ] B030 Gerar 6 propostas Grupo A SEM aceite — CNJs 5000792-52.2025, 5002175-65.2025, 5003685-50.2024, 5003880-69.2023, 5004205-10.2024, 5004301-88.2025 — decidir por processo: valor-piso R$ 612 (rapido) OU pleito majoracao 2,5x-5x (R$ 1.530-3.060) fundamentado CGJ-MG (deslocamento rural Taiobeiras 600+km BH, exame domiciliar quando acamado, multiplos CIDs/comorbidades, idade extrema >80 ou menor com deficiencia severa). (contexto: historico Vara Unica Taiobeiras = R$ 612 uniforme n=6 casos 2021-2025, cross-check `banco-de-dados/Banco-Transversal/Honorarios-Periciais/Casos-Reais/Norte-Mineiro/taiobeiras-vara-unica-consolidado-0680.md`)
- [ ] B031 Auditoria pipeline-proposta-honorarios: criar TEMPLATE.md para classe `interdicao-curatela` em `cowork/02-BIBLIOTECA/peticoes/proposta-honorarios/` — hoje inexistente, 21 de 24 processos Taiobeiras sao interdicao. Variaveis: diagnostico, idade, mobilidade, quesitos, deslocamento, exame-domiciliar, fundamentacao-majoracao-CGJ, valor-base, valor-pleito. (contexto: classe mais usada e sem template — gap critico descoberto em 23/abr)
- [ ] B032 Auditoria pipeline: implementar scorer de complexidade 0-100 (input: FICHA.json, output: simples/medio/complexo → roteia para `gerador-peticao-simples`/`medio`/`complexo`) em `cowork/05-AUTOMACOES/scripts/`. Hoje nao existe, decisao e subjetiva. (contexto: dependencia central do pipeline oficial mas nao bloqueia hoje)
- [ ] B033 Auditoria pipeline: criar agente `cfm-buscador` (consulta CRM/RQE do medico reu em processos de erro medico) em `~/.claude/agents/`. (contexto: dependencia do pipeline mas irrelevante para Taiobeiras — zero erros medicos na lista)
- [ ] B034 Auditoria pipeline: preencher templates vazios em `cowork/02-BIBLIOTECA/peticoes/proposta-honorarios/{erro-medico,previdenciario,trabalhista,dpvat}/` — hoje so tem README, falta TEMPLATE.md por classe. Migrar/adaptar templates ja existentes em `PERICIA FINAL/templates/proposta/proposta-securitaria.md` e `proposta-erro-medico.md` para schema do cowork. (contexto: securitario ja usa o template legado — migracao nao-bloqueante)
- [ ] B035 Revisar 15 aceites Grupo A ja gerados em `Modelos-gerados-pelo-Cowork/aceites-taiobeiras-2026-04-22/` — decidir se precisam proposta complementar ou se aceite ja contem valor implicito (R$ 612). (contexto: baixa prioridade apos B027-B030)
