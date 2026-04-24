"""Schema e conexão do banco de memória de sessões."""

import sqlite3
import os
import sys

DB_PATH = os.path.expanduser("~/stemmia-forense/data/memoria.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    jsonl_path TEXT NOT NULL,
    jsonl_hash TEXT NOT NULL,
    jsonl_size INTEGER,
    slug TEXT,
    model TEXT,
    version TEXT,
    cwd TEXT,
    git_branch TEXT,
    started_at TEXT,
    ended_at TEXT,
    duration_minutes INTEGER,
    user_message_count INTEGER DEFAULT 0,
    assistant_message_count INTEGER DEFAULT 0,
    tool_use_count INTEGER DEFAULT 0,
    files_written_count INTEGER DEFAULT 0,
    topics TEXT,
    summary TEXT,
    all_text TEXT,
    indexed_at TEXT
);

CREATE TABLE IF NOT EXISTS tool_uses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id),
    tool_name TEXT NOT NULL,
    tool_input_summary TEXT,
    timestamp TEXT
);

CREATE TABLE IF NOT EXISTS files_touched (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id),
    file_path TEXT NOT NULL,
    action TEXT NOT NULL,
    UNIQUE(session_id, file_path, action)
);
"""

FTS_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
    id, slug, topics, summary, all_text,
    content=sessions,
    content_rowid=rowid,
    tokenize='unicode61 remove_diacritics 2'
);
"""


def get_connection(db_path=None):
    """Abre conexão e cria tabelas se necessário."""
    path = db_path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.executescript(SCHEMA)
    try:
        conn.executescript(FTS_SCHEMA)
    except sqlite3.OperationalError:
        pass  # FTS5 pode não estar disponível
    conn.commit()
    return conn


def rebuild_fts(conn):
    """Reconstrói índice FTS5 a partir da tabela sessions."""
    try:
        # Dropar e recriar FTS5 para evitar corrupção
        conn.execute("DROP TABLE IF EXISTS sessions_fts")
        conn.execute("""
            CREATE VIRTUAL TABLE sessions_fts USING fts5(
                id, slug, topics, summary, all_text,
                content=sessions,
                content_rowid=rowid,
                tokenize='unicode61 remove_diacritics 2'
            )
        """)
        conn.execute("""
            INSERT INTO sessions_fts(rowid, id, slug, topics, summary, all_text)
            SELECT rowid, id, slug, topics, summary, all_text FROM sessions
        """)
        conn.commit()
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        print(f"  Aviso FTS5: {e}", file=sys.stderr)
        try:
            conn.rollback()
        except Exception:
            pass


def get_stats(conn):
    """Retorna estatísticas do banco."""
    stats = {}
    row = conn.execute("SELECT COUNT(*), SUM(duration_minutes) FROM sessions").fetchone()
    stats["total_sessions"] = row[0]
    stats["total_minutes"] = row[1] or 0
    stats["total_hours"] = round(stats["total_minutes"] / 60, 1)

    row = conn.execute("SELECT MIN(started_at), MAX(started_at) FROM sessions").fetchone()
    stats["first_session"] = (row[0] or "")[:10]
    stats["last_session"] = (row[1] or "")[:10]

    rows = conn.execute("""
        SELECT model, COUNT(*) as cnt FROM sessions
        WHERE model IS NOT NULL GROUP BY model ORDER BY cnt DESC LIMIT 5
    """).fetchall()
    stats["models"] = [(r[0], r[1]) for r in rows]

    rows = conn.execute("""
        SELECT tool_name, COUNT(*) as cnt FROM tool_uses
        GROUP BY tool_name ORDER BY cnt DESC LIMIT 10
    """).fetchall()
    stats["top_tools"] = [(r[0], r[1]) for r in rows]

    rows = conn.execute("""
        SELECT file_path, COUNT(*) as cnt FROM files_touched
        GROUP BY file_path ORDER BY cnt DESC LIMIT 10
    """).fetchall()
    stats["top_files"] = [(r[0], r[1]) for r in rows]

    return stats
