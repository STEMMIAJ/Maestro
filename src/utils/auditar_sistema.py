#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditor de Saúde do Sistema Stemmia v1.0
Escaneia agentes, skills, hooks, scripts e gera relatório JSON + HTML dashboard.
Uso: python3 auditar_sistema.py [--json] [--html CAMINHO]
"""

import json
import os
import re
import glob
import subprocess
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# ============================================================
# CAMINHOS
# ============================================================
HOME = Path.home()
AGENTS_DIR = HOME / ".claude" / "agents"
PLUGIN_DIR = HOME / ".claude" / "plugins" / "stemmia-forense"
PLUGIN_SKILLS_DIR = PLUGIN_DIR / "skills"
PLUGIN_AGENTS_DIR = PLUGIN_DIR / "agents"
SETTINGS_FILE = HOME / ".claude" / "settings.json"
ANALISADOR = HOME / "Desktop" / "ANALISADOR FINAL"
SCRIPTS_DIR = ANALISADOR / "scripts"
HOOKS_DIR = ANALISADOR / "hooks"
PLAN_MODE = HOME / "Desktop" / "Projetos - Plan Mode"
PLAN_SCRIPTS = PLAN_MODE / "scripts"
HANDOFF = ANALISADOR / "config" / "HANDOFF.md"
REGISTRO = HOME / "Desktop" / "Centro de Comando" / "REGISTRO.json"
MEMORY = HOME / ".claude" / "projects" / "-Users-jesusnoleto" / "memory" / "MEMORY.md"
SESSOES_DIR = PLAN_MODE / "Registros Sessoes"
HTML_OUTPUT = HOME / "Desktop" / "SAUDE-SISTEMA-STEMMIA.html"


def contar_agentes():
    """Conta agentes em ~/.claude/agents/ e no plugin."""
    agentes_global = []
    agentes_plugin = []

    if AGENTS_DIR.exists():
        for f in AGENTS_DIR.glob("*.md"):
            nome = f.stem
            # Ler front-matter para descrição
            desc = ""
            try:
                conteudo = f.read_text(encoding="utf-8", errors="replace")
                m = re.search(r"description:\s*[\"']?(.+?)[\"']?\s*\n", conteudo)
                if m:
                    desc = m.group(1).strip().strip("\"'")
            except Exception:
                pass
            agentes_global.append({"nome": nome, "descricao": desc, "caminho": str(f)})

    if PLUGIN_AGENTS_DIR.exists():
        for f in PLUGIN_AGENTS_DIR.glob("*.md"):
            nome = f.stem
            desc = ""
            try:
                conteudo = f.read_text(encoding="utf-8", errors="replace")
                m = re.search(r"description:\s*[\"']?(.+?)[\"']?\s*\n", conteudo)
                if m:
                    desc = m.group(1).strip().strip("\"'")
            except Exception:
                pass
            agentes_plugin.append({"nome": nome, "descricao": desc, "caminho": str(f)})

    return agentes_global, agentes_plugin


def contar_skills():
    """Conta skills no plugin (pastas com SKILL.md + .md soltos)."""
    skills = []
    soltas = []

    if PLUGIN_SKILLS_DIR.exists():
        for item in sorted(PLUGIN_SKILLS_DIR.iterdir()):
            if item.is_dir():
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    nome = item.name
                    desc = ""
                    gatilhos = ""
                    try:
                        conteudo = skill_md.read_text(encoding="utf-8", errors="replace")
                        m = re.search(r"description:\s*[\"']?(.+?)[\"']?\s*\n", conteudo)
                        if m:
                            desc = m.group(1).strip().strip("\"'")
                    except Exception:
                        pass
                    skills.append({"nome": nome, "descricao": desc, "caminho": str(skill_md)})
                else:
                    skills.append({"nome": item.name, "descricao": "(sem SKILL.md)", "caminho": str(item)})
            elif item.suffix == ".md":
                soltas.append({"nome": item.stem, "caminho": str(item)})

    return skills, soltas


def analisar_hooks():
    """Analisa hooks do settings.json."""
    hooks_ativos = []
    hooks_orfaros = []
    problemas = []

    if not SETTINGS_FILE.exists():
        return hooks_ativos, hooks_orfaros, problemas

    try:
        settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        problemas.append("settings.json não pôde ser lido")
        return hooks_ativos, hooks_orfaros, problemas

    hooks_config = settings.get("hooks", {})
    total_hooks = 0

    for evento, grupos in hooks_config.items():
        for grupo in grupos:
            matcher = grupo.get("matcher", "*")
            for hook in grupo.get("hooks", []):
                total_hooks += 1
                cmd = hook.get("command", "")
                # Extrair caminho do script (remover escapes)
                script_path = cmd.replace("\\ ", " ").strip()

                existe = os.path.exists(script_path)
                executavel = os.access(script_path, os.X_OK) if existe else False

                entry = {
                    "evento": evento,
                    "matcher": matcher,
                    "script": os.path.basename(script_path),
                    "caminho": script_path,
                    "existe": existe,
                    "executavel": executavel,
                }
                hooks_ativos.append(entry)

                if not existe:
                    problemas.append(f"Hook {evento} referencia script inexistente: {script_path}")
                elif not executavel:
                    problemas.append(f"Hook {evento} script sem permissão de execução: {script_path}")

    # Scripts em hooks/ e Plan Mode/scripts/ que NÃO estão no settings.json
    scripts_referenciados = {h["caminho"] for h in hooks_ativos}
    for pasta in [HOOKS_DIR, PLAN_SCRIPTS]:
        if pasta.exists():
            for f in pasta.glob("*.sh"):
                if str(f) not in scripts_referenciados:
                    hooks_orfaros.append({"script": f.name, "caminho": str(f)})

    return hooks_ativos, hooks_orfaros, problemas


def analisar_scripts():
    """Lista scripts Python em scripts/ e verifica quais são usados."""
    scripts = []
    if SCRIPTS_DIR.exists():
        for f in sorted(SCRIPTS_DIR.glob("*.py")):
            scripts.append({"nome": f.name, "caminho": str(f), "tamanho_kb": round(f.stat().st_size / 1024, 1)})
    return scripts


def analisar_persistencia():
    """Verifica HANDOFF.md, sessões, REGISTRO.json."""
    resultado = {
        "handoff_existe": False,
        "handoff_tarefas_pendentes": 0,
        "sessoes_total": 0,
        "sessoes_vazias": 0,
        "sessoes_com_conteudo": 0,
        "registro_existe": False,
        "registro_agentes": 0,
        "registro_ultima_atualizacao": "",
    }

    # HANDOFF
    if HANDOFF.exists():
        resultado["handoff_existe"] = True
        try:
            texto = HANDOFF.read_text(encoding="utf-8", errors="replace")
            pendentes = len(re.findall(r"- \[ \]", texto))
            resultado["handoff_tarefas_pendentes"] = pendentes
        except Exception:
            pass

    # Sessões
    if SESSOES_DIR.exists():
        for f in SESSOES_DIR.glob("SESSAO-*.md"):
            resultado["sessoes_total"] += 1
            try:
                conteudo = f.read_text(encoding="utf-8", errors="replace")
                # Considera vazia se tem menos de 300 chars ou só template
                if len(conteudo) < 300 or "A ser preenchido" in conteudo:
                    resultado["sessoes_vazias"] += 1
                else:
                    resultado["sessoes_com_conteudo"] += 1
            except Exception:
                resultado["sessoes_vazias"] += 1

    # REGISTRO.json
    if REGISTRO.exists():
        resultado["registro_existe"] = True
        try:
            reg = json.loads(REGISTRO.read_text(encoding="utf-8"))
            if isinstance(reg, dict):
                resultado["registro_agentes"] = len(reg.get("agentes", reg.get("agents", [])))
            resultado["registro_ultima_atualizacao"] = datetime.fromtimestamp(
                REGISTRO.stat().st_mtime
            ).strftime("%d/%m/%Y %H:%M")
        except Exception:
            pass

    return resultado


def detectar_conflitos(skills, agentes_global, agentes_plugin):
    """Detecta sobreposições de função."""
    conflitos = []

    # 1. Verificadores múltiplos
    verificadores = [s for s in skills if "verificar" in s["nome"] or "conferir" in s["nome"]]
    agentes_verificadores = [a for a in agentes_global if "verificador" in a["nome"].lower() or "verificar" in a["nome"].lower()]
    if len(verificadores) + len(agentes_verificadores) > 3:
        nomes = [v["nome"] for v in verificadores] + [a["nome"] for a in agentes_verificadores]
        conflitos.append({
            "tipo": "Sobreposição de verificadores",
            "gravidade": "importante",
            "componentes": nomes,
            "recomendacao": "Consolidar em 2 verificadores: 1 para peças processuais (petições/laudos) e 1 para erros materiais (CIDs, datas, nomes)."
        })

    # 2. Propostas de honorários
    propostas_skill = [s for s in skills if "proposta" in s["nome"]]
    propostas_agente = [a for a in agentes_global + agentes_plugin if "proposta" in a["nome"].lower() or "honorar" in a["nome"].lower()]
    if len(propostas_skill) + len(propostas_agente) > 1:
        nomes = [p["nome"] for p in propostas_skill] + [a["nome"] for a in propostas_agente]
        conflitos.append({
            "tipo": "Propostas de honorários duplicadas",
            "gravidade": "importante",
            "componentes": nomes,
            "recomendacao": "Manter apenas a skill /proposta do plugin. Remover versão local e agente redundante."
        })

    # 3. Roteadores inteligentes
    roteadores = [a for a in agentes_global + agentes_plugin
                  if any(kw in a["nome"].lower() for kw in ["concierge", "orquestrador", "orq-", "classificador"])]
    if len(roteadores) > 2:
        nomes = [r["nome"] for r in roteadores]
        conflitos.append({
            "tipo": "Roteadores/classificadores múltiplos",
            "gravidade": "leve",
            "componentes": nomes,
            "recomendacao": "Definir hierarquia clara: classificador-intencoes → orq-multi-dominio → concierge (fallback humano)."
        })

    # 4. Análise de processo
    analises = [s for s in skills if s["nome"] in ("analisar", "rapida", "completa", "stemmia")]
    if len(analises) > 2:
        nomes = [a["nome"] for a in analises]
        conflitos.append({
            "tipo": "Múltiplas entradas para análise de processo",
            "gravidade": "leve",
            "componentes": nomes,
            "recomendacao": "Manter: /rapida (resumo), /completa (profunda), /analisar (legacy redirect → /completa)."
        })

    # 5. Skills soltas (.md direto)
    # Já detectado na contagem de skills

    # 6. Sessão / transição
    sessao_agentes = [a for a in agentes_global + agentes_plugin
                      if any(kw in a["nome"].lower() for kw in ["sessao", "sessão", "transicao", "transição", "resumo-sessao"])]
    if len(sessao_agentes) > 2:
        nomes = [s["nome"] for s in sessao_agentes]
        conflitos.append({
            "tipo": "Agentes de sessão com funções parecidas",
            "gravidade": "leve",
            "componentes": nomes,
            "recomendacao": "Consolidar em 2: transicao-sessao (trocar) e resumo-sessao (contexto)."
        })

    return conflitos


def gerar_receituario(problemas_hooks, conflitos, persistencia, hooks_orfaos):
    """Gera lista de ações recomendadas por urgência."""
    receitas = []

    # Críticos
    for p in problemas_hooks:
        if "inexistente" in p:
            receitas.append({"urgencia": "critico", "acao": p, "tipo": "hook"})
        elif "permissão" in p:
            receitas.append({"urgencia": "importante", "acao": p, "tipo": "hook"})

    if persistencia["sessoes_vazias"] > persistencia["sessoes_com_conteudo"]:
        pct = round(persistencia["sessoes_vazias"] / max(persistencia["sessoes_total"], 1) * 100)
        receitas.append({
            "urgencia": "critico",
            "acao": f"{pct}% das sessões têm registro vazio ({persistencia['sessoes_vazias']}/{persistencia['sessoes_total']}). "
                    "O hook sintese-automatica.sh cria templates vazios. Já removido do settings.json.",
            "tipo": "persistencia"
        })

    if persistencia["handoff_tarefas_pendentes"] > 5:
        receitas.append({
            "urgencia": "importante",
            "acao": f"HANDOFF.md tem {persistencia['handoff_tarefas_pendentes']} tarefas pendentes. Revisar e fechar as concluídas.",
            "tipo": "persistencia"
        })

    for c in conflitos:
        receitas.append({
            "urgencia": c["gravidade"],
            "acao": f"{c['tipo']}: {', '.join(c['componentes'])}. {c['recomendacao']}",
            "tipo": "conflito"
        })

    if len(hooks_orfaos) > 10:
        receitas.append({
            "urgencia": "leve",
            "acao": f"{len(hooks_orfaos)} scripts de hooks não estão registrados no settings.json. Avaliar quais ativar.",
            "tipo": "hook"
        })

    # Ordenar por urgência
    ordem = {"critico": 0, "importante": 1, "leve": 2}
    receitas.sort(key=lambda r: ordem.get(r["urgencia"], 3))

    return receitas


def gerar_html(dados):
    """Gera dashboard HTML visual estilo médico."""
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Contagens
    n_agentes = len(dados["agentes_global"]) + len(dados["agentes_plugin"])
    n_skills = len(dados["skills"])
    n_hooks = len(dados["hooks_ativos"])
    n_scripts = len(dados["scripts"])
    n_hooks_orfaos = len(dados["hooks_orfaos"])
    n_skills_soltas = len(dados["skills_soltas"])

    # Score de saúde (0-100)
    score = 100
    for r in dados["receituario"]:
        if r["urgencia"] == "critico":
            score -= 15
        elif r["urgencia"] == "importante":
            score -= 8
        else:
            score -= 3
    score = max(0, score)

    if score >= 80:
        score_cor = "#22c55e"
        score_label = "Saudável"
    elif score >= 60:
        score_cor = "#f59e0b"
        score_label = "Atenção"
    elif score >= 40:
        score_cor = "#f97316"
        score_label = "Comprometido"
    else:
        score_cor = "#ef4444"
        score_label = "Crítico"

    # Problemas hooks
    hooks_ok = sum(1 for h in dados["hooks_ativos"] if h["existe"] and h["executavel"])
    hooks_problema = len(dados["hooks_ativos"]) - hooks_ok

    # Persistência
    p = dados["persistencia"]

    # Montar HTML
    conflitos_html = ""
    for c in dados["conflitos"]:
        grav_cor = {"importante": "#f59e0b", "leve": "#60a5fa", "critico": "#ef4444"}.get(c["gravidade"], "#9ca3af")
        componentes = ", ".join(c["componentes"])
        conflitos_html += f"""
        <div class="card conflict-card">
            <div class="conflict-header">
                <span class="badge" style="background:{grav_cor}">{c['gravidade'].upper()}</span>
                <strong>{c['tipo']}</strong>
            </div>
            <div class="conflict-body">
                <div class="components">{componentes}</div>
                <div class="recommendation">{c['recomendacao']}</div>
            </div>
        </div>"""

    receitas_html = ""
    for r in dados["receituario"]:
        urg_cor = {"critico": "#ef4444", "importante": "#f59e0b", "leve": "#60a5fa"}.get(r["urgencia"], "#9ca3af")
        urg_icon = {"critico": "🔴", "importante": "🟡", "leve": "🔵"}.get(r["urgencia"], "⚪")
        receitas_html += f"""
        <div class="recipe-item">
            <span class="recipe-urgency" style="color:{urg_cor}">{urg_icon} {r['urgencia'].upper()}</span>
            <span class="recipe-text">{r['acao']}</span>
        </div>"""

    hooks_detalhe_html = ""
    for h in dados["hooks_ativos"]:
        status_icon = "✅" if h["existe"] and h["executavel"] else ("⚠️" if h["existe"] else "❌")
        hooks_detalhe_html += f"""
        <tr>
            <td>{status_icon}</td>
            <td>{h['evento']}</td>
            <td>{h['matcher']}</td>
            <td title="{h['caminho']}">{h['script']}</td>
        </tr>"""

    hooks_orfaos_html = ""
    for h in dados["hooks_orfaos"][:15]:
        hooks_orfaos_html += f"""<li title="{h['caminho']}">{h['script']}</li>"""
    if len(dados["hooks_orfaos"]) > 15:
        hooks_orfaos_html += f"<li>... e mais {len(dados['hooks_orfaos']) - 15}</li>"

    agentes_html = ""
    todos_agentes = sorted(dados["agentes_global"] + dados["agentes_plugin"], key=lambda a: a["nome"])
    for a in todos_agentes:
        origem = "plugin" if "plugins" in a["caminho"] else "global"
        agentes_html += f"""
        <tr>
            <td>{a['nome']}</td>
            <td class="desc">{a['descricao'][:80]}{'...' if len(a['descricao']) > 80 else ''}</td>
            <td><span class="badge badge-sm {'badge-plugin' if origem == 'plugin' else 'badge-global'}">{origem}</span></td>
        </tr>"""

    skills_html = ""
    for s in sorted(dados["skills"], key=lambda x: x["nome"]):
        skills_html += f"""
        <tr>
            <td>/{s['nome']}</td>
            <td class="desc">{s['descricao'][:80]}{'...' if len(s['descricao']) > 80 else ''}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Saúde do Sistema Stemmia — {agora}</title>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --surface2: #334155;
            --text: #e2e8f0;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --green: #22c55e;
            --yellow: #f59e0b;
            --red: #ef4444;
            --blue: #60a5fa;
            --orange: #f97316;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            padding: 30px 0 20px;
            border-bottom: 2px solid var(--surface2);
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            color: var(--accent);
            margin-bottom: 5px;
        }}
        .header .subtitle {{
            color: var(--text-muted);
            font-size: 14px;
        }}
        .score-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin: 25px 0;
        }}
        .score-circle {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 6px solid {score_cor};
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: var(--surface);
        }}
        .score-number {{
            font-size: 36px;
            font-weight: 800;
            color: {score_cor};
        }}
        .score-label {{
            font-size: 12px;
            color: {score_cor};
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .vitals {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .vital-card {{
            background: var(--surface);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid var(--surface2);
        }}
        .vital-number {{
            font-size: 32px;
            font-weight: 800;
            color: var(--accent);
        }}
        .vital-label {{
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 5px;
        }}
        .vital-sub {{
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 3px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            font-size: 18px;
            color: var(--accent);
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--surface2);
        }}
        .card {{
            background: var(--surface);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border: 1px solid var(--surface2);
        }}
        .conflict-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }}
        .conflict-body {{
            padding-left: 10px;
        }}
        .components {{
            color: var(--text-muted);
            font-size: 13px;
            margin-bottom: 5px;
        }}
        .recommendation {{
            color: var(--green);
            font-size: 13px;
            font-style: italic;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            color: #fff;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .badge-sm {{
            font-size: 10px;
            padding: 1px 8px;
        }}
        .badge-plugin {{ background: #8b5cf6; }}
        .badge-global {{ background: #6366f1; }}
        .recipe-item {{
            display: flex;
            gap: 12px;
            align-items: flex-start;
            padding: 10px 0;
            border-bottom: 1px solid var(--surface2);
        }}
        .recipe-urgency {{
            font-size: 12px;
            font-weight: 700;
            min-width: 110px;
            white-space: nowrap;
        }}
        .recipe-text {{
            font-size: 13px;
            color: var(--text);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        th {{
            text-align: left;
            padding: 8px 10px;
            background: var(--surface2);
            color: var(--accent);
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        td {{
            padding: 6px 10px;
            border-bottom: 1px solid var(--surface2);
        }}
        td.desc {{
            color: var(--text-muted);
            max-width: 400px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .orfaos-list {{
            list-style: none;
            columns: 2;
            gap: 10px;
        }}
        .orfaos-list li {{
            font-size: 13px;
            color: var(--text-muted);
            padding: 3px 0;
        }}
        .orfaos-list li::before {{
            content: "📄 ";
        }}
        .persist-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .persist-item {{
            background: var(--surface);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid var(--surface2);
        }}
        .persist-item .label {{
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .persist-item .value {{
            font-size: 22px;
            font-weight: 700;
            color: var(--text);
            margin-top: 5px;
        }}
        .persist-item .detail {{
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 3px;
        }}
        .footer {{
            text-align: center;
            color: var(--text-muted);
            font-size: 12px;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--surface2);
        }}
        details {{
            margin-top: 10px;
        }}
        summary {{
            cursor: pointer;
            color: var(--accent);
            font-size: 14px;
            font-weight: 600;
            padding: 5px 0;
        }}
        .tabs {{
            display: flex;
            gap: 5px;
            margin-bottom: 15px;
        }}
        .tab {{
            padding: 8px 16px;
            background: var(--surface);
            border: 1px solid var(--surface2);
            border-radius: 8px;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }}
        .tab:hover, .tab.active {{
            background: var(--surface2);
            color: var(--accent);
            border-color: var(--accent);
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
    </style>
</head>
<body>

<div class="header">
    <h1>🏥 Saúde do Sistema Stemmia</h1>
    <div class="subtitle">Check-up realizado em {agora}</div>
</div>

<div class="score-container">
    <div class="score-circle">
        <div class="score-number">{score}</div>
        <div class="score-label">{score_label}</div>
    </div>
</div>

<!-- SINAIS VITAIS -->
<div class="section">
    <h2>📊 Sinais Vitais</h2>
    <div class="vitals">
        <div class="vital-card">
            <div class="vital-number">{n_agentes}</div>
            <div class="vital-label">Agentes</div>
            <div class="vital-sub">{len(dados['agentes_global'])} global + {len(dados['agentes_plugin'])} plugin</div>
        </div>
        <div class="vital-card">
            <div class="vital-number">{n_skills}</div>
            <div class="vital-label">Skills</div>
            <div class="vital-sub">{n_skills_soltas} soltas (fora do padrão)</div>
        </div>
        <div class="vital-card">
            <div class="vital-number">{n_hooks}</div>
            <div class="vital-label">Hooks Ativos</div>
            <div class="vital-sub">{hooks_ok} OK, {hooks_problema} com problema</div>
        </div>
        <div class="vital-card">
            <div class="vital-number">{n_scripts}</div>
            <div class="vital-label">Scripts Python</div>
            <div class="vital-sub">em scripts/</div>
        </div>
        <div class="vital-card">
            <div class="vital-number">{n_hooks_orfaos}</div>
            <div class="vital-label">Scripts Órfãos</div>
            <div class="vital-sub">.sh não registrados</div>
        </div>
        <div class="vital-card">
            <div class="vital-number">{len(dados['conflitos'])}</div>
            <div class="vital-label">Conflitos</div>
            <div class="vital-sub">sobreposições detectadas</div>
        </div>
    </div>
</div>

<!-- RECEITUÁRIO -->
<div class="section">
    <h2>💊 Receituário — Ações Recomendadas</h2>
    <div class="card">
        {receitas_html if receitas_html else '<div style="color:var(--green);text-align:center;padding:20px">Nenhuma ação urgente necessária. Sistema saudável.</div>'}
    </div>
</div>

<!-- CONFLITOS -->
<div class="section">
    <h2>⚠️ Exames de Conflito</h2>
    {conflitos_html if conflitos_html else '<div class="card" style="text-align:center;color:var(--green)">Nenhum conflito detectado.</div>'}
</div>

<!-- PERSISTÊNCIA -->
<div class="section">
    <h2>💾 Exame de Persistência</h2>
    <div class="persist-grid">
        <div class="persist-item">
            <div class="label">HANDOFF.md</div>
            <div class="value">{'✅ Existe' if p['handoff_existe'] else '❌ Ausente'}</div>
            <div class="detail">{p['handoff_tarefas_pendentes']} tarefas pendentes</div>
        </div>
        <div class="persist-item">
            <div class="label">Sessões Registradas</div>
            <div class="value">{p['sessoes_total']}</div>
            <div class="detail">{p['sessoes_com_conteudo']} com conteúdo, {p['sessoes_vazias']} vazias</div>
        </div>
        <div class="persist-item">
            <div class="label">REGISTRO.json</div>
            <div class="value">{'✅' if p['registro_existe'] else '❌'} {p['registro_agentes']} agentes</div>
            <div class="detail">Atualizado: {p['registro_ultima_atualizacao'] or 'desconhecido'}</div>
        </div>
    </div>
</div>

<!-- HOOKS -->
<div class="section">
    <h2>🔗 Exame de Hooks</h2>

    <details open>
        <summary>Hooks Ativos ({n_hooks})</summary>
        <table>
            <thead><tr><th>Status</th><th>Evento</th><th>Matcher</th><th>Script</th></tr></thead>
            <tbody>{hooks_detalhe_html}</tbody>
        </table>
    </details>

    <details>
        <summary>Scripts Órfãos ({n_hooks_orfaos})</summary>
        <ul class="orfaos-list">{hooks_orfaos_html}</ul>
    </details>
</div>

<!-- CATÁLOGO -->
<div class="section">
    <h2>📋 Catálogo Completo</h2>

    <details>
        <summary>Agentes ({n_agentes})</summary>
        <table>
            <thead><tr><th>Nome</th><th>Descrição</th><th>Origem</th></tr></thead>
            <tbody>{agentes_html}</tbody>
        </table>
    </details>

    <details>
        <summary>Skills ({n_skills})</summary>
        <table>
            <thead><tr><th>Skill</th><th>Descrição</th></tr></thead>
            <tbody>{skills_html}</tbody>
        </table>
    </details>
</div>

<div class="footer">
    Stemmia Forense — Auditor de Saúde v1.0 — Gerado em {agora}<br>
    Próximo check-up recomendado: semanalmente ou após criar 5+ componentes novos
</div>

<script>
// Tabs
document.querySelectorAll('.tab').forEach(tab => {{
    tab.addEventListener('click', () => {{
        const group = tab.closest('.tabs-container');
        group.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        group.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab).classList.add('active');
    }});
}});
</script>

</body>
</html>"""

    return html


def main():
    import sys

    print("🏥 Auditor de Saúde do Sistema Stemmia v1.0")
    print("=" * 50)

    # Coletar dados
    print("📊 Escaneando agentes...")
    agentes_global, agentes_plugin = contar_agentes()
    print(f"   → {len(agentes_global)} globais + {len(agentes_plugin)} plugin = {len(agentes_global) + len(agentes_plugin)} total")

    print("📊 Escaneando skills...")
    skills, skills_soltas = contar_skills()
    print(f"   → {len(skills)} skills + {len(skills_soltas)} soltas")

    print("📊 Analisando hooks...")
    hooks_ativos, hooks_orfaos, problemas_hooks = analisar_hooks()
    print(f"   → {len(hooks_ativos)} ativos + {len(hooks_orfaos)} órfãos")

    print("📊 Listando scripts...")
    scripts = analisar_scripts()
    print(f"   → {len(scripts)} scripts Python")

    print("📊 Verificando persistência...")
    persistencia = analisar_persistencia()

    print("📊 Detectando conflitos...")
    conflitos = detectar_conflitos(skills, agentes_global, agentes_plugin)
    print(f"   → {len(conflitos)} conflitos encontrados")

    # Montar dados
    dados = {
        "data_auditoria": datetime.now().isoformat(),
        "agentes_global": agentes_global,
        "agentes_plugin": agentes_plugin,
        "skills": skills,
        "skills_soltas": skills_soltas,
        "hooks_ativos": hooks_ativos,
        "hooks_orfaos": hooks_orfaos,
        "problemas_hooks": problemas_hooks,
        "scripts": scripts,
        "persistencia": persistencia,
        "conflitos": conflitos,
        "receituario": [],
    }

    # Gerar receituário
    dados["receituario"] = gerar_receituario(problemas_hooks, conflitos, persistencia, hooks_orfaos)

    # Gerar JSON
    json_output = "--json" in sys.argv
    if json_output:
        json_path = ANALISADOR / "config" / "SAUDE-SISTEMA.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n📄 JSON salvo: {json_path}")

    # Gerar HTML
    html_path = HTML_OUTPUT
    for arg in sys.argv:
        if arg.startswith("--html="):
            html_path = Path(arg.split("=", 1)[1])
        elif arg == "--html" and sys.argv.index(arg) + 1 < len(sys.argv):
            html_path = Path(sys.argv[sys.argv.index(arg) + 1])

    print("\n🎨 Gerando dashboard HTML...")
    html = gerar_html(dados)
    html_path.write_text(html, encoding="utf-8")
    print(f"✅ Dashboard salvo: {html_path}")

    # Resumo
    n_total = len(agentes_global) + len(agentes_plugin)
    print(f"\n{'=' * 50}")
    print(f"📋 RESUMO:")
    print(f"   Agentes:    {n_total}")
    print(f"   Skills:     {len(skills)} (+{len(skills_soltas)} soltas)")
    print(f"   Hooks:      {len(hooks_ativos)} ativos, {len(hooks_orfaos)} órfãos")
    print(f"   Scripts:    {len(scripts)}")
    print(f"   Conflitos:  {len(conflitos)}")
    print(f"   Receitas:   {len(dados['receituario'])}")
    print(f"{'=' * 50}")

    return dados


if __name__ == "__main__":
    main()
