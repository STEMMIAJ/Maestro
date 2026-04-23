---
titulo: "Estatística descritiva — medidas de tendência central e dispersão"
bloco: "06_data_analytics/statistics_foundations"
tipo: "fundamento"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 7
---

# Estatística descritiva

Resume um conjunto de dados em poucos números. Base de qualquer análise clínica ou pericial antes de inferência.

## Medidas de tendência central

- **Média aritmética**: soma / n. Sensível a outliers.
- **Mediana**: valor central do conjunto ordenado. Robusta a outliers.
- **Moda**: valor mais frequente. Útil em variáveis categóricas.

Regra prática em saúde: **distribuição assimétrica (ex.: PSA, tempo de internação) → usar mediana**. Distribuição aproximadamente normal (ex.: altura, pressão arterial em adultos saudáveis) → usar média.

## Medidas de dispersão

- **Amplitude**: máximo − mínimo. Pouco informativa.
- **Variância (σ²)**: média dos quadrados dos desvios.
- **Desvio padrão (DP, σ)**: raiz da variância. Mesma unidade da variável.
- **Coeficiente de variação (CV)**: DP/média × 100. Permite comparar variáveis de unidades diferentes.
- **Intervalo interquartil (IIQ)**: Q3 − Q1. Robusto, acompanha mediana.

## Percentis e quartis

Percentil `p` = valor que deixa `p%` das observações abaixo.
- **Q1 = P25**, **Q2 = P50 = mediana**, **Q3 = P75**.
- Boxplot usa Q1, mediana, Q3 + whiskers (±1,5 × IIQ) → identifica outliers visualmente.

## Exemplos clínicos

**Idade ao diagnóstico de câncer de próstata em uma coorte (n=120):**
- Média = 66,4 anos; DP = 8,2; mediana = 67; IIQ = 61–72.
- Interpretação: distribuição aproximadamente simétrica, média e mediana próximas.

**PSA sérico (ng/mL) em suspeita de neoplasia (n=80):**
- Média = 12,3; mediana = 4,8; DP = 38,9.
- Grande diferença média × mediana → **distribuição muito assimétrica à direita** (poucos pacientes com PSA > 100 puxam a média). Em laudo, reportar **mediana + IIQ**, nunca só média.

## Forma da distribuição

- **Assimetria (skewness)**: > 0 cauda direita, < 0 cauda esquerda.
- **Curtose**: > 3 (leptocúrtica, caudas pesadas), < 3 (platicúrtica).
- Teste de normalidade: Shapiro-Wilk (n < 50), Kolmogorov-Smirnov (n maior).

## Como reportar em laudo pericial

1. Variáveis contínuas normais: **média (DP)**.
2. Variáveis contínuas assimétricas: **mediana (IIQ)** ou **mediana (mín–máx)**.
3. Variáveis categóricas: **n (%)**.
4. Sempre reportar **n** da amostra antes de qualquer estatística.

## Armadilhas

- Reportar média de variável assimétrica esconde outliers clinicamente relevantes.
- DP sem média não informa nada — sempre apresentar par.
- Percentis com `n` pequeno (< 20) têm erro alto — preferir mín/máx.
