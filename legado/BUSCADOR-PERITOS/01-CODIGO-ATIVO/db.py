"""Banco de dados SQLite para oportunidades de perícia."""

import sqlite3
import os
from datetime import datetime
from typing import Optional
from config import DB_PATH, DATA_CORTE
from models import Oportunidade


def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = _conn()

    # Criar tabelas
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS oportunidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            fonte TEXT NOT NULL,
            termo_busca TEXT NOT NULL,
            categoria TEXT NOT NULL,
            titulo TEXT DEFAULT '',
            trecho TEXT DEFAULT '',
            comarca TEXT DEFAULT '',
            vara TEXT DEFAULT '',
            tribunal TEXT DEFAULT '',
            estado TEXT DEFAULT '',
            data_publicacao TEXT DEFAULT '',
            data_titulo TEXT DEFAULT '',
            processo_numero TEXT DEFAULT '',
            primeiro_visto TEXT NOT NULL,
            ultimo_visto TEXT NOT NULL,
            relevante INTEGER DEFAULT 1,
            contatado INTEGER DEFAULT 0,
            notas TEXT DEFAULT '',
            ignorado INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS buscas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_inicio TEXT NOT NULL,
            data_fim TEXT,
            total_encontrados INTEGER DEFAULT 0,
            total_novos INTEGER DEFAULT 0,
            termos_buscados INTEGER DEFAULT 0,
            fonte TEXT DEFAULT ''
        );
    """)

    # Migrar: adicionar coluna data_titulo se não existir
    try:
        conn.execute("SELECT data_titulo FROM oportunidades LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE oportunidades ADD COLUMN data_titulo TEXT DEFAULT ''")
        conn.commit()

    # Criar índices (após migração)
    conn.executescript("""
        CREATE INDEX IF NOT EXISTS idx_op_comarca ON oportunidades(comarca);
        CREATE INDEX IF NOT EXISTS idx_op_categoria ON oportunidades(categoria);
        CREATE INDEX IF NOT EXISTS idx_op_estado ON oportunidades(estado);
        CREATE INDEX IF NOT EXISTS idx_op_relevante ON oportunidades(relevante);
        CREATE INDEX IF NOT EXISTS idx_op_data ON oportunidades(data_publicacao);
        CREATE INDEX IF NOT EXISTS idx_op_data_titulo ON oportunidades(data_titulo);
    """)
    conn.close()


def inserir_oportunidade(op: Oportunidade) -> tuple[str, Optional[int]]:
    conn = _conn()
    cursor = conn.cursor()
    agora = datetime.now().isoformat()

    cursor.execute("SELECT id FROM oportunidades WHERE url = ?", (op.url,))
    row = cursor.fetchone()

    if row:
        oport_id = row[0]
        cursor.execute("""
            UPDATE oportunidades SET ultimo_visto = ?,
            comarca = CASE WHEN ? != '' THEN ? ELSE comarca END,
            data_titulo = CASE WHEN ? != '' THEN ? ELSE data_titulo END
            WHERE id = ?
        """, (agora, op.comarca, op.comarca, op.data_titulo, op.data_titulo, oport_id))
        conn.commit()
        conn.close()
        return ("existente", oport_id)

    cursor.execute("""
        INSERT INTO oportunidades (url, fonte, termo_busca, categoria, titulo, trecho,
            comarca, vara, tribunal, estado, data_publicacao, data_titulo, processo_numero,
            primeiro_visto, ultimo_visto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (op.url, op.fonte, op.termo_busca, op.categoria, op.titulo, op.trecho,
          op.comarca, op.vara, op.tribunal, op.estado, op.data_publicacao,
          op.data_titulo, op.processo_numero, agora, agora))

    oport_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ("novo", oport_id)


