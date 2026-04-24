#!/usr/bin/env python3
"""
gerar_mapa_interativo.py — Gera documentação viva do sistema Stemmia Forense
=============================================================================
Escaneia scripts, agentes, skills, hooks e workflows N8N.
Gera 1 HTML self-contained com 5 abas interativas.

Uso:
    python3 gerar_mapa_interativo.py
    python3 gerar_mapa_interativo.py --deploy
    python3 gerar_mapa_interativo.py --abrir
"""

import ast
import json
import re
import sys
import webbrowser
from datetime import datetime
from html import escape
from pathlib import Path

HOME = Path.home()
SCRIPTS_DIR = HOME / "Desktop" / "ANALISADOR FINAL" / "scripts"
AGENTS_DIR = HOME / ".claude" / "agents"
SKILLS_DIR = HOME / ".claude" / "plugins" / "stemmia-forense" / "skills"
HOOKS_DIR = HOME / "Desktop" / "STEMMIA Dexter" / "hooks"
N8N_DIR = HOME / "Desktop" / "STEMMIA Dexter" / "n8n"
MAPA_HTML = HOME / "Desktop" / "STEMMIA Dexter" / "AUTOMAÇÃO" / "MAPA-AUTOMACAO.html"
DESTINO = HOME / "Desktop" / "STEMMIA Dexter" / "AUTOMAÇÃO" / "MAPA-AUTOMACAO-INTERATIVO.html"
CAT_ORDEM = ["Download", "Análise", "Petições", "Monitoramento", "Verificação", "Gestão", "Utilidades"]
CAT_CORES = {
    "Download": "#3b82f6", "Análise": "#8b5cf6", "Petições": "#059669",
    "Monitoramento": "#f59e0b", "Verificação": "#ef4444", "Gestão": "#6366f1", "Utilidades": "#6b7280",
}

PY_TOKEN = re.compile(
    r"(?P<comment>#.*$)"
    r"|(?P<keyword>\b(?:def|class|import|from|return|if|elif|else|for|while|try|except|"
    r"finally|with|as|raise|pass|break|continue|and|or|not|in|is|lambda|"
    r"yield|global|nonlocal|assert|del|True|False|None|async|await)\b)"
)


# ══════════════════════════════════════════════════════════════════
#  SCANNERS
# ══════════════════════════════════════════════════════════════════

def categorizar_script(nome):
    n = nome.lower()
    if any(x in n for x in ["sincronizar", "consultar_aj", "baixar_pje", "atualizar-pje", "pje_standalone", "consultar_ajg"]):
        return "Download"
    if any(x in n for x in ["pipeline_analise", "extrair_partes", "classificar", "detectar_urgencia", "resumir_fatos", "triagem", "triar_pdf", "sequencia_cron"]):
        return "Análise"
    if any(x in n for x in ["gerar_peticao", "gerar-aceite", "gerar_aceite", "gerar_checklist", "gerar_mutirao", "md_para_pdf", "md_para_xml", "laudo_pipeline"]):
        return "Petições"
    if any(x in n for x in ["monitor", "datajud", "dje_tjmg", "comunica_pje", "deadline"]):
        return "Monitoramento"
    if any(x in n for x in ["gerar_verificacao", "verificar_", "comparar_versoes", "gerar_prova"]):
        return "Verificação"
    if any(x in n for x in ["scanner", "gerar_visao", "gestor", "workflow", "atualizar_progresso", "padronizar", "batch_despachar", "descobrir_", "inbox_"]):
        return "Gestão"
    return "Utilidades"


def escanear_scripts(pasta):
    scripts = []
    pastas_scan = [pasta]
    for d in pasta.iterdir():
        if d.is_dir() and not d.name.startswith(".") and d.name != "__pycache__":
            pastas_scan.append(d)
    for p in pastas_scan:
        for arq in sorted(p.glob("*.py")):
            try:
                codigo = arq.read_text(encoding="utf-8")
            except Exception:
                continue
            linhas = len(codigo.splitlines())
            data_mod = datetime.fromtimestamp(arq.stat().st_mtime).strftime("%d/%m/%Y")
            docstring, funcoes, imports_list, sub_calls = "", [], [], []
            try:
                tree = ast.parse(codigo)
                docstring = ast.get_docstring(tree) or ""
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        funcoes.append({
                            "nome": node.name, "linha": node.lineno,
                            "docstring": ast.get_docstring(node) or "",
                            "args": [a.arg for a in node.args.args if a.arg != "self"],
                        })
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports_list.append(alias.name)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports_list.append(node.module)
            except SyntaxError:
                m = re.search(r'^"""(.*?)"""', codigo, re.DOTALL)
                if m:
                    docstring = m.group(1).strip()
            for m in re.finditer(r"[\"'](\w+\.py)", codigo):
                sub_calls.append(m.group(1).replace(".py", ""))
            cat = categorizar_script(arq.stem)
            if "monitor-publicacoes" in str(arq):
                cat = "Monitoramento"
            scripts.append({
                "nome": arq.stem, "arquivo": arq.name, "caminho": str(arq),
                "linhas": linhas, "data_mod": data_mod, "docstring": docstring,
                "funcoes": funcoes, "imports": imports_list, "subprocess_calls": sub_calls,
                "has_argparse": "argparse" in codigo, "categoria": cat, "codigo": codigo,
            })
    return scripts


