---
titulo: "Teste A/B na prática — quando faz sentido em fluxos processuais"
bloco: "06_data_analytics/experimentation"
tipo: "pratica"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 7
---

# Teste A/B na prática

A/B = comparar duas versões (A controle, B variante) randomizando quem recebe cada uma, medir desfecho. Nasceu em marketing, vale para qualquer fluxo com métrica objetiva — inclusive perícia.

## Quando faz sentido

- Existem **duas formas plausíveis** de fazer a mesma coisa.
- A diferença esperada é **pequena** e precisa de dado para decidir.
- Desfecho é **mensurável e rápido** (semanas, não anos).
- Há **volume suficiente** para detectar diferença (n ≥ 30 por braço, ideal maior).

## Quando NÃO faz sentido

- Diferença óbvia (não precisa teste).
- Volume ínfimo (perito faz 10 perícias/mês → impossível detectar efeito moderado).
- Impacto ético (não dá para testar protocolo clínico sem ética).
- Métrica mal definida.

## Exemplo pericial: dois fluxos de triagem de processos

**Problema**: receber nomeação judicial → decidir se aceita. Dois fluxos:

- **A (controle)**: leitura integral do processo antes de decidir (45 min médios).
- **B (variante)**: checklist automatizado + leitura focada (15 min).

**Pergunta**: fluxo B mantém qualidade de decisão (aceitar caso viável, recusar inviável) com menos tempo?

**Desfechos**:
- **Primário**: % de processos aceitos que resultaram em laudo entregue no prazo.
- **Secundário**: tempo médio de triagem; subjetivo de carga cognitiva (escala 1–10).

**Alocação**: 50/50 dos próximos 60 processos (30 em cada), randomizado por `random.random() < 0.5`.

## Passos

### 1. Hipótese

- H₀: taxa de entrega-no-prazo é igual entre A e B.
- H₁: taxa difere.
- Definir efeito mínimo relevante (ex.: queda > 10 p.p. inaceitável).

### 2. Tamanho amostral

Calcular via `pwr` (R) ou `statsmodels.stats.power` (Python). Para detectar diferença de 10 p.p. em proporções com α=0,05 e poder 80%, precisa ~190 por braço (aprox.). Para perito solo com 10 processos/mês, **impraticável** com esse efeito — rever: ou aceitar efeito maior, ou estender tempo.

### 3. Randomização

- Aleatorização verdadeira (não "alterna semana"): `python -c "import random; print(random.choice(['A','B']))"`.
- Registrar alocação antes de ver resultado.

### 4. Cegamento

Ideal que quem avalia desfecho não saiba do braço. Difícil quando é autoavaliação — documentar o risco.

### 5. Coleta

Log em planilha / SQLite: `processo_id, braço, tempo_triagem, decisão, desfecho, data`.

### 6. Análise

- Proporção com intervalo de confiança (binomial exato para n pequeno).
- Teste qui-quadrado (ou Fisher) para comparar proporções.
- t de Student ou Mann-Whitney para tempo.
- Reportar efeito + IC95% + p-valor.

### 7. Decisão

- Resultado claramente melhor e IC sem sobreposição → adotar variante.
- Resultado equivalente (IC estreito em torno de zero) → adotar a mais barata/rápida.
- Resultado inconclusivo (IC largo) → coletar mais dado ou aceitar incerteza.

## Variantes de desenho

- **A/A test**: duas vezes o mesmo fluxo. Serve para calibrar variância basal.
- **Crossover**: mesmo indivíduo faz A depois B (pareado). Reduz variância, mas efeito de ordem pode contaminar.
- **Multi-variante (A/B/C)**: precisa correção para múltiplas comparações (Bonferroni).

## Armadilhas

1. **Peeking**: olhar resultado parcial e parar cedo. Infla falso positivo. Usar métodos sequenciais (Pocock, O'Brien-Fleming) se for interromper.
2. **Novidade**: B pode parecer melhor só porque é novidade — medir em janela longa.
3. **Viés de seleção**: randomização falhou (ex.: B só em processos mais simples).
4. **Métrica proxy**: otimizar tempo de triagem pode piorar qualidade — sempre métrica de qualidade junto.

## Ferramentas

- Python: `scipy.stats`, `statsmodels`.
- R: `pwr`, `exact2x2`.
- Planilha: para volumes < 100, Excel resolve com fórmulas.
