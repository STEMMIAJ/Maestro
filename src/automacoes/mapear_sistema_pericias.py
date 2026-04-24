#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mapear_sistema_pericias.py — Mapeador do Sistema de Perícias

Varre a lista canônica de pastas-raiz do sistema pericial, calcula tamanho,
contagem de arquivos, última modificação, detecta symlinks e problemas, e:
  1. Gera snapshot JSON em ~/stemmia-forense/automacoes/logs/mapa-sistema-pericias-YYYYMMDD.json
  2. Atualiza o bloco ESTADO ATUAL em ~/.claude/docs/SISTEMA-PERICIAS-MAPA-MESTRE.md
     (tudo fora do bloco <!-- BEGIN-ESTADO-ATUAL --> / <!-- END-ESTADO-ATUAL --> é preservado)

Uso:
    python3 ~/stemmia-forense/automacoes/mapear_sistema_pericias.py
    python3 ~/stemmia-forense/automacoes/mapear_sistema_pericias.py --json-only
    python3 ~/stemmia-forense/automacoes/mapear_sistema_pericias.py --verbose

Sem dependências externas — stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

HOME = Path.home()
DOC_MESTRE = HOME / ".claude" / "docs" / "SISTEMA-PERICIAS-MAPA-MESTRE.md"
LOG_DIR = HOME / "stemmia-forense" / "automacoes" / "logs"
MARKER_BEGIN = "<!-- BEGIN-ESTADO-ATUAL -->"
MARKER_END = "<!-- END-ESTADO-ATUAL -->"

