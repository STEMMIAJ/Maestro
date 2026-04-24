# Análise do banco de modelos — plano ultrathink

**Criado:** 2026-04-20
**Disparo:** quando o banco (`02-BIBLIOTECA/peticoes/_corpus-estilo/` + `laudos/_corpus-estilo/`) estiver com ≥ 30 peças por tipo

---

## Por que esperar antes de analisar

Análise de padrões com N < 20 peças por tipo dá conclusões ruins (ruído > sinal). Usuário vai popular o banco aos poucos — não faz sentido rodar análise prematura.

**Gatilho automático:** hook semanal verifica contagem. Quando qualquer tipo cruza 30 peças, notifica: "pronto para análise".

---

## O que a análise vai produzir

### 1. Perfil de estilo por tipo de peça
Para cada tipo (proposta-erro-medico, proposta-securitario, esclarecimento, aceite-majoracao, laudo-erro-medico, laudo-securitario, etc.):

```json
{
  "tipo": "proposta-erro-medico",
  "n_amostras": 42,
  "metricas": {
    "palavras_por_peca_media": 1240,
    "palavras_por_peca_mediana": 1180,
    "frases_por_peca": 48,
    "palavras_por_frase_media": 25.8,
    "ttr": 0.42,
    "pessoa_verbal_dominante": "3a",
    "conectores_top10": ["ademais", "outrossim", "nada obstante", ...],
    "latim_densidade_por_mil": 3.2,
    "citacoes_jurisprudencia_media": 1.4,
    "secoes_presentes_pct": {"preambulo": 1.0, "qualificacao": 1.0, "fundamentacao": 0.93, ...}
  },
  "assinaturas": [
    "Nestes termos, pede-se deferimento",
    "o Perito signatário, no exercício de seu múnus público...",
    "impõe-se a majoração do honorário pericial, considerando..."
  ]
}
```

### 2. Clusters (agrupamentos)
Detectar sub-padrões dentro do mesmo tipo. Ex: em 42 propostas de erro-médico, o sistema descobre 3 clusters:
- **Cluster A** (18 peças): casos simples (1 réu, 1 lesão) — texto ~800 palavras, estrutura enxuta
- **Cluster B** (20 peças): casos médios (1-2 réus, nexo contestado) — texto ~1400 palavras
- **Cluster C** (4 peças): casos graves (óbito, múltiplos réus) — texto ~2200 palavras, 4 citações de jurisprudência

Cada cluster vira **template próprio** com placeholders próprios. Sistema aprende a selecionar cluster pelo score de complexidade (`pipeline-proposta-honorarios`).

### 3. Frases-gabarito reutilizáveis
Sentenças que aparecem em ≥ 30% das peças do tipo viram **cláusulas padrão** em `02-BIBLIOTECA/clausulas-padrao/`. Exemplo: se 40 de 42 propostas têm uma variação de "considerando a complexidade técnica dos atos médicos em análise", essa vira cláusula `complexidade-abertura.md` com placeholders.

### 4. Catálogo de jurisprudência citada
Extrair todas as citações e ranquear por frequência. Top 20 jurisprudências que você usa viram biblioteca em `02-BIBLIOTECA/jurisprudencia/top-usadas.md` com contexto ("quando cito qual").

### 5. Detector de outliers
Peças que destoam muito do perfil do tipo — candidatas a revisão. Motivos possíveis: (a) peça de transição de estilo, (b) peça de outro perito copiada por engano, (c) caso atípico que virou cluster novo.

---

## Técnicas (ultrathink — máximo esforço analítico)

### Nível 0 — Estatística descritiva
- Contagens, médias, desvios, histogramas.
- Ferramenta: Python + pandas.
- Tempo: 1 bloco de 40 min.

### Nível 1 — Análise lexical
- TF-IDF para achar termos característicos de cada tipo vs. baseline.
- Bigramas e trigramas dominantes.
- N-gramas de assinatura (sequências raras mas recorrentes).
- Ferramenta: scikit-learn TfidfVectorizer.
- Tempo: 1 bloco de 60 min.

### Nível 2 — Clusterização
- Embeddings por peça (sentence-transformers ou OpenAI text-embedding-3-small).
- DBSCAN ou HDBSCAN para descoberta automática de nº de clusters (sem K pré-definido).
- Visualização UMAP 2D para sanidade visual.
- Ferramenta: sentence-transformers + hdbscan.
- Tempo: 1 bloco de 60 min.

