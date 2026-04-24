# Analisador de Processos — Instruções Locais

## REGRA PRINCIPAL: DETECÇÃO AUTOMÁTICA DE INTENÇÃO

O usuário é perito médico judicial. Ele NÃO precisa lembrar comandos. Ao receber QUALQUER mensagem, identificar a intenção e agir automaticamente.

### Mapa de Intenções (linguagem natural → ação)

| O que o usuário pode dizer | O que fazer |
|---------------------------|-------------|
| "analise esse processo", "olha esse PDF", "novo processo", "recebi nomeação" | → **PIPELINE COMPLETO**: extração + verificadores em paralelo + síntese + score |
| "proposta", "quanto cobrar", "honorários" | → **SKILL proposta-honorarios** |
| "aceite", "aceitar" | → Gerar petição de aceite |
| "contestaram", "impugnaram", "contestar", "reduziram" | → Resposta à contestação com jurisprudência |
| "justificar", "fundamentar honorários" | → Justificativa técnica de honorários |
| "agendar", "marcar perícia" | → Petição de agendamento |
| "quesitos", "vícios", "problemas nos quesitos" | → Análise de vícios nos quesitos |
| "petição", "manifestação" | → **SKILL /peticao** com tipo auto-detectado |
| "prorrogação", "mais prazo" | → `/peticao prorrogacao` |
| "requisitar documentos", "faltam documentos" | → `/peticao requisicao` |
| "esclarecimentos", "quesito suplementar" | → `/peticao esclarecimentos` |
| "gerar pdf", "markdown para pdf" | → **SKILL /pdf** |
| "verifica", "confere", "confere as leis" | → **VERIFICADOR**: validar referências legais |
| "erros", "confere esse laudo", "erros materiais" | → **ORQUESTRADOR DE ERROS**: 5 verificadores em paralelo |
| "jurisprudência sobre X", "precedente" | → **BUSCA JURÍDICA**: 3 buscadores em paralelo |
| "revisa esse laudo" | → Revisor de laudo pericial |
| "monta o laudo", "redigir laudo" | → Redator de laudo pericial |
| "sincronizar", "sync" | → `python3 sincronizar_aj_pje.py --novos-apenas --json` |
| "pipeline", "faz tudo", "gera tudo" | → `/pipeline` |
| "pipeline rápido", "despacha isso" | → `/pipeline-rapido` |
| "faz todos", "batch", "lote" | → `/pipeline-batch` |
| "pipeline do laudo" | → `/pipeline-laudo` |
| "contestaram e faz tudo" | → `/pipeline-contestacao` |
| "prioriza", "pendentes", "quais processos primeiro" | → `/priorizar` |
| "saúde do sistema", "auditar" | → `/saude` |

### QUANDO O USUÁRIO COLOCA UM PDF SEM DIZER NADA:
1. Extrair texto automaticamente
2. Identificar se é processo novo, contestação, ou outro documento
3. Agir conforme o tipo identificado — SEM PERGUNTAR

## PIPELINE COMPLETO DE ANÁLISE

### Fase 1 — Extração (sequencial)
1. `pdfinfo` → `pdftotext` (ou `tesseract` se escaneado)
2. Criar subpasta `[NUMERO-CNJ]/` e salvar TEXTO-EXTRAIDO.txt

### Fase 2 — Verificadores em PARALELO (Task tool)
- **Verificador de CIDs** — valida CID-10 contra tabela DataSUS
- **Verificador de Datas** — linha do tempo + inconsistências
- **Verificador de Nomes e Números** — grafias, CPFs, OABs
- **Verificador de Medicamentos** — prescrições e dosagens
- **Verificador de Exames** — exames citados vs anexados

### Fase 3 — Análise (sequencial)
1. Preencher ROTINA-ANALISE-PROCESSO.md (6 etapas + score)
2. Calcular honorários
3. Gerar ANALISE.md + RELATORIO-ERROS.md

### Fase 4 — Apresentação
Resumo compacto com recomendação ACEITAR/RECUSAR e próximos passos.

## VERIFICAÇÃO DE REFERÊNCIAS LEGAIS

Para CADA referência no documento:
1. Buscar na Base Local → Tribunais → Acadêmico (em paralelo)
2. Gerar relatório: REFERÊNCIA | STATUS | LINK | OBSERVAÇÃO
3. **NUNCA inventar** número de processo, REsp, HC ou identificador judicial

## Prompts portáteis
- Índice completo: `~/Desktop/ANALISADOR FINAL/prompts/INDICE-PROMPTS.md`

## Caminhos das ferramentas

