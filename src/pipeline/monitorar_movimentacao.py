#!/usr/bin/env python3
# DATAJUD_GUIA: ~/Desktop/STEMMIA Dexter/DOCS/datajud/DATAJUD-GUIA.md — ler antes de alterar chamadas DataJud
"""
Monitor de Movimentações — Compara PDFs baixados com movimentações online.

Para cada processo em processos/:
  1. Verifica data do PDF mais recente na pasta
  2. Consulta DataJud API para movimentações novas
  3. Se houver movimentação após a data do PDF → reporta

Uso:
  python3 monitorar_movimentacao.py              # Verifica todos
  python3 monitorar_movimentacao.py --json        # Saída JSON (para Telegram)
  python3 monitorar_movimentacao.py --silencioso   # Só novidades (para heartbeat)

IMPORTANTE: Este script NÃO baixa PDFs. Apenas detecta quais processos precisam atualizar.
            Use atualizar_pdfs.py para baixar os novos.
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# Caminhos
SCRIPTS_DIR = Path(__file__).parent
PROCESSOS_DIR = SCRIPTS_DIR / "processos"

# DataJud API
DATAJUD_BASE = "https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal}/_search"
DATAJUD_KEY = os.getenv("DATAJUD_API_KEY", "")
if not DATAJUD_KEY:
    raise RuntimeError(
        "DATAJUD_API_KEY não setada. Execute: "
        'export DATAJUD_API_KEY="<chave>" '
        "(ver https://datajud-wiki.cnj.jus.br/api-publica/acesso)"
    )

# Regex
RE_DATA = re.compile(r'(\d{2})[/.-](\d{2})[/.-](\d{4})')
RE_CNJ = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')


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
    print(f"  [{ts}] {prefix} {msg}", file=sys.stderr)


# ============================================================
# FUNÇÕES DE DATA
# ============================================================

def data_modificacao_pdf(pasta):
    """Retorna a data de modificação do PDF mais recente na pasta."""
    pdfs = list(pasta.glob("*.pdf")) + list(pasta.glob("*.PDF"))
    if not pdfs:
        return None
    # Pegar o mais recente por data de modificação do arquivo
    mais_recente = max(pdfs, key=lambda p: p.stat().st_mtime)
    mtime = mais_recente.stat().st_mtime
    return datetime.fromtimestamp(mtime)


def extrair_data_texto_pdf(pdf_path):
    """Extrai a última data encontrada no texto do PDF (última movimentação)."""
    try:
        txt_path = pdf_path.with_suffix(".txt")
        # Tenta usar texto já extraído
        if not txt_path.exists():
            result = subprocess.run(
                ["pdftotext", str(pdf_path), str(txt_path)],
                capture_output=True, timeout=30
            )
            if result.returncode != 0:
                return None

        texto = txt_path.read_text(encoding="utf-8", errors="ignore")
        # Encontra todas as datas no texto
        datas = RE_DATA.findall(texto)
        if not datas:
            return None

        # Converte para datetime e pega a mais recente
        datas_dt = []
        for d, m, a in datas:
            try:
                dt = datetime(int(a), int(m), int(d))
                if dt.year >= 2020 and dt <= datetime.now():
                    datas_dt.append(dt)
            except ValueError:
                continue

        return max(datas_dt) if datas_dt else None
    except Exception:
        return None


# ============================================================
# DATAJUD API
# ============================================================

def consultar_datajud(cnj, tribunal="tjmg", max_retries=3):
    """Consulta movimentações via DataJud API com rate limiting e retry."""
    url = DATAJUD_BASE.format(tribunal=tribunal)
    body = json.dumps({
        "query": {
            "match": {
                "numeroProcesso": cnj.replace("-", "").replace(".", "")
            }
        },
        "size": 1
    }).encode("utf-8")

    req = urllib.request.Request(
        url, data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"APIKey {DATAJUD_KEY}"
        },
        method="POST"
    )

    for tentativa in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                hits = data.get("hits", {}).get("hits", [])
                if hits:
                    return hits[0].get("_source", {})
                return None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                log(f"Rate limited (429) no DataJud — aguardando 60s (tentativa {tentativa+1}/{max_retries})", "AVISO")
                time.sleep(60)
                continue
            return None
        except (urllib.error.URLError, TimeoutError):
            return None
    return None


def ultima_movimentacao_datajud(cnj, tribunal="tjmg"):
    """Retorna (data, nome) da última movimentação via DataJud."""
    resultado = consultar_datajud(cnj, tribunal)
    if not resultado:
        return None, None

    movs = resultado.get("movimentos", [])
    if not movs:
        return None, None

    ultima = movs[0]
    nome = ultima.get("nome", "Sem nome")
    data_str = ultima.get("dataHora", "")[:10]

    try:
        data = datetime.strptime(data_str, "%Y-%m-%d")
        return data, nome
    except ValueError:
        return None, nome


# ============================================================
# COLETAR PROCESSOS LOCAIS
# ============================================================

def coletar_processos():
    """Coleta todos os processos com FICHA.json."""
    processos = []
    if not PROCESSOS_DIR.exists():
        return processos

    for pasta in sorted(PROCESSOS_DIR.iterdir()):
        if not pasta.is_dir() or pasta.is_symlink():
            continue
        ficha_path = pasta / "FICHA.json"
        if not ficha_path.exists():
            continue
        try:
            ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
            cnj = ficha.get("numero_cnj", "")
            if not cnj:
                continue
            processos.append({
                "cnj": cnj,
                "pasta": pasta,
                "pasta_nome": pasta.name,
                "tribunal": ficha.get("tribunal", "TJMG"),
                "numero_pericia": ficha.get("numero_pericia", 0),
                "cidade": ficha.get("cidade", ""),
                "vara": ficha.get("vara", ""),
                "ficha": ficha,
            })
        except Exception:
            continue

    return processos


# ============================================================
# VERIFICAÇÃO PRINCIPAL
# ============================================================

def verificar_movimentacoes(silencioso=False):
    """Verifica todos os processos e retorna lista de novidades."""
    processos = coletar_processos()
    if not processos:
        if not silencioso:
            log("Nenhum processo encontrado em processos/", "AVISO")
        return []

    if not silencioso:
        log(f"Verificando {len(processos)} processos...")

    novidades = []
    sem_pdf = []
    sem_datajud = []
    ok = []

    for i, proc in enumerate(processos):
        cnj = proc["cnj"]
        pasta = proc["pasta"]
        tribunal = proc["tribunal"].lower()

        # Mapear tribunal para endpoint DataJud
        tribunal_map = {
            "tjmg": "tjmg", "trf6": "trf6", "trf1": "trf1", "trt3": "trt3",
            "tj13": "tjmg",  # AJG usa código 8.13 = TJMG
        }
        endpoint = tribunal_map.get(tribunal, "tjmg")

        # Data do PDF local
        data_pdf = data_modificacao_pdf(pasta)
        if not data_pdf:
            sem_pdf.append(proc)
            continue

        # Rate limiting: 1 segundo entre chamadas DataJud
        if i > 0:
            time.sleep(1.0)

        # Consultar DataJud
        data_mov, nome_mov = ultima_movimentacao_datajud(cnj, endpoint)

        if data_mov is None:
            sem_datajud.append(proc)
            continue

        # Comparar
        if data_mov > data_pdf:
            novidades.append({
                "cnj": cnj,
                "pasta_nome": proc["pasta_nome"],
                "numero_pericia": proc["numero_pericia"],
                "cidade": proc["cidade"],
                "data_pdf": data_pdf.strftime("%d/%m/%Y"),
                "data_movimentacao": data_mov.strftime("%d/%m/%Y"),
                "nome_movimentacao": nome_mov,
                "tribunal": proc["tribunal"],
            })
        else:
            ok.append(proc)

    if not silencioso:
        log(f"Resultado: {len(novidades)} com novidade, {len(ok)} sem novidade, "
            f"{len(sem_pdf)} sem PDF, {len(sem_datajud)} sem DataJud", "OK")

    return novidades


# ============================================================
# FORMATAÇÃO
# ============================================================

def formatar_novidades(novidades, silencioso=False):
    """Formata e exibe as novidades encontradas."""
    if not novidades:
        if not silencioso:
            print(f"\n  {C.G}Nenhuma movimentação nova detectada.{C.R}\n")
        return

    print()
    print(f"{C.B}  MOVIMENTAÇÕES NOVAS DETECTADAS{C.R}")
    print(f"{'═' * 60}")

    for n in novidades:
        num = n.get("numero_pericia", "?")
        cidade = n.get("cidade", "?")
        print(f"\n  {C.Y}Perícia {num:02d} - {cidade}{C.R}")
        print(f"  CNJ: {n['cnj']}")
        print(f"  PDF baixado em: {n['data_pdf']}")
        print(f"  Nova movimentação: {C.RE}{n['data_movimentacao']}{C.R} — {n['nome_movimentacao']}")
        print(f"  → RECOMENDAÇÃO: Atualizar PDF")

    print(f"\n{'═' * 60}")
    print(f"  {C.B}{len(novidades)} processo(s) com movimentação nova{C.R}")
    print()


# ============================================================
# MAIN
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Monitor de movimentações processuais")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    parser.add_argument("--silencioso", action="store_true", help="Só novidades (para heartbeat)")
    args = parser.parse_args()

    novidades = verificar_movimentacoes(silencioso=args.silencioso)

    if args.json:
        print(json.dumps(novidades, ensure_ascii=False, indent=2))
    elif args.silencioso:
        if novidades:
            for n in novidades:
                print(f"NOVA: Perícia {n.get('numero_pericia', '?'):02d} — {n['nome_movimentacao']} ({n['data_movimentacao']})")
    else:
        formatar_novidades(novidades)


if __name__ == "__main__":
    main()