def escanear_agentes(pasta):
    agentes = []
    if not pasta.exists():
        return agentes
    for arq in sorted(pasta.glob("*.md")):
        try:
            texto = arq.read_text(encoding="utf-8")
        except Exception:
            continue
        desc, ferramentas, modelo = "", "", ""
        fm = re.search(r"^---\s*\n(.*?)\n---", texto, re.DOTALL)
        if fm:
            ft = fm.group(1)
            m = re.search(r"description:\s*(.+)", ft)
            if m:
                desc = m.group(1).strip().strip('"')
            else:
                m = re.search(r"description:\s*>?\s*\n((?:\s+.+\n)*)", ft)
                if m:
                    desc = m.group(1).strip()
            m = re.search(r"tools:\s*(.+)", ft)
            if m:
                ferramentas = m.group(1).strip()
            m = re.search(r"model:\s*(.+)", ft)
            if m:
                modelo = m.group(1).strip()
        agentes.append({"nome": arq.stem, "descricao": desc[:300], "ferramentas": ferramentas, "modelo": modelo})
    return agentes


def escanear_skills(pasta):
    skills = []
    if not pasta.exists():
        return skills
    for sd in sorted(pasta.iterdir()):
        if not sd.is_dir():
            continue
        sf = sd / "SKILL.md"
        if not sf.exists():
            sf = sd / "skill.md"
        if not sf.exists():
            continue
        try:
            texto = sf.read_text(encoding="utf-8")
        except Exception:
            continue
        nome = sd.name
        m = re.search(r"^name:\s*(.+)$", texto, re.MULTILINE)
        if m:
            nome = m.group(1).strip()
        desc = ""
        m = re.search(r"description:\s*>?\s*\n((?:\s+.+\n)*)", texto, re.MULTILINE)
        if m:
            desc = m.group(1).strip()
        else:
            m = re.search(r"description:\s*(.+)", texto)
            if m:
                desc = m.group(1).strip().strip('"')
        triggers = re.findall(r'"([^"]{3,60})"', desc)
        skills.append({"nome": nome, "dir": sd.name, "descricao": desc[:300], "triggers": triggers[:8]})
    return skills


def escanear_workflows(pasta):
    wfs = []
    if not pasta.exists():
        return wfs
    for arq in sorted(pasta.glob("*.json")):
        try:
            d = json.loads(arq.read_text(encoding="utf-8"))
        except Exception:
            continue
        nos = [{"nome": n.get("name", ""), "tipo": n.get("type", "")} for n in d.get("nodes", [])]
        wfs.append({"nome": d.get("name", arq.stem), "arquivo": arq.name, "nos": nos, "total_nos": len(nos)})
    return wfs


def escanear_hooks(pasta):
    hooks = []
    if not pasta.exists():
        return hooks
    for arq in sorted(pasta.glob("*.js")):
        if arq.name == ".gitkeep":
            continue
        try:
            codigo = arq.read_text(encoding="utf-8")
        except Exception:
            continue
        evento = ""
        m = re.search(r"//\s*(.+)", codigo)
        if m:
            evento = m.group(1).strip()
        hooks.append({"nome": arq.stem, "arquivo": arq.name, "linhas": len(codigo.splitlines()), "evento": evento})
    return hooks


def mapear_dependencias(scripts):
    nomes = {s["nome"] for s in scripts}
    deps = {s["nome"]: {"usa": [], "usado_por": []} for s in scripts}
    for s in scripts:
        usa = set()
        for imp in s["imports"]:
            for parte in imp.split("."):
                if parte in nomes and parte != s["nome"]:
                    usa.add(parte)
        for call in s["subprocess_calls"]:
            if call in nomes and call != s["nome"]:
                usa.add(call)
        deps[s["nome"]]["usa"] = list(usa)
    for nome, d in deps.items():
        for dep in d["usa"]:
            if dep in deps:
                deps[dep]["usado_por"].append(nome)
    return deps


