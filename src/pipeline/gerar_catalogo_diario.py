#!/usr/bin/env python3
"""
Catálogo Diário de Criações — Stemmia Forense
Escaneia criações do dia (agentes, skills, scripts, sites, documentos)
e gera PDF com: nome, data, explicação técnica + leiga, onde encontrar.

Uso:
    python3 gerar_catalogo_diario.py              # Criações de hoje
    python3 gerar_catalogo_diario.py --data 2026-03-04  # Data específica
    python3 gerar_catalogo_diario.py --dias 7      # Últimos 7 dias

Saída: ~/Desktop/CATALOGO-CRIACOES-DIARIO.html (abre no navegador para imprimir como PDF)
"""

import os
import sys
import json
import datetime

# === CONFIGURAÇÃO ===

DIRETORIOS_ESCANEADOS = [
    {
        "caminho": os.path.expanduser("~/.claude/agents/"),
        "tipo": "Agente",
        "icone": "🤖",
        "explicacao_leiga": "Robô que faz tarefas específicas automaticamente"
    },
    {
        "caminho": os.path.expanduser("~/.claude/plugins/stemmia-forense/skills/"),
        "tipo": "Skill",
        "icone": "⚡",
        "explicacao_leiga": "Comando com / que executa algo específico"
    },
    {
        "caminho": os.path.expanduser("~/Desktop/ANALISADOR FINAL/scripts/"),
        "tipo": "Script",
        "icone": "📜",
        "explicacao_leiga": "Programa que roda no terminal"
    },
    {
        "caminho": os.path.expanduser("~/Desktop/ANALISADOR FINAL/hooks/"),
        "tipo": "Hook",
        "icone": "🪝",
        "explicacao_leiga": "Gancho que roda automaticamente antes/depois de ações"
    },
    {
        "caminho": os.path.expanduser("~/Sites/webdev/teste/"),
        "tipo": "Site",
        "icone": "🌐",
        "explicacao_leiga": "Site de cliente ou projeto web"
    },
    {
        "caminho": os.path.expanduser("~/Desktop/"),
        "tipo": "Documento",
        "icone": "📄",
        "explicacao_leiga": "Documento criado na mesa",
        "extensoes": [".md", ".html", ".pdf", ".txt"],
        "profundidade": 1
    },
    {
        "caminho": os.path.expanduser("~/Desktop/ANALISADOR FINAL/modelos-laudo/"),
        "tipo": "Modelo de Laudo",
        "icone": "📋",
        "explicacao_leiga": "Template para laudos periciais"
    },
    {
        "caminho": os.path.expanduser("~/Desktop/ANALISADOR FINAL/prompts/"),
        "tipo": "Prompt",
        "icone": "💬",
        "explicacao_leiga": "Instrução reutilizável para o Claude"
    },
]

SAIDA = os.path.expanduser("~/Desktop/CATALOGO-CRIACOES-DIARIO.html")


def obter_data_alvo(args):
    """Determina a data-alvo com base nos argumentos."""
    if "--data" in args:
        idx = args.index("--data")
        return datetime.datetime.strptime(args[idx + 1], "%Y-%m-%d").date(), 1
    elif "--dias" in args:
        idx = args.index("--dias")
        dias = int(args[idx + 1])
        return datetime.date.today() - datetime.timedelta(days=dias - 1), dias
    else:
        return datetime.date.today(), 1


