"""Dashboard HTML para visualização de oportunidades."""

import http.server
import re
import threading
import webbrowser
from urllib.parse import parse_qs, urlparse

from config import DASHBOARD_PORT
from db import get_oportunidades, get_estatisticas, marcar_contatado, ignorar_oportunidade


CATEGORIAS_LABEL = {
    "escassez_direta": "Escassez Direta",
    "dificuldade_nomeacao": "Dificuldade de Nomeação",
    "mutirao": "Mutirão",
    "perito_fora_comarca": "Perito Fora da Comarca",
    "cadastro_aberto": "Cadastro Aberto",
}

CATEGORIAS_COR = {
    "escassez_direta": "#e74c3c",
    "dificuldade_nomeacao": "#e67e22",
    "mutirao": "#f39c12",
    "perito_fora_comarca": "#3498db",
    "cadastro_aberto": "#27ae60",
}

ESTADOS_DIARIO = {
    "DJMG": "MG", "DJSP": "SP", "DJRJ": "RJ", "DJBA": "BA", "DJGO": "GO",
    "DJPR": "PR", "DJSC": "SC", "DJRS": "RS", "DJCE": "CE", "DJMT": "MT",
    "DJMS": "MS", "DJES": "ES", "DOECE": "CE", "DOETO": "TO",
}


def _extrair_ano(titulo):
    m = re.search(r'\d{2}/\d{2}/(\d{4})', titulo or '')
    return m.group(1) if m else ""


def _extrair_estado(titulo, estado_db):
    if estado_db:
        return estado_db
    for sigla, uf in ESTADOS_DIARIO.items():
        if (titulo or '').startswith(sigla):
            return uf
    m = re.search(r'TJ([A-Z]{2})', titulo or '')
    if m:
        return m.group(1)
    if "Minas Gerais" in (titulo or ''):
        return "MG"
    if "AL-MG" in (titulo or ''):
        return "MG"
    return ""


def _extrair_comarca_titulo(titulo):
    """Tenta extrair comarca do formato 'DJMG DD/MM/YYYY - Pág. X - Comarca - ...'"""
    m = re.search(r'DJ\w+\s+\d{2}/\d{2}/\d{4}\s+-\s+Pág\.\s*\d+\s+-\s+(.+?)\s+-\s+', titulo or '')
    if m:
        candidato = m.group(1).strip()
        skip = {"Administrativo", "Judiciário", "Judicial", "Caderno", "Edição Extra",
                "CADERNO", "SUPLEMENTO", "Seção", "SECAO"}
        for s in skip:
            if candidato.startswith(s) or candidato.startswith(s.upper()):
                return ""
        return candidato
    return ""


