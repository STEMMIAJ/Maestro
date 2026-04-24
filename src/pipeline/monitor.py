#!/usr/bin/env python3
# DATAJUD_GUIA: ~/Desktop/STEMMIA Dexter/DOCS/datajud/DATAJUD-GUIA.md — ler antes de alterar chamadas DataJud
"""
Monitor de Prazos e Intimações — Integrado com agenda-pericial.
Verifica periodicamente se há novidades nos processos via DataJud API.

Uso:
  python3 monitor.py prazos              # Lista prazos próximos
  python3 monitor.py alertas             # Mostra alertas ativos
  python3 monitor.py verificar           # Consulta DataJud para novidades
  python3 monitor.py verificar --silencioso  # Modo silencioso (para heartbeat)
  python3 monitor.py sincronizar         # Sincroniza processos/ com agenda-pericial
"""

import json
import os
import re
import sqlite3
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent
PROCESSOS_DIR = BASE_DIR / "processos"
AGENDA_DIR = Path.home() / "Desktop" / "Projetos - Plan Mode" / "agenda-pericial"
DB_PATH = AGENDA_DIR / "data" / "agenda.db"

# DataJud API
DATAJUD_BASE = "https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal}/_search"

# Cores
class C:
    R = "\033[0m"
    B = "\033[1m"
    G = "\033[32m"
    Y = "\033[33m"
    RE = "\033[31m"
    CY = "\033[36m"
    DIM = "\033[2m"


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ", "OK": "✓", "ERRO": "✗", "AVISO": "⚠"}.get(level, "·")
    print(f"  [{ts}] {prefix} {msg}")


# ============================================================
# BANCO DE DADOS
# ============================================================