def escanear_diretorio(config, data_inicio, dias):
    """Escaneia um diretório e retorna arquivos criados/modificados no período."""
    caminho = config["caminho"]
    if not os.path.exists(caminho):
        return []

    resultados = []
    profundidade = config.get("profundidade", 10)
    extensoes = config.get("extensoes", None)

    for raiz, dirs, arquivos in os.walk(caminho):
        # Controlar profundidade
        nivel = raiz.replace(caminho, "").count(os.sep)
        if nivel >= profundidade:
            dirs.clear()
            continue

        # Ignorar pastas ocultas e de backup
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in [
            "analisador de processos", "Analisa Processual Completa",
            "__pycache__", "node_modules", ".git"
        ]]

        for arquivo in arquivos:
            if arquivo.startswith("."):
                continue

            if extensoes and not any(arquivo.endswith(ext) for ext in extensoes):
                continue

            caminho_completo = os.path.join(raiz, arquivo)
            try:
                stat = os.stat(caminho_completo)
                mtime = datetime.date.fromtimestamp(stat.st_mtime)
                ctime = datetime.date.fromtimestamp(stat.st_birthtime) if hasattr(stat, "st_birthtime") else mtime

                data_ref = max(mtime, ctime)
                data_limite = data_inicio

                if data_ref >= data_limite:
                    tamanho = stat.st_size
                    resultados.append({
                        "nome": arquivo,
                        "caminho": caminho_completo,
                        "tipo": config["tipo"],
                        "icone": config["icone"],
                        "explicacao_leiga": config["explicacao_leiga"],
                        "data_modificacao": mtime.isoformat(),
                        "data_criacao": ctime.isoformat() if hasattr(stat, "st_birthtime") else "N/D",
                        "tamanho": tamanho,
                        "tamanho_legivel": formatar_tamanho(tamanho),
                    })
            except (OSError, ValueError):
                continue

    return resultados


def formatar_tamanho(bytes_val):
    """Formata bytes para leitura humana."""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB"
    else:
        return f"{bytes_val / (1024 * 1024):.1f} MB"


def extrair_descricao(caminho):
    """Tenta extrair uma descrição do arquivo (primeira linha, frontmatter, etc.)."""
    try:
        with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
            linhas = f.readlines()[:20]

        # YAML frontmatter — buscar description
        if linhas and linhas[0].strip() == "---":
            for linha in linhas[1:]:
                if linha.strip() == "---":
                    break
                if linha.strip().startswith("description:"):
                    return linha.split(":", 1)[1].strip().strip('"').strip("'")

        # Markdown — primeira linha que não seja # ou vazia
        for linha in linhas:
            texto = linha.strip()
            if texto.startswith("#"):
                return texto.lstrip("#").strip()
            if texto.startswith(">"):
                return texto.lstrip(">").strip()
            if texto and not texto.startswith("---") and not texto.startswith("```"):
                return texto[:120]

        return "(sem descrição)"
    except Exception:
        return "(não legível)"


