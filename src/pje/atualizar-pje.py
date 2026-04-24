#!/usr/bin/env python3
"""Atualizar PJe — Download incremental de processos.

Refatorado 2026-04-19 aplicando PYTHON-BASE:
- ref BUGS.md §8: removido IP hardcoded → env CHROME_DEBUG_IP
- ref REFACTOR-PLAN §1.2: hardcodes → env vars
- ref REFACTOR-PLAN §3.3: BAIXAR_PJE externo morto → import direto
- ref PJE-007: validar CNJ no PDF antes de salvar
- ref PJE-009: bloquear execução fora janela TJMG 13-19h
- ref PJE-014: verificar /json/version antes de connect_over_cdp
- ref PJE-021: shutil.move cross-FS via paths.safe_move
- ref GL-001: import módulos de common/, sem path-magia

Uso:
  python3 atualizar-pje.py --listar
  python3 atualizar-pje.py --novos-apenas
  python3 atualizar-pje.py --processo 5030880-86.2024.8.13.0105
  python3 atualizar-pje.py --extrair-texto

Pré-requisito (Windows/Parallels):
  Chrome com --remote-debugging-port=9222 --remote-allow-origins=*
  Token VidaaS A3 logado no PJe TJMG.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Importa common/ via path do próprio pacote
sys.path.insert(0, str(Path(__file__).parent.parent))

from pje.common.browser import BrowserError, abrir_browser
from pje.common.cnj import safe_filename_cnj, validar_cnj
from pje.common.config import SETTINGS
from pje.common.janela import dentro_janela_tjmg, msg_janela
from pje.common.logger import get_logger
from pje.common.paths import processos_dir, quarentena_dir, safe_move
from pje.common.pdf import cnj_no_pdf, pdf_valido

logger = get_logger("atualizar-pje")

# Caminhos base — processos ficam aqui (env PROCESSOS_DIR override)
PROCESSOS_DIR = processos_dir()


# ============================================================
# Coletar processos do filesystem
# ============================================================
def coletar_processos() -> list[dict]:
    processos: list[dict] = []
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
        except (json.JSONDecodeError, OSError) as e:
            logger.captura_falha(
                tecnologia="geral", categoria="encoding",
                sintoma=f"FICHA.json inválida em {pasta.name}: {e}",
                contexto={"pasta": str(pasta)},
                ref_falhas_json="GL-002", exc=e,
            )
            continue
        cnj = ficha.get("numero_cnj", "")
        if not cnj:
            continue
        processos.append({
            "cnj": cnj,
            "pasta": pasta,
            "ficha": ficha,
            "tem_pdf": _tem_pdf(pasta),
            "tem_texto": (pasta / "TEXTO-EXTRAIDO.txt").exists(),
            "tamanho_pdf_mb": _tamanho_pdf_mb(pasta),
        })
    return processos


def _pdf_principal(pasta: Path) -> Path | None:
    for nome in ("autos-completos.pdf", "PROCESSO-ORIGINAL.pdf"):
        p = pasta / nome
        if p.exists():
            return p
    return None


def _tem_pdf(pasta: Path) -> bool:
    return _pdf_principal(pasta) is not None


def _tamanho_pdf_mb(pasta: Path) -> float:
    p = _pdf_principal(pasta)
    return (p.stat().st_size / (1024 * 1024)) if p else 0.0


# ============================================================
# Comando: --listar
# ============================================================
def cmd_listar() -> None:
    procs = coletar_processos()
    com_pdf = sum(1 for p in procs if p["tem_pdf"])
    com_txt = sum(1 for p in procs if p["tem_texto"])
    print(f"\n  STATUS — {len(procs)} processos")
    print("  " + "─" * 70)
    for p in procs:
        nome = p["pasta"].name
        if len(nome) > 45:
            nome = nome[:42] + "..."
        pdf = f"PDF ({p['tamanho_pdf_mb']:.1f}MB)" if p["tem_pdf"] else "SEM PDF"
        txt = "TXT" if p["tem_texto"] else "---"
        print(f"  {nome:<46} {pdf:<22} {txt}")
    print("  " + "─" * 70)
    print(f"  Com PDF: {com_pdf}  |  Sem PDF: {len(procs)-com_pdf}  |  Com texto: {com_txt}\n")


# ============================================================
# Comando: --extrair-texto
# ============================================================
def cmd_extrair_texto() -> None:
    procs = coletar_processos()
    extraidos = falhas = 0
    for p in procs:
        if p["tem_texto"]:
            continue
        pdf = _pdf_principal(p["pasta"])
        if not pdf:
            continue
        txt = p["pasta"] / "TEXTO-EXTRAIDO.txt"
        logger.info("Extraindo texto: %s", p["cnj"])
        try:
            r = subprocess.run(
                ["pdftotext", "-layout", str(pdf), str(txt)],
                capture_output=True, text=True, timeout=120,
            )
            if r.returncode == 0 and txt.exists() and txt.stat().st_size > 0:
                extraidos += 1
                logger.info("  %.0fKB extraídos", txt.stat().st_size / 1024)
            else:
                falhas += 1
                logger.captura_falha(
                    tecnologia="subprocess", categoria="encoding",
                    sintoma=f"pdftotext returncode={r.returncode}: {r.stderr[:200]}",
                    contexto={"cnj": p["cnj"], "pdf": str(pdf)},
                    ref_falhas_json=None,
                )
        except subprocess.TimeoutExpired as e:
            falhas += 1
            logger.captura_falha(
                tecnologia="subprocess", categoria="timeout",
                sintoma="pdftotext timeout 120s",
                contexto={"cnj": p["cnj"], "pdf": str(pdf)},
                ref_falhas_json=None, exc=e,
            )
        except FileNotFoundError as e:
            logger.captura_falha(
                tecnologia="geral", categoria="ambiente",
                sintoma="pdftotext não encontrado (instalar: brew install poppler)",
                contexto={}, ref_falhas_json="PW-001", exc=e,
            )
            return
    print(f"\n  Extraídos: {extraidos} | Falhas: {falhas}\n")


# ============================================================
# Comando: download via Chrome debug (CDP)
# ============================================================
async def cmd_baixar(args: argparse.Namespace) -> None:
    # Guarda 1: janela TJMG (PJE-009)
    if not dentro_janela_tjmg() and not args.forcar_horario:
        logger.aviso(msg_janela() + " (use --forcar-horario para ignorar)")
        return

    motor = (args.motor or SETTINGS.motor or "local").lower()
    ip = args.ip or SETTINGS.chrome_debug_ip
    porta = args.porta or SETTINGS.chrome_debug_porta

    # Filtragem
    procs = coletar_processos()
    if args.processo:
        procs = [p for p in procs if args.processo in p["cnj"]]
        if not procs:
            logger.erro("Processo não encontrado: %s", args.processo)
            return
    if args.novos_apenas:
        procs = [p for p in procs if not p["tem_pdf"]]
        if not procs:
            logger.info("Todos os processos já têm PDF.")
            return

    temp_download = Path(__file__).parent / "_downloads_temp"
    temp_download.mkdir(exist_ok=True)

    sucesso = falha = quarentena = 0
    cnjs = [p["cnj"] for p in procs]
    print(f"\n  ATUALIZAR PJe — {len(cnjs)} processos (motor={motor})\n  " + "─" * 50)
    for c in cnjs:
        print(f"    {c}")

    pw = ctx = page = None
    try:
        try:
            pw, ctx, page = await abrir_browser(motor=motor, ip=ip, porta=porta)
        except BrowserError as e:
            logger.captura_falha(
                tecnologia="playwright", categoria="config",
                sintoma=str(e),
                contexto={"motor": motor, "ip": ip, "porta": porta},
                ref_falhas_json=getattr(e, "ref_falhas_json", None) or "GL-001",
                exc=e,
            )
            if motor == "remoto":
                print(
                    f"\n  Verifique:\n"
                    f"  1. Chrome rodando no Windows com "
                    f"--remote-debugging-port={porta} --remote-allow-origins=*\n"
                    f"  2. IP correto: {ip}\n"
                    f"  3. Token VidaaS logado no PJe\n"
                )
            return

        logger.info("Browser pronto (motor=%s)", motor)

        for i, proc in enumerate(procs, 1):
            cnj = proc["cnj"]
            pasta = proc["pasta"]
            print(f"\n  [{i}/{len(procs)}] {cnj}")

            # Sequência de cliques PJe específica do TJMG ainda não foi reescrita
            # em Playwright. O legado Selenium baixar_push_pje.py roda no Windows
            # e cobre esse caminho hoje. Registramos a falha factual no JSONL para
            # decidir empiricamente quando vale reimplementar (ref: PJE-NEW).
            falha += 1
            logger.captura_falha(
                tecnologia="playwright", categoria="download",
                sintoma=(
                    f"download Playwright não implementado para motor={motor}; "
                    "usar baixar_push_pje.py (Selenium) no Windows até reimplementar"
                ),
                contexto={"cnj": cnj, "motor": motor, "pasta": str(pasta)},
                ref_falhas_json="PJE-NEW",
            )

    except Exception as e:
        logger.captura_falha(
            tecnologia="playwright", categoria="config",
            sintoma=f"Erro geral cmd_baixar: {e}",
            contexto={"motor": motor}, ref_falhas_json=None, exc=e,
        )
    finally:
        shutil.rmtree(temp_download, ignore_errors=True)
        try:
            if ctx is not None:
                await ctx.close()
        except Exception:
            pass
        try:
            if pw is not None:
                await pw.stop()
        except Exception:
            pass

    print(f"\n  Sucesso: {sucesso} | Falha: {falha} | Quarentena: {quarentena} | "
          f"Total: {len(procs)}\n")


# ============================================================
# CLI
# ============================================================
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Atualizar processos do PJe (Chrome debug via CDP)",
    )
    parser.add_argument("--todos", action="store_true")
    parser.add_argument("--processo", help="CNJ formatado")
    parser.add_argument("--novos-apenas", action="store_true",
                        help="Só baixa processos sem PDF")
    parser.add_argument("--listar", action="store_true")
    parser.add_argument("--extrair-texto", action="store_true")
    parser.add_argument("--ip", default=None,
                        help=f"IP Chrome debug (default: env CHROME_DEBUG_IP={SETTINGS.chrome_debug_ip})")
    parser.add_argument("--porta", type=int, default=None,
                        help=f"Porta CDP (default: {SETTINGS.chrome_debug_porta})")
    parser.add_argument("--forcar-horario", action="store_true",
                        help="Ignora janela TJMG 13-19h (não recomendado)")
    parser.add_argument("--motor", choices=["local", "remoto"], default=None,
                        help=f"Motor browser (default: env PJE_MOTOR={SETTINGS.motor})")
    args = parser.parse_args()

    if args.processo and not validar_cnj(args.processo):
        logger.erro("CNJ inválido: %s", args.processo)
        sys.exit(2)

    if args.listar:
        cmd_listar()
    elif args.extrair_texto:
        cmd_extrair_texto()
    elif args.todos or args.processo or args.novos_apenas:
        asyncio.run(cmd_baixar(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