### Nível 3 — Análise estrutural
- Extrair árvore de seções de cada peça (via headers/parágrafos-gatilho).
- Alinhamento de sequências para descobrir estrutura canônica por tipo.
- Ferramenta: regex + análise de sequências.
- Tempo: 1 bloco de 45 min.

### Nível 4 — Análise semântica (mais custosa)
- Classificar cada parágrafo por FUNÇÃO (qualificação / fundamentação / pedido / justificativa de complexidade / fecho).
- LLM (Claude Haiku) roda sobre cada parágrafo com prompt curto — classificador barato.
- Produz **heatmap** de quanto tempo em cada função por tipo.
- Tempo: 1 bloco de 60 min + custo API.

### Nível 5 — Análise evolutiva
- Ordenar peças por data. Plotar métricas ao longo do tempo.
- Descobrir tendências (texto ficando mais curto? mais latim? menos jurisprudência?).
- Útil para: (a) detectar melhoria do estilo, (b) congelar "melhor versão" como referência.
- Tempo: 1 bloco de 30 min.

### Nível 6 — Benchmark externo
- Comparar perfil do usuário com referências públicas (jurisprudência de peritos renomados, manuais de perícia).
- Identificar lacunas / diferenciais.
- Cuidadoso: não é "estar errado diferente do padrão" — pode ser assinatura pessoal valiosa.
- Tempo: 1 bloco de 60 min.

---

## Produtos finais da análise

1. **`06-APRENDIZADO/perfil-estilo-consolidado.json`** — o JSON de referência que vira input de agentes de redação.
2. **`02-BIBLIOTECA/peticoes/proposta/<classe>/<cluster>.md`** — templates por cluster descoberto.
3. **`02-BIBLIOTECA/clausulas-padrao/*.md`** — banco de cláusulas reutilizáveis.
4. **`02-BIBLIOTECA/jurisprudencia/top-usadas.md`** — jurisprudência recorrente com contexto.
5. **`06-APRENDIZADO/relatorio-analise-<data>.md`** — relatório narrativo (autismo-friendly: estrutura fixa, tabelas, conclusões secas).
6. **`06-APRENDIZADO/outliers.md`** — peças desviantes para revisão humana.

---

## Dashboard pós-análise

Arquivo `06-APRENDIZADO/dashboard.html` (local, abre no browser) com:

- Tabela tipo × N amostras × % cobertura
- Gráfico evolução palavras/peça por mês
- Top 10 cláusulas reutilizadas
- Mapa de clusters (UMAP)
- Lista de outliers clicável
- Comparador: "sua petição atual X média do seu perfil"

---

## Fluxo recomendado (quando disparar)

```
Popular banco aos poucos (usuário)
  ↓
Hook contador semanal detecta N ≥ 30 por tipo
  ↓
Notifica via Telegram: "Pronto para análise: [tipos]"
  ↓
Usuário responde /analise-banco <tipo>
  ↓
Sistema roda níveis 0-3 (blocos de 40-60min cada)
  ↓
Usuário revisa relatório MD + aprova clusters
  ↓
Sistema promove clusters a templates ativos
  ↓
Próximos pipelines já usam novos templates
```

---

## Integração com pipeline-proposta-honorarios

Depois que a análise roda:
- Template `02-BIBLIOTECA/peticoes/proposta/erro-medico.md` é substituído por 3 variantes (simples/médio/grave).
- Scorer de complexidade é calibrado com dados empíricos (não mais chute).
- Cláusula de "complexidade" é auto-selecionada pelo cluster certo.

---

## Quando re-rodar

- A cada 20 peças novas → refresh incremental.
- Se usuário mudar significativamente estilo → re-rodar nível 5 manualmente.
- Se abrir classe processual nova → rodar do zero para a classe.

---

## Cuidados (armadilhas)

1. **Não clusterizar com < 20 amostras** — resultado inútil, introduz ruído.
2. **Não substituir template antigo sem versionar** — salvar como `-v2.md`, manter `-v1.md` de referência.
3. **Não confundir estilo com erro** — se 40% das peças têm um vício recorrente (ex: parágrafo redundante), NÃO é "padrão a preservar", é "padrão a corrigir". Análise deve sinalizar candidatos a revisão pelo usuário, não eternizar.
4. **Auditar privacidade do corpus** — antes de rodar em API externa (OpenAI embeddings), verificar se nomes de partes e dados sensíveis estão mascarados. Alternativa: embeddings locais (sentence-transformers, roda no Mac).
5. **Não automatizar aprovação** — clusters novos precisam validação humana antes de virarem templates. Caso contrário o sistema se auto-reforça em padrões ruins.
