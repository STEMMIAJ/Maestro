---
nome: pipeline-proposta-honorarios
entrada: _dados/FICHA.json + classe-processual (inferida ou explícita)
saida: peticoes-geradas/<data>-proposta-honorarios.md + .pdf
duracao_estimada: 20 min (30 min se inclui busca CFM)
agentes_envolvidos: [peticao-identificador, peticao-extrator, cfm-buscador, calculador-complexidade, peticao-montador, peticao-verificador, peticao-gerador-pdf]
---

# Pipeline — Proposta de Honorários (ramificado por classe)

## Objetivo

Gerar proposta de honorários **adequada ao tipo de processo**, com fundamentação específica que o juiz precisa ver para deferir o valor. Não é 1 template para tudo — são N templates, um por classe, com blocos condicionais.

## Pré-requisitos

- `_dados/FICHA.json` completo (executado pipeline-analise-processo antes)
- `_dados/FICHA.json:classe_processual` preenchido (se não, pipeline pergunta/infere)
- Integração CFM funcionando se classe = erro-medico (ver `pipeline-integracao-cfm.md`)
- `03-IDENTIDADE/dados-profissionais.md` preenchido (banco/PIX/CRM subscriber)

## Ramificações por classe

```
FICHA.classe_processual == "erro-medico"
  → template: 02-BIBLIOTECA/peticoes/proposta/erro-medico.md
  → variáveis extras: medico_reu_cfm, rqe, especialidade, nexo_contestado
  → busca CFM: OBRIGATÓRIA
  → apolice: FALSO (default)
  → checklist: checklist-erro-medico.md

FICHA.classe_processual == "securitario"
  → template: 02-BIBLIOTECA/peticoes/proposta/securitario.md
  → variáveis extras: numero_apolices, valor_segurado, seguradora
  → busca CFM: NÃO
  → apolice: TRUE (detectar nº)
  → checklist: checklist-securitario.md

FICHA.classe_processual == "previdenciario"
  → template: 02-BIBLIOTECA/peticoes/proposta/previdenciario.md
  → variáveis extras: did, dii, cid_principal, tipo_beneficio (aux-doenca/aposentadoria-invalidez/bpc)
  → busca CFM: NÃO
  → checklist: checklist-previdenciario.md

FICHA.classe_processual == "trabalhista"
  → template: 02-BIBLIOTECA/peticoes/proposta/trabalhista.md
  → variáveis extras: cat, ppp, agente_insalubre, nexo_ocupacional
  → checklist: checklist-trabalhista.md

FICHA.classe_processual == "civel-danopessoal"
  → template: 02-BIBLIOTECA/peticoes/proposta/civel-danopessoal.md
  → variáveis extras: boletim_ocorrencia, at_autor, at_reu
```

## Passos numerados

### 1. Classificar caso
- **Agente:** `classificador-tipo-acao`
- **Lê:** `_dados/FICHA.json`, `documentos-recebidos/*.pdf`
- **Escreve:** `_dados/classe-processual.json`
- **Sucesso:** um dos 5 valores acima + confiança ≥ 0.8; se < 0.8, pipeline pausa e pergunta ao usuário.

### 2. (Só erro-médico) Buscar médico-réu no CFM
- **Agente:** `cfm-buscador` (a criar — ver `pipeline-integracao-cfm.md`)
- **Entrada:** `_dados/FICHA.json:medico_reu_nome`
- **Escreve:** `_dados/cfm-medico-reu.json` com `{crm, uf, rqe, especialidade, situacao}`
- **Sucesso:** JSON existe e `situacao == "ATIVO"`. Se inativo/cassado, sinalizar na proposta.

### 3. Rodar checklist específico da classe
- **Onde:** `02-BIBLIOTECA/clausulas-padrao/checklists/checklist-<classe>.md`
- **Sucesso:** TODOS os itens verificados (ou justificados como N/A).
- **Se falhar:** pipeline pausa e lista itens pendentes.

### 4. Calcular score de complexidade
- **Script:** `05-AUTOMACOES/scripts/scorer-complexidade.py` (a criar)
- **Fórmula:** `score = nº_quesitos×2 + nº_documentos×0.1 + nº_apolices×5 + (AT ? 10 : 0) + nº_partes×3 + urgencia`
- **Escreve:** `_dados/complexidade.json` com `{score, faixa, multiplicador, justificativa}`
- **Faixas:** 0-30 base; 31-60 médio (1.5×); 61-100 alto (2-3×).

