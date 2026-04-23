---
titulo: Leitura e escrita de arquivos em Python
bloco: 02_programming
tipo: tutorial
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 7
---

# Leitura e escrita de arquivos

## `open` — forma genérica
```python
with open("relatorio.txt", "r", encoding="utf-8") as f:
    conteudo = f.read()

with open("saida.txt", "w", encoding="utf-8") as f:
    f.write("linha 1\n")
```

Modos: `r` leitura, `w` escrita (sobrescreve), `a` append, `rb`/`wb` binário (PDF, imagem).

`with` garante fechamento mesmo em erro. **Sempre usar.**

`encoding="utf-8"` é obrigatório para texto com acento. Sem isso, quebra em Windows.

## `pathlib.Path` — caminhos modernos
Substitui `os.path`. Mais legível.

```python
from pathlib import Path

pasta = Path.home() / "Desktop" / "STEMMIA Dexter" / "laudos"
caminho = pasta / "FICHA.json"

caminho.exists()                     # True/False
caminho.read_text(encoding="utf-8")  # lê tudo como str
caminho.write_text("oi", encoding="utf-8")
caminho.read_bytes()                 # binário

# listar
for pdf in pasta.glob("*.pdf"):
    print(pdf.name)

# recursivo
for pdf in pasta.rglob("*.pdf"):
    ...

# criar pasta
(pasta / "nova").mkdir(parents=True, exist_ok=True)
```

Por que importa: `Path` funciona igual em Mac, Linux e Windows. Evita quebrar script quando muda de máquina.

## JSON — `json.load` / `json.dump`
JSON é o formato padrão de troca de dados (DataJud, PJe API, MCP tudo usa).

```python
import json
from pathlib import Path

# ler
ficha = json.loads(Path("FICHA.json").read_text(encoding="utf-8"))
print(ficha["cnj"])

# escrever
dados = {"cnj": "0001-2024", "autor": "João"}
Path("saida.json").write_text(
    json.dumps(dados, indent=2, ensure_ascii=False),
    encoding="utf-8"
)
```

`ensure_ascii=False` preserva acentos (sem isso, vira `\u00e1`).
`indent=2` deixa legível.

## CSV — planilhas leves
```python
import csv

# ler
with open("processos.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for linha in reader:
        print(linha["cnj"], linha["autor"])

# escrever
with open("saida.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["cnj", "autor"])
    writer.writeheader()
    writer.writerow({"cnj": "0001", "autor": "João"})
```

`newline=""` evita linhas em branco no Windows.

## Excel — `openpyxl`
Para `.xlsx` (formato novo, não `.xls`).

```python
from openpyxl import load_workbook, Workbook

# ler
wb = load_workbook("processos.xlsx")
ws = wb.active                        # primeira aba
for linha in ws.iter_rows(min_row=2, values_only=True):
    cnj, autor = linha[0], linha[1]

# escrever
wb = Workbook()
ws = wb.active
ws.append(["CNJ", "Autor"])
ws.append(["0001-2024", "João"])
wb.save("saida.xlsx")
```

Instalar: `pip install openpyxl`.

## Regra de bolso
| Formato | Use |
|---|---|
| Configuração, resposta de API | JSON |
| Planilha para editor humano | CSV (simples) ou XLSX (formatação) |
| Texto corrido (laudo, log) | `.txt` via `write_text` |
| PDF, imagem | binário (`read_bytes` / `write_bytes`) |

## Armadilha frequente
Ler PDF com `read_text` → lixo. PDF é binário. Use biblioteca própria: `pypdf`, `pdfplumber` ou `pymupdf` para extrair texto.