def extrair_fluxos(mapa_path):
    if not mapa_path.exists():
        return []
    texto = mapa_path.read_text(encoding="utf-8")
    fluxos = []
    blocos = re.split(r'(?=<div id="f\d+" class="fluxo">)', texto)
    for bloco in blocos:
        id_m = re.search(r'<div id="(f\d+)" class="fluxo">', bloco)
        if not id_m:
            continue
        fid = id_m.group(1)
        h2 = re.search(r"<h2>(.*?)<span", bloco, re.DOTALL)
        titulo = re.sub(r"<[^>]+>", "", h2.group(1)).strip() if h2 else ""
        st = re.search(r'<span class="status (\w+)">(.*?)</span>', bloco)
        status = st.group(1) if st else "parcial"
        status_label = st.group(2) if st else "Parcial"
        desc_m = re.search(r'<p class="desc">(.*?)</p>', bloco)
        descricao = desc_m.group(1) if desc_m else ""
        scripts_ref = list(set(re.findall(r"(\w+\.py)", bloco)))
        conteudo = bloco[id_m.end():]
        fim = conteudo.rfind("</div>")
        if fim > 0:
            conteudo = conteudo[:fim]
        fluxos.append({
            "id": fid, "titulo": titulo, "status": status, "status_label": status_label,
            "descricao": descricao, "scripts_referenciados": scripts_ref, "html_detalhe": conteudo,
        })
    return fluxos


# ══════════════════════════════════════════════════════════════════
#  HIGHLIGHTING (server-side, sem innerHTML no client)
# ══════════════════════════════════════════════════════════════════

def _e(text):
    return escape(str(text))


def _hl_line(line):
    s = line.lstrip()
    if s.startswith('@'):
        indent = line[:len(line) - len(s)]
        return f'{indent}<span class="hd">{s}</span>'
    def _repl(m):
        if m.group('comment'):
            return f'<span class="hc">{m.group("comment")}</span>'
        return f'<span class="hk">{m.group("keyword")}</span>'
    return PY_TOKEN.sub(_repl, line)


def _linhas_code(codigo):
    linhas = _e(codigo).splitlines()
    return "\n".join(f'<span class="ln">{_hl_line(l)}</span>' for l in linhas)


# ══════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════

