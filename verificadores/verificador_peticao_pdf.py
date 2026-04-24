#!/usr/bin/env python3
"""
verificador_peticao_pdf.py — rastreabilidade afirmacao -> trecho-fonte.

Le uma peticao em Markdown, extrai afirmacoes factuais e verifica cada uma
contra o corpus TEXTO-EXTRAIDO.txt do processo, produzindo relatorio
JSON + Markdown e exit code que bloqueia entregas sem ancora.

Uso:
    verificador_peticao_pdf.py --peticao <peticao.md> \\
        --processo <pasta-do-CNJ> \\
        [--threshold-ancorada 85] [--threshold-suspeita 60] \\
        [--out-dir <pasta>] [--dry-run] [--verbose]

Status de cada afirmacao:
    ANCORADA        score >= threshold-ancorada
    SUSPEITA        threshold-suspeita <= score < threshold-ancorada
    SEM-ANCORA      score < threshold-suspeita
    CITACAO_LEGAL   sentenca e apenas citacao de lei/artigo (skip)

Exit code:
    0  tudo ANCORADA/CITACAO_LEGAL
    1  ha SUSPEITA mas zero SEM-ANCORA (warning)
    2  ha pelo menos uma SEM-ANCORA (bloqueia pipeline)
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Dependencia opcional: rapidfuzz
# ---------------------------------------------------------------------------
try:
    from rapidfuzz import fuzz as _rf_fuzz  # type: ignore
    RAPIDFUZZ_OK = True
except ImportError:
    _rf_fuzz = None
    RAPIDFUZZ_OK = False


# ---------------------------------------------------------------------------
# Configuracao / logging
# ---------------------------------------------------------------------------
LOG = logging.getLogger("verificador")

SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])")
HEADER_RE = re.compile(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9\s\-:]{1,60}$")
SAUDACAO_RE = re.compile(
    r"^(excelent[íi]ssim|merit[íi]ssim|il[íu]strissim|egr[ée]gio|colendo|digno|nobre)",
    re.IGNORECASE,
)
CITACAO_LEGAL_RE = re.compile(
    r"(art(?:\.|igo)\s*\d+|cpc|cpp|cf/88|lei\s+n?o?\.?\s*\d|s[úu]mula\s+\d|constitui[çc][ãa]o)",
    re.IGNORECASE,
)
PAGINA_MARKER_RE = re.compile(r"<<<\s*P[ÁA]GINA\s+(\d+)\s*>>>", re.IGNORECASE)
CNJ_RE = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")

MIN_SENTENCE_LEN = 15
WINDOW_SIZE = 500
WINDOW_STEP = 250
CONTEXT_PAD = 80


# ---------------------------------------------------------------------------
# Utilitarios
# ---------------------------------------------------------------------------
def _normalize(texto: str) -> str:
    """Lowercase, sem acento, whitespace collapsado."""
    nfkd = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento.lower()).strip()


def _load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def _extract_cnj_from_path(processo: Path) -> str:
    match = CNJ_RE.search(processo.name)
    if match:
        return match.group(0)
    for parent in processo.parents:
        match = CNJ_RE.search(parent.name)
        if match:
            return match.group(0)
    return processo.name


# ---------------------------------------------------------------------------
# Extracao de afirmacoes
# ---------------------------------------------------------------------------
def extrair_afirmacoes(peticao_texto: str) -> List[str]:
    """Split por sentencas + filtros de cabecalho/saudacao/curtas."""
    # Remove blocos markdown (codigo, titulos de 1 linha)
    linhas_limpas: List[str] = []
    for linha in peticao_texto.splitlines():
        stripped = linha.strip()
        if not stripped:
            linhas_limpas.append("")
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("```"):
            continue
        if stripped.startswith(">"):
            stripped = stripped.lstrip("> ").strip()
        # Descarta linhas HEADER curtas totalmente em caixa alta
        if len(stripped) < 60 and HEADER_RE.match(stripped):
            continue
        linhas_limpas.append(stripped)

    texto = " ".join(l for l in linhas_limpas if l)
    bruto = SENT_SPLIT_RE.split(texto)

    afirmacoes: List[str] = []
    for sent in bruto:
        s = sent.strip()
        if len(s) < MIN_SENTENCE_LEN:
            continue
        if SAUDACAO_RE.match(s):
            continue
        afirmacoes.append(s)

    return afirmacoes


def is_citacao_legal(afirmacao: str) -> bool:
    """Heuristica: sentenca com alta densidade de referencia legal e pouco fato."""
    if not CITACAO_LEGAL_RE.search(afirmacao):
        return False
    # Se a sentenca e curta e tem ref legal, trata como citacao
    if len(afirmacao) < 120:
        return True
    # Sentenca longa com mais de 2 marcadores legais tambem vira citacao
    marcadores = len(CITACAO_LEGAL_RE.findall(afirmacao))
    return marcadores >= 2


# ---------------------------------------------------------------------------
# Paginas
# ---------------------------------------------------------------------------
def construir_indice_paginas(corpus: str) -> List[Tuple[int, int]]:
    """Lista de (offset_inicio, numero_pagina) a partir dos marcadores."""
    indices: List[Tuple[int, int]] = []
    for m in PAGINA_MARKER_RE.finditer(corpus):
        indices.append((m.end(), int(m.group(1))))
    return indices


def pagina_de_offset(offset: int, indice: List[Tuple[int, int]]) -> Optional[int]:
    if not indice:
        return None
    atual: Optional[int] = None
    for ini, pag in indice:
        if ini <= offset:
            atual = pag
        else:
            break
    return atual


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------
def _fuzz_partial_ratio(a: str, b: str) -> float:
    """Wrapper: usa rapidfuzz se disponivel; fallback simples caso contrario."""
    if _rf_fuzz is not None:
        return float(_rf_fuzz.partial_ratio(a, b))
    # Fallback: longest common substring ratio (aproximacao grosseira)
    if not a or not b:
        return 0.0
    if a in b:
        return 100.0
    # Heuristica: proporcao de tokens de `a` presentes em `b`
    toks_a = [t for t in a.split() if len(t) >= 4]
    if not toks_a:
        return 0.0
    hits = sum(1 for t in toks_a if t in b)
    return (hits / len(toks_a)) * 100.0


def buscar_ancora(
    afirmacao: str,
    corpus_norm: str,
    corpus_orig: str,
) -> Tuple[float, int, str]:
    """
    Retorna (score, offset_no_original, trecho_contexto).

    Tenta substring exata (normalizada); se falhar, janelas deslizantes com
    rapidfuzz.partial_ratio.
    """
    alvo = _normalize(afirmacao)
    if not alvo:
        return 0.0, -1, ""

    # 1) Substring exata na versao normalizada
    pos_norm = corpus_norm.find(alvo)
    if pos_norm >= 0:
        # Mapear pos_norm -> offset no corpus_orig e' aproximado.
        # Usamos proporcao (bom o suficiente para exibicao de contexto).
        if len(corpus_norm) > 0:
            ratio = pos_norm / len(corpus_norm)
            off = int(ratio * len(corpus_orig))
        else:
            off = 0
        trecho = _extrair_contexto(corpus_orig, off, len(afirmacao))
        return 100.0, off, trecho

    # 2) Janelas deslizantes
    melhor_score = 0.0
    melhor_offset = -1
    tamanho = len(corpus_norm)
    if tamanho == 0:
        return 0.0, -1, ""

    for inicio in range(0, tamanho, WINDOW_STEP):
        fim = min(inicio + WINDOW_SIZE, tamanho)
        janela = corpus_norm[inicio:fim]
        score = _fuzz_partial_ratio(alvo, janela)
        if score > melhor_score:
            melhor_score = score
            melhor_offset = inicio
        if score >= 99.0:
            break

    if melhor_offset < 0:
        return melhor_score, -1, ""

    # Aproximacao offset_norm -> offset_orig
    ratio = melhor_offset / max(1, tamanho)
    off_orig = int(ratio * len(corpus_orig))
    trecho = _extrair_contexto(corpus_orig, off_orig, len(afirmacao))
    return melhor_score, off_orig, trecho


def _extrair_contexto(corpus: str, offset: int, alvo_len: int) -> str:
    ini = max(0, offset - CONTEXT_PAD)
    fim = min(len(corpus), offset + alvo_len + CONTEXT_PAD)
    trecho = corpus[ini:fim].replace("\n", " ")
    return re.sub(r"\s+", " ", trecho).strip()


# ---------------------------------------------------------------------------
# Classificacao
# ---------------------------------------------------------------------------
def classificar(score: float, th_ancorada: float, th_suspeita: float) -> str:
    if score >= th_ancorada:
        return "ANCORADA"
    if score >= th_suspeita:
        return "SUSPEITA"
    return "SEM-ANCORA"


def veredito_global(totais: Dict[str, int]) -> str:
    if totais["sem_ancora"] > 0:
        return "BLOQUEADA"
    if totais["suspeitas"] > 0:
        return "REVISAR"
    return "APROVADA"


# ---------------------------------------------------------------------------
# Relatorios
# ---------------------------------------------------------------------------
def gerar_markdown(payload: Dict) -> str:
    t = payload["totais"]
    linhas = [
        f"# Relatorio de Verificacao — {payload.get('cnj', '?')}",
        "",
        f"- Peticao: `{payload['peticao_path']}`",
        f"- Processo: `{payload['processo_path']}`",
        f"- Gerado em: {payload['gerado_em']}",
        f"- Veredito: **{payload['veredito_global']}**",
        "",
        "## Totais",
        "",
        f"- Total de afirmacoes: {t['total']}",
        f"- ANCORADAS: {t['ancoradas']}",
        f"- SUSPEITAS: {t['suspeitas']}",
        f"- SEM-ANCORA: {t['sem_ancora']}",
        f"- CITACOES LEGAIS (skip): {t['citacoes_legais']}",
        "",
        "## Afirmacoes",
        "",
        "| # | Status | Score | Pag. | Afirmacao | Ancora |",
        "|---|--------|-------|------|-----------|--------|",
    ]
    for af in payload["afirmacoes"]:
        texto = af["texto_original"].replace("|", "\\|")
        ancora = (af.get("ancora_trecho") or "").replace("|", "\\|")
        if len(texto) > 120:
            texto = texto[:117] + "..."
        if len(ancora) > 120:
            ancora = ancora[:117] + "..."
        pag = af.get("pagina")
        pag_str = str(pag) if pag is not None else "-"
        linhas.append(
            f"| {af['id']} | {af['status']} | {af['score']:.1f} | {pag_str} | {texto} | {ancora} |"
        )
    linhas.append("")
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------
def verificar(
    peticao_path: Path,
    processo_path: Path,
    th_ancorada: float,
    th_suspeita: float,
) -> Dict:
    peticao_texto = _load_text(peticao_path)
    corpus_path = processo_path / "TEXTO-EXTRAIDO.txt"
    corpus_orig = _load_text(corpus_path)
    corpus_norm = _normalize(corpus_orig)
    indice_pag = construir_indice_paginas(corpus_orig)

    afirmacoes = extrair_afirmacoes(peticao_texto)
    LOG.info("Extraidas %d sentencas candidatas da peticao", len(afirmacoes))

    resultados: List[Dict] = []
    totais = {
        "ancoradas": 0,
        "suspeitas": 0,
        "sem_ancora": 0,
        "citacoes_legais": 0,
        "total": len(afirmacoes),
    }

    for idx, af in enumerate(afirmacoes, start=1):
        if is_citacao_legal(af):
            resultados.append({
                "id": idx,
                "texto_original": af,
                "status": "CITACAO_LEGAL",
                "score": 0.0,
                "ancora_trecho": None,
                "pagina": None,
                "threshold_aplicado": None,
            })
            totais["citacoes_legais"] += 1
            LOG.info("[%d/%d] CITACAO_LEGAL: %s", idx, len(afirmacoes), af[:80])
            continue

        score, offset, trecho = buscar_ancora(af, corpus_norm, corpus_orig)
        status = classificar(score, th_ancorada, th_suspeita)
        pagina = pagina_de_offset(offset, indice_pag) if offset >= 0 else None

        resultados.append({
            "id": idx,
            "texto_original": af,
            "status": status,
            "score": round(score, 2),
            "ancora_trecho": trecho if trecho else None,
            "pagina": pagina,
            "threshold_aplicado": th_ancorada,
        })

        if status == "ANCORADA":
            totais["ancoradas"] += 1
        elif status == "SUSPEITA":
            totais["suspeitas"] += 1
        else:
            totais["sem_ancora"] += 1

        LOG.info("[%d/%d] %s (score=%.1f): \"%s\"",
                 idx, len(afirmacoes), status, score, af[:80])

    payload = {
        "peticao_path": str(peticao_path),
        "processo_path": str(processo_path),
        "cnj": _extract_cnj_from_path(processo_path),
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "totais": totais,
        "veredito_global": veredito_global(totais),
        "afirmacoes": resultados,
    }
    return payload


def escrever_saida(payload: Dict, out_dir: Path, dry_run: bool) -> None:
    json_path = out_dir / "RELATORIO-VERIFICACAO.json"
    md_path = out_dir / "RELATORIO-VERIFICACAO.md"
    if dry_run:
        LOG.info("[DRY] escreveria: %s", json_path)
        LOG.info("[DRY] escreveria: %s", md_path)
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md_path.write_text(gerar_markdown(payload), encoding="utf-8")
    LOG.info("Escrito: %s", json_path)
    LOG.info("Escrito: %s", md_path)


def computar_exit_code(payload: Dict) -> int:
    t = payload["totais"]
    if t["sem_ancora"] > 0:
        return 2
    if t["suspeitas"] > 0:
        return 1
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifica se afirmacoes de peticao tem ancora no TEXTO-EXTRAIDO do processo."
    )
    parser.add_argument("--peticao", required=True, help="Caminho do peticao.md")
    parser.add_argument("--processo", required=True,
                        help="Pasta do CNJ contendo TEXTO-EXTRAIDO.txt")
    parser.add_argument("--threshold-ancorada", type=float, default=85.0)
    parser.add_argument("--threshold-suspeita", type=float, default=60.0)
    parser.add_argument("--out-dir", default=None,
                        help="Pasta de saida (default: mesma do processo)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Nao escreve arquivos, so relata")
    parser.add_argument("--verbose", action="store_true", help="DEBUG logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )

    if not RAPIDFUZZ_OK:
        LOG.warning(
            "rapidfuzz indisponivel — usando fallback aproximado. "
            "Instale com: pip install rapidfuzz"
        )

    peticao_path = Path(args.peticao).expanduser().resolve()
    processo_path = Path(args.processo).expanduser().resolve()

    if not peticao_path.is_file():
        LOG.error("Peticao nao encontrada: %s", peticao_path)
        return 3
    if not processo_path.is_dir():
        LOG.error("Pasta do processo nao e diretorio: %s", processo_path)
        return 3
    if not (processo_path / "TEXTO-EXTRAIDO.txt").exists():
        LOG.error("TEXTO-EXTRAIDO.txt ausente em: %s", processo_path)
        return 3

    if args.threshold_suspeita >= args.threshold_ancorada:
        LOG.error("threshold-suspeita deve ser < threshold-ancorada")
        return 3

    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else processo_path

    try:
        payload = verificar(
            peticao_path,
            processo_path,
            args.threshold_ancorada,
            args.threshold_suspeita,
        )
    except FileNotFoundError as exc:
        LOG.error("%s", exc)
        return 3

    escrever_saida(payload, out_dir, args.dry_run)

    t = payload["totais"]
    LOG.info(
        "Resumo: total=%d ancoradas=%d suspeitas=%d sem_ancora=%d citacoes=%d veredito=%s",
        t["total"], t["ancoradas"], t["suspeitas"], t["sem_ancora"],
        t["citacoes_legais"], payload["veredito_global"],
    )

    return computar_exit_code(payload)


if __name__ == "__main__":
    raise SystemExit(main())
