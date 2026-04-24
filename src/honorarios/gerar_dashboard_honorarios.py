#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Dashboard de Honorários Periciais — Stemmia Forense

Lê o banco SQLite ~/Desktop/PESQUISADOR-HONORARIOS/dados/honorarios.db
e gera um HTML interativo estático standalone.

Saída: ~/Desktop/PESQUISADOR-HONORARIOS/MAPA-PESQUISA-HONORARIOS.html
"""

import json
import os
import sqlite3
import statistics
from datetime import datetime
from pathlib import Path


# === CAMINHOS ===
BASE_DIR = Path.home() / "Desktop" / "PESQUISADOR-HONORARIOS"
DB_PATH = BASE_DIR / "dados" / "honorarios.db"
OUTPUT_PATH = BASE_DIR / "MAPA-PESQUISA-HONORARIOS.html"


def fmt_brl(valor):
    """Formata valor numérico como R$ com separador de milhar."""
    if valor is None:
        return "—"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def mediana(valores):
    """Calcula mediana de uma lista de valores."""
    if not valores:
        return 0
    return statistics.median(valores)


def percentil(valores, p):
    """Calcula percentil p (0-100) de uma lista."""
    if not valores:
        return 0
    sorted_v = sorted(valores)
    k = (len(sorted_v) - 1) * (p / 100)
    f = int(k)
    c = f + 1
    if c >= len(sorted_v):
        return sorted_v[f]
    d0 = sorted_v[f] * (c - k)
    d1 = sorted_v[c] * (k - f)
    return d0 + d1


def carregar_dados():
    """Carrega todos os dados do banco SQLite e retorna dicionário com tudo."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # Honorários coletados
    cur = conn.execute("SELECT * FROM honorarios_coletados ORDER BY ano DESC, tribunal, tipo_pericia")
    coletados = [dict(r) for r in cur.fetchall()]

    # Honorários próprios
    cur = conn.execute("SELECT * FROM honorarios_proprios ORDER BY numero_pericia DESC")
    proprios = [dict(r) for r in cur.fetchall()]

    # Tabelas oficiais
    cur = conn.execute("SELECT * FROM tabelas_oficiais ORDER BY vigencia_inicio DESC")
    oficiais = [dict(r) for r in cur.fetchall()]

    conn.close()
    return {
        "coletados": coletados,
        "proprios": proprios,
        "oficiais": oficiais,
    }


def preparar_dados_json(dados):
    """Prepara dados para injeção como JSON no HTML (para filtros JS)."""
    registros = []

    for r in dados["coletados"]:
        registros.append({
            "origem": "coletado",
            "tribunal": r["tribunal"] or "—",
            "tipo_pericia": r["tipo_pericia"] or "—",
            "ano": r["ano"] or 0,
            "valor_proposto": r["valor_proposto"],
            "valor_fixado": r["valor_fixado"],
            "decisao": r["decisao"] or "—",
            "comarca": r["comarca"] or "—",
            "numero_processo": r["numero_processo"] or "—",
            "observacoes": r["observacoes"] or "",
        })

    for r in dados["proprios"]:
        registros.append({
            "origem": "proprio",
            "tribunal": r["tribunal"] or "—",
            "tipo_pericia": r["tipo_pericia"] or "—",
            "ano": 0,
            "valor_proposto": r["valor_proposto"],
            "valor_fixado": r["valor_fixado"],
            "decisao": r["status"] or "—",
            "comarca": r["comarca"] or "—",
            "numero_processo": r["numero_cnj"] or "—",
            "numero_pericia": r["numero_pericia"],
            "areas_medicas": r["areas_medicas"] or "",
            "status": r["status"] or "pendente",
            "num_especialidades": r["num_especialidades"] or 1,
            "observacoes": r["observacoes"] or "",
        })

    return registros


def preparar_oficiais_json(dados):
    """Prepara tabelas oficiais para injeção JSON."""
    result = []
    for r in dados["oficiais"]:
        result.append({
            "fonte": r["fonte"] or "—",
            "tipo": r["tipo"] or "—",
            "valor_base": r["valor_base"],
            "valor_maximo": r["valor_maximo"],
            "vigencia_inicio": r["vigencia_inicio"] or "—",
            "vigencia_fim": r["vigencia_fim"] or "—",
            "normativo": r["normativo"] or "",
            "observacoes": r["observacoes"] or "",
        })
    return result


