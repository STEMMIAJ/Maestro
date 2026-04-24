#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
indexer_ficha.py — varre FICHA.json dos processos e faz upsert em maestro.db.

Fonte-da-verdade continua sendo o FICHA.json em disco; este script apenas
indexa em SQLite para consulta rapida e export de dashboard.

Falhas consultadas (ref: PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json):
  - GL-002  : abrir arquivos texto com encoding='utf-8' e errors='replace'
  - PW-030  : normalizar strings com unicodedata (evitar lixo em paths/cnj)
  - CDP-001 : nao aplicavel aqui (mantido para rastreio)
  - PJE-014 : nao aplicavel aqui (mantido para rastreio)

Uso:
  python3 indexer_ficha.py                       # real, origem default
  python3 indexer_ficha.py --dry-run             # simula, nao grava
  python3 indexer_ficha.py --source /caminho     # origem alternativa
  python3 indexer_ficha.py --db /caminho.db      # DB alternativo
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

# Paths default (absolutos, sem dependencia de cwd).
DEFAULT_SOURCE = Path("/Users/jesus/Desktop/ANALISADOR FINAL/processos")
DEFAULT_DB = Path(__file__).resolve().parent / "maestro.db"
SCHEMA = Path(__file__).resolve().parent / "schema.sql"