def gerar_html(resultados, data_inicio, dias):
    """Gera o HTML do catálogo."""
    hoje = datetime.date.today().isoformat()

    if dias == 1:
        titulo_periodo = f"Criações de {data_inicio.isoformat()}"
    else:
        titulo_periodo = f"Criações dos últimos {dias} dias (desde {data_inicio.isoformat()})"

    # Agrupar por tipo
    por_tipo = {}
    for r in resultados:
        tipo = r["tipo"]
        if tipo not in por_tipo:
            por_tipo[tipo] = []
        por_tipo[tipo].append(r)

    # Ordenar cada grupo por data
    for tipo in por_tipo:
        por_tipo[tipo].sort(key=lambda x: x["data_modificacao"], reverse=True)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo de Criações — {hoje}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #1a1a1a;
            background: #f5f5f5;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .header h1 {{ font-size: 24px; color: #1565C0; }}
        .header p {{ color: #666; margin-top: 5px; }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        .stat {{
            background: #E3F2FD;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 600;
        }}
        .tipo-grupo {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .tipo-header {{
            background: #1565C0;
            color: white;
            padding: 12px 20px;
            font-size: 18px;
            font-weight: 600;
        }}
        .item {{
            padding: 12px 20px;
            border-bottom: 1px solid #eee;
            display: flex;
            gap: 15px;
            align-items: flex-start;
        }}
        .item:last-child {{ border-bottom: none; }}
        .item-icone {{ font-size: 24px; flex-shrink: 0; margin-top: 2px; }}
        .item-info {{ flex: 1; }}
        .item-nome {{ font-weight: 600; font-size: 15px; color: #1565C0; }}
        .item-desc {{ color: #555; margin-top: 2px; }}
        .item-meta {{ color: #999; font-size: 12px; margin-top: 4px; }}
        .item-caminho {{
            font-family: monospace;
            font-size: 11px;
            color: #888;
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 4px;
            display: inline-block;
            margin-top: 4px;
        }}
        .footer {{
            text-align: center;
            color: #999;
            padding: 20px;
            font-size: 12px;
        }}
        .vazio {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 16px;
        }}
        @media print {{
            body {{ background: white; padding: 0; }}
            .tipo-grupo {{ box-shadow: none; border: 1px solid #ddd; }}
            .header {{ box-shadow: none; border: 1px solid #ddd; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📦 Catálogo de Criações</h1>
        <p>{titulo_periodo}</p>
        <div class="stats">
            <div class="stat">📊 Total: {len(resultados)} itens</div>
"""

    for tipo, itens in por_tipo.items():
        icone = itens[0]["icone"] if itens else ""
        html += f'            <div class="stat">{icone} {tipo}: {len(itens)}</div>\n'

    html += """        </div>
    </div>
"""

    if not resultados:
        html += '    <div class="vazio">Nenhuma criação encontrada no período.</div>\n'
    else:
        for tipo, itens in sorted(por_tipo.items()):
            icone = itens[0]["icone"]
            leiga = itens[0]["explicacao_leiga"]
            html += f"""
    <div class="tipo-grupo">
        <div class="tipo-header">{icone} {tipo} — <span style="font-weight:normal; font-size:14px;">{leiga}</span></div>
"""
            for item in itens:
                desc = extrair_descricao(item["caminho"])
                caminho_curto = item["caminho"].replace(os.path.expanduser("~"), "~")
                html += f"""        <div class="item">
            <div class="item-icone">{item['icone']}</div>
            <div class="item-info">
                <div class="item-nome">{item['nome']}</div>
                <div class="item-desc">{desc}</div>
                <div class="item-meta">Modificado: {item['data_modificacao']} | Tamanho: {item['tamanho_legivel']}</div>
                <div class="item-caminho">{caminho_curto}</div>
            </div>
        </div>
"""
            html += "    </div>\n"

    html += f"""
    <div class="footer">
        <p>Gerado automaticamente por gerar_catalogo_diario.py — Stemmia Forense</p>
        <p>{hoje}</p>
    </div>
</body>
</html>"""

    return html


def main():
    args = sys.argv[1:]
    data_inicio, dias = obter_data_alvo(args)

    print(f"🔍 Escaneando criações desde {data_inicio.isoformat()} ({dias} dia(s))...")

    todos_resultados = []
    for config in DIRETORIOS_ESCANEADOS:
        resultados = escanear_diretorio(config, data_inicio, dias)
        todos_resultados.extend(resultados)
        if resultados:
            print(f"  {config['icone']} {config['tipo']}: {len(resultados)} itens")

    print(f"\n📊 Total: {len(todos_resultados)} criações encontradas")

    html = gerar_html(todos_resultados, data_inicio, dias)

    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Catálogo salvo em: {SAIDA}")

    # Também gerar JSON para integração
    json_saida = SAIDA.replace(".html", ".json")
    with open(json_saida, "w", encoding="utf-8") as f:
        json.dump({
            "data_geracao": datetime.date.today().isoformat(),
            "periodo_inicio": data_inicio.isoformat(),
            "dias": dias,
            "total": len(todos_resultados),
            "itens": todos_resultados
        }, f, ensure_ascii=False, indent=2)

    print(f"📋 JSON salvo em: {json_saida}")


if __name__ == "__main__":
    main()
