#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
orquestrador.py — pipeline determinístico para ingestão de peças reais do perito.

Fluxo:
  INBOX/<qualquer arquivo> -> (extrair -> normalizar -> classificar -> arquivar -> reportar)

Regras do projeto:
- stdlib-only no caminho crítico; fallbacks opcionais (pdftotext binary, pdfminer.six)
- idempotente: SHA-256 dos bytes crus indexado em _logs/index.jsonl
- CONSTÂNCIA: mesma estrutura de pastas, mesmo frontmatter, mesmo nome por ISO-date + hash curto
- PADRÃO: nunca inventa dados; classificação abaixo do limiar -> AMBIGUO/
- tom dos relatórios: seco, checklist, sem humanização

Uso:
  python3 orquestrador.py                 # roda com config padrão
  python3 orquestrador.py --workers 2     # paralelismo
  python3 orquestrador.py --dry-run       # não move nem escreve, só reporta
  python3 orquestrador.py --inbox /tmp/x  # sobrescreve inbox
  python3 orquestrador.py --rebuild-index # descarta index.jsonl (reprocessa tudo)

Saída por item processado:
  <destino>/<basename>.txt                 (texto normalizado)
  <destino>/<basename>.<ext-original>      (original movido)
  <destino>/<basename>.meta.json           (metadados + score)
  _logs/index.jsonl                        (append-only)
  RELATORIOS/<ISO-ts>.md                   (um relatório por rodada)

Saída global:
  - AMBIGUO/<basename>.*  -> quando score < limiar
  - RELATORIOS/<ts>.md    -> sumário RC + listagem por subtipo
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import traceback
import unicodedata
import zipfile
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constantes de projeto
# ---------------------------------------------------------------------------

__version__ = "0.1.0"
SCRIPT_DIR = Path(__file__).resolve().parent
COWORK_ROOT = SCRIPT_DIR.parent.parent  # .../cowork/
DESTINO_PETICOES = COWORK_ROOT / "02-BIBLIOTECA" / "peticoes" / "_fonte-originais-perito"
DESTINO_LAUDOS = COWORK_ROOT / "02-BIBLIOTECA" / "laudos" / "_fonte-originais-perito"
DESTINO_RESPOSTAS = COWORK_ROOT / "02-BIBLIOTECA" / "respostas" / "_fonte-originais-perito"
DESTINOS_POR_FAMILIA = {
    "peticoes": DESTINO_PETICOES,
    "laudos": DESTINO_LAUDOS,
    "respostas": DESTINO_RESPOSTAS,
}

INBOX_DEFAULT = SCRIPT_DIR / "INBOX"
AMBIGUO_DIR = SCRIPT_DIR / "AMBIGUO"
RELATORIOS_DIR = SCRIPT_DIR / "RELATORIOS"
LOGS_DIR = SCRIPT_DIR / "_logs"
INDEX_FILE = LOGS_DIR / "index.jsonl"
REGRAS_FILE = SCRIPT_DIR / "regras_classificacao.json"

EXTENSOES_SUPORTADAS = {".docx", ".pdf", ".txt", ".md"}

# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------


@dataclass
class ItemProcessado:
    origem: str
    basename: str
    extensao: str
    sha256: str
    bytes_originais: int
    familia: Optional[str] = None
    subtipo: Optional[str] = None
    score: float = 0.0
    scores_top: list = field(default_factory=list)  # [(familia/subtipo, score), ...]
    status: str = "pendente"  # pendente | arquivado | ambiguo | duplicado | erro
    destino_final: Optional[str] = None
    texto_bytes: int = 0
    motivo_erro: Optional[str] = None
    extrator: Optional[str] = None  # docx-zip | pdftotext | pdfminer | text
    timestamp_iso: str = ""


# ---------------------------------------------------------------------------
# Util
# ---------------------------------------------------------------------------


def iso_ts() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H%M%S%z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def slug_basename(nome: str) -> str:
    """Converte 'Aceite - 0038122 - Mantena.docx' -> 'aceite-0038122-mantena'."""
    base = Path(nome).stem
    base = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    return base or "sem-nome"


