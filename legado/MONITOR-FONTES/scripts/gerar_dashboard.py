#!/usr/bin/env python3
"""Gera dashboard HTML em dashboard/index.html a partir do consolidado."""
import html
import json
from datetime import datetime
from pathlib import Path

RAIZ = Path.home() / "Desktop" / "MONITOR-FONTES"
CONSOLIDADO = RAIZ / "dados" / "processos-consolidados.json"
DASH = RAIZ / "dashboard" / "index.html"
CSS = RAIZ / "dashboard" / "assets" / "style.css"

CORES_FONTE = {
    "aj": "#3b82f6",
    "ajg": "#8b5cf6",
    "djen": "#10b981",
    "domicilio": "#ef4444",
    "datajud": "#f59e0b",
}

NOMES_FONTE = {
    "aj": "AJ TJMG",
    "ajg": "AJG",
    "djen": "DJEN",
    "domicilio": "Domicilio",
    "datajud": "DataJud",
}


def _chip(fonte: str) -> str:
    cor = CORES_FONTE.get(fonte, "#64748b")
    nome = NOMES_FONTE.get(fonte, fonte.upper())
    return f'<span class="chip" style="background:{cor}">{html.escape(nome)}</span>'


def _linha(p: dict) -> str:
    cnj = html.escape(p.get("cnj", ""))
    data = html.escape(p.get("data_mais_recente") or "—")
    chips = " ".join(_chip(f) for f in p.get("fontes", []))
    resumo = p.get("resumo", {})
    classe = html.escape(resumo.get("classe", ""))
    orgao = html.escape(resumo.get("orgao", ""))
    n = len(p.get("detalhes", []))
    return (
        f'<tr data-fontes="{"+".join(p.get("fontes", []))}">'
        f"<td><code>{cnj}</code></td>"
        f"<td>{data}</td>"
        f"<td>{chips}</td>"
        f"<td>{classe}</td>"
        f"<td>{orgao}</td>"
        f"<td class=n>{n}</td>"
        "</tr>"
    )


def _contagem_por_fonte(lista: list) -> dict:
    contagem = {fid: 0 for fid in CORES_FONTE}
    for p in lista:
        for f in p.get("fontes", []):
            contagem[f] = contagem.get(f, 0) + 1
    return contagem


def gerar() -> Path:
    lista = []
    if CONSOLIDADO.exists():
        try:
            lista = json.loads(CONSOLIDADO.read_text())
        except json.JSONDecodeError:
            lista = []

    contagem = _contagem_por_fonte(lista)
    cards = "".join(
        f'<div class="card" style="border-color:{CORES_FONTE[fid]}">'
        f'<div class="card-num">{contagem.get(fid, 0)}</div>'
        f'<div class="card-lbl">{NOMES_FONTE[fid]}</div>'
        "</div>"
        for fid in CORES_FONTE
    )

    filtros = "".join(
        f'<button class="filtro" data-f="{fid}" style="border-color:{CORES_FONTE[fid]}">'
        f"{NOMES_FONTE[fid]}</button>"
        for fid in CORES_FONTE
    )

    linhas_html = "".join(_linha(p) for p in lista)
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    total = len(lista)

    html_doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>MONITOR-FONTES — {total} processos</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header>
  <h1>MONITOR-FONTES</h1>
  <p class="sub">{total} processos unicos · atualizado {agora}</p>
</header>

<section class="cards">{cards}</section>

<section class="filtros">
  <span>Filtrar:</span>
  <button class="filtro ativo" data-f="todos">Todos</button>
  {filtros}
</section>

<section>
<table id="tab">
<thead><tr>
  <th>CNJ</th><th>Data</th><th>Fontes</th><th>Classe</th><th>Orgao</th><th>Intimacoes</th>
</tr></thead>
<tbody>
{linhas_html}
</tbody>
</table>
</section>

<script>
document.querySelectorAll(".filtro").forEach(btn => {{
  btn.onclick = () => {{
    document.querySelectorAll(".filtro").forEach(b => b.classList.remove("ativo"));
    btn.classList.add("ativo");
    const f = btn.dataset.f;
    document.querySelectorAll("#tab tbody tr").forEach(tr => {{
      const fontes = tr.dataset.fontes.split("+");
      tr.style.display = (f === "todos" || fontes.includes(f)) ? "" : "none";
    }});
  }};
}});
</script>
</body>
</html>"""

    DASH.parent.mkdir(parents=True, exist_ok=True)
    DASH.write_text(html_doc, encoding="utf-8")

    CSS.parent.mkdir(parents=True, exist_ok=True)
    if not CSS.exists():
        CSS.write_text(_CSS_DEFAULT)

    return DASH


_CSS_DEFAULT = """
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #0f172a; color: #e2e8f0;
  margin: 0; padding: 24px; max-width: 1400px; margin-left: auto; margin-right: auto;
}
header { border-bottom: 2px solid #1e293b; padding-bottom: 16px; margin-bottom: 24px; }
h1 { margin: 0; font-size: 1.8rem; color: #60a5fa; }
.sub { margin: 4px 0 0; color: #94a3b8; font-size: 0.9rem; }

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}
.card {
  background: #1e293b; padding: 16px;
  border-left: 4px solid #60a5fa; border-radius: 6px;
}
.card-num { font-size: 2rem; font-weight: bold; }
.card-lbl { font-size: 0.85rem; color: #94a3b8; margin-top: 4px; }

.filtros { display: flex; gap: 8px; align-items: center; margin-bottom: 16px; flex-wrap: wrap; }
.filtros span { color: #94a3b8; font-size: 0.9rem; }
.filtro {
  background: transparent; border: 1px solid #334155; color: #e2e8f0;
  padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85rem;
}
.filtro.ativo { background: #334155; border-color: #60a5fa; }
.filtro:hover { background: #1e293b; }

table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 6px; overflow: hidden; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #334155; }
th { background: #0f172a; color: #60a5fa; position: sticky; top: 0; font-weight: 600; font-size: 0.85rem; }
td.n { text-align: center; font-weight: bold; color: #fbbf24; }
tr:hover { background: #334155; }
code { color: #60a5fa; font-size: 0.85rem; }

.chip {
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  color: white; font-size: 0.7rem; font-weight: bold; margin: 0 2px;
}
""".lstrip()


if __name__ == "__main__":
    p = gerar()
    print(f"Dashboard: {p}")