def log(msg: str) -> None:
    # Saida simples para stdout. ref: GL-002 -> garantir utf-8.
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def norm_text(value) -> str | None:
    """Normaliza string (NFKD) e remove controle; ref: PW-030."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        try:
            value = json.dumps(value, ensure_ascii=False)
        except Exception:
            value = str(value)
    s = str(value).strip()
    if not s:
        return None
    s = unicodedata.normalize("NFKC", s)
    return s


def pick(d: dict, *keys, default=None):
    for k in keys:
        if k in d and d[k] not in (None, "", []):
            return d[k]
    return default


def extract_partes(ficha: dict) -> tuple[str | None, str | None]:
    """Deriva parte_autor e parte_reu de FICHA.json (campos irregulares)."""
    autor = pick(ficha, "autor")
    reu = pick(ficha, "reu")
    partes = ficha.get("partes")
    if isinstance(partes, dict):
        if not autor:
            autor = partes.get("autor") or partes.get("requerente")
        if not reu:
            reu = partes.get("reu") or partes.get("requerido")
    elif isinstance(partes, list) and partes:
        # Heuristica: primeiro = autor, segundo = reu.
        if not autor and len(partes) >= 1:
            autor = partes[0]
        if not reu and len(partes) >= 2:
            reu = partes[1]
    return norm_text(autor), norm_text(reu)


def parse_valor(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s:
        return None
    # Formatos BR: "R$ 12.345,67" ou "12345.67".
    s = s.replace("R$", "").replace("\xa0", "").strip()
    # Se tem virgula, tratar como decimal BR.
    if "," in s and s.count(",") == 1:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def derive_urgencia(ficha: dict) -> str | None:
    """Heuristica minima: se FICHA marca liminar true ou prazo curto, urgente."""
    if ficha.get("liminar") is True:
        return "alta"
    prazos = ficha.get("prazos")
    if isinstance(prazos, list) and prazos:
        return "media"
    # Sem dado -> deixa None (indexador nao inventa).
    return None


def ensure_schema(conn: sqlite3.Connection) -> None:
    if not SCHEMA.exists():
        raise FileNotFoundError(f"schema ausente: {SCHEMA}")
    # ref: GL-002
    sql = SCHEMA.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


def upsert_processo(conn: sqlite3.Connection, row: dict) -> None:
    """Upsert usando ON CONFLICT(cnj). created_at preservado em update."""
    sql = """
    INSERT INTO processos (
        cnj, comarca, parte_autor, parte_reu, valor_causa,
        data_nomeacao, urgencia, status, created_at, updated_at, ficha_json_path
    ) VALUES (
        :cnj, :comarca, :parte_autor, :parte_reu, :valor_causa,
        :data_nomeacao, :urgencia, :status, :now, :now, :ficha_json_path
    )
    ON CONFLICT(cnj) DO UPDATE SET
        comarca         = excluded.comarca,
        parte_autor     = excluded.parte_autor,
        parte_reu       = excluded.parte_reu,
        valor_causa     = excluded.valor_causa,
        data_nomeacao   = excluded.data_nomeacao,
        urgencia        = excluded.urgencia,
        status          = excluded.status,
        updated_at      = excluded.updated_at,
        ficha_json_path = excluded.ficha_json_path
    ;
    """
    conn.execute(sql, row)


def record_heartbeat(conn: sqlite3.Connection, status: str, detalhe: str) -> None:
    conn.execute(
        "INSERT INTO heartbeat (componente, status, detalhe) VALUES (?, ?, ?)",
        ("indexer_ficha", status, detalhe),
    )


def processar_ficha(path: Path) -> dict | None:
    """Le e normaliza uma FICHA.json. Retorna row dict pronta p/ upsert."""
    try:
        # ref: GL-002
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            ficha = json.load(fh)
    except (json.JSONDecodeError, OSError) as e:
        log(f"[skip] FICHA invalida: {path} -> {e}")
        return None

    if not isinstance(ficha, dict):
        log(f"[skip] FICHA nao e objeto JSON: {path}")
        return None

    cnj = pick(ficha, "cnj", "numero_cnj", "cnj_arquivo_original")
    cnj = norm_text(cnj)
    if not cnj:
        # Fallback: nome do diretorio pai.
        cnj = norm_text(path.parent.name)
    if not cnj:
        log(f"[skip] sem CNJ identificavel: {path}")
        return None

    autor, reu = extract_partes(ficha)
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")

    return {
        "cnj": cnj,
        "comarca": norm_text(pick(ficha, "comarca", "cidade")),
        "parte_autor": autor,
        "parte_reu": reu,
        "valor_causa": parse_valor(pick(ficha, "valor_causa", "valor_honorarios")),
        "data_nomeacao": norm_text(pick(ficha, "data_nomeacao", "data_aceite")),
        "urgencia": derive_urgencia(ficha),
        "status": norm_text(pick(ficha, "status", "etapa_atual")),
        "now": now_iso,
        "ficha_json_path": str(path),
    }


def varrer_fichas(source: Path) -> list[Path]:
    if not source.exists():
        log(f"[info] origem nao existe: {source}")
        return []
    if not source.is_dir():
        log(f"[info] origem nao e diretorio: {source}")
        return []
    encontrados: list[Path] = []
    # rglob captura subpastas com acento (aceita path existente).
    for p in source.rglob("FICHA.json"):
        if p.is_file():
            encontrados.append(p)
    return encontrados


def main() -> int:
    ap = argparse.ArgumentParser(description="Indexa FICHA.json em SQLite.")
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                    help=f"diretorio-raiz com subpastas de processos (default: {DEFAULT_SOURCE})")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB,
                    help=f"caminho do maestro.db (default: {DEFAULT_DB})")
    ap.add_argument("--dry-run", action="store_true",
                    help="nao grava no DB; apenas conta e valida")
    args = ap.parse_args()

    source: Path = args.source
    db_path: Path = args.db

    log(f"[info] source = {source}")
    log(f"[info] db     = {db_path}")
    log(f"[info] dry_run= {args.dry_run}")

    fichas = varrer_fichas(source)
    total = len(fichas)
    log(f"[info] FICHA.json encontradas: {total}")

    if total == 0:
        # Retorno zero sem crash (contrato).
        if not args.dry_run:
            db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(db_path))
            try:
                ensure_schema(conn)
                record_heartbeat(conn, "ok-zero", f"source={source}")
                conn.commit()
            finally:
                conn.close()
        log("[done] zero processos indexados.")
        return 0

    processadas = 0
    rejeitadas = 0
    rows: list[dict] = []
    for p in fichas:
        row = processar_ficha(p)
        if row is None:
            rejeitadas += 1
            continue
        rows.append(row)
        processadas += 1

    log(f"[info] processadas={processadas} rejeitadas={rejeitadas}")

    if args.dry_run:
        log("[done] dry-run — nada gravado.")
        return 0

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        ensure_schema(conn)
        with conn:  # transacao unica
            for row in rows:
                upsert_processo(conn, row)
            record_heartbeat(
                conn, "ok",
                f"encontrados={total} processadas={processadas} rejeitadas={rejeitadas}",
            )
        log(f"[done] upsert concluido: {processadas} linhas.")
    except sqlite3.Error as e:
        log(f"[err] sqlite: {e}")
        return 2
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