def get_css():
    return """
:root{--green:#22c55e;--yellow:#eab308;--red:#ef4444;--blue:#3b82f6;--gray:#6b7280;--bg:#f8fafc;--card:#fff;--text:#1e293b;--border:#e2e8f0;--sidebar:#1e293b;--code-bg:#282c34}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);display:flex;min-height:100vh;font-size:14px;line-height:1.6}
nav{width:280px;background:var(--sidebar);color:#e2e8f0;position:fixed;height:100vh;overflow-y:auto;z-index:10;display:flex;flex-direction:column}
nav .logo{font-size:15px;font-weight:700;padding:18px 20px 10px;color:#fff;letter-spacing:.5px;border-bottom:1px solid #334155}
nav .search{margin:12px 16px;padding:8px 12px;background:#334155;border:none;border-radius:6px;color:#e2e8f0;font-size:13px;outline:none;width:calc(100% - 32px)}
nav .search::placeholder{color:#94a3b8}
nav .tabs{display:flex;flex-direction:column;gap:2px;padding:8px 12px}
nav .tabs a{display:block;padding:8px 12px;border-radius:6px;color:#cbd5e1;text-decoration:none;font-size:13px;cursor:pointer;transition:background .15s}
nav .tabs a:hover{background:#334155;color:#fff}
nav .tabs a.active{background:#3b82f6;color:#fff}
nav .script-nav{padding:8px 12px;border-top:1px solid #334155;overflow-y:auto;flex:1}
nav .script-nav h3{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#94a3b8;margin:10px 0 4px;padding-left:4px}
nav .script-nav a{display:block;padding:4px 8px;color:#94a3b8;text-decoration:none;font-size:12px;border-radius:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
nav .script-nav a:hover{background:#334155;color:#e2e8f0}
main{margin-left:280px;padding:28px 36px;max-width:1100px;width:100%}
.tab{display:none}
.tab.active{display:block}
h1.page-title{font-size:22px;margin-bottom:4px}
.subtitle{color:var(--gray);font-size:13px;margin-bottom:24px}
.cards-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:14px;margin-bottom:28px}
.stat-card{background:var(--card);border-radius:10px;padding:18px;border:1px solid var(--border);text-align:center}
.stat-card .num{font-size:30px;font-weight:700}
.stat-card .label{font-size:11px;color:var(--gray);text-transform:uppercase;letter-spacing:.5px}
.stat-card.green .num{color:var(--green)}
.stat-card.yellow .num{color:var(--yellow)}
.stat-card.red .num{color:var(--red)}
.stat-card.blue .num{color:var(--blue)}
.stat-card.purple .num{color:#8b5cf6}
.badge{display:inline-block;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600;text-transform:uppercase}
.badge.ok{background:#dcfce7;color:#166534}
.badge.parcial{background:#fef9c3;color:#854d0e}
.badge.quebrado{background:#fee2e2;color:#991b1b}
.card{background:var(--card);border-radius:10px;padding:20px 24px;margin-bottom:16px;border:1px solid var(--border)}
.card h2{font-size:16px;display:flex;align-items:center;gap:10px;margin-bottom:6px}
.card .desc{color:var(--gray);font-size:13px;margin-bottom:10px}
.card-cat{display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:600;color:#fff;margin-right:6px}
details{margin-top:8px}
details summary{cursor:pointer;font-size:13px;color:var(--blue);font-weight:600;padding:4px 0;user-select:none}
details summary:hover{text-decoration:underline}
details[open] summary{margin-bottom:8px}
.func-list{list-style:none;margin:8px 0}
.func-list li{padding:4px 0;font-size:13px;border-bottom:1px solid var(--border)}
.func-list li:last-child{border-bottom:none}
.func-name{font-family:'SF Mono',Monaco,monospace;font-weight:600;color:#8b5cf6}
.func-line{color:var(--gray);font-size:11px;margin-left:6px}
.func-doc{color:var(--gray);font-size:12px;display:block;padding-left:12px}
pre.code-block{background:var(--code-bg);border-radius:8px;padding:16px;overflow:auto;max-height:600px;font-size:12px;line-height:1.5;margin:8px 0;position:relative}
pre.code-block code{color:#abb2bf;font-family:'SF Mono',Monaco,'Fira Code',monospace;counter-reset:ln}
pre.code-block code .ln{display:block;white-space:pre}
pre.code-block code .ln::before{counter-increment:ln;content:counter(ln);display:inline-block;width:4ch;margin-right:1.5ch;text-align:right;color:#5c6370;border-right:1px solid #3e4451;padding-right:1ch;user-select:none}
.hk{color:#c678dd}.hs{color:#98c379}.hc{color:#5c6370;font-style:italic}.hd{color:#e5c07b}.hn{color:#d19a66}.hf{color:#61afef}
.btn-copy{position:absolute;top:8px;right:8px;background:#3e4451;color:#abb2bf;border:none;padding:4px 10px;border-radius:4px;font-size:11px;cursor:pointer}
.btn-copy:hover{background:#4b5263}
.dep-links{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}
.dep-links a{display:inline-block;padding:2px 8px;background:#eff6ff;color:#2563eb;border-radius:4px;font-size:12px;text-decoration:none}
.dep-links a:hover{background:#dbeafe}
.agent-card{background:var(--card);border-radius:8px;padding:12px 16px;border:1px solid var(--border);margin-bottom:8px}
.agent-card .name{font-weight:600;font-size:14px}
.agent-card .desc{color:var(--gray);font-size:12px;margin-top:2px}
.agent-card .tools{margin-top:4px}
.tool-badge{display:inline-block;padding:1px 6px;background:#f1f5f9;border-radius:3px;font-size:10px;color:#64748b;margin:2px}
.trigger-badge{display:inline-block;padding:2px 8px;background:#e8f0fe;color:#1a56db;border-radius:12px;font-size:10px;margin:2px}
.passos{list-style:none;counter-reset:passo}
.passos li{counter-increment:passo;padding:8px 0 8px 36px;position:relative;border-left:2px solid var(--border);margin-left:12px}
.passos li::before{content:counter(passo);position:absolute;left:-13px;top:6px;width:24px;height:24px;background:var(--blue);color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600}
.passos li:last-child{border-left-color:transparent}
.cmd{background:#f1f5f9;border:1px solid var(--border);border-radius:6px;padding:6px 10px;font-family:'SF Mono',Monaco,monospace;font-size:12px;margin:4px 0;display:block;word-break:break-all}
.falha{background:#fff7ed;border-left:3px solid #f97316;padding:6px 10px;margin:4px 0;font-size:12px;border-radius:0 4px 4px 0}
.falha strong{color:#c2410c}
.manual{background:#eff6ff;border-left:3px solid var(--blue);padding:6px 10px;margin:4px 0;font-size:12px;border-radius:0 4px 4px 0}
.manual strong{color:#1d4ed8}
.saida{color:var(--green);font-size:12px}
.cred-table{width:100%;border-collapse:collapse;font-size:13px;margin:8px 0}
.cred-table th{text-align:left;padding:6px 10px;background:#f1f5f9;border-bottom:1px solid var(--border)}
.cred-table td{padding:6px 10px;border-bottom:1px solid var(--border)}
.hidden{display:none!important}
.orfao{border-left:3px solid var(--yellow)}
@media print{nav{display:none}main{margin-left:0;max-width:100%}}
@media(max-width:768px){nav{width:220px}main{margin-left:220px;padding:16px}}
"""


