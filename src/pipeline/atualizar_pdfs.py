#!/usr/bin/env python3
"""
Atualizador de PDFs — Substitui PDFs antigos quando há movimentação nova.

Uso:
  python3 atualizar_pdfs.py --listar           # Mostra quais precisam atualizar
  python3 atualizar_pdfs.py --cnj 5002424...   # Atualiza um específico
  python3 atualizar_pdfs.py --todos             # Atualiza todos com novidade

Fluxo:
  1. Roda monitorar_movimentacao.py para detectar novidades
  2. Para cada processo com novidade:
     a. Renomeia PDF antigo → PROCESSO-BACKUP-[data].pdf
     b. Baixa novo PDF (PJe via Windows ou AJG via Mac)
     c. Extrai texto com pdftotext
     d. Atualiza FICHA.json

IMPORTANTE: O download do PJe TJMG requer o Windows/Parallels rodando.
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
PROCESSOS_DIR = SCRIPTS_DIR / "processos"
BAIXAR_PJE = Path.home() / "Desktop" / "Projetos - Plan Mode" / "processos-pje" / "baixar_pje.py"


class C:
    R = "\033[0m"
    B = "\033[1m"
    G = "\033[32m"
    Y = "\033[33m"
    RE = "\033[31m"


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ", "OK": "✓", "ERRO": "✗", "AVISO": "⚠"}.get(level, "·")
    print(f"  [{ts}] {prefix} {msg}")


def detectar_novidades():
    """Executa monitorar_movimentacao.py e retorna lista de processos com novidade."""
    script = SCRIPTS_DIR / "monitorar_movimentacao.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--json"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except Exception as e:
        log(f"Erro ao verificar movimentações: {e}", "ERRO")
    return []


def backup_pdf(pasta):
    """Renomeia PDFs existentes para backup. Retorna número de backups feitos."""
    backups = 0
    data_str = datetime.now().strftime("%Y%m%d")
    for pdf in list(pasta.glob("*.pdf")) + list(pasta.glob("*.PDF")):
        if "BACKUP" in pdf.name:
            continue
        novo_nome = pdf.stem + f"-BACKUP-{data_str}" + pdf.suffix
        destino = pasta / novo_nome
        pdf.rename(destino)
        log(f"Backup: {pdf.name} → {novo_nome}")
        backups += 1
    return backups


def extrair_texto(pdf_path):
    """Extrai texto do PDF com pdftotext."""
    txt_path = pdf_path.with_name("TEXTO-EXTRAIDO.txt")
    try:
        result = subprocess.run(
            ["pdftotext", str(pdf_path), str(txt_path)],
            capture_output=True, timeout=60
        )
        if result.returncode == 0:
            log(f"Texto extraído: {txt_path.name}", "OK")
            return True
    except Exception:
        pass
    return False


def atualizar_ficha(pasta, cnj):
    """Atualiza FICHA.json com data de atualização."""
    ficha_path = pasta / "FICHA.json"
    if ficha_path.exists():
        try:
            ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
            ficha["pdf_atualizado_em"] = datetime.now().isoformat()
            ficha_path.write_text(
                json.dumps(ficha, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass


def encontrar_pasta_cnj(cnj):
    """Encontra a pasta de um processo pelo CNJ."""
    if not PROCESSOS_DIR.exists():
        return None

    # Tenta symlink direto
    link = PROCESSOS_DIR / cnj
    if link.exists():
        return link.resolve()

    # Busca em FICHA.json
    for pasta in PROCESSOS_DIR.iterdir():
        if not pasta.is_dir() or pasta.is_symlink():
            continue
        ficha_path = pasta / "FICHA.json"
        if ficha_path.exists():
            try:
                ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
                if ficha.get("numero_cnj") == cnj:
                    return pasta
            except Exception:
                continue
    return None


def listar_pendentes(novidades):
    """Lista processos que precisam atualizar PDF."""
    if not novidades:
        print(f"\n  {C.G}Nenhum processo precisa atualizar PDF.{C.R}\n")
        return

    print(f"\n{C.B}  PROCESSOS COM PDF DESATUALIZADO{C.R}")
    print(f"{'─' * 70}")

    for n in novidades:
        num = n.get("numero_pericia", "?")
        print(f"  Perícia {num:02d} — {n['cnj']}")
        print(f"    PDF: {n['data_pdf']} | Nova mov: {n['data_movimentacao']} — {n['nome_movimentacao']}")
        print()

    print(f"  Total: {len(novidades)} processo(s)")
    print(f"  Para atualizar: python3 atualizar_pdfs.py --todos")
    print()


def atualizar_processo(cnj):
    """Atualiza o PDF de um processo específico."""
    pasta = encontrar_pasta_cnj(cnj)
    if not pasta:
        log(f"Pasta não encontrada para {cnj}", "ERRO")
        return False

    log(f"Atualizando {pasta.name}...")

    # 1. Backup dos PDFs antigos
    backups = backup_pdf(pasta)
    if backups == 0:
        log("Nenhum PDF para fazer backup (pasta sem PDFs)", "AVISO")

    # 2. Baixar novo PDF
    # Detectar se é PJe (TJMG) ou AJG
    ficha_path = pasta / "FICHA.json"
    tribunal = "TJMG"
    if ficha_path.exists():
        try:
            ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
            tribunal = ficha.get("tribunal", "TJMG")
        except Exception:
            pass

    pdf_baixado = False

    if tribunal.startswith("TRF") or tribunal.startswith("JF"):
        # Justiça Federal — tentar via AJG (requer Chrome com CDP)
        log("Processo federal — download via AJG não implementado ainda", "AVISO")
        log("Baixe manualmente pelo AJG e coloque o PDF na pasta", "INFO")
        log(f"Pasta: {pasta}", "INFO")
    else:
        # TJMG — usar baixar_pje.py via Windows
        if BAIXAR_PJE.exists():
            log("Baixando via PJe (Windows)...")
            saida_dir = pasta
            try:
                result = subprocess.run(
                    [sys.executable, str(BAIXAR_PJE),
                     "--processos", cnj,
                     "--saida", str(saida_dir)],
                    capture_output=True, text=True, timeout=120
                )
                if result.returncode == 0:
                    # Verificar se o PDF foi baixado
                    novos_pdfs = [f for f in pasta.glob("*.pdf")
                                  if "BACKUP" not in f.name]
                    if novos_pdfs:
                        pdf_baixado = True
                        log(f"PDF baixado: {novos_pdfs[0].name}", "OK")
                else:
                    log(f"Erro no download: {result.stderr[:200]}", "ERRO")
            except subprocess.TimeoutExpired:
                log("Timeout no download (>2min)", "ERRO")
            except Exception as e:
                log(f"Erro: {e}", "ERRO")
        else:
            log(f"Script baixar_pje.py não encontrado em {BAIXAR_PJE}", "ERRO")
            log("Baixe manualmente pelo PJe e coloque o PDF na pasta", "INFO")

    # 3. Extrair texto do novo PDF
    if pdf_baixado:
        novos_pdfs = [f for f in pasta.glob("*.pdf") if "BACKUP" not in f.name]
        if novos_pdfs:
            extrair_texto(novos_pdfs[0])

    # 4. Atualizar FICHA.json
    atualizar_ficha(pasta, cnj)

    return pdf_baixado


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Atualizar PDFs de processos")
    parser.add_argument("--listar", action="store_true", help="Lista quais precisam atualizar")
    parser.add_argument("--cnj", type=str, help="Atualiza um processo específico")
    parser.add_argument("--todos", action="store_true", help="Atualiza todos com novidade")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    args = parser.parse_args()

    if not args.cnj:
        log("Verificando movimentações...")
        novidades = detectar_novidades()
    else:
        novidades = [{"cnj": args.cnj}]

    if args.listar:
        if args.json:
            print(json.dumps(novidades, ensure_ascii=False, indent=2))
        else:
            listar_pendentes(novidades)
        return

    if args.cnj:
        sucesso = atualizar_processo(args.cnj)
        if sucesso:
            log(f"Processo {args.cnj} atualizado!", "OK")
        else:
            log(f"Não foi possível atualizar {args.cnj}", "AVISO")
        return

    if args.todos:
        if not novidades:
            log("Nenhum processo precisa atualizar", "OK")
            return

        log(f"Atualizando {len(novidades)} processo(s)...")
        ok = 0
        erros = 0
        for n in novidades:
            cnj = n.get("cnj", "")
            if cnj:
                if atualizar_processo(cnj):
                    ok += 1
                else:
                    erros += 1

        log(f"Concluído: {ok} atualizados, {erros} com erro", "OK")
        return

    # Default: listar
    listar_pendentes(novidades)


if __name__ == "__main__":
    main()
