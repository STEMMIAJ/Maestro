---
titulo: "Testes estatísticos comuns em saúde — quando e como usar"
bloco: "06_data_analytics/statistics_foundations"
tipo: "fundamento"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 10
---

# Testes estatísticos comuns em saúde

Seleção depende de: **tipo de variável** (contínua/categórica), **n amostras** (2 ou mais), **pareamento** (amostras dependentes) e **distribuição** (normal vs não-normal).

## t de Student

- **Uso**: comparar **médias** entre 2 grupos com variável contínua **normal**.
- **t pareado**: mesmo indivíduo antes/depois (ex.: PA pré vs pós fármaco).
- **t independente**: dois grupos distintos (ex.: grupo A vs B).
- **Pressupostos**: normalidade; variâncias homogêneas (Levene). Se variâncias diferentes → t de Welch.
- **Saída**: diferença de médias, IC95%, p-valor.

**Exemplo**: Tempo de recuperação pós-cirurgia, grupo fisioterapia (n=30, média 21d) vs controle (n=30, média 28d). Teste t independente, p = 0,003 → aceitar diferença real.

## Mann-Whitney U (Wilcoxon rank-sum)

- **Uso**: alternativa **não-paramétrica** ao t independente.
- Quando: variável contínua **não-normal** ou ordinal; n pequeno (< 30); presença de outliers.
- Compara **distribuições** (na prática, medianas se as distribuições têm forma similar).
- **Wilcoxon signed-rank**: versão pareada (análogo ao t pareado).

**Exemplo**: PSA entre pacientes com e sem neoplasia — PSA é muito assimétrico → Mann-Whitney.

## Qui-quadrado (χ²)

- **Uso**: associação entre **duas variáveis categóricas** em tabela de contingência.
- **Qui-quadrado de Pearson**: amostras independentes, frequências esperadas ≥ 5 em ≥ 80% das células.
- **Teste exato de Fisher**: quando χ² não é válido (n pequeno, frequências esperadas < 5).
- **McNemar**: categóricas pareadas (antes/depois do mesmo indivíduo).

**Exemplo**: Tabela 2×2 — reinternação em 30 dias (sim/não) × tipo de alta (com equipe multiprofissional/sem). χ² = 6,4; p = 0,011; OR = 0,52 [0,31–0,88] → alta multiprofissional reduz reinternação.

## ANOVA

- **Uso**: comparar médias de **3 ou mais grupos** com variável contínua normal.
- **ANOVA 1-fator**: um fator categórico (ex.: 3 doses de fármaco).
- **ANOVA fatorial**: ≥ 2 fatores, avalia interações.
- **Post-hoc**: Tukey HSD, Bonferroni — identificar quais pares diferem.
- Não-paramétrico equivalente: **Kruskal-Wallis**.

## Regressão linear

- **Uso**: relação entre variável contínua desfecho (Y) e ≥ 1 preditor (X).
- Coeficiente β = variação em Y por unidade de X, ajustado pelas demais variáveis.
- Pressupostos: linearidade, independência, homocedasticidade, normalidade de resíduos.

## Regressão logística

- **Uso**: desfecho **binário** (sim/não, doente/saudável).
- Retorna **odds ratio (OR)** = exp(β).
- OR > 1 aumenta chance; OR < 1 reduz.
- **Exemplo**: probabilidade de complicação pós-operatória vs idade, diabetes, IMC.
- **Curva ROC + AUC** avalia poder discriminativo do modelo.

## Sobrevida

- **Kaplan-Meier**: curvas de sobrevida por grupo.
- **Log-rank test**: compara curvas.
- **Regressão de Cox**: hazard ratio (HR), ajustado por covariáveis.

## Fluxograma rápido

1. Contínua × contínua → correlação (Pearson/Spearman) ou regressão linear.
2. Contínua × categórica (2 grupos): t de Student (normal) ou Mann-Whitney.
3. Contínua × categórica (≥ 3 grupos): ANOVA ou Kruskal-Wallis.
4. Categórica × categórica: χ² ou Fisher; McNemar se pareado.
5. Desfecho binário com múltiplos preditores: regressão logística.
6. Tempo até evento: Kaplan-Meier + Cox.

## Software

- **R**: `t.test`, `wilcox.test`, `chisq.test`, `fisher.test`, `glm(family=binomial)`, `survival::coxph`.
- **Python**: `scipy.stats`, `statsmodels`, `lifelines`.
- **JASP/Jamovi**: GUI amigáveis para quem não programa.