# ══════════════════════════════════════════════════════════════════
#  JS (sem innerHTML — tudo seguro com textContent/classList)
# ══════════════════════════════════════════════════════════════════

def get_js():
    return r"""
(function(){
var tabs=document.querySelectorAll('nav .tabs a');
var secs=document.querySelectorAll('.tab');
var snav=document.querySelector('.script-nav');
tabs.forEach(function(t){t.addEventListener('click',function(e){
  e.preventDefault();
  tabs.forEach(function(x){x.classList.remove('active')});
  secs.forEach(function(x){x.classList.remove('active')});
  t.classList.add('active');
  var sec=document.getElementById('tab-'+t.dataset.tab);
  if(sec)sec.classList.add('active');
  if(snav)snav.style.display=t.dataset.tab==='scripts'?'block':'none';
})});
var input=document.querySelector('.search');
if(input)input.addEventListener('input',function(){
  var q=this.value.toLowerCase();
  var active=document.querySelector('.tab.active');
  if(!active)return;
  active.querySelectorAll('[data-s]').forEach(function(el){
    if(!q||el.dataset.s.indexOf(q)!==-1)el.classList.remove('hidden');
    else el.classList.add('hidden');
  });
});
document.querySelectorAll('.btn-copy').forEach(function(b){
  b.addEventListener('click',function(){
    var pre=b.closest('pre');
    if(!pre)return;
    var code=pre.querySelector('code');
    if(!code)return;
    navigator.clipboard.writeText(code.textContent).then(function(){
      b.textContent='Copiado!';setTimeout(function(){b.textContent='Copiar'},1500);
    });
  });
});
document.querySelectorAll('.script-nav a').forEach(function(a){
  a.addEventListener('click',function(e){
    e.preventDefault();
    var id=a.getAttribute('href').slice(1);
    var el=document.getElementById(id);
    if(!el)return;
    tabs.forEach(function(x){x.classList.remove('active')});
    secs.forEach(function(x){x.classList.remove('active')});
    var st=document.querySelector('[data-tab="scripts"]');
    if(st)st.classList.add('active');
    var sec=document.getElementById('tab-scripts');
    if(sec)sec.classList.add('active');
    if(snav)snav.style.display='block';
    el.scrollIntoView({behavior:'smooth',block:'start'});
    el.style.outline='2px solid #3b82f6';
    setTimeout(function(){el.style.outline='none'},2000);
  });
});
})();
"""


# ══════════════════════════════════════════════════════════════════
#  HTML BUILDERS
# ══════════════════════════════════════════════════════════════════

def build_sidebar(scripts_por_cat):
    p = ['<nav>', '<div class="logo">STEMMIA FORENSE</div>',
         '<input type="search" class="search" placeholder="Buscar script, agente, skill...">',
         '<div class="tabs">']
    for tab, label in [("painel", "Painel"), ("fluxos", "Fluxos"), ("scripts", "Scripts"),
                       ("agentes", "Agentes & Skills"), ("infra", "Infraestrutura")]:
        cls = ' class="active"' if tab == "painel" else ""
        p.append(f'<a data-tab="{tab}"{cls}>{label}</a>')
    p.append("</div>")
    p.append('<div class="script-nav" style="display:none">')
    for cat in CAT_ORDEM:
        lista = scripts_por_cat.get(cat, [])
        if not lista:
            continue
        p.append(f"<h3>{_e(cat)} ({len(lista)})</h3>")
        for s in lista:
            p.append(f'<a href="#script-{_e(s["nome"])}">{_e(s["arquivo"])}</a>')
    p.append("</div></nav>")
    return "\n".join(p)


