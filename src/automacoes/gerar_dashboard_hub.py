#!/usr/bin/env python3
"""Gerador de Dashboard Hub — Painel de Trabalho do Perito.

Lê estado_hub.json e PROCESSOS-CONSOLIDADO.json,
gera DASHBOARD-HUB.html standalone (zero deps externas).

Redesign: layout full-width, task-oriented, kanban pipeline.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ESTADO_PATH = Path.home() / "stemmia-forense" / "automacoes" / "estado_hub.json"
DASHBOARD_PATH = Path.home() / "stemmia-forense" / "automacoes" / "DASHBOARD-HUB.html"
CONSOLIDADO_JSON = Path.home() / "stemmia-forense" / "data" / "PROCESSOS-CONSOLIDADO.json"

FONTES = [
    {"id": "dje_tjmg", "nome": "DJe TJMG", "cor": "#3b82f6"},
    {"id": "datajud", "nome": "DataJud API", "cor": "#8b5cf6"},
    {"id": "pje_consulta", "nome": "PJe Consulta", "cor": "#f59e0b"},
    {"id": "comunica_pje", "nome": "Comunica PJe", "cor": "#6b7280"},
]

CORES_ETAPA = {
    "PENDENTE-ACEITE": "#eab308",
    "PENDENTE-PDF": "#f59e0b",
    "PENDENTE-EXTRACAO": "#fb923c",
    "PENDENTE-ANALISE": "#f97316",
    "PENDENTE-PROPOSTA": "#f97316",
    "PENDENTE-AGENDAMENTO": "#8b5cf6",
    "PERICIA-AGENDADA": "#06b6d4",
    "PERICIA-REALIZADA": "#0ea5e9",
    "PENDENTE-LAUDO": "#ec4899",
    "EM-CONTESTACAO": "#ef4444",
    "COMPLETO": "#22c55e",
    "EXPIRADO": "#ef4444",
    "CANCELADO": "#6b7280",
    "RECUSADO": "#6b7280",
    "VAZIO": "#475569",
    "NOMEACAO": "#64748b",
}

# Etapas que aparecem no kanban (ordem visual)
ETAPAS_KANBAN = [
    "PENDENTE-ACEITE",
    "PENDENTE-PDF",
    "PENDENTE-ANALISE",
    "PENDENTE-PROPOSTA",
    "PENDENTE-AGENDAMENTO",
    "PERICIA-AGENDADA",
    "PERICIA-REALIZADA",
    "PENDENTE-LAUDO",
    "EM-CONTESTACAO",
]

# Labels curtos para kanban
ETAPA_LABELS = {
    "PENDENTE-ACEITE": "ACEITE",
    "PENDENTE-PDF": "PDF",
    "PENDENTE-ANALISE": "ANALISE",
    "PENDENTE-PROPOSTA": "PROPOSTA",
    "PENDENTE-AGENDAMENTO": "AGENDAMENTO",
    "PERICIA-AGENDADA": "AGENDADA",
    "PERICIA-REALIZADA": "REALIZADA",
    "PENDENTE-LAUDO": "LAUDO",
    "EM-CONTESTACAO": "CONTESTACAO",
}

# Prazos em dias corridos por etapa
PRAZOS_ETAPA = {
    "PENDENTE-ACEITE": 7,        # ~5 uteis
    "PENDENTE-PROPOSTA": 5,      # 5 corridos
    "PENDENTE-LAUDO": 30,        # 30 corridos
    "EM-CONTESTACAO": 21,        # ~15 uteis
}

ETAPAS_INATIVAS = {"COMPLETO", "EXPIRADO", "CANCELADO", "RECUSADO", "VAZIO"}

CORES_SITUACAO = {
    "ACEITA": "#22c55e",
    "SERVICO PRESTADO": "#3b82f6",
    "PERDA DE PRAZO": "#ef4444",
    "CANCELADA PELO JUIZ": "#f97316",
    "RECUSADA": "#a855f7",
    "PJe direto": "#64748b",
    "AGUARDANDO ACEITE": "#eab308",
}


def carregar_estado():
    if ESTADO_PATH.exists():
        with open(ESTADO_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {
        "timestamp": datetime.now().isoformat(),
        "duracao_segundos": 0,
        "fontes": {},
        "descobertas_novas": [],
        "movimentacoes_novas": [],
        "processos": {},
        "historico": [],
    }


def carregar_processos():
    if CONSOLIDADO_JSON.exists():
        with open(CONSOLIDADO_JSON, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return data.get("processos", [])
    return []


def _parse_data(s):
    """Tenta parsear data em DD/MM/YYYY ou YYYYMMDD."""
    if not s:
        return None
    for fmt in ("%d/%m/%Y", "%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip()[:10], fmt)
        except (ValueError, IndexError):
            continue
    return None


def _parse_valor_br(v):
    if not v:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace("R$", "").strip()
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0


def gerar_tarefas(processos):
    """Gera lista de tarefas a partir dos processos ativos.

    Retorna lista de dicts com:
        cnj, cidade, vara, etapa, acao, prazo_dias, urgencia, cor_etapa
    Agrupados por urgencia: VENCIDO, URGENTE, NORMAL, SEM_PRAZO
    """
    hoje = datetime.now()
    tarefas = []

    for p in processos:
        etapa = p.get("etapa_pipeline", "")
        # Normalizar etapas com acento
        etapa_norm = etapa.replace("Í", "I").replace("Ã", "A").replace("Ç", "C")

        if etapa in ETAPAS_INATIVAS or etapa_norm in ETAPAS_INATIVAS:
            continue

        acao = p.get("proxima_acao", "")
        if not acao:
            acao = f"Processar etapa: {etapa}"

        cnj = p.get("cnj", "")
        cidade = p.get("cidade", "") or ""
        vara = p.get("vara", "") or p.get("orgao_julgador", "") or ""
        cor = CORES_ETAPA.get(etapa_norm, CORES_ETAPA.get(etapa, "#64748b"))

        # Calcular prazo
        prazo_dias = None
        data_ref = _parse_data(p.get("data_nomeacao", ""))

        if etapa_norm in PRAZOS_ETAPA and data_ref:
            deadline = data_ref + timedelta(days=PRAZOS_ETAPA[etapa_norm])
            prazo_dias = (deadline - hoje).days

        # Determinar urgencia
        if prazo_dias is not None:
            if prazo_dias < 0:
                urgencia = "VENCIDO"
            elif prazo_dias <= 3:
                urgencia = "URGENTE"
            else:
                urgencia = "NORMAL"
        else:
            urgencia = "SEM_PRAZO"

        tarefas.append({
            "cnj": cnj,
            "cidade": cidade,
            "vara": vara,
            "etapa": etapa,
            "etapa_norm": etapa_norm,
            "acao": acao,
            "prazo_dias": prazo_dias,
            "urgencia": urgencia,
            "cor_etapa": cor,
        })

    # Ordenar: VENCIDO primeiro (mais vencido no topo), depois URGENTE, NORMAL, SEM_PRAZO
    ordem_urg = {"VENCIDO": 0, "URGENTE": 1, "NORMAL": 2, "SEM_PRAZO": 3}
    tarefas.sort(key=lambda t: (
        ordem_urg.get(t["urgencia"], 9),
        t["prazo_dias"] if t["prazo_dias"] is not None else 9999,
    ))

    return tarefas


def _cnj_curto(cnj):
    """Retorna CNJ truncado: últimos 13 chars."""
    if len(cnj) > 13:
        return "..." + cnj[-13:]
    return cnj


def gerar_html(estado, processos):
    timestamp = estado.get("timestamp", "")
    duracao = estado.get("duracao_segundos", 0)
    fontes = estado.get("fontes", {})
    descobertas = estado.get("descobertas_novas", [])
    movimentacoes = estado.get("movimentacoes_novas", [])

    try:
        ts_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        ts_fmt = ts_dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        ts_fmt = timestamp[:16] if timestamp else "N/A"

    # Gerar tarefas
    tarefas = gerar_tarefas(processos)

    # Contar por urgencia
    urg_counts = {"VENCIDO": 0, "URGENTE": 0, "NORMAL": 0, "SEM_PRAZO": 0}
    for t in tarefas:
        urg_counts[t["urgencia"]] = urg_counts.get(t["urgencia"], 0) + 1

    # Contar por etapa para kanban
    etapa_counts = {}
    etapa_procs = {}
    for p in processos:
        e = p.get("etapa_pipeline", "").replace("Í", "I").replace("Ã", "A").replace("Ç", "C")
        etapa_counts[e] = etapa_counts.get(e, 0) + 1
        etapa_procs.setdefault(e, []).append(p)

    total_ativos = len(tarefas)
    total_processos = len(processos)

    # Fontes inline dots
    fontes_dots = []
    for f_def in FONTES:
        fid = f_def["id"]
        f_data = fontes.get(fid, {})
        status = f_data.get("status", "desativada")
        if status == "ok":
            dot = "#22c55e"
        elif status == "erro":
            dot = "#ef4444"
        else:
            dot = "#475569"
        fontes_dots.append(
            f'<span class="hd-fonte" title="{f_def["nome"]}: {status}">'
            f'<span class="hd-dot" style="background:{dot}"></span>'
            f'{f_def["nome"]}'
            f'</span>'
        )
    fontes_html = " ".join(fontes_dots)

    # --- TAREFAS HTML ---
    tarefas_sections = []
    urg_config = {
        "VENCIDO": {"label": "VENCIDO", "bg": "#7f1d1d", "fg": "#fca5a5", "border": "#ef4444", "icon": "!!"},
        "URGENTE": {"label": "URGENTE", "bg": "#78350f", "fg": "#fde68a", "border": "#eab308", "icon": "!"},
        "NORMAL": {"label": "NORMAL", "bg": "#1e3a5f", "fg": "#93c5fd", "border": "#3b82f6", "icon": ""},
        "SEM_PRAZO": {"label": "SEM PRAZO", "bg": "#1e293b", "fg": "#94a3b8", "border": "#475569", "icon": ""},
    }

    for urg_key in ["VENCIDO", "URGENTE", "NORMAL", "SEM_PRAZO"]:
        items = [t for t in tarefas if t["urgencia"] == urg_key]
        if not items:
            continue

        cfg = urg_config[urg_key]
        rows = []
        for t in items:
            prazo_text = ""
            if t["prazo_dias"] is not None:
                if t["prazo_dias"] < 0:
                    prazo_text = f'<span class="prazo vencido">vencido ha {abs(t["prazo_dias"])}d</span>'
                elif t["prazo_dias"] == 0:
                    prazo_text = '<span class="prazo vencido">vence HOJE</span>'
                elif t["prazo_dias"] == 1:
                    prazo_text = '<span class="prazo urgente">vence amanha</span>'
                else:
                    cls = "urgente" if t["prazo_dias"] <= 3 else "normal"
                    prazo_text = f'<span class="prazo {cls}">vence em {t["prazo_dias"]}d</span>'

            cidade_vara = t["cidade"]
            if t["vara"]:
                vara_short = t["vara"][:40] + "..." if len(t["vara"]) > 40 else t["vara"]
                cidade_vara += f" — {vara_short}"

            rows.append(
                f'<div class="tarefa-item">'
                f'  <div class="tarefa-top">'
                f'    <span class="cnj">{_cnj_curto(t["cnj"])}</span>'
                f'    <span class="tarefa-badge" style="background:{t["cor_etapa"]}">{t["etapa_norm"]}</span>'
                f'    {prazo_text}'
                f'  </div>'
                f'  <div class="tarefa-acao">{t["acao"]}</div>'
                f'  <div class="tarefa-local">{cidade_vara}</div>'
                f'</div>'
            )

        rows_html = "\n".join(rows)
        tarefas_sections.append(
            f'<div class="urg-group">'
            f'  <div class="urg-header" style="background:{cfg["bg"]};border-left:4px solid {cfg["border"]}">'
            f'    <span style="color:{cfg["fg"]}">{cfg["label"]}</span>'
            f'    <span class="urg-count" style="color:{cfg["fg"]}">{len(items)}</span>'
            f'  </div>'
            f'  <div class="urg-items">'
            f'    {rows_html}'
            f'  </div>'
            f'</div>'
        )

    tarefas_html = "\n".join(tarefas_sections)

    # --- KANBAN HTML ---
    kanban_cols = []
    for etapa in ETAPAS_KANBAN:
        cor = CORES_ETAPA.get(etapa, "#64748b")
        count = etapa_counts.get(etapa, 0)
        label = ETAPA_LABELS.get(etapa, etapa)

        items_html = ""
        for p in etapa_procs.get(etapa, []):
            cidade_short = (p.get("cidade") or "?")[:14]
            items_html += f'<div class="kb-item" title="{p["cnj"]}">{cidade_short}</div>\n'

        kanban_cols.append(
            f'<div class="kb-col" style="border-top:3px solid {cor}">'
            f'  <div class="kb-header"><span style="color:{cor}">{label}</span></div>'
            f'  <div class="kb-count" style="color:{cor}">{count}</div>'
            f'  <div class="kb-items">{items_html}</div>'
            f'</div>'
        )
    kanban_html = "\n".join(kanban_cols)

    # --- MOVIMENTACOES + DESCOBERTAS ---
    sec4_parts = []

    if movimentacoes:
        mov_items = []
        for m in movimentacoes[:10]:
            cnj = m.get("cnj", "")
            cidade = m.get("cidade", "")
            ult_mov = m.get("ultima_movimentacao", "")
            data_mov = m.get("data_movimentacao", "")
            delta = m.get("delta", 0)
            mov_items.append(
                f'<div class="mov-card">'
                f'  <div class="mov-top"><span class="cnj">{_cnj_curto(cnj)}</span><span class="mov-cidade">{cidade}</span></div>'
                f'  <div class="mov-text">{ult_mov}</div>'
                f'  <div class="mov-footer"><span>{data_mov}</span><span class="mov-delta">+{delta}</span></div>'
                f'</div>'
            )
        sec4_parts.append(
            f'<div class="sub-section">'
            f'  <h3>Movimentacoes Novas <span class="count-sm">{len(movimentacoes)}</span></h3>'
            f'  <div class="mov-grid">{"".join(mov_items)}</div>'
            f'</div>'
        )

    if descobertas:
        desc_items = []
        for d in descobertas[:10]:
            cnj = d.get("cnj", "")
            classe = d.get("classe", "")
            orgao = d.get("orgao_julgador", "")
            desc_items.append(
                f'<div class="desc-card">'
                f'  <span class="cnj">{cnj}</span>'
                f'  <span class="desc-info">{classe} — {orgao}</span>'
                f'</div>'
            )
        sec4_parts.append(
            f'<div class="sub-section">'
            f'  <h3>Processos Descobertos <span class="count-sm">{len(descobertas)}</span></h3>'
            f'  <div class="desc-list">{"".join(desc_items)}</div>'
            f'</div>'
        )

    sec4_html = "\n".join(sec4_parts) if sec4_parts else ""

    # --- TABELA COMPLETA ---
    sit_set = sorted(set(p.get("situacao_aj", "") for p in processos if p.get("situacao_aj")))
    etapa_set = sorted(set(p.get("etapa_pipeline", "") for p in processos if p.get("etapa_pipeline")))

    sit_options = '<option value="">Todas</option>\n'
    for s in sit_set:
        sit_options += f'<option value="{s}">{s}</option>\n'
    etapa_options = '<option value="">Todas</option>\n'
    for e in etapa_set:
        etapa_options += f'<option value="{e}">{e}</option>\n'

    proc_rows = []
    for p in processos:
        cnj = p.get("cnj", "")
        cidade = p.get("cidade", "")
        sit = p.get("situacao_aj", "")
        etapa = p.get("etapa_pipeline", "")
        data_nom = p.get("data_nomeacao", "")
        valor = p.get("valor_honorario", "")
        total_mov = p.get("total_movimentos", 0)
        acao = p.get("proxima_acao", "")

        sit_cor = CORES_SITUACAO.get(sit, "#64748b")
        etapa_cor = CORES_ETAPA.get(
            etapa.replace("Í", "I").replace("Ã", "A").replace("Ç", "C"),
            CORES_ETAPA.get(etapa, "#64748b")
        )

        valor_num = _parse_valor_br(valor)
        valor_fmt = ""
        if valor_num > 0:
            valor_fmt = f"R$ {valor_num:,.0f}".replace(",", ".")

        proc_rows.append(
            f'<tr data-cnj="{cnj}" data-sit="{sit}" data-etapa="{etapa}" data-cidade="{cidade}">'
            f'<td class="cnj">{cnj}</td>'
            f'<td>{cidade}</td>'
            f'<td><span class="badge" style="background:{etapa_cor}">{etapa}</span></td>'
            f'<td>{acao[:50]}</td>'
            f'<td>{data_nom}</td>'
            f'<td class="valor">{valor_fmt}</td>'
            f'<td style="text-align:center">{total_mov}</td>'
            f'</tr>'
        )
    proc_rows_html = "\n".join(proc_rows)

    # Embed data
    procs_json = json.dumps(processos, ensure_ascii=False)

    # Secao 4 condicional
    if sec4_html:
        sec4_block = (
            '<div class="section" id="novidades">\n'
            '    <div class="section-title">Novidades</div>\n'
            f'    {sec4_html}\n'
            '  </div>'
        )
    else:
        sec4_block = ""

    # ================================================================
    # HTML COMPLETO
    # ================================================================
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Painel de Trabalho — Stemmia Forense</title>
<style>
:root {{
  --bg: #0f172a; --bg2: #1e293b; --bg3: #334155;
  --text: #e2e8f0; --text2: #94a3b8; --text3: #64748b;
  --accent: #38bdf8; --green: #22c55e; --red: #ef4444;
  --yellow: #eab308; --purple: #8b5cf6; --orange: #f97316;
  --pink: #ec4899; --cyan: #06b6d4; --blue: #3b82f6;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
}}

/* ===== HEADER STICKY ===== */
.header {{
  position: sticky;
  top: 0;
  z-index: 50;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  border-bottom: 1px solid var(--bg3);
  padding: 16px 0;
}}
.header-inner {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}}
.header h1 {{
  font-size: 20px;
  color: #f8fafc;
  font-weight: 700;
  letter-spacing: -0.3px;
}}
.hd-meta {{
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}}
.hd-fontes {{
  display: flex;
  gap: 12px;
  align-items: center;
}}
.hd-fonte {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--text2);
}}
.hd-dot {{
  width: 7px;
  height: 7px;
  border-radius: 50%;
  display: inline-block;
}}
.hd-time {{
  font-size: 11px;
  color: var(--text3);
}}
.hd-stats {{
  display: flex;
  gap: 14px;
  font-size: 12px;
}}
.hd-stat {{
  display: flex;
  align-items: center;
  gap: 4px;
}}
.hd-stat .n {{ font-weight: 700; }}

/* ===== CONTAINER ===== */
.container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}}

/* ===== SECTION ===== */
.section {{
  margin-bottom: 32px;
}}
.section-title {{
  font-size: 17px;
  color: #f1f5f9;
  font-weight: 600;
  margin-bottom: 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--bg3);
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.section-title .count {{
  font-size: 12px;
  color: var(--text2);
  font-weight: 400;
}}

/* ===== TAREFAS ===== */
.urg-group {{
  margin-bottom: 16px;
}}
.urg-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 14px;
  border-radius: 6px 6px 0 0;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}}
.urg-count {{
  font-size: 14px;
  font-weight: 700;
}}
.urg-items {{
  display: flex;
  flex-direction: column;
  gap: 1px;
}}
.tarefa-item {{
  background: var(--bg2);
  padding: 12px 16px;
  border-left: 3px solid var(--bg3);
  transition: background 0.1s;
}}
.tarefa-item:hover {{
  background: rgba(30, 41, 59, 0.9);
  border-left-color: var(--accent);
}}
.tarefa-item:last-child {{
  border-radius: 0 0 6px 6px;
}}
.tarefa-top {{
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}}
.tarefa-badge {{
  display: inline-block;
  padding: 1px 7px;
  border-radius: 3px;
  font-size: 9px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}}
.tarefa-acao {{
  font-size: 14px;
  color: #f1f5f9;
  font-weight: 500;
  margin-bottom: 2px;
}}
.tarefa-local {{
  font-size: 11px;
  color: var(--text3);
}}
.prazo {{
  font-size: 11px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 3px;
}}
.prazo.vencido {{
  background: #7f1d1d;
  color: #fca5a5;
}}
.prazo.urgente {{
  background: #78350f;
  color: #fde68a;
}}
.prazo.normal {{
  color: var(--text2);
}}

/* ===== KANBAN ===== */
.kanban {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 8px;
}}
.kb-col {{
  background: var(--bg2);
  border-radius: 8px;
  padding: 10px;
  min-height: 80px;
}}
.kb-header {{
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}}
.kb-count {{
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 6px;
}}
.kb-items {{
  max-height: 160px;
  overflow-y: auto;
}}
.kb-item {{
  font-size: 10px;
  padding: 3px 5px;
  margin: 2px 0;
  background: rgba(255,255,255,0.03);
  border-radius: 3px;
  color: var(--text2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.kb-item:hover {{
  background: rgba(255,255,255,0.07);
  color: var(--text);
}}

/* ===== MOVIMENTACOES / DESCOBERTAS ===== */
.sub-section {{
  margin-bottom: 16px;
}}
.sub-section h3 {{
  font-size: 14px;
  color: var(--text2);
  margin-bottom: 10px;
  font-weight: 500;
}}
.count-sm {{
  background: var(--bg3);
  color: var(--text2);
  padding: 1px 7px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 400;
  margin-left: 6px;
}}
.mov-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 10px;
}}
.mov-card {{
  background: var(--bg2);
  border-radius: 8px;
  padding: 12px 14px;
  border: 1px solid var(--bg3);
  border-left: 3px solid var(--accent);
}}
.mov-top {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}}
.mov-cidade {{
  font-size: 11px;
  color: var(--text3);
}}
.mov-text {{
  font-size: 13px;
  color: var(--text);
  margin-bottom: 6px;
  line-height: 1.4;
}}
.mov-footer {{
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text3);
}}
.mov-delta {{
  color: var(--accent);
  font-weight: 600;
}}
.desc-list {{
  display: flex;
  flex-direction: column;
  gap: 6px;
}}
.desc-card {{
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--bg2);
  border-radius: 6px;
  border-left: 3px solid var(--purple);
}}
.desc-info {{
  font-size: 12px;
  color: var(--text2);
}}

/* ===== TABELA COLAPSAVEL ===== */
.collapsible-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 12px 16px;
  background: var(--bg2);
  border-radius: 8px;
  border: 1px solid var(--bg3);
  transition: background 0.15s;
  user-select: none;
}}
.collapsible-header:hover {{
  background: var(--bg3);
}}
.collapsible-header .arrow {{
  font-size: 12px;
  color: var(--text3);
  transition: transform 0.2s;
}}
.collapsible-header.open .arrow {{
  transform: rotate(180deg);
}}
.collapsible-body {{
  display: none;
  margin-top: 8px;
}}
.collapsible-body.open {{
  display: block;
}}
.filters {{
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
  align-items: center;
}}
.filters input, .filters select {{
  background: var(--bg2);
  border: 1px solid var(--bg3);
  color: var(--text);
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
}}
.filters input {{ width: 240px; }}
.filters input:focus, .filters select:focus {{
  outline: none;
  border-color: var(--accent);
}}
.filter-count {{
  font-size: 11px;
  color: var(--text3);
}}
.table-wrap {{
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid var(--bg3);
  max-height: 500px;
  overflow-y: auto;
}}
table {{
  width: 100%;
  border-collapse: collapse;
}}
th {{
  background: var(--bg2);
  color: var(--text2);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding: 8px 6px;
  text-align: left;
  position: sticky;
  top: 0;
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}}
th:hover {{ color: var(--accent); }}
th.sorted-asc::after {{ content: ' \\25B2'; font-size: 8px; }}
th.sorted-desc::after {{ content: ' \\25BC'; font-size: 8px; }}
td {{
  padding: 7px 6px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  font-size: 12px;
  vertical-align: top;
}}
tr:hover {{ background: rgba(255,255,255,0.02); }}
.cnj {{
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  font-size: 11px;
  color: #7dd3fc;
  white-space: nowrap;
}}
.badge {{
  display: inline-block;
  padding: 2px 7px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}}
.valor {{
  color: var(--green);
  font-weight: 600;
  white-space: nowrap;
}}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: var(--bg); }}
::-webkit-scrollbar-thumb {{ background: var(--bg3); border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--text3); }}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {{
  .header-inner {{ flex-direction: column; align-items: flex-start; }}
  .kanban {{ grid-template-columns: repeat(3, 1fr); }}
  .mov-grid {{ grid-template-columns: 1fr; }}
  .filters input {{ width: 100%; }}
  .container {{ padding: 16px; }}
}}
</style>
</head>
<body>

<!-- ===== HEADER STICKY ===== -->
<header class="header">
  <div class="header-inner">
    <h1>Painel de Trabalho</h1>
    <div class="hd-meta">
      <div class="hd-fontes">{fontes_html}</div>
      <span class="hd-time">{ts_fmt} ({duracao}s)</span>
      <div class="hd-stats">
        <span class="hd-stat"><span class="n" style="color:var(--red)">{urg_counts["VENCIDO"]}</span> vencidos</span>
        <span class="hd-stat"><span class="n" style="color:var(--yellow)">{urg_counts["URGENTE"]}</span> urgentes</span>
        <span class="hd-stat"><span class="n" style="color:var(--accent)">{total_ativos}</span> ativos</span>
      </div>
    </div>
  </div>
</header>

<div class="container">

  <!-- ===== TAREFAS DO DIA ===== -->
  <div class="section" id="tarefas">
    <div class="section-title">
      Tarefas Pendentes
      <span class="count">{total_ativos} processos ativos de {total_processos}</span>
    </div>
    {tarefas_html}
  </div>

  <!-- ===== KANBAN PIPELINE ===== -->
  <div class="section" id="pipeline">
    <div class="section-title">
      Pipeline
      <span class="count">{total_ativos} em andamento</span>
    </div>
    <div class="kanban">
      {kanban_html}
    </div>
  </div>

  <!-- ===== MOVIMENTACOES + DESCOBERTAS ===== -->
  {sec4_block}

  <!-- ===== TABELA COMPLETA (colapsavel) ===== -->
  <div class="section" id="tabela">
    <div class="collapsible-header" id="tbl-toggle" onclick="toggleTable()">
      <span style="font-size:14px;font-weight:600;color:var(--text)">Todos os processos ({total_processos})</span>
      <span class="arrow">&#9660;</span>
    </div>
    <div class="collapsible-body" id="tbl-body">
      <div class="filters">
        <input type="text" id="filter-text" placeholder="Buscar CNJ, cidade..." autocomplete="off">
        <select id="filter-etapa">{etapa_options}</select>
        <span class="filter-count" id="filter-count">{total_processos} processos</span>
      </div>
      <div class="table-wrap">
        <table id="proc-table">
          <thead>
            <tr>
              <th data-col="cnj">CNJ</th>
              <th data-col="cidade">Cidade</th>
              <th data-col="etapa">Etapa</th>
              <th data-col="acao">Proxima Acao</th>
              <th data-col="data">Nomeacao</th>
              <th data-col="valor">Honorario</th>
              <th data-col="movs">Movs</th>
            </tr>
          </thead>
          <tbody id="proc-tbody">
            {proc_rows_html}
          </tbody>
        </table>
      </div>
    </div>
  </div>

</div>

<script>
(function() {{
  'use strict';

  // Toggle tabela
  window.toggleTable = function() {{
    var header = document.getElementById('tbl-toggle');
    var body = document.getElementById('tbl-body');
    header.classList.toggle('open');
    body.classList.toggle('open');
  }};

  // Filtros
  var filterText = document.getElementById('filter-text');
  var filterEtapa = document.getElementById('filter-etapa');
  var filterCount = document.getElementById('filter-count');
  var tbody = document.getElementById('proc-tbody');

  function applyFilters() {{
    if (!tbody) return;
    var text = (filterText ? filterText.value : '').toLowerCase();
    var etapa = filterEtapa ? filterEtapa.value : '';
    var rows = tbody.querySelectorAll('tr');
    var visible = 0;
    rows.forEach(function(row) {{
      var rowText = row.textContent.toLowerCase();
      var rowEtapa = row.getAttribute('data-etapa') || '';
      var show = true;
      if (text && rowText.indexOf(text) === -1) show = false;
      if (etapa && rowEtapa !== etapa) show = false;
      row.style.display = show ? '' : 'none';
      if (show) visible++;
    }});
    if (filterCount) {{
      filterCount.textContent = visible + ' de ' + rows.length + ' processos';
    }}
  }}

  if (filterText) filterText.addEventListener('input', applyFilters);
  if (filterEtapa) filterEtapa.addEventListener('change', applyFilters);

  // Sorting
  var procTable = document.getElementById('proc-table');
  if (procTable) {{
    var headers = procTable.querySelectorAll('th[data-col]');
    var sortCol = '', sortDir = 1;
    headers.forEach(function(th) {{
      th.addEventListener('click', function() {{
        var col = this.getAttribute('data-col');
        if (sortCol === col) {{ sortDir *= -1; }} else {{ sortCol = col; sortDir = 1; }}
        headers.forEach(function(h) {{ h.classList.remove('sorted-asc', 'sorted-desc'); }});
        this.classList.add(sortDir === 1 ? 'sorted-asc' : 'sorted-desc');
        var colIndex = Array.from(this.parentNode.children).indexOf(this);
        var rowsArr = Array.from(tbody.querySelectorAll('tr'));
        rowsArr.sort(function(a, b) {{
          var aVal = a.children[colIndex] ? a.children[colIndex].textContent.trim() : '';
          var bVal = b.children[colIndex] ? b.children[colIndex].textContent.trim() : '';
          var aNum = parseFloat(aVal.replace(/[R$\\s.]/g, '').replace(',', '.'));
          var bNum = parseFloat(bVal.replace(/[R$\\s.]/g, '').replace(',', '.'));
          if (!isNaN(aNum) && !isNaN(bNum)) return (aNum - bNum) * sortDir;
          return aVal.localeCompare(bVal, 'pt-BR') * sortDir;
        }});
        rowsArr.forEach(function(row) {{ tbody.appendChild(row); }});
      }});
    }});
  }}

}})();
</script>
</body>
</html>'''

    return html


def main():
    estado = carregar_estado()
    processos = carregar_processos()
    html = gerar_html(estado, processos)
    DASHBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_PATH.write_text(html, encoding="utf-8")
    tarefas = gerar_tarefas(processos)
    urg = {"VENCIDO": 0, "URGENTE": 0, "NORMAL": 0, "SEM_PRAZO": 0}
    for t in tarefas:
        urg[t["urgencia"]] = urg.get(t["urgencia"], 0) + 1
    print(f"Dashboard gerado: {DASHBOARD_PATH}", file=sys.stderr)
    print(f"  Processos: {len(processos)} | Ativos: {len(tarefas)}", file=sys.stderr)
    print(f"  Vencidos: {urg['VENCIDO']} | Urgentes: {urg['URGENTE']} | Normais: {urg['NORMAL']} | Sem prazo: {urg['SEM_PRAZO']}", file=sys.stderr)


if __name__ == "__main__":
    main()