def get_db():
    """Conecta ao banco da agenda-pericial."""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Garante que as tabelas existem."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS casos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_cnj TEXT UNIQUE NOT NULL,
            numero_pericia TEXT DEFAULT '',
            tribunal TEXT NOT NULL,
            comarca TEXT DEFAULT '',
            vara TEXT DEFAULT '',
            area TEXT DEFAULT '',
            tipo TEXT DEFAULT '',
            objeto TEXT DEFAULT '',
            areas_medicas TEXT DEFAULT '[]',
            status TEXT DEFAULT 'nomeado',
            urgencia TEXT DEFAULT 'MEDIA',
            data_nomeacao TEXT DEFAULT '',
            data_intimacao TEXT DEFAULT '',
            data_aceite TEXT DEFAULT '',
            data_proposta_honorarios TEXT DEFAULT '',
            data_deposito_honorarios TEXT DEFAULT '',
            data_agendamento_pericia TEXT DEFAULT '',
            data_pericia TEXT DEFAULT '',
            data_entrega_laudo TEXT DEFAULT '',
            data_prazo_laudo TEXT DEFAULT '',
            honorarios_propostos REAL DEFAULT 0,
            honorarios_depositados REAL DEFAULT 0,
            pasta_local TEXT DEFAULT '',
            pasta_organizador TEXT DEFAULT '',
            notas TEXT DEFAULT '',
            ativo INTEGER DEFAULT 1,
            criado_em TEXT NOT NULL,
            atualizado_em TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS prazos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caso_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            data_inicio TEXT NOT NULL,
            data_vencimento TEXT NOT NULL,
            dias_uteis INTEGER NOT NULL,
            status TEXT DEFAULT 'pendente',
            cumprido_em TEXT DEFAULT '',
            alerta_enviado_3d INTEGER DEFAULT 0,
            alerta_enviado_1d INTEGER DEFAULT 0,
            alerta_enviado_hoje INTEGER DEFAULT 0,
            alerta_enviado_vencido INTEGER DEFAULT 0,
            criado_em TEXT NOT NULL,
            atualizado_em TEXT NOT NULL,
            FOREIGN KEY (caso_id) REFERENCES casos(id)
        );

        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caso_id INTEGER,
            numero_cnj TEXT NOT NULL,
            fonte TEXT NOT NULL,
            codigo_tpu INTEGER DEFAULT 0,
            nome TEXT NOT NULL,
            data_movimento TEXT NOT NULL,
            texto_complementar TEXT DEFAULT '',
            processado INTEGER DEFAULT 0,
            relevante INTEGER DEFAULT 1,
            acao_gerada TEXT DEFAULT '',
            hash_dedup TEXT UNIQUE,
            criado_em TEXT NOT NULL,
            FOREIGN KEY (caso_id) REFERENCES casos(id)
        );

        CREATE TABLE IF NOT EXISTS alertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caso_id INTEGER,
            prazo_id INTEGER,
            tipo TEXT NOT NULL,
            titulo TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            urgencia TEXT DEFAULT 'MEDIA',
            enviado INTEGER DEFAULT 0,
            enviado_em TEXT DEFAULT '',
            lido INTEGER DEFAULT 0,
            criado_em TEXT NOT NULL,
            FOREIGN KEY (caso_id) REFERENCES casos(id),
            FOREIGN KEY (prazo_id) REFERENCES prazos(id)
        );

        CREATE INDEX IF NOT EXISTS idx_casos_cnj ON casos(numero_cnj);
        CREATE INDEX IF NOT EXISTS idx_prazos_vencimento ON prazos(data_vencimento);
        CREATE INDEX IF NOT EXISTS idx_prazos_status ON prazos(status);
    """)
    conn.close()


# ============================================================
# SINCRONIZAÇÃO processos/ → banco
# ============================================================

def cmd_sincronizar():
    """Sincroniza processos/ com o banco da agenda-pericial."""
    init_db()
    conn = get_db()
    agora = datetime.now().isoformat()

    if not PROCESSOS_DIR.exists():
        log("Pasta processos/ não existe", "ERRO")
        return

    novos = 0
    atualizados = 0

    for pasta in sorted(PROCESSOS_DIR.iterdir()):
        if not pasta.is_dir() or pasta.is_symlink():
            continue

        ficha_path = pasta / "FICHA.json"
        if not ficha_path.exists():
            continue

        try:
            ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        cnj = ficha.get("numero_cnj", "")
        if not cnj:
            continue

        # Verificar se já existe no banco
        row = conn.execute("SELECT id FROM casos WHERE numero_cnj = ?", (cnj,)).fetchone()

        if row:
            # Atualizar
            conn.execute("""
                UPDATE casos SET
                    comarca = ?, vara = ?, area = ?, tipo = ?,
                    pasta_local = ?, atualizado_em = ?
                WHERE numero_cnj = ?
            """, (
                ficha.get("comarca", ""),
                ficha.get("vara", ""),
                ficha.get("area", ""),
                ficha.get("tipo_pericia", ""),
                str(pasta),
                agora,
                cnj
            ))
            atualizados += 1
        else:
            # Inserir novo
            tribunal = ficha.get("tribunal", "TJMG")
            conn.execute("""
                INSERT INTO casos (numero_cnj, numero_pericia, tribunal, comarca, vara,
                    area, tipo, objeto, areas_medicas, status, pasta_local, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cnj,
                str(ficha.get("numero_pericia", "")),
                tribunal,
                ficha.get("comarca", ""),
                ficha.get("vara", ""),
                ficha.get("area", ""),
                ficha.get("tipo_pericia", ""),
                ficha.get("objeto", ""),
                json.dumps(ficha.get("areas_medicas", []), ensure_ascii=False),
                ficha.get("status", "nomeado"),
                str(pasta),
                agora, agora
            ))
            novos += 1

    conn.commit()
    conn.close()

    log(f"Sincronização: {novos} novos, {atualizados} atualizados", "OK")


# ============================================================
# PRAZOS
# ============================================================

