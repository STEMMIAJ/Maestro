#!/usr/bin/env python3
"""
gerar_checklist.py — Checklist interativo: Petição vs PDF do Processo
Stemmia Forense v4.1.0

Gera HTML com checklist da petição (esquerda) e PDF do processo embutido (direita).
Clique numa frase → PDF navega para a página onde o dado aparece.

Uso:
    python3 gerar_checklist.py --peticao PETIÇÃO.md --pdf PROCESSO-ORIGINAL.pdf
    python3 gerar_checklist.py --peticao PETIÇÃO.md --pdf PROCESSO.pdf --output CHECKLIST.html
"""

import re
import os
import sys
import json
import argparse
import subprocess
from html import escape
from datetime import datetime


def extrair_texto_por_pagina(pdf_path: str) -> list[str]:
    """Extrai texto do PDF usando pdftotext, retorna lista de strings por página."""
    result = subprocess.run(
        ["pdftotext", "-layout", pdf_path, "-"],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"Erro ao extrair texto: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    pages = result.stdout.split("\f")
    return [p for p in pages if p.strip()]


def parse_peticao(md_path: str) -> list[dict]:
    """Lê petição .md e divide em seções e itens."""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    secoes = []
    current_section = {"titulo": "Início", "itens": []}

    lines = content.split("\n")
    buffer = []
    in_table = False

    for line in lines:
        stripped = line.strip()

        # Header markdown → nova seção
        if stripped.startswith("#"):
            # Flush buffer
            if buffer:
                texto = "\n".join(buffer).strip()
                if texto and len(texto) > 5:
                    current_section["itens"].append(texto)
                buffer = []

            # Salvar seção anterior se tem itens
            if current_section["itens"]:
                secoes.append(current_section)

            titulo = re.sub(r"^#+\s*", "", stripped)
            titulo = re.sub(r"\*+", "", titulo).strip()
            current_section = {"titulo": titulo, "itens": []}
            continue

        # Linha de tabela markdown
        if "|" in stripped and not stripped.startswith("|-"):
            # Pular header separators
            if re.match(r"^\|[\s\-:|]+\|$", stripped):
                continue
            # Cada linha de tabela vira um item
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            if cells and not all(c == "---" or c == "----" for c in cells):
                texto_tabela = " | ".join(cells)
                if len(texto_tabela) > 5:
                    current_section["itens"].append(texto_tabela)
            continue

        # Linha vazia → flush buffer como parágrafo
        if not stripped:
            if buffer:
                texto = "\n".join(buffer).strip()
                if texto and len(texto) > 5:
                    current_section["itens"].append(texto)
                buffer = []
            continue

        # Separador ---
        if stripped == "---":
            if buffer:
                texto = "\n".join(buffer).strip()
                if texto and len(texto) > 5:
                    current_section["itens"].append(texto)
                buffer = []
            continue

        buffer.append(line)

    # Flush final
    if buffer:
        texto = "\n".join(buffer).strip()
        if texto and len(texto) > 5:
            current_section["itens"].append(texto)
    if current_section["itens"]:
        secoes.append(current_section)

    return secoes


# Padrões para detectar dados verificáveis
PATTERNS = {
    "id_pje": re.compile(r"\b(\d{10,13})\b"),
    "cnj": re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"),
    "data": re.compile(r"\d{1,2}/\d{1,2}/\d{4}"),
    "valor": re.compile(r"R\$\s*[\d.,]+"),
    "artigo": re.compile(r"Art\.?\s*\d+", re.IGNORECASE),
    "oab_crm": re.compile(r"(OAB|CRM)[/\-]?\s*\w{2}\s*[\d.]+", re.IGNORECASE),
    "cid": re.compile(r"\b[A-Z]\d{2}(\.\d{1,2})?\b"),
    "nome_maiusculo": re.compile(r"\b([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,}\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,}(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,})*)\b"),
}


def extrair_dados_verificaveis(texto: str) -> list[dict]:
    """Extrai dados verificáveis de um trecho de texto."""
    dados = []
    seen = set()

    for tipo, pattern in PATTERNS.items():
        for match in pattern.finditer(texto):
            valor = match.group(0).strip()
            if valor not in seen and len(valor) > 2:
                # Filtrar falsos positivos de nomes maiúsculos
                if tipo == "nome_maiusculo":
                    # Ignorar palavras comuns em maiúsculo
                    palavras_comuns = {"DADOS", "PARA", "PROPOSTA", "HONORÁRIOS", "PERICIAIS",
                                       "PROCESSO", "CAMPO", "VALOR", "AUTOR", "RÉUS", "IDENTIFICAÇÃO",
                                       "PARTES", "REPRESENTANTES", "NOMEAÇÃO", "PERICIAL", "DECISÃO",
                                       "OBJETO", "AÇÃO", "SÍNTESE", "FATOS", "LESÕES", "DOCUMENTAIS",
                                       "CLASSIFICAÇÃO", "COMPLEXIDADE", "FATORES", "ESTIMATIVA",
                                       "ATIVIDADES", "SIM", "NÃO", "VERIFICAÇÃO", "OBRIGATÓRIA"}
                    palavras = valor.split()
                    if all(p in palavras_comuns for p in palavras):
                        continue
                    if len(palavras) < 2:
                        continue
                dados.append({"tipo": tipo, "valor": valor, "inicio": match.start(), "fim": match.end()})
                seen.add(valor)

    return dados


def buscar_em_paginas(dado: str, paginas: list[str]) -> list[dict]:
    """Busca um dado nas páginas do texto extraído. Retorna lista de matches com página e contexto."""
    resultados = []
    dado_lower = dado.lower().strip()
    dado_normalizado = re.sub(r"[\s./-]+", "", dado_lower)

    for i, pagina in enumerate(paginas):
        pagina_lower = pagina.lower()
        pagina_normalizada = re.sub(r"[\s./-]+", "", pagina_lower)

        # Busca exata
        pos = pagina_lower.find(dado_lower)
        if pos >= 0:
            inicio = max(0, pos - 150)
            fim = min(len(pagina), pos + len(dado_lower) + 150)
            contexto = pagina[inicio:fim].strip()
            resultados.append({"pagina": i + 1, "contexto": contexto, "tipo_match": "exato"})
            continue

        # Busca normalizada (sem espaços, pontos, hífens)
        if len(dado_normalizado) > 3:
            pos_n = pagina_normalizada.find(dado_normalizado)
            if pos_n >= 0:
                # Estimar posição no texto original
                ratio = pos_n / max(len(pagina_normalizada), 1)
                pos_aprox = int(ratio * len(pagina))
                inicio = max(0, pos_aprox - 150)
                fim = min(len(pagina), pos_aprox + 300)
                contexto = pagina[inicio:fim].strip()
                resultados.append({"pagina": i + 1, "contexto": contexto, "tipo_match": "normalizado"})
                continue

    return resultados


def destacar_dados(texto_html: str, dados: list[dict]) -> str:
    """Destaca dados verificáveis no texto HTML com <mark>."""
    # Ordenar do maior para menor para evitar conflitos de substituição
    dados_sorted = sorted(dados, key=lambda d: len(d["valor"]), reverse=True)
    for dado in dados_sorted:
        valor_esc = escape(dado["valor"])
        if valor_esc in texto_html:
            texto_html = texto_html.replace(
                valor_esc,
                f'<mark class="dado dado-{dado["tipo"]}" data-busca="{escape(dado["valor"])}">{valor_esc}</mark>',
                1  # só primeira ocorrência
            )
    return texto_html


def gerar_html(secoes_processadas: list[dict], pdf_filename: str, peticao_nome: str, cnj: str) -> str:
    """Gera o HTML completo do checklist."""

    total_itens = sum(len(s["itens"]) for s in secoes_processadas)

    # Gerar cards
    cards_html = ""
    item_id = 0

    for secao in secoes_processadas:
        cards_html += f'<div class="secao-header">{escape(secao["titulo"])}</div>\n'

        for item in secao["itens"]:
            item_id += 1
            texto_esc = escape(item["texto"])
            texto_destacado = destacar_dados(texto_esc, item["dados"])

            # Melhor match (primeira página encontrada)
            pagina_info = ""
            contexto_html = ""
            pagina_num = 0

            if item["matches"]:
                melhor = item["matches"][0]
                pagina_num = melhor["pagina"]
                pagina_info = f'<span class="pagina-badge" onclick="irParaPagina({pagina_num})">Página {pagina_num}</span>'
                contexto_esc = escape(melhor["contexto"])
                # Destacar o dado encontrado no contexto
                for d in item["dados"]:
                    if d["valor"].lower() in melhor["contexto"].lower():
                        idx = melhor["contexto"].lower().find(d["valor"].lower())
                        original = melhor["contexto"][idx:idx+len(d["valor"])]
                        contexto_esc = contexto_esc.replace(escape(original), f'<strong class="match-highlight">{escape(original)}</strong>', 1)
                contexto_html = f'''<div class="contexto-box" id="ctx-{item_id}">
                    <div class="contexto-label">Trecho do processo (p.{pagina_num}):</div>
                    <div class="contexto-texto">...{contexto_esc}...</div>
                </div>'''
            else:
                if item["dados"]:
                    pagina_info = '<span class="nao-encontrado">NÃO ENCONTRADO</span>'

            # Indicadores de dados
            dados_tags = ""
            for d in item["dados"]:
                tipo_label = {"id_pje": "ID", "cnj": "CNJ", "data": "Data", "valor": "R$",
                              "artigo": "Lei", "oab_crm": "OAB/CRM", "cid": "CID",
                              "nome_maiusculo": "Nome"}.get(d["tipo"], d["tipo"])
                dados_tags += f'<span class="dado-tag tag-{d["tipo"]}">{tipo_label}</span> '

            onclick_pagina = f'onclick="irParaPagina({pagina_num})"' if pagina_num > 0 else ""

            cards_html += f'''
            <div class="item-card" id="card-{item_id}" data-status="pendente" data-pagina="{pagina_num}">
                <div class="item-header" {onclick_pagina}>
                    <span class="item-num">#{item_id}</span>
                    <div class="item-texto">{texto_destacado}</div>
                </div>
                <div class="item-meta">
                    {dados_tags}
                    {pagina_info}
                </div>
                {contexto_html}
                <div class="item-actions">
                    <button class="btn-status btn-ok" onclick="setStatus({item_id}, 'ok')">✓ OK</button>
                    <button class="btn-status btn-pendente active" onclick="setStatus({item_id}, 'pendente')">? Pendente</button>
                    <button class="btn-status btn-erro" onclick="setStatus({item_id}, 'erro')">✗ Erro</button>
                    <textarea class="nota-campo" id="nota-{item_id}" placeholder="Nota..."
                              oninput="salvarNota({item_id})"></textarea>
                </div>
            </div>\n'''

    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Checklist — {escape(peticao_nome)}</title>
<style>
:root {{
    --cor-ok: #38a169;
    --cor-pendente: #d69e2e;
    --cor-erro: #e53e3e;
    --cor-fundo: #f7fafc;
    --cor-card: #ffffff;
    --cor-borda: #e2e8f0;
    --cor-texto: #2d3748;
    --cor-header: #1a365d;
    --cor-accent: #3182ce;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--cor-fundo); color: var(--cor-texto); height: 100vh; overflow: hidden; }}

/* Header */
.header {{
    background: linear-gradient(135deg, var(--cor-header), #2a4a7f);
    color: white; padding: 12px 20px; display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2); z-index: 100;
}}
.header h1 {{ font-size: 16px; font-weight: 600; }}
.header .info {{ font-size: 12px; opacity: 0.8; }}

/* Progress bar */
.progress-bar {{
    background: #edf2f7; padding: 8px 20px; display: flex; align-items: center; gap: 16px;
    border-bottom: 1px solid var(--cor-borda); position: sticky; top: 0; z-index: 90;
}}
.progress-track {{ flex: 1; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }}
.progress-fill {{ height: 100%; background: var(--cor-ok); transition: width 0.3s; border-radius: 4px; }}
.progress-stats {{ display: flex; gap: 12px; font-size: 12px; font-weight: 600; white-space: nowrap; }}
.stat-ok {{ color: var(--cor-ok); }}
.stat-pendente {{ color: var(--cor-pendente); }}
.stat-erro {{ color: var(--cor-erro); }}

/* Layout principal */
.container {{ display: flex; height: calc(100vh - 90px); }}
.painel-checklist {{ width: 42%; overflow-y: auto; padding: 12px; border-right: 3px solid var(--cor-borda); }}
.painel-pdf {{ width: 58%; display: flex; flex-direction: column; }}
.painel-pdf iframe {{ flex: 1; border: none; }}

/* Seções */
.secao-header {{
    font-size: 13px; font-weight: 700; color: var(--cor-header); text-transform: uppercase;
    padding: 10px 8px 4px; margin-top: 8px; border-bottom: 2px solid var(--cor-accent);
    letter-spacing: 0.5px;
}}

/* Cards */
.item-card {{
    background: var(--cor-card); border-radius: 6px; margin: 6px 0; padding: 10px 12px;
    border-left: 4px solid var(--cor-pendente); box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.item-card[data-status="ok"] {{ border-left-color: var(--cor-ok); }}
.item-card[data-status="pendente"] {{ border-left-color: var(--cor-pendente); }}
.item-card[data-status="erro"] {{ border-left-color: var(--cor-erro); background: #fff5f5; }}

.item-header {{ display: flex; gap: 8px; cursor: pointer; }}
.item-header:hover {{ opacity: 0.8; }}
.item-num {{ font-size: 11px; font-weight: 700; color: var(--cor-accent); min-width: 28px; padding-top: 2px; }}
.item-texto {{ font-size: 13px; line-height: 1.5; flex: 1; }}

.item-meta {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; align-items: center; }}

/* Tags de dados */
.dado-tag {{ font-size: 10px; padding: 1px 6px; border-radius: 3px; font-weight: 600; }}
.tag-id_pje {{ background: #ebf4ff; color: #2b6cb0; }}
.tag-cnj {{ background: #faf5ff; color: #6b46c1; }}
.tag-data {{ background: #fefcbf; color: #975a16; }}
.tag-valor {{ background: #f0fff4; color: #276749; }}
.tag-artigo {{ background: #fed7d7; color: #9b2c2c; }}
.tag-oab_crm {{ background: #e9d8fd; color: #553c9a; }}
.tag-cid {{ background: #bee3f8; color: #2a4365; }}
.tag-nome_maiusculo {{ background: #feebc8; color: #7b341e; }}

.pagina-badge {{
    font-size: 11px; padding: 2px 8px; border-radius: 10px;
    background: var(--cor-accent); color: white; cursor: pointer; font-weight: 600;
}}
.pagina-badge:hover {{ background: #2c5282; }}
.nao-encontrado {{
    font-size: 11px; padding: 2px 8px; border-radius: 10px;
    background: var(--cor-erro); color: white; font-weight: 600;
}}

/* Contexto */
.contexto-box {{
    margin-top: 6px; padding: 8px; background: #f7fafc; border-radius: 4px;
    border: 1px dashed var(--cor-borda); font-size: 12px;
}}
.contexto-label {{ font-weight: 600; color: var(--cor-accent); margin-bottom: 4px; font-size: 11px; }}
.contexto-texto {{ color: #4a5568; line-height: 1.5; white-space: pre-wrap; word-break: break-word; }}
.match-highlight {{ background: #fefcbf; color: #744210; padding: 0 2px; }}

/* Dados destacados na petição */
mark.dado {{ padding: 0 2px; border-radius: 2px; cursor: pointer; }}
mark.dado-id_pje {{ background: #ebf4ff; }}
mark.dado-cnj {{ background: #faf5ff; }}
mark.dado-data {{ background: #fefcbf; }}
mark.dado-valor {{ background: #f0fff4; }}
mark.dado-artigo {{ background: #fed7d7; }}
mark.dado-oab_crm {{ background: #e9d8fd; }}
mark.dado-cid {{ background: #bee3f8; }}
mark.dado-nome_maiusculo {{ background: #feebc8; }}

/* Botões */
.item-actions {{ display: flex; gap: 6px; margin-top: 8px; align-items: center; flex-wrap: wrap; }}
.btn-status {{
    font-size: 11px; padding: 3px 10px; border-radius: 4px; border: 1px solid var(--cor-borda);
    cursor: pointer; font-weight: 600; background: white; transition: all 0.15s;
}}
.btn-ok:hover, .btn-ok.active {{ background: var(--cor-ok); color: white; border-color: var(--cor-ok); }}
.btn-pendente:hover, .btn-pendente.active {{ background: var(--cor-pendente); color: white; border-color: var(--cor-pendente); }}
.btn-erro:hover, .btn-erro.active {{ background: var(--cor-erro); color: white; border-color: var(--cor-erro); }}

.nota-campo {{
    flex: 1; min-width: 120px; font-size: 11px; padding: 4px 8px; border: 1px solid var(--cor-borda);
    border-radius: 4px; resize: vertical; min-height: 24px; max-height: 80px;
    font-family: inherit;
}}
.nota-campo:focus {{ border-color: var(--cor-accent); outline: none; }}

/* Filtros */
.filtros {{
    padding: 6px 20px; background: white; border-bottom: 1px solid var(--cor-borda);
    display: flex; gap: 8px; align-items: center;
}}
.filtro-btn {{
    font-size: 11px; padding: 3px 10px; border-radius: 12px; border: 1px solid var(--cor-borda);
    cursor: pointer; background: white; transition: all 0.15s;
}}
.filtro-btn.active {{ background: var(--cor-header); color: white; border-color: var(--cor-header); }}
.filtro-btn:hover {{ background: #edf2f7; }}
.filtro-btn.active:hover {{ background: var(--cor-header); }}
.busca-input {{
    margin-left: auto; font-size: 12px; padding: 4px 10px; border: 1px solid var(--cor-borda);
    border-radius: 4px; width: 180px;
}}

/* Print */
@media print {{
    .painel-pdf, .filtros, .btn-status, .nota-campo {{ display: none !important; }}
    .painel-checklist {{ width: 100% !important; overflow: visible !important; }}
    .item-card {{ break-inside: avoid; }}
}}
</style>
</head>
<body>

<div class="header">
    <div>
        <h1>Checklist — {escape(peticao_nome)}</h1>
        <div class="info">{escape(cnj)} · Gerado em {datetime.now().strftime("%d/%m/%Y %H:%M")}</div>
    </div>
    <div class="info">{total_itens} itens para conferir</div>
</div>

<div class="filtros">
    <button class="filtro-btn active" onclick="filtrar('todos')">Todos ({total_itens})</button>
    <button class="filtro-btn" onclick="filtrar('ok')" id="filtro-ok">✓ OK (<span id="count-ok">0</span>)</button>
    <button class="filtro-btn" onclick="filtrar('pendente')" id="filtro-pendente">? Pendente (<span id="count-pendente">{total_itens}</span>)</button>
    <button class="filtro-btn" onclick="filtrar('erro')" id="filtro-erro">✗ Erro (<span id="count-erro">0</span>)</button>
    <input type="text" class="busca-input" placeholder="Buscar no checklist..." oninput="buscar(this.value)">
</div>

<div class="progress-bar">
    <div class="progress-track"><div class="progress-fill" id="progress-fill" style="width: 0%"></div></div>
    <div class="progress-stats">
        <span class="stat-ok" id="stat-ok">0 OK</span>
        <span class="stat-pendente" id="stat-pendente">{total_itens} pendente</span>
        <span class="stat-erro" id="stat-erro">0 erro</span>
    </div>
</div>

<div class="container">
    <div class="painel-checklist" id="checklist">
        {cards_html}
    </div>
    <div class="painel-pdf">
        <iframe id="pdf-viewer" src="{escape(pdf_filename)}#page=1"></iframe>
    </div>
</div>

<script>
const STORAGE_KEY = "checklist-{escape(peticao_nome.replace('"', ''))}";
const TOTAL = {total_itens};
let estados = {{}};
let notas = {{}};

// Carregar do localStorage
function carregar() {{
    try {{
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {{
            const data = JSON.parse(saved);
            estados = data.estados || {{}};
            notas = data.notas || {{}};
            // Aplicar estados salvos
            for (const [id, status] of Object.entries(estados)) {{
                const card = document.getElementById("card-" + id);
                if (card) {{
                    card.dataset.status = status;
                    // Atualizar botões
                    card.querySelectorAll(".btn-status").forEach(b => b.classList.remove("active"));
                    const btn = card.querySelector(".btn-" + status);
                    if (btn) btn.classList.add("active");
                }}
            }}
            // Aplicar notas
            for (const [id, nota] of Object.entries(notas)) {{
                const el = document.getElementById("nota-" + id);
                if (el) el.value = nota;
            }}
        }}
    }} catch(e) {{}}
    atualizarProgresso();
}}

function salvar() {{
    try {{
        localStorage.setItem(STORAGE_KEY, JSON.stringify({{ estados, notas }}));
    }} catch(e) {{}}
}}

function setStatus(id, status) {{
    estados[id] = status;
    const card = document.getElementById("card-" + id);
    if (card) {{
        card.dataset.status = status;
        card.querySelectorAll(".btn-status").forEach(b => b.classList.remove("active"));
        const btn = card.querySelector(".btn-" + status);
        if (btn) btn.classList.add("active");
    }}
    salvar();
    atualizarProgresso();
}}

function salvarNota(id) {{
    const el = document.getElementById("nota-" + id);
    if (el) {{
        notas[id] = el.value;
        salvar();
    }}
}}

function irParaPagina(pagina) {{
    const viewer = document.getElementById("pdf-viewer");
    const src = viewer.src.split("#")[0];
    viewer.src = src + "#page=" + pagina;
}}

function atualizarProgresso() {{
    let ok = 0, pendente = 0, erro = 0;
    for (let i = 1; i <= TOTAL; i++) {{
        const s = estados[i] || "pendente";
        if (s === "ok") ok++;
        else if (s === "erro") erro++;
        else pendente++;
    }}
    const pct = TOTAL > 0 ? Math.round((ok / TOTAL) * 100) : 0;
    document.getElementById("progress-fill").style.width = pct + "%";
    document.getElementById("stat-ok").textContent = ok + " OK";
    document.getElementById("stat-pendente").textContent = pendente + " pendente";
    document.getElementById("stat-erro").textContent = erro + " erro";
    document.getElementById("count-ok").textContent = ok;
    document.getElementById("count-pendente").textContent = pendente;
    document.getElementById("count-erro").textContent = erro;
}}

function filtrar(status) {{
    document.querySelectorAll(".filtro-btn").forEach(b => b.classList.remove("active"));
    if (status === "todos") {{
        document.querySelector('.filtro-btn').classList.add("active");
    }} else {{
        document.getElementById("filtro-" + status).classList.add("active");
    }}
    document.querySelectorAll(".item-card").forEach(card => {{
        if (status === "todos") {{
            card.style.display = "";
        }} else {{
            card.style.display = card.dataset.status === status ? "" : "none";
        }}
    }});
}}

function buscar(termo) {{
    const lower = termo.toLowerCase();
    document.querySelectorAll(".item-card").forEach(card => {{
        if (!termo) {{
            card.style.display = "";
        }} else {{
            const texto = card.textContent.toLowerCase();
            card.style.display = texto.includes(lower) ? "" : "none";
        }}
    }});
}}

// Click em mark → navegar para página
document.addEventListener("click", function(e) {{
    if (e.target.tagName === "MARK" && e.target.dataset.busca) {{
        const card = e.target.closest(".item-card");
        if (card && card.dataset.pagina > 0) {{
            irParaPagina(parseInt(card.dataset.pagina));
        }}
    }}
}});

// Inicializar
carregar();
</script>
</body>
</html>'''

    return html


def main():
    parser = argparse.ArgumentParser(description="Gera checklist interativo: Petição vs PDF do Processo")
    parser.add_argument("--peticao", required=True, help="Arquivo .md da petição")
    parser.add_argument("--pdf", required=True, help="PDF do processo")
    parser.add_argument("--output", help="Arquivo HTML de saída (padrão: CHECKLIST-[nome].html)")
    args = parser.parse_args()

    if not os.path.exists(args.peticao):
        print(f"Erro: petição não encontrada: {args.peticao}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(args.pdf):
        print(f"Erro: PDF não encontrado: {args.pdf}", file=sys.stderr)
        sys.exit(1)

    peticao_nome = os.path.splitext(os.path.basename(args.peticao))[0]
    pdf_filename = os.path.basename(args.pdf)

    # Detectar CNJ no nome da pasta ou no arquivo
    cnj_match = re.search(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", os.path.abspath(args.peticao))
    cnj = cnj_match.group(0) if cnj_match else "Sem CNJ"

    # Saída padrão na mesma pasta da petição
    if not args.output:
        pasta = os.path.dirname(os.path.abspath(args.peticao))
        args.output = os.path.join(pasta, f"CHECKLIST-{peticao_nome}.html")

    print(f"Extraindo texto do PDF ({pdf_filename})...")
    paginas = extrair_texto_por_pagina(args.pdf)
    print(f"  {len(paginas)} páginas extraídas")

    print(f"Lendo petição ({peticao_nome})...")
    secoes = parse_peticao(args.peticao)

    total_itens = sum(len(s["itens"]) for s in secoes)
    print(f"  {len(secoes)} seções, {total_itens} itens")

    print("Buscando dados verificáveis nas páginas do processo...")
    secoes_processadas = []
    total_matches = 0
    total_dados = 0

    for secao in secoes:
        secao_proc = {"titulo": secao["titulo"], "itens": []}
        for texto in secao["itens"]:
            dados = extrair_dados_verificaveis(texto)
            total_dados += len(dados)

            # Buscar cada dado nas páginas
            matches = []
            for dado in dados:
                resultados = buscar_em_paginas(dado["valor"], paginas)
                if resultados:
                    matches.extend(resultados)
                    total_matches += 1

            # Deduplica por página (manter o primeiro match por página)
            seen_pages = set()
            matches_unicos = []
            for m in matches:
                if m["pagina"] not in seen_pages:
                    seen_pages.add(m["pagina"])
                    matches_unicos.append(m)

            secao_proc["itens"].append({
                "texto": texto,
                "dados": dados,
                "matches": matches_unicos
            })
        secoes_processadas.append(secao_proc)

    print(f"  {total_dados} dados verificáveis encontrados")
    print(f"  {total_matches} dados localizados no processo")

    print("Gerando HTML...")
    html = gerar_html(secoes_processadas, pdf_filename, peticao_nome, cnj)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nCHECKLIST GERADO")
    print(f"  Arquivo: {args.output}")
    print(f"  Itens: {total_itens}")
    print(f"  Dados verificáveis: {total_dados}")
    print(f"  Localizados no processo: {total_matches}")
    print(f"\n  IMPORTANTE: O HTML e o PDF devem estar na mesma pasta para funcionar.")


if __name__ == "__main__":
    main()
