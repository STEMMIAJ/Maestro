#!/usr/bin/env python3
"""Radar — Gerador de relatórios HTML (diário/semanal/mensal)."""

import json
import os
import sys
from datetime import datetime, timedelta
from collections import Counter
from pathlib import Path

RADAR_DIR = Path.home() / "Desktop" / "Radar"
DADOS_DIR = RADAR_DIR / "dados"

CAT_CORES = {
    "pericia": ("#d35400", "Perícia"),
    "web": ("#8e44ad", "Web/Sites"),
    "automacao": ("#2980b9", "Automação"),
    "config": ("#7f8c8d", "Configuração"),
    "documentacao": ("#27ae60", "Documentação"),
    "outro": ("#95a5a6", "Outros"),
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Radar — {titulo}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #1a1a2e;
    color: #e0e0e0;
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}}
h1 {{
    color: #00d2ff;
    font-size: 28px;
    margin-bottom: 5px;
}}
.subtitulo {{
    color: #888;
    font-size: 14px;
    margin-bottom: 25px;
}}
.stats {{
    display: flex;
    gap: 15px;
    margin-bottom: 25px;
    flex-wrap: wrap;
}}
.stat-card {{
    background: #16213e;
    border-radius: 10px;
    padding: 15px 20px;
    min-width: 120px;
    text-align: center;
    border: 1px solid #2a2a4a;
}}
.stat-num {{
    font-size: 32px;
    font-weight: bold;
    color: #00d2ff;
}}
.stat-label {{
    font-size: 12px;
    color: #888;
    margin-top: 4px;
}}
.categorias {{
    display: flex;
    gap: 10px;
    margin-bottom: 25px;
    flex-wrap: wrap;
}}
.cat-badge {{
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
    color: #fff;
}}
.filtro {{
    margin-bottom: 20px;
}}
.filtro input {{
    width: 100%;
    padding: 10px 15px;
    background: #16213e;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    color: #e0e0e0;
    font-size: 14px;
    outline: none;
}}
.filtro input:focus {{
    border-color: #00d2ff;
}}
.item-card {{
    background: #16213e;
    border-radius: 10px;
    padding: 15px 20px;
    margin-bottom: 10px;
    border-left: 4px solid #2a2a4a;
    transition: border-color 0.2s;
}}
.item-card:hover {{
    border-left-color: #00d2ff;
}}
.item-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}}
.item-nome {{
    font-weight: 600;
    font-size: 15px;
    color: #fff;
}}
.item-hora {{
    font-size: 12px;
    color: #666;
}}
.item-caminho {{
    font-size: 12px;
    color: #555;
    word-break: break-all;
    margin-bottom: 6px;
}}
.item-meta {{
    display: flex;
    gap: 10px;
    align-items: center;
}}
.item-tamanho {{
    font-size: 11px;
    color: #666;
}}
.cat-tag {{
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 10px;
    color: #fff;
}}
.vazio {{
    text-align: center;
    padding: 60px 20px;
    color: #555;
    font-size: 18px;
}}
</style>
</head>
<body>
<h1>Radar — {titulo}</h1>
<p class="subtitulo">Gerado em {gerado_em}</p>

<div class="stats">
    <div class="stat-card">
        <div class="stat-num">{total}</div>
        <div class="stat-label">Arquivos</div>
    </div>
    {stats_categorias}
</div>

<div class="categorias">
    {badges_categorias}
</div>

<div class="filtro">
    <input type="text" id="filtro" placeholder="Filtrar por nome ou caminho..." oninput="filtrar()">
</div>

<div id="lista">
{cards}
</div>

