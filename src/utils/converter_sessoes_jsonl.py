#!/usr/bin/env python3
"""
CONVERSOR DE SESSÕES JSONL → TEXTO LEGÍVEL
===========================================
Converte os arquivos .jsonl do Claude Code em transcrições legíveis.

USO:
    python3 converter_sessoes_jsonl.py                    # Converte todas as sessões
    python3 converter_sessoes_jsonl.py --sessao UUID      # Converte uma sessão específica
    python3 converter_sessoes_jsonl.py --ultimas 10       # Converte as 10 mais recentes
    python3 converter_sessoes_jsonl.py --saida /caminho   # Define pasta de saída

SAÍDA:
    ~/Desktop/TRANSCRICOES-SESSOES/SESSAO-[slug]-[data].txt

FORMATO DE CADA ARQUIVO:
    Cabeçalho com metadados (sessão, modelo, data)
    Mensagens do usuário e do Claude em ordem cronológica
    Ações do Claude (ferramentas usadas, arquivos editados, comandos)

REPLICAÇÃO:
    1. Precisa de Python 3.8+
    2. Os .jsonl ficam em ~/.claude/projects/-Users-[usuario]/
    3. Cada linha do .jsonl é um objeto JSON com type, message, timestamp
    4. Tipos relevantes: "user" (mensagem do usuário), "assistant" (resposta do Claude)
    5. Mensagens do assistant têm content[] com type: text, tool_use, thinking
"""

import json
import os
import sys
import glob
from datetime import datetime

# Configuração
JSONL_DIR = os.path.expanduser("~/.claude/projects/-Users-jesusnoleto")
SAIDA_DIR = os.path.expanduser("~/Desktop/TRANSCRICOES-SESSOES")


def extrair_texto_content(content):
    """Extrai texto de content (pode ser string ou array)."""
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
    """Extrai descrição legível de uma tool_use."""
    nome = item.get("name", "?")
    inp = item.get("input", {})

    if nome in ("Read", "Write", "Edit"):
        return f"{nome}: {inp.get('file_path', '?')}"
    elif nome == "Bash":
        cmd = inp.get("command", "?")
        desc = inp.get("description", "")
        if desc:
            return f"Bash ({desc}): {cmd[:300]}"
        return f"Bash: {cmd[:300]}"
    elif nome in ("Grep", "Glob"):
        return f"{nome}: {inp.get('pattern', '?')}"
    elif nome == "WebFetch":
        return f"WebFetch: {inp.get('url', '?')}"
    elif nome == "WebSearch":
        return f"WebSearch: {inp.get('query', '?')}"
    elif nome == "Agent":
        return f"Agent: {inp.get('prompt', '?')[:200]}"
    elif nome == "Skill":
        return f"Skill: {inp.get('skill_name', '?')}"
    elif nome == "ToolSearch":
        return f"ToolSearch: {inp.get('query', '?')}"
    else:
        chaves = list(inp.keys())[:3]
        resumo = ", ".join(f"{k}={str(inp[k])[:80]}" for k in chaves)
        return f"{nome}: {resumo}"


