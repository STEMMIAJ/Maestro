# PLANO DE AÇÃO — Escritório Digital COWORK

**Data:** 2026-04-20
**Princípio:** Decidir e executar. Perguntar só o que só o usuário sabe.

---

## FASE 0 — Esqueleto (CONCLUÍDO)

- [x] Pastas criadas em `cowork/`
- [x] Symlinks para `MODELOS PETIÇÕES PLACEHOLDERS`, `LAUDOS-REFERENCIA`, `_MESA/templates`
- [x] README mestre em `00-INDICE/`

---

## FASE 1 — Identidade (PARCIAL — 60% OK em 2026-04-20)

Objetivo: toda petição sai com seu timbrado, assinatura e dados corretos, sem edição manual.

- [x] Timbrado oficial localizado e renomeado → `03-IDENTIDADE/timbrado/timbrado-topo-pagina.png` (500×500, 8-bit gray+alpha) + variante alternativa
- [x] `dados-profissionais.md` preenchido com: nome completo, CRM-MG 92.148, endereço pericial (Rua João Pinheiro 531, Sala 207, Empresarial Maria Costa, Centro, Governador Valadares/MG), telefone (33) 99900-1122, email perito@drjesus.com.br, filiação ABMLPM
- [x] `estilo-redacao-extraido.md` — 10 seções: endereçamento caixa alta, "Meritíssimo Juiz,", 1ª pessoa, refs por ID PJe, fecho "Termos em que,/Pede deferimento.", assinatura 3 linhas, EN DASH, data por extenso
- [x] 3 DOCX originais preservados em `02-BIBLIOTECA/peticoes/_fonte-originais-perito/` (aceite, aceite-condicionado, agendamento) — fonte de verdade do estilo
- [ ] Assinatura digital PNG transparente + certificado A1/A3 → `03-IDENTIDADE/assinatura/`
- [ ] Completar dados pendentes: CPF, RG, RQE, especialidade registrada, CEP, dados bancários/PIX para honorários

**Perguntas abertas residuais:** P1 (assinatura), P3 (CPF/RG/RQE/banco), P4 (subir corpus de 5-10 peças antigas) — veja seção no final.

---

## FASE 2 — Biblioteca viva (EM ANDAMENTO)

Objetivo: catálogo navegável de tudo que pode ser reaproveitado.

- [x] Symlink `peticoes/_fonte-placeholders` → `MODELOS PETIÇÕES PLACEHOLDERS/`
- [x] Symlink `peticoes/_fonte-prontas` → `MODELOS/petições-prontas/`
- [x] Symlink `laudos/_fonte-referencia` → `LAUDOS-REFERENCIA/`
- [x] Symlink `laudos/_fonte-templates-mesa` → `_MESA/10-PERICIA/templates-reaproveitaveis/`
- [x] `02-BIBLIOTECA/_INDICE.md` — taxonomia completa publicada
- [x] Subpastas criadas por subtipo: peticoes/{11 subtipos} + proposta-honorarios/{6 classes}
- [x] Subpastas por classe em laudos/{6 classes} com README explicando particularidades
- [x] `respostas/` novo: quesitos-suplementares, impugnacao-laudo, esclarecimento-juiz
- [x] `clausulas-padrao/{preambulo,qualificacao-perito,metodologia,fundamentacao-complexidade,nexo-causal,avaliacao-dano,fecho}/`
- [x] `quesitos/{ortopedia,psiquiatria,clinica-geral,neurologia,cirurgia-geral,ginecologia}/`
- [x] `jurisprudencia/{honorarios,nexo-causal,incapacidade,erro-medico,previdenciario}/`
- [x] `_corpus-estilo/` separado em peticoes/ laudos/ respostas/ (corpus ≠ templates)
- [x] **3 TEMPLATEs ativos funcionais (2026-04-20):**
  - `peticoes/aceite/TEMPLATE.md` — aceite simples
  - `peticoes/aceite/TEMPLATE-condicionado.md` — aceite com honorários já fixados
  - `peticoes/agendamento/TEMPLATE.md` — agendamento consultório padrão
  - Todos com frontmatter YAML (variaveis_requeridas, timbrado, fonte_original) + placeholders `{{a.b.c}}` e `{{#lista:}}`
