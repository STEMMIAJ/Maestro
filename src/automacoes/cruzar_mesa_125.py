#!/usr/bin/env python3
"""
cruzar_mesa_125.py — Cruza os 125 CNJs da mesa (AJ+AJG) com PDFs baixados,
identificando por CONTEÚDO da primeira página (não pelo nome do arquivo).

Fonte de verdade: ~/Desktop/LISTA-TOTAL-DISCRIMINADA-16042026.md (BLOCO 1).
Outputs:
  ~/Desktop/MESA-125-STATUS-17042026.md
  ~/Desktop/MESA-125-FALTANTES.txt
  ~/Desktop/indice-pdfs-mesa.json
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

HOME = Path.home()
MESA_MD = HOME / "Desktop/LISTA-TOTAL-DISCRIMINADA-16042026.md"
PASTAS_PDF = [
    HOME / "Desktop/processos-pje",
    HOME / "Desktop/FENIX/processos",
    HOME / "Desktop/PROCESSOS FINAIS",
    HOME / "Desktop/TODOS OS PROCESSOS",
]
OUT_DIR = HOME / "Desktop/STEMMIA Dexter/mesa-125"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_JSON = OUT_DIR / "indice-pdfs.json"
OUT_MD = OUT_DIR / f"STATUS-{datetime.now():%d%m%Y}.md"
OUT_FALTANTES = OUT_DIR / "FALTANTES.txt"

CNJ_RE = re.compile(r"(\d{7}-\d{2}\.\d{4}\.8\.13\.\d{4})")


def parse_mesa_125(md_path: Path) -> dict:
    """Extrai CNJs do BLOCO 1 do MD.
    Retorna dict {cnj: {comarca, situacao, aj_ajg, tambem_em}}."""
    texto = md_path.read_text()
    m_inicio = re.search(r"^## BLOCO 1 ", texto, re.M)
    m_fim = re.search(r"^## BLOCO 2 ", texto, re.M)
    bloco = texto[m_inicio.start():m_fim.start()] if m_fim else texto[m_inicio.start():]

    mesa = {}
    for linha in bloco.splitlines():
        if not linha.startswith("|"):
            continue
        cols = [c.strip() for c in linha.split("|")]
        # formato: | # | `CNJ` | Comarca | Situacao | AJ/AJG | Tambem em |
        if len(cols) < 7:
            continue
        m = CNJ_RE.search(cols[2])
        if not m:
            continue
        cnj = m.group(1)
        mesa[cnj] = {
            "comarca": cols[3],
            "situacao": cols[4],
            "aj_ajg": cols[5],
            "tambem_em": cols[6],
        }
    return mesa


def extrair_texto(pdf: Path) -> str:
    """Extrai texto do PDF inteiro (até 200KB). Usa TEXTO-EXTRAIDO.txt ao lado se existir."""
    irmao = pdf.parent / "TEXTO-EXTRAIDO.txt"
    if irmao.exists():
        try:
            return irmao.read_text(errors="ignore")[:200_000]
        except Exception:
            pass
    try:
        out = subprocess.run(
            ["pdftotext", str(pdf), "-"],
            capture_output=True, timeout=60, text=True, errors="ignore",
        )
        return out.stdout[:200_000]
    except Exception:
        return ""


def _processar_pdf(path_str: str) -> tuple:
    """Worker para pool: retorna (chave_cache, contagem_cnjs)."""
    p = Path(path_str)
    try:
        st = p.stat()
    except FileNotFoundError:
        return (None, None)
    chave = f"{path_str}|{st.st_mtime}|{st.st_size}"
    texto = extrair_texto(p)
    matches = CNJ_RE.findall(texto)
    contagem = {}
    for c in matches:
        contagem[c] = contagem.get(c, 0) + 1
    return (chave, contagem)


def indexar_pdfs(pastas: list, cache_path: Path) -> dict:
    """Walk nas pastas, extrai CNJ da pg1, produz {cnj: [paths]}.
    Cache invalidado por (path, mtime, size)."""
    cache = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text())
        except Exception:
            cache = {}

    arquivos = []
    for p in pastas:
        if p.exists():
            arquivos.extend(p.rglob("*.pdf"))
            arquivos.extend(p.rglob("*.PDF"))

    # dedup
    arquivos = sorted({str(a.resolve()) for a in arquivos})

    # índice: cnj -> [(path, contagem), ...]
    indice = defaultdict(list)
    novo_cache = {}
    total = len(arquivos)
    sem_cnj = []
    divergencias = []

    # Separa: em_cache (sem custo) vs precisa_extrair (paraleliza)
    resultados = {}  # path_str -> contagem_cnjs
    a_extrair = []
    for path_str in arquivos:
        p = Path(path_str)
        try:
            st = p.stat()
        except FileNotFoundError:
            continue
        chave = f"{path_str}|{st.st_mtime}|{st.st_size}"
        if chave in cache and isinstance(cache[chave], dict):
            resultados[path_str] = cache[chave]
            novo_cache[chave] = cache[chave]
        else:
            a_extrair.append(path_str)

    print(f"  Cache hit: {len(resultados)}/{total}. Extraindo {len(a_extrair)} em paralelo…", file=sys.stderr)

    workers = min(8, (os.cpu_count() or 4))
    if a_extrair:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futures = {ex.submit(_processar_pdf, p): p for p in a_extrair}
            done = 0
            for fut in as_completed(futures):
                done += 1
                chave, contagem = fut.result()
                if chave is None:
                    continue
                path_str = chave.split("|")[0]
                resultados[path_str] = contagem
                novo_cache[chave] = contagem
                if done % 10 == 0 or done == len(a_extrair):
                    print(f"  [{done}/{len(a_extrair)}]", file=sys.stderr)

    for path_str in arquivos:
        p = Path(path_str)
        contagem_cnjs = resultados.get(path_str)
        if contagem_cnjs is None:
            continue

        if not contagem_cnjs:
            sem_cnj.append(path_str)
            continue

        # CNJ "principal" = o mais frequente (aparece em cabeçalho de toda página)
        cnj_principal = max(contagem_cnjs, key=contagem_cnjs.get)
        peso = contagem_cnjs[cnj_principal]

        # registrar TODOS os CNJs encontrados no PDF (útil para PDFs com múltiplos)
        for cnj, cnt in contagem_cnjs.items():
            indice[cnj].append({"path": path_str, "count": cnt, "principal": cnj == cnj_principal})

        # divergência: filename tem CNJ que não bate com o principal
        m_fn = CNJ_RE.search(p.name)
        if m_fn and m_fn.group(1) != cnj_principal:
            divergencias.append({
                "arquivo": path_str,
                "filename_cnj": m_fn.group(1),
                "pg1_cnj": cnj_principal,
                "peso_principal": peso,
            })

    cache_path.write_text(json.dumps(novo_cache, indent=2, ensure_ascii=False))

    return {
        "indice": dict(indice),
        "sem_cnj": sem_cnj,
        "divergencias": divergencias,
    }


def comarca_de(cnj: str) -> str:
    return cnj.split(".")[-1] if "." in cnj else ""


def main():
    print("=" * 60)
    print("CRUZAR MESA 125 × PDFs baixados")
    print("=" * 60)

    print("\n[1/3] Parseando os 125 CNJs da mesa…")
    mesa = parse_mesa_125(MESA_MD)
    print(f"  Encontrados: {len(mesa)} CNJs")
    assert len(mesa) == 125, f"Esperado 125, achei {len(mesa)}"

    print("\n[2/3] Indexando PDFs por conteúdo da pg1…")
    r = indexar_pdfs(PASTAS_PDF, CACHE_JSON)
    indice = r["indice"]
    print(f"  PDFs indexados: {sum(len(v) for v in indice.values())}")
    print(f"  CNJs únicos detectados: {len(indice)}")
    print(f"  PDFs sem CNJ identificado: {len(r['sem_cnj'])}")
    print(f"  Divergências filename≠pg1: {len(r['divergencias'])}")

    print("\n[3/3] Cruzando…")
    # baixado = mesa_cnj está presente em algum PDF (qualquer peso)
    baixados = {c: indice[c] for c in mesa if c in indice}
    faltantes_raw = [c for c in mesa if c not in indice]
    # órfão = cnj principal de algum PDF, mas não está na mesa
    orfaos = {c: indice[c] for c in indice
              if c not in mesa and any(e["principal"] for e in indice[c])}

    # PDFs cujo filename contém um CNJ da mesa MAS o conteúdo não bate
    # (downloads falhos / arquivos renomeados / capas erradas)
    cache_raw = json.loads(CACHE_JSON.read_text())
    filename_mentiroso = defaultdict(list)
    for chave, cnjs_dict in cache_raw.items():
        path_str = chave.split("|")[0]
        name = Path(path_str).name
        m = CNJ_RE.search(name)
        if not m:
            continue
        cnj_fn = m.group(1)
        if cnj_fn not in mesa:
            continue
        if cnj_fn in indice:
            continue  # já achado pelo conteúdo, OK
        filename_mentiroso[cnj_fn].append(path_str)

    # faltantes "de verdade" = nem conteúdo nem filename
    faltantes = [c for c in faltantes_raw if c not in filename_mentiroso]
    faltantes_com_arquivo_errado = sorted(filename_mentiroso.keys())

    assert len(baixados) + len(faltantes_raw) == len(mesa), "cruzamento incoerente"

    # ordenação prioritária: Taiobeiras (0680) primeiro
    def chave(cnj):
        com = comarca_de(cnj)
        prioridade = {"0680": 0, "0105": 1, "0396": 2, "0184": 3}
        return (prioridade.get(com, 9), com, cnj)

    faltantes.sort(key=chave)
    a_rebaixar = sorted(faltantes + faltantes_com_arquivo_errado, key=chave)

    # --- MESA-125-FALTANTES.txt ---
    linhas = [
        "# CNJs da mesa (125) a BAIXAR ou RE-BAIXAR no PJe",
        f"# Gerado: {datetime.now():%Y-%m-%d %H:%M}",
        f"# Total: {len(a_rebaixar)}/125  "
        f"(não-baixados: {len(faltantes)}  +  filename-mentiroso: {len(faltantes_com_arquivo_errado)})",
        "",
    ]
    bloco_atual = None
    for cnj in a_rebaixar:
        com = comarca_de(cnj)
        nome_com = {"0680": "TAIOBEIRAS", "0105": "GOV VALADARES",
                    "0396": "MANTENA", "0184": "CONS PENA"}.get(com, f"COD {com}")
        if nome_com != bloco_atual:
            linhas.append(f"\n# === {nome_com} ===")
            bloco_atual = nome_com
        marca = "  # filename mentiroso" if cnj in filename_mentiroso else ""
        linhas.append(f"{cnj}{marca}")
    OUT_FALTANTES.write_text("\n".join(linhas) + "\n")

    # --- MESA-125-STATUS.md ---
    md = [
        f"# MESA 125 — STATUS {datetime.now():%d/%m/%Y %H:%M}",
        "",
        "## Resumo",
        "",
        f"- **Mesa total**: 125 CNJs (AJ + AJG)",
        f"- **Baixados (OK)** — conteúdo do PDF bate com o CNJ: **{len(baixados)}/125**",
        f"- **Filename mentiroso** — PDF existe com nome do CNJ mas conteúdo é outro: **{len(faltantes_com_arquivo_errado)}/125** (re-baixar)",
        f"- **Não baixados** — nenhum vestígio: **{len(faltantes)}/125**",
        f"- **Total a re-baixar**: **{len(faltantes) + len(faltantes_com_arquivo_errado)}/125**",
        "",
        f"_Outros achados: {len(orfaos)} órfãos (PDFs de processos fora da mesa), "
        f"{len(r['divergencias'])} divergências filename/conteúdo, "
        f"{len(r['sem_cnj'])} PDFs sem CNJ legível (scan sem OCR)._",
        "",
        "## Filename mentiroso — PDFs a RE-BAIXAR",
        "",
        "_O arquivo existe com o nome do CNJ, mas abrindo descobre-se que é outro processo. Deletar e baixar de novo._",
        "",
    ]
    if faltantes_com_arquivo_errado:
        md.append("| CNJ (mesa) | Arquivo atual (enganoso) | Contém na verdade |")
        md.append("|---|---|---|")
        for cnj in faltantes_com_arquivo_errado:
            for p in filename_mentiroso[cnj]:
                real = cache_raw.get(next((k for k in cache_raw if k.startswith(p + "|")), ""), {})
                real_str = ", ".join(f"`{c}` (×{n})" for c, n in sorted(real.items(), key=lambda x: -x[1])[:3]) or "(sem CNJ)"
                md.append(f"| `{cnj}` | {p.replace(str(HOME), '~')} | {real_str} |")
        md.append("")

    md.append("## Faltam baixar (priorizado — Taiobeiras primeiro)")
    md.append("")
    por_comarca = defaultdict(list)
    for c in faltantes:
        por_comarca[comarca_de(c)].append(c)

    nomes = {"0680": "TAIOBEIRAS", "0105": "GOV VALADARES",
             "0396": "MANTENA", "0184": "CONSELHEIRO PENA"}

    for com in sorted(por_comarca, key=lambda c: ({"0680": 0, "0105": 1, "0396": 2, "0184": 3}.get(c, 9), c)):
        md.append(f"### {nomes.get(com, 'Comarca ' + com)} ({com}) — {len(por_comarca[com])}")
        md.append("")
        md.append("| CNJ | Comarca/Vara | Situação | AJ/AJG |")
        md.append("|---|---|---|---|")
        for cnj in por_comarca[com]:
            m = mesa[cnj]
            md.append(f"| `{cnj}` | {m['comarca']} | {m['situacao']} | {m['aj_ajg']} |")
        md.append("")

    md.append("## Já baixados")
    md.append("")
    md.append("_\"Peso\" = nº de ocorrências do CNJ no PDF. Peso alto (>10) = cabeçalho em toda pg = processo inteiro._")
    md.append("")
    md.append("| CNJ | Comarca | Peso | Caminho (principal) |")
    md.append("|---|---|---|---|")
    for cnj in sorted(baixados):
        m = mesa[cnj]
        entradas = baixados[cnj]
        principais = [e for e in entradas if e["principal"]] or entradas
        melhor = max(principais, key=lambda e: e["count"])
        path_str = melhor["path"].replace(str(HOME), "~")
        extras = len(entradas) - 1
        extras_str = f" <sub>+{extras} outro(s)</sub>" if extras else ""
        md.append(f"| `{cnj}` | {m['comarca']} | {melhor['count']} | {path_str}{extras_str} |")
    md.append("")

    # órfãos: CNJs principais de PDFs que não estão na mesa
    if orfaos:
        md.append(f"## Órfãos — CNJs encontrados em PDFs mas fora da mesa ({len(orfaos)})")
        md.append("")
        md.append("| CNJ | Caminho | Peso |")
        md.append("|---|---|---|")
        for cnj in sorted(orfaos):
            for e in orfaos[cnj]:
                if e["principal"]:
                    md.append(f"| `{cnj}` | {e['path'].replace(str(HOME), '~')} | {e['count']} |")
        md.append("")

    if r["divergencias"]:
        md.append(f"## Divergências filename ≠ pg1 ({len(r['divergencias'])})")
        md.append("")
        md.append("| Arquivo | CNJ no filename | CNJ na pg1 |")
        md.append("|---|---|---|")
        for d in r["divergencias"]:
            md.append(f"| {d['arquivo'].replace(str(HOME), '~')} | `{d['filename_cnj']}` | `{d['pg1_cnj']}` |")
        md.append("")

    if r["sem_cnj"]:
        md.append(f"## PDFs sem CNJ identificado na pg1 ({len(r['sem_cnj'])})")
        md.append("")
        md.append("_Prováveis: procurações, anexos, scans sem OCR, petições avulsas._")
        md.append("")
        for p in r["sem_cnj"][:50]:
            md.append(f"- {p.replace(str(HOME), '~')}")
        if len(r["sem_cnj"]) > 50:
            md.append(f"- …e mais {len(r['sem_cnj']) - 50}")

    OUT_MD.write_text("\n".join(md))

    # --- Resumo final no terminal ---
    print("\n" + "=" * 60)
    print(f"MESA               : 125")
    print(f"BAIXADOS OK        : {len(baixados)}")
    print(f"FILENAME MENTIROSO : {len(faltantes_com_arquivo_errado)}  (re-baixar)")
    print(f"NAO BAIXADOS       : {len(faltantes)}")
    print(f"TOTAL A RE-BAIXAR  : {len(faltantes) + len(faltantes_com_arquivo_errado)}")
    print()
    print("Não-baixados por comarca:")
    for com in sorted(por_comarca, key=lambda c: ({"0680": 0, "0105": 1, "0396": 2, "0184": 3}.get(c, 9), c)):
        print(f"  └─ {nomes.get(com, com):20s}: {len(por_comarca[com])}")
    print(f"\nÓRFÃOS (fora mesa) : {len(orfaos)}")
    print(f"SEM CNJ LEGIVEL    : {len(r['sem_cnj'])}")
    print("=" * 60)
    print(f"Relatório: {OUT_MD}")
    print(f"Faltantes: {OUT_FALTANTES}")
    print(f"Índice   : {CACHE_JSON}")


if __name__ == "__main__":
    main()