| Ferramenta | Caminho |
|-----------|---------|
| ROTINA de análise | `~/Desktop/ANALISADOR FINAL/ROTINA-ANALISE-PROCESSO.md` |
| Leitor PDF grande | `~/Desktop/ANALISADOR FINAL/leitor-pdf-grande/ler.sh` |
| BANCO DE DADOS GERAL | `~/Desktop/ANALISADOR FINAL/BANCO DE DADOS GERAL/` |
| Precedentes (CLI) | `~/Documentos/pericia-conhecimento/` |
| Banco de contestações | `~/Desktop/ANALISADOR FINAL/Contestar/` |
| Exemplo real (Perícia 14) | `~/Desktop/ANALISADOR FINAL/PERICIA-14-FUNDAMENTACAO-HONORARIOS.md` |
| Proposta modelo | `~/Desktop/ANALISADOR FINAL/proposta-honorarios-reorganizada.md` |
| Modelo securitário | `~/Documentos/pericia-conhecimento/precedentes-salvos/por-tema/honorarios-periciais/modelos/MODELO-PROPOSTA-HONORARIOS-SECURITARIA.md` |
| Triagem PJe | `~/Desktop/ANALISADOR FINAL/skills/triagem-pericial/` |
| 19 modelos de laudo | `~/Desktop/ANALISADOR FINAL/modelos-laudo/` |
| Tabela TJMG 2025 | `~/Documentos/pericia-conhecimento/precedentes-salvos/por-tema/honorarios-periciais/tabelas-oficiais/tabela-honorarios-tjmg-2025.txt` |

---

## ESTILO JURÍDICO

### Preferências
- Tom de perito/assistente técnico (NÃO advogado)
- Formal sem excessos, conciso
- Frases diretas, períodos curtos
- Referências precisas (artigos, páginas, documentos)

### Evitar
- "Este perito" (usar "o perito" ou nome)
- "Ilustríssimo", "Excelentíssimo" (usar "o Juízo")
- Latinismos desnecessários, redundâncias

### Comandos de texto
- **"resume isso"** → versão ~50% menor, manter argumentos centrais
- **"petição" / "pro juiz"** → 1ª pessoa formal, linguagem técnica clara

---

## VERIFICAÇÃO 100% APÓS PEÇAS PROCESSUAIS

Após gerar QUALQUER petição/peça:
1. NUNCA incluir dado que não existe no TEXTO-EXTRAIDO.txt
2. NUNCA preencher referência jurídica "de cabeça" — buscar na base
3. Se não encontrou → usar: **[NÃO CONFIRMADO — verificar manualmente]**
4. Após gerar, OBRIGATORIAMENTE rodar verificador-100 (6 etapas)
5. Gerar JSON → `verificacao-[tipo].json` na pasta do processo
6. Executar: `python3 ~/Desktop/ANALISADOR\ FINAL/scripts/gerar_verificacao.py --json JSON --output HTML`
- **Agente:** `~/.claude/agents/verificador-100.md`
- **Método:** `~/Desktop/ANALISADOR\ FINAL/metodos/VERIFICADOR-100/`

---

## PDF GRANDE (> 50 páginas ou > 5 MB)

1. `pdfinfo arquivo.pdf`
2. `pdftotext arquivo.pdf arquivo.txt`
3. Ler o .txt. Se ainda grande: `pdfseparate arquivo.pdf parte-%d.pdf`
- Ferramentas: pdftotext, pdfinfo, pdfunite, pdfseparate, gs, tesseract, pandoc

---

## REGRAS DE PETIÇÃO

### Regras locais específicas
1. SEMPRE trabalhar dentro da subpasta do processo (`[NUMERO-CNJ]/`)
2. SEMPRE usar `pdftotext` antes de ler PDF grande (>50 páginas ou >5MB)
3. SEMPRE referenciar IDs de documentos do PJe quando disponíveis
4. IDs sempre em **negrito** — tanto "ID" quanto o número
5. "Meritíssimo Juiz," em **negrito** após o título centralizado
6. Identificar corretamente tipo de documento — despacho ≠ decisão ≠ manifestação ≠ intimação
7. ABMLPM sempre com nome completo

### Regra de dados
- Quando perguntar sobre direito/medicina, primeiro buscar na base. NUNCA inventar informação jurídica.
- Busca rápida: `cd ~/Desktop/ANALISADOR\ FINAL/BANCO\ DE\ DADOS\ GERAL && ./_sistema/base buscar "termo"`

### Geração de PDF — Script único: `gerar_peticao.py`
```bash
# Via arquivo XML (recomendado)
python3 ~/Desktop/ANALISADOR\ FINAL/scripts/gerar_peticao.py --output NOME.pdf --corpo-arquivo /tmp/corpo.xml

# Via corpo inline (petições curtas)
python3 ~/Desktop/ANALISADOR\ FINAL/scripts/gerar_peticao.py --output NOME.pdf --corpo "<w:p>...</w:p>"
```
**NUNCA** usar reportlab, fpdf2 ou descompactar DOCX manualmente.

### Checklist de conferência manual (obrigatória após gerar petição)
Tabela com colunas: | DADO | ONDE CITEI | FONTE NO PROCESSO |

## Estrutura de subpasta de processo
- Referência: `~/Desktop/ANALISADOR FINAL/ESTRUTURA-PROCESSO.md`