def cmd_prazos():
    """Lista prazos pendentes ordenados por vencimento."""
    init_db()
    conn = get_db()

    # Marcar vencidos
    hoje = datetime.now().strftime("%Y-%m-%d")
    conn.execute("""
        UPDATE prazos SET status = 'vencido', atualizado_em = ?
        WHERE status = 'pendente' AND data_vencimento < ?
    """, (datetime.now().isoformat(), hoje))
    conn.commit()

    # Buscar prazos pendentes
    prazos = conn.execute("""
        SELECT p.*, c.numero_cnj, c.comarca, c.vara, c.numero_pericia
        FROM prazos p
        JOIN casos c ON p.caso_id = c.id
        WHERE p.status IN ('pendente', 'vencido') AND c.ativo = 1
        ORDER BY p.data_vencimento ASC
    """).fetchall()

    # Buscar vencidos
    vencidos = conn.execute("""
        SELECT p.*, c.numero_cnj, c.comarca, c.vara, c.numero_pericia
        FROM prazos p
        JOIN casos c ON p.caso_id = c.id
        WHERE p.status = 'vencido' AND c.ativo = 1
        ORDER BY p.data_vencimento ASC
    """).fetchall()

    conn.close()

    print(f"\n{C.B}  PRAZOS — {len(prazos)} pendentes{C.R}")
    print(f"{'─'*70}")

    if not prazos:
        print(f"  {C.DIM}Nenhum prazo cadastrado.{C.R}")
        print(f"  Use 'python3 monitor.py sincronizar' para importar processos.")
        print()
        return

    for p in prazos:
        vencimento = p["data_vencimento"]
        dias_restantes = (datetime.strptime(vencimento, "%Y-%m-%d") - datetime.now()).days

        if dias_restantes < 0:
            urgencia = f"{C.RE}VENCIDO ({abs(dias_restantes)}d){C.R}"
        elif dias_restantes <= 3:
            urgencia = f"{C.RE}{dias_restantes}d{C.R}"
        elif dias_restantes <= 7:
            urgencia = f"{C.Y}{dias_restantes}d{C.R}"
        else:
            urgencia = f"{C.G}{dias_restantes}d{C.R}"

        num = p["numero_pericia"] or "?"
        cnj = p["numero_cnj"]
        tipo = p["tipo"]
        desc = p["descricao"][:40]

        print(f"  {urgencia:>20}  Perícia {num} | {tipo} — {desc}")
        print(f"  {' ':>20}  {C.DIM}{cnj} | {vencimento}{C.R}")
        print()


# ============================================================
# ALERTAS
# ============================================================

def cmd_alertas():
    """Mostra alertas não lidos."""
    init_db()
    conn = get_db()

    alertas = conn.execute("""
        SELECT a.*, c.numero_cnj, c.numero_pericia
        FROM alertas a
        LEFT JOIN casos c ON a.caso_id = c.id
        WHERE a.lido = 0
        ORDER BY a.criado_em DESC
        LIMIT 20
    """).fetchall()

    conn.close()

    print(f"\n{C.B}  ALERTAS — {len(alertas)} não lidos{C.R}")
    print(f"{'─'*70}")

    if not alertas:
        print(f"  {C.G}Nenhum alerta pendente.{C.R}")
        print()
        return

    for a in alertas:
        urg = a["urgencia"]
        if urg == "ALTA":
            icon = f"{C.RE}!!{C.R}"
        elif urg == "MEDIA":
            icon = f"{C.Y}! {C.R}"
        else:
            icon = f"{C.DIM}  {C.R}"

        num = a["numero_pericia"] or "?"
        print(f"  {icon} Perícia {num} — {a['titulo']}")
        print(f"     {a['mensagem'][:60]}")
        print(f"     {C.DIM}{a['criado_em'][:19]}{C.R}")
        print()


# ============================================================
# VERIFICAR (DataJud API)
# ============================================================

