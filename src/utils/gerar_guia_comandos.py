#!/usr/bin/env python3
"""
gerar_guia_comandos.py — Gera PDF do Guia de Comandos Stemmia Forense
=====================================================================
Autor: Jésus Eduardo Nolêto da Penha (CRM-MG 92.148)
Versão: 1.0 — 03/03/2026

Escaneia skills/, agents/ e gera HTML → PDF com TODAS as frases
que o usuário pode dizer para ativar cada funcionalidade.

USO:
    python3 gerar_guia_comandos.py
    python3 gerar_guia_comandos.py --output ~/Desktop/MEU-GUIA.pdf

COMO FUNCIONA:
    1. Escaneia ~/.claude/plugins/stemmia-forense/skills/*/SKILL.md
    2. Escaneia ~/.claude/agents/*.md
    3. Escaneia ~/.claude/plugins/stemmia-forense/agents/*.md
    4. Extrai frases-gatilho de cada description
    5. Gera HTML bonito
    6. Converte para PDF via wkhtmltopdf ou Chrome headless
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# === CAMINHOS ===
HOME = Path.home()
SKILLS_DIR = HOME / ".claude" / "plugins" / "stemmia-forense" / "skills"
AGENTS_DIR = HOME / ".claude" / "agents"
PLUGIN_AGENTS_DIR = HOME / ".claude" / "plugins" / "stemmia-forense" / "agents"
DEFAULT_OUTPUT = HOME / "Desktop" / "_PDFs" / "GUIA-COMANDOS-STEMMIA.pdf"
HTML_OUTPUT = HOME / "Desktop" / "_Relatórios-HTML" / "GUIA-COMANDOS-STEMMIA.html"


def extrair_frases_gatilho(description: str) -> "List[str]":
    """Extrai frases entre aspas da description do YAML."""
    frases = re.findall(r'"([^"]+)"', description)
    if not frases:
        frases = re.findall(r"'([^']+)'", description)
    return frases


def extrair_nome_e_desc(skill_path: Path) -> "Optional[dict]":
    """Lê SKILL.md e extrai name, description, frases."""
    try:
        texto = skill_path.read_text(encoding="utf-8")
    except Exception:
        return None

    # Extrair name
    match_name = re.search(r"^name:\s*(.+)$", texto, re.MULTILINE)
    name = match_name.group(1).strip() if match_name else skill_path.parent.name

    # Extrair description (multilinha)
    match_desc = re.search(
        r"description:\s*>?\s*\n((?:\s+.+\n)*)", texto, re.MULTILINE
    )
    if match_desc:
        desc = match_desc.group(1).strip()
    else:
        match_desc = re.search(r'description:\s*"([^"]+)"', texto)
        desc = match_desc.group(1) if match_desc else ""

    frases = extrair_frases_gatilho(desc)

    # Resumo curto (primeira frase significativa após as aspas)
    resumo = ""
    for linha in desc.split("\n"):
        linha = linha.strip()
        if linha and not linha.startswith("Use ") and not linha.startswith("Also"):
            resumo = linha
            break
    if not resumo and desc:
        # Pegar a parte após a última aspa
        partes = desc.split('"')
        if len(partes) > 1:
            resumo = partes[-1].strip().rstrip(".")
            if resumo.startswith(","):
                resumo = resumo[1:].strip()
            if resumo.startswith("or "):
                resumo = resumo[3:].strip()

    return {"name": name, "frases": frases, "resumo": resumo, "desc": desc}


def extrair_agent_info(agent_path: Path) -> "Optional[dict]":
    """Lê agent .md e extrai nome e description."""
    try:
        texto = agent_path.read_text(encoding="utf-8")
    except Exception:
        return None

    name = agent_path.stem

    match_desc = re.search(
        r"description:\s*>?\s*\n((?:\s+.+\n)*)", texto, re.MULTILINE
    )
    if match_desc:
        desc = match_desc.group(1).strip()
    else:
        match_desc = re.search(r'description:\s*"([^"]+)"', texto)
        desc = match_desc.group(1) if match_desc else ""

    # Traduzir nomes para português
    traducoes = {
        "analisador-quesitos-auto": "Analisador de Quesitos",
        "buscador-academico": "Buscador Acadêmico",
        "buscador-base-local": "Buscador na Base Local",
        "buscador-tribunais": "Buscador em Tribunais",
        "classificador-documento": "Classificador de Documentos",
        "classificador-intencoes": "Classificador de Intenções",
        "classificador-tipo-acao": "Classificador de Tipo de Ação",
        "detector-urgencia": "Detector de Urgência",
        "detetive-inconsistencias": "Detetive de Inconsistências",
        "extrator-informacoes-doc": "Extrator de Informações",
        "extrator-partes": "Extrator de Partes",
        "mapeador-provas": "Mapeador de Provas",
        "orq-analise-completa": "Orquestrador de Análise Completa",
        "orq-analise-documento": "Orquestrador de Análise de Documento",
        "orq-analise-rapida": "Orquestrador de Análise Rápida",
        "orq-erros-materiais": "Orquestrador de Erros Materiais",
        "orq-jurisprudencia": "Orquestrador de Jurisprudência",
        "orq-multi-dominio": "Orquestrador Multi-Domínio",
        "redator-laudo": "Redator de Laudo Pericial",
        "resumidor-fatos": "Resumidor de Fatos",
        "revisor-laudo": "Revisor de Laudo Pericial",
        "verificador-100": "Verificador 100%",
        "verificador-cids": "Verificador de CIDs",
        "verificador-cruzado": "Verificador Cruzado",
        "verificador-datas": "Verificador de Datas",
        "verificador-exames": "Verificador de Exames",
        "verificador-medicamentos": "Verificador de Medicamentos",
        "verificador-nomes-numeros": "Verificador de Nomes e Números",
        "batch-analyzer": "Analisador em Lote",
        "batch-verifier": "Verificador em Lote",
        "mapeador-sessao": "Mapeador de Sessão",
        "orquestrador": "Orquestrador Principal",
        "pipeline-pje": "Pipeline PJe",
    }

    nome_pt = traducoes.get(name, name.replace("-", " ").title())

    return {"name": name, "nome_pt": nome_pt, "desc": desc}


def gerar_html(skills: list, agents_globais: list, agents_plugin: list) -> str:
    """Gera HTML completo do guia."""
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")

    # Categorizar skills
    pipelines = [s for s in skills if s["name"].startswith("pipeline")]
    verificacao = [
        s
        for s in skills
        if any(
            x in s["name"]
            for x in ["conferir", "verificar", "provar"]
        )
    ]
    analise = [
        s
        for s in skills
        if any(x in s["name"] for x in ["analisar", "rapida", "completa", "documento", "nomeacao"])
    ]
    peticoes = [
        s
        for s in skills
        if any(
            x in s["name"]
            for x in ["proposta", "aceite", "agendar", "contestar", "justificar"]
        )
    ]
    gestao = [
        s
        for s in skills
        if s not in pipelines
        and s not in verificacao
        and s not in analise
        and s not in peticoes
    ]

    def skill_cards(lista, cor):
        html = ""
        for s in lista:
            frases_html = ""
            for f in s["frases"][:6]:
                frases_html += f'<span class="frase">&ldquo;{f}&rdquo;</span>\n'
            html += f"""
            <div class="card" style="border-left: 4px solid {cor}">
                <div class="card-header">
                    <span class="cmd">/{s['name']}</span>
                </div>
                <div class="frases-container">{frases_html}</div>
            </div>
            """
        return html

    # Categorizar agents
    orquestradores = [
        a for a in agents_globais if a["name"].startswith("orq-")
    ]
    verificadores = [
        a for a in agents_globais if a["name"].startswith("verificador-")
    ]
    extratores = [
        a
        for a in agents_globais
        if any(x in a["name"] for x in ["extrator", "classificador", "detector", "resumidor", "mapeador"])
    ]
    geradores = [
        a
        for a in agents_globais
        if any(x in a["name"] for x in ["redator", "revisor", "detetive", "buscador", "analisador"])
    ]

    def agent_pills(lista):
        html = ""
        for a in lista:
            html += f'<span class="agent-pill">{a["nome_pt"]}</span>\n'
        return html

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Guia de Comandos — Stemmia Forense</title>
<style>
    @page {{ size: A4; margin: 15mm; }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 11px;
        color: #1a1a1a;
        background: #fff;
        line-height: 1.4;
    }}
    .header {{
        text-align: center;
        padding: 12px 0;
        border-bottom: 2px solid #2563eb;
        margin-bottom: 16px;
    }}
    .header h1 {{
        font-size: 20px;
        color: #1e3a5f;
        margin-bottom: 2px;
    }}
    .header .sub {{
        font-size: 10px;
        color: #666;
    }}
    .section {{
        margin-bottom: 14px;
        break-inside: avoid;
    }}
    .section-title {{
        font-size: 13px;
        font-weight: 700;
        color: #fff;
        padding: 4px 10px;
        border-radius: 4px;
        margin-bottom: 6px;
        display: inline-block;
    }}
    .cards {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px;
    }}
    .card {{
        background: #f8f9fa;
        padding: 6px 8px;
        border-radius: 4px;
        break-inside: avoid;
    }}
    .card-header {{
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 3px;
    }}
    .cmd {{
        font-family: 'SF Mono', Monaco, monospace;
        font-size: 11px;
        font-weight: 700;
        color: #2563eb;
    }}
    .frases-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 3px;
    }}
    .frase {{
        background: #e8f0fe;
        color: #1a56db;
        padding: 1px 6px;
        border-radius: 10px;
        font-size: 9px;
        white-space: nowrap;
    }}
    .agents-section {{
        margin-bottom: 12px;
    }}
    .agent-group {{
        margin-bottom: 8px;
    }}
    .agent-group-title {{
        font-size: 10px;
        font-weight: 700;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }}
    .agent-pills {{
        display: flex;
        flex-wrap: wrap;
        gap: 3px;
    }}
    .agent-pill {{
        background: #f0f0f0;
        color: #333;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 9px;
        border: 1px solid #ddd;
    }}
    .stats {{
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 8px 0;
        border-top: 1px solid #e0e0e0;
        margin-top: 10px;
    }}
    .stat {{
        text-align: center;
    }}
    .stat-num {{
        font-size: 18px;
        font-weight: 800;
        color: #2563eb;
    }}
    .stat-label {{
        font-size: 8px;
        color: #888;
        text-transform: uppercase;
    }}
    .footer {{
        text-align: center;
        font-size: 8px;
        color: #aaa;
        margin-top: 8px;
        padding-top: 6px;
        border-top: 1px solid #eee;
    }}
    .tip {{
        background: #fffbeb;
        border: 1px solid #fbbf24;
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 10px;
        margin-bottom: 10px;
    }}
    .tip strong {{ color: #92400e; }}
</style>
</head>
<body>

<div class="header">
    <h1>Guia de Comandos — Stemmia Forense</h1>
    <div class="sub">O que dizer ao Claude para cada tarefa &bull; Atualizado: {agora}</div>
</div>

<div class="tip">
    <strong>Como usar:</strong> Abra o Claude Code em <code>~/Desktop/ANALISADOR FINAL/</code> e diga qualquer frase listada abaixo. Não precisa lembrar comandos — fale naturalmente.
</div>

<div class="section">
    <span class="section-title" style="background: #7c3aed;">PIPELINES — Fluxos Completos</span>
    <div class="cards">
        {skill_cards(pipelines, '#7c3aed')}
    </div>
</div>

<div class="section">
    <span class="section-title" style="background: #059669;">ANÁLISE — Entender o Processo</span>
    <div class="cards">
        {skill_cards(analise, '#059669')}
    </div>
</div>

<div class="section">
    <span class="section-title" style="background: #dc2626;">VERIFICAÇÃO — Conferir e Provar</span>
    <div class="cards">
        {skill_cards(verificacao, '#dc2626')}
    </div>
</div>

<div class="section">
    <span class="section-title" style="background: #2563eb;">PETIÇÕES — Gerar Documentos</span>
    <div class="cards">
        {skill_cards(peticoes, '#2563eb')}
    </div>
</div>

<div class="section">
    <span class="section-title" style="background: #6b7280;">GESTÃO — Organizar e Planejar</span>
    <div class="cards">
        {skill_cards(gestao, '#6b7280')}
    </div>
</div>

<div class="agents-section">
    <span class="section-title" style="background: #1e3a5f;">AGENTES — Trabalhadores Automáticos ({len(agents_globais) + len(agents_plugin)} ativos)</span>

    <div class="agent-group">
        <div class="agent-group-title">Orquestradores (coordenam outros agentes)</div>
        <div class="agent-pills">{agent_pills(orquestradores)}{agent_pills(agents_plugin)}</div>
    </div>

    <div class="agent-group">
        <div class="agent-group-title">Verificadores (conferem dados)</div>
        <div class="agent-pills">{agent_pills(verificadores)}</div>
    </div>

    <div class="agent-group">
        <div class="agent-group-title">Extratores e Classificadores</div>
        <div class="agent-pills">{agent_pills(extratores)}</div>
    </div>

    <div class="agent-group">
        <div class="agent-group-title">Geradores e Buscadores</div>
        <div class="agent-pills">{agent_pills(geradores)}</div>
    </div>
</div>

<div class="stats">
    <div class="stat"><div class="stat-num">{len(skills)}</div><div class="stat-label">Skills</div></div>
    <div class="stat"><div class="stat-num">{len(agents_globais)}</div><div class="stat-label">Agentes</div></div>
    <div class="stat"><div class="stat-num">{len(agents_plugin)}</div><div class="stat-label">Agentes Plugin</div></div>
    <div class="stat"><div class="stat-num">{len(pipelines)}</div><div class="stat-label">Pipelines</div></div>
    <div class="stat"><div class="stat-num">17</div><div class="stat-label">Scripts</div></div>
</div>

<div class="footer">
    Stemmia Forense &bull; Dr. Jésus Eduardo Nolêto da Penha &bull; CRM-MG 92.148
    <br>Gerado automaticamente por <code>gerar_guia_comandos.py</code> em {agora}
    <br>Para atualizar: <code>python3 ~/Desktop/ANALISADOR\\ FINAL/scripts/gerar_guia_comandos.py</code>
</div>

</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(
        description="Gera PDF do Guia de Comandos Stemmia Forense"
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Caminho do PDF")
    args = parser.parse_args()

    # Coletar skills
    skills = []
    if SKILLS_DIR.exists():
        for skill_dir in sorted(SKILLS_DIR.iterdir()):
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                info = extrair_nome_e_desc(skill_file)
                if info:
                    skills.append(info)

    # Coletar agents globais
    agents_globais = []
    if AGENTS_DIR.exists():
        for agent_file in sorted(AGENTS_DIR.glob("*.md")):
            info = extrair_agent_info(agent_file)
            if info:
                agents_globais.append(info)

    # Coletar agents do plugin
    agents_plugin = []
    if PLUGIN_AGENTS_DIR.exists():
        for agent_file in sorted(PLUGIN_AGENTS_DIR.glob("*.md")):
            info = extrair_agent_info(agent_file)
            if info:
                agents_plugin.append(info)

    # Gerar HTML
    html = gerar_html(skills, agents_globais, agents_plugin)

    # Salvar HTML
    html_path = str(HTML_OUTPUT)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML gerado: {html_path}")

    # Converter para PDF
    pdf_path = args.output

    # Tentar wkhtmltopdf primeiro
    try:
        subprocess.run(
            [
                "wkhtmltopdf",
                "--page-size", "A4",
                "--margin-top", "10",
                "--margin-bottom", "10",
                "--margin-left", "10",
                "--margin-right", "10",
                "--encoding", "UTF-8",
                "--quiet",
                html_path,
                pdf_path,
            ],
            check=True,
            capture_output=True,
        )
        print(f"PDF gerado: {pdf_path}")
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    # Tentar Chrome headless
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for chrome in chrome_paths:
        if os.path.exists(chrome):
            try:
                subprocess.run(
                    [
                        chrome,
                        "--headless",
                        "--disable-gpu",
                        f"--print-to-pdf={pdf_path}",
                        "--no-pdf-header-footer",
                        f"file://{html_path}",
                    ],
                    check=True,
                    capture_output=True,
                )
                print(f"PDF gerado: {pdf_path}")
                return
            except subprocess.CalledProcessError:
                pass

    # Tentar LibreOffice como fallback
    try:
        subprocess.run(
            [
                "/opt/homebrew/bin/soffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", os.path.dirname(pdf_path),
                html_path,
            ],
            check=True,
            capture_output=True,
        )
        # Renomear output
        lo_output = os.path.join(
            os.path.dirname(pdf_path),
            os.path.splitext(os.path.basename(html_path))[0] + ".pdf",
        )
        if lo_output != pdf_path and os.path.exists(lo_output):
            os.rename(lo_output, pdf_path)
        print(f"PDF gerado: {pdf_path}")
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    print(f"PDF não gerado (wkhtmltopdf/Chrome/LibreOffice não disponíveis).")
    print(f"HTML disponível em: {html_path}")


if __name__ == "__main__":
    main()
