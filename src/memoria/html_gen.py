"""Gera dashboard HTML pesquisável da memória de sessões."""

import json
import os
from datetime import datetime

from .db import get_connection, get_stats


def generate_dashboard(db_path, output_path):
    """Gera HTML standalone com dados embutidos e busca client-side."""
    conn = get_connection(db_path)

    # Buscar todas as sessões
    rows = conn.execute("""
        SELECT id, slug, model, started_at, ended_at, duration_minutes,
               topics, summary, user_message_count, assistant_message_count,
               tool_use_count, files_written_count, cwd
        FROM sessions
        WHERE user_message_count > 0 OR tool_use_count > 0
        ORDER BY started_at DESC
    """).fetchall()

    sessions = []
    for r in rows:
        sessions.append({
            "id": r[0] or "",
            "slug": r[1] or "",
            "model": r[2] or "",
            "started": r[3] or "",
            "ended": r[4] or "",
            "duration": r[5],
            "topics": r[6] or "",
            "summary": (r[7] or "")[:150],
            "user_msgs": r[8] or 0,
            "assistant_msgs": r[9] or 0,
            "tools": r[10] or 0,
            "files": r[11] or 0,
            "cwd": r[12] or "",
        })

    stats = get_stats(conn)
    conn.close()

    # Gerar HTML
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    sessions_json = json.dumps(sessions, ensure_ascii=False)

    # O HTML usa apenas DOM APIs seguras (createElement/textContent)
    # A única exceção é o highlight de busca que usa createTextNode + mark element
    html = _build_html(sessions_json, stats, now)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)


def _build_html(sessions_json, stats, now):
    total = stats['total_sessions']
    hours = stats['total_hours']
    first = stats['first_session']
    last = stats['last_session']

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Memoria Claude Code</title>
<style>
:root {{
  --bg-deep: #04060d;
  --bg-surface: #0a0f1e;
  --bg-card: #101729;
  --bg-hover: #151d35;
  --accent: #3b82f6;
  --accent-soft: rgba(59,130,246,0.10);
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --text: #eaf0f7;
  --text2: #94a3b8;
  --text3: #5a6882;
  --border: rgba(148,163,184,0.08);
  --radius: 14px;
  --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: var(--font); background: var(--bg-deep); color: var(--text); min-height: 100vh; }}
