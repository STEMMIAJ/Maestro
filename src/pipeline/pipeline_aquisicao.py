#!/usr/bin/env python3
"""
Pipeline de Aquisição Processual — Stemmia Forense

Recebe lista de CNJs (do monitor ou manual), executa:
  1. Consulta metadados via DataJud API
  2. Baixa autos completos via pje_standalone.py (Playwright)
  3. Extrai texto com pdftotext
  4. Gera FICHA.json padronizada
  5. Valida integridade do download
  6. Notifica Telegram

Estrutura de destino:
  ~/processos/{numero_cnj}/{data}/
  ├── autos-completos.pdf
  ├── FICHA.json
  ├── movimento.txt
  └── raw/

Uso:
  python3 pipeline_aquisicao.py --cnj 5001615-98.2025.8.13.0074
  python3 pipeline_aquisicao.py --cnj 5001615-98.2025.8.13.0074 5002424-12.2025.8.13.0105
  python3 pipeline_aquisicao.py --from-monitor            # Lê último resultado do monitor
  python3 pipeline_aquisicao.py --from-json resultado.json # Lê JSON com cnjs_detectados
  python3 pipeline_aquisicao.py --dry-run --cnj ...        # Simula sem baixar
  python3 pipeline_aquisicao.py --skip-download --cnj ...  # Só metadados + ficha (sem browser)

IMPORTANTE: O download via PJe requer login VidaaS (manual, 1x por sessão).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO
# ============================================================

STEMMIA_DIR = Path.home() / "stemmia-forense"
PJE_STANDALONE = STEMMIA_DIR / "src" / "pje" / "pje_standalone.py"
MONITOR_RESULTADOS = STEMMIA_DIR / "src" / "pje" / "monitor-publicacoes" / "resultados"

try:
    sys.path.insert(0, str(STEMMIA_DIR))
    from src.pje.datajud_client import consultar_processo as _datajud_consultar
except ImportError:
    _datajud_consultar = None

PROCESSOS_DIR = Path.home() / "processos"
LOG_DIR = STEMMIA_DIR / "logs"

RE_CNJ = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')

# Tamanho mínimo para considerar PDF válido (50KB)
PDF_MIN_SIZE = 50 * 1024

try:
    from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
except ImportError:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8397602236")


# ============================================================
# CORES E LOG
# ============================================================

class C:
    R = "\033[0m"
    B = "\033[1m"
    G = "\033[32m"
    Y = "\033[33m"
    RE = "\033[31m"
    CY = "\033[36m"


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ", "OK": "✓", "ERRO": "✗", "AVISO": "⚠", "NOVO": "★"}.get(level, "·")
    print(f"  [{ts}] {prefix} {msg}", file=sys.stderr)


def log_arquivo(msg):
    """Append ao log persistente."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / "pipeline-aquisicao.log"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


# ============================================================
# 1. CONSULTA METADADOS (DataJud API)
# ============================================================

def consultar_metadados(cnj):
    """Consulta metadados do processo via DataJud API (import direto)."""
    log(f"Consultando metadados DataJud: {cnj}")

    if _datajud_consultar is None:
        log("datajud_client nao disponivel — import falhou", "ERRO")
        return None

    try:
        dados = _datajud_consultar(cnj)
        if not dados:
            log("Processo nao encontrado na API DataJud", "AVISO")
            return None

        # Adaptar formato _source do DataJud para o esperado por gerar_ficha()
        classe = dados.get("classe", {})
        orgao = dados.get("orgaoJulgador", {})
        assuntos = dados.get("assuntos", [])
        movs_raw = dados.get("movimentos", [])

        metadados = {
            "encontrado": True,
            "classe": classe.get("nome", "") if isinstance(classe, dict) else str(classe),
            "orgao_julgador": orgao.get("nome", "") if isinstance(orgao, dict) else str(orgao),
            "assuntos": ", ".join(a.get("nome", "") for a in assuntos if isinstance(a, dict)),
            "total_movimentacoes": len(movs_raw),
            "movimentacoes_recentes": len(movs_raw[:20]),
            "movimentacoes": [
                {
                    "data": m.get("dataHora", "")[:10],
                    "nome": m.get("nome", m.get("descricao", "")),
                }
                for m in movs_raw[:20]
            ],
        }

        log(f"Metadados obtidos: {metadados['classe']}", "OK")
        return metadados

    except Exception as e:
        log(f"Erro ao consultar DataJud: {e}", "ERRO")
        return None


# ============================================================
# 2. PREPARAR ESTRUTURA DE DESTINO
# ============================================================

