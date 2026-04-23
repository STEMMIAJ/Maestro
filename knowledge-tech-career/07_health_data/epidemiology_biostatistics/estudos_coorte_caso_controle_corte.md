---
titulo: "Desenhos de estudo — coorte, caso-controle, transversal"
bloco: "07_health_data/epidemiology_biostatistics"
tipo: "fundamento"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 8
---

# Desenhos de estudo observacionais

Três desenhos-base: **coorte**, **caso-controle** e **transversal** (corte). A escolha depende da doença (rara/comum), do tempo/recurso, da pergunta.

## Estudo de coorte

Parte da **exposição** e segue no tempo para medir **incidência do desfecho**.

- **Prospectivo**: recruta expostos e não expostos, acompanha adiante.
- **Retrospectivo (histórico)**: recria a coorte a partir de registros antigos, "segue" até presente.

### Vantagens

- Mede incidência direta → RR verdadeiro.
- Temporalidade clara (exposição antes do desfecho).
- Boa para exposições raras.
- Avalia múltiplos desfechos a partir de uma exposição.

### Limitações

- Caro e longo para desfechos raros.
- Perdas de seguimento.
- Não serve bem para doenças raras.

Exemplos: Framingham Heart Study; coorte de Pelotas (Brasil); coorte ELSA-Brasil.

## Estudo caso-controle

Parte do **desfecho** (casos = com doença; controles = sem) e olha para trás para comparar exposições.

### Vantagens

- Eficiente para **doenças raras** ou de latência longa.
- Rápido e barato (amostra pequena).
- Permite avaliar múltiplas exposições.

### Limitações

- **Viés de memória** (cases lembram mais).
- **Seleção de controles** é crítica — precisam vir da mesma população que originou os casos.
- Não estima incidência — usa **odds ratio**.
- Temporalidade ambígua (exposição pode ser consequência).

### Variantes

- **Caso-controle aninhado** (nested): dentro de coorte — reduz viés de memória.
- **Caso-coorte**: controles sorteados da coorte basal.

Exemplos: associação tabagismo × câncer pulmão (Doll & Hill, 1950); talidomida × focomelia.

## Estudo transversal (corte / cross-sectional)

Mede exposição e desfecho **simultaneamente** em um momento.

### Vantagens

- Rápido, barato.
- Estima **prevalência**.
- Útil para planejamento de serviço.

### Limitações

- Não estabelece temporalidade (não há "antes" e "depois").
- Não serve para causalidade isolada.
- Doenças de curta duração são subestimadas.

Exemplos: Vigitel; inquéritos de saúde escolar; censos.

## Ensaio clínico randomizado (ECR)

Nível mais alto entre desenhos primários.

- Randomização elimina confundimento (em média).
- Cegamento reduz viés.
- Permite inferência causal direta.
- Limitação: custoso, ético nem sempre permite.

Fora do escopo observacional, mas entra no ranking.

## Ecológico

Unidade de análise é **grupo** (cidade, país), não indivíduo.

- Rápido, usa dados agregados (SIM, IBGE).
- Risco de **falácia ecológica**: associação no nível agregado não implica individual.

## Hierarquia de evidência (GRADE simplificado)

Do mais forte ao mais fraco:

1. Metanálise de ECRs.
2. ECR individual bem conduzido.
3. Coorte prospectiva grande.
4. Caso-controle bem desenhado.
5. Transversal / série de casos.
6. Relato de caso / opinião de especialista.

## Quando escolher cada

| Cenário | Desenho |
|---|---|
| Exposição rara, recursos amplos | Coorte prospectiva |
| Doença rara, recursos limitados | Caso-controle |
| Estimar prevalência / planejamento | Transversal |
| Testar intervenção (fármaco, protocolo) | ECR |
| Dados agregados já disponíveis | Ecológico |
| Exposição passada + registros longos | Coorte retrospectiva |

## Implicações periciais

- **Metanálise de ECRs** é o padrão-ouro quando disponível.
- **Caso-controle único** tem limitações — exigir replicação.
- **Estudos ecológicos** citados para inferir causalidade individual = crítica obrigatória.
- **Temporalidade** (critério de Hill) só é garantida em coorte e ECR.

## Reporte e ferramentas

- **STROBE**: diretriz para reporte de estudos observacionais.
- **CONSORT**: para ECRs.
- **PRISMA**: para revisões sistemáticas e metanálises.
- Checagem rápida do perito: rodar checklist CASP antes de citar estudo.
