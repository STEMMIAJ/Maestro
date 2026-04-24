"""
conferir_nomeacoes.py — Confere quais nomeações já estão baixadas localmente.

Entrada: arquivo Markdown/texto com lista de CNJs (20 dígitos ou formatados).
Saída:
  - consolidado/NOMEACOES_JA_TENHO_{data}.csv   (CNJ, onde_encontrado)
  - consolidado/NOMEACOES_FALTA_BAIXAR_{data}.txt (1 CNJ por linha)
  - stdout com resumo

Locais de busca:
  1. ~/Desktop/processos-pje/                  (Mac — 102 PDFs hoje)
  2. ~/Desktop/processos-pje-windows/          (Parallels symlink — quando Windows ativo)
  3. ~/Desktop/ANALISADOR FINAL/processos/     (pasta processada, 190+ CNJs)
  4. _downloads_feitos.json                    (índice dedup do baixar_push_pje.py)

Uso:
    python3 conferir_nomeacoes.py              # usa _input/ mais recente
    python3 conferir_nomeacoes.py arquivo.md   # arquivo específico
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
HOME = Path.home()
DEXTER = HOME / "Desktop" / "STEMMIA Dexter"
PJE_ROOT = DEXTER / "src" / "pje"
INPUT_DIR = PJE_ROOT / "_input"
CONSOLIDADO = PJE_ROOT / "descoberta" / "consolidado"

LOCAIS_BUSCA = [
    HOME / "Desktop" / "processos-pje",
    HOME / "Desktop" / "processos-pje-windows",
    HOME / "Desktop" / "ANALISADOR FINAL" / "processos",
]

DEDUP_INDEX = PJE_ROOT / "download" / "_downloads_feitos.json"

# CNJ formatado: NNNNNNN-NN.AAAA.J.TR.OOOO
RE_CNJ_FMT = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")
# CNJ cru: 20 dígitos
RE_CNJ_CRU = re.compile(r"\b\d{20}\b")


# ─────────────────────────────────────────────
# Normalização
# ─────────────────────────────────────────────
def normalizar(s: str) -> str | None:
    """Converte qualquer forma em CNJ formatado, ou None se inválido."""
    digitos = "".join(c for c in s if c.isdigit())
    if len(digitos) != 20:
        return None
    return f"{digitos[:7]}-{digitos[7:9]}.{digitos[9:13]}.{digitos[13]}.{digitos[14:16]}.{digitos[16:20]}"


def extrair_cnjs(texto: str) -> List[str]:
    """Extrai todos os CNJs únicos, formatados."""
    encontrados: Set[str] = set()

    for m in RE_CNJ_FMT.finditer(texto):
        norm = normalizar(m.group())
        if norm:
            encontrados.add(norm)

    for m in RE_CNJ_CRU.finditer(texto):
        norm = normalizar(m.group())
        if norm:
            encontrados.add(norm)

    return sorted(encontrados)


# ─────────────────────────────────────────────
# Busca local
# ─────────────────────────────────────────────
def _indice_dedup() -> Set[str]:
    """Lê índice de downloads já feitos (se existir)."""
    if not DEDUP_INDEX.exists():
        return set()
    try:
        data = json.loads(DEDUP_INDEX.read_text(encoding="utf-8"))
        # Formato esperado: {"cnjs": [...]} ou dict com chaves CNJ
        if isinstance(data, dict):
            if "cnjs" in data:
                return {normalizar(c) or c for c in data["cnjs"]}
            return {normalizar(k) or k for k in data.keys()}
        if isinstance(data, list):
            return {normalizar(c) or c for c in data}
    except Exception as e:
        print(f"[aviso] falha lendo {DEDUP_INDEX}: {e}", file=sys.stderr)
    return set()


def _indexar_local(pasta: Path) -> Set[str]:
    """
    Varre uma pasta e indexa todos os CNJs encontrados.
    Aceita: arquivo CNJ.pdf, diretório CNJ/, arquivo com CNJ no nome.
    """
    if not pasta.exists():
        return set()

    encontrados: Set[str] = set()
    try:
        # Não usa rglob profundo: só 1 nível (performance + evita lixo)
        for item in pasta.iterdir():
            nome = item.name
            # Tenta formatado
            m = RE_CNJ_FMT.search(nome)
            if m:
                n = normalizar(m.group())
                if n:
                    encontrados.add(n)
                    continue
            # Tenta cru (raro em nome de arquivo, mas existe)
            m = RE_CNJ_CRU.search(nome)
            if m:
                n = normalizar(m.group())
                if n:
                    encontrados.add(n)
    except PermissionError:
        print(f"[aviso] sem permissão em {pasta}", file=sys.stderr)
    except OSError as e:
        print(f"[aviso] erro lendo {pasta}: {e}", file=sys.stderr)

    return encontrados


def localizar(cnjs_alvo: List[str]) -> Tuple[Dict[str, List[str]], List[str]]:
    """
    Para cada CNJ, retorna lista de locais onde foi encontrado.
    Retorna (ja_tenho, falta).
    """
    indices: Dict[str, Set[str]] = {}
    for pasta in LOCAIS_BUSCA:
        rotulo = str(pasta).replace(str(HOME), "~")
        indices[rotulo] = _indexar_local(pasta)

    dedup = _indice_dedup()
    if dedup:
        indices["_downloads_feitos.json"] = dedup

    ja_tenho: Dict[str, List[str]] = {}
    falta: List[str] = []

    for cnj in cnjs_alvo:
        locais = [rot for rot, conj in indices.items() if cnj in conj]
        if locais:
            ja_tenho[cnj] = locais
        else:
            falta.append(cnj)

    return ja_tenho, falta


# ─────────────────────────────────────────────
# Saída
# ─────────────────────────────────────────────
def salvar_csv_ja_tenho(ja_tenho: Dict[str, List[str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cnj", "locais"])
        for cnj in sorted(ja_tenho.keys()):
            w.writerow([cnj, " | ".join(ja_tenho[cnj])])


def salvar_txt_falta(falta: List[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(falta) + ("\n" if falta else ""), encoding="utf-8")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def arquivo_mais_recente() -> Path | None:
    if not INPUT_DIR.exists():
        return None
    candidatos = sorted(
        [p for p in INPUT_DIR.glob("nomeacoes-*.md")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidatos[0] if candidatos else None


def main(argv: List[str]) -> int:
    if len(argv) > 1:
        entrada = Path(argv[1]).expanduser().resolve()
    else:
        entrada = arquivo_mais_recente()
        if not entrada:
            print(f"ERRO: nenhum arquivo em {INPUT_DIR}", file=sys.stderr)
            return 2

    if not entrada.exists():
        print(f"ERRO: não encontrado: {entrada}", file=sys.stderr)
        return 2

    print(f"[entrada]    {entrada}")
    texto = entrada.read_text(encoding="utf-8")
    cnjs = extrair_cnjs(texto)
    print(f"[CNJs únicos] {len(cnjs)}")

    if not cnjs:
        print("Nenhum CNJ encontrado no arquivo.", file=sys.stderr)
        return 1

    ja_tenho, falta = localizar(cnjs)

    data = datetime.now().strftime("%d%m%Y")
    csv_path = CONSOLIDADO / f"NOMEACOES_JA_TENHO_{data}.csv"
    txt_path = CONSOLIDADO / f"NOMEACOES_FALTA_BAIXAR_{data}.txt"

    salvar_csv_ja_tenho(ja_tenho, csv_path)
    salvar_txt_falta(falta, txt_path)

    print()
    print(f"  Total      : {len(cnjs)}")
    print(f"  Já tenho   : {len(ja_tenho)}")
    print(f"  Falta      : {len(falta)}")
    print()
    print(f"[csv ok]  {csv_path.relative_to(HOME)}")
    print(f"[txt ok]  {txt_path.relative_to(HOME)}")

    if falta:
        print()
        print("Primeiros 10 faltantes:")
        for c in falta[:10]:
            print(f"  - {c}")
        if len(falta) > 10:
            print(f"  ... +{len(falta) - 10}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
