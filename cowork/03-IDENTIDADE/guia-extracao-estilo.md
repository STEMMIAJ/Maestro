# Guia de Extração de Estilo

## 1. Conceito

"Extrator de estilo" = script de NLP simples que lê peças já redigidas pelo Dr. Jesus (laudos, petições, pareceres) e produz um perfil quantitativo do jeito dele de escrever. Não usa IA generativa para medir — usa estatística descritiva e contagem de n-grams (sequências de N palavras consecutivas). Saída é um JSON determinístico que vira prompt de sistema para os agentes de redação.

Objetivo: qualquer peça nova gerada pelo Claude deve ser indistinguível, em métricas de estilo, das peças históricas do usuário.

## 2. Corpus de entrada

Caminho: `02-BIBLIOTECA/peticoes/_corpus-estilo/`

Organização mínima:

```
_corpus-estilo/
├── laudos/           # .txt ou .md — apenas corpo redigido, sem cabeçalho institucional
├── peticoes/         # idem
├── pareceres/        # idem
└── quesitos/         # respostas do perito a quesitos
```

Regras do corpus:
- Mínimo viável: 5 peças por categoria. Ideal: 20+.
- Texto limpo: remover cabeçalho, rodapé, timbre, tabelas, citações de parte contrária (o que importa é a voz do usuário).
- Formato: `.txt` UTF-8 ou `.md`. Nada de PDF direto (extrair texto antes).
- Nome de arquivo: `AAAA-MM_tipo_brevedescricao.txt` (ex.: `2025-03_laudo_lombalgia-INSS.txt`).

## 3. Métricas a extrair (10 obrigatórias)

| # | Métrica | O que mede | Como calcular |
|---|---|---|---|
| 1 | Comprimento médio de frase (palavras) | Fôlego da prosa | total de palavras ÷ total de frases (split por `.!?`) |
| 2 | Comprimento médio de parágrafo (frases) | Densidade argumentativa | total de frases ÷ total de parágrafos (split por `\n\n`) |
| 3 | TTR (type-token ratio) | Riqueza lexical | tokens únicos ÷ total de tokens (amostra de 1000 tokens) |
| 4 | Top-20 bigramas | Colocações preferidas ("nesse sentido", "ante o exposto") | contagem de pares de palavras consecutivas, filtrando stopwords puras |
| 5 | Top-20 trigramas | Fórmulas fixas ("ante o exposto,", "resta comprovado que") | idem com triplas |
| 6 | Conectores (lista fechada) | Quais conectores usa e com que frequência relativa | contar ocorrências de lista pré-definida: "outrossim", "destarte", "nesse sentido", "ante o exposto", "cumpre salientar", "impende observar", "não obstante", "com efeito", "isto posto", "diante do exposto", "nesse diapasão" |
| 7 | Densidade de latim | Ocorrências de expressões latinas ÷ 1000 palavras | lista: "data venia", "ex vi", "in casu", "mutatis mutandis", "a quo", "ad quem", "sub judice", "lato sensu", "stricto sensu", "prima facie" |
| 8 | Distribuição 1ª/3ª pessoa | Como o perito se refere a si | contar "analisei/concluí/verifiquei" (1ª) vs. "o Perito/o subscritor/este Perito/constatou-se" (3ª impessoal) |
| 9 | Densidade de citações | Citações legais por 1000 palavras | regex para "art. \d+", "Lei \d+", "STF", "STJ", "CPC", "CC/2002", "Súmula" |
| 10 | Comprimento médio de título de seção | Estilo de cabeçalho | média de palavras em linhas que começam com maiúscula, numeração romana ou arábica e terminam sem ponto |

Métricas opcionais (extra, quando corpus ≥ 30 peças):
- Posição média do verbo principal na frase (começa com sujeito? com advérbio?)
- Frequência de voz passiva
- Uso de nota de rodapé (sim/não)
- Ratio de períodos compostos por subordinação vs. coordenação

## 4. Saída: `perfil-estilo.json`

Caminho de saída: `03-IDENTIDADE/perfil-estilo.json` (sobrescreve a cada nova extração).

Esquema:

```json
{
  "gerado_em": "AAAA-MM-DD",
  "corpus": {
    "total_pecas": 0,
    "total_palavras": 0,
    "distribuicao": {"laudos": 0, "peticoes": 0, "pareceres": 0, "quesitos": 0}
  },
  "metricas": {
    "frase_media_palavras": 0.0,
    "paragrafo_medio_frases": 0.0,
    "ttr": 0.0,
    "top_bigramas": [["ante o", 12], ["nesse sentido", 9]],
    "top_trigramas": [["ante o exposto", 11]],
    "conectores": {"nesse sentido": 9, "ante o exposto": 11, "outrossim": 0},
    "latim_por_mil": 1.4,
    "pessoa": {"primeira": 3, "terceira_tecnica": 142, "impessoal": 58},
    "citacoes_por_mil": 4.2,
    "titulo_medio_palavras": 2.8
  },
  "assinaturas": [
    "Frase-gabarito 1: abertura típica de laudo.",
    "Frase-gabarito 2: transição típica entre tese e conclusão.",
    "Frase-gabarito 3: fórmula de resposta a quesito.",
    "Frase-gabarito 4: fórmula de referência a exame.",
    "Frase-gabarito 5: fecho típico."
  ],
  "termos_evitados_observados": ["salvo melhor juízo", "acreditamos que"],
  "fonte_manual": "estilo-redacao.md",
  "observacoes": ""
}
```