def preparar_pasta(cnj):
    """
    Cria estrutura de pasta para o processo.

    Retorna:
      ~/processos/{cnj}/{data_hoje}/
      ├── raw/
    """
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    pasta = PROCESSOS_DIR / cnj / data_hoje
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "raw").mkdir(exist_ok=True)

    # Symlink "latest" na pasta do processo
    latest = PROCESSOS_DIR / cnj / "latest"
    if latest.is_symlink():
        latest.unlink()
    try:
        latest.symlink_to(pasta.name)
    except OSError:
        pass  # Windows ou permissão

    log(f"Pasta criada: {pasta}", "OK")
    return pasta


# ============================================================
# 3. DOWNLOAD VIA PJE_STANDALONE
# ============================================================

def baixar_autos(cnj, pasta_destino):
    """
    Baixa autos completos via pje_standalone.py.

    O pje_standalone usa Playwright + Chromium, abre browser visível,
    faz login VidaaS (manual 1x), depois baixa automaticamente.

    Retorna: Path do PDF baixado ou None.
    """
    if not PJE_STANDALONE.exists():
        log(f"pje_standalone.py não encontrado em {PJE_STANDALONE}", "ERRO")
        return None

    log(f"Baixando autos via PJe: {cnj}")
    log("Se o browser abrir, faça login VidaaS quando solicitado", "AVISO")

    try:
        result = subprocess.run(
            [sys.executable, str(PJE_STANDALONE),
             "--baixar", cnj,
             "--saida", str(pasta_destino),
             "--json"],
            capture_output=True, text=True,
            timeout=600,  # 10 min (inclui tempo de login manual)
            cwd=str(STEMMIA_DIR),
        )

        # Verificar se o PDF foi baixado
        # pje_standalone salva em {saida}/{cnj}/autos-completos.pdf
        pdf_subpasta = pasta_destino / cnj / "autos-completos.pdf"
        pdf_direto = pasta_destino / "autos-completos.pdf"

        pdf_path = None
        if pdf_subpasta.exists():
            pdf_path = pdf_subpasta
        elif pdf_direto.exists():
            pdf_path = pdf_direto
        else:
            # Buscar qualquer PDF novo na pasta
            for f in pasta_destino.rglob("*.pdf"):
                if f.stat().st_size > PDF_MIN_SIZE:
                    pdf_path = f
                    break

        if pdf_path:
            # Mover para localização padrão se não estiver lá
            destino_final = pasta_destino / "autos-completos.pdf"
            if pdf_path != destino_final:
                shutil.move(str(pdf_path), str(destino_final))
                pdf_path = destino_final

            tamanho_mb = pdf_path.stat().st_size / (1024 * 1024)
            log(f"PDF baixado: {tamanho_mb:.1f} MB", "OK")
            return pdf_path
        else:
            stderr = result.stderr[:300] if result.stderr else ""
            log(f"PDF não encontrado após download. stderr: {stderr}", "ERRO")
            return None

    except subprocess.TimeoutExpired:
        log("Timeout no download (>10 min)", "ERRO")
        return None
    except Exception as e:
        log(f"Erro no download: {e}", "ERRO")
        return None


# ============================================================
# 4. EXTRAIR TEXTO
# ============================================================

def extrair_texto(pdf_path, pasta_destino):
    """
    Extrai texto do PDF com pdftotext.
    Salva como movimento.txt na pasta de destino.
    """
    txt_path = pasta_destino / "movimento.txt"

    # Tentar pdftotext (poppler-utils)
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), str(txt_path)],
            capture_output=True, timeout=120,
        )
        if result.returncode == 0 and txt_path.exists() and txt_path.stat().st_size > 0:
            tamanho_kb = txt_path.stat().st_size / 1024
            log(f"Texto extraído: {tamanho_kb:.0f} KB", "OK")
            return txt_path
    except FileNotFoundError:
        log("pdftotext não encontrado. Instale: brew install poppler", "AVISO")
    except subprocess.TimeoutExpired:
        log("Timeout na extração de texto (>2 min)", "AVISO")
    except Exception as e:
        log(f"Erro na extração: {e}", "AVISO")

    return None


# ============================================================
# 5. GERAR FICHA.JSON
# ============================================================

