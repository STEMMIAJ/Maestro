#!/usr/bin/env python3
"""
sync_memoria_obsidian.py
Sincroniza memorias do Claude (~/.claude/projects/-Users-jesus/memory/)
para o vault Obsidian (~/Desktop/STEMMIA Dexter/memoria/CLAUDE-MEMORY/).

- Copia todos os .md
- Adiciona frontmatter Obsidian se ausente
- Gera INDEX.md por categoria
- Idempotente (so atualiza se conteudo mudou)
"""

from __future__ import annotations
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

SRC = Path("/Users/jesus/.claude/projects/-Users-jesus/memory")
DST = Path("/Users/jesus/Desktop/STEMMIA Dexter/memoria/CLAUDE-MEMORY")

CATEGORIAS = {
    "user": "Perfil do Usuario",
    "feedback": "Feedback Operacional",
    "project": "Projetos",
    "reference": "Referencias",
    "MEMORY": "Indice Raiz",
}


def categoria(nome: str) -> str:
    base = nome.replace(".md", "")
    for prefixo in CATEGORIAS:
        if base.startswith(prefixo):
            return prefixo
    return "outros"


def hash_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def garantir_frontmatter(conteudo: str, nome_arquivo: str) -> str:
    """Adiciona frontmatter Obsidian se nao houver."""
    if conteudo.lstrip().startswith("---"):
        return conteudo

    base = nome_arquivo.replace(".md", "")
    cat = categoria(nome_arquivo)
    alias = base.replace("_", " ").replace("-", " ").title()

    fm = (
        "---\n"
        f"title: {alias}\n"
        f"aliases: [{base}]\n"
        f"tags: [claude-memory, {cat}]\n"
        f"categoria: {cat}\n"
        f"sincronizado: {datetime.now().isoformat(timespec='seconds')}\n"
        "---\n\n"
    )
    return fm + conteudo


def sync() -> dict:
    DST.mkdir(parents=True, exist_ok=True)

    stats = {"novos": 0, "atualizados": 0, "iguais": 0, "total": 0}
    arquivos_por_categoria: dict[str, list[str]] = {}

    for src_file in sorted(SRC.glob("*.md")):
        nome = src_file.name
        dst_file = DST / nome
        stats["total"] += 1

        cat = categoria(nome)
        arquivos_por_categoria.setdefault(cat, []).append(nome)

        novo_conteudo = garantir_frontmatter(
            src_file.read_text(encoding="utf-8"), nome
        )

        if dst_file.exists():
            if hash_file(dst_file) == hashlib.sha256(
                novo_conteudo.encode("utf-8")
            ).hexdigest():
                stats["iguais"] += 1
                continue
            stats["atualizados"] += 1
        else:
            stats["novos"] += 1

        dst_file.write_text(novo_conteudo, encoding="utf-8")

    # Index
    gerar_index(arquivos_por_categoria, stats)
    return stats


def gerar_index(arquivos: dict[str, list[str]], stats: dict) -> None:
    linhas = [
        "---",
        "title: Indice de Memorias do Claude",
        "tags: [claude-memory, indice]",
        f"atualizado: {datetime.now().isoformat(timespec='seconds')}",
        "---",
        "",
        "# Indice de Memorias do Claude",
        "",
        f"**Total:** {stats['total']} memorias  ",
        f"**Novos:** {stats['novos']} | **Atualizados:** {stats['atualizados']} | **Sem mudanca:** {stats['iguais']}",
        "",
        "Sincronizado automaticamente via `sync_memoria_obsidian.py`.",
        "Origem: `~/.claude/projects/-Users-jesus/memory/`",
        "",
    ]

    ordem = ["MEMORY", "user", "feedback", "project", "reference", "outros"]
    for cat in ordem:
        if cat not in arquivos:
            continue
        titulo = CATEGORIAS.get(cat, cat.title())
        linhas.append(f"## {titulo} ({len(arquivos[cat])})")
        linhas.append("")
        for nome in sorted(arquivos[cat]):
            base = nome.replace(".md", "")
            linhas.append(f"- [[{base}]]")
        linhas.append("")

    (DST / "INDEX.md").write_text("\n".join(linhas), encoding="utf-8")


if __name__ == "__main__":
    print(f"[sync] origem: {SRC}")
    print(f"[sync] destino: {DST}")
    s = sync()
    print(
        f"[sync] total={s['total']} novos={s['novos']} "
        f"atualizados={s['atualizados']} iguais={s['iguais']}"
    )
    print(f"[sync] INDEX.md gerado em {DST/'INDEX.md'}")
