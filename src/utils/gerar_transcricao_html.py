#!/usr/bin/env python3
"""
GERADOR DE TRANSCRIÇÃO HTML EDITÁVEL
=====================================
Converte um arquivo .jsonl do Claude Code em HTML editável no navegador.

USO:
    python3 gerar_transcricao_html.py --jsonl-file ARQUIVO.jsonl --saida PASTA/
    python3 gerar_transcricao_html.py --sessao UUID --saida PASTA/

SAÍDA:
    TRANSCRICAO-EDITAVEL.html na pasta de saída

RECURSOS:
    - Mensagens formatadas com cores (azul=usuário, cinza=Claude)
    - Ferramentas usadas em collapsible <details>
    - contenteditable="true" nas mensagens (editável no navegador)
    - Botão "Salvar como TXT" (JS puro, sem servidor)
    - Busca por texto customizada
"""

import json
import os
import sys
from datetime import datetime
from html import escape

JSONL_DIR = os.path.expanduser("~/.claude/projects/-Users-jesusnoleto")


def extrair_texto_content(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        partes = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    partes.append(item.get("text", ""))
            elif isinstance(item, str):
                partes.append(item)
        return "\n".join(partes)
    return ""


def extrair_tool_use(item):
    nome = item.get("name", "?")
    inp = item.get("input", {})
    if nome in ("Read", "Write", "Edit"):
        return f"{nome}: {inp.get('file_path', '?')}"
    elif nome == "Bash":
        cmd = inp.get("command", "?")
        desc = inp.get("description", "")
        if desc:
            return f"Bash ({desc}): {cmd[:500]}"
        return f"Bash: {cmd[:500]}"
    elif nome in ("Grep", "Glob"):
        return f"{nome}: {inp.get('pattern', '?')}"
    elif nome == "WebFetch":
        return f"WebFetch: {inp.get('url', '?')}"
    elif nome == "WebSearch":
        return f"WebSearch: {inp.get('query', '?')}"
    elif nome == "Task":
        return f"Task ({inp.get('subagent_type', '?')}): {inp.get('prompt', '?')[:200]}"
    else:
        chaves = list(inp.keys())[:3]
        resumo = ", ".join(f"{k}={str(inp[k])[:80]}" for k in chaves)
        return f"{nome}: {resumo}"


def _extrair_hora(timestamp):
    if not timestamp:
        return "--:--"
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except (ValueError, TypeError):
        return "--:--"


def processar_jsonl(jsonl_path):
    mensagens = []
    meta = {"modelo": "?", "sessao": "?", "slug": "?", "cwd": "?", "version": "?"}
    primeira_data = None
    ultima_data = None

    with open(jsonl_path, "r", encoding="utf-8", errors="replace") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            try:
                obj = json.loads(linha)
            except json.JSONDecodeError:
                continue

            tipo = obj.get("type", "")
            timestamp = obj.get("timestamp", "")

            if obj.get("sessionId") and meta["sessao"] == "?":
                meta["sessao"] = obj["sessionId"]
            if obj.get("slug") and meta["slug"] == "?":
                meta["slug"] = obj["slug"]
            if obj.get("cwd") and meta["cwd"] == "?":
                meta["cwd"] = obj["cwd"]
            if obj.get("version") and meta["version"] == "?":
                meta["version"] = obj["version"]

            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    if primeira_data is None:
                        primeira_data = dt
                    ultima_data = dt
                except (ValueError, TypeError):
                    pass

            if tipo == "user":
                msg = obj.get("message", {})
                texto = extrair_texto_content(msg.get("content", ""))
                if texto:
                    hora = _extrair_hora(timestamp)
                    mensagens.append(("user", hora, texto, []))

            elif tipo == "assistant":
                msg = obj.get("message", {})
                modelo = msg.get("model", "")
                if modelo:
                    meta["modelo"] = modelo

                content = msg.get("content", [])
                if isinstance(content, list):
                    hora = _extrair_hora(timestamp)
                    textos = []
                    tools = []
                    for item in content:
                        if not isinstance(item, dict):
                            continue
                        ct = item.get("type", "")
                        if ct == "text":
                            texto = item.get("text", "")
                            if texto:
                                textos.append(texto)
                        elif ct == "tool_use":
                            tools.append(extrair_tool_use(item))

                    if textos or tools:
                        mensagens.append(("assistant", hora, "\n".join(textos), tools))

    return mensagens, meta, primeira_data, ultima_data


def gerar_html(mensagens, meta, primeira_data, ultima_data, jsonl_path, saida_dir):
    slug = meta["slug"] if meta["slug"] != "?" else meta["sessao"][:12]
    data_str = primeira_data.strftime("%Y-%m-%d") if primeira_data else "sem-data"
    nome_arquivo = f"TRANSCRICAO-EDITAVEL-{slug}-{data_str}.html"
    caminho_saida = os.path.join(saida_dir, nome_arquivo)

    total_user = sum(1 for m in mensagens if m[0] == "user")
    total_assistant = sum(1 for m in mensagens if m[0] == "assistant")
    total_tools = sum(len(m[3]) for m in mensagens)

    inicio_str = primeira_data.strftime("%d/%m/%Y %H:%M") if primeira_data else "?"
    fim_str = ultima_data.strftime("%d/%m/%Y %H:%M") if ultima_data else "?"

    msgs_html = []
    for tipo, hora, texto, tools in mensagens:
        texto_escaped = escape(texto).replace("\n", "<br>")

        if tipo == "user":
            msgs_html.append(f'''
        <div class="msg msg-user">
            <div class="msg-header">
                <span class="msg-label label-user">USUÁRIO</span>
                <span class="msg-hora">{hora}</span>
            </div>
            <div class="msg-body" contenteditable="true">{texto_escaped}</div>
        </div>''')
        else:
            tools_html = ""
            if tools:
                tools_items = "".join(f"<li>{escape(t)}</li>" for t in tools)
                tools_html = f'''
                <details class="tools-details">
                    <summary>Ferramentas usadas ({len(tools)})</summary>
                    <ul>{tools_items}</ul>
                </details>'''

            msgs_html.append(f'''
        <div class="msg msg-claude">
            <div class="msg-header">
                <span class="msg-label label-claude">CLAUDE</span>
                <span class="msg-hora">{hora}</span>
            </div>
            <div class="msg-body" contenteditable="true">{texto_escaped}</div>
            {tools_html}
        </div>''')

    mensagens_html = "\n".join(msgs_html)

    # Nota: todo conteúdo inserido no HTML é previamente sanitizado com html.escape()
    # A busca usa textContent para comparação e marca resultados com classe CSS
    html_content = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transcrição — {escape(slug)}</title>
    <style>
        :root {{
            --azul: #2563eb;
            --azul-claro: #eff6ff;
            --cinza: #4b5563;
            --cinza-claro: #f3f4f6;
            --verde: #059669;
            --borda: #e5e7eb;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            font-size: 15px;
            line-height: 1.6;
            color: #1f2937;
            background: #fff;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            border-bottom: 3px solid var(--azul);
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .header h1 {{ font-size: 22px; color: var(--azul); }}
        .meta {{ font-size: 13px; color: var(--cinza); margin-top: 8px; }}
        .meta span {{ margin-right: 20px; }}
        .toolbar {{
            position: sticky;
            top: 0;
            background: #fff;
            padding: 10px 0;
            border-bottom: 1px solid var(--borda);
            margin-bottom: 20px;
            z-index: 100;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .toolbar input {{
            flex: 1;
            padding: 8px 12px;
            border: 2px solid var(--borda);
            border-radius: 6px;
            font-size: 14px;
            outline: none;
        }}
        .toolbar input:focus {{ border-color: var(--azul); }}
        .toolbar button {{
            padding: 8px 16px;
            background: var(--azul);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            white-space: nowrap;
        }}
        .toolbar button:hover {{ opacity: 0.9; }}
        .toolbar button.btn-verde {{ background: var(--verde); }}
        .msg {{
            margin-bottom: 16px;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--borda);
        }}
        .msg-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 12px;
            font-size: 12px;
        }}
        .msg-user .msg-header {{ background: var(--azul-claro); }}
        .msg-claude .msg-header {{ background: var(--cinza-claro); }}
        .msg-label {{ font-weight: 700; font-size: 11px; letter-spacing: 0.5px; }}
        .label-user {{ color: var(--azul); }}
        .label-claude {{ color: var(--cinza); }}
        .msg-hora {{ color: #9ca3af; font-size: 11px; }}
        .msg-body {{
            padding: 12px 16px;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 14px;
            line-height: 1.6;
            min-height: 20px;
        }}
        .msg-body:focus {{
            outline: 2px solid var(--azul);
            outline-offset: -2px;
            background: #fefce8;
        }}
        .tools-details {{
            border-top: 1px solid var(--borda);
            padding: 8px 16px;
            font-size: 12px;
            color: var(--cinza);
        }}
        .tools-details summary {{
            cursor: pointer;
            font-weight: 600;
        }}
        .tools-details ul {{
            margin-top: 6px;
            padding-left: 20px;
        }}
        .tools-details li {{
            font-family: monospace;
            font-size: 11px;
            margin-bottom: 3px;
            word-break: break-all;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid var(--borda);
            text-align: center;
            font-size: 12px;
            color: var(--cinza);
        }}
        .search-match {{ background: #fef08a; }}
        @media print {{
            .toolbar {{ display: none; }}
            .msg-body {{ outline: none !important; background: none !important; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Transcrição de Sessão Claude Code</h1>
        <div class="meta">
            <span>Sessão: {escape(meta["sessao"][:12])}</span>
            <span>Modelo: {escape(meta["modelo"])}</span>
            <span>Início: {inicio_str}</span>
            <span>Fim: {fim_str}</span>
        </div>
        <div class="meta">
            <span>Mensagens: {total_user} do usuário, {total_assistant} do Claude</span>
            <span>Ferramentas: {total_tools}</span>
        </div>
    </div>

    <div class="toolbar">
        <input type="text" id="busca" placeholder="Buscar na transcrição...">
        <button id="btnBuscar">Buscar</button>
        <button class="btn-verde" id="btnSalvar">Salvar como TXT</button>
    </div>

    <div id="mensagens">
{mensagens_html}
    </div>

    <div class="footer">
        <p>Gerado em {datetime.now().strftime("%d/%m/%Y %H:%M")} — Fonte: {escape(os.path.basename(jsonl_path))}</p>
        <p>As mensagens são editáveis — clique para editar. Use "Salvar como TXT" para exportar.</p>
    </div>

    <script>
        // Busca usa TreeWalker para percorrer nós de texto (sem innerHTML)
        document.getElementById('btnBuscar').addEventListener('click', function() {{
            buscar();
        }});
        document.getElementById('busca').addEventListener('keydown', function(e) {{
            if (e.key === 'Enter') buscar();
        }});
        document.getElementById('btnSalvar').addEventListener('click', function() {{
            salvarTXT();
        }});

        function buscar() {{
            // Remove marcações anteriores
            document.querySelectorAll('.search-match').forEach(function(el) {{
                var parent = el.parentNode;
                parent.replaceChild(document.createTextNode(el.textContent), el);
                parent.normalize();
            }});

            var termo = document.getElementById('busca').value.trim().toLowerCase();
            if (!termo) return;

            var msgs = document.querySelectorAll('.msg-body');
            var primeiro = true;
            msgs.forEach(function(msg) {{
                var walker = document.createTreeWalker(msg, NodeFilter.SHOW_TEXT, null, false);
                var nodesToProcess = [];
                while (walker.nextNode()) {{
                    nodesToProcess.push(walker.currentNode);
                }}
                nodesToProcess.forEach(function(node) {{
                    var text = node.textContent;
                    var lower = text.toLowerCase();
                    var idx = lower.indexOf(termo);
                    if (idx === -1) return;
                    var frag = document.createDocumentFragment();
                    var lastIdx = 0;
                    while (idx !== -1) {{
                        frag.appendChild(document.createTextNode(text.substring(lastIdx, idx)));
                        var span = document.createElement('span');
                        span.className = 'search-match';
                        span.textContent = text.substring(idx, idx + termo.length);
                        frag.appendChild(span);
                        if (primeiro) {{
                            span.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                            primeiro = false;
                        }}
                        lastIdx = idx + termo.length;
                        idx = lower.indexOf(termo, lastIdx);
                    }}
                    frag.appendChild(document.createTextNode(text.substring(lastIdx)));
                    node.parentNode.replaceChild(frag, node);
                }});
            }});
        }}

        function salvarTXT() {{
            var msgs = document.querySelectorAll('.msg');
            var linhas = ['TRANSCRIÇÃO DE SESSÃO CLAUDE CODE', '='.repeat(80), ''];
            msgs.forEach(function(msg) {{
                var label = msg.querySelector('.msg-label').textContent;
                var hora = msg.querySelector('.msg-hora').textContent;
                var body = msg.querySelector('.msg-body').textContent;
                linhas.push('[' + hora + '] ── ' + label + ' ──');
                linhas.push(body);
                linhas.push('');
            }});
            var texto = linhas.join('\\n');
            var blob = new Blob([texto], {{ type: 'text/plain;charset=utf-8' }});
            var url = URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = 'TRANSCRICAO-EDITADA.txt';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
    </script>
</body>
</html>'''

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(html_content)

    return caminho_saida


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gera transcrição HTML editável de sessão Claude Code")
    parser.add_argument("--sessao", help="UUID da sessão")
    parser.add_argument("--jsonl-file", help="Caminho direto para o .jsonl")
    parser.add_argument("--saida", default=os.path.expanduser("~/Desktop"), help="Pasta de saída")
    args = parser.parse_args()

    saida_dir = args.saida
    os.makedirs(saida_dir, exist_ok=True)

    if args.jsonl_file:
        jsonl_path = args.jsonl_file
    elif args.sessao:
        jsonl_path = os.path.join(JSONL_DIR, f"{args.sessao}.jsonl")
    else:
        print("Uso: --jsonl-file ARQUIVO ou --sessao UUID")
        sys.exit(1)

    if not os.path.isfile(jsonl_path):
        print(f"Arquivo não encontrado: {jsonl_path}")
        sys.exit(1)

    print(f"Processando: {jsonl_path}")
    mensagens, meta, primeira_data, ultima_data = processar_jsonl(jsonl_path)

    if not mensagens:
        print("Nenhuma mensagem encontrada.")
        sys.exit(1)

    caminho = gerar_html(mensagens, meta, primeira_data, ultima_data, jsonl_path, saida_dir)
    print(f"HTML gerado: {caminho}")
    print(f"Mensagens: {sum(1 for m in mensagens if m[0] == 'user')} do usuário, {sum(1 for m in mensagens if m[0] == 'assistant')} do Claude")


if __name__ == "__main__":
    main()