# ---------------------------------------------------------------------------
# Extratores
# ---------------------------------------------------------------------------


RE_TAGS_XML = re.compile(r"<[^>]+>")
RE_MULTI_WS = re.compile(r"[ \t]+")
RE_MULTI_NL = re.compile(r"\n{3,}")


def extrair_docx(path: Path) -> tuple[str, str]:
    """Retorna (texto, extrator). Usa zipfile + regex sobre word/document.xml."""
    with zipfile.ZipFile(path, "r") as z:
        with z.open("word/document.xml") as f:
            xml = f.read().decode("utf-8", errors="replace")
    # Preserva quebras de parágrafo (w:p) e linhas (w:br) como \n
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:br[^/]*/>", "\n", xml)
    texto = RE_TAGS_XML.sub("", xml)
    return texto, "docx-zip"


def extrair_pdf(path: Path) -> tuple[str, str]:
    """Tenta pdftotext (poppler). Fallback: pdfminer.six. Erro se nenhum disponível."""
    # 1) pdftotext binário
    try:
        out = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"],
            check=True, capture_output=True, timeout=120,
        )
        return out.stdout.decode("utf-8", errors="replace"), "pdftotext"
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    # 2) pdfminer.six (se instalado)
    try:
        from pdfminer.high_level import extract_text  # type: ignore
        return extract_text(str(path)) or "", "pdfminer"
    except Exception:
        raise RuntimeError("Nenhum extrator PDF disponível (pdftotext/pdfminer).")


