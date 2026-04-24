"""Parser de JSONL + indexador SQLite + busca FTS5."""

import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime

from .stopwords_pt import STOPWORDS
from .db import get_connection, rebuild_fts


JSONL_DIR = os.path.expanduser("~/.claude/projects/-Users-jesus")


def file_hash(path):
    """SHA256 do arquivo."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_topics(text, n=8):
    """Extrai top N palavras-chave do texto."""
    words = re.findall(r"[a-záàâãéèêíïóôõúüç]{3,}", text.lower())
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 3]
    if not filtered:
        return ""
    return ", ".join(w for w, _ in Counter(filtered).most_common(n))


def parse_session(jsonl_path):
    """Parseia um arquivo JSONL e retorna dados estruturados."""
    session_id = None
    slug = None
    model = None
    version = None
    cwd = None
    git_branch = None
    started_at = None
    ended_at = None

    user_texts = []
    all_texts = []
    tool_uses = []
    files = {}  # path -> action
    user_count = 0
    assistant_count = 0
    tool_count = 0
    summary = ""

    try:
        with open(jsonl_path, "r", errors="replace") as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg_type = obj.get("type", "")
                ts = obj.get("timestamp")

                if msg_type == "queue-operation":
                    continue

                # Extrair metadados da primeira linha
                if session_id is None:
                    session_id = obj.get("sessionId", "")
                    slug = obj.get("slug", "")
                    version = obj.get("version", "")
                    cwd = obj.get("cwd", "")
                    git_branch = obj.get("gitBranch", "")

                if ts:
                    if started_at is None:
                        started_at = ts
                    ended_at = ts

                if msg_type == "user":
                    user_count += 1
                    content = obj.get("message", {}).get("content", "")
                    if isinstance(content, str) and content.strip():
                        user_texts.append(content.strip())
                        all_texts.append(content.strip())
                        if not summary:
                            summary = content.strip()[:200]
                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict):
                                if block.get("type") == "text":
                                    txt = block.get("text", "").strip()
                                    if txt:
                                        user_texts.append(txt)
                                        all_texts.append(txt)
                                        if not summary:
                                            summary = txt[:200]

                elif msg_type == "assistant":
                    assistant_count += 1
                    msg = obj.get("message", {})
                    if not model:
                        model = msg.get("model", "")
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for block in content:
                            if not isinstance(block, dict):
                                continue
                            btype = block.get("type", "")
                            if btype == "text":
                                txt = block.get("text", "").strip()
                                if txt and len(txt) > 10:
                                    all_texts.append(txt[:500])
                            elif btype == "tool_use":
                                tool_count += 1
                                name = block.get("name", "")
                                inp = block.get("input", {})
                                input_summary = ""
                                if name in ("Read", "Write", "Edit", "MultiEdit"):
                                    input_summary = inp.get("file_path", "")
                                    if name in ("Write", "Edit"):
                                        files[input_summary] = name.lower()
                                    elif name == "Read":
                                        files.setdefault(input_summary, "read")
                                elif name == "Glob":
                                    input_summary = inp.get("pattern", "")
                                elif name == "Grep":
                                    input_summary = inp.get("pattern", "")
                                elif name == "Bash":
                                    cmd = inp.get("command", "")
                                    input_summary = cmd[:100]
                                elif name == "Agent":
                                    input_summary = inp.get("description", "")[:80]
                                elif name == "Skill":
                                    input_summary = inp.get("skill", "")

                                tool_uses.append({
                                    "tool_name": name,
                                    "tool_input_summary": input_summary,
                                    "timestamp": ts,
                                })

    except Exception as e:
        print(f"  ERRO parsing {jsonl_path}: {e}", file=sys.stderr)
        return None

    if not session_id:
        # Usar nome do arquivo como fallback
        session_id = os.path.splitext(os.path.basename(jsonl_path))[0]

    # Calcular duração
    duration = None
    if started_at and ended_at:
        try:
            fmt_candidates = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"]
            t1 = t2 = None
            for fmt in fmt_candidates:
                try:
                    t1 = datetime.strptime(started_at, fmt)
                    break
                except ValueError:
                    continue
            for fmt in fmt_candidates:
                try:
                    t2 = datetime.strptime(ended_at, fmt)
                    break
                except ValueError:
                    continue
            if t1 and t2:
                duration = max(0, int((t2 - t1).total_seconds() / 60))
        except Exception:
            pass

    # Texto completo para busca
    all_text = "\n".join(all_texts)
    topics = extract_topics(all_text)
    files_written = sum(1 for a in files.values() if a in ("write", "edit"))

    return {
        "id": session_id,
        "jsonl_path": jsonl_path,
        "jsonl_hash": file_hash(jsonl_path),
        "jsonl_size": os.path.getsize(jsonl_path),
        "slug": slug,
        "model": model,
        "version": version,
        "cwd": cwd,
        "git_branch": git_branch,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_minutes": duration,
        "user_message_count": user_count,
        "assistant_message_count": assistant_count,
        "tool_use_count": tool_count,
        "files_written_count": files_written,
        "topics": topics,
        "summary": summary,
        "all_text": all_text[:50000],  # limitar tamanho
        "indexed_at": datetime.now().isoformat(),
        "tool_uses": tool_uses,
        "files": files,
    }


def index_session(conn, data):
    """Insere/atualiza uma sessão no banco."""
    conn.execute("""
        INSERT OR REPLACE INTO sessions
        (id, jsonl_path, jsonl_hash, jsonl_size, slug, model, version, cwd,
         git_branch, started_at, ended_at, duration_minutes,
         user_message_count, assistant_message_count, tool_use_count,
         files_written_count, topics, summary, all_text, indexed_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data["id"], data["jsonl_path"], data["jsonl_hash"], data["jsonl_size"],
        data["slug"], data["model"], data["version"], data["cwd"],
        data["git_branch"], data["started_at"], data["ended_at"],
        data["duration_minutes"], data["user_message_count"],
        data["assistant_message_count"], data["tool_use_count"],
        data["files_written_count"], data["topics"], data["summary"],
        data["all_text"], data["indexed_at"],
    ))

    # Tool uses (limitar a 200 por sessão para performance)
    for tu in data.get("tool_uses", [])[:200]:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO tool_uses (session_id, tool_name, tool_input_summary, timestamp)
                VALUES (?, ?, ?, ?)
            """, (data["id"], tu["tool_name"], tu["tool_input_summary"], tu["timestamp"]))
        except Exception:
            pass

    # Files touched
    for fpath, action in data.get("files", {}).items():
        if fpath:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO files_touched (session_id, file_path, action)
                    VALUES (?, ?, ?)
                """, (data["id"], fpath, action))
            except Exception:
                pass

    conn.commit()


