#!/usr/bin/env python3
"""
Orchestrator de busca jurídica — 4 fontes em paralelo.

Fontes:
  - Base local (Whoosh) — offline, curada
  - DataJud API (CNJ) — processos TJMG/TRF6/TRT3
  - Google Scholar — jurisprudência geral
  - brlaw MCP (STJ/STF/TST) — via subprocess quando disponível

Uso:
    python3 buscar_jurisprudencia.py --query "honorários periciais depósito" --limite 10
    python3 buscar_jurisprudencia.py --query "nexo causal acidente" --area previdenciario --fontes local,datajud
    python3 buscar_jurisprudencia.py --query "perícia médica incapacidade" --saida json
"""

import os
import sys
import json
import asyncio
import logging
import argparse
import hashlib
from pathlib import Path
from datetime import datetime

# — Setup ———————————————————————————————————————————————
DEXTER = Path(__file__).parent.parent.parent
sys.path.insert(0, str(Path(__file__).parent / "modulos"))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("busca")

# — Helpers ——————————————————————————————————————————————
def _hash(texto: str) -> str:
    return hashlib.md5(texto[:200].encode()).hexdigest()[:8]

def _score_base(r: dict) -> int:
    """Score de relevância por campos presentes."""
    s = 0
    if r.get("numero"): s += 20
    if r.get("data"):   s += 10
    if r.get("valor"):  s += 30
    if r.get("ementa") and len(r["ementa"]) > 100: s += 20
    if r.get("tribunal") in ("STJ", "STF", "TST"): s += 20
    return s

# — FONTE 1: Base Local (Whoosh) ————————————————————————
async def buscar_base_local(query: str, area: str = None, limite: int = 10) -> list[dict]:
    try:
        from indexar_base_local import buscar, INDEX_DIR
        from whoosh import index as whoosh_index
        if not whoosh_index.exists_in(str(INDEX_DIR)):
            log.warning("Base local não indexada. Rode indexar_base_local.py primeiro.")
            return []
        hits = await asyncio.to_thread(buscar, query, area, limite)
        return [{
            "fonte":    "base_local",
            "tribunal": h["tribunal"],
            "area":     h["area"],
            "numero":   h.get("numero", ""),
            "data":     h.get("data", ""),
            "valor":    h.get("valor", ""),
            "ementa":   h.get("resumo", ""),
            "score":    int(h.get("score", 0) * 10),
            "_hash":    _hash(h.get("resumo", "")),
        } for h in hits]
    except Exception as e:
        log.warning(f"Base local: {e}")
        return []