### 5. Extrair dados para template
- **Agente:** `peticao-extrator` (já existe)
- **Produz:** objeto JSON com todas as variáveis que o template precisa.

### 6. Preencher template da classe
- **Agente:** `peticao-montador` (já existe)
- **Lê:** template da classe + dados extraídos + `03-IDENTIDADE/dados-profissionais.md`
- **Escreve:** `peticoes-geradas/<data>-proposta-<classe>.md`
- **Aplica blocos condicionais** (`{{#se:tem_apolice}}`, etc.).

### 7. Verificar anti-erro
- **Agente:** `peticao-verificador` (já existe) + verificador específico da classe
- **Checa:** nome das partes, CNJ, gênero do juiz, valores por extenso, CRM/RQE do réu se erro-médico, nº apólices se securitário.
- **Se erro:** pausa, lista problemas, não gera PDF.

### 8. Gerar PDF timbrado
- **Agente:** `peticao-gerador-pdf` (já existe)
- **Aplica:** timbrado de `03-IDENTIDADE/timbrado/`
- **Escreve:** `peticoes-geradas/<data>-proposta-<classe>.pdf`

### 9. Registrar no aprendizado
- **Script:** appenda linha em `06-APRENDIZADO/propostas-emitidas.jsonl` com `{data, classe, score, multiplicador, valor_final, duracao_pipeline}`.

## Pontos de verificação (anti-mentira)

| Após passo | Verificar | Como |
|---|---|---|
| 1 | Classe válida | `jq .classe _dados/classe-processual.json` ∈ {erro-medico, securitario, ...} |
| 2 | CFM resolvido | `test -f _dados/cfm-medico-reu.json && jq .situacao` |
| 4 | Score calculado | `jq .score _dados/complexidade.json` é número |
| 6 | MD gerado | `wc -l peticoes-geradas/*-proposta-*.md` > 30 |
| 6 | Sem placeholder solto | `! grep -E '\{\{[A-Z_]+\}\}' peticoes-geradas/*-proposta-*.md` |
| 8 | PDF existe | `test -f peticoes-geradas/*-proposta-*.pdf` |

## Erros comuns + fix

1. **Classe ambígua** (ex: erro médico + securitário ao mesmo tempo) → pipeline abre 2 templates e pergunta qual é principal; subordinada vira anexo justificatório.
2. **Médico-réu com nome comum** (ex: "João Silva") → CFM retorna múltiplos; pausa e pede UF + especialidade inicial para desambiguar.
3. **FICHA sem nº quesitos** (ainda não foram formulados) → score roda com `nº_quesitos = estimado_pela_classe` (default 10) e proposta menciona "sem prejuízo de majoração após quesitos".
4. **Apólice citada mas não anexada** → sistema sinaliza e proposta pede intimação para juntada antes da perícia (justifica complexidade extra).
5. **Classe nova não coberta** → pipeline cai em template genérico `proposta/_fallback.md` + log em `06-APRENDIZADO/classes-novas.jsonl` para revisão semanal.

## Exemplo executado

Caso fictício: `0000000-00.0000.0.00.0000`, ação de erro médico, réu Dr. X (especialista em cirurgia vascular), 3 apólices de seguro profissional, 2 ATs.

1. classe = erro-medico (confiança 0.95)
2. CFM resolve → CRM 12345/MG, RQE 5678, especialidade "Cirurgia Vascular", ATIVO
3. checklist erro-medico: 7/7 OK
4. score: quesitos(12)×2 + docs(34)×0.1 + apólices(3)×5 + AT(2×10) + partes(4)×3 + urgência(0) = 24+3.4+15+20+12 = **74.4 → faixa ALTA → multiplicador 2.2×**
5. extração OK
6. template `erro-medico.md` preenchido com blocos: apólice(SIM, 3), AT(SIM), CFM(preenchido)
7. verificador: 0 erros
8. PDF gerado com timbrado
9. log registrado

**Output final:** proposta de honorários de ~R$ X (base × 2.2) justificada com: especialidade do réu, 12 quesitos, 3 apólices, 2 ATs, 34 docs para análise.

---

**Dependências a construir** (antes deste pipeline rodar):
- [ ] Templates por classe em `02-BIBLIOTECA/peticoes/proposta/`
- [ ] Checklists em `02-BIBLIOTECA/clausulas-padrao/checklists/`
- [ ] Scorer de complexidade em `05-AUTOMACOES/scripts/`
- [ ] Agente `cfm-buscador` (ver `pipeline-integracao-cfm.md`)
- [ ] Campo `classe_processual` no schema do FICHA.json