body::before {{ content: ''; position: fixed; inset: 0; background: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59,130,246,0.05) 0%, transparent 70%); pointer-events: none; }}
.header {{ position: sticky; top: 0; z-index: 10; background: rgba(4,6,13,0.9); backdrop-filter: blur(16px); border-bottom: 1px solid var(--border); padding: 14px 24px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }}
.header h1 {{ font-size: 16px; font-weight: 700; background: linear-gradient(135deg, var(--accent), #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.header .info {{ font-size: 11px; color: var(--text3); }}
.search {{ flex: 1; min-width: 200px; background: var(--bg-surface); border: 1px solid var(--border); color: var(--text); padding: 8px 14px; border-radius: 999px; font-size: 13px; outline: none; font-family: var(--font); }}
.search:focus {{ border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }}
.main {{ max-width: 1100px; margin: 0 auto; padding: 20px 24px 60px; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 24px; }}
.stat {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; text-align: center; }}
.stat-val {{ font-size: 24px; font-weight: 700; color: var(--accent); }}
.stat-lbl {{ font-size: 11px; color: var(--text3); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.08em; }}
.filters {{ display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }}
.fbtn {{ background: var(--bg-card); border: 1px solid var(--border); color: var(--text2); padding: 5px 12px; border-radius: 999px; font-size: 11px; cursor: pointer; font-family: var(--font); transition: all 0.12s; }}
.fbtn:hover, .fbtn.on {{ border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }}
.count {{ font-size: 12px; color: var(--text3); margin-bottom: 12px; }}
.session {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; margin-bottom: 8px; transition: border-color 0.12s; }}
.session:hover {{ border-color: rgba(148,163,184,0.18); }}
.s-top {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 6px; flex-wrap: wrap; }}
.s-date {{ font-size: 13px; font-weight: 600; }}
.s-dur {{ font-size: 11px; color: var(--text3); background: var(--bg-surface); padding: 2px 8px; border-radius: 6px; }}
.s-model {{ font-size: 10px; color: var(--text3); background: var(--bg-surface); padding: 2px 8px; border-radius: 6px; }}
.s-slug {{ font-size: 11px; color: var(--accent); font-family: monospace; }}
.s-topics {{ font-size: 11px; color: var(--warning); margin: 4px 0; }}
.s-summary {{ font-size: 12px; color: var(--text2); line-height: 1.5; word-break: break-word; }}
.s-meta {{ display: flex; gap: 12px; margin-top: 8px; font-size: 10px; color: var(--text3); }}
.hl {{ background: rgba(245,158,11,0.3); color: var(--text); border-radius: 2px; padding: 0 2px; }}
.empty {{ text-align: center; padding: 40px; color: var(--text3); font-size: 14px; }}
.load-more {{ display: block; width: 100%; padding: 10px; background: var(--bg-card); border: 1px dashed var(--border); color: var(--text3); border-radius: var(--radius); font-size: 12px; cursor: pointer; font-family: var(--font); margin-top: 8px; }}
.load-more:hover {{ border-color: var(--accent); color: var(--accent); }}
@media (max-width: 600px) {{ .main {{ padding: 12px; }} .stats {{ grid-template-columns: repeat(2, 1fr); }} }}
</style>
</head>
<body>
<div class="header">
  <h1>MEMORIA CLAUDE CODE</h1>
  <span class="info">{total} sessoes | {hours}h | Atualizado: {now}</span>
  <input class="search" id="q" type="text" placeholder="Buscar sessoes..." autofocus>
</div>
<div class="main">
  <div class="stats" id="stats-grid"></div>
  <div class="filters" id="filters"></div>
  <div class="count" id="count"></div>
  <div id="list"></div>
</div>
<script>
var ALL={sessions_json};
var PAGE=50,showing=PAGE,query='',mf='';

function E(t,a,c){{var e=document.createElement(t);if(a)Object.keys(a).forEach(function(k){{if(k==='className')e.className=a[k];else if(k==='textContent')e.textContent=a[k];else e.setAttribute(k,a[k]);}});if(c){{if(typeof c==='string')e.textContent=c;else if(Array.isArray(c))c.forEach(function(x){{if(x)e.appendChild(x);}});else e.appendChild(c);}}return e;}}

function fmtD(s){{if(!s)return'?';var d=s.substring(0,10).split('-');return d[2]+'/'+d[1]+'/'+d[0];}}
function fmtT(s){{if(!s)return'';return s.substring(11,16);}}
function fmtDur(m){{if(!m&&m!==0)return'?';if(m<60)return m+'min';return Math.floor(m/60)+'h'+String(m%60).padStart(2,'0');}}
function sModel(m){{if(!m)return'';if(m.indexOf('opus')>=0)return'Opus';if(m.indexOf('sonnet')>=0)return'Sonnet';if(m.indexOf('haiku')>=0)return'Haiku';if(m.indexOf('synthetic')>=0)return'Summary';return m.split('-').pop();}}

function hlText(text,q,parent){{
  if(!text)return;
  if(!q){{parent.appendChild(document.createTextNode(text));return;}}
  var ql=q.toLowerCase(),tl=text.toLowerCase(),idx=tl.indexOf(ql);
  if(idx<0){{parent.appendChild(document.createTextNode(text));return;}}
  parent.appendChild(document.createTextNode(text.substring(0,idx)));
  var m=E('span',{{className:'hl'}},text.substring(idx,idx+q.length));
  parent.appendChild(m);
  parent.appendChild(document.createTextNode(text.substring(idx+q.length)));
}}

