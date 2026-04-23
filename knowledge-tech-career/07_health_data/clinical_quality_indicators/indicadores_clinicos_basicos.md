---
titulo: "Indicadores clínicos básicos — mortalidade, reinternação, ISC, cesárea"
bloco: "07_health_data/clinical_quality_indicators"
tipo: "referencia"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 7
---

# Indicadores clínicos básicos

Padrão internacional para medir qualidade assistencial. Donabedian classifica em **estrutura**, **processo** e **resultado**. Os indicadores abaixo são de **resultado** — os mais usados em auditoria e perícia.

## Mortalidade intra-hospitalar

- **Definição**: óbitos durante a internação / altas + óbitos no período.
- Geral: média nacional SUS em torno de 3–5% `[TODO/RESEARCH: referência 2026]`; varia enormemente por perfil.
- Específica: **mortalidade por IAM** (objetivo < 10%), **mortalidade cirúrgica geral** (< 2%), **mortalidade materna** (por 100.000 nascidos vivos).
- Ajustar por **case-mix** (gravidade, idade, comorbidades). APACHE II, SAPS II em UTI; Charlson geral.

Fonte: SIH + CNES + SIM (linkage).

## Taxa de reinternação em 30 dias

- **Definição**: pacientes reinternados por qualquer causa em ≤ 30 dias da alta / total de altas.
- Proxy de qualidade de alta e transição de cuidado.
- Alvo CMS (EUA): < 15% para condições rastreadas (IAM, IC, pneumonia).
- Ajustar: reinternações **não planejadas** (excluir quimioterapia programada).

Cálculo em SIH:

```sql
-- pseudo
SELECT paciente_id,
       data_alta,
       LEAD(data_inter) OVER (PARTITION BY paciente_id ORDER BY data_inter) AS prox_inter
FROM sih
WHERE ...;
-- reinternação = prox_inter - data_alta <= 30
```

## Infecção de sítio cirúrgico (ISC)

- **Definição (CDC)**: infecção em incisão ou órgão/cavidade manipulada, até 30 dias pós-cirurgia (ou 90 dias se implante).
- Classificação: superficial, profunda, órgão/espaço.
- Taxas-alvo variam por potencial de contaminação da ferida (limpa < 2%, limpo-contaminada < 5%, contaminada < 10%, infectada < 20%).
- Vigilância ativa (ANVISA/NHSN) recomendada.
- Fatores de risco: índice NNIS (classe ferida + ASA + duração cirurgia).

## Taxa de cesárea

- **Definição**: partos cesáreos / total de partos.
- **Meta OMS**: 10–15% populacional.
- Brasil (média): ~57% total (2022), com enorme variação pública x privada `[TODO/RESEARCH: Vigitel/SINASC 2024]`.
- Estratificar com classificação de **Robson** (10 grupos) permite comparação justa.

Fonte: SINASC + SIH (AIH de parto).

## Outros indicadores essenciais

### Infecção de corrente sanguínea associada a cateter (ICS-CVC)

- Densidade: casos por 1.000 cateter-dia.
- Alvo NHSN: < 1,0/1.000 cateter-dia em UTI.

### Pneumonia associada à ventilação (PAV)

- Casos por 1.000 dias de ventilação mecânica.
- Alvo: < 10/1.000 dias em UTI adulto.

### Úlcera por pressão

- Incidência em pacientes hospitalizados > 48 h.
- Estágios 2–4 são os reportáveis; alvo < 3%.

### Quedas com dano

- Por 1.000 pacientes-dia. Alvo < 1/1.000.

### Tempo porta-balão (IAM com supradesnível ST)

- Mediana < 90 min indica rede eficiente.

### Tempo porta-agulha (AVC isquêmico)

- Mediana < 60 min para trombólise.

## Avaliação comparativa

- **Benchmarking** dentro da mesma categoria hospitalar (complexidade, tipo de paciente).
- **SMR** (Standardized Mortality Ratio): observado / esperado. > 1 pior que esperado.
- **Funnel plot**: taxa × volume. Pontos fora do funil = outliers.

## Fontes de dados

- **SIH-SUS** (AIH).
- **CNES** (estrutura).
- **SIM** (óbitos).
- **SINAIS-ANVISA/NHSN Brasil** (infecções).
- **SINASC** (nascimentos).
- Prontuário eletrônico + relatório próprio em rede privada.

## Aplicações periciais

- Comparar mortalidade do hospital réu com média ajustada da mesma categoria.
- Avaliar se ISC está dentro de padrão esperado para a cirurgia em questão.
- Demonstrar desvio da taxa de cesárea em caso de suposta indução sem indicação.
- Identificar falhas em **bundle** (pacote de medidas) de prevenção de PAV/ICS.

## Limitações

1. Todo indicador depende de **codificação correta** — hospital com má codificação parece ter indicador "melhor" ou "pior" artificialmente.
2. **Case-mix** não ajustado mascara tudo.
3. Definição pode variar entre países (CDC vs NHSN vs ANVISA).
4. **Séries curtas** oscilam por acaso — exigir pelo menos 12 meses.