def converter_sessao(jsonl_path, saida_dir):
    """Converte um arquivo .jsonl em texto legível."""
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

            # Captura metadados da primeira mensagem que tiver
            if obj.get("sessionId") and meta["sessao"] == "?":
                meta["sessao"] = obj["sessionId"]
            if obj.get("slug") and meta["slug"] == "?":
                meta["slug"] = obj["slug"]
            if obj.get("cwd") and meta["cwd"] == "?":
                meta["cwd"] = obj["cwd"]
            if obj.get("version") and meta["version"] == "?":
                meta["version"] = obj["version"]

            # Rastreia datas
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    if primeira_data is None:
                        primeira_data = dt
                    ultima_data = dt
                except (ValueError, TypeError):
                    pass

            # Mensagem do usuário
            if tipo == "user":
                msg = obj.get("message", {})
                texto = extrair_texto_content(msg.get("content", ""))
                if texto:
                    hora = _extrair_hora(timestamp)
                    mensagens.append(("USUÁRIO", hora, texto))

            # Mensagem do assistente
            elif tipo == "assistant":
                msg = obj.get("message", {})
                modelo = msg.get("model", "")
                if modelo:
                    meta["modelo"] = modelo

                content = msg.get("content", [])
                if isinstance(content, list):
                    hora = _extrair_hora(timestamp)
                    for item in content:
                        if not isinstance(item, dict):
                            continue
                        ct = item.get("type", "")
                        if ct == "text":
                            texto = item.get("text", "")
                            if texto:
                                mensagens.append(("CLAUDE", hora, texto))
                        elif ct == "tool_use":
                            desc = extrair_tool_use(item)
                            mensagens.append(("FERRAMENTA", hora, desc))

            # Resultado de ferramenta (tool_result) — pular, é verbose demais

    if not mensagens:
        return None

    # Monta nome do arquivo
    data_str = primeira_data.strftime("%Y-%m-%d_%H%M") if primeira_data else "sem-data"
    slug = meta["slug"] if meta["slug"] != "?" else meta["sessao"][:12]
    nome_arquivo = f"SESSAO-{slug}-{data_str}.txt"
    caminho_saida = os.path.join(saida_dir, nome_arquivo)

    # Gera conteúdo
    linhas = []
    linhas.append("=" * 80)
    linhas.append(f"TRANSCRIÇÃO DE SESSÃO CLAUDE CODE")
    linhas.append("=" * 80)
    linhas.append(f"Sessão:  {meta['sessao']}")
    linhas.append(f"Slug:    {meta['slug']}")
    linhas.append(f"Modelo:  {meta['modelo']}")
    linhas.append(f"Versão:  {meta['version']}")
    linhas.append(f"CWD:     {meta['cwd']}")
    if primeira_data:
        linhas.append(f"Início:  {primeira_data.strftime('%d/%m/%Y %H:%M')}")
    if ultima_data:
        linhas.append(f"Fim:     {ultima_data.strftime('%d/%m/%Y %H:%M')}")
    linhas.append(f"Mensagens: {sum(1 for m in mensagens if m[0] in ('USUÁRIO', 'CLAUDE'))}")
    linhas.append(f"Ferramentas: {sum(1 for m in mensagens if m[0] == 'FERRAMENTA')}")
    linhas.append(f"Fonte:   {jsonl_path}")
    linhas.append("=" * 80)
    linhas.append("")

    for tipo_msg, hora, texto in mensagens:
        if tipo_msg == "USUÁRIO":
            linhas.append(f"[{hora}] ──── USUÁRIO ────────────────────────────────────")
            linhas.append(texto)
            linhas.append("")
        elif tipo_msg == "CLAUDE":
            linhas.append(f"[{hora}] ──── CLAUDE ─────────────────────────────────────")
            linhas.append(texto)
            linhas.append("")
        elif tipo_msg == "FERRAMENTA":
            linhas.append(f"  [{hora}] → {texto}")

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    return caminho_saida


def _extrair_hora(timestamp):
    """Extrai hora HH:MM de um timestamp ISO."""
    if not timestamp:
        return "--:--"
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except (ValueError, TypeError):
        return "--:--"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Converte sessões .jsonl do Claude Code em texto legível")
    parser.add_argument("--sessao", help="UUID de uma sessão específica")
    parser.add_argument("--jsonl-file", help="Caminho direto para um arquivo .jsonl (cópias salvas)")
    parser.add_argument("--ultimas", type=int, help="Converter apenas as N mais recentes")
    parser.add_argument("--saida", default=SAIDA_DIR, help=f"Pasta de saída (padrão: {SAIDA_DIR})")
    parser.add_argument("--json", action="store_true", help="Saída em JSON com resumo")
    args = parser.parse_args()

    saida_dir = args.saida
    os.makedirs(saida_dir, exist_ok=True)

    # Encontra .jsonl
    if args.jsonl_file:
        if not os.path.isfile(args.jsonl_file):
            print(f"Arquivo não encontrado: {args.jsonl_file}")
            sys.exit(1)
        arquivos = [args.jsonl_file]
    elif args.sessao:
        arquivos = glob.glob(os.path.join(JSONL_DIR, f"{args.sessao}.jsonl"))
        if not arquivos:
            print(f"Sessão não encontrada: {args.sessao}")
            sys.exit(1)
    else:
        arquivos = sorted(glob.glob(os.path.join(JSONL_DIR, "*.jsonl")),
                         key=os.path.getmtime)

    if args.ultimas:
        arquivos = arquivos[-args.ultimas:]

    total = len(arquivos)
    convertidos = 0
    erros = 0
    resultados = []

    print(f"Convertendo {total} sessões → {saida_dir}/")
    print()

    for i, arq in enumerate(arquivos, 1):
        nome = os.path.basename(arq)
        try:
            resultado = converter_sessao(arq, saida_dir)
            if resultado:
                convertidos += 1
                resultados.append({"fonte": arq, "saida": resultado})
                print(f"  [{i}/{total}] ✓ {os.path.basename(resultado)}")
            else:
                print(f"  [{i}/{total}] ⊘ {nome} (vazio)")
        except Exception as e:
            erros += 1
            print(f"  [{i}/{total}] ✗ {nome}: {e}")

    print()
    print(f"Concluído: {convertidos} convertidos, {total - convertidos - erros} vazios, {erros} erros")
    print(f"Pasta: {saida_dir}/")

    if args.json:
        resumo = {
            "total": total,
            "convertidos": convertidos,
            "erros": erros,
            "pasta_saida": saida_dir,
            "arquivos": [r["saida"] for r in resultados]
        }
        json_path = os.path.join(saida_dir, "RESUMO-CONVERSAO.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(resumo, f, indent=2, ensure_ascii=False)
        print(f"Resumo JSON: {json_path}")


if __name__ == "__main__":
    main()