def registrar_busca(data_inicio, data_fim, total_encontrados, total_novos, termos_buscados, fonte):
    conn = _conn()
    conn.execute("""
        INSERT INTO buscas (data_inicio, data_fim, total_encontrados, total_novos, termos_buscados, fonte)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data_inicio, data_fim, total_encontrados, total_novos, termos_buscados, fonte))
    conn.commit()
    conn.close()


def get_oportunidades(filtro_estado="", filtro_categoria="", apenas_novos=False, recentes=True):
    conn = _conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM oportunidades WHERE ignorado = 0"
    params = []

    if filtro_estado:
        query += " AND estado = ?"
        params.append(filtro_estado)
    if filtro_categoria:
        query += " AND categoria = ?"
        params.append(filtro_categoria)
    if apenas_novos:
        query += " AND contatado = 0"
    if recentes:
        query += " AND (data_titulo >= ? OR data_titulo = '')"
        params.append(DATA_CORTE)

    query += " ORDER BY data_titulo DESC, primeiro_visto DESC"

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_estatisticas():
    conn = _conn()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM oportunidades WHERE ignorado = 0")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM oportunidades WHERE contatado = 0 AND ignorado = 0")
    pendentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM oportunidades WHERE contatado = 1")
    contatados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT comarca) FROM oportunidades WHERE ignorado = 0 AND comarca != ''")
    comarcas = cursor.fetchone()[0]

    cursor.execute("SELECT data_fim FROM buscas ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    ultima_busca = row[0] if row else None

    cursor.execute("""
        SELECT categoria, COUNT(*) as qtd FROM oportunidades
        WHERE ignorado = 0 GROUP BY categoria ORDER BY qtd DESC
    """)
    por_categoria = {r[0]: r[1] for r in cursor.fetchall()}

    # Recentes (últimos 12 meses)
    cursor.execute("SELECT COUNT(*) FROM oportunidades WHERE ignorado = 0 AND data_titulo >= ?", (DATA_CORTE,))
    recentes = cursor.fetchone()[0]

    conn.close()
    return {
        "total": total,
        "pendentes": pendentes,
        "contatados": contatados,
        "comarcas": comarcas,
        "ultima_busca": ultima_busca,
        "por_categoria": por_categoria,
        "recentes": recentes,
    }


def marcar_contatado(oport_id: int):
    conn = _conn()
    conn.execute("UPDATE oportunidades SET contatado = 1 WHERE id = ?", (oport_id,))
    conn.commit()
    conn.close()


def ignorar_oportunidade(oport_id: int):
    conn = _conn()
    conn.execute("UPDATE oportunidades SET ignorado = 1 WHERE id = ?", (oport_id,))
    conn.commit()
    conn.close()


def salvar_nota(oport_id: int, nota: str):
    conn = _conn()
    conn.execute("UPDATE oportunidades SET notas = ? WHERE id = ?", (nota, oport_id))
    conn.commit()
    conn.close()


def limpar_antigos():
    """Marca como ignorados resultados antigos (>12 meses) e fora das comarcas 200km."""
    from config import COMARCAS_200KM
    conn = _conn()
    cursor = conn.cursor()

    # Ignorar resultados antigos
    cursor.execute("""
        UPDATE oportunidades SET ignorado = 1
        WHERE data_titulo != '' AND data_titulo < ? AND ignorado = 0
    """, (DATA_CORTE,))
    antigos = cursor.rowcount

    # Ignorar resultados fora de MG
    cursor.execute("""
        UPDATE oportunidades SET ignorado = 1
        WHERE estado != 'MG' AND estado != '' AND ignorado = 0
        AND titulo NOT LIKE '%DJMG%'
    """)
    fora_mg = cursor.rowcount

    # Ignorar resultados de MG que não são das comarcas 200km
    # (apenas se temos comarca identificada e ela não está na lista)
    cursor.execute("SELECT id, titulo, comarca FROM oportunidades WHERE ignorado = 0")
    fora_raio = 0
    comarcas_lower = [c.lower() for c in COMARCAS_200KM]
    for row_id, titulo, comarca in cursor.fetchall():
        titulo_lower = (titulo or '').lower()
        comarca_lower = (comarca or '').lower()
        # Verificar se alguma comarca 200km aparece no título ou campo comarca
        dentro = False
        for c in comarcas_lower:
            if c in titulo_lower or c in comarca_lower:
                dentro = True
                break
        # Se o título é DJMG com seção "Administrativo" sem cidade,
        # manter (pode ser relevante para todo MG)
        if not dentro and "djmg" in titulo_lower:
            # Manter resultados administrativos genéricos de MG
            dentro = True
        if not dentro:
            cursor.execute("UPDATE oportunidades SET ignorado = 1 WHERE id = ?", (row_id,))
            fora_raio += 1

    conn.commit()
    conn.close()
    return antigos, fora_mg, fora_raio


def atualizar_data_titulo_existentes():
    """Preenche data_titulo para registros existentes que não têm."""
    import re
    conn = _conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo FROM oportunidades WHERE data_titulo = '' OR data_titulo IS NULL")
    rows = cursor.fetchall()
    atualizados = 0
    for row_id, titulo in rows:
        m = re.search(r'(\d{2})/(\d{2})/(\d{4})', titulo or '')
        if m:
            data_titulo = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
            cursor.execute("UPDATE oportunidades SET data_titulo = ? WHERE id = ?", (data_titulo, row_id))
            atualizados += 1
    conn.commit()
    conn.close()
    return atualizados