<script>
function filtrar() {{
    const q = document.getElementById('filtro').value.toLowerCase();
    document.querySelectorAll('.item-card').forEach(c => {{
        const texto = c.textContent.toLowerCase();
        c.style.display = texto.includes(q) ? '' : 'none';
    }});
}}
</script>
</body>
</html>"""


def formatar_tamanho(b):
    if b < 1024:
        return f"{b} B"
    elif b < 1024 * 1024:
        return f"{b / 1024:.1f} KB"
    elif b < 1024 * 1024 * 1024:
        return f"{b / (1024*1024):.1f} MB"
    return f"{b / (1024*1024*1024):.1f} GB"


def carregar_snapshots(periodo):
    """Carrega e mescla snapshots do período."""
    todos = []
    vistos = set()

    arquivos_snap = sorted(DADOS_DIR.glob("snapshot-*.json"), reverse=True)
    agora = datetime.now()

    for snap_path in arquivos_snap:
        try:
            nome = snap_path.stem  # snapshot-2026-03-02-14
            partes = nome.replace("snapshot-", "").split("-")
            if len(partes) >= 3:
                data_snap = datetime(int(partes[0]), int(partes[1]), int(partes[2]))
            else:
                continue
        except (ValueError, IndexError):
            continue

        if periodo == "dia" and data_snap.date() != agora.date():
            continue
        elif periodo == "semana" and (agora - data_snap).days > 7:
            continue
        elif periodo == "mes" and (agora - data_snap).days > 31:
            continue

        try:
            with open(snap_path) as f:
                data = json.load(f)
            for arq in data.get("arquivos", []):
                chave = arq.get("caminho", "")
                if chave not in vistos:
                    vistos.add(chave)
                    todos.append(arq)
        except (json.JSONDecodeError, IOError):
            continue

    return todos


def gerar_html(arquivos, titulo, saida_path):
    total = len(arquivos)
    cats = Counter(a.get("categoria", "outro") for a in arquivos)

    # Stats por categoria
    stats_html = ""
    for cat, n in cats.most_common():
        cor, nome = CAT_CORES.get(cat, ("#95a5a6", cat.title()))
        stats_html += f"""    <div class="stat-card">
        <div class="stat-num" style="color:{cor}">{n}</div>
        <div class="stat-label">{nome}</div>
    </div>\n"""

    # Badges
    badges_html = ""
    for cat, n in cats.most_common():
        cor, nome = CAT_CORES.get(cat, ("#95a5a6", cat.title()))
        badges_html += f'    <span class="cat-badge" style="background:{cor}">{nome} ({n})</span>\n'

    # Cards
    arquivos_ord = sorted(arquivos, key=lambda a: a.get("data_modificacao", ""), reverse=True)
    cards_html = ""

    if total == 0:
        cards_html = '<div class="vazio">Nenhum arquivo encontrado no período.</div>'
    else:
        for a in arquivos_ord:
            nome = a.get("nome", "")
            caminho = a.get("caminho", "")
            tamanho = formatar_tamanho(a.get("tamanho", 0))
            cat = a.get("categoria", "outro")
            cor, cat_nome = CAT_CORES.get(cat, ("#95a5a6", "Outro"))

            hora = ""
            dm = a.get("data_modificacao", "")
            if dm:
                try:
                    dt = datetime.strptime(dm, "%Y-%m-%dT%H:%M:%S")
                    hora = dt.strftime("%H:%M — %d/%m")
                except ValueError:
                    hora = dm

            cards_html += f"""<div class="item-card" style="border-left-color:{cor}">
    <div class="item-header">
        <span class="item-nome">{nome}</span>
        <span class="item-hora">{hora}</span>
    </div>
    <div class="item-caminho">{caminho}</div>
    <div class="item-meta">
        <span class="item-tamanho">{tamanho}</span>
        <span class="cat-tag" style="background:{cor}">{cat_nome}</span>
    </div>
</div>\n"""

    html = HTML_TEMPLATE.format(
        titulo=titulo,
        gerado_em=datetime.now().strftime("%d/%m/%Y às %H:%M"),
        total=total,
        stats_categorias=stats_html,
        badges_categorias=badges_html,
        cards=cards_html,
    )

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with open(saida_path, "w", encoding="utf-8") as f:
        f.write(html)

    return saida_path


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "dia"

    agora = datetime.now()

    if modo == "dia":
        titulo = f"Diário — {agora.strftime('%d/%m/%Y')}"
        saida = RADAR_DIR / "diario" / f"{agora.strftime('%Y-%m-%d')}.html"
    elif modo == "semana":
        sem = agora.strftime("%V")
        titulo = f"Semana {sem} — {agora.year}"
        saida = RADAR_DIR / "semanal" / f"Semana-{sem}-{agora.year}.html"
    elif modo == "mes":
        titulo = f"{agora.strftime('%B %Y')}"
        saida = RADAR_DIR / "mensal" / f"{agora.strftime('%Y-%m')}.html"
    else:
        titulo = f"Relatório — {agora.strftime('%d/%m/%Y')}"
        saida = RADAR_DIR / "diario" / f"{agora.strftime('%Y-%m-%d')}.html"
        modo = "dia"

    arquivos = carregar_snapshots(modo)
    caminho = gerar_html(arquivos, titulo, saida)
    print(f"Radar: {len(arquivos)} arquivos → {caminho}")


if __name__ == "__main__":
    main()
