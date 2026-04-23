---
titulo: "Medidas de frequência — prevalência, incidência, densidade"
bloco: "07_health_data/epidemiology_biostatistics"
tipo: "fundamento"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 7
---

# Medidas de frequência em epidemiologia

Quantificam ocorrência de doença/evento na população. Base para comparar grupos e avaliar risco.

## Prevalência

Fração da população que **tem** a condição em um momento/período.

- **Prevalência pontual** = `casos existentes / população` (snapshot).
- **Prevalência de período** = `casos existentes durante período / população do período`.

Características:
- Numerador inclui casos antigos e novos.
- Sensível à **duração** da doença. Condições crônicas têm prevalência alta.
- Útil para planejamento de serviço (quantos leitos, quanta medicação).
- Expressa em proporção (0–1) ou por 100.000 habitantes.

Exemplo: prevalência de hipertensão em adultos brasileiros ~24% `[TODO/RESEARCH: dado Vigitel 2024]`.

## Incidência

Fração de pessoas que **desenvolvem** a condição em um período (antes sadias).

### Incidência cumulativa (risco)

- `casos novos / população em risco no início`.
- Adimensional, precisa declarar período.
- Pressupõe seguimento completo de todos.

Exemplo: 8 casos de TVP pós-operatória em 200 pacientes em 30 dias → incidência cumulativa 4% em 30 dias.

### Densidade de incidência (taxa)

- `casos novos / soma dos tempos sob risco (pessoa-tempo)`.
- Unidade: casos / pessoa-ano (ou pessoa-mês).
- Lida com seguimento variável (censura).

Exemplo: 12 casos de IAM em coorte de 500 adultos seguidos 5 anos (2.480 pessoas-ano após perdas) → densidade = 12/2480 ≈ 4,8/1.000 pessoas-ano.

## Relação entre prevalência e incidência

Para doença estável (fluxo entrada ≈ saída):

```
Prevalência ≈ Incidência × Duração média
```

Implicação: se tratamento prolonga vida sem curar, prevalência sobe mesmo com incidência constante (ex.: HIV com antirretroviral).

## Taxa de ataque

Caso especial de incidência cumulativa em surto: `casos / expostos no período do surto`. Clássico em investigação de intoxicação alimentar.

## Taxa de ataque secundária

`casos secundários / contatos suscetíveis de um caso índice`. Mede transmissibilidade.

## Letalidade (CFR, case fatality rate)

- `mortes por doença / casos confirmados da doença`.
- Diferente de mortalidade: CFR condiciona ao diagnóstico.
- Sensível a subnotificação — COVID precisou corrigir por soroprevalência.

## Mortalidade

- **Mortalidade geral**: `óbitos / população` (em período).
- **Mortalidade específica**: `óbitos por causa X / população`.
- **Mortalidade proporcional**: `óbitos por causa X / total de óbitos` (não é taxa, só composição).

## Padronização

Comparar populações com estruturas etárias diferentes exige ajuste.

- **Direta**: aplica taxas específicas da população de estudo à população-padrão.
- **Indireta**: aplica taxas da população-padrão à estrutura da população de estudo → SMR (Standardized Mortality Ratio).

## Fontes brasileiras

- **SIM** (Sistema de Informações sobre Mortalidade): causas de óbito.
- **SINASC**: nascidos vivos.
- **SINAN**: agravos de notificação compulsória.
- **SIH** (AIH): internação hospitalar.
- **SIA**: ambulatorial.
- **Vigitel**: inquérito telefônico de fatores de risco.

## Exemplos periciais

- Estimar **probabilidade de dano** pós-procedimento: usar incidência cumulativa em literatura pertinente.
- Comparar **mortalidade** entre dois serviços: padronizar por idade e gravidade (case-mix).
- Avaliar **subnotificação**: divergência entre SIM local e estimativa por captura-recaptura.

## Armadilhas

1. Confundir prevalência com incidência — erro básico em laudo.
2. Reportar taxa sem denominador e período.
3. Esquecer censura em seguimento longo → usar densidade, não cumulativa.
4. Comparar populações com idades diferentes sem padronizar.
