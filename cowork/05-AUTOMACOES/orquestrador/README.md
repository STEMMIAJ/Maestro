# Orquestrador — ingestão determinística de peças reais

**Versão:** 0.1.0
**Criado:** 2026-04-20

Pipeline para processar arquivos que o Dr. Jesus solta em `INBOX/`:
extrai texto, normaliza, classifica por família/subtipo e arquiva no destino correto,
com idempotência por SHA-256 e relatório por rodada.

---

## Uso rápido

```bash
cd "/Users/jesus/Desktop/STEMMIA Dexter/cowork/05-AUTOMACOES/orquestrador"

# 1) Soltar arquivos dentro de INBOX/
cp ~/Downloads/*.docx INBOX/

# 2) Dry-run para ver o que vai acontecer (nada é movido)
python3 orquestrador.py --dry-run --verbose

# 3) Rodar em produção
python3 orquestrador.py --workers 4

# 4) Relatório gerado em RELATORIOS/<timestamp>.md
```

---

## Fluxo

```
INBOX/arquivo.docx
   │
   ├─ extrair texto (docx-zip | pdftotext | pdfminer | text)
   ├─ normalizar (NFC, BOM, espaços, quebras)
   ├─ classificar (regras_classificacao.json, score por palavra-chave + título)
   │
   ├─ se score >= limiar:
   │     -> cowork/02-BIBLIOTECA/<familia>/_fonte-originais-perito/<subtipo>/
   │        ├─ <basename>-<sha8>.txt     (texto normalizado)
   │        ├─ <basename>-<sha8>.docx    (original movido)
   │        └─ <basename>-<sha8>.meta.json
   │
   └─ se score < limiar:
         -> AMBIGUO/<basename>-<sha8>.*  (Dr. Jesus decide à mão)

_logs/index.jsonl  (append-only, uma linha JSON por item)
RELATORIOS/<ts>.md (checklist da rodada)
```

---

## Extensões suportadas

- `.docx` — stdlib zipfile + regex sobre `word/document.xml`
- `.pdf` — tenta `pdftotext` (poppler); fallback `pdfminer.six` se instalado
- `.txt` / `.md` — UTF-8, UTF-8-SIG, Latin-1, CP1252 (primeira que decodifica)

Outras extensões vão para `status=erro` no relatório.

---

## Regras de classificação

Editáveis em `regras_classificacao.json`. Estrutura:

```json
{
  "_meta": {
    "limiar_geral": 3,
    "titulo_bonus": 5,
    "max_linhas_titulo": 6
  },
  "familias": {
    "peticoes": {
      "subtipos": {
        "aceite": {
          "titulo_regex": "(?i)aceite de encargo|...",
          "palavras_chave_positivas": ["aceito o encargo", "..."],
          "antonimos": ["escusa", "..."]
        }
      }
    }
  }
}
```

Score por subtipo =
  `titulo_bonus` se título bate o regex
  + soma(min(contagem(chave), 3)) para cada palavra-chave positiva
  − soma(min(contagem(chave)·2, 4)) para cada antônimo.

Se o melhor score < `limiar_geral`, o arquivo vai para `AMBIGUO/`.

---

## Idempotência

Cada item processado é registrado em `_logs/index.jsonl` com o SHA-256 dos bytes originais.
Em rodadas subsequentes, arquivos com SHA já visto recebem `status=duplicado` e NÃO são
movidos nem regravados.

Para reprocessar tudo:
```bash
python3 orquestrador.py --rebuild-index
```
(o index antigo vira `.bak-<ts>`.)

---

## Pastas

| Pasta | Conteúdo |
|---|---|
| `INBOX/` | Entrada. Dr. Jesus deposita aqui. Esvazia ao processar. |
| `AMBIGUO/` | Saída de baixa confiança. Decisão manual. |
| `RELATORIOS/` | Um `.md` por rodada com resumo e tabela por item. |
| `_logs/` | `index.jsonl` append-only. Única fonte de idempotência. |

---

## CLI

| Flag | Descrição |
|---|---|
| `--inbox PATH` | Override da pasta de entrada |
| `--workers N` | Paralelismo (default 4) |
| `--dry-run` | Processa sem mover nada, só reporta |
| `--rebuild-index` | Arquiva index antigo e reprocessa tudo |
| `--verbose` / `-v` | Logs em stderr |

Códigos de retorno: `0` = sem erros, `2` = houve pelo menos 1 erro.

---

## Princípios (não-negociáveis)

1. **Constância:** mesma estrutura de nome (`<slug>-<sha8>.ext`), mesmo frontmatter, mesma hierarquia de pastas.
2. **Padrão:** regras externas em JSON — comportamento nunca muda por hard-code.
3. **Idempotência:** rodar 10 vezes = rodar 1 vez.
4. **Sem invenção:** abaixo do limiar → AMBIGUO/. Nunca "chuta" subtipo.
5. **Append-only:** `_logs/index.jsonl` só cresce. Rebuild explícito via flag.

---

## Próximos passos sugeridos

- Integração com `aplicar_template.py`: após arquivar ≥2 peças do mesmo subtipo, chamar
  `analisar_subtipo.py` (a criar) para gerar diff e candidatos de placeholder.
- Extração de CNJ automática do texto para preencher campo em `.meta.json`.
- Detecção de timbrado/assinatura em imagens incorporadas (`word/media/`).