def gerar_html():
    stats = get_estatisticas()
    oportunidades = get_oportunidades(recentes=False)  # Pegar todos, filtrar no JS

    estados_set = set()
    anos_set = set()

    cards_html = ""
    for op in oportunidades:
        cat = op.get("categoria", "")
        cor = CATEGORIAS_COR.get(cat, "#95a5a6")
        label = CATEGORIAS_LABEL.get(cat, cat)
        contatado = "contatado" if op.get("contatado") else ""

        trecho = (op.get("trecho", "") or "")[:300]
        if len(op.get("trecho", "") or "") > 300:
            trecho += "..."

        titulo = op.get("titulo", "Sem titulo")
        estado = _extrair_estado(titulo, op.get("estado", ""))
        ano = _extrair_ano(titulo)
        comarca = op.get("comarca", "") or _extrair_comarca_titulo(titulo)

        if estado:
            estados_set.add(estado)
        if ano:
            anos_set.add(ano)

        cards_html += f"""
        <div class="card {contatado}" data-cat="{cat}" data-estado="{estado}" data-ano="{ano}">
            <div class="card-header">
                <span class="tag" style="background:{cor}">{label}</span>
                <span class="fonte">{op.get('fonte', '')}</span>
                {'<span class="tag-estado">' + estado + '</span>' if estado else ''}
            </div>
            <h3 class="card-title">
                <a href="{op.get('url', '#')}" target="_blank">
                    {titulo[:120]}
                </a>
            </h3>
            <div class="card-meta">
                {'<span class="comarca">📍 ' + comarca + '</span>' if comarca else ''}
                {'<span class="vara">' + op.get('vara', '') + '</span>' if op.get('vara') else ''}
                {'<span class="tribunal">' + op.get('tribunal', '') + '</span>' if op.get('tribunal') else ''}
            </div>
            <p class="trecho">{trecho}</p>
            <div class="card-actions">
                <a href="/contatado?id={op['id']}" class="btn btn-ok">Contatado</a>
                <a href="/ignorar?id={op['id']}" class="btn btn-skip">Ignorar</a>
                <span class="data-visto">{(op.get('data_titulo', '') or (op.get('primeiro_visto', '') or '')[:10])}</span>
            </div>
        </div>
        """

    # Botões de estado
    estados_sorted = sorted(estados_set)
    estados_btns = '<button class="filter-btn" onclick="filtrarEstado(\'todos\')">Todos UF</button>'
    for uf in estados_sorted:
        active = ' active' if uf == 'MG' else ''
        estados_btns += f'<button class="filter-btn{active}" onclick="filtrarEstado(\'{uf}\')">{uf}</button>'

    # Botões de ano
    anos_sorted = sorted(anos_set, reverse=True)
    anos_btns = '<button class="filter-btn" onclick="filtrarAno(\'todos\')">Todos</button>'
    for a in anos_sorted:
        active = ' active' if a == '2025' else ''
        anos_btns += f'<button class="filter-btn{active}" onclick="filtrarAno(\'{a}\')">{a}+</button>'

    # Stats por categoria
    cats_html = ""
    for cat, qtd in stats.get("por_categoria", {}).items():
        cor = CATEGORIAS_COR.get(cat, "#95a5a6")
        label_cat = CATEGORIAS_LABEL.get(cat, cat)
        cats_html += f'<span class="stat-cat" style="border-left:4px solid {cor}">{label_cat}: <b>{qtd}</b></span>'

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Oportunidades para Perito - MG</title>
<style>
:root {{
    --bg: #0f1117;
    --surface: #1a1d27;
    --border: #2a2d3a;
    --text: #e0e0e0;
    --text-dim: #8b8fa3;
    --accent: #6c5ce7;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
}}
.header {{
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 20px 30px;
}}
.header h1 {{ font-size: 1.4em; margin-bottom: 15px; }}
.stats {{
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    margin-bottom: 10px;
}}
.stat {{
    background: var(--bg);
    padding: 10px 18px;
    border-radius: 8px;
    font-size: 0.9em;
}}
.stat b {{ color: var(--accent); font-size: 1.3em; }}
.stats-cats {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 10px;
}}
.stat-cat {{
    padding: 5px 12px;
    background: var(--bg);
    border-radius: 4px;
    font-size: 0.85em;
}}
.filter-row {{
    padding: 8px 30px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
}}
.filter-row:first-of-type {{ padding-top: 15px; }}
.filter-label {{
    font-size: 0.8em;
    color: var(--text-dim);
    margin-right: 4px;
    min-width: 70px;
}}
.filter-btn {{
    padding: 6px 14px;
    border: 1px solid var(--border);
    border-radius: 20px;
    background: transparent;
    color: var(--text-dim);
    cursor: pointer;
    font-size: 0.85em;
    transition: all 0.2s;
}}
.filter-btn:hover, .filter-btn.active {{
    background: var(--accent);
    color: white;
    border-color: var(--accent);
}}
.counter {{
    padding: 10px 30px;
    font-size: 0.85em;
    color: var(--text-dim);
}}
.container {{
    padding: 20px 30px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 15px;
}}
.card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px;
    transition: transform 0.2s;
}}
.card:hover {{ transform: translateY(-2px); }}
.card.contatado {{ opacity: 0.5; }}
.card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    gap: 8px;
}}
.tag {{
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.75em;
    color: white;
    font-weight: 600;
}}
.tag-estado {{
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75em;
    color: var(--accent);
    border: 1px solid var(--accent);
    font-weight: 600;
}}
.fonte {{
    font-size: 0.75em;
    color: var(--text-dim);
    text-transform: uppercase;
}}
.card-title {{
    font-size: 1em;
    margin-bottom: 8px;
    line-height: 1.4;
}}
.card-title a {{
    color: var(--text);
    text-decoration: none;
}}
.card-title a:hover {{ color: var(--accent); }}
.card-meta {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 8px;
    font-size: 0.8em;
    color: var(--text-dim);
}}
.trecho {{
    font-size: 0.85em;
    color: var(--text-dim);
    line-height: 1.5;
    margin-bottom: 12px;
    max-height: 100px;
    overflow: hidden;
}}
.card-actions {{
    display: flex;
    gap: 8px;
    align-items: center;
}}
.btn {{
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 0.8em;
    text-decoration: none;
    border: 1px solid var(--border);
    color: var(--text-dim);
    transition: all 0.2s;
}}
.btn-ok:hover {{ background: #27ae60; color: white; border-color: #27ae60; }}
.btn-skip:hover {{ background: #e74c3c; color: white; border-color: #e74c3c; }}
.data-visto {{
    margin-left: auto;
    font-size: 0.75em;
    color: var(--text-dim);
}}
.empty {{
    text-align: center;
    padding: 60px;
    color: var(--text-dim);
    font-size: 1.1em;
}}
</style>
</head>
<body>
<div class="header">
    <h1>Oportunidades para Perito - Comarcas 200km de GV</h1>
    <div class="stats">
        <div class="stat">Total <b>{stats['total']}</b></div>
        <div class="stat">Recentes <b>{stats.get('recentes', 0)}</b></div>
        <div class="stat">Pendentes <b>{stats['pendentes']}</b></div>
        <div class="stat">Contatadas <b>{stats['contatados']}</b></div>
        <div class="stat">Comarcas <b>{stats['comarcas']}</b></div>
        <div class="stat">Busca <b>{(stats['ultima_busca'] or 'Nunca')[:16]}</b></div>
    </div>
    <div class="stats-cats">{cats_html}</div>
</div>
<div class="filter-row">
    <span class="filter-label">Categoria:</span>
    <button class="filter-btn active" onclick="filtrarCat('todos')">Todos</button>
    <button class="filter-btn" onclick="filtrarCat('escassez_direta')">Escassez</button>
    <button class="filter-btn" onclick="filtrarCat('dificuldade_nomeacao')">Dificuldade</button>
    <button class="filter-btn" onclick="filtrarCat('mutirao')">Mutirão</button>
    <button class="filter-btn" onclick="filtrarCat('perito_fora_comarca')">Fora da Comarca</button>
    <button class="filter-btn" onclick="filtrarCat('cadastro_aberto')">Cadastro Aberto</button>
</div>
<div class="filter-row">
    <span class="filter-label">Estado:</span>
    {estados_btns}
</div>
<div class="filter-row">
    <span class="filter-label">Ano:</span>
    {anos_btns}
</div>
<div class="counter" id="counter"></div>
<div class="container" id="cards">
    {cards_html if cards_html else '<div class="empty">Nenhuma oportunidade encontrada ainda.<br>Execute: python3 main.py --buscar</div>'}
</div>
<script>
let filtros = {{cat: 'todos', estado: 'MG', ano: '2025'}};

function setActive(btn) {{
    btn.closest('.filter-row').querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
}}

function filtrarCat(val) {{
    filtros.cat = val;
    setActive(event.target);
    aplicarFiltros();
}}

function filtrarEstado(val) {{
    filtros.estado = val;
    setActive(event.target);
    aplicarFiltros();
}}

function filtrarAno(val) {{
    filtros.ano = val;
    setActive(event.target);
    aplicarFiltros();
}}

function aplicarFiltros() {{
    let visivel = 0;
    document.querySelectorAll('.card').forEach(c => {{
        let show = true;
        if (filtros.cat !== 'todos' && c.dataset.cat !== filtros.cat) show = false;
        if (filtros.estado !== 'todos' && c.dataset.estado !== filtros.estado) show = false;
        if (filtros.ano !== 'todos') {{
            const cardAno = parseInt(c.dataset.ano || '0');
            const filtroAno = parseInt(filtros.ano);
            if (cardAno < filtroAno) show = false;
        }}
        c.style.display = show ? '' : 'none';
        if (show) visivel++;
    }});
    document.getElementById('counter').textContent = visivel + ' resultado(s)';
}}

// Aplicar filtros padrão ao carregar
document.addEventListener('DOMContentLoaded', aplicarFiltros);
</script>
</body>
</html>"""


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/contatado" and "id" in params:
            marcar_contatado(int(params["id"][0]))
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        if parsed.path == "/ignorar" and "id" in params:
            ignorar_oportunidade(int(params["id"][0]))
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(gerar_html().encode("utf-8"))

    def log_message(self, format, *args):
        pass


def iniciar_dashboard():
    server = http.server.HTTPServer(("", DASHBOARD_PORT), DashboardHandler)
    print(f"\nDashboard rodando em http://localhost:{DASHBOARD_PORT}")
    print("Ctrl+C para parar\n")
    threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{DASHBOARD_PORT}")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard encerrado.")
        server.shutdown()
