---
titulo: Verificador petição-PDF que rastreia afirmação -> trecho-fonte com rapidfuzz e exit code bloqueante
tipo: evidencia
dominio: Python
subtopico: NLP básico (fuzzy matching) + CLI enforcement
nivel_demonstrado: 3
versao: 0.1
status: validada
ultima_atualizacao: 2026-04-23
fonte: /Users/jesus/Desktop/STEMMIA Dexter/Maestro/verificadores/verificador_peticao_pdf.py
---

## Descrição
CLI que lê uma petição em Markdown, segmenta em sentenças (regex unicode-aware para pt-BR), classifica
cada sentença como fato verificável vs. citação legal (regex de artigos/CPC/súmula/CF), e para cada
fato procura âncora no corpus `TEXTO-EXTRAIDO.txt` do processo: primeiro substring exata normalizada
(NFKD sem acento), depois janelas deslizantes de 500 chars com `rapidfuzz.partial_ratio`. Produz
relatório JSON+Markdown e exit code 0/1/2 que bloqueia o pipeline se houver afirmação SEM-ANCORA.

## Arquivo real
`/Users/jesus/Desktop/STEMMIA Dexter/Maestro/verificadores/verificador_peticao_pdf.py`

## Habilidade demonstrada
- `Python.sintaxe básica` — 3 (800+ linhas, argparse, logging, pathlib)
- `Estatística.descritiva` — 2 (threshold-ancorada/suspeita configurável via CLI)
- `Perícia.quesitos e impugnação` — 4 (a lógica reflete domínio pericial: o que é fato vs. citação legal)
- `Automação doc.` — 3

## Trecho relevante
```python
try:
    from rapidfuzz import fuzz as _rf_fuzz
    RAPIDFUZZ_OK = True
except ImportError:
    _rf_fuzz = None
    RAPIDFUZZ_OK = False

SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])")
CITACAO_LEGAL_RE = re.compile(
    r"(art(?:\.|igo)\s*\d+|cpc|cpp|cf/88|lei\s+n?o?\.?\s*\d|s[úu]mula\s+\d|"
    r"constitui[çc][ãa]o)", re.IGNORECASE)

# Status de cada afirmacao:
#   ANCORADA        score >= threshold-ancorada (85)
#   SUSPEITA        60 <= score < 85
#   SEM-ANCORA      score < 60
#   CITACAO_LEGAL   sentenca e apenas citacao de lei/artigo (skip)
# Exit code:
#   0  tudo ANCORADA/CITACAO_LEGAL
#   1  ha SUSPEITA mas zero SEM-ANCORA (warning)
#   2  ha pelo menos uma SEM-ANCORA (bloqueia pipeline)
```

## Data
2026-04 (Maestro sessão 02, CHECKPOINT-2026-04-23).

## Validação externa
**Média-Forte** — possui `SCHEMA-verificacao.json` + `README.md` próprios em `Maestro/verificadores/`.
Desenhado com gate de CI (exit code). Ainda sem prova de uso em N>10 petições reais (pedir registro).

## Limitações conhecidas
- Falha silenciosa se `rapidfuzz` não instalado — cai para substring exata (perde recall).
- Heurística de citação legal não pega Resolução CNJ, portaria, IN Receita.
- Sem suporte a OCR: se TEXTO-EXTRAIDO.txt for ruim (PDF escaneado sem OCR), tudo vira SEM-ANCORA falso.
