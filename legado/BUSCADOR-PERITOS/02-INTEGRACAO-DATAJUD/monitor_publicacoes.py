#!/usr/bin/env python3
"""
Orquestrador do Monitor de Publicações Judiciais.

Roda TODAS as fontes em sequência:
  1. DataJud API (movimentações processuais) — sempre funciona
  2. DJe TJMG (publicações no diário) — sempre funciona
  3. Comunicações PJe/DJEN (intimações) — requer cadastro CNJ

NÃO gasta tokens Anthropic. Tudo é Python puro + APIs públicas gratuitas.

Uso:
  python3 monitor_publicacoes.py                  # Roda tudo
  python3 monitor_publicacoes.py --fonte datajud  # Só DataJud
  python3 monitor_publicacoes.py --fonte dje      # Só DJe
  python3 monitor_publicacoes.py --fonte comunica # Só Comunicações
  python3 monitor_publicacoes.py --dias 7         # Últimos 7 dias
  python3 monitor_publicacoes.py --notificar      # Notifica macOS se achar algo
  python3 monitor_publicacoes.py --telegram       # Envia resumo pro Telegram

Cron recomendado (6h seg-sáb):
  0 6 * * 1-6 cd ~/Desktop/ANALISADOR\ FINAL && python3 scripts/monitor-publicacoes/monitor_publicacoes.py --notificar --salvar 2>>scripts/monitor-publicacoes/monitor.log
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO
# ============================================================

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent.parent
SAIDA_DIR = SCRIPT_DIR / "resultados"
LOG_FILE = SCRIPT_DIR / "monitor.log"

# Dados do perito para notificação
PERITO = "Dr. Jesus Eduardo Noleto da Penha"
try:
    from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
except ImportError:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()


# ============================================================
# CORES
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


# ============================================================
# IMPORTAÇÃO DINÂMICA DOS MÓDULOS
# ============================================================

def importar_modulo(nome_arquivo):
    """Importa módulo Python do mesmo diretório."""
    caminho = SCRIPT_DIR / nome_arquivo
    if not caminho.exists():
        log(f"Módulo não encontrado: {caminho}", "ERRO")
        return None
    spec = importlib.util.spec_from_file_location(nome_arquivo.replace(".py", ""), str(caminho))
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        log(f"Erro ao importar {nome_arquivo}: {e}", "ERRO")
        return None


# ============================================================
# NOTIFICAÇÕES
# ============================================================

def notificar_macos(titulo, mensagem):
    """Envia notificação macOS. Escapa aspas para evitar AppleScript injection."""
    def _esc(s):
        return str(s).replace("\\", "\\\\").replace('"', '\\"')
    try:
        subprocess.run([
            "osascript", "-e",
            f'display notification "{_esc(mensagem)}" with title "{_esc(titulo)}" sound name "Glass"'
        ], capture_output=True, timeout=5)
    except Exception:
        pass


def notificar_telegram(mensagem, token=None, chat_id=None):
    """Envia mensagem ao Telegram."""
    token = token or TELEGRAM_BOT_TOKEN
    chat_id = chat_id or TELEGRAM_CHAT_ID
    if not token or not chat_id:
        return False

    try:
        import requests
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": mensagem, "parse_mode": "HTML"},
            timeout=10,
        )
        return resp.ok
    except Exception:
        return False


def tocar_som():
    """Toca som de notificação."""
    try:
        subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], capture_output=True, timeout=5)
    except Exception:
        pass


# ============================================================
# ORQUESTRADOR
# ============================================================

def executar(fontes=None, dias=7, notificar=False, telegram=False, salvar=False):
    """Executa monitoramento em todas as fontes."""

    if fontes is None:
        fontes = ["datajud", "dje", "comunica"]

    print(f"\n  {C.B}{'═' * 60}{C.R}", file=sys.stderr)
    print(f"  {C.B}  MONITOR DE PUBLICAÇÕES JUDICIAIS{C.R}", file=sys.stderr)
    print(f"  {C.B}  {datetime.now().strftime('%d/%m/%Y %H:%M')}{C.R}", file=sys.stderr)
    print(f"  {C.B}{'═' * 60}{C.R}", file=sys.stderr)

    resumo_geral = {
        "data": datetime.now().isoformat(),
        "fontes": {},
        "alertas": [],
        "cnjs_detectados": [],
    }

    # ─── FONTE 1: DataJud API ───
    if "datajud" in fontes:
        print(f"\n  {C.B}[1/3] DataJud API — Movimentações{C.R}", file=sys.stderr)
        print(f"  {'─' * 50}", file=sys.stderr)

        mod = importar_modulo("datajud_api.py")
        if mod:
            try:
                cnjs = mod.carregar_cnjs_ativos()
                if cnjs:
                    resultado = mod.monitorar(cnjs, dias=dias, modo_json=False, salvar=salvar)
                    resumo_geral["fontes"]["datajud"] = {
                        "status": "ok",
                        "processos": resultado.get("total_processos", 0),
                        "com_movimentacoes": resultado.get("com_movimentacoes", 0),
                        "total_movimentacoes": resultado.get("total_movimentacoes", 0),
                    }

                    if resultado.get("com_movimentacoes", 0) > 0:
                        resumo_geral["alertas"].append(
                            f"DataJud: {resultado['com_movimentacoes']} processo(s) com movimentação"
                        )
                        # Propagar CNJs com movimentação para pipeline
                        for r in resultado.get("resultados", []):
                            if r.get("movimentacoes_recentes", 0) > 0 and r.get("cnj"):
                                if r["cnj"] not in resumo_geral["cnjs_detectados"]:
                                    resumo_geral["cnjs_detectados"].append(r["cnj"])
                else:
                    log("Sem processos ativos para monitorar", "AVISO")
                    resumo_geral["fontes"]["datajud"] = {"status": "sem_processos"}
            except Exception as e:
                log(f"Erro no DataJud: {e}", "ERRO")
                resumo_geral["fontes"]["datajud"] = {"status": "erro", "erro": str(e)}
        else:
            resumo_geral["fontes"]["datajud"] = {"status": "modulo_nao_encontrado"}

    # ─── FONTE 2: DJe TJMG ───
    if "dje" in fontes:
        print(f"\n  {C.B}[2/3] DJe TJMG — Publicações no Diário{C.R}", file=sys.stderr)
        print(f"  {'─' * 50}", file=sys.stderr)

        mod = importar_modulo("dje_tjmg.py")
        if mod:
            try:
                hoje = datetime.now()
                from datetime import timedelta
                datas = []
                for i in range(dias if dias <= 7 else 7):  # Máximo 7 dias no DJe
                    d = hoje - timedelta(days=i)
                    if d.weekday() != 6:  # Pula domingo
                        datas.append(d.strftime("%d/%m/%Y"))

                resultado = mod.monitorar(datas, modo_json=False, salvar=salvar)
                resumo_geral["fontes"]["dje"] = {
                    "status": "ok",
                    "datas": datas,
                    "total_matches": resultado.get("total_matches", 0),
                }

                if resultado.get("total_matches", 0) > 0:
                    resumo_geral["alertas"].append(
                        f"DJe: {resultado['total_matches']} publicação(ões) encontrada(s)!"
                    )
                    # Propagar CNJs descobertos no DJe para pipeline
                    for cnj in resultado.get("cnjs_descobertos", []):
                        if cnj not in resumo_geral["cnjs_detectados"]:
                            resumo_geral["cnjs_detectados"].append(cnj)
            except Exception as e:
                log(f"Erro no DJe: {e}", "ERRO")
                resumo_geral["fontes"]["dje"] = {"status": "erro", "erro": str(e)}
        else:
            resumo_geral["fontes"]["dje"] = {"status": "modulo_nao_encontrado"}

    # ─── FONTE 3: Comunicações PJe ───
    if "comunica" in fontes:
        print(f"\n  {C.B}[3/3] Comunicações PJe/DJEN{C.R}", file=sys.stderr)
        print(f"  {'─' * 50}", file=sys.stderr)

        cred_file = SCRIPT_DIR / ".credenciais-cnj.json"
        if cred_file.exists():
            mod = importar_modulo("comunica_pje.py")
            if mod:
                try:
                    cnjs = mod.carregar_cnjs_ativos()
                    if cnjs:
                        resultado = mod.monitorar(cnjs, dias=min(dias, 7), modo_json=False, salvar=salvar)
                        resumo_geral["fontes"]["comunica"] = {"status": "ok"}
                    else:
                        resumo_geral["fontes"]["comunica"] = {"status": "sem_processos"}
                except Exception as e:
                    log(f"Erro nas Comunicações: {e}", "ERRO")
                    resumo_geral["fontes"]["comunica"] = {"status": "erro", "erro": str(e)}
        else:
            log("Credenciais CNJ não configuradas — pulando", "AVISO")
            log("Rode: python3 comunica_pje.py --cadastro", "INFO")
            resumo_geral["fontes"]["comunica"] = {"status": "sem_credenciais"}

    # ─── RESUMO FINAL ───
    print(f"\n  {C.B}{'═' * 60}{C.R}", file=sys.stderr)
    print(f"  {C.B}RESUMO DO MONITORAMENTO{C.R}", file=sys.stderr)
    print(f"  {'─' * 50}", file=sys.stderr)

    for fonte, info in resumo_geral["fontes"].items():
        status = info.get("status", "?")
        if status == "ok":
            print(f"  {C.G}✓{C.R} {fonte}: OK", file=sys.stderr)
        elif status == "sem_credenciais":
            print(f"  {C.Y}⚠{C.R} {fonte}: sem credenciais (rode --cadastro)", file=sys.stderr)
        elif status == "erro":
            print(f"  {C.RE}✗{C.R} {fonte}: {info.get('erro', 'erro desconhecido')}", file=sys.stderr)
        else:
            print(f"  {C.Y}⚠{C.R} {fonte}: {status}", file=sys.stderr)

    if resumo_geral["alertas"]:
        print(f"\n  {C.RE}{C.B}ALERTAS:{C.R}", file=sys.stderr)
        for alerta in resumo_geral["alertas"]:
            print(f"  {C.RE}★ {alerta}{C.R}", file=sys.stderr)

    print(f"  {C.B}{'═' * 60}{C.R}\n", file=sys.stderr)

    # ─── NOTIFICAÇÕES ───
    if resumo_geral["alertas"]:
        msg = "\n".join(resumo_geral["alertas"])

        if notificar:
            notificar_macos("Monitor Judicial", msg)
            tocar_som()

        if telegram:
            texto_telegram = f"<b>Monitor Judicial</b>\n{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            texto_telegram += "\n".join(f"• {a}" for a in resumo_geral["alertas"])
            notificar_telegram(texto_telegram)

    # ─── SALVAR ───
    if salvar:
        SAIDA_DIR.mkdir(parents=True, exist_ok=True)
        data_str = datetime.now().strftime("%Y-%m-%d_%H%M")
        saida = SAIDA_DIR / f"monitor-completo-{data_str}.json"
        saida.write_text(json.dumps(resumo_geral, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"Resumo salvo em {saida}", "OK")

    return resumo_geral


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Monitor de publicações judiciais — orquestrador",
    )
    parser.add_argument("--fonte", choices=["datajud", "dje", "comunica"], nargs="+",
                        help="Fontes específicas (padrão: todas)")
    parser.add_argument("--dias", type=int, default=7, help="Últimos N dias (padrão: 7)")
    parser.add_argument("--notificar", action="store_true", help="Notificação macOS")
    parser.add_argument("--telegram", action="store_true", help="Enviar pro Telegram")
    parser.add_argument("--salvar", action="store_true", help="Salvar resultados")

    args = parser.parse_args()
    executar(
        fontes=args.fonte,
        dias=args.dias,
        notificar=args.notificar,
        telegram=args.telegram,
        salvar=args.salvar,
    )


if __name__ == "__main__":
    main()