# Lista canônica — espelha seção 1 do doc mestre.
# Formato: (id, path_relativo_home, rótulo, categoria, obrigatório)
#   path_relativo_home = caminho começando com ~/ ou absoluto
#   obrigatório = se True, ausência vira warning no relatório
PATHS_CANONICOS: list[tuple[str, str, str, str, bool]] = [
    # hub
    ("01", "~/Desktop/STEMMIA Dexter", "Hub Dexter (raiz)", "hub", True),
    # processos
    ("02", "~/Desktop/processos-pje", "Downloads brutos PJe", "processos", True),
    ("03", "~/Desktop/PROCESSOS FINAIS", "Processos finalizados (laudo entregue)", "processos", False),
    ("04", "~/Desktop/Processos Atualizados", "Snapshot corrente em andamento", "processos", False),
    ("05", "~/Desktop/TODOS OS PROCESSOS", "Consolidado histórico", "processos", False),
    ("06", "~/Desktop/ANALISADOR FINAL/processos", "Estrutura padrão CNJ/{PDFs,FICHA.json}", "processos", True),
    # scripts
    ("07", "~/Desktop/ANALISADOR FINAL/scripts", "Scripts canônicos (63 py)", "scripts", True),
    ("08", "~/Desktop/STEMMIA Dexter/src", "Scripts modularizados (~95)", "scripts", True),
    ("09", "~/stemmia-forense", "Hub automação (3º espelho)", "scripts", True),
    ("10", "~/stemmia-forense/automacoes", "hub.py, dashboard_hub, sync_memoria", "scripts", True),
    ("11", "~/stemmia-forense/hooks", "10 hooks anti-mentira + testes", "scripts", True),
    ("12", "~/.claude/hooks", "Hooks globais Claude", "scripts", True),
    ("13", "~/Desktop/Automações", "Automações antigas (03-Auto-PJe, 04-Laudos)", "scripts", False),
    # mesa
    ("14", "~/Desktop/_MESA/10-PERICIA", "Laudos, roteiros, quesitos, atestados", "mesa", True),
    ("15", "~/Desktop/_MESA/20-SCRIPTS", "bat-windows, command-mac, python-avulsos", "mesa", False),
    ("16", "~/Desktop/_MESA/30-DOCS/relatorios", "Relatórios, auditorias, mapas", "mesa", True),
    ("17", "~/Desktop/_MESA/40-CLAUDE", "Configs, guias, backups conversas", "mesa", False),
    ("18", "~/Desktop/_MESA/01-ATIVO", "Em uso hoje (máx 10)", "mesa", False),
    ("19", "~/Desktop/_MESA/00-INBOX", "Sem classificação (triagem)", "mesa", False),
    # pje browsers
    ("20", "~/Desktop/STEMMIA Dexter/PJE-INFRA/.chrome-pje", "Profile Chrome PJe uso diário (migrado 22/abr)", "pje", False),
    ("21", "~/Desktop/chrome-pje-profile", "Profile Chrome PJe (Selenium)", "pje", False),
    ("22", "~/Desktop/chrome-pje-profile-playwright", "Profile Chrome PJe (Playwright)", "pje", False),
    ("23", "~/.pje-browser-data", "Browser data PJe (cookies)", "pje", False),
    ("24", "~/.pjeoffice-pro", "Config PJeOffice Pro (assinador)", "pje", False),
    ("25", "~/Desktop/processos-pje-windows", "Symlink Parallels (VM)", "pje", False),
    # material
    ("26", "~/Desktop/PERÍCIA", "Material pericial antigo (iCloud)", "material", False),
    ("27", "~/Desktop/Projetos - Plan Mode", "Planos, registros de sessão", "material", False),
    ("28", "~/Desktop/STEMMIA Dexter/BANCO-DADOS", "Medicina/Direito/Perícia/TI/GERAL", "material", True),
    ("29", "~/Desktop/STEMMIA Dexter/PERÍCIA FINAL", "Pipeline (dados_brutos, fases, templates)", "material", True),
    ("30", "~/Desktop/STEMMIA Dexter/MODELOS", "Templates petição (8 tipos)", "material", True),
    ("30b", "~/Desktop/STEMMIA Dexter/MODELOS PETIÇÕES PLACEHOLDERS", "Templates com placeholders", "material", True),
    ("31", "~/Desktop/STEMMIA Dexter/MUTIRÃO", "Mutirões periciais", "material", False),
    ("31b", "~/Desktop/STEMMIA Dexter/Mutirão Conselheiro Pena", "Mutirão específico", "material", False),
    # ferramentas
    ("32", "~/Desktop/STEMMIA Dexter/FERRAMENTAS", "analisador-novo/ultra, openclaw, CIF, MEEM", "ferramentas", True),
    ("33", "~/Desktop/MONITOR-FONTES", "Monitor fontes (publicações, intimações)", "ferramentas", False),
    ("34", "~/Desktop/BUSCADOR-PERITOS", "Busca/cadastro peritos", "ferramentas", False),
    ("35", "~/Desktop/FENIX", "Módulo FENIX (automação pericial)", "ferramentas", False),
    # claude infra
    ("36", "~/Desktop/CLAUDE REVOLUÇÃO", "Doc mestra (arquitetura)", "claude", False),
    ("37", "~/Desktop/STEMMIA — SISTEMA COMPLETO", "Bundle sistema completo", "claude", False),
    ("38", "~/.claude", "Agentes, skills, plans, plugins", "claude", True),
    ("39", "~/.claude/docs", "Docs mestres (este mapa)", "claude", True),
    ("40", "~/Desktop/BACKUP CLAUDE", "Backups históricos (rollback)", "claude", False),
    ("41", "~/Desktop/PLUGINS CLAUDE", "PLUGINS-NOVOS.md", "claude", False),
    # migração 22/abr/2026
    ("42", "~/Desktop/STEMMIA Dexter/PJE-INFRA", "PJE-INFRA (perfis Chrome/Playwright + browser-data)", "pje", True),
    ("43", "~/Desktop/STEMMIA Dexter/legado", "Pastas Desktop migradas (CLAUDE REV, MONITOR-FONTES, etc.)", "hub", True),
    ("44", "~/Desktop/STEMMIA Dexter/00-CONTROLE/migracoes", "Snapshots de migrações (rollback)", "hub", True),
]

# Docs primários a checar existência
DOCS_PRIMARIOS = [
    ("Mapa Dexter completo", "~/Desktop/_MESA/30-DOCS/relatorios/MAPA-DEXTER-COMPLETO-2026-04-21.txt"),
    ("Gaps e TODO", "~/Desktop/_MESA/30-DOCS/relatorios/MAPA-FALTANDO-E-PROMPTS-PERPLEXITY-2026-04-22.md"),
    ("README operacional", "~/Desktop/STEMMIA Dexter/README.md"),
    ("CLAUDE.md local Dexter", "~/Desktop/STEMMIA Dexter/CLAUDE.md"),
    ("Organograma visual", "~/Desktop/STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA.html"),
    ("DECISOES.md", "~/Desktop/STEMMIA Dexter/DECISOES.md"),
    ("AGORA.md", "~/Desktop/STEMMIA Dexter/00-CONTROLE/AGORA.md"),
    ("Plano unificação", "~/Desktop/STEMMIA Dexter/00-CONTROLE/PLANO-UNIFICACAO-2026-04-17.md"),
    ("Banco falhas Python", "~/Desktop/STEMMIA Dexter/PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json"),
]


