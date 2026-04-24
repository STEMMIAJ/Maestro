#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
comarcas_proximas_gv.py
=======================

CLI que lista comarcas TJMG ordenadas por distância de Governador Valadares e
cruza com contatos (telefone/email/setor/varas) extraídos pelo pipeline irmão.

Fontes de dados:
  - Distâncias (OSRM):
      ../distancias-gv/output/distancias_gv.json
      Lista de objetos: {codigo, nome, lat, lon, display_name, km, min, fonte}
  - Comarcas TJMG (sede + municípios + distritos):
      ./data/comarcas.json
      Dict por nome: {codigo_tjmg, entrancia, forum, cep, telefone, municipios[], distritos[]}
  - Contatos completos (output do extrator do Time A, opcional):
      ./data/contatos_completo.json
      Dict por nome: {codigo_tjmg, tipo, forum_nome, endereco, telefone_principal,
                      setores[{nome,email,telefone,...}], varas[{nome,email,...}]}

Estratégia de cruzamento:
  1. A entrada de distância pode bater num distrito ("Derribadinha") cuja sede
     é "Governador Valadares". Construímos um índice
        nome_normalizado -> nome_da_comarca_sede
     usando os campos `municipios[]` e `distritos[]` do comarcas.json.
  2. Para cada comarca-sede pegamos a MENOR distância entre ela própria e
     qualquer município/distrito subordinado (representa a "borda" mais próxima).
  3. Cruzamos com contatos_completo.json (se existir). Caso contrário, usamos
     telefone do comarcas.json e deixamos email vazio (modo degradado).

Encoding: leitura/escrita SEMPRE com encoding='utf-8'.
# ref: GL-002 (subprocess/encoding cp1252 vs utf-8 — aqui evitamos abrindo
# explicitamente em utf-8 em todos os open()).

Uso:
    python3 comarcas_proximas_gv.py --raio 100
    python3 comarcas_proximas_gv.py --raio 100 --com-email --formato md \\
        --output output/comarcas_100km.md
    python3 comarcas_proximas_gv.py --raio 200 --setor "Administração" --formato csv

Autor: Time B (sistema Stemmia)
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Paths fixos (relativos ao próprio script)
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
PROJ_ROOT = HERE.parent  # 08-SISTEMAS-COMPLETOS
DIST_JSON = PROJ_ROOT / "distancias-gv" / "output" / "distancias_gv.json"
COMARCAS_JSON = HERE / "data" / "comarcas.json"
CONTATOS_JSON = HERE / "data" / "contatos_completo.json"
OUTPUT_DIR = HERE / "output"

NOME_GV = "Governador Valadares"

