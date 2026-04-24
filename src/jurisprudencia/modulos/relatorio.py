#!/usr/bin/env python3
"""Módulo 5: Gera relatório HTML interativo com gráficos e filtros."""

import json
import logging
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import obter_casos, obter_jurisprudencia, estatisticas
from config import BASE_DIR, TABELA_TJMG

logger = logging.getLogger("jurisprudencia")


def formatar_valor_html(valor):
    """Formata valor para exibição HTML."""
    if not valor or valor == 0:
        return "—"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_html(conn, tempo_execucao: float) -> str:
    """Gera HTML completo do relatório."""
    stats = estatisticas(conn)
    casos = obter_casos(conn)
    juris = obter_jurisprudencia(conn)
    juris_com_valor = [j for j in juris if j.get("valor_encontrado") and j["valor_encontrado"] > 0]

    # Dados para gráficos
    por_tribunal = {}
    por_tipo = {}
    valores_lista = []
    for j in juris:
        t = j.get("tribunal", "N/D")
        por_tribunal[t] = por_tribunal.get(t, 0) + 1
        tp = j.get("tipo_pericia_inferido", "outra") or "outra"
        por_tipo[tp] = por_tipo.get(tp, 0) + 1
        if j.get("valor_encontrado") and j["valor_encontrado"] > 0:
            valores_lista.append(j["valor_encontrado"])

    # Faixas de valores
    faixas = {"Até R$1.000": 0, "R$1.000-3.000": 0, "R$3.000-5.000": 0,
              "R$5.000-10.000": 0, "R$10.000+": 0}
    for v in valores_lista:
        if v <= 1000:
            faixas["Até R$1.000"] += 1
        elif v <= 3000:
            faixas["R$1.000-3.000"] += 1
        elif v <= 5000:
            faixas["R$3.000-5.000"] += 1
        elif v <= 10000:
            faixas["R$5.000-10.000"] += 1
        else:
            faixas["R$10.000+"] += 1

    # Casos por custeio
    partes = sum(1 for c in casos if c.get("tipo_custeio") == "PARTES")
    gratuidade = sum(1 for c in casos if c.get("tipo_custeio") == "GRATUIDADE")
    indefinido = sum(1 for c in casos if c.get("tipo_custeio") == "INDEFINIDO")

    # Tabela de jurisprudência (rows HTML)
    juris_rows = ""
    for j in juris[:200]:  # limitar a 200 para performance
        valor_str = formatar_valor_html(j.get("valor_encontrado"))
        ementa_curta = (j.get("ementa", "") or "")[:200]
        if len(j.get("ementa", "")) > 200:
            ementa_curta += "..."
        url = j.get("url", "")
        link_html = f'<a href="{url}" target="_blank">Ver</a>' if url else "—"
        tipo_d = j.get("tipo_decisao", "—")
        tipo_p = (j.get("tipo_pericia_inferido", "—") or "—")

        juris_rows += f"""<tr>
            <td>{j.get('tribunal', '')}</td>
            <td>{j.get('numero', '')}</td>
            <td>{valor_str}</td>
            <td>{tipo_d}</td>
            <td>{tipo_p}</td>
            <td title="{(j.get('ementa', '') or '').replace('"', '&quot;')[:500]}">{ementa_curta}</td>
            <td>{link_html}</td>
        </tr>"""

    # Cards de casos
    casos_cards = ""
    for c in casos:
        custeio_class = "partes" if c.get("tipo_custeio") == "PARTES" else "gratuidade" if c.get("tipo_custeio") == "GRATUIDADE" else "indefinido"
        areas_med = ""
        try:
            areas = json.loads(c.get("areas_medicas", "[]"))
            areas_med = ", ".join(areas) if areas else "N/D"
        except (json.JSONDecodeError, TypeError):
            areas_med = str(c.get("areas_medicas", "N/D"))

        casos_cards += f"""<div class="caso-card {custeio_class}">
            <div class="caso-header">
                <span class="caso-pericia">Perícia {c.get('numero_pericia', '?')}</span>
                <span class="custeio-badge {custeio_class}">{c.get('tipo_custeio', '?')}</span>
            </div>
            <div class="caso-cnj">{c.get('numero_cnj', '')}</div>
            <div class="caso-info">{c.get('vara', '')} — {c.get('cidade', '')}</div>
            <div class="caso-area">{c.get('area', '')}</div>
            <div class="caso-medicas">{areas_med}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Relatório de Jurisprudência e Honorários — Stemmia Forense</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root {{
    --bg: #0f1117;
    --card: #1a1d27;
    --border: #2a2d37;
    --text: #e0e0e0;
    --text-dim: #888;
    --accent: #6c8cff;
    --green: #4ade80;
    --yellow: #fbbf24;
    --red: #f87171;
    --purple: #a78bfa;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
}}
h1 {{ font-size: 1.8em; margin-bottom: 5px; }}
.subtitle {{ color: var(--text-dim); margin-bottom: 25px; }}
.stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 15px;
    margin-bottom: 30px;
}}
.stat-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}}
.stat-valor {{ font-size: 2em; font-weight: 700; color: var(--accent); }}
.stat-label {{ color: var(--text-dim); font-size: 0.85em; margin-top: 5px; }}
.section {{ margin-bottom: 35px; }}
.section-title {{ font-size: 1.3em; margin-bottom: 15px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
.charts-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}}
.chart-container {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    background: var(--card);
    border-radius: 10px;
    overflow: hidden;
}}
th, td {{
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
    font-size: 0.9em;
}}
th {{ background: #22252f; color: var(--accent); font-weight: 600; position: sticky; top: 0; }}
tr:hover {{ background: #22252f; }}
td a {{ color: var(--accent); text-decoration: none; }}
.filtros {{
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
    flex-wrap: wrap;
}}
.filtros select, .filtros input {{
    background: var(--card);
    color: var(--text);
    border: 1px solid var(--border);
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.9em;
}}
.casos-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 12px;
}}
.caso-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 15px;
    border-left: 4px solid var(--border);
}}
.caso-card.partes {{ border-left-color: var(--green); }}
.caso-card.gratuidade {{ border-left-color: var(--yellow); }}
.caso-card.indefinido {{ border-left-color: var(--text-dim); }}
.caso-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
.caso-pericia {{ font-weight: 700; color: var(--accent); }}
.custeio-badge {{
    font-size: 0.75em;
    padding: 2px 8px;
    border-radius: 10px;
    font-weight: 600;
}}
.custeio-badge.partes {{ background: rgba(74,222,128,0.15); color: var(--green); }}
.custeio-badge.gratuidade {{ background: rgba(251,191,36,0.15); color: var(--yellow); }}
.custeio-badge.indefinido {{ background: rgba(136,136,136,0.15); color: var(--text-dim); }}
.caso-cnj {{ font-family: monospace; font-size: 0.85em; color: var(--text-dim); margin-bottom: 5px; }}
.caso-info {{ font-size: 0.9em; }}
.caso-area {{ font-size: 0.85em; color: var(--purple); margin-top: 5px; }}
.caso-medicas {{ font-size: 0.8em; color: var(--text-dim); margin-top: 3px; }}
.table-wrapper {{ max-height: 600px; overflow-y: auto; border-radius: 10px; }}
</style>
</head>
<body>

<h1>Relatório de Jurisprudência e Honorários</h1>
<p class="subtitle">Stemmia Forense — Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} — Tempo: {tempo_execucao:.0f}s</p>

<!-- Stats -->
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-valor">{stats['total_jurisprudencia']}</div>
        <div class="stat-label">Decisões coletadas</div>
    </div>
    <div class="stat-card">
        <div class="stat-valor">{stats['com_valor']}</div>
        <div class="stat-label">Com valor de honorários</div>
    </div>
    <div class="stat-card">
        <div class="stat-valor">{formatar_valor_html(stats['valor_mediana'])}</div>
        <div class="stat-label">Mediana</div>
    </div>
    <div class="stat-card">
        <div class="stat-valor">{formatar_valor_html(stats['valor_media'])}</div>
        <div class="stat-label">Média</div>
    </div>
    <div class="stat-card">
        <div class="stat-valor">{stats['total_casos']}</div>
        <div class="stat-label">Suas perícias</div>
    </div>
    <div class="stat-card">
        <div class="stat-valor">{partes}</div>
        <div class="stat-label">Custeadas pelas partes</div>
    </div>
    <div class="stat-card">
        <div class="stat-valor">{stats['argumentos_gerados']}</div>
        <div class="stat-label">Argumentos gerados</div>
    </div>
    <div class="stat-card">
        <div class="stat-valor">{stats['total_similares']}</div>
        <div class="stat-label">Matches de similaridade</div>
    </div>
</div>

<!-- Gráficos -->
<div class="section">
    <h2 class="section-title">Distribuição de Valores</h2>
    <div class="charts-grid">
        <div class="chart-container">
            <canvas id="chartFaixas"></canvas>
        </div>
        <div class="chart-container">
            <canvas id="chartTribunais"></canvas>
        </div>
    </div>
    <div class="charts-grid">
        <div class="chart-container">
            <canvas id="chartTipos"></canvas>
        </div>
        <div class="chart-container">
            <canvas id="chartCusteio"></canvas>
        </div>
    </div>
</div>

<!-- Tabela de jurisprudência -->
<div class="section">
    <h2 class="section-title">Jurisprudência Coletada ({stats['total_jurisprudencia']} decisões)</h2>
    <div class="filtros">
        <select id="filtroTribunal" onchange="filtrar()">
            <option value="">Todos os tribunais</option>
            {''.join(f'<option value="{t}">{t} ({c})</option>' for t, c in sorted(por_tribunal.items()))}
        </select>
        <select id="filtroTipo" onchange="filtrar()">
            <option value="">Todos os tipos</option>
            {''.join(f'<option value="{t}">{t} ({c})</option>' for t, c in sorted(por_tipo.items()))}
        </select>
        <select id="filtroValor" onchange="filtrar()">
            <option value="">Qualquer valor</option>
            <option value="com">Com valor</option>
            <option value="sem">Sem valor</option>
        </select>
        <input type="text" id="filtroBusca" placeholder="Buscar na ementa..." oninput="filtrar()">
    </div>
    <div class="table-wrapper">
        <table id="tabelaJuris">
            <thead>
                <tr>
                    <th>Tribunal</th>
                    <th>Número</th>
                    <th>Valor</th>
                    <th>Decisão</th>
                    <th>Tipo</th>
                    <th>Ementa</th>
                    <th>Link</th>
                </tr>
            </thead>
            <tbody>{juris_rows}</tbody>
        </table>
    </div>
</div>

<!-- Casos -->
<div class="section">
    <h2 class="section-title">Suas Perícias ({stats['total_casos']} casos — {partes} PARTES / {gratuidade} GRATUIDADE / {indefinido} INDEFINIDO)</h2>
    <div class="casos-grid">{casos_cards}</div>
</div>

<script>
// Gráfico de faixas
new Chart(document.getElementById('chartFaixas'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(list(faixas.keys()))},
        datasets: [{{
            label: 'Decisões por faixa de valor',
            data: {json.dumps(list(faixas.values()))},
            backgroundColor: ['#6c8cff', '#a78bfa', '#4ade80', '#fbbf24', '#f87171'],
            borderRadius: 6,
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
            y: {{ grid: {{ color: '#2a2d37' }}, ticks: {{ color: '#888' }} }},
            x: {{ grid: {{ display: false }}, ticks: {{ color: '#888' }} }}
        }}
    }}
}});

// Gráfico por tribunal
new Chart(document.getElementById('chartTribunais'), {{
    type: 'doughnut',
    data: {{
        labels: {json.dumps(list(por_tribunal.keys()))},
        datasets: [{{
            data: {json.dumps(list(por_tribunal.values()))},
            backgroundColor: ['#6c8cff', '#a78bfa', '#4ade80', '#fbbf24', '#f87171', '#38bdf8'],
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{ legend: {{ position: 'right', labels: {{ color: '#e0e0e0' }} }} }}
    }}
}});

// Gráfico por tipo
new Chart(document.getElementById('chartTipos'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(list(por_tipo.keys()))},
        datasets: [{{
            label: 'Decisões por tipo de perícia',
            data: {json.dumps(list(por_tipo.values()))},
            backgroundColor: '#a78bfa',
            borderRadius: 6,
        }}]
    }},
    options: {{
        responsive: true,
        indexAxis: 'y',
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
            x: {{ grid: {{ color: '#2a2d37' }}, ticks: {{ color: '#888' }} }},
            y: {{ grid: {{ display: false }}, ticks: {{ color: '#888' }} }}
        }}
    }}
}});

// Gráfico de custeio dos casos
new Chart(document.getElementById('chartCusteio'), {{
    type: 'doughnut',
    data: {{
        labels: ['Partes', 'Gratuidade', 'Indefinido'],
        datasets: [{{
            data: [{partes}, {gratuidade}, {indefinido}],
            backgroundColor: ['#4ade80', '#fbbf24', '#888'],
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{ legend: {{ position: 'right', labels: {{ color: '#e0e0e0' }} }} }}
    }}
}});

// Filtros
function filtrar() {{
    const tribunal = document.getElementById('filtroTribunal').value;
    const tipo = document.getElementById('filtroTipo').value;
    const valor = document.getElementById('filtroValor').value;
    const busca = document.getElementById('filtroBusca').value.toLowerCase();
    const rows = document.querySelectorAll('#tabelaJuris tbody tr');

    rows.forEach(row => {{
        const cells = row.cells;
        let show = true;
        if (tribunal && cells[0].textContent !== tribunal) show = false;
        if (tipo && cells[4].textContent !== tipo) show = false;
        if (valor === 'com' && cells[2].textContent === '—') show = false;
        if (valor === 'sem' && cells[2].textContent !== '—') show = false;
        if (busca && !row.textContent.toLowerCase().includes(busca)) show = false;
        row.style.display = show ? '' : 'none';
    }});
}}
</script>

</body>
</html>"""
    return html


def executar_relatorio(conn, tempo_execucao: float) -> str:
    """Gera e salva o relatório HTML."""
    html = gerar_html(conn, tempo_execucao)
    caminho = BASE_DIR / "RELATORIO-JURISPRUDENCIA.html"
    caminho.write_text(html, encoding="utf-8")
    logger.info(f"  Relatório salvo em: {caminho}")
    return str(caminho)
