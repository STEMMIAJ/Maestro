#!/usr/bin/env python3
"""
SCRIPT 3 — Cruzar listas de processos PJe TJMG
================================================
Puro Python. NÃO usa Selenium. Roda offline.

Lê:
  output/expedientes_raw.csv
  output/acervo_raw.csv
  output/push_raw.csv

Gera:
  output/processos_unificados.csv
  output/resumo_fontes.csv

Como rodar:
  python cruzar_listas_processos.py

Pré-requisito: rodar os Scripts 1 e 2 antes.
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

OUTPUT_DIR = Path(__file__).parent / "output"
DATA_COLETA = datetime.now().strftime("%Y-%m-%d %H:%M")

ARQUIVOS = {
    "expedientes": OUTPUT_DIR / "expedientes_raw.csv",
    "acervo":      OUTPUT_DIR / "acervo_raw.csv",
    "push":        OUTPUT_DIR / "push_raw.csv",
}

import re
CNJ_RE = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar_cnj(cnj: str) -> str:
    """Garante formato canônico NNNNNNN-DD.AAAA.J.TT.OOOO."""
    cnj = cnj.strip()
    m = CNJ_RE.search(cnj)
    return m.group(0) if m else cnj


# ============================================================
# LER CSVs
# ============================================================

def ler_csv(path: Path, campo_cnj: str = "numero_cnj") -> set[str]:
    """Lê CSV e retorna set de CNJs normalizados."""
    if not path.exists():
        print(f"  [!] Arquivo não encontrado: {path}")
        return set()
    cnjs = set()
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw = row.get(campo_cnj, "").strip()
                if raw:
                    normalizado = normalizar_cnj(raw)
                    if CNJ_RE.match(normalizado):
                        cnjs.add(normalizado)
    except Exception as e:
        print(f"  [X] Erro ao ler {path}: {e}")
    return cnjs


# ============================================================
# CRUZAMENTO
# ============================================================

def cruzar(
    cnjs_exp: set[str],
    cnjs_acv: set[str],
    cnjs_push: set[str],
) -> list[dict]:
    """
    Unifica e marca presença em cada fonte.
    Retorna lista ordenada de dicts.
    """
    todos = cnjs_exp | cnjs_acv | cnjs_push
    resultado = []

    for cnj in sorted(todos):
        em_exp  = cnj in cnjs_exp
        em_acv  = cnj in cnjs_acv
        em_push = cnj in cnjs_push

        fontes = []
        if em_exp:  fontes.append("expedientes")
        if em_acv:  fontes.append("acervo")
        if em_push: fontes.append("push")

        resultado.append({
            "numero_cnj":    cnj,
            "em_expedientes": "sim" if em_exp  else "nao",
            "em_acervo":      "sim" if em_acv  else "nao",
            "em_push":        "sim" if em_push else "nao",
            "fontes":         "+".join(fontes),
            "n_fontes":       len(fontes),
            "data_coleta":    DATA_COLETA,
        })

    # Ordena: mais fontes primeiro, depois por CNJ
    resultado.sort(key=lambda r: (-r["n_fontes"], r["numero_cnj"]))
    return resultado


# ============================================================
# SALVAR
# ============================================================

def salvar_unificados(dados: list[dict]) -> Path:
    path = OUTPUT_DIR / "processos_unificados.csv"
    campos = ["numero_cnj", "em_expedientes", "em_acervo", "em_push",
              "fontes", "n_fontes", "data_coleta"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(dados)
    print(f"  [+] Salvo: {path} ({len(dados)} CNJs únicos)")
    return path


def salvar_resumo(cnjs_exp, cnjs_acv, cnjs_push, total_unicos) -> Path:
    path = OUTPUT_DIR / "resumo_fontes.csv"
    campos = ["fonte", "quantidade_processos", "data_coleta"]

    linhas = [
        {"fonte": "expedientes", "quantidade_processos": len(cnjs_exp),  "data_coleta": DATA_COLETA},
        {"fonte": "acervo",      "quantidade_processos": len(cnjs_acv),  "data_coleta": DATA_COLETA},
        {"fonte": "push",        "quantidade_processos": len(cnjs_push), "data_coleta": DATA_COLETA},
        {"fonte": "TOTAL_UNICO", "quantidade_processos": total_unicos,   "data_coleta": DATA_COLETA},
        # Interseções úteis
        {"fonte": "exp+acv",       "quantidade_processos": len(cnjs_exp & cnjs_acv),          "data_coleta": DATA_COLETA},
        {"fonte": "exp+push",      "quantidade_processos": len(cnjs_exp & cnjs_push),         "data_coleta": DATA_COLETA},
        {"fonte": "acv+push",      "quantidade_processos": len(cnjs_acv & cnjs_push),         "data_coleta": DATA_COLETA},
        {"fonte": "exp+acv+push",  "quantidade_processos": len(cnjs_exp & cnjs_acv & cnjs_push), "data_coleta": DATA_COLETA},
        # Exclusivos
        {"fonte": "so_expedientes", "quantidade_processos": len(cnjs_exp  - cnjs_acv - cnjs_push), "data_coleta": DATA_COLETA},
        {"fonte": "so_acervo",      "quantidade_processos": len(cnjs_acv  - cnjs_exp - cnjs_push), "data_coleta": DATA_COLETA},
        {"fonte": "so_push",        "quantidade_processos": len(cnjs_push - cnjs_exp - cnjs_acv),  "data_coleta": DATA_COLETA},
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)
    print(f"  [+] Salvo: {path}")
    return path


# ============================================================
# MAIN
# ============================================================

def main():
    print()
    print("=" * 65)
    print("  CRUZAR LISTAS — PJe TJMG")
    print("=" * 65)
    print()

    # Verifica arquivos de entrada
    faltando = [nome for nome, path in ARQUIVOS.items() if not path.exists()]
    if faltando:
        print(f"  [!] Arquivos faltando: {faltando}")
        print()
        for nome in faltando:
            print(f"  Rode primeiro: mapear_{nome}_tjmg.py")
        if "expedientes" in faltando and "acervo" in faltando:
            print("  → mapear_expedientes_acervo_tjmg.py gera expedientes e acervo")
        if "push" in faltando:
            print("  → mapear_push_tjmg.py gera push")
        print()
        if len(faltando) == len(ARQUIVOS):
            print("  Nenhum CSV encontrado. Abortando.")
            sys.exit(1)
        print("  Continuando com os arquivos disponíveis...")
        print()

    # Lê CSVs
    cnjs_exp  = ler_csv(ARQUIVOS["expedientes"])
    cnjs_acv  = ler_csv(ARQUIVOS["acervo"])
    cnjs_push = ler_csv(ARQUIVOS["push"])

    total_unico = len(cnjs_exp | cnjs_acv | cnjs_push)

    print(f"  Expedientes: {len(cnjs_exp)} CNJs")
    print(f"  Acervo:      {len(cnjs_acv)} CNJs")
    print(f"  Push:        {len(cnjs_push)} CNJs")
    print(f"  Total único: {total_unico} CNJs")
    print()

    # Cruzamento
    dados = cruzar(cnjs_exp, cnjs_acv, cnjs_push)

    # Salva
    salvar_unificados(dados)
    salvar_resumo(cnjs_exp, cnjs_acv, cnjs_push, total_unico)

    # Relatório em tela
    em_todas   = [d for d in dados if d["n_fontes"] == 3]
    em_duas    = [d for d in dados if d["n_fontes"] == 2]
    so_push    = [d for d in dados if d["em_push"] == "sim" and d["em_expedientes"] == "nao" and d["em_acervo"] == "nao"]
    so_acervo  = [d for d in dados if d["em_acervo"] == "sim" and d["em_push"] == "nao" and d["em_expedientes"] == "nao"]
    so_exp     = [d for d in dados if d["em_expedientes"] == "sim" and d["em_push"] == "nao" and d["em_acervo"] == "nao"]

    print()
    print("=" * 65)
    print(f"  RESUMO DO CRUZAMENTO")
    print("=" * 65)
    print(f"  Em todas as 3 fontes:   {len(em_todas)}")
    print(f"  Em 2 fontes:            {len(em_duas)}")
    print(f"  Só na PUSH:             {len(so_push)}")
    print(f"  Só no Acervo:           {len(so_acervo)}")
    print(f"  Só em Expedientes:      {len(so_exp)}")
    print()
    print(f"  Saída: {OUTPUT_DIR}/")
    print()

    # Alerta: processos só na PUSH mas não no Acervo podem indicar
    # processos que o perito está monitorando mas não tem expediente ativo
    if so_push:
        print(f"  [!] {len(so_push)} processos cadastrados na PUSH mas ausentes no Acervo/Expedientes")
        print(f"      → Pode incluir processos de outras varas ou encerrados")
        if len(so_push) <= 10:
            for d in so_push[:10]:
                print(f"      - {d['numero_cnj']}")
        print()

    print("=" * 65)


if __name__ == "__main__":
    main()
