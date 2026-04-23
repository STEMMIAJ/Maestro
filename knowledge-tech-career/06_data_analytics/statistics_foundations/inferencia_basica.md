---
titulo: "Inferência estatística básica — IC, p-valor, erros tipo I e II"
bloco: "06_data_analytics/statistics_foundations"
tipo: "fundamento"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 9
---

# Inferência estatística básica

Usar amostra para estimar parâmetro populacional. O perito precisa distinguir **significância estatística** de **relevância clínica**.

## Intervalo de confiança (IC)

Faixa de valores plausíveis para o parâmetro, dado o nível de confiança escolhido (padrão 95%).

- **IC 95% para média**: `x̄ ± 1,96 × (DP/√n)` (n grande ou distribuição normal).
- Interpretação correta: em 95 amostras de 100, o IC contém o parâmetro verdadeiro.
- Interpretação incorreta: "há 95% de chance de o parâmetro estar nesse intervalo" (interpretação bayesiana, não frequentista).

**Exemplo**: Tempo médio de cicatrização pós-artroscopia = 42 dias; IC95% = [38, 46]. Outra técnica reporta 50 dias, IC95% = [45, 55]. **Intervalos se sobrepõem pouco** → diferença provavelmente real.

## Teste de hipóteses

- **H₀ (hipótese nula)**: sem efeito / sem diferença.
- **H₁ (alternativa)**: há efeito / diferença.
- **p-valor**: probabilidade de observar resultado tão extremo quanto o obtido, **se H₀ for verdadeira**.
- **α (nível de significância)**: limiar escolhido a priori, geralmente 0,05.
- **p < α** → rejeita H₀.

## Erros tipo I e II

| | H₀ verdadeira | H₀ falsa |
|---|---|---|
| **Rejeita H₀** | Erro tipo I (α) | Acerto (poder = 1−β) |
| **Não rejeita H₀** | Acerto | Erro tipo II (β) |

- **Erro tipo I (falso positivo)**: "achar" diferença que não existe. Controlado por α.
- **Erro tipo II (falso negativo)**: "não achar" diferença real. Controlado por β (tamanho amostral, tamanho de efeito).
- **Poder estatístico** = 1 − β. Mínimo aceitável: 80%.

## Armadilhas comuns

1. **p-valor NÃO é probabilidade de H₀ ser verdadeira**. É probabilidade do dado dado H₀.
2. **p > 0,05 não prova H₀**. Ausência de evidência ≠ evidência de ausência.
3. **Significância estatística ≠ relevância clínica**. Com n enorme, diferenças ínfimas ficam "significativas".
4. **p-hacking**: rodar múltiplos testes até achar p < 0,05. Exige correção (Bonferroni, Holm, FDR).
5. **IC é mais informativo que p-valor** — mostra magnitude e precisão.

## Como reportar

- Sempre: efeito (diferença de médias, OR, RR) + IC95% + p-valor.
- **Nunca** reportar só p-valor.
- Arredondar p a 3 casas; p < 0,001 reportar como "p < 0,001", não "p = 0,000".

## Testes bilaterais vs unilaterais

- **Bilateral (two-tailed)**: H₁ = diferença ≠ 0. Padrão, mais conservador.
- **Unilateral**: só faz sentido quando direção é justificável a priori (ex.: novo fármaco não pode ser pior que placebo). Uso raro e precisa ser declarado antes da análise.

## Conexão com perícia

- Laudo que cita "p < 0,05" isolado é frágil — pedir efeito + IC.
- Metanálise usa IC para forest plot: IC cruzando o "1" (para OR/RR) = sem diferença significativa.
- Em discussão de causalidade, combinar inferência + critérios de Hill (plausibilidade biológica, temporalidade, gradiente dose-resposta).
