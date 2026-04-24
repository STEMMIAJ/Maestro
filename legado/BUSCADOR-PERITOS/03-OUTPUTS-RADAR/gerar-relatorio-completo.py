#!/usr/bin/env python3
"""Radar — Relatório completo dividido por categoria com caminhos completos."""

import json
import sys
from datetime import datetime
from collections import Counter, defaultdict
from pathlib import Path

RADAR_DIR = Path.home() / "Desktop" / "Radar"
HOME = str(Path.home())

CAT_CORES = {
    "pericia": ("#d35400", "Perícia"),
    "web": ("#8e44ad", "Web/Sites"),
    "automacao": ("#2980b9", "Automação"),
    "config": ("#7f8c8d", "Configuração"),
    "documentacao": ("#27ae60", "Documentação"),
    "outro": ("#95a5a6", "Outros"),
}

CAT_ORDEM = ["pericia", "automacao", "documentacao", "web", "config", "outro"]


def fmt_tam(b):
    if b < 1024: return f"{b} B"
    if b < 1048576: return f"{b/1024:.1f} KB"
    if b < 1073741824: return f"{b/1048576:.1f} MB"
    return f"{b/1073741824:.1f} GB"


def fmt_hora(dm):
    if not dm: return ""
    try:
        return datetime.strptime(dm, "%Y-%m-%dT%H:%M:%S").strftime("%H:%M")
    except ValueError:
        return ""


def main():
    snapshot_path = sys.argv[1] if len(sys.argv) > 1 else ""
    output_path = sys.argv[2] if len(sys.argv) > 2 else str(Path.home() / "Desktop" / "RELATORIO-RADAR.html")
    horas = int(sys.argv[3]) if len(sys.argv) > 3 else 12

    if not snapshot_path:
        snaps = sorted(RADAR_DIR.glob("dados/snapshot-*.json"), reverse=True)
        if not snaps:
            print("Nenhum snapshot.")
            sys.exit(1)
        snapshot_path = str(snaps[0])

    with open(snapshot_path) as f:
        data = json.load(f)

    arquivos = data.get("arquivos", [])
    total = len(arquivos)
    tamanho_total = sum(a.get("tamanho", 0) for a in arquivos)

    # Agrupar por categoria
    por_cat = defaultdict(list)
    for a in arquivos:
        por_cat[a.get("categoria", "outro")].append(a)

    # Dentro de cada categoria, agrupar por pasta
    def pasta_base(caminho):
        c = caminho.replace(HOME + "/", "")
        partes = c.split("/")
        if len(partes) >= 3:
            return "/".join(partes[:3])
        if len(partes) >= 2:
            return "/".join(partes[:2])
        return partes[0] if partes else ""

    # Stats
    cats = Counter(a.get("categoria", "outro") for a in arquivos)
    exts = Counter(a.get("extensao", "").lower() for a in arquivos if a.get("extensao"))
    ext_top = ", ".join(f"{e} ({n})" for e, n in exts.most_common(5))

    # Horas de atividade
    horas_ativ = Counter()
    for a in arquivos:
        dm = a.get("data_modificacao", "")
        if dm:
            try:
                dt = datetime.strptime(dm, "%Y-%m-%dT%H:%M:%S")
                horas_ativ[dt.hour] += 1
            except ValueError:
                pass
    hora_pico = horas_ativ.most_common(1)[0] if horas_ativ else (0, 0)

    agora = datetime.now()

    # ── GERAR SEÇÕES POR CATEGORIA ──
    secoes_html = ""
    nav_links = ""

    for cat_key in CAT_ORDEM:
        if cat_key not in por_cat:
            continue
        arqs = por_cat[cat_key]
        cor, nome = CAT_CORES.get(cat_key, ("#95a5a6", cat_key.title()))
        n = len(arqs)

        nav_links += f'<a href="#{cat_key}" class="nav-link" style="border-color:{cor}">{nome} ({n})</a>\n'

        # Agrupar por pasta dentro da categoria
        por_pasta = defaultdict(list)
        for a in arqs:
            p = pasta_base(a.get("caminho", ""))
            por_pasta[p].append(a)

        # Ordenar pastas por quantidade
        pastas_ord = sorted(por_pasta.items(), key=lambda x: len(x[1]), reverse=True)

        conteudo_pastas = ""
        for pasta, arqs_pasta in pastas_ord:
            arqs_pasta_ord = sorted(arqs_pasta, key=lambda a: a.get("data_modificacao", ""), reverse=True)

            itens = ""
            for a in arqs_pasta_ord:
                nm = a.get("nome", "")
                cam = a.get("caminho", "")
                tam = fmt_tam(a.get("tamanho", 0))
                hora = fmt_hora(a.get("data_modificacao", ""))
                ext = a.get("extensao", "")

                itens += f"""<div class="arquivo">
    <div class="arq-linha1">
        <span class="arq-nome">{nm}</span>
        <span class="arq-meta">{tam} &middot; {hora}</span>
    </div>
    <div class="arq-caminho">{cam}</div>
</div>\n"""

            conteudo_pastas += f"""<div class="pasta-grupo">
    <div class="pasta-titulo">
        <span class="pasta-icone">📁</span>
        <span>{pasta}</span>
        <span class="pasta-count">{len(arqs_pasta)}</span>
    </div>
    {itens}
</div>\n"""

        secoes_html += f"""<div class="secao" id="{cat_key}">
    <div class="secao-header" style="border-color:{cor}">
        <span class="secao-dot" style="background:{cor}"></span>
        <h2>{nome}</h2>
        <span class="secao-count">{n} arquivos</span>
    </div>
    {conteudo_pastas}
</div>\n"""

    # ── RESUMO ──
    cat_top = cats.most_common(1)[0] if cats else ("outro", 0)
    cat_top_nome = CAT_CORES.get(cat_top[0], ("", ""))[1]

    resumo_itens = ""
    for cat_key in CAT_ORDEM:
        if cat_key not in cats:
            continue
        cor, nome = CAT_CORES.get(cat_key, ("#95a5a6", cat_key.title()))
        n = cats[cat_key]
        resumo_itens += f"""<div class="resumo-item">
    <span class="resumo-dot" style="background:{cor}"></span>
    <span class="resumo-nome">{nome}</span>
    <span class="resumo-num">{n}</span>
</div>\n"""

    # ── BARRAS DE HORA ──
    max_h = max(horas_ativ.values()) if horas_ativ else 1
    horas_html = ""
    for h in range(24):
        n = horas_ativ.get(h, 0)
        alt = int((n / max_h) * 50) if max_h > 0 else 0
        op = "0.15" if n == 0 else "1"
        horas_html += f'<div class="hcol"><div class="hbar" style="height:{max(2,alt)}px;opacity:{op}"></div><div class="hlbl">{h}</div></div>\n'

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Radar — Relatório {agora.strftime("%d/%m/%Y")}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
    background: #0d0d1a;
    color: #d0d0d0;
    padding: 25px;
    max-width: 1000px;
    margin: 0 auto;
}}

