#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exportar_dashboard.py — le maestro.db e gera data.json para o dashboard.

Contrato de saida (chaves obrigatorias):
  - resumo: {total_processos, urgentes, tarefas_prazo_7d, ultimo_heartbeat_ts}
  - recentes: lista top 20 por updated_at
  - tarefas_urgentes: lista tarefas com prazo < 7 dias
  - gerado_em: ISO timestamp UTC

Falhas consultadas (ref: PYTHON-BASE/03-FALHAS-SOLUCOES/db/falhas.json):
  - GL-002 : abrir arquivo de saida em utf-8
  - PW-030 : normalizar strings de saida
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent / "maestro.db"
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "dashboard" / "data.json"


def row_to_dict(cursor: sqlite3.Cursor, row) -> dict:
    return {d[0]: row[i] for i, d in enumerate(cursor.description)}


def fetch_resumo(conn: sqlite3.Connection) -> dict:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM processos;")
    total_processos = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM processos WHERE urgencia IN ('alta','urgente','critica');")
    urgentes = cur.fetchone()[0]

    hoje = datetime.now(timezone.utc).date()
    limite = (hoje + timedelta(days=7)).isoformat()
    cur.execute(
        "SELECT COUNT(*) FROM tarefas WHERE status != 'concluida' "
        "AND prazo_data IS NOT NULL AND prazo_data <= ?;",
        (limite,),
    )
    tarefas_prazo_7d = cur.fetchone()[0]

    cur.execute("SELECT ts FROM heartbeat ORDER BY ts DESC LIMIT 1;")
    row = cur.fetchone()
    ultimo_heartbeat_ts = row[0] if row else None

    return {
        "total_processos": total_processos,
        "urgentes": urgentes,
        "tarefas_prazo_7d": tarefas_prazo_7d,
        "ultimo_heartbeat_ts": ultimo_heartbeat_ts,
    }


def fetch_recentes(conn: sqlite3.Connection, limit: int = 20) -> list[dict]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT cnj, comarca, parte_autor, parte_reu, valor_causa,
               data_nomeacao, urgencia, status, updated_at
        FROM processos
        ORDER BY updated_at DESC
        LIMIT ?;
        """,
        (limit,),
    )
    return [row_to_dict(cur, r) for r in cur.fetchall()]


def fetch_tarefas_urgentes(conn: sqlite3.Connection) -> list[dict]:
    cur = conn.cursor()
    hoje = datetime.now(timezone.utc).date()
    limite = (hoje + timedelta(days=7)).isoformat()
    cur.execute(
        """
        SELECT id, cnj, descricao, prazo_data, prioridade, status, created_at
        FROM tarefas
        WHERE status != 'concluida'
          AND prazo_data IS NOT NULL
          AND prazo_data <= ?
        ORDER BY prazo_data ASC, prioridade ASC
        LIMIT 200;
        """,
        (limite,),
    )
    return [row_to_dict(cur, r) for r in cur.fetchall()]


def main() -> int:
    ap = argparse.ArgumentParser(description="Exporta snapshot do maestro.db para data.json.")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB,
                    help=f"caminho do maestro.db (default: {DEFAULT_DB})")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help=f"arquivo data.json de saida (default: {DEFAULT_OUT})")
    args = ap.parse_args()

    db_path: Path = args.db
    out_path: Path = args.out

    if not db_path.exists():
        sys.stderr.write(f"[err] DB nao existe: {db_path}\n")
        return 2

    conn = sqlite3.connect(str(db_path))
    try:
        conn.row_factory = None
        payload = {
            "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "resumo": fetch_resumo(conn),
            "recentes": fetch_recentes(conn),
            "tarefas_urgentes": fetch_tarefas_urgentes(conn),
        }
    finally:
        conn.close()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # ref: GL-002
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=False)

    sys.stdout.write(
        f"[done] {out_path} — "
        f"total={payload['resumo']['total_processos']} "
        f"urg={payload['resumo']['urgentes']} "
        f"tarefas7d={payload['resumo']['tarefas_prazo_7d']}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