"Assinaturas" são 5 frases reais do corpus que melhor representam o usuário. Critério de seleção: frases que contêm ≥ 2 dos top-10 trigramas. Escolha automática; usuário pode editar à mão.

## 5. Pipeline de execução

1. `scan`: listar todos os `.txt`/`.md` em `_corpus-estilo/` recursivamente.
2. `clean`: remover linhas de cabeçalho/rodapé detectáveis por regex (datas isoladas, CRM isolado, nome em caixa-alta isolado).
3. `tokenize`: separar em parágrafos, frases, tokens. Normalizar aspas/hifens.
4. `measure`: aplicar as 10 métricas.
5. `signatures`: ranquear frases por cobertura de top-trigramas; escolher 5.
6. `write`: salvar `perfil-estilo.json`.
7. `diff`: comparar com o perfil anterior (se existir) e listar mudanças significativas (≥ 15% em qualquer métrica).

Implementação sugerida: Python 3 puro + `collections.Counter` + regex. Sem dependência externa pesada. Script fica em `~/stemmia-forense/automacoes/extrair_perfil_estilo.py` (a criar — fora do escopo deste guia).

## 6. Regatilho de regeração

Regerar `perfil-estilo.json` quando:
- Corpus cresce ≥ 20% em número de peças desde a última extração.
- Usuário edita `estilo-redacao.md` (mudança manual sobrescreve métrica automática).
- Passaram-se 6 meses desde a última geração.
- Usuário executa comando explícito "regerar perfil de estilo".

## 7. Como o perfil vira prompt de sistema

O agente de redação (qualquer um que produza texto para o usuário: laudo, petição, parecer, e-mail) recebe, como prefixo do system prompt, um bloco construído dinamicamente a partir de `perfil-estilo.json` + `estilo-redacao.md` + `dados-profissionais.md`.

Estrutura do bloco injetado:

```
# IDENTIDADE DO AUTOR
Nome: {{NOME_PROFISSIONAL}} — CRM {{CRM_UF_NUMERO}} — RQE {{RQE_NUMERO}}.
Atua como: perito judicial.

# ESTILO (escolhas manuais)
- Tratamento ao juiz: <da opção marcada em estilo-redacao.md §1>
- Pessoa verbal: <§4>
- Auto-designação: <§5>
- Fecho: <§14>
- Termos proibidos: <§13 + termos_evitados_observados do JSON>

# ESTILO (métricas do corpus real)
- Frase média: {frase_media_palavras} palavras. Respeitar ±15%.
- Parágrafo médio: {paragrafo_medio_frases} frases. Máx. {limite} linhas.
- Conectores permitidos com frequência observada: <lista do JSON, só os com contagem > 0>
- Latim: usar no máximo {latim_por_mil} expressões por 1000 palavras, em itálico.
- Referência a si: prevalece {terceira_tecnica} (3ª pessoa técnica).
- Densidade de citações esperada: {citacoes_por_mil} por 1000 palavras.

# ASSINATURAS (imitar ritmo e estrutura destas frases reais)
1. <assinatura 1>
2. <assinatura 2>
3. <assinatura 3>
4. <assinatura 4>
5. <assinatura 5>

# VALIDAÇÃO PÓS-GERAÇÃO
Antes de entregar, verificar que a peça gerada respeita:
- comprimento médio de frase dentro de ±15% da métrica do corpus
- ausência total de termos da lista de proibidos
- uso de pelo menos 2 conectores da lista do corpus
- fecho exato conforme §14
Se falhar, reescrever.
```

O bloco é montado por um script pré-resposta (hook `UserPromptSubmit` ou função utilitária chamada pelo agente). A ordem de precedência é:
1. `estilo-redacao.md` (escolha manual do usuário) — vence em conflito.
2. `perfil-estilo.json` (métrica observada) — preenche o que o usuário não decidiu.
3. `dados-profissionais.md` — fornece apenas dados, nunca estilo.

## 8. Auditoria

Cada peça gerada grava em `04-LOGS/geracoes.jsonl` uma linha com: data, tipo de peça, métricas da peça gerada, comparação com o perfil (desvio percentual por métrica). Desvios > 20% em 3 peças seguidas disparam alerta e revisão manual do perfil.
