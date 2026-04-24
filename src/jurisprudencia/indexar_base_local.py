#!/usr/bin/env python3
"""
Indexa base local de jurisprudência com Whoosh.
Fontes: BANCO-DADOS/GERAL/direito/jurisprudencia/ + banco-de-dados/Banco-Transversal/

Uso:
    python3 indexar_base_local.py          # reindexar tudo
    python3 indexar_base_local.py --status # ver estado do índice
"""

import os
import re
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

try:
    from whoosh import index
    from whoosh.fields import Schema, TEXT, ID, KEYWORD, STORED
    from whoosh.analysis import StemmingAnalyzer
    from whoosh.qparser import MultifieldParser
except ImportError:
    print("ERRO: pip3 install whoosh")
    sys.exit(1)

# — Paths ——————————————————————————————————————————————
DEXTER = Path(__file__).parent.parent.parent  # ~/Desktop/STEMMIA Dexter
BASE_TXT   = DEXTER / "BANCO-DADOS" / "GERAL" / "direito" / "jurisprudencia"
BASE_TRANS = DEXTER / "banco-de-dados" / "Banco-Transversal"
INDEX_DIR  = DEXTER / "banco-de-dados" / ".indice_whoosh"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("indexador")

# — Schema ——————————————————————————————————————————————
SCHEMA = Schema(
    id         = ID(stored=True, unique=True),
    tribunal   = KEYWORD(stored=True),
    area       = KEYWORD(stored=True),
    numero     = ID(stored=True),
    data       = STORED(),
    valor      = STORED(),
    fonte      = STORED(),
    arquivo    = STORED(),
    conteudo   = TEXT(analyzer=StemmingAnalyzer(), stored=False),
    resumo     = STORED(),
)

# — Parser ——————————————————————————————————————————————
def extrair_tribunal(nome: str) -> str:
    for t in ("STJ", "STF", "TST", "TJMG", "TRF", "TRT"):
        if t in nome.upper():
            return t
    return "OUTRO"

def extrair_numero(nome: str) -> str:
    m = re.search(r'(REsp|AREsp|AgRg|RE|ADI|RR|AIRR)[-\s]?(\d[\d\.-]+)', nome, re.I)
    return m.group(0) if m else ""

def extrair_valor(texto: str) -> str:
    m = re.search(r'R\$\s?[\d.,]+', texto)
    return m.group(0) if m else ""

def extrair_data(texto: str) -> str:
    m = re.search(r'(20\d{2}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]20\d{2})', texto)
    return m.group(0) if m else ""

# — Indexação ——————————————————————————————————————————
def indexar_arquivo(writer, caminho: Path, area: str, fonte: str) -> int:
    try:
        texto = caminho.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        log.warning(f"  falha ao ler {caminho.name}: {e}")
        return 0

    doc_id = str(caminho.relative_to(DEXTER))
    tribunal = extrair_tribunal(caminho.name)
    numero   = extrair_numero(caminho.name)
    valor    = extrair_valor(texto)
    data     = extrair_data(texto)
    resumo   = texto[:400].replace("\n", " ")

    writer.update_document(
        id       = doc_id,
        tribunal = tribunal,
        area     = area,
        numero   = numero,
        data     = data,
        valor    = valor,
        fonte    = fonte,
        arquivo  = str(caminho),
        conteudo = texto,
        resumo   = resumo,
    )
    return 1

def indexar_tudo() -> dict:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    if index.exists_in(str(INDEX_DIR)):
        ix = index.open_dir(str(INDEX_DIR))
    else:
        ix = index.create_in(str(INDEX_DIR), SCHEMA)

    stats = {"total": 0, "fontes": {}}

    with ix.writer() as w:
        # 1. Arquivos .txt de jurisprudência por área
        if BASE_TXT.exists():
            for area_dir in sorted(BASE_TXT.iterdir()):
                if not area_dir.is_dir():
                    continue
                area = area_dir.name
                n = 0
                for arq in area_dir.glob("*.txt"):
                    n += indexar_arquivo(w, arq, area, "base_txt")
                for arq in area_dir.glob("*.md"):
                    n += indexar_arquivo(w, arq, area, "base_txt")
                if n:
                    stats["fontes"][area] = n
                    stats["total"] += n
                    log.info(f"  {area}: {n} docs")

        # 2. Banco-Transversal (Jurisprudencia, Sentencas, Contestacoes)
        for subpasta in ("Jurisprudencia", "Sentencas", "Contestacoes", "Honorarios-Periciais"):
            sp = BASE_TRANS / subpasta
            if not sp.exists():
                continue
            n = 0
            for arq in sp.rglob("*.md"):
                n += indexar_arquivo(w, arq, subpasta.lower(), "transversal")
            for arq in sp.rglob("*.txt"):
                n += indexar_arquivo(w, arq, subpasta.lower(), "transversal")
            if n:
                stats["fontes"][subpasta] = n
                stats["total"] += n
                log.info(f"  {subpasta}: {n} docs")

        # 3. Arquivos MD raiz (Súmulas, Índices)
        for arq in BASE_TXT.glob("*.md"):
            n = indexar_arquivo(w, arq, "sumulas", "base_txt")
            stats["total"] += n

    log.info(f"ÍNDICE: {stats['total']} documentos indexados em {INDEX_DIR}")
    return stats

# — Busca ——————————————————————————————————————————————
def buscar(query: str, area: str = None, limite: int = 10) -> list[dict]:
    if not index.exists_in(str(INDEX_DIR)):
        log.error("Índice não existe. Rode sem --status primeiro.")
        return []

    ix = index.open_dir(str(INDEX_DIR))
    campos = ["conteudo"]
    parser = MultifieldParser(campos, ix.schema)

    q_str = query
    if area:
        q_str = f"area:{area} AND ({query})"

    with ix.searcher() as s:
        q = parser.parse(q_str)
        hits = s.search(q, limit=limite)
        resultados = []
        for h in hits:
            resultados.append({
                "tribunal": h["tribunal"],
                "area":     h["area"],
                "numero":   h.get("numero", ""),
                "data":     h.get("data", ""),
                "valor":    h.get("valor", ""),
                "arquivo":  h["arquivo"],
                "resumo":   h.get("resumo", "")[:300],
                "score":    round(h.score, 2),
            })
    return resultados

# — CLI ——————————————————————————————————————————————
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--status",  action="store_true", help="ver estado do índice")
    ap.add_argument("--buscar",  help="buscar termo no índice")
    ap.add_argument("--area",    help="filtrar por área (civil, previdenciario...)")
    ap.add_argument("--limite",  type=int, default=10)
    args = ap.parse_args()

    if args.status:
        if index.exists_in(str(INDEX_DIR)):
            ix = index.open_dir(str(INDEX_DIR))
            print(f"Índice OK — {ix.doc_count()} documentos em {INDEX_DIR}")
        else:
            print("Índice NÃO existe. Rode sem argumentos para indexar.")
    elif args.buscar:
        hits = buscar(args.buscar, area=args.area, limite=args.limite)
        for i, h in enumerate(hits, 1):
            print(f"\n[{i}] {h['tribunal']} {h['numero']} — score {h['score']}")
            print(f"    área: {h['area']} | data: {h['data']} | valor: {h['valor']}")
            print(f"    {h['resumo'][:200]}...")
    else:
        stats = indexar_tudo()
        print(f"\nOK — {stats['total']} documentos indexados")