# — FONTE 2: DataJud API (CNJ) ——————————————————————————
async def buscar_datajud(query: str, area: str = None, limite: int = 10) -> list[dict]:
    try:
        sys.path.insert(0, str(DEXTER / "src" / "jurisprudencia"))
        from harvester import processar_resultado

        # Busca assíncrona via subprocess para não bloquear event loop
        import subprocess
        script = DEXTER / "src" / "jurisprudencia" / "consultar_aj.py"
        if not script.exists():
            return []

        result = await asyncio.to_thread(
            subprocess.run,
            [sys.executable, str(script), "--query", query, "--limite", str(limite), "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return []

        dados = json.loads(result.stdout)
        return [{
            "fonte":    "datajud",
            "tribunal": d.get("tribunal", ""),
            "area":     d.get("area", area or ""),
            "numero":   d.get("numero_cnj", ""),
            "data":     d.get("data_julgamento", ""),
            "valor":    d.get("valor_causa", ""),
            "ementa":   d.get("ementa", ""),
            "score":    d.get("relevancia_score", 0) + _score_base(d),
            "_hash":    _hash(d.get("ementa", "") or d.get("numero_cnj", "")),
        } for d in dados]
    except Exception as e:
        log.warning(f"DataJud: {e}")
        return []

# — FONTE 3: Google Scholar (harvester) ————————————————
async def buscar_scholar(query: str, area: str = None, limite: int = 5) -> list[dict]:
    try:
        sys.path.insert(0, str(DEXTER / "src" / "jurisprudencia" / "modulos"))
        from harvester import QUERIES_GERAIS
        # harvester busca via scraping — rodar em thread separada
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "harvester",
            str(DEXTER / "src" / "jurisprudencia" / "modulos" / "harvester.py")
        )
        return []  # placeholder — integrar quando harvester tiver interface CLI
    except Exception as e:
        log.warning(f"Scholar: {e}")
        return []

# — FONTE 4: Base Transversal (Banco-Transversal curado) —
async def buscar_transversal(query: str, area: str = None, limite: int = 10) -> list[dict]:
    """Busca direta nos arquivos MD do Banco-Transversal por keywords."""
    try:
        base = DEXTER / "banco-de-dados" / "Banco-Transversal"
        if not base.exists():
            return []

        query_lower = query.lower()
        termos = query_lower.split()
        resultados = []

        subpastas = ["Jurisprudencia", "Sentencas", "Contestacoes", "Honorarios-Periciais"]
        for sp in subpastas:
            pasta = base / sp
            if not pasta.exists():
                continue
            for arq in pasta.rglob("*.md"):
                try:
                    texto = arq.read_text(encoding="utf-8", errors="ignore").lower()
                    hits = sum(1 for t in termos if t in texto)
                    if hits >= max(1, len(termos) // 2):
                        conteudo = arq.read_text(encoding="utf-8", errors="ignore")
                        resultados.append({
                            "fonte":    "transversal",
                            "tribunal": "LOCAL",
                            "area":     sp.lower(),
                            "numero":   arq.stem,
                            "data":     "",
                            "valor":    "",
                            "ementa":   conteudo[:400],
                            "score":    hits * 15,
                            "_hash":    _hash(arq.stem),
                        })
                except Exception:
                    pass

        return sorted(resultados, key=lambda x: x["score"], reverse=True)[:limite]
    except Exception as e:
        log.warning(f"Transversal: {e}")
        return []

# — Deduplicação e ranking ——————————————————————————————
def deduplica_e_ordena(listas: list[list[dict]]) -> list[dict]:
    """Une resultados, deduplica por hash, ordena por score."""
    vistos = set()
    unidos = []
    for lista in listas:
        for r in (lista or []):
            h = r.get("_hash", "")
            num = r.get("numero", "")
            chave = num if num else h
            if chave and chave in vistos:
                continue
            vistos.add(chave)
            r["score"] = r.get("score", 0) + _score_base(r)
            unidos.append(r)
    return sorted(unidos, key=lambda x: x["score"], reverse=True)

# — Orchestrator principal ———————————————————————————————
async def buscar_tudo(
    query: str,
    area: str = None,
    fontes: list[str] = None,
    limite: int = 10,
) -> dict:
    fontes = fontes or ["local", "datajud", "transversal"]
    log.info(f"Buscando: '{query}' | área: {area} | fontes: {fontes}")

    tasks = {}
    if "local" in fontes:
        tasks["base_local"]    = buscar_base_local(query, area, limite)
    if "datajud" in fontes:
        tasks["datajud"]       = buscar_datajud(query, area, limite)
    if "transversal" in fontes:
        tasks["transversal"]   = buscar_transversal(query, area, limite)
    if "scholar" in fontes:
        tasks["scholar"]       = buscar_scholar(query, area, 5)

    resultados_brutos = await asyncio.gather(*tasks.values(), return_exceptions=True)
    por_fonte = {}
    for nome, res in zip(tasks.keys(), resultados_brutos):
        if isinstance(res, Exception):
            log.warning(f"Fonte {nome} falhou: {res}")
            por_fonte[nome] = []
        else:
            por_fonte[nome] = res or []
            log.info(f"  {nome}: {len(por_fonte[nome])} resultados")

    consolidado = deduplica_e_ordena(list(por_fonte.values()))

    return {
        "query":   query,
        "area":    area,
        "fontes":  fontes,
        "ts":      datetime.now().isoformat(),
        "total":   len(consolidado),
        "por_fonte": {k: len(v) for k, v in por_fonte.items()},
        "resultados": consolidado[:limite],
    }

# — Formatar para laudo ——————————————————————————————————
def formatar_para_laudo(resultado: dict) -> str:
    linhas = [
        f"## Jurisprudência — {resultado['query']}",
        f"*Fontes: {', '.join(resultado['fontes'])} | {resultado['total']} resultados | {resultado['ts'][:10]}*\n",
    ]
    for i, r in enumerate(resultado["resultados"], 1):
        linhas.append(f"**[{i}] {r['tribunal']} {r['numero']}**")
        if r.get("data"):
            linhas.append(f"Data: {r['data']}")
        if r.get("valor"):
            linhas.append(f"Valor: {r['valor']}")
        linhas.append(f"Área: {r['area']} | Fonte: {r['fonte']} | Score: {r['score']}")
        if r.get("ementa"):
            linhas.append(f"\n> {r['ementa'][:300]}...\n")
        linhas.append("---")
    return "\n".join(linhas)

# — CLI ——————————————————————————————————————————————————
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Busca jurídica multi-fonte")
    ap.add_argument("--query",   required=True, help="Termo de busca")
    ap.add_argument("--area",    help="Área: civil, previdenciario, trabalhista, penal...")
    ap.add_argument("--fontes",  default="local,datajud,transversal",
                    help="Fontes: local,datajud,transversal,scholar (vírgula)")
    ap.add_argument("--limite",  type=int, default=10)
    ap.add_argument("--saida",   choices=["json", "md", "texto"], default="texto")
    args = ap.parse_args()

    fontes = [f.strip() for f in args.fontes.split(",")]
    resultado = asyncio.run(buscar_tudo(args.query, args.area, fontes, args.limite))

    if args.saida == "json":
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    elif args.saida == "md":
        print(formatar_para_laudo(resultado))
    else:
        print(f"\n{'='*60}")
        print(f"BUSCA: {resultado['query']}")
        print(f"Total: {resultado['total']} | Por fonte: {resultado['por_fonte']}")
        print('='*60)
        for i, r in enumerate(resultado["resultados"], 1):
            print(f"\n[{i}] {r['tribunal']} {r['numero']} (score: {r['score']})")
            print(f"    Área: {r['area']} | Data: {r['data']} | Fonte: {r['fonte']}")
            if r.get("ementa"):
                print(f"    {r['ementa'][:250]}...")