def build_painel(scripts, agentes, skills, workflows, hooks, fluxos, orfaos):
    total_linhas = sum(s["linhas"] for s in scripts)
    total_funcoes = sum(len(s["funcoes"]) for s in scripts)
    ok = sum(1 for f in fluxos if f["status"] == "ok")
    parcial = sum(1 for f in fluxos if f["status"] == "parcial")
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")
    p = [f'<section id="tab-painel" class="tab active">',
         '<h1 class="page-title">Mapa Interativo de Automação</h1>',
         f'<p class="subtitle">Gerado em {agora} — regenerável com: python3 gerar_mapa_interativo.py</p>',
         '<div class="cards-grid">']
    for num, label, cor in [
        (len(scripts), "Scripts Python", "blue"),
        (f"{total_linhas:,}".replace(",", "."), "Linhas de código", "purple"),
        (total_funcoes, "Funções", "green"),
        (len(agentes), "Agentes Claude", "purple"),
        (len(skills), "Skills", "green"),
        (len(workflows), "Workflows N8N", "yellow"),
        (len(hooks), "Hooks", "blue"),
        (len(fluxos), "Fluxos", "green"),
        (ok, "Funcionando", "green"),
        (parcial, "Parciais", "yellow"),
        (len(orfaos), "Scripts órfãos", "red"),
    ]:
        p.append(f'<div class="stat-card {cor}"><div class="num">{num}</div><div class="label">{label}</div></div>')
    p.append("</div>")
    if orfaos:
        p.append('<div class="card orfao"><h2>Scripts órfãos</h2>')
        p.append('<p class="desc">Não referenciados em nenhum fluxo e não chamados por outros scripts.</p>')
        p.append('<div class="dep-links">')
        for s in orfaos:
            p.append(f'<a href="#script-{_e(s["nome"])}">{_e(s["arquivo"])}</a>')
        p.append("</div></div>")
    p.append("</section>")
    return "\n".join(p)


def build_fluxos(fluxos):
    p = ['<section id="tab-fluxos" class="tab">',
         '<h1 class="page-title">Fluxos de Automação</h1>',
         f'<p class="subtitle">{len(fluxos)} fluxos — clique para expandir detalhes</p>']
    for f in fluxos:
        st = f"{_e(f['titulo'])} {_e(f['descricao'])} {' '.join(f.get('scripts_referenciados', []))}".lower()
        p.append(f'<div class="card" id="fluxo-{_e(f["id"])}" data-s="{_e(st)}">')
        p.append(f'<h2>{_e(f["titulo"])} <span class="badge {_e(f["status"])}">{_e(f["status_label"])}</span></h2>')
        p.append(f'<p class="desc">{_e(f["descricao"])}</p>')
        refs = f.get("scripts_referenciados", [])
        if refs:
            p.append('<div class="dep-links">')
            for r in refs:
                p.append(f'<a href="#script-{_e(r.replace(".py", ""))}">{_e(r)}</a>')
            p.append("</div>")
        det = f.get("html_detalhe", "")
        if det:
            p.append("<details><summary>Ver passos detalhados</summary>")
            p.append(det)
            p.append("</details>")
        p.append("</div>")
    p.append("</section>")
    return "\n".join(p)


def build_scripts(scripts, deps, scripts_por_cat):
    p = ['<section id="tab-scripts" class="tab">',
         '<h1 class="page-title">Leitor de Scripts</h1>',
         f'<p class="subtitle">{len(scripts)} scripts — docstring, funções e código-fonte com highlighting</p>']
    for cat in CAT_ORDEM:
        lista = scripts_por_cat.get(cat, [])
        if not lista:
            continue
        cor = CAT_CORES.get(cat, "#6b7280")
        p.append(f'<h2 style="margin:20px 0 10px"><span class="card-cat" style="background:{cor}">{_e(cat)}</span> {len(lista)} scripts</h2>')
        for s in lista:
            nome = s["nome"]
            st = f'{nome} {s["docstring"][:100]} {" ".join(fn["nome"] for fn in s["funcoes"])}'.lower()
            p.append(f'<article class="card" id="script-{_e(nome)}" data-s="{_e(st)}">')
            p.append(f'<h2><span class="card-cat" style="background:{cor}">{_e(cat)}</span> {_e(s["arquivo"])}</h2>')
            p.append(f'<p class="desc">{s["linhas"]} linhas &middot; {_e(s["data_mod"])} &middot; {"CLI (argparse)" if s["has_argparse"] else "sem CLI"}</p>')
            if s["docstring"]:
                dl = s["docstring"].strip().splitlines()
                p.append("<p>" + "<br>".join(_e(l) for l in dl[:8]) + "</p>")
                if len(dl) > 8:
                    p.append(f"<details><summary>Docstring completa ({len(dl)} linhas)</summary>")
                    p.append("<pre>" + "\n".join(_e(l) for l in dl) + "</pre></details>")
            d = deps.get(nome, {"usa": [], "usado_por": []})
            if d["usa"]:
                p.append('<div><strong>Usa:</strong> <span class="dep-links">')
                for dep in d["usa"]:
                    p.append(f'<a href="#script-{_e(dep)}">{_e(dep)}.py</a>')
                p.append("</span></div>")
            if d["usado_por"]:
                p.append('<div><strong>Usado por:</strong> <span class="dep-links">')
                for dep in d["usado_por"]:
                    p.append(f'<a href="#script-{_e(dep)}">{_e(dep)}.py</a>')
                p.append("</span></div>")
            if s["funcoes"]:
                p.append(f'<details><summary>Funções ({len(s["funcoes"])})</summary><ul class="func-list">')
                for fn in s["funcoes"]:
                    args = ", ".join(fn["args"][:6])
                    p.append(f'<li><span class="func-name">{_e(fn["nome"])}({_e(args)})</span>')
                    p.append(f'<span class="func-line">linha {fn["linha"]}</span>')
                    if fn["docstring"]:
                        p.append(f'<span class="func-doc">{_e(fn["docstring"][:120])}</span>')
                    p.append("</li>")
                p.append("</ul></details>")
            p.append(f'<details><summary>Código-fonte ({s["linhas"]} linhas)</summary>')
            p.append(f'<pre class="code-block"><button class="btn-copy">Copiar</button><code>{_linhas_code(s["codigo"])}</code></pre>')
            p.append("</details></article>")
    p.append("</section>")
    return "\n".join(p)