def consultar_datajud(cnj, tribunal="tjmg"):
    """Consulta movimentações de um processo via DataJud API."""
    url = DATAJUD_BASE.format(tribunal=tribunal)

    body = json.dumps({
        "query": {
            "match": {
                "numeroProcesso": cnj.replace("-", "").replace(".", "")
            }
        },
        "size": 1
    }).encode("utf-8")

    _datajud_key = os.getenv("DATAJUD_API_KEY", "")
    if not _datajud_key:
        raise RuntimeError(
            "DATAJUD_API_KEY não setada. Execute: "
            'export DATAJUD_API_KEY="<chave>" '
            "(ver https://datajud-wiki.cnj.jus.br/api-publica/acesso)"
        )
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"APIKey {_datajud_key}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            hits = data.get("hits", {}).get("hits", [])
            if hits:
                return hits[0].get("_source", {})
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        pass

    return None


def cmd_verificar(silencioso=False):
    """Verifica DataJud para novidades em todos os processos."""
    init_db()
    cmd_sincronizar()  # Sincroniza primeiro

    conn = get_db()
    casos = conn.execute("SELECT * FROM casos WHERE ativo = 1").fetchall()

    if not casos:
        if not silencioso:
            log("Nenhum caso no banco. Rode 'sincronizar' primeiro.", "AVISO")
        conn.close()
        return

    if not silencioso:
        print(f"\n{C.B}  VERIFICANDO {len(casos)} processos via DataJud{C.R}")
        print(f"{'─'*50}")

    novidades = []
    agora = datetime.now().isoformat()

    for caso in casos:
        cnj = caso["numero_cnj"]
        tribunal = (caso["tribunal"] or "TJMG").lower()

        # Mapear tribunal para endpoint DataJud
        tribunal_map = {
            "tjmg": "tjmg",
            "trf6": "trf6",
            "trf1": "trf1",
            "trt3": "trt3",
        }
        endpoint = tribunal_map.get(tribunal, "tjmg")

        resultado = consultar_datajud(cnj, endpoint)

        if resultado:
            movs = resultado.get("movimentos", [])
            if movs:
                ultima_mov = movs[0]  # Mais recente
                nome_mov = ultima_mov.get("nome", "Sem nome")
                data_mov = ultima_mov.get("dataHora", "")[:10]

                # Verificar se já temos essa movimentação
                import hashlib
                hash_dedup = hashlib.md5(
                    f"{cnj}|{ultima_mov.get('codigo', 0)}|{data_mov}|{nome_mov}".encode()
                ).hexdigest()

                existente = conn.execute(
                    "SELECT id FROM movimentacoes WHERE hash_dedup = ?", (hash_dedup,)
                ).fetchone()

                if not existente:
                    # Nova movimentação!
                    conn.execute("""
                        INSERT INTO movimentacoes (caso_id, numero_cnj, fonte, codigo_tpu,
                            nome, data_movimento, texto_complementar, hash_dedup, criado_em)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        caso["id"], cnj, "datajud",
                        ultima_mov.get("codigo", 0),
                        nome_mov, data_mov,
                        json.dumps(ultima_mov.get("complementosTabelados", []), ensure_ascii=False),
                        hash_dedup, agora
                    ))

                    novidades.append({
                        "cnj": cnj,
                        "pericia": caso["numero_pericia"],
                        "movimento": nome_mov,
                        "data": data_mov,
                    })

                    if not silencioso:
                        log(f"{C.G}NOVO{C.R} Perícia {caso['numero_pericia']} — {nome_mov} ({data_mov})")

        if not silencioso:
            # Progresso
            pass

    conn.commit()
    conn.close()

    if not silencioso:
        print(f"\n  {C.B}Novidades encontradas: {len(novidades)}{C.R}\n")

    # Se silencioso e há novidades, retorna para o heartbeat usar
    return novidades


# ============================================================
# MAIN
# ============================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()

    if cmd == "prazos":
        cmd_prazos()
    elif cmd == "alertas":
        cmd_alertas()
    elif cmd == "verificar":
        silencioso = "--silencioso" in sys.argv or "--silent" in sys.argv
        cmd_verificar(silencioso)
    elif cmd == "sincronizar":
        init_db()
        cmd_sincronizar()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