/* TOPO */
.topo {{
    text-align: center;
    padding: 20px 0 25px;
    border-bottom: 1px solid #1a1a30;
    margin-bottom: 25px;
}}
.topo h1 {{ color: #00d2ff; font-size: 26px; font-weight: 700; }}
.topo .sub {{ color: #555; font-size: 13px; margin-top: 4px; }}

/* RESUMO EXECUTIVO */
.resumo-box {{
    background: #111125;
    border: 1px solid #1a1a35;
    border-radius: 12px;
    padding: 22px 25px;
    margin-bottom: 22px;
}}
.resumo-box h3 {{
    color: #00d2ff;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}}
.resumo-texto {{
    font-size: 15px;
    line-height: 1.8;
    color: #bbb;
    margin-bottom: 15px;
}}
.resumo-texto strong {{ color: #fff; }}
.resumo-grid {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}}
.resumo-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: #0d0d1a;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 13px;
}}
.resumo-dot {{
    width: 10px; height: 10px;
    border-radius: 50%;
}}
.resumo-nome {{ color: #aaa; }}
.resumo-num {{ color: #fff; font-weight: 700; }}

/* STATS */
.stats {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 22px;
}}
.st {{
    background: #111125;
    border: 1px solid #1a1a35;
    border-radius: 10px;
    padding: 15px;
    text-align: center;
}}
.st-n {{ font-size: 26px; font-weight: 700; color: #00d2ff; }}
.st-l {{ font-size: 10px; color: #555; text-transform: uppercase; letter-spacing: 1px; margin-top: 3px; }}

/* ATIVIDADE POR HORA */
.hora-box {{
    background: #111125;
    border: 1px solid #1a1a35;
    border-radius: 10px;
    padding: 15px 20px;
    margin-bottom: 22px;
}}
.hora-box h3 {{
    font-size: 11px;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}}
.horas {{
    display: flex;
    align-items: flex-end;
    gap: 3px;
    height: 65px;
}}
.hcol {{ flex:1; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; }}
.hbar {{ width:100%; background:linear-gradient(0,#0070cc,#00d2ff); border-radius:2px 2px 0 0; }}
.hlbl {{ font-size:8px; color:#444; margin-top:3px; }}

/* NAV */
.nav {{
    display: flex;
    gap: 8px;
    margin-bottom: 22px;
    flex-wrap: wrap;
    position: sticky;
    top: 0;
    background: #0d0d1a;
    padding: 10px 0;
    z-index: 10;
}}
.nav-link {{
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 13px;
    color: #ccc;
    text-decoration: none;
    background: #111125;
    border-left: 3px solid #333;
    transition: background 0.2s;
}}
.nav-link:hover {{ background: #1a1a35; }}

/* FILTRO */
.filtro {{
    margin-bottom: 20px;
}}
.filtro input {{
    width: 100%;
    padding: 11px 16px;
    background: #111125;
    border: 1px solid #1a1a35;
    border-radius: 8px;
    color: #ddd;
    font-size: 14px;
    outline: none;
}}
.filtro input:focus {{ border-color: #00d2ff; }}

/* SEÇÕES */
.secao {{
    margin-bottom: 30px;
}}
.secao-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 0;
    border-bottom: 2px solid #333;
    margin-bottom: 12px;
}}
.secao-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
.secao-header h2 {{ font-size: 16px; color: #fff; }}
.secao-count {{ font-size: 12px; color: #555; margin-left: auto; }}

/* PASTA-GRUPO */
.pasta-grupo {{
    margin-bottom: 15px;
    margin-left: 10px;
}}
.pasta-titulo {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #888;
    padding: 5px 0;
    border-bottom: 1px solid #151525;
    margin-bottom: 5px;
}}
.pasta-icone {{ font-size: 14px; }}
.pasta-count {{
    margin-left: auto;
    background: #1a1a35;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    color: #666;
}}

/* ARQUIVO */
.arquivo {{
    padding: 6px 10px;
    border-radius: 5px;
    margin-bottom: 2px;
    transition: background 0.15s;
}}
.arquivo:hover {{ background: #111125; }}
.arq-linha1 {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.arq-nome {{
    font-size: 13px;
    font-weight: 500;
    color: #e0e0e0;
}}
.arq-meta {{
    font-size: 11px;
    color: #555;
    white-space: nowrap;
}}
.arq-caminho {{
    font-size: 11px;
    color: #3a3a5a;
    font-family: 'SF Mono', Menlo, monospace;
    word-break: break-all;
    margin-top: 1px;
    user-select: all;
}}

@media (max-width: 600px) {{
    .stats {{ grid-template-columns: repeat(2, 1fr); }}
}}
</style>
</head>
<body>

<div class="topo">
    <h1>Radar — Relatório Completo</h1>
    <div class="sub">Últimas {horas} horas &middot; {agora.strftime("%d/%m/%Y às %H:%M")} &middot; {total} arquivos</div>
</div>

<div class="resumo-box">
    <h3>Resumo executivo</h3>
    <div class="resumo-texto">
        Nas últimas <strong>{horas} horas</strong> foram criados ou modificados <strong>{total} arquivos</strong>
        totalizando <strong>{fmt_tam(tamanho_total)}</strong>.
        Categoria principal: <strong>{cat_top_nome}</strong> ({cat_top[1]} arquivos).
        Tipos mais comuns: {ext_top}.
        Pico de atividade: <strong>{hora_pico[0]}h</strong> ({hora_pico[1]} arquivos).
    </div>
    <div class="resumo-grid">
        {resumo_itens}
    </div>
</div>

<div class="stats">
    <div class="st"><div class="st-n">{total}</div><div class="st-l">Arquivos</div></div>
    <div class="st"><div class="st-n">{fmt_tam(tamanho_total)}</div><div class="st-l">Volume total</div></div>
    <div class="st"><div class="st-n">{len(por_cat)}</div><div class="st-l">Categorias</div></div>
    <div class="st"><div class="st-n">{hora_pico[0]}h</div><div class="st-l">Pico</div></div>
</div>

<div class="hora-box">
    <h3>Atividade por hora</h3>
    <div class="horas">{horas_html}</div>
</div>

<div class="nav">
    {nav_links}
</div>

<div class="filtro">
    <input type="text" id="filtro" placeholder="Filtrar por nome ou caminho..." oninput="filtrar()">
</div>

{secoes_html}

<script>
function filtrar() {{
    const q = document.getElementById('filtro').value.toLowerCase();
    document.querySelectorAll('.arquivo').forEach(el => {{
        el.style.display = el.textContent.toLowerCase().includes(q) ? '' : 'none';
    }});
    // Esconder pastas vazias
    document.querySelectorAll('.pasta-grupo').forEach(g => {{
        const visiveis = g.querySelectorAll('.arquivo:not([style*="display: none"])');
        g.style.display = visiveis.length > 0 ? '' : 'none';
    }});
}}
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Radar: {total} arquivos → {output_path}")


if __name__ == "__main__":
    main()