def escape_html(text):
    """Escapa caracteres HTML para uso seguro em conteúdo."""
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


def gerar_html(dados):
    """Gera o HTML completo do dashboard."""
    registros_json = json.dumps(preparar_dados_json(dados), ensure_ascii=False)
    oficiais_json = json.dumps(preparar_oficiais_json(dados), ensure_ascii=False)

    # Calcular tribunais e tipos únicos para os filtros
    tribunais = sorted(set(
        [r["tribunal"] for r in dados["coletados"] if r["tribunal"]]
        + [r["tribunal"] for r in dados["proprios"] if r["tribunal"]]
    ))
    tipos = sorted(set(
        [r["tipo_pericia"] for r in dados["coletados"] if r["tipo_pericia"]]
        + [r["tipo_pericia"] for r in dados["proprios"] if r["tipo_pericia"]]
    ))
    anos = sorted(set(
        [r["ano"] for r in dados["coletados"] if r["ano"]]
    ))

    tribunais_options = "\n".join(
        f'<option value="{escape_html(t)}">{escape_html(t)}</option>' for t in tribunais
    )
    tipos_options = "\n".join(
        f'<option value="{escape_html(t)}">{escape_html(t)}</option>' for t in tipos
    )
    anos_options = "\n".join(
        f'<option value="{a}">{a}</option>' for a in anos
    )

    total_registros = len(dados["coletados"]) + len(dados["proprios"])
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")

    # Gerar linhas dos processos próprios para a tabela estática
    proprios_rows = ""
    for r in dados["proprios"]:
        status = r["status"] or "pendente"
        status_class = "green" if status == "aceito" else ("yellow" if status == "pendente" else "red")
        valor = fmt_brl(r["valor_fixado"]) if r["valor_fixado"] else fmt_brl(r["valor_proposto"])
        proprios_rows += (
            "<tr>"
            f"<td>{escape_html(r['numero_pericia']) if r['numero_pericia'] else '—'}</td>"
            f"<td>{escape_html(r['comarca']) if r['comarca'] else '—'}</td>"
            f'<td class="tipo-cell">{escape_html(r["tipo_pericia"]) if r["tipo_pericia"] else "—"}</td>'
            f"<td>{escape_html(valor)}</td>"
            f'<td><span class="badge badge-{status_class}">{escape_html(status)}</span></td>'
            "</tr>\n"
        )

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard de Honorários — Stemmia Forense</title>
<style>
  :root {{
    --bg: #f8fafc;
    --sidebar-bg: #1e293b;
    --sidebar-text: #94a3b8;
    --sidebar-active: #3b82f6;
    --card-bg: #ffffff;
    --text: #334155;
    --text-light: #64748b;
    --green: #22c55e;
    --yellow: #eab308;
    --red: #ef4444;
    --blue: #3b82f6;
    --border: #e2e8f0;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--text);
    display: flex;
    min-height: 100vh;
    font-size: 14px;
    line-height: 1.6;
  }}

  /* SIDEBAR */
  nav {{
    width: 280px;
    background: var(--sidebar-bg);
    color: #e2e8f0;
    padding: 20px 0;
    position: fixed;
    height: 100vh;
    overflow-y: auto;
    z-index: 100;
    flex-shrink: 0;
  }}
  nav .brand {{
    padding: 0 20px 8px;
    border-bottom: 1px solid #334155;
    margin-bottom: 10px;
  }}
  nav .brand h1 {{
    font-size: 15px;
    color: #fff;
    font-weight: 700;
    letter-spacing: 0.3px;
  }}
  nav .brand .sub {{
    font-size: 11px;
    color: var(--sidebar-text);
    margin-top: 2px;
  }}
  nav h2 {{
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--sidebar-text);
    padding: 18px 20px 5px;
  }}
  nav a {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 20px;
    color: #cbd5e1;
    text-decoration: none;
    font-size: 13px;
    transition: background 0.15s, color 0.15s;
    border-left: 3px solid transparent;
  }}
  nav a:hover {{
    background: #334155;
    color: #fff;
  }}
  nav a.active {{
    background: rgba(59, 130, 246, 0.1);
    color: #fff;
    border-left-color: var(--sidebar-active);
  }}
  nav a .icon {{
    width: 18px;
    text-align: center;
    font-size: 14px;
    flex-shrink: 0;
  }}

  /* MAIN */
  main {{
    margin-left: 280px;
    padding: 30px 40px 60px;
    max-width: 1180px;
    width: 100%;
  }}
  h1.page-title {{
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 4px;
  }}
  .subtitle {{
    color: var(--text-light);
    margin-bottom: 25px;
    font-size: 13px;
  }}

  /* FILTROS */
  .filtros {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 30px;
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    align-items: end;
  }}
  .filtro-group {{
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
    min-width: 180px;
  }}
  .filtro-group label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-light);
  }}
  .filtro-group select {{
    padding: 8px 12px;
    border: 1px solid var(--border);
    border-radius: 8px;
    font-size: 13px;
    font-family: inherit;
    color: var(--text);
    background: #fff;
    cursor: pointer;
    appearance: auto;
  }}
  .filtro-group select:focus {{
    outline: none;
    border-color: var(--blue);
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12);
  }}
  .btn-limpar {{
    padding: 8px 18px;
    background: var(--blue);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-family: inherit;
    cursor: pointer;
    font-weight: 600;
    transition: background 0.15s;
    align-self: end;
  }}
  .btn-limpar:hover {{ background: #2563eb; }}

  /* SECTION */
  section {{
    margin-bottom: 35px;
    scroll-margin-top: 20px;
  }}
  section > h2 {{
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  section > h2 .section-icon {{
    font-size: 20px;
  }}

  /* RESUMO CARDS */
  .resumo {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 10px;
  }}
  .resumo-card {{
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px 20px;
    border: 1px solid var(--border);
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s;
  }}
  .resumo-card:hover {{
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  }}
  .resumo-card .num {{
    font-size: 36px;
    font-weight: 800;
    line-height: 1.1;
  }}
  .resumo-card .label {{
    font-size: 11px;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 6px;
  }}
  .resumo-card.blue .num {{ color: var(--blue); }}
  .resumo-card.green .num {{ color: var(--green); }}

  /* CARD GENÉRICO */
  .card {{
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px;
    border: 1px solid var(--border);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    margin-bottom: 16px;
    overflow-x: auto;
  }}
  .card h3 {{
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 12px;
    color: var(--text);
  }}

  /* TABELAS */
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }}
  thead th {{
    text-align: left;
    padding: 10px 12px;
    background: #f1f5f9;
    border-bottom: 2px solid var(--border);
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-light);
    white-space: nowrap;
  }}
  tbody td {{
    padding: 10px 12px;
    border-bottom: 1px solid var(--border);
    vertical-align: middle;
  }}
  tbody tr:nth-child(even) {{
    background: #f8fafc;
  }}
  tbody tr:hover {{
    background: #eef2ff;
  }}
  .tipo-cell {{
    max-width: 280px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}
  td.num {{
    text-align: right;
    font-variant-numeric: tabular-nums;
    font-weight: 500;
  }}

  /* BARRAS PROPORCIONAIS */
  .bar-container {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .bar {{
    height: 8px;
    border-radius: 4px;
    background: var(--blue);
    transition: width 0.4s ease;
    min-width: 2px;
  }}
  .bar.bar-green {{ background: var(--green); }}
  .bar.bar-yellow {{ background: var(--yellow); }}
  .bar.bar-red {{ background: var(--red); }}

  /* BADGES */
  .badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    white-space: nowrap;
  }}
  .badge-green {{ background: #dcfce7; color: #166534; }}
  .badge-yellow {{ background: #fef9c3; color: #854d0e; }}
  .badge-red {{ background: #fee2e2; color: #991b1b; }}
  .badge-blue {{ background: #dbeafe; color: #1e40af; }}
  .badge-gray {{ background: #f1f5f9; color: #475569; }}

  /* SEMÁFORO (Faixas Seguras) */
  .semaforo-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
  }}
  .semaforo-card {{
    background: var(--card-bg);
    border-radius: 12px;
    border: 1px solid var(--border);
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }}
  .semaforo-card h4 {{
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 14px;
    color: var(--text);
    line-height: 1.3;
  }}
  .faixa {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 0;
    font-size: 13px;
  }}
  .faixa .indicador {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
  }}
  .faixa .indicador.verde {{ background: var(--green); }}
  .faixa .indicador.amarelo {{ background: var(--yellow); }}
  .faixa .indicador.vermelho {{ background: var(--red); }}
  .faixa .faixa-label {{
    font-weight: 600;
    min-width: 80px;
    flex-shrink: 0;
  }}
  .faixa .faixa-valor {{
    color: var(--text-light);
    font-variant-numeric: tabular-nums;
  }}

  /* OFICIAIS */
  .oficiais-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 16px;
  }}
  .oficial-card {{
    background: var(--card-bg);
    border-radius: 12px;
    border: 1px solid var(--border);
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    position: relative;
    overflow: hidden;
  }}
  .oficial-card.revogada {{
    opacity: 0.55;
  }}
  .oficial-card .vigencia-bar {{
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--green);
  }}
  .oficial-card.revogada .vigencia-bar {{
    background: var(--red);
  }}
  .oficial-card h4 {{
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 10px;
    padding-right: 80px;
  }}
  .oficial-card .badge-vigencia {{
    position: absolute;
    top: 14px;
    right: 16px;
  }}
  .oficial-card .info-row {{
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    font-size: 13px;
  }}
  .oficial-card .info-row .info-label {{
    color: var(--text-light);
  }}
  .oficial-card .info-row .info-value {{
    font-weight: 600;
  }}
  .oficial-card .obs {{
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid var(--border);
    font-size: 12px;
    color: var(--text-light);
    font-style: italic;
  }}

  /* FOOTER */
  footer {{
    margin-top: 40px;
    padding: 20px 0;
    border-top: 1px solid var(--border);
    text-align: center;
    font-size: 12px;
    color: var(--text-light);
  }}
  footer strong {{
    color: var(--text);
  }}

  /* EMPTY STATE */
  .empty {{
    text-align: center;
    padding: 40px 20px;
    color: var(--text-light);
    font-size: 14px;
  }}

  /* RESPONSIVE */
  @media (max-width: 1024px) {{
    nav {{ width: 240px; }}
    main {{ margin-left: 240px; padding: 20px 24px 40px; }}
    .resumo {{ grid-template-columns: repeat(3, 1fr); }}
  }}
  @media (max-width: 768px) {{
    nav {{
      width: 100%;
      height: auto;
      position: relative;
      padding: 12px 0;
    }}
    nav .brand {{ padding: 0 16px 8px; }}
    nav a {{ display: inline-flex; padding: 6px 12px; font-size: 12px; }}
    nav h2 {{ display: none; }}
    main {{ margin-left: 0; padding: 16px; max-width: 100%; }}
    body {{ flex-direction: column; }}
    .resumo {{ grid-template-columns: 1fr; }}
    .filtros {{ flex-direction: column; }}
    .semaforo-grid {{ grid-template-columns: 1fr; }}
    .oficiais-grid {{ grid-template-columns: 1fr; }}
  }}

  /* PRINT */
  @media print {{
    nav {{ display: none; }}
    main {{ margin-left: 0; max-width: 100%; padding: 10px; }}
    .filtros {{ display: none; }}
    .card, .resumo-card, .semaforo-card, .oficial-card {{
      break-inside: avoid;
      box-shadow: none;
      border: 1px solid #ddd;
    }}
    body {{ font-size: 11px; }}
  }}
</style>
</head>
<body>

<!-- SIDEBAR -->
<nav>
  <div class="brand">
    <h1>Pesquisador de Honorários</h1>
    <div class="sub">Stemmia Forense</div>
  </div>
  <h2>Navegação</h2>
  <a href="#resumo" class="active"><span class="icon">&#x1F4CA;</span> Resumo Geral</a>
  <a href="#por-tipo"><span class="icon">&#x1F52C;</span> Por Tipo de Perícia</a>
  <a href="#por-tribunal"><span class="icon">&#x2696;</span> Por Tribunal</a>
  <a href="#meus-processos"><span class="icon">&#x1F4C1;</span> Meus Processos</a>
  <a href="#tabelas-oficiais"><span class="icon">&#x1F4CB;</span> Tabelas Oficiais</a>
  <a href="#faixas-seguras"><span class="icon">&#x1F6A6;</span> Faixas Seguras</a>
</nav>

<!-- MAIN -->
<main>
  <h1 class="page-title">Dashboard de Honorários Periciais</h1>
  <p class="subtitle">Gerado em {agora} — {total_registros} registros no banco</p>

  <!-- FILTROS -->
  <div class="filtros">
    <div class="filtro-group">
      <label>Tribunal</label>
      <select id="filtro-tribunal" onchange="aplicarFiltros()">
        <option value="">Todos</option>
        {tribunais_options}
      </select>
    </div>
    <div class="filtro-group">
      <label>Tipo de perícia</label>
      <select id="filtro-tipo" onchange="aplicarFiltros()">
        <option value="">Todos</option>
        {tipos_options}
      </select>
    </div>
    <div class="filtro-group">
      <label>Ano</label>
      <select id="filtro-ano" onchange="aplicarFiltros()">
        <option value="">Todos</option>
        {anos_options}
      </select>
    </div>
    <button class="btn-limpar" onclick="limparFiltros()">Limpar filtros</button>
  </div>

  <!-- RESUMO GERAL -->
  <section id="resumo">
    <h2><span class="section-icon">&#x1F4CA;</span> Resumo Geral</h2>
    <div class="resumo">
      <div class="resumo-card blue">
        <div class="num" id="stat-total">{total_registros}</div>
        <div class="label">Total de registros</div>
      </div>
      <div class="resumo-card green">
        <div class="num" id="stat-media">—</div>
        <div class="label">Média dos fixados</div>
      </div>
      <div class="resumo-card">
        <div class="num" id="stat-mediana">—</div>
        <div class="label">Mediana dos fixados</div>
      </div>
    </div>
  </section>

  <!-- POR TIPO DE PERÍCIA -->
  <section id="por-tipo">
    <h2><span class="section-icon">&#x1F52C;</span> Distribuição por Tipo de Perícia</h2>
    <div class="card">
      <div id="tabela-tipo-container">
        <table>
          <thead>
            <tr>
              <th>Tipo de perícia</th>
              <th>Qtd</th>
              <th>Mín</th>
              <th>Média</th>
              <th>Mediana</th>
              <th>Máx</th>
              <th style="width:25%">Distribuição</th>
            </tr>
          </thead>
          <tbody id="tbody-tipo"></tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- POR TRIBUNAL -->
  <section id="por-tribunal">
    <h2><span class="section-icon">&#x2696;</span> Distribuição por Tribunal</h2>
    <div class="card">
      <div id="tabela-tribunal-container">
        <table>
          <thead>
            <tr>
              <th>Tribunal</th>
              <th>Qtd</th>
              <th>Mín</th>
              <th>Média</th>
              <th>Mediana</th>
              <th>Máx</th>
              <th style="width:25%">Distribuição</th>
            </tr>
          </thead>
          <tbody id="tbody-tribunal"></tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- MEUS PROCESSOS -->
  <section id="meus-processos">
    <h2><span class="section-icon">&#x1F4C1;</span> Meus Processos</h2>
    <div class="card">
      <table>
        <thead>
          <tr>
            <th># Perícia</th>
            <th>Comarca</th>
            <th>Tipo</th>
            <th>Valor</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody id="tbody-proprios">
          {proprios_rows}
        </tbody>
      </table>
    </div>
  </section>

  <!-- TABELAS OFICIAIS -->
  <section id="tabelas-oficiais">
    <h2><span class="section-icon">&#x1F4CB;</span> Tabelas Oficiais Vigentes</h2>
    <div class="oficiais-grid" id="oficiais-grid"></div>
  </section>

  <!-- FAIXAS SEGURAS -->
  <section id="faixas-seguras">
    <h2><span class="section-icon">&#x1F6A6;</span> Faixas Seguras (Semáforo)</h2>
    <p style="color:var(--text-light);font-size:13px;margin-bottom:16px;">
      Calculadas com base nos valores fixados: verde até mediana, amarelo até percentil 75, vermelho acima.
    </p>
    <div class="semaforo-grid" id="semaforo-grid"></div>
  </section>

  <!-- FOOTER -->
  <footer>
    Gerado em <strong>{agora}</strong> &mdash;
    {total_registros} registros &mdash;
    <strong>Stemmia Forense</strong>
  </footer>
</main>

<script>
(function() {{
  "use strict";

  // === DADOS INJETADOS ===
  var REGISTROS = {registros_json};
  var OFICIAIS = {oficiais_json};

  // === UTILIDADES ===
  function fmtBRL(v) {{
    if (v === null || v === undefined || isNaN(v)) return "\u2014";
    return "R$\u00a0" + v.toLocaleString("pt-BR", {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
  }}

  function calcMedia(arr) {{
    if (!arr.length) return 0;
    return arr.reduce(function(a, b) {{ return a + b; }}, 0) / arr.length;
  }}

  function calcMediana(arr) {{
    if (!arr.length) return 0;
    var sorted = arr.slice().sort(function(a, b) {{ return a - b; }});
    var mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
  }}

  function calcPercentil(arr, p) {{
    if (!arr.length) return 0;
    var sorted = arr.slice().sort(function(a, b) {{ return a - b; }});
    var k = (sorted.length - 1) * (p / 100);
    var f = Math.floor(k);
    var c = f + 1;
    if (c >= sorted.length) return sorted[f];
    return sorted[f] * (c - k) + sorted[c] * (k - f);
  }}

  function escapeText(str) {{
    if (!str) return "";
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(str));
    return div.textContent;
  }}

  function agrupar(registros, campo) {{
    var grupos = {{}};
    registros.forEach(function(r) {{
      var chave = r[campo] || "\u2014";
      if (!grupos[chave]) grupos[chave] = [];
      grupos[chave].push(r);
    }});
    return grupos;
  }}

  // === CRIAÇÃO SEGURA DE ELEMENTOS ===
  function criarCelula(texto, classes) {{
    var td = document.createElement("td");
    if (classes) td.className = classes;
    td.textContent = texto;
    return td;
  }}

  function criarCelulaBar(widthPct) {{
    var td = document.createElement("td");
    var container = document.createElement("div");
    container.className = "bar-container";
    var bar = document.createElement("div");
    bar.className = "bar";
    bar.style.width = widthPct + "%";
    container.appendChild(bar);
    td.appendChild(container);
    return td;
  }}

  // === FILTROS ===
  function getFiltros() {{
    return {{
      tribunal: document.getElementById("filtro-tribunal").value,
      tipo: document.getElementById("filtro-tipo").value,
      ano: document.getElementById("filtro-ano").value
    }};
  }}

  function filtrar(registros) {{
    var f = getFiltros();
    return registros.filter(function(r) {{
      if (f.tribunal && r.tribunal !== f.tribunal) return false;
      if (f.tipo && r.tipo_pericia !== f.tipo) return false;
      if (f.ano && r.ano !== parseInt(f.ano) && r.ano !== 0) return false;
      return true;
    }});
  }}

  window.limparFiltros = function() {{
    document.getElementById("filtro-tribunal").value = "";
    document.getElementById("filtro-tipo").value = "";
    document.getElementById("filtro-ano").value = "";
    aplicarFiltros();
  }};

  // === RENDERIZAÇÃO ===
  function renderResumo(dados) {{
    var fixados = [];
    dados.forEach(function(r) {{
      if (r.valor_fixado) fixados.push(r.valor_fixado);
    }});
    document.getElementById("stat-total").textContent = dados.length;
    document.getElementById("stat-media").textContent = fixados.length ? fmtBRL(calcMedia(fixados)) : "\u2014";
    document.getElementById("stat-mediana").textContent = fixados.length ? fmtBRL(calcMediana(fixados)) : "\u2014";
  }}

  function renderTabelaAgrupada(dados, campo, tbodyId) {{
    var grupos = agrupar(dados, campo);
    var tbody = document.getElementById(tbodyId);
    while (tbody.firstChild) tbody.removeChild(tbody.firstChild);

    // Encontrar max para barras proporcionais
    var globalMax = 0;
    Object.keys(grupos).forEach(function(chave) {{
      var fixados = [];
      grupos[chave].forEach(function(r) {{
        if (r.valor_fixado) fixados.push(r.valor_fixado);
      }});
      if (fixados.length) {{
        var m = Math.max.apply(null, fixados);
        if (m > globalMax) globalMax = m;
      }}
    }});

    // Ordenar por quantidade decrescente
    var chaves = Object.keys(grupos).sort(function(a, b) {{
      return grupos[b].length - grupos[a].length;
    }});

    if (!chaves.length) {{
      var tr = document.createElement("tr");
      var td = document.createElement("td");
      td.colSpan = 7;
      td.className = "empty";
      td.textContent = "Nenhum registro encontrado com os filtros atuais.";
      tr.appendChild(td);
      tbody.appendChild(tr);
      return;
    }}

    chaves.forEach(function(chave) {{
      var arr = grupos[chave];
      var fixados = [];
      arr.forEach(function(r) {{
        if (r.valor_fixado) fixados.push(r.valor_fixado);
      }});
      var minVal = fixados.length ? Math.min.apply(null, fixados) : 0;
      var maxVal = fixados.length ? Math.max.apply(null, fixados) : 0;
      var media = fixados.length ? calcMedia(fixados) : 0;
      var med = fixados.length ? calcMediana(fixados) : 0;
      var barWidth = globalMax > 0 ? Math.max(2, (maxVal / globalMax) * 100) : 0;

      var tr = document.createElement("tr");
      tr.appendChild(criarCelula(chave, "tipo-cell"));
      tr.appendChild(criarCelula(arr.length, "num"));
      tr.appendChild(criarCelula(fixados.length ? fmtBRL(minVal) : "\u2014", "num"));
      tr.appendChild(criarCelula(fixados.length ? fmtBRL(media) : "\u2014", "num"));
      tr.appendChild(criarCelula(fixados.length ? fmtBRL(med) : "\u2014", "num"));
      tr.appendChild(criarCelula(fixados.length ? fmtBRL(maxVal) : "\u2014", "num"));
      tr.appendChild(criarCelulaBar(barWidth));
      tbody.appendChild(tr);
    }});
  }}

  function renderOficiais() {{
    var grid = document.getElementById("oficiais-grid");
    while (grid.firstChild) grid.removeChild(grid.firstChild);

    if (!OFICIAIS.length) {{
      var empty = document.createElement("div");
      empty.className = "empty";
      empty.textContent = "Nenhuma tabela oficial cadastrada.";
      grid.appendChild(empty);
      return;
    }}

    OFICIAIS.forEach(function(o) {{
      var vigente = o.vigencia_fim === "atual" || o.vigencia_fim === "\u2014" || !o.vigencia_fim;
      var card = document.createElement("div");
      card.className = "oficial-card" + (vigente ? "" : " revogada");

      var vigBar = document.createElement("div");
      vigBar.className = "vigencia-bar";
      card.appendChild(vigBar);

      var badgeVig = document.createElement("span");
      badgeVig.className = "badge " + (vigente ? "badge-green" : "badge-red") + " badge-vigencia";
      badgeVig.textContent = vigente ? "Vigente" : "Revogada";
      card.appendChild(badgeVig);

      var h4 = document.createElement("h4");
      h4.textContent = o.fonte;
      card.appendChild(h4);

      var campos = [
        ["Tipo", o.tipo],
        ["Valor base", fmtBRL(o.valor_base)],
        ["Valor máximo", fmtBRL(o.valor_maximo)],
        ["Vigência", o.vigencia_inicio + " \u2014 " + (o.vigencia_fim || "atual")]
      ];
      campos.forEach(function(c) {{
        var row = document.createElement("div");
        row.className = "info-row";
        var lbl = document.createElement("span");
        lbl.className = "info-label";
        lbl.textContent = c[0];
        var val = document.createElement("span");
        val.className = "info-value";
        val.textContent = c[1];
        row.appendChild(lbl);
        row.appendChild(val);
        card.appendChild(row);
      }});

      if (o.observacoes) {{
        var obs = document.createElement("div");
        obs.className = "obs";
        obs.textContent = o.observacoes;
        card.appendChild(obs);
      }}

      grid.appendChild(card);
    }});
  }}

  function renderSemaforo(dados) {{
    var grid = document.getElementById("semaforo-grid");
    while (grid.firstChild) grid.removeChild(grid.firstChild);

    var grupos = agrupar(dados, "tipo_pericia");
    var chaves = Object.keys(grupos).sort();

    if (!chaves.length) {{
      var empty = document.createElement("div");
      empty.className = "empty";
      empty.textContent = "Nenhum dado disponível para calcular faixas.";
      grid.appendChild(empty);
      return;
    }}

    chaves.forEach(function(tipo) {{
      var arr = grupos[tipo];
      var fixados = [];
      arr.forEach(function(r) {{
        if (r.valor_fixado) fixados.push(r.valor_fixado);
      }});
      if (!fixados.length) return;

      var med = calcMediana(fixados);
      var p75 = calcPercentil(fixados, 75);

      var card = document.createElement("div");
      card.className = "semaforo-card";

      var h4 = document.createElement("h4");
      h4.textContent = tipo;
      card.appendChild(h4);

      var faixas = [
        ["verde", "Segura", "até " + fmtBRL(med)],
        ["amarelo", "Atenção", fmtBRL(med) + " \u2014 " + fmtBRL(p75)],
        ["vermelho", "Risco", "acima de " + fmtBRL(p75)]
      ];
      faixas.forEach(function(f) {{
        var row = document.createElement("div");
        row.className = "faixa";
        var ind = document.createElement("div");
        ind.className = "indicador " + f[0];
        var lbl = document.createElement("span");
        lbl.className = "faixa-label";
        lbl.textContent = f[1];
        var val = document.createElement("span");
        val.className = "faixa-valor";
        val.textContent = f[2];
        row.appendChild(ind);
        row.appendChild(lbl);
        row.appendChild(val);
        card.appendChild(row);
      }});

      grid.appendChild(card);
    }});
  }}

  // === APLICAR FILTROS ===
  window.aplicarFiltros = function() {{
    var dados = filtrar(REGISTROS);
    renderResumo(dados);
    renderTabelaAgrupada(dados, "tipo_pericia", "tbody-tipo");
    renderTabelaAgrupada(dados, "tribunal", "tbody-tribunal");
    renderSemaforo(dados);
  }};

  // === SCROLL HIGHLIGHT ===
  function setupScrollHighlight() {{
    var links = document.querySelectorAll("nav a[href^='#']");
    var sections = [];
    links.forEach(function(a) {{
      var id = a.getAttribute("href").substring(1);
      var el = document.getElementById(id);
      if (el) sections.push({{ link: a, el: el }});
    }});

    window.addEventListener("scroll", function() {{
      var current = sections[0];
      sections.forEach(function(s) {{
        if (s.el.getBoundingClientRect().top <= 100) current = s;
      }});
      links.forEach(function(a) {{ a.classList.remove("active"); }});
      if (current) current.link.classList.add("active");
    }});
  }}

  // === INIT ===
  document.addEventListener("DOMContentLoaded", function() {{
    aplicarFiltros();
    renderOficiais();
    setupScrollHighlight();
  }});
}})();
</script>
</body>
</html>"""

    return html


def main():
    """Função principal: lê banco, gera HTML, salva arquivo."""
    if not DB_PATH.exists():
        print(f"ERRO: Banco de dados não encontrado em {DB_PATH}")
        return

    print(f"Lendo banco de dados: {DB_PATH}")
    dados = carregar_dados()

    print(f"  - {len(dados['coletados'])} honorários coletados")
    print(f"  - {len(dados['proprios'])} honorários próprios")
    print(f"  - {len(dados['oficiais'])} tabelas oficiais")

    print("Gerando HTML...")
    html = gerar_html(dados)

    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard salvo em: {OUTPUT_PATH}")
    print(f"Tamanho: {len(html):,} bytes")


if __name__ == "__main__":
    main()