def build_agentes(agentes, skills, hooks):
    p = ['<section id="tab-agentes" class="tab">',
         '<h1 class="page-title">Agentes, Skills & Hooks</h1>',
         f'<p class="subtitle">{len(agentes)} agentes + {len(skills)} skills + {len(hooks)} hooks</p>',
         f"<h2 style='margin:16px 0 8px'>Agentes ({len(agentes)})</h2>"]
    for a in agentes:
        st = f'{a["nome"]} {a["descricao"]}'.lower()
        p.append(f'<div class="agent-card" data-s="{_e(st)}">')
        p.append(f'<div class="name">{_e(a["nome"])}</div>')
        p.append(f'<div class="desc">{_e(a["descricao"][:200])}</div>')
        if a["ferramentas"]:
            p.append('<div class="tools">')
            for t in a["ferramentas"].replace("[", "").replace("]", "").split(","):
                t = t.strip().strip("' \"")
                if t:
                    p.append(f'<span class="tool-badge">{_e(t)}</span>')
            p.append("</div>")
        if a["modelo"]:
            p.append(f'<div class="desc">Modelo: {_e(a["modelo"])}</div>')
        p.append("</div>")
    p.append(f"<h2 style='margin:24px 0 8px'>Skills ({len(skills)})</h2>")
    for sk in skills:
        st = f'{sk["nome"]} {sk["descricao"]}'.lower()
        p.append(f'<div class="agent-card" data-s="{_e(st)}">')
        p.append(f'<div class="name">/{_e(sk["dir"])}</div>')
        p.append(f'<div class="desc">{_e(sk["descricao"][:200])}</div>')
        if sk["triggers"]:
            p.append("<div>")
            for tr in sk["triggers"]:
                p.append(f'<span class="trigger-badge">&ldquo;{_e(tr)}&rdquo;</span>')
            p.append("</div>")
        p.append("</div>")
    if hooks:
        p.append(f"<h2 style='margin:24px 0 8px'>Hooks ({len(hooks)})</h2>")
        for h in hooks:
            p.append(f'<div class="agent-card" data-s="{_e(h["nome"]).lower()}">')
            p.append(f'<div class="name">{_e(h["nome"])}</div>')
            p.append(f'<div class="desc">{h["linhas"]} linhas &middot; {_e(h["evento"])}</div>')
            p.append("</div>")
    p.append("</section>")
    return "\n".join(p)