- [x] Teste end-to-end OK: `aplicar_template.py` + `FICHA-EXEMPLO.json` → saída IDÊNTICA aos DOCX originais (RC=0, TESTE-LOG.md)
- [ ] Popular TEMPLATE.md restantes: proposta-honorarios/{erro-medico,securitario,previdenciario,trabalhista,civel,dpvat}, escusa, esclarecimento, majoracao-honorarios, impugnacao-quesitos, complementar, mutirao
- [ ] Popular laudos/{erro-medico,securitario,previdenciario,trabalhista,civel-dano-pessoal,psiquiatrico}/TEMPLATE.md
- [ ] Popular respostas/{quesitos-suplementares,impugnacao-laudo,esclarecimento-juiz}/TEMPLATE.md

---

## FASE 3 — Pipelines MD (EM ANDAMENTO)

Objetivo: receitas determinísticas. Cada pipeline = arquivo MD com passos numerados que Claude executa.

- [x] `04-PIPELINES/blocos-tempo-cronometrados.md` — blocos TDAH/autismo (triagem 25min, análise profunda 45min, petição simples 15min, laudo discussão 60min)
- [ ] `pipeline-analise-processo.md` — PDF → FICHA.json (quem, o quê, quando)
- [ ] `pipeline-geracao-peticao.md` — FICHA + tipo → petição MD → PDF timbrado
- [ ] `pipeline-geracao-laudo.md` — FICHA + notas exame → laudo completo
- [ ] `pipeline-revisao-qualidade.md` — Verificação 100% antes de entregar
- [ ] `pipeline-intimacao.md` — Nova intimação → triagem → próxima ação

---

## FASE 4 — Automações-chave (EM ANDAMENTO)

Objetivo: comandos de uma linha que fazem horas de trabalho manual.

| Comando | O que faz | Estado |
|---|---|---|
| `/novo-caso <numero>` | Cria pasta do caso a partir de `_TEMPLATE-CASO/` | a criar |
| `/peticao <tipo>` | Gera petição timbrada do caso atual | **FUNCIONAL** — skill `~/.claude/skills/peticao-cowork/SKILL.md` + motor `aplicar_template.py` (3 templates ativos) |
| `/laudo` | Inicia/continua laudo com template por patologia | já existe em `skills/` — integrar |
| `/intimacao` | Triagem de intimação do PJe | a criar |
| `/arquivar <numero>` | Move caso encerrado para `07-ARQUIVO/` | a criar |
| `/dashboard` | Status de todos os casos ativos | a criar |

**Motor de preenchimento:** `cowork/05-AUTOMACOES/scripts/aplicar_template.py` (stdlib apenas)
- Placeholders simples `{{a.b.c}}` ✅
- Lista `{{#lista:path:prefixo="":separador=""}}` ✅
- Data do sistema `{{data.por_extenso}}` ✅
- Frontmatter YAML removido auto ✅
- Falta detectada vira `[[FALTA:path]]` + warning stderr ✅
- **Pendente:** `{{#se:cond}}...{{/se}}` (para proposta-honorarios condicional), MD→DOCX com timbrado (pandoc ou python-docx), comentário de rastreabilidade auto, integração CFM/RQE (ideia anotada em `06-APRENDIZADO/IDEIA-proposta-honorarios-por-classe.md`)

---

## FASE 5 — Aprendizado contínuo (PLANEJADO)

Objetivo: cada caso torna o próximo mais rápido.

- [x] `06-APRENDIZADO/ANALISE-BANCO-MODELOS.md` — plano ultrathink 6 níveis (descritiva, lexical, clusterização HDBSCAN, estrutural, semântica, evolutiva, benchmark). Gatilho: ≥30 peças por tipo.
- [x] `06-APRENDIZADO/IDEIA-proposta-honorarios-por-classe.md` — anotada ideia CFM/RQE: tabela por classe, blocos condicionais, scorer complexidade
- [ ] Hook pós-petição: registra erros/correções em `06-APRENDIZADO/erros.md`
- [ ] Agente semanal: extrai padrões de `01-CASOS-ATIVOS/*/peticoes-geradas/` e atualiza templates
- [ ] Dashboard de métricas: tempo médio por caso, petições por tipo, taxa de erro material