# ---------------------------------------------------------------------------
# Utilidades de normalização
# ---------------------------------------------------------------------------
def norm(s: Optional[str]) -> str:
    """lowercase, strip, sem acentos, sem espaço duplicado. Para chave de match."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


# ---------------------------------------------------------------------------
# Carregamento (cache em memória durante a execução)
# ---------------------------------------------------------------------------
def carregar_distancias(path: Path = DIST_JSON) -> List[Dict[str, Any]]:
    if not path.exists():
        sys.exit(f"[ERRO] Arquivo de distâncias não encontrado: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        sys.exit(f"[ERRO] Formato inesperado em {path} (esperava list)")
    return data


def carregar_comarcas(path: Path = COMARCAS_JSON) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        sys.exit(f"[ERRO] Arquivo de comarcas não encontrado: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def carregar_contatos(path: Path = CONTATOS_JSON) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        print(
            f"[WARN] {path.name} não encontrado, usando só comarcas.json",
            file=sys.stderr,
        )
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            d = json.load(f)
        if not isinstance(d, dict):
            print(
                f"[WARN] {path.name} com formato inesperado, ignorando.",
                file=sys.stderr,
            )
            return {}
        return d
    except json.JSONDecodeError as e:
        print(f"[WARN] {path.name} inválido ({e}), ignorando.", file=sys.stderr)
        return {}


# ---------------------------------------------------------------------------
# Cruzamento
# ---------------------------------------------------------------------------
@dataclass
class Linha:
    """Linha consolidada por comarca-sede."""
    comarca: str                       # nome canônico (do comarcas.json)
    codigo_tjmg: Optional[str]
    entrancia: Optional[str]
    forum: Optional[str]
    cep: Optional[str]
    telefone: Optional[str]
    km: float
    min: float                         # tempo de viagem (minutos)
    nome_origem_match: str             # quem na lista de distâncias deu o melhor match
    tipo_match: str                    # 'sede' | 'municipio' | 'distrito'
    emails_setores: Dict[str, str] = field(default_factory=dict)  # nome_setor -> email
    email_admin: Optional[str] = None
    email_cejusc: Optional[str] = None
    todos_emails: List[str] = field(default_factory=list)
    setores: List[Dict[str, Any]] = field(default_factory=list)
    varas: List[Dict[str, Any]] = field(default_factory=list)


def construir_indice_subordinados(
    comarcas: Dict[str, Dict[str, Any]]
) -> Dict[str, Tuple[str, str]]:
    """
    Mapa: nome_normalizado -> (nome_canonico_da_sede, tipo)
    onde tipo ∈ {'sede','municipio','distrito'}
    """
    idx: Dict[str, Tuple[str, str]] = {}
    for nome_sede, info in comarcas.items():
        idx.setdefault(norm(nome_sede), (nome_sede, "sede"))
        for m in info.get("municipios") or []:
            idx.setdefault(norm(m), (nome_sede, "municipio"))
        for d in info.get("distritos") or []:
            idx.setdefault(norm(d), (nome_sede, "distrito"))
    return idx


def cruzar_dados(
    distancias: List[Dict[str, Any]],
    comarcas: Dict[str, Dict[str, Any]],
    contatos: Dict[str, Dict[str, Any]],
) -> List[Linha]:
    """
    Para cada comarca-sede do comarcas.json, encontra a MENOR km entre ela e
    qualquer município/distrito subordinado. Resultado: 1 linha por sede.
    """
    idx = construir_indice_subordinados(comarcas)
    melhores: Dict[str, Dict[str, Any]] = {}

    for d in distancias:
        nm = d.get("nome")
        km = d.get("km")
        if nm is None or km is None:
            continue
        chave = norm(nm)
        match = idx.get(chave)
        if not match:
            continue
        sede, tipo = match
        cur = melhores.get(sede)
        if cur is None or d["km"] < cur["km"]:
            melhores[sede] = {
                "km": d["km"],
                "min": d.get("min", 0.0) or 0.0,
                "origem": nm,
                "tipo_match": tipo,
            }

    # Index contatos por nome normalizado para tolerância de caixa/acento
    contatos_idx = {norm(k): v for k, v in (contatos or {}).items()}

    linhas: List[Linha] = []
    for sede, info in comarcas.items():
        best = melhores.get(sede)
        if best is None:
            continue  # sem distância calculada
        cont = contatos_idx.get(norm(sede), {})

        setores = cont.get("setores") or []
        varas = cont.get("varas") or []
        emails_setores: Dict[str, str] = {}
        todos_emails: List[str] = []
        email_admin = None
        email_cejusc = None

        for s in setores:
            nome_s = (s.get("nome") or "").strip()
            email_s = (s.get("email") or "").strip()
            if email_s:
                emails_setores[nome_s] = email_s
                todos_emails.append(email_s)
                ns = norm(nome_s)
                # email_admin: por nome do setor OU por padrão TJMG `<sigla>adm@`
                if email_admin is None and (
                    "administ" in ns
                    or "secretaria" in ns
                    or "diretoria" in ns
                    or re.search(r"adm@tjmg\.jus\.br$", email_s, flags=re.I)
                ):
                    email_admin = email_s
                if email_cejusc is None and (
                    "cejusc" in ns or "concilia" in ns or "cejusc" in email_s.lower()
                ):
                    email_cejusc = email_s
        for v in varas:
            email_v = (v.get("email") or "").strip()
            if email_v:
                todos_emails.append(email_v)

        # dedup mantendo ordem
        seen = set()
        todos_emails = [e for e in todos_emails if not (e in seen or seen.add(e))]

        telefone = cont.get("telefone_principal") or info.get("telefone")

        linhas.append(
            Linha(
                comarca=sede,
                codigo_tjmg=info.get("codigo_tjmg"),
                entrancia=info.get("entrancia"),
                forum=info.get("forum") or cont.get("forum_nome"),
                cep=info.get("cep"),
                telefone=telefone,
                km=round(float(best["km"]), 2),
                min=round(float(best["min"]), 1),
                nome_origem_match=best["origem"],
                tipo_match=best["tipo_match"],
                emails_setores=emails_setores,
                email_admin=email_admin,
                email_cejusc=email_cejusc,
                todos_emails=todos_emails,
                setores=setores,
                varas=varas,
            )
        )
    linhas.sort(key=lambda x: x.km)
    return linhas


# ---------------------------------------------------------------------------
# Filtros
# ---------------------------------------------------------------------------
def filtrar(
    linhas: List[Linha],
    raio: float,
    tipo: str,
    entrancias: List[str],
    com_email: bool,
    setor: Optional[str],
    excluir_gv: bool,
    limite: Optional[int],
) -> List[Linha]:
    out = []
    setor_norm = norm(setor) if setor else None
    entr_norm = {norm(e) for e in entrancias} if entrancias else None
    for l in linhas:
        if l.km > raio:
            continue
        if excluir_gv and norm(l.comarca) == norm(NOME_GV):
            continue
        # 'sede' e 'todos' aceitam qualquer match (1 linha por comarca-sede,
        # com a distância mais curta entre sede e municípios/distritos).
        # 'distrito' restringe para casos em que a aproximação se deu via distrito.
        if tipo == "distrito" and l.tipo_match != "distrito":
            continue
        if entr_norm and norm(l.entrancia or "") not in entr_norm:
            continue
        if com_email and not l.todos_emails:
            continue
        if setor_norm:
            achou = any(setor_norm in norm(s) for s in l.emails_setores.keys())
            if not achou:
                continue
        out.append(l)
    if limite:
        out = out[:limite]
    return out


def email_setor_especifico(linha: Linha, setor: str) -> str:
    """Retorna o primeiro email cujo nome de setor casa com `setor` (substring norm)."""
    sn = norm(setor)
    for nome_s, email_s in linha.emails_setores.items():
        if sn in norm(nome_s):
            return email_s
    return ""


# ---------------------------------------------------------------------------
# Formatadores
# ---------------------------------------------------------------------------
def _abreviar(s: Optional[str], n: int) -> str:
    if not s:
        return ""
    return s if len(s) <= n else s[: n - 1] + "…"


def formatar_tabela(
    linhas: List[Linha], raio: float, setor: Optional[str] = None
) -> str:
    com_email = sum(1 for l in linhas if l.todos_emails)
    header = f"RAIO {raio:g} km — {len(linhas)} comarcas ({com_email} com email)\n\n"

    # Tenta rich
    try:
        from rich.console import Console
        from rich.table import Table

        buf = io.StringIO()
        console = Console(file=buf, width=160, force_terminal=False)
        table = Table(show_lines=False)
        table.add_column("#", justify="right")
        table.add_column("KM", justify="right")
        table.add_column("MIN", justify="right")
        table.add_column("COMARCA")
        table.add_column("ENTRÂNCIA")
        table.add_column("TELEFONE")
        table.add_column("EMAIL ADMIN")
        col_extra = "EMAIL CEJUSC" if not setor else f"EMAIL {setor.upper()}"
        table.add_column(col_extra)
        for i, l in enumerate(linhas, 1):
            extra = (
                email_setor_especifico(l, setor) if setor else (l.email_cejusc or "")
            )
            table.add_row(
                str(i),
                f"{l.km:.0f}",
                f"{l.min:.0f}",
                _abreviar(l.comarca, 28),
                _abreviar(l.entrancia or "", 10),
                _abreviar(l.telefone or "", 18),
                _abreviar(l.email_admin or "", 30),
                _abreviar(extra, 30),
            )
        console.print(table)
        return header + buf.getvalue()
    except ImportError:
        pass

    # Fallback tabulate
    try:
        from tabulate import tabulate

        rows = []
        for i, l in enumerate(linhas, 1):
            extra = (
                email_setor_especifico(l, setor) if setor else (l.email_cejusc or "")
            )
            rows.append(
                [
                    i,
                    f"{l.km:.0f}",
                    f"{l.min:.0f}",
                    _abreviar(l.comarca, 28),
                    _abreviar(l.entrancia or "", 10),
                    _abreviar(l.telefone or "", 18),
                    _abreviar(l.email_admin or "", 30),
                    _abreviar(extra, 30),
                ]
            )
        head = [
            "#",
            "KM",
            "MIN",
            "COMARCA",
            "ENTRÂNCIA",
            "TELEFONE",
            "EMAIL ADMIN",
            "EMAIL CEJUSC" if not setor else f"EMAIL {setor.upper()}",
        ]
        return header + tabulate(rows, headers=head, tablefmt="simple")
    except ImportError:
        pass

    # Fallback manual
    cols = [
        ("#", 3),
        ("KM", 5),
        ("MIN", 5),
        ("COMARCA", 28),
        ("ENTRÂNCIA", 10),
        ("TELEFONE", 18),
        ("EMAIL ADMIN", 30),
        ("EMAIL CEJUSC" if not setor else f"EMAIL {setor.upper()}", 30),
    ]
    out = [header]
    out.append("  ".join(f"{n:<{w}}" for n, w in cols))
    out.append("  ".join("-" * w for _, w in cols))
    for i, l in enumerate(linhas, 1):
        extra = email_setor_especifico(l, setor) if setor else (l.email_cejusc or "")
        vals = [
            str(i),
            f"{l.km:.0f}",
            f"{l.min:.0f}",
            _abreviar(l.comarca, 28),
            _abreviar(l.entrancia or "", 10),
            _abreviar(l.telefone or "", 18),
            _abreviar(l.email_admin or "", 30),
            _abreviar(extra, 30),
        ]
        out.append("  ".join(f"{v:<{w}}" for v, (_, w) in zip(vals, cols)))
    return "\n".join(out)


def formatar_md(linhas: List[Linha], raio: float, setor: Optional[str] = None) -> str:
    com_email = sum(1 for l in linhas if l.todos_emails)
    out = [
        f"# Comarcas TJMG até {raio:g} km de Governador Valadares",
        "",
        f"- **Total:** {len(linhas)} comarcas",
        f"- **Com email:** {com_email}",
        "",
        "| # | km | min | Comarca | Entrância | Telefone | Email admin | Outros emails |",
        "|---|---:|---:|---|---|---|---|---|",
    ]
    for i, l in enumerate(linhas, 1):
        admin = (
            f"[{l.email_admin}](mailto:{l.email_admin})" if l.email_admin else ""
        )
        outros = []
        for e in l.todos_emails:
            if e != l.email_admin:
                outros.append(f"[{e}](mailto:{e})")
        outros_str = "<br>".join(outros[:5])
        out.append(
            f"| {i} | {l.km:.0f} | {l.min:.0f} | {l.comarca} | "
            f"{l.entrancia or ''} | {l.telefone or ''} | {admin} | {outros_str} |"
        )
    return "\n".join(out) + "\n"


def formatar_csv(linhas: List[Linha], setor: Optional[str] = None) -> str:
    buf = io.StringIO()
    fields = [
        "rank",
        "comarca",
        "codigo_tjmg",
        "entrancia",
        "km",
        "min",
        "telefone",
        "email_admin",
        "email_cejusc",
        "email_setor_filtrado",
        "todos_emails",
        "forum",
        "cep",
        "tipo_match",
        "origem_match",
    ]
    w = csv.DictWriter(buf, fieldnames=fields)
    w.writeheader()
    for i, l in enumerate(linhas, 1):
        w.writerow(
            {
                "rank": i,
                "comarca": l.comarca,
                "codigo_tjmg": l.codigo_tjmg or "",
                "entrancia": l.entrancia or "",
                "km": f"{l.km:.2f}",
                "min": f"{l.min:.1f}",
                "telefone": l.telefone or "",
                "email_admin": l.email_admin or "",
                "email_cejusc": l.email_cejusc or "",
                "email_setor_filtrado": email_setor_especifico(l, setor) if setor else "",
                "todos_emails": ";".join(l.todos_emails),
                "forum": l.forum or "",
                "cep": l.cep or "",
                "tipo_match": l.tipo_match,
                "origem_match": l.nome_origem_match,
            }
        )
    return buf.getvalue()


def formatar_json(linhas: List[Linha]) -> str:
    out = []
    for i, l in enumerate(linhas, 1):
        out.append(
            {
                "rank": i,
                "comarca": l.comarca,
                "codigo_tjmg": l.codigo_tjmg,
                "entrancia": l.entrancia,
                "forum": l.forum,
                "cep": l.cep,
                "telefone": l.telefone,
                "km": l.km,
                "min": l.min,
                "tipo_match": l.tipo_match,
                "origem_match": l.nome_origem_match,
                "email_admin": l.email_admin,
                "email_cejusc": l.email_cejusc,
                "todos_emails": l.todos_emails,
                "emails_setores": l.emails_setores,
                "setores": l.setores,
                "varas": l.varas,
            }
        )
    return json.dumps(out, ensure_ascii=False, indent=2)


def formatar_html(linhas: List[Linha], raio: float, setor: Optional[str] = None) -> str:
    com_email = sum(1 for l in linhas if l.todos_emails)
    rows = []
    for i, l in enumerate(linhas, 1):
        admin_link = (
            f'<a href="mailto:{l.email_admin}">{l.email_admin}</a>'
            if l.email_admin
            else ""
        )
        outros = "<br>".join(
            f'<a href="mailto:{e}">{e}</a>'
            for e in l.todos_emails
            if e != l.email_admin
        )
        rows.append(
            f"<tr><td>{i}</td><td>{l.km:.0f}</td><td>{l.min:.0f}</td>"
            f"<td>{l.comarca}</td><td>{l.entrancia or ''}</td>"
            f"<td>{l.telefone or ''}</td><td>{admin_link}</td><td>{outros}</td></tr>"
        )
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Comarcas TJMG até {raio:g} km de GV</title>
<style>
body{{font-family:-apple-system,sans-serif;margin:24px;color:#222}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ddd;padding:6px 8px;text-align:left;font-size:13px}}
th{{background:#f4f4f4}}
tr:nth-child(even){{background:#fafafa}}
</style></head><body>
<h1>Comarcas TJMG até {raio:g} km de Governador Valadares</h1>
<p><b>{len(linhas)}</b> comarcas — <b>{com_email}</b> com email</p>
<table>
<thead><tr><th>#</th><th>km</th><th>min</th><th>Comarca</th><th>Entrância</th>
<th>Telefone</th><th>Email admin</th><th>Outros emails</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody></table>
</body></html>
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Lista comarcas TJMG ordenadas por distância de Governador "
            "Valadares e cruza com contatos (telefone/email/setores)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--raio", type=float, default=100.0, help="Raio em km (default 100)")
    p.add_argument(
        "--tipo",
        choices=["sede", "todos", "distrito"],
        default="sede",
        help="Filtro por tipo de match. Default: sede.",
    )
    p.add_argument(
        "--entrancia",
        action="append",
        default=[],
        help="Filtra entrância (Especial/Primeira/Segunda). Pode repetir flag.",
    )
    p.add_argument("--com-email", action="store_true", help="Só listar quem tem email.")
    p.add_argument(
        "--formato",
        choices=["tabela", "csv", "json", "md", "html"],
        default="tabela",
    )
    p.add_argument("--output", type=str, default=None, help="Caminho do arquivo de saída.")
    p.add_argument("--limite", type=int, default=None, help="Top N mais próximos.")
    p.add_argument("--setor", type=str, default=None, help="Filtra setor específico.")
    p.add_argument(
        "--excluir-gv",
        action="store_true",
        help="Não listar a própria Governador Valadares.",
    )
    return p.parse_args(argv)


def resolver_output_path(args: argparse.Namespace) -> Optional[Path]:
    if args.output:
        out = Path(args.output)
        if not out.is_absolute():
            # relativo ao script
            out = HERE / out
        return out
    if args.formato == "tabela":
        return None  # stdout
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ext = {"csv": "csv", "json": "json", "md": "md", "html": "html"}[args.formato]
    return OUTPUT_DIR / f"comarcas_proximas.{ext}"


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    distancias = carregar_distancias()
    comarcas = carregar_comarcas()
    contatos = carregar_contatos()

    linhas = cruzar_dados(distancias, comarcas, contatos)
    filtradas = filtrar(
        linhas,
        raio=args.raio,
        tipo=args.tipo,
        entrancias=args.entrancia,
        com_email=args.com_email,
        setor=args.setor,
        excluir_gv=args.excluir_gv,
        limite=args.limite,
    )

    if args.formato == "tabela":
        out = formatar_tabela(filtradas, args.raio, setor=args.setor)
    elif args.formato == "md":
        out = formatar_md(filtradas, args.raio, setor=args.setor)
    elif args.formato == "csv":
        out = formatar_csv(filtradas, setor=args.setor)
    elif args.formato == "json":
        out = formatar_json(filtradas)
    elif args.formato == "html":
        out = formatar_html(filtradas, args.raio, setor=args.setor)
    else:
        sys.exit(f"[ERRO] formato desconhecido: {args.formato}")

    out_path = resolver_output_path(args)
    if out_path is None:
        print(out)
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out, encoding="utf-8")
        print(f"[OK] {len(filtradas)} comarcas salvas em {out_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
