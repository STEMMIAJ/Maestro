-- Maestro DB local — schema v1
-- Fonte-da-verdade: FICHA.json por processo. Esta base e indice rapido.
-- ref: GL-002 (utf-8 sempre), PW-030 (normalizar unicode em paths)

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA encoding = "UTF-8";

CREATE TABLE IF NOT EXISTS processos (
    cnj             TEXT PRIMARY KEY,
    comarca         TEXT,
    parte_autor     TEXT,
    parte_reu       TEXT,
    valor_causa     REAL,
    data_nomeacao   TEXT,
    urgencia        TEXT,
    status          TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ficha_json_path TEXT
);

CREATE TABLE IF NOT EXISTS documentos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    cnj         TEXT NOT NULL,
    tipo        TEXT,
    data        TEXT,
    caminho     TEXT,
    verificado  INTEGER DEFAULT 0,
    FOREIGN KEY (cnj) REFERENCES processos(cnj) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tarefas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    cnj         TEXT NOT NULL,
    descricao   TEXT,
    prazo_data  TEXT,
    prioridade  INTEGER DEFAULT 3,
    status      TEXT DEFAULT 'aberta',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cnj) REFERENCES processos(cnj) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS heartbeat (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    componente  TEXT,
    status      TEXT,
    detalhe     TEXT
);

CREATE INDEX IF NOT EXISTS idx_doc_cnj    ON documentos (cnj);
CREATE INDEX IF NOT EXISTS idx_task_cnj   ON tarefas    (cnj);
CREATE INDEX IF NOT EXISTS idx_task_prazo ON tarefas    (prazo_data);
CREATE INDEX IF NOT EXISTS idx_heart_ts   ON heartbeat  (ts);
CREATE INDEX IF NOT EXISTS idx_proc_urg   ON processos  (urgencia);