---

## FASE 6 — Replicabilidade (DOCUMENTAR)

Esta mesma estrutura deve caber em:
- **Clínica Minas** (sistema de gestão médica)
- **Stemmia Forense** (consultoria pericial)
- **Projetos pessoais** (ex: automações domésticas)

Ver `REPLICABILIDADE.md`.

---

## PERGUNTAS ABERTAS AO USUÁRIO

Responda quando puder — cada resposta destrava uma fase.

### P1. Timbrado e identidade visual
- [ ] Onde está seu papel timbrado atual? (caminho no Mac ou upload?)
- [ ] Quer **1 timbrado único** ou variações (perito / advogado / academia)?
- [ ] Formato preferido de saída: PDF apenas, ou PDF + DOCX editável?

### P2. Estilo de redação
- [ ] Tratamento: "Excelência", "Vossa Excelência", "MM. Juiz(a)"?
- [ ] Parágrafo numerado ou corrido?
- [ ] Usa "este Perito" ou "o subscritor" ou "o signatário"?
- [ ] Fecho padrão (ex: "Nestes termos, pede deferimento.")?

### P3. Dados profissionais (fonte única)
- [ ] CRM, CPF, endereço pericial para constar em todas as peças?
- [ ] Banco/chave PIX para propostas de honorários?
- [ ] OAB (se for peticionar como advogado em causa própria ou da família)?

### P4. Petições antigas
- [ ] Onde vai subir? Sugestão: `cowork/02-BIBLIOTECA/peticoes/_historico/` (por tipo) ou `_corpus-estilo/` (todas juntas, vira input do extrator de estilo).
- [ ] Tem preferência de formato? PDF/DOCX original serve — o sistema extrai texto.

### P5. Prioridade imediata
- [ ] Qual o **primeiro caso real** para testar o fluxo ponta-a-ponta esta semana?
- [ ] Tipo de petição mais frequente hoje (aceite? esclarecimento? proposta?)

---

## SNAPSHOT 2026-04-20 — sessão automode

### Concluído nesta sessão
1. Timbrado oficial identificado (PNG 500×500) + variante renomeada
2. `dados-profissionais.md` preenchido com 8 campos reais
3. `estilo-redacao-extraido.md` criado (10 seções derivadas dos 3 DOCX originais)
4. `_INDICE.md` da biblioteca publicado (taxonomia 11/6/6/3)
5. 3 TEMPLATEs ativos: `aceite/TEMPLATE.md`, `aceite/TEMPLATE-condicionado.md`, `agendamento/TEMPLATE.md`
6. Motor `aplicar_template.py` v0.2 (stdlib) — 6/6 testes RC=0 + 7/7 unitários do condicional
7. Skill `/peticao` criada em `~/.claude/skills/peticao-cowork/SKILL.md`
8. `PLANO-ACAO.md` atualizado (este arquivo)
9. **Orquestrador v0.1** em `05-AUTOMACOES/orquestrador/` — pipeline determinístico DOCX/PDF/TXT/MD → classificação → arquivamento → relatório. Testado com 3 DOCX reais: 3/3 classificados corretamente (aceite 6.0, aceite 6.0, agendamento 5.0). Idempotência por SHA-256 verificada (duplicado detectado em rerun).

### Fica esperando do usuário
- Subir 5-10 DOCX antigos (qualquer tipo) → alimenta `_corpus-estilo/` → destrava extração automatizada de estilo por subtipo
- Completar campos pendentes em `dados-profissionais.md`: CPF, RG, RQE, especialidade, CEP, banco/PIX
- Indicar primeiro CNJ real para testar fluxo ponta-a-ponta

### Próximas sessões (ordem sugerida)
1. Implementar `{{#se:cond}}...{{/se}}` no motor → destrava proposta-honorarios condicional
2. Popular `proposta-honorarios/erro-medico/TEMPLATE.md` (usando blocos condicionais + tabela CFM/RQE)
3. Integração MD→DOCX com timbrado automático (pandoc ou python-docx)
4. Skill `/novo-caso <CNJ>` que cria pasta a partir de `_TEMPLATE-CASO/`
5. Hook pós-petição que registra o gerado em `06-APRENDIZADO/erros.md`
