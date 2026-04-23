---
titulo: "Tamanho de amostra e power analysis"
bloco: "06_data_analytics/experimentation"
tipo: "fundamento"
nivel: "intermediario"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 7
---

# Tamanho de amostra e power analysis

Calcular n **antes** de coletar. Estudo subdimensionado não detecta efeito real (erro tipo II); superdimensionado gasta recurso e pode detectar "significância" trivial.

## Os 4 ingredientes

Fórmula clássica para comparação de médias com 2 grupos:

```
n por grupo ≈ ((z_α/2 + z_β)² × 2σ²) / δ²
```

- **δ (delta)**: diferença mínima clinicamente relevante (tamanho de efeito).
- **σ (sigma)**: desvio padrão esperado.
- **α**: nível de significância (0,05 → z = 1,96 bilateral).
- **β**: 1 − poder (0,20 → z = 0,84 para poder 80%).

Troca um dos 4 → os outros precisam recalcular.

## Tamanho de efeito (effect size)

- **d de Cohen** (médias): `(μ₁ − μ₂) / σ`. Convenções: 0,2 pequeno; 0,5 médio; 0,8 grande.
- **h de Cohen** (proporções): função de arcseno.
- **f² de Cohen** (regressão): 0,02 pequeno; 0,15 médio; 0,35 grande.
- **OR** (caso-controle): interpretar no contexto, não há regra universal.

**Regra prática em saúde**: se não consegue estimar δ do piloto ou literatura, buscar o menor efeito **clinicamente relevante** — não o que "espera-se achar".

## G\*Power (GUI)

Software gratuito (Windows/macOS). Passos:
1. Selecionar família de teste (t, F, χ², exata).
2. Selecionar teste específico (t independente, pareado).
3. Tipo de análise: **A priori** (calcular n dado poder).
4. Inserir α, poder (1−β), efeito esperado.
5. Calcular → n total e por grupo.

Bom para revisores e comitês de ética: exporta PDF com justificativa.

## pwr (R)

```r
library(pwr)

# t independente, d=0.5, poder=0.8, alfa=0.05
pwr.t.test(d = 0.5, power = 0.80, sig.level = 0.05, type = "two.sample")
# n = 63.77 → 64 por grupo

# Qui-quadrado 2x2, w=0.3 (efeito médio), df=1
pwr.chisq.test(w = 0.3, df = 1, power = 0.8)

# Correlação, r=0.3
pwr.r.test(r = 0.3, power = 0.8)

# ANOVA 1-fator, 4 grupos, f=0.25 (médio)
pwr.anova.test(k = 4, f = 0.25, power = 0.8)
```

## statsmodels (Python)

```python
from statsmodels.stats.power import TTestIndPower, FTestAnovaPower
from statsmodels.stats.proportion import samplesize_proportions_2indep_onetail

# t independente
analysis = TTestIndPower()
n = analysis.solve_power(effect_size=0.5, alpha=0.05, power=0.8)
print(n)  # ~64

# Proporções (p1=0.30, p2=0.45), alfa 0.05 unilateral
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
h = proportion_effectsize(0.45, 0.30)
NormalIndPower().solve_power(effect_size=h, alpha=0.05, power=0.8, alternative='larger')
```

## Ajustes práticos

- **Perda esperada** (dropout): inflar n por `1 / (1 − perda)`. Perda 20% → n × 1,25.
- **Múltiplos testes**: Bonferroni reduz α → inflar n.
- **Desfecho raro**: para proporções < 5%, preferir fórmulas exatas (binomial); aproximação normal falha.
- **Pareamento**: reduz variância, diminui n necessário. Usar fórmula pareada.

## Piloto

Quando σ é desconhecido: rodar piloto de 10–20 sujeitos, estimar σ, recalcular n. Piloto **não** serve para testar hipótese principal.

## Exemplo clínico-pericial

Comparar tempo até reabilitação (dias) após duas técnicas cirúrgicas.

- Literatura: média A = 42 dias (DP 8).
- Diferença clinicamente relevante: 5 dias.
- d = 5/8 = 0,625.
- α=0,05 bilateral, poder 80%.

R:
```r
pwr.t.test(d = 0.625, power = 0.8, sig.level = 0.05, type = "two.sample")
# n = 41.7 → 42 por grupo = 84 total
```

Se espera perda 15%: 42 / 0,85 ≈ 50 por grupo = 100 total.

## Poder observado (post-hoc)

**Evitar**. Calcular poder depois do estudo usando efeito observado é circular e enganoso. Para estudo nulo, reportar IC e discutir relevância do limite inferior.