def extrair_texto_simples(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return data.decode(enc), f"text/{enc}"
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace"), "text/forced-utf8"


def extrair(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower()
    if ext == ".docx":
        return extrair_docx(path)
    if ext == ".pdf":
        return extrair_pdf(path)
    if ext in (".txt", ".md"):
        return extrair_texto_simples(path)
    raise RuntimeError(f"Extensão não suportada: {ext}")


# ---------------------------------------------------------------------------
# Normalização
# ---------------------------------------------------------------------------


def normalizar(texto: str) -> str:
    if not texto:
        return ""
    # Remove BOM isolado
    texto = texto.lstrip("\ufeff")
    # Unicode NFC (preserva acentos, elimina combinações duplicadas)
    texto = unicodedata.normalize("NFC", texto)
    # Colapsa espaços horizontais
    texto = RE_MULTI_WS.sub(" ", texto)
    # Normaliza quebras >=3 para 2
    texto = RE_MULTI_NL.sub("\n\n", texto)
    # Strip por linha
    linhas = [ln.rstrip() for ln in texto.splitlines()]
    # Remove linhas totalmente vazias no topo/base
    while linhas and not linhas[0].strip():
        linhas.pop(0)
    while linhas and not linhas[-1].strip():
        linhas.pop()
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Classificação
# ---------------------------------------------------------------------------


def carregar_regras() -> dict:
    with open(REGRAS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def classificar(texto: str, regras: dict) -> tuple[Optional[str], Optional[str], float, list]:
    """Retorna (familia, subtipo, score, top_N). Se score < limiar, familia/subtipo = None."""
    meta = regras.get("_meta", {})
    limiar = float(meta.get("limiar_geral", 3))
    titulo_bonus = float(meta.get("titulo_bonus", 5))
    max_linhas_titulo = int(meta.get("max_linhas_titulo", 6))

    linhas = texto.splitlines()
    titulo = "\n".join(linhas[:max_linhas_titulo]).lower()
    corpo = texto.lower()

    scores: list[tuple[str, str, float]] = []  # (familia, subtipo, score)

    for familia, fconf in regras.get("familias", {}).items():
        for subtipo, sconf in fconf.get("subtipos", {}).items():
            score = 0.0
            # Título (bônus)
            titulo_regex = sconf.get("titulo_regex")
            if titulo_regex and re.search(titulo_regex, titulo):
                score += titulo_bonus
            # Palavras-chave positivas (1 ponto por ocorrência de cada termo, cap 3 por termo)
            for termo in sconf.get("palavras_chave_positivas", []):
                c = corpo.count(termo.lower())
                if c:
                    score += min(c, 3)
            # Antônimos (penaliza 2 por ocorrência, cap 4)
            for termo in sconf.get("antonimos", []):
                c = corpo.count(termo.lower())
                if c:
                    score -= min(c * 2, 4)
            scores.append((familia, subtipo, score))

    scores.sort(key=lambda t: t[2], reverse=True)
    top = [(f"{f}/{s}", sc) for f, s, sc in scores[:5]]
    if not scores:
        return None, None, 0.0, top
    melhor_f, melhor_s, melhor_score = scores[0]
    if melhor_score < limiar:
        return None, None, melhor_score, top
    return melhor_f, melhor_s, melhor_score, top


# ---------------------------------------------------------------------------
# Índice de idempotência
# ---------------------------------------------------------------------------


def carregar_sha_index() -> set:
    if not INDEX_FILE.exists():
        return set()
    hashes = set()
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            try:
                obj = json.loads(linha)
                if "sha256" in obj:
                    hashes.add(obj["sha256"])
            except json.JSONDecodeError:
                continue
    return hashes


def anexar_index(item: ItemProcessado) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Pipeline por item
# ---------------------------------------------------------------------------


def processar(path: Path, regras: dict, sha_cache: set, dry_run: bool) -> ItemProcessado:
    item = ItemProcessado(
        origem=str(path),
        basename=slug_basename(path.name),
        extensao=path.suffix.lower(),
        sha256="",
        bytes_originais=0,
        timestamp_iso=iso_ts(),
    )

    if path.suffix.lower() not in EXTENSOES_SUPORTADAS:
        item.status = "erro"
        item.motivo_erro = f"Extensão não suportada: {item.extensao}"
        return item

    try:
        data = path.read_bytes()
        item.bytes_originais = len(data)
        item.sha256 = sha256_bytes(data)

        if item.sha256 in sha_cache:
            item.status = "duplicado"
            return item

        texto, extrator = extrair(path)
        item.extrator = extrator
        texto_norm = normalizar(texto)
        item.texto_bytes = len(texto_norm.encode("utf-8"))

        familia, subtipo, score, top = classificar(texto_norm, regras)
        item.score = score
        item.scores_top = top

        if familia and subtipo:
            item.familia = familia
            item.subtipo = subtipo
            destino_base = DESTINOS_POR_FAMILIA[familia] / subtipo
        else:
            item.status = "ambiguo"
            destino_base = AMBIGUO_DIR

        if not dry_run:
            destino_base.mkdir(parents=True, exist_ok=True)
            sha_curto = item.sha256[:8]
            nome_base = f"{item.basename}-{sha_curto}"
            txt_path = destino_base / f"{nome_base}.txt"
            meta_path = destino_base / f"{nome_base}.meta.json"
            original_path = destino_base / f"{nome_base}{item.extensao}"

            txt_path.write_text(texto_norm, encoding="utf-8")
            meta_path.write_text(
                json.dumps(asdict(item), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            shutil.move(str(path), str(original_path))
            item.destino_final = str(destino_base)

        if item.status != "ambiguo":
            item.status = "arquivado"

    except Exception as e:
        item.status = "erro"
        item.motivo_erro = f"{type(e).__name__}: {e}"
        # Anexa traceback em debug
        sys.stderr.write(
            f"[ERRO] {path.name}\n{traceback.format_exc()}\n"
        )

    return item


# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------


def gerar_relatorio(itens: list, ts: str, dry_run: bool) -> Path:
    RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)
    rel_path = RELATORIOS_DIR / f"{ts.replace(':', '').replace('+', 'p')}.md"

    total = len(itens)
    por_status: dict[str, int] = {}
    por_subtipo: dict[str, int] = {}
    ambiguos: list = []
    erros: list = []

    for it in itens:
        por_status[it.status] = por_status.get(it.status, 0) + 1
        if it.familia and it.subtipo:
            chave = f"{it.familia}/{it.subtipo}"
            por_subtipo[chave] = por_subtipo.get(chave, 0) + 1
        if it.status == "ambiguo":
            ambiguos.append(it)
        if it.status == "erro":
            erros.append(it)

    linhas = [
        f"# Relatório da rodada — {ts}",
        "",
        f"**Versão do orquestrador:** {__version__}",
        f"**Modo:** {'dry-run' if dry_run else 'produção'}",
        f"**Total de itens:** {total}",
        "",
        "## Contagem por status",
    ]
    for st, n in sorted(por_status.items()):
        linhas.append(f"- {st}: {n}")
    linhas += ["", "## Contagem por subtipo"]
    if por_subtipo:
        for k, v in sorted(por_subtipo.items(), key=lambda x: -x[1]):
            linhas.append(f"- {k}: {v}")
    else:
        linhas.append("_(nenhum)_")

    linhas += ["", "## Itens"]
    linhas.append("| Arquivo | Extrator | Família/Subtipo | Score | Status | Destino |")
    linhas.append("|---|---|---|---|---|---|")
    for it in itens:
        fs = f"{it.familia}/{it.subtipo}" if it.familia else "-"
        dest = it.destino_final or "-"
        # Encurta caminho do destino
        dest_display = dest.replace(str(COWORK_ROOT), "cowork") if dest != "-" else "-"
        linhas.append(
            f"| `{Path(it.origem).name}` | {it.extrator or '-'} | {fs} | {it.score:.1f} | {it.status} | {dest_display} |"
        )

    if ambiguos:
        linhas += ["", "## Ambíguos — top 3 por item"]
        for it in ambiguos:
            linhas.append(f"- `{Path(it.origem).name}`")
            for chave, sc in it.scores_top[:3]:
                linhas.append(f"  - {chave}: {sc:.1f}")

    if erros:
        linhas += ["", "## Erros"]
        for it in erros:
            linhas.append(f"- `{Path(it.origem).name}`: {it.motivo_erro}")

    rel_path.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return rel_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def listar_candidatos(inbox: Path) -> list:
    if not inbox.exists():
        return []
    out = []
    for p in inbox.rglob("*"):
        if p.is_file() and p.suffix.lower() in EXTENSOES_SUPORTADAS:
            out.append(p)
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Orquestrador de ingestão de peças reais.")
    ap.add_argument("--inbox", type=Path, default=INBOX_DEFAULT)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rebuild-index", action="store_true")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    # Pré-criação de pastas
    for d in (AMBIGUO_DIR, RELATORIOS_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    if args.rebuild_index and INDEX_FILE.exists() and not args.dry_run:
        bak = INDEX_FILE.with_suffix(f".jsonl.bak-{iso_ts()}")
        INDEX_FILE.rename(bak)
        sys.stderr.write(f"[INFO] index.jsonl movido para {bak.name}\n")

    regras = carregar_regras()
    sha_cache = carregar_sha_index()

    candidatos = listar_candidatos(args.inbox)
    if args.verbose:
        sys.stderr.write(f"[INFO] Inbox: {args.inbox}\n")
        sys.stderr.write(f"[INFO] Candidatos: {len(candidatos)}\n")
        sys.stderr.write(f"[INFO] SHAs já processados: {len(sha_cache)}\n")

    if not candidatos:
        sys.stderr.write(f"[INFO] Nenhum arquivo em {args.inbox}\n")
        rel = gerar_relatorio([], iso_ts(), args.dry_run)
        print(f"Relatório: {rel}")
        return 0

    ts_run = iso_ts()
    resultados: list = []
    with cf.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(processar, p, regras, sha_cache, args.dry_run): p for p in candidatos}
        for f in cf.as_completed(futs):
            item = f.result()
            resultados.append(item)
            if not args.dry_run and item.status in ("arquivado", "ambiguo"):
                anexar_index(item)

    rel = gerar_relatorio(resultados, ts_run, args.dry_run)
    ok = sum(1 for r in resultados if r.status == "arquivado")
    amb = sum(1 for r in resultados if r.status == "ambiguo")
    dup = sum(1 for r in resultados if r.status == "duplicado")
    err = sum(1 for r in resultados if r.status == "erro")
    print(
        f"RESUMO: total={len(resultados)} arquivados={ok} ambiguos={amb} duplicados={dup} erros={err}"
    )
    print(f"Relatório: {rel}")
    return 0 if err == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
