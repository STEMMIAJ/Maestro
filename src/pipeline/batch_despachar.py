#!/usr/bin/env python3
"""
batch_despachar.py — Despacha múltiplos processos em lote
Grupo A (aceites): Python puro via gerar_peticao.py (~12s cada)
Grupo B (propostas): Claude CLI via claude -p (~60s cada)
Grupo C (contestações): Claude CLI via claude -p (~120s cada)

Uso:
    python3 batch_despachar.py --tipo all                # Despacha tudo
    python3 batch_despachar.py --tipo aceite             # Só aceites
    python3 batch_despachar.py --tipo proposta            # Só propostas
    python3 batch_despachar.py --tipo contestacao         # Só contestações
    python3 batch_despachar.py --tipo aceite --max 5      # Limitar a 5
    python3 batch_despachar.py --tipo all --dry-run       # Mostra o que faria
    python3 batch_despachar.py --tipo all --json          # Saída JSON
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(os.path.expanduser("~/Desktop/ANALISADOR FINAL"))
PROCESSOS_DIR = BASE_DIR / "processos"
SCRIPTS_DIR = BASE_DIR / "scripts"
STATUS_JSON = BASE_DIR / "STATUS-PROCESSOS.json"
CLAUDE_CLI = Path(os.path.expanduser("~/.local/bin/claude"))


def carregar_status():
    """Carrega STATUS-PROCESSOS.json."""
    if not STATUS_JSON.exists():
        # Rodar scanner primeiro
        subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "scanner_processos.py"), "--json-only"],
            capture_output=True, timeout=30,
        )

    if STATUS_JSON.exists():
        return json.loads(STATUS_JSON.read_text(encoding="utf-8"))
    return {"processos": []}


def filtrar_por_estado(status_data, estado):
    """Filtra processos por estado."""
    return [p for p in status_data.get("processos", []) if p.get("estado") == estado]


def gerar_aceite(processo, dry_run=False):
    """Gera aceite via gerar_peticao.py (Python puro, ~12s)."""
    cnj = processo.get("cnj", "")
    pasta = processo.get("caminho", "")

    if not cnj or not pasta:
        return {"ok": False, "erro": "CNJ ou pasta não encontrado"}

    if dry_run:
        return {"ok": True, "tipo": "aceite", "cnj": cnj, "dry_run": True}

    # Verificar se TEXTO-EXTRAIDO.txt existe
    texto_path = Path(pasta) / "TEXTO-EXTRAIDO.txt"
    if not texto_path.exists():
        return {"ok": False, "erro": "TEXTO-EXTRAIDO.txt não encontrado", "cnj": cnj}

    output_pdf = f"ACEITE-{cnj}.pdf"

    # Gerar corpo XML simples para aceite
    corpo_xml = f"""<w:p><w:pPr><w:jc w:val="both"/></w:pPr>