def build_infra(workflows):
    p = ['<section id="tab-infra" class="tab">',
         '<h1 class="page-title">Infraestrutura</h1>',
         '<p class="subtitle">Credenciais, cron, N8N, dependências do sistema</p>',
         '<div class="card"><h2>Dependências do Sistema</h2>',
         '<table class="cred-table"><tr><th>Ferramenta</th><th>Caminho</th><th>Uso</th></tr>']
    for nome, cam, uso in [
        ("pdftotext", "/opt/homebrew/bin/pdftotext", "Extração de texto de PDF"),
        ("tesseract", "/opt/homebrew/bin/tesseract", "OCR para PDFs escaneados"),
        ("Microsoft Word", "/Applications/Microsoft Word.app", "Conversão DOCX para PDF"),
        ("Python 3", "/usr/bin/python3", "Runtime dos scripts"),
        ("Chrome", "Parallels/Windows", "PJe via Chrome DevTools Protocol"),
    ]:
        p.append(f"<tr><td><strong>{_e(nome)}</strong></td><td><code>{_e(cam)}</code></td><td>{_e(uso)}</td></tr>")
    p.append("</table></div>")
    p.append('<div class="card"><h2>Cron Jobs</h2>')
    p.append('<table class="cred-table"><tr><th>Quando</th><th>O que roda</th></tr>')
    p.append("<tr><td>6h seg-sáb</td><td>monitor_publicacoes.py --notificar --salvar --telegram</td></tr>")
    p.append("<tr><td>20h domingo</td><td>scanner_processos.py + gerar_visao_unificada.py</td></tr>")
    p.append("</table></div>")
    p.append('<div class="card"><h2>Telegram</h2>')
    p.append('<table class="cred-table"><tr><th>Item</th><th>Valor</th></tr>')
    p.append("<tr><td>Bot</td><td>@stemmiapericia_bot</td></tr>")
    p.append("<tr><td>Chat ID</td><td>8397602236</td></tr></table></div>")
    if workflows:
        p.append(f'<div class="card"><h2>Workflows N8N ({len(workflows)})</h2>')
        for wf in workflows:
            p.append(f'<details data-s="{_e(wf["nome"]).lower()}"><summary>{_e(wf["nome"])} ({wf["total_nos"]} nós)</summary>')
            p.append('<table class="cred-table"><tr><th>Nó</th><th>Tipo</th></tr>')
            for no in wf["nos"]:
                p.append(f'<tr><td>{_e(no["nome"])}</td><td><code>{_e(no["tipo"])}</code></td></tr>')
            p.append("</table></details>")
        p.append("</div>")
    p.append('<div class="card"><h2>Credenciais e Acessos</h2>')
    p.append('<table class="cred-table"><tr><th>Serviço</th><th>Status</th></tr>')
    for nome, ok, label in [
        ("Telegram Bot Token", True, "CONFIGURADO"), ("N8N API Key", True, "CONFIGURADO"),
        ("DataJud API", True, "PÚBLICA"), ("DJe TJMG", True, "PÚBLICA"),
        ("Credenciais CNJ", False, "FALTA"), ("Credencial Telegram no N8N", False, "FALTA"),
    ]:
        cor = "color:#22c55e;font-weight:600" if ok else "color:#ef4444;font-weight:600"
        p.append(f'<tr><td>{_e(nome)}</td><td style="{cor}">{_e(label)}</td></tr>')
    p.append("</table></div></section>")
    return "\n".join(p)


# ══════════════════════════════════════════════════════════════════
#  GERADOR PRINCIPAL
# ══════════════════════════════════════════════════════════════════

def gerar_html_completo(scripts, agentes, skills, workflows, hooks, fluxos, deps):
    scripts_por_cat = {}
    for s in scripts:
        scripts_por_cat.setdefault(s["categoria"], []).append(s)
    scripts_nos_fluxos = set()
    for f in fluxos:
        for ref in f.get("scripts_referenciados", []):
            scripts_nos_fluxos.add(ref.replace(".py", ""))
    orfaos = [s for s in scripts
              if s["nome"] not in scripts_nos_fluxos
              and not deps.get(s["nome"], {}).get("usado_por", [])]

    css = get_css()
    js = get_js()
    sidebar = build_sidebar(scripts_por_cat)
    painel = build_painel(scripts, agentes, skills, workflows, hooks, fluxos, orfaos)
    fluxos_html = build_fluxos(fluxos)
    scripts_html = build_scripts(scripts, deps, scripts_por_cat)
    agentes_html = build_agentes(agentes, skills, hooks)
    infra_html = build_infra(workflows)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mapa Interativo — Stemmia Forense</title>
<style>{css}</style>
</head>
<body>
{sidebar}
<main>
{painel}
{fluxos_html}
{scripts_html}
{agentes_html}
{infra_html}
</main>
<script>{js}</script>
</body>
</html>"""


# ══════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════

def main():
    print("Escaneando artefatos...")
    scripts = escanear_scripts(SCRIPTS_DIR)
    agentes = escanear_agentes(AGENTS_DIR)
    skills = escanear_skills(SKILLS_DIR)
    workflows = escanear_workflows(N8N_DIR)
    hooks = escanear_hooks(HOOKS_DIR)
    fluxos = extrair_fluxos(MAPA_HTML)
    deps = mapear_dependencias(scripts)
    print(f"  {len(scripts)} scripts, {len(agentes)} agentes, {len(skills)} skills, "
          f"{len(workflows)} workflows, {len(hooks)} hooks, {len(fluxos)} fluxos")
    html = gerar_html_completo(scripts, agentes, skills, workflows, hooks, fluxos, deps)
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(html, encoding="utf-8")
    tamanho = len(html) // 1024
    print(f"Gerado: {DESTINO} ({tamanho}KB)")
    if "--deploy" in sys.argv:
        sys.path.insert(0, str(Path(__file__).parent))
        try:
            from deploy_site import upload_ftp
            upload_ftp(str(DESTINO), "webdev/mapa-automacao.html")
        except ImportError:
            print("ERRO: deploy_site.py nao encontrado")
    if "--abrir" in sys.argv:
        webbrowser.open(f"file://{DESTINO}")


if __name__ == "__main__":
    main()
