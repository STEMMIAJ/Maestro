#!/usr/bin/env python3
"""CLI para o sistema de memória de sessões Claude Code."""

import argparse
import json
import os
import sys

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memoria.db import DB_PATH, get_connection, get_stats
from memoria.indexer import index_all, index_file, search, get_recent


def cmd_index(args):
    """Indexar todas as sessões."""
    result = index_all(
        db_path=args.db or DB_PATH,
        jsonl_dir=args.dir,
        force=args.force,
        quiet=args.quiet,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False))


def cmd_index_file(args):
    """Indexar um único arquivo."""
    db = args.db or DB_PATH
    ok = index_file(db, args.path)
    if ok:
        print(f"Indexado: {args.path}")
    else:
        print(f"Erro ao indexar: {args.path}", file=sys.stderr)
        sys.exit(1)


def cmd_search(args):
    """Buscar sessões."""
    db = args.db or DB_PATH
    query = " ".join(args.query)
    results = search(db, query, limit=args.limit)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
        return

    if not results:
        print(f"Nenhum resultado para: {query}")
        return

    print(f"=== {len(results)} resultado(s) para: {query} ===\n")
    for r in results:
        data = (r.get("started_at") or "")[:10]
        dur = f"{r.get('duration_minutes', '?')}min"
        slug = r.get("slug") or ""
        model = (r.get("model") or "")
        if model:
            model = model.split("-")[-1] if "claude" in model else model
        topics = r.get("topics") or ""
        summary = (r.get("summary") or "")[:100]
        tools = r.get("tool_use_count", 0)
        files = r.get("files_written_count", 0)

        print(f"  {data} ({dur}) [{slug}]")
        if model:
            print(f"    Modelo: {model}")
        if topics:
            print(f"    Topicos: {topics}")
        if summary:
            print(f"    Resumo: {summary}")
        print(f"    Tools: {tools} | Arquivos: {files}")
        print()


def cmd_stats(args):
    """Mostrar estatísticas."""
    db = args.db or DB_PATH
    conn = get_connection(db)
    stats = get_stats(conn)
    conn.close()

    if args.json:
        # Converter tuples para listas para JSON
        stats["models"] = [{"model": m, "count": c} for m, c in stats["models"]]
        stats["top_tools"] = [{"tool": t, "count": c} for t, c in stats["top_tools"]]
        stats["top_files"] = [{"file": f, "count": c} for f, c in stats["top_files"]]
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return

    print("=== ESTATISTICAS DA MEMORIA ===\n")
    print(f"  Total sessoes: {stats['total_sessions']}")
    print(f"  Horas totais: {stats['total_hours']}h")
    print(f"  Periodo: {stats['first_session']} a {stats['last_session']}")

    if stats["models"]:
        print(f"\n  Modelos usados:")
        for m, c in stats["models"]:
            print(f"    {m}: {c} sessoes")

    if stats["top_tools"]:
        print(f"\n  Top 10 ferramentas:")
        for t, c in stats["top_tools"]:
            print(f"    {t}: {c} usos")

    if stats["top_files"]:
        print(f"\n  Top 10 arquivos:")
        for f, c in stats["top_files"]:
            print(f"    {f}: {c} toques")


def cmd_recent(args):
    """Mostrar sessões recentes."""
    db = args.db or DB_PATH
    results = get_recent(db, limit=args.limit)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
        return

    print(f"=== ULTIMAS {len(results)} SESSOES ===\n")
    for r in results:
        data = (r.get("started_at") or "")[:16]
        dur = f"{r.get('duration_minutes', '?')}min"
        slug = r.get("slug") or ""
        topics = r.get("topics") or ""
        summary = (r.get("summary") or "")[:80]
        print(f"  {data} ({dur}) [{slug}]")
        if topics:
            print(f"    {topics}")
        if summary:
            print(f"    > {summary}")
        print()


def cmd_export_html(args):
    """Gerar dashboard HTML."""
    from memoria.html_gen import generate_dashboard
    db = args.db or DB_PATH
    output = args.output or os.path.expanduser("~/stemmia-forense/data/MEMORIA-CLAUDE.html")
    generate_dashboard(db, output)
    print(f"Dashboard gerado: {output}")


def main():
    parser = argparse.ArgumentParser(description="Memoria de sessoes Claude Code")
    parser.add_argument("--db", help="Caminho do banco SQLite")
    parser.add_argument("--json", action="store_true", help="Saida em JSON")
    parser.add_argument("--quiet", action="store_true", help="Sem output de progresso")

    sub = parser.add_subparsers(dest="command")

    # index
    p_idx = sub.add_parser("index", help="Indexar todas as sessoes")
    p_idx.add_argument("--force", action="store_true", help="Reindexar tudo")
    p_idx.add_argument("--dir", help="Diretorio dos JSONL",
                        default=os.path.expanduser("~/.claude/projects/-Users-jesus"))
    p_idx.set_defaults(func=cmd_index)

    # index-file
    p_if = sub.add_parser("index-file", help="Indexar um arquivo")
    p_if.add_argument("path", help="Caminho do JSONL")
    p_if.set_defaults(func=cmd_index_file)

    # search
    p_s = sub.add_parser("search", help="Buscar sessoes")
    p_s.add_argument("query", nargs="+", help="Termo de busca")
    p_s.add_argument("--limit", type=int, default=20)
    p_s.set_defaults(func=cmd_search)

    # stats
    p_st = sub.add_parser("stats", help="Estatisticas")
    p_st.set_defaults(func=cmd_stats)

    # recent
    p_r = sub.add_parser("recent", help="Sessoes recentes")
    p_r.add_argument("--limit", type=int, default=10)
    p_r.set_defaults(func=cmd_recent)

    # export-html
    p_h = sub.add_parser("export-html", help="Gerar dashboard HTML")
    p_h.add_argument("--output", help="Caminho do HTML de saida")
    p_h.set_defaults(func=cmd_export_html)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