<w:r><w:rPr><w:b/></w:rPr><w:t>Meritíssimo Juiz,</w:t></w:r></w:p>
<w:p><w:pPr><w:jc w:val="both"/></w:pPr>
<w:r><w:t xml:space="preserve">Venho respeitosamente ACEITAR o encargo de perito médico judicial nos autos do processo nº </w:t></w:r>
<w:r><w:rPr><w:b/></w:rPr><w:t>{cnj}</w:t></w:r>
<w:r><w:t xml:space="preserve">, conforme nomeação.</w:t></w:r></w:p>
<w:p><w:pPr><w:jc w:val="both"/></w:pPr>
<w:r><w:t xml:space="preserve">Aguardo os trâmites para a proposta de honorários, caso não haja manifestação das partes quanto ao perito nomeado.</w:t></w:r></w:p>"""

    try:
        # Salvar corpo temporário
        corpo_file = Path(f"/tmp/corpo-aceite-{cnj}.xml")
        corpo_file.write_text(corpo_xml, encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "gerar_peticao.py"),
             "--output", output_pdf, "--corpo-arquivo", str(corpo_file)],
            capture_output=True, text=True, timeout=60,
            cwd=str(Path(pasta)),
        )

        corpo_file.unlink(missing_ok=True)

        if result.returncode == 0:
            return {"ok": True, "tipo": "aceite", "cnj": cnj, "pdf": output_pdf}
        else:
            return {"ok": False, "tipo": "aceite", "cnj": cnj, "erro": result.stderr[-200:]}

    except (subprocess.TimeoutExpired, OSError) as e:
        return {"ok": False, "tipo": "aceite", "cnj": cnj, "erro": str(e)}


def gerar_via_claude(processo, skill, tipo, dry_run=False):
    """Gera documento via Claude CLI (~60-120s)."""
    cnj = processo.get("cnj", "")
    pasta = processo.get("caminho", "")

    if not cnj or not pasta:
        return {"ok": False, "erro": "CNJ ou pasta não encontrado"}

    if dry_run:
        return {"ok": True, "tipo": tipo, "cnj": cnj, "dry_run": True}

    if not CLAUDE_CLI.exists():
        return {"ok": False, "tipo": tipo, "cnj": cnj, "erro": "Claude CLI não encontrado"}

    texto_path = Path(pasta) / "TEXTO-EXTRAIDO.txt"
    if not texto_path.exists():
        return {"ok": False, "tipo": tipo, "cnj": cnj, "erro": "TEXTO-EXTRAIDO.txt não encontrado"}

    prompt = f"Leia {texto_path} e {skill} para o processo {cnj}. Salve o resultado em {pasta}/."

    try:
        result = subprocess.run(
            [str(CLAUDE_CLI), "-p", prompt, "--model", "sonnet"],
            capture_output=True, text=True, timeout=180,
        )

        if result.returncode == 0:
            return {"ok": True, "tipo": tipo, "cnj": cnj, "saida": result.stdout[-300:]}
        else:
            return {"ok": False, "tipo": tipo, "cnj": cnj, "erro": result.stderr[-200:]}

    except subprocess.TimeoutExpired:
        return {"ok": False, "tipo": tipo, "cnj": cnj, "erro": "Timeout (>180s)"}
    except OSError as e:
        return {"ok": False, "tipo": tipo, "cnj": cnj, "erro": str(e)}


def despachar(tipo, max_n=None, dry_run=False):
    """Despacha processos por tipo."""
    status = carregar_status()
    resultados = {"aceites": [], "propostas": [], "contestacoes": []}
    inicio = time.time()

    tipos_a_processar = []
    if tipo in ("all", "aceite"):
        tipos_a_processar.append(("PENDENTE-ACEITE", "aceite"))
    if tipo in ("all", "proposta"):
        tipos_a_processar.append(("PENDENTE-PROPOSTA", "proposta"))
    if tipo in ("all", "contestacao"):
        tipos_a_processar.append(("EM-CONTESTAÇÃO", "contestacao"))

    for estado, nome_tipo in tipos_a_processar:
        processos = filtrar_por_estado(status, estado)

        if max_n:
            processos = processos[:max_n]

        for p in processos:
            if nome_tipo == "aceite":
                r = gerar_aceite(p, dry_run)
                resultados["aceites"].append(r)
            elif nome_tipo == "proposta":
                r = gerar_via_claude(p, "gere proposta de honorários seguindo o modelo da Perícia 14", "proposta", dry_run)
                resultados["propostas"].append(r)
            elif nome_tipo == "contestacao":
                r = gerar_via_claude(p, "responda a contestação/impugnação com jurisprudência", "contestacao", dry_run)
                resultados["contestacoes"].append(r)

    tempo = time.time() - inicio

    return {
        "data": datetime.now().isoformat(),
        "tipo": tipo,
        "dry_run": dry_run,
        "tempo_total": round(tempo, 1),
        "resultados": resultados,
        "resumo": {
            "aceites_ok": sum(1 for r in resultados["aceites"] if r.get("ok")),
            "aceites_total": len(resultados["aceites"]),
            "propostas_ok": sum(1 for r in resultados["propostas"] if r.get("ok")),
            "propostas_total": len(resultados["propostas"]),
            "contestacoes_ok": sum(1 for r in resultados["contestacoes"] if r.get("ok")),
            "contestacoes_total": len(resultados["contestacoes"]),
        },
    }


def formato_terminal(dados):
    """Formata para terminal."""
    r = dados["resumo"]
    print("=" * 60)
    print(f"BATCH DESPACHAR — {dados['data'][:19]}")
    if dados["dry_run"]:
        print("*** MODO DRY-RUN — nada foi executado ***")
    print("=" * 60)

    if r["aceites_total"] > 0:
        print(f"\nACEITES: {r['aceites_ok']}/{r['aceites_total']} gerados")
        for a in dados["resultados"]["aceites"]:
            status = "OK" if a.get("ok") else "ERRO"
            print(f"  [{status}] {a.get('cnj', '?')}")
            if a.get("erro"):
                print(f"    {a['erro'][:80]}")

    if r["propostas_total"] > 0:
        print(f"\nPROPOSTAS: {r['propostas_ok']}/{r['propostas_total']} geradas")
        for a in dados["resultados"]["propostas"]:
            status = "OK" if a.get("ok") else "ERRO"
            print(f"  [{status}] {a.get('cnj', '?')}")

    if r["contestacoes_total"] > 0:
        print(f"\nCONTESTAÇÕES: {r['contestacoes_ok']}/{r['contestacoes_total']} respondidas")
        for a in dados["resultados"]["contestacoes"]:
            status = "OK" if a.get("ok") else "ERRO"
            print(f"  [{status}] {a.get('cnj', '?')}")

    print(f"\nTempo total: {dados['tempo_total']}s")


def formato_telegram(dados):
    """Formata para Telegram."""
    r = dados["resumo"]
    linhas = []

    if dados["dry_run"]:
        linhas.append("*DRY-RUN — simulação*\n")

    partes = []
    if r["aceites_total"] > 0:
        partes.append(f"{r['aceites_ok']}/{r['aceites_total']} aceites")
    if r["propostas_total"] > 0:
        partes.append(f"{r['propostas_ok']}/{r['propostas_total']} propostas")
    if r["contestacoes_total"] > 0:
        partes.append(f"{r['contestacoes_ok']}/{r['contestacoes_total']} contestações")

    if partes:
        linhas.append(f"*Gerados:* {', '.join(partes)}")
    else:
        linhas.append("Nenhum processo para despachar.")

    linhas.append(f"Tempo: {dados['tempo_total']}s")
    print("\n".join(linhas))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Despacha processos em lote")
    parser.add_argument("--tipo", required=True, choices=["all", "aceite", "proposta", "contestacao"])
    parser.add_argument("--max", type=int, default=None, help="Máximo de processos por tipo")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--telegram", action="store_true")
    args = parser.parse_args()

    dados = despachar(args.tipo, max_n=args.max, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(dados, ensure_ascii=False, indent=2))
    elif args.telegram:
        formato_telegram(dados)
    else:
        formato_terminal(dados)