def expand(p: str) -> Path:
    return Path(os.path.expanduser(p))


def du_sh(p: Path) -> str:
    """Retorna `du -sh` em string humana. Rápido, usa du do sistema."""
    try:
        out = subprocess.run(
            ["du", "-sh", str(p)],
            capture_output=True, text=True, timeout=30
        )
        if out.returncode == 0 and out.stdout:
            return out.stdout.split()[0]
    except (subprocess.TimeoutExpired, OSError):
        pass
    return "?"


def count_files(p: Path, max_depth: int = 99) -> int:
    """Conta arquivos recursivamente. Usa find para velocidade."""
    try:
        out = subprocess.run(
            ["find", str(p), "-type", "f"],
            capture_output=True, text=True, timeout=30
        )
        if out.returncode == 0:
            return len([ln for ln in out.stdout.splitlines() if ln.strip()])
    except (subprocess.TimeoutExpired, OSError):
        pass
    return -1


def last_modified(p: Path) -> str:
    """Timestamp ISO da última modificação do diretório raiz."""
    try:
        ts = p.stat().st_mtime
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except OSError:
        return "?"


def inspect(path_str: str) -> dict[str, Any]:
    p = expand(path_str)
    info: dict[str, Any] = {
        "path": str(p),
        "existe": False,
        "is_symlink": False,
        "symlink_target": None,
        "symlink_broken": False,
        "size": None,
        "files": None,
        "mtime": None,
        "warn": [],
    }
    if p.is_symlink():
        info["is_symlink"] = True
        try:
            target = os.readlink(str(p))
            info["symlink_target"] = target
        except OSError:
            pass
        if not p.exists():
            info["symlink_broken"] = True
            info["warn"].append("symlink quebrado")
            return info

    if not p.exists():
        info["warn"].append("ausente")
        return info

    info["existe"] = True
    if p.is_file():
        info["size"] = du_sh(p)
        info["mtime"] = last_modified(p)
        info["files"] = 1
        return info

    info["size"] = du_sh(p)
    info["files"] = count_files(p)
    info["mtime"] = last_modified(p)
    if info["size"] == "0B" or info["files"] == 0:
        info["warn"].append("vazia (iCloud offload possível)")
    return info


def build_snapshot(verbose: bool = False) -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "host": os.uname().nodename,
        "paths": [],
        "docs_primarios": [],
        "totais_por_categoria": {},
        "warnings": [],
    }

    categoria_files: dict[str, int] = {}

    for pid, pstr, rotulo, categoria, obrigatorio in PATHS_CANONICOS:
        if verbose:
            print(f"  [{pid}] {pstr}", file=sys.stderr)
        info = inspect(pstr)
        entry = {
            "id": pid,
            "rotulo": rotulo,
            "categoria": categoria,
            "obrigatorio": obrigatorio,
            **info,
        }
        snapshot["paths"].append(entry)

        if obrigatorio and not info["existe"] and not info["is_symlink"]:
            snapshot["warnings"].append(f"[{pid}] {rotulo} AUSENTE (obrigatório) — {pstr}")
        if info["symlink_broken"]:
            snapshot["warnings"].append(f"[{pid}] {rotulo} symlink QUEBRADO — {pstr}")

        if info["files"] and info["files"] > 0:
            categoria_files[categoria] = categoria_files.get(categoria, 0) + info["files"]

    snapshot["totais_por_categoria"] = categoria_files

    for nome, pstr in DOCS_PRIMARIOS:
        p = expand(pstr)
        existe = p.exists()
        tamanho = p.stat().st_size if existe else 0
        snapshot["docs_primarios"].append({
            "nome": nome,
            "path": str(p),
            "existe": existe,
            "bytes": tamanho,
        })
        if not existe:
            snapshot["warnings"].append(f"Doc primário AUSENTE: {nome} — {pstr}")

    return snapshot