def gerar_ficha(cnj, pasta_destino, metadados=None, pdf_path=None, txt_path=None):
    """
    Gera FICHA.json padronizada com metadados do processo.
    """
    ficha = {
        "numero_cnj": cnj,
        "adquirido_em": datetime.now().isoformat(),
        "pipeline_versao": "1.0",
        "fonte": "pipeline_aquisicao.py",
    }

    # Metadados da API
    if metadados:
        ficha["classe"] = metadados.get("classe", "")
        ficha["orgao_julgador"] = metadados.get("orgao_julgador", "")
        ficha["assuntos"] = metadados.get("assuntos", "")
        ficha["total_movimentacoes"] = metadados.get("total_movimentacoes", 0)
        ficha["movimentacoes_recentes"] = metadados.get("movimentacoes_recentes", 0)

        # Última movimentação
        movs = metadados.get("movimentacoes", [])
        if movs:
            ficha["ultima_movimentacao"] = {
                "data": movs[0].get("data", ""),
                "nome": movs[0].get("nome", ""),
            }

    # Info do PDF
    if pdf_path and pdf_path.exists():
        stat = pdf_path.stat()
        ficha["pdf"] = {
            "arquivo": pdf_path.name,
            "tamanho_bytes": stat.st_size,
            "tamanho_mb": round(stat.st_size / (1024 * 1024), 1),
            "baixado_em": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

    # Info do texto extraído
    if txt_path and txt_path.exists():
        ficha["texto_extraido"] = {
            "arquivo": txt_path.name,
            "tamanho_bytes": txt_path.stat().st_size,
        }

    # Status
    ficha["status"] = {
        "metadados": "ok" if metadados else "sem_dados",
        "pdf": "ok" if (pdf_path and pdf_path.exists()) else "pendente",
        "texto": "ok" if (txt_path and txt_path.exists()) else "pendente",
    }

    ficha_path = pasta_destino / "FICHA.json"
    ficha_path.write_text(
        json.dumps(ficha, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    log(f"FICHA.json gerada", "OK")
    return ficha_path


# ============================================================
# 6. VALIDAR INTEGRIDADE
# ============================================================

def validar_download(pasta_destino, cnj):
    """
    Valida integridade do download:
      - PDF existe e tem tamanho > threshold
      - PDF é válido (header %PDF)
      - FICHA.json existe e é JSON válido
      - movimento.txt existe (se PDF existe)

    Retorna: (ok: bool, erros: list)
    """
    erros = []

    pdf_path = pasta_destino / "autos-completos.pdf"
    ficha_path = pasta_destino / "FICHA.json"
    txt_path = pasta_destino / "movimento.txt"

    # PDF
    if not pdf_path.exists():
        erros.append("PDF não encontrado")
    else:
        size = pdf_path.stat().st_size
        if size < PDF_MIN_SIZE:
            erros.append(f"PDF muito pequeno ({size} bytes, mínimo {PDF_MIN_SIZE})")

        # Verificar header PDF
        try:
            with open(pdf_path, "rb") as f:
                header = f.read(5)
            if header != b"%PDF-":
                erros.append(f"Arquivo não é PDF válido (header: {header!r})")
        except Exception as e:
            erros.append(f"Erro ao ler header do PDF: {e}")

    # FICHA.json
    if not ficha_path.exists():
        erros.append("FICHA.json não encontrada")
    else:
        try:
            json.loads(ficha_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            erros.append(f"FICHA.json inválida: {e}")

    # movimento.txt (warning, não erro)
    if pdf_path.exists() and not txt_path.exists():
        erros.append("movimento.txt não gerado (pdftotext pode estar ausente)")

    ok = len(erros) == 0
    if ok:
        log(f"Validação OK: {cnj}", "OK")
    else:
        for e in erros:
            log(f"Validação: {e}", "AVISO")

    return ok, erros


# ============================================================
# 7. NOTIFICAR TELEGRAM
# ============================================================

def notificar_telegram(resultados):
    """Envia resumo da aquisição via Telegram."""
    if not TELEGRAM_BOT_TOKEN:
        log("Token Telegram não configurado, pulando notificação", "AVISO")
        return

    total = len(resultados)
    ok = sum(1 for r in resultados if r["status"] == "OK")
    erros = sum(1 for r in resultados if r["status"] == "ERRO")
    parciais = sum(1 for r in resultados if r["status"] == "PARCIAL")

    msg = f"<b>Pipeline Aquisição</b>\n"
    msg += f"{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    msg += f"Total: {total} | OK: {ok} | Erro: {erros}"
    if parciais:
        msg += f" | Parcial: {parciais}"
    msg += "\n"

    for r in resultados:
        icone = "✓" if r["status"] == "OK" else "⚠" if r["status"] == "PARCIAL" else "✗"
        msg += f"\n{icone} {r['cnj']}"
        if r.get("tamanho_mb"):
            msg += f" ({r['tamanho_mb']} MB)"
        if r.get("erros"):
            msg += f"\n  {'; '.join(r['erros'][:2])}"

    try:
        import requests
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"},
            timeout=10,
        )
        if resp.ok:
            log("Telegram notificado", "OK")
        else:
            log(f"Telegram erro: {resp.status_code}", "AVISO")
    except Exception as e:
        log(f"Erro ao notificar Telegram: {e}", "AVISO")


# ============================================================
# PIPELINE PRINCIPAL
# ============================================================

def adquirir_processo(cnj, skip_download=False, dry_run=False):
    """
    Executa pipeline completo para um processo.

    Args:
        cnj: Número CNJ do processo
        skip_download: Se True, só consulta metadados (sem browser)
        dry_run: Se True, só mostra o que faria

    Returns:
        Dict com resultado da aquisição
    """
    resultado = {
        "cnj": cnj,
        "inicio": datetime.now().isoformat(),
        "status": "PENDENTE",
        "erros": [],
    }

    log(f"\n{'═' * 60}")
    log(f"ADQUIRINDO: {cnj}")
    log(f"{'═' * 60}")

    if dry_run:
        log("[DRY RUN] Simulação — nenhuma ação executada", "AVISO")
        resultado["status"] = "DRY_RUN"
        return resultado

    # 1. Preparar pasta
    pasta = preparar_pasta(cnj)
    resultado["pasta"] = str(pasta)

    # 2. Consultar metadados
    metadados = consultar_metadados(cnj)
    resultado["metadados_ok"] = metadados is not None

    # 3. Download (se não skip)
    pdf_path = None
    txt_path = None

    if not skip_download:
        pdf_path = baixar_autos(cnj, pasta)
        resultado["pdf_baixado"] = pdf_path is not None

        if pdf_path:
            resultado["tamanho_mb"] = round(pdf_path.stat().st_size / (1024 * 1024), 1)

            # 4. Extrair texto
            txt_path = extrair_texto(pdf_path, pasta)
            resultado["texto_extraido"] = txt_path is not None
    else:
        log("Download pulado (--skip-download)", "INFO")
        resultado["pdf_baixado"] = False

    # 5. Gerar FICHA.json
    gerar_ficha(cnj, pasta, metadados=metadados, pdf_path=pdf_path, txt_path=txt_path)

    # 6. Validar
    if not skip_download:
        ok, erros = validar_download(pasta, cnj)
        resultado["validacao_ok"] = ok
        resultado["erros"] = erros

        if ok:
            resultado["status"] = "OK"
        elif pdf_path:
            resultado["status"] = "PARCIAL"
        else:
            resultado["status"] = "ERRO"
    else:
        resultado["status"] = "METADADOS_ONLY"

    resultado["fim"] = datetime.now().isoformat()
    log_arquivo(f"{resultado['status']} {cnj} pasta={pasta}")

    return resultado


def carregar_cnjs_do_monitor():
    """
    Lê o último resultado do monitor e extrai cnjs_detectados.
    Busca o arquivo mais recente em resultados/.
    """
    if not MONITOR_RESULTADOS.exists():
        log("Pasta de resultados do monitor não encontrada", "ERRO")
        return []

    arquivos = sorted(
        MONITOR_RESULTADOS.glob("monitor-completo-*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    if not arquivos:
        log("Nenhum resultado do monitor encontrado", "ERRO")
        return []

    ultimo = arquivos[0]
    log(f"Lendo resultado do monitor: {ultimo.name}")

    try:
        data = json.loads(ultimo.read_text(encoding="utf-8"))
        cnjs = data.get("cnjs_detectados", [])
        if cnjs:
            log(f"{len(cnjs)} CNJ(s) detectados pelo monitor", "OK")
        else:
            log("Nenhum CNJ detectado no último resultado", "INFO")
        return cnjs
    except (json.JSONDecodeError, OSError) as e:
        log(f"Erro ao ler resultado: {e}", "ERRO")
        return []


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de Aquisição Processual — Stemmia Forense",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python3 pipeline_aquisicao.py --cnj 5001615-98.2025.8.13.0074\n"
            "  python3 pipeline_aquisicao.py --from-monitor\n"
            "  python3 pipeline_aquisicao.py --dry-run --cnj 5001615-98.2025.8.13.0074\n"
            "  python3 pipeline_aquisicao.py --skip-download --cnj ...\n"
        ),
    )
    parser.add_argument("--cnj", nargs="+", metavar="CNJ",
                        help="CNJ(s) para adquirir")
    parser.add_argument("--from-monitor", action="store_true",
                        help="Lê CNJs do último resultado do monitor")
    parser.add_argument("--from-json", type=str, metavar="ARQUIVO",
                        help="Lê CNJs de arquivo JSON (campo cnjs_detectados)")
    parser.add_argument("--skip-download", action="store_true",
                        help="Só metadados, sem browser/download")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simula sem executar")
    parser.add_argument("--json", action="store_true",
                        help="Saída JSON")
    parser.add_argument("--no-telegram", action="store_true",
                        help="Não enviar notificação Telegram")

    args = parser.parse_args()

    # Determinar CNJs
    cnjs = []

    if args.cnj:
        cnjs = args.cnj
    elif args.from_monitor:
        cnjs = carregar_cnjs_do_monitor()
    elif args.from_json:
        try:
            data = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
            cnjs = data.get("cnjs_detectados", data.get("cnjs", []))
        except Exception as e:
            log(f"Erro ao ler {args.from_json}: {e}", "ERRO")
            sys.exit(1)

    if not cnjs:
        log("Nenhum CNJ para processar. Use --cnj, --from-monitor ou --from-json.", "ERRO")
        sys.exit(1)

    # Validar formato
    invalidos = [c for c in cnjs if not RE_CNJ.match(c)]
    if invalidos:
        for c in invalidos:
            log(f"CNJ inválido: {c}", "ERRO")
        sys.exit(1)

    # Remover duplicatas preservando ordem
    vistos = set()
    cnjs_unicos = []
    for c in cnjs:
        if c not in vistos:
            vistos.add(c)
            cnjs_unicos.append(c)
    cnjs = cnjs_unicos

    # Executar pipeline
    print(f"\n  {C.B}{'═' * 60}{C.R}", file=sys.stderr)
    print(f"  {C.B}  PIPELINE DE AQUISIÇÃO PROCESSUAL{C.R}", file=sys.stderr)
    print(f"  {C.B}  {datetime.now().strftime('%d/%m/%Y %H:%M')}{C.R}", file=sys.stderr)
    print(f"  {C.B}  {len(cnjs)} processo(s) para adquirir{C.R}", file=sys.stderr)
    if args.skip_download:
        print(f"  {C.Y}  Modo: somente metadados (sem download){C.R}", file=sys.stderr)
    if args.dry_run:
        print(f"  {C.Y}  Modo: dry-run (simulação){C.R}", file=sys.stderr)
    print(f"  {C.B}{'═' * 60}{C.R}\n", file=sys.stderr)

    resultados = []
    for i, cnj in enumerate(cnjs, 1):
        log(f"\n[{i}/{len(cnjs)}] Processando {cnj}")
        resultado = adquirir_processo(
            cnj,
            skip_download=args.skip_download,
            dry_run=args.dry_run,
        )
        resultados.append(resultado)

    # Resumo
    ok = sum(1 for r in resultados if r["status"] == "OK")
    erros = sum(1 for r in resultados if r["status"] == "ERRO")
    parciais = sum(1 for r in resultados if r["status"] == "PARCIAL")

    print(f"\n  {C.B}{'═' * 60}{C.R}", file=sys.stderr)
    print(f"  {C.B}RESUMO{C.R}", file=sys.stderr)
    print(f"  Total: {len(cnjs)}", file=sys.stderr)
    print(f"  OK: {C.G}{ok}{C.R}  Parcial: {C.Y}{parciais}{C.R}  Erro: {C.RE}{erros}{C.R}", file=sys.stderr)
    print(f"  {C.B}{'═' * 60}{C.R}\n", file=sys.stderr)

    # Saída JSON
    if args.json:
        print(json.dumps({
            "data": datetime.now().isoformat(),
            "total": len(cnjs),
            "ok": ok,
            "erros": erros,
            "parciais": parciais,
            "resultados": resultados,
        }, ensure_ascii=False, indent=2))

    # Salvar relatório
    PROCESSOS_DIR.mkdir(parents=True, exist_ok=True)
    relatorio_path = PROCESSOS_DIR / "ultima-aquisicao.json"
    relatorio_path.write_text(json.dumps({
        "data": datetime.now().isoformat(),
        "total": len(cnjs),
        "ok": ok,
        "erros": erros,
        "resultados": resultados,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # Notificar Telegram
    if not args.no_telegram and not args.dry_run and resultados:
        notificar_telegram(resultados)

    # Exit code
    if erros > 0 and ok == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