def index_all(db_path=None, jsonl_dir=None, force=False, quiet=False):
    """Indexa todas as sessões JSONL."""
    db_path = db_path or os.path.expanduser("~/stemmia-forense/data/memoria.db")
    jsonl_dir = jsonl_dir or JSONL_DIR

    conn = get_connection(db_path)

    # Carregar hashes existentes
    existing = {}
    if not force:
        rows = conn.execute("SELECT jsonl_path, jsonl_hash FROM sessions").fetchall()
        existing = {r[0]: r[1] for r in rows}

    # Listar arquivos JSONL
    jsonl_files = sorted(
        [os.path.join(jsonl_dir, f) for f in os.listdir(jsonl_dir)
         if f.endswith(".jsonl") and not os.path.isdir(os.path.join(jsonl_dir, f))],
        key=os.path.getmtime
    )

    total = len(jsonl_files)
    indexed = 0
    skipped = 0
    errors = 0

    if not quiet:
        print(f"Encontrados: {total} arquivos JSONL em {jsonl_dir}")

    for i, path in enumerate(jsonl_files):
        # Check hash para dedup
        if not force and path in existing:
            current_hash = file_hash(path)
            if current_hash == existing[path]:
                skipped += 1
                continue

        # Parsear e indexar
        data = parse_session(path)
        if data:
            index_session(conn, data)
            indexed += 1
        else:
            errors += 1

        if not quiet and (i + 1) % 50 == 0:
            print(f"  Progresso: {i + 1}/{total} ({indexed} indexados, {skipped} pulados)")

    # Rebuild FTS
    if indexed > 0:
        if not quiet:
            print("Reconstruindo indice FTS5...")
        rebuild_fts(conn)

    conn.close()

    if not quiet:
        print(f"\nResultado: {indexed} indexados, {skipped} sem mudanca, {errors} erros")
        print(f"Total no banco: {indexed + skipped} sessoes")

    return {"indexed": indexed, "skipped": skipped, "errors": errors}


def index_file(db_path, jsonl_path):
    """Indexa um único arquivo JSONL."""
    conn = get_connection(db_path)
    data = parse_session(jsonl_path)
    if data:
        index_session(conn, data)
        rebuild_fts(conn)
        conn.close()
        return True
    conn.close()
    return False


def search(db_path, query, limit=20):
    """Busca sessões por texto."""
    conn = get_connection(db_path)
    results = []

    # Tentar FTS5 primeiro
    try:
        fts_query = " OR ".join(query.split())
        rows = conn.execute("""
            SELECT s.id, s.slug, s.model, s.started_at, s.ended_at,
                   s.duration_minutes, s.topics, s.summary,
                   s.user_message_count, s.tool_use_count, s.files_written_count,
                   rank
            FROM sessions_fts f
            JOIN sessions s ON s.id = f.id
            WHERE sessions_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (fts_query, limit)).fetchall()
        results = [dict(r) for r in rows]
    except Exception:
        pass

    # Fallback: LIKE search
    if not results:
        like = f"%{query}%"
        rows = conn.execute("""
            SELECT id, slug, model, started_at, ended_at,
                   duration_minutes, topics, summary,
                   user_message_count, tool_use_count, files_written_count
            FROM sessions
            WHERE all_text LIKE ? OR topics LIKE ? OR summary LIKE ? OR slug LIKE ?
            ORDER BY started_at DESC
            LIMIT ?
        """, (like, like, like, like, limit)).fetchall()
        results = [dict(r) for r in rows]

    conn.close()
    return results


def get_recent(db_path, limit=10):
    """Retorna sessões mais recentes."""
    conn = get_connection(db_path)
    rows = conn.execute("""
        SELECT id, slug, model, started_at, ended_at,
               duration_minutes, topics, summary,
               user_message_count, tool_use_count, files_written_count
        FROM sessions
        ORDER BY started_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