def save_json(snapshot: dict[str, Any]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    out = LOG_DIR / f"mapa-sistema-pericias-{stamp}.json"
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    latest = LOG_DIR / "mapa-sistema-pericias-LATEST.json"
    latest.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def render_estado_atual(snapshot: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"**Gerado em:** {snapshot['gerado_em']} · **host:** {snapshot['host']}")
    lines.append("")
    if snapshot["warnings"]:
        lines.append("### Warnings")
        for w in snapshot["warnings"]:
            lines.append(f"- {w}")
        lines.append("")
    else:
        lines.append("### Warnings")
        lines.append("- _nenhum_")
        lines.append("")

    lines.append("### Totais por categoria (arquivos)")
    for cat, n in sorted(snapshot["totais_por_categoria"].items(), key=lambda x: -x[1]):
        lines.append(f"- **{cat}**: {n:,} arquivos")
    lines.append("")

    lines.append("### Paths canônicos")
    lines.append("")
    lines.append("| # | Categoria | Rótulo | Tamanho | Arquivos | Mod. | Status |")
    lines.append("|---|---|---|---|---|---|---|")
    for e in snapshot["paths"]:
        status_parts = []
        if not e["existe"] and not e["is_symlink"]:
            status_parts.append("AUSENTE")
        if e["is_symlink"]:
            status_parts.append(f"symlink → `{e['symlink_target']}`" if e["symlink_target"] else "symlink")
        if e["symlink_broken"]:
            status_parts.append("QUEBRADO")
        if e["warn"]:
            status_parts.extend(e["warn"])
        status = " · ".join(status_parts) if status_parts else "ok"
        size = e["size"] or "—"
        files = "—" if e["files"] in (None, -1) else f"{e['files']:,}"
        mtime = e["mtime"] or "—"
        lines.append(f"| {e['id']} | {e['categoria']} | {e['rotulo']} | {size} | {files} | {mtime} | {status} |")
    lines.append("")

    lines.append("### Documentos primários")
    lines.append("")
    lines.append("| Nome | Existe | Tamanho (bytes) |")
    lines.append("|---|---|---|")
    for d in snapshot["docs_primarios"]:
        ex = "✓" if d["existe"] else "✗"
        lines.append(f"| {d['nome']} | {ex} | {d['bytes']:,} |")
    lines.append("")

    return "\n".join(lines)


def patch_doc_mestre(snapshot: dict[str, Any]) -> bool:
    if not DOC_MESTRE.exists():
        print(f"Doc mestre não existe: {DOC_MESTRE}", file=sys.stderr)
        return False
    text = DOC_MESTRE.read_text(encoding="utf-8")
    if MARKER_BEGIN not in text or MARKER_END not in text:
        print(f"Marcadores {MARKER_BEGIN} / {MARKER_END} ausentes no doc mestre.", file=sys.stderr)
        return False
    bloco_novo = render_estado_atual(snapshot)
    pre, rest = text.split(MARKER_BEGIN, 1)
    _, pos = rest.split(MARKER_END, 1)
    novo = f"{pre}{MARKER_BEGIN}\n{bloco_novo}\n{MARKER_END}{pos}"
    DOC_MESTRE.write_text(novo, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Mapeador do sistema de perícias")
    parser.add_argument("--json-only", action="store_true", help="Só gera JSON; não atualiza o doc mestre")
    parser.add_argument("--verbose", "-v", action="store_true", help="Log verboso no stderr")
    args = parser.parse_args()

    print("Varrendo paths canônicos...", file=sys.stderr)
    snapshot = build_snapshot(verbose=args.verbose)
    json_path = save_json(snapshot)
    print(f"JSON salvo em: {json_path}", file=sys.stderr)
    print(f"LATEST: {LOG_DIR / 'mapa-sistema-pericias-LATEST.json'}", file=sys.stderr)

    n_paths = len(snapshot["paths"])
    n_existem = sum(1 for p in snapshot["paths"] if p["existe"])
    n_warn = len(snapshot["warnings"])
    print(
        f"Resultado: {n_existem}/{n_paths} paths existem · "
        f"{n_warn} warnings · "
        f"{sum(snapshot['totais_por_categoria'].values()):,} arquivos totais",
        file=sys.stderr,
    )

    if not args.json_only:
        ok = patch_doc_mestre(snapshot)
        if ok:
            print(f"Doc mestre atualizado: {DOC_MESTRE}", file=sys.stderr)
        else:
            print("Doc mestre NÃO atualizado (ver erros acima).", file=sys.stderr)
            return 2

    if snapshot["warnings"]:
        print("\n=== WARNINGS ===", file=sys.stderr)
        for w in snapshot["warnings"]:
            print(f"  - {w}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
