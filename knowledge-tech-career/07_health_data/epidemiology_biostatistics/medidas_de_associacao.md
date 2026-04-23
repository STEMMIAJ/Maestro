---
titulo: "Medidas de associação — RR, OR, risco absoluto, NNT"
bloco: "07_health_data/epidemiology_biostatistics"
tipo: "fundamento"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 7
---

# Medidas de associação

Quantificam **quanto** uma exposição muda risco/chance do desfecho. Em perícia, é onde o raciocínio causal fica mensurável.

## Tabela 2×2 de referência

| | Desfecho + | Desfecho − | Total |
|---|---|---|---|
| **Expostos** | a | b | a+b |
| **Não expostos** | c | d | c+d |

## Risco absoluto (AR, incidência)

- Expostos: `R₁ = a / (a+b)`.
- Não expostos: `R₀ = c / (c+d)`.

## Risco relativo (RR)

- `RR = R₁ / R₀`.
- Usado em **coorte** e ensaio clínico (denominador conhecido).
- Interpretação: RR = 2 → exposto tem 2× o risco do não exposto.
- RR = 1 → sem associação; < 1 → exposição é protetora.

## Odds ratio (OR)

- Odds: `a/b` (expostos) e `c/d` (não expostos).
- `OR = (a × d) / (b × c)`.
- Usado em **caso-controle** (não há denominador populacional).
- Aproxima RR quando desfecho é raro (< 10%).
- Em desfecho frequente, OR **superestima** RR — erro comum em mídia.

## Diferença de risco (ARR — absolute risk reduction)

- `ARR = R₀ − R₁` (em intervenção que reduz risco).
- Absoluta, em pontos percentuais. Mais informativa clinicamente que RR.

Exemplo: RR = 0,50 soa impactante, mas se R₀ = 2% e R₁ = 1%, ARR = 1 p.p. → impacto populacional pequeno.

## NNT — número necessário tratar

- `NNT = 1 / ARR`.
- Interpretação: quantos pacientes precisam receber o tratamento para **evitar 1 evento**.
- Menor NNT = tratamento mais eficiente.
- Ex.: ARR 0,02 → NNT = 50; tratar 50 para evitar 1 evento.

## NNH — number needed to harm

- Análogo para danos: `NNH = 1 / ARI` (absolute risk increase).
- Menor NNH = tratamento mais tóxico.

## Redução relativa do risco (RRR)

- `RRR = 1 − RR = (R₀ − R₁) / R₀`.
- Expressa em %. Frequentemente inflada em marketing médico.

## Fração atribuível

### Na população exposta (FAR — attributable risk fraction)

- `FAR = (R₁ − R₀) / R₁`.
- % dos casos entre expostos atribuíveis à exposição.

### Na população total (PAF — population attributable fraction)

- `PAF = Pₑ × (RR − 1) / [Pₑ × (RR − 1) + 1]`, onde Pₑ = prevalência da exposição.
- Mede impacto populacional — útil para políticas de saúde.

## Hazard ratio (HR)

- Vindo da regressão de Cox em análise de sobrevida.
- Interpretação similar a RR, mas **ao longo do tempo**.
- Pressupõe riscos proporcionais (testar Schoenfeld).

## Intervalo de confiança

- Todas as medidas devem vir com **IC95%**.
- IC que contém 1 (para RR, OR, HR) → sem associação significativa.
- IC que contém 0 (para ARR) → sem diferença significativa.

## Exemplo clínico

Ensaio de anticoagulante em pós-operatório:
- Controle (placebo): 40 TVP em 500 (R₀ = 8%).
- Tratamento: 20 TVP em 500 (R₁ = 4%).

- RR = 4/8 = 0,50 (IC95% 0,30–0,84).
- ARR = 4 p.p.
- RRR = 50%.
- NNT = 1/0,04 = 25.

Relato honesto: "o anticoagulante reduz o risco de TVP em 50% em termos relativos (4% → 2%), precisando tratar 25 pacientes para evitar 1 TVP".

## Exemplo pericial

Metanálise cita OR = 3,2 (IC 1,5–6,8) entre droga X e dano Y.

- Desfecho é raro? Se sim, OR ≈ RR.
- IC não inclui 1 → associação significativa.
- Magnitude moderada, mas plausibilidade biológica + temporalidade + gradiente dose-resposta precisam estar presentes para alegar causalidade.

## Armadilhas

1. Reportar só RR relativo sem risco absoluto basal.
2. Tratar OR como RR em desfechos comuns.
3. NNT sem janela de tempo (NNT em 1 ano ≠ NNT em 5 anos).
4. Ignorar IC — efeito pequeno e IC largo = incerteza alta.
