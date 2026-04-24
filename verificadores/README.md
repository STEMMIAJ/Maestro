# Verificadores — Maestro

Peca que transforma o Maestro de "pipeline que gera" em "pipeline que garante".

## verificador_peticao_pdf.py

Rastreabilidade afirmacao -> trecho-fonte. Le uma peticao Markdown, extrai
afirmacoes factuais e testa cada uma contra o `TEXTO-EXTRAIDO.txt` da pasta
do processo.

### Uso

```bash
python3 verificador_peticao_pdf.py \
  --peticao ./peticao.md \
  --processo "~/Desktop/ANALISADOR FINAL/processos/0001234-56.2026.8.13.0024" \
  [--threshold-ancorada 85] [--threshold-suspeita 60] \
  [--out-dir <pasta>] [--dry-run] [--verbose]
```

Gera, na pasta do processo (ou em `--out-dir`):

- `RELATORIO-VERIFICACAO.json` (ver `SCHEMA-verificacao.json`)
- `RELATORIO-VERIFICACAO.md` (tabela legivel por humano)

### Interpretacao

Cada afirmacao recebe um dos status:

- **ANCORADA** — score >= threshold-ancorada (default 85). Ha trecho no PDF.
- **SUSPEITA** — score entre thresholds. Revisar manualmente.
- **SEM-ANCORA** — score < threshold-suspeita. Afirmacao sem respaldo nos autos.
- **CITACAO_LEGAL** — apenas referencia a lei/CPC/artigo. Nao verificada.

### Exit code (integrac ao pipeline)

- `0` tudo ANCORADA/CITACAO_LEGAL -> pipeline segue.
- `1` ha SUSPEITA mas zero SEM-ANCORA -> warning, pipeline segue com aviso.
- `2` ha pelo menos uma SEM-ANCORA -> `pericia_completa.sh` deve abortar.

### Dependencia

`rapidfuzz` (opcional, mas recomendado):

```bash
pip install rapidfuzz
```

Sem rapidfuzz o script usa fallback aproximado (substring + overlap de tokens).
Integracao no `pericia_completa.sh` e Onda 2.