// Build stats
(function(){{
  var sg=document.getElementById('stats-grid');
  var data=[
    ['{total}','Sessoes'],['{hours}h','Horas totais'],
    ['{first}','Primeira'],['{last}','Ultima']
  ];
  data.forEach(function(d){{
    var s=E('div',{{className:'stat'}});
    s.appendChild(E('div',{{className:'stat-val'}},d[0]));
    s.appendChild(E('div',{{className:'stat-lbl'}},d[1]));
    sg.appendChild(s);
  }});
}})();

function getModels(){{
  var m={{}};ALL.forEach(function(s){{var sm=sModel(s.model);if(sm)m[sm]=(m[sm]||0)+1;}});
  return Object.entries(m).sort(function(a,b){{return b[1]-a[1];}});
}}

function fil(){{
  var ql=query.toLowerCase();
  return ALL.filter(function(s){{
    if(mf&&sModel(s.model)!==mf)return false;
    if(!ql)return true;
    return(s.topics&&s.topics.toLowerCase().indexOf(ql)>=0)||
      (s.summary&&s.summary.toLowerCase().indexOf(ql)>=0)||
      (s.slug&&s.slug.toLowerCase().indexOf(ql)>=0)||
      (s.cwd&&s.cwd.toLowerCase().indexOf(ql)>=0);
  }});
}}

function render(){{
  var list=document.getElementById('list');list.textContent='';
  var items=fil();
  document.getElementById('count').textContent=items.length+' sessao(es)'+(query?' para "'+query+'"':'');
  if(!items.length){{list.appendChild(E('div',{{className:'empty'}},'Nenhum resultado.'));return;}}
  var show=Math.min(showing,items.length);
  for(var i=0;i<show;i++){{
    var s=items[i],card=E('div',{{className:'session'}});
    var top=E('div',{{className:'s-top'}}),left=E('div');
    left.appendChild(E('span',{{className:'s-date'}},fmtD(s.started)+' '+fmtT(s.started)));
    if(s.slug){{left.appendChild(document.createTextNode(' '));var sl=E('span',{{className:'s-slug'}});hlText(s.slug,query,sl);left.appendChild(sl);}}
    top.appendChild(left);
    var right=E('div',{{style:'display:flex;gap:6px;flex-wrap:wrap'}});
    right.appendChild(E('span',{{className:'s-dur'}},fmtDur(s.duration)));
    var sm=sModel(s.model);if(sm)right.appendChild(E('span',{{className:'s-model'}},sm));
    top.appendChild(right);card.appendChild(top);
    if(s.topics){{var tp=E('div',{{className:'s-topics'}});hlText(s.topics,query,tp);card.appendChild(tp);}}
    if(s.summary){{var su=E('div',{{className:'s-summary'}});hlText(s.summary,query,su);card.appendChild(su);}}
    var meta=E('div',{{className:'s-meta'}});
    meta.appendChild(E('span',null,s.user_msgs+' msgs'));
    meta.appendChild(E('span',null,s.tools+' tools'));
    if(s.files)meta.appendChild(E('span',null,s.files+' arquivos'));
    card.appendChild(meta);list.appendChild(card);
  }}
  if(show<items.length){{
    var btn=E('button',{{className:'load-more'}},'Mostrar mais ('+(items.length-show)+' restantes)');
    btn.addEventListener('click',function(){{showing+=PAGE;render();}});list.appendChild(btn);
  }}
}}

function renderF(){{
  var fc=document.getElementById('filters');fc.textContent='';
  var ab=E('button',{{className:'fbtn'+(mf?'':' on')}},'Todos');
  ab.addEventListener('click',function(){{mf='';showing=PAGE;render();renderF();}});fc.appendChild(ab);
  getModels().forEach(function(m){{
    var b=E('button',{{className:'fbtn'+(mf===m[0]?' on':'')}},m[0]+' ('+m[1]+')');
    b.addEventListener('click',function(){{mf=m[0];showing=PAGE;render();renderF();}});fc.appendChild(b);
  }});
}}

document.getElementById('q').addEventListener('input',function(){{query=this.value.trim();showing=PAGE;render();}});
renderF();render();
</script>
</body>
</html>"""
