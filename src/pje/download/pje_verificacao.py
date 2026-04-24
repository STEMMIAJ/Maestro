"""Verificação pós-download, ordenação por comarca, janela TJMG e Telegram.

Chamado por baixar_push_pje.py. Isolado para permitir auditoria independente
e reutilização por outros scripts.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from datetime import datetime, time as dtime
from pathlib import Path
from typing import Optional, Tuple

try:
    import urllib.request as _urlreq
    import urllib.parse as _urlparse
    import json as _json
except Exception:  # pragma: no cover
    _urlreq = None

try:
    from dotenv import load_dotenv
    # Tenta carregar .env do projeto (3 níveis acima = raiz stemmia-forense)
    for candidate in (
        Path(__file__).resolve().parents[2] / ".env",
        Path.home() / ".env",
        Path.home() / "stemmia-forense" / ".env",
    ):
        if candidate.exists():
            load_dotenv(candidate)
            break
except ImportError:
    pass

CNJ_CANONICO_RE = re.compile(
    r"N[úu]mero\s*:\s*(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})", re.IGNORECASE
)
CNJ_GENERICO_RE = re.compile(r"\b(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})\b")
COMARCA_RE = re.compile(r"Comarca\s+de\s+([^\n,/\-]+)", re.IGNORECASE)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT = os.getenv("TELEGRAM_CHAT_ID", "8397602236").strip()

# Janela oficial TJMG em que download integral dos autos fica indisponível
JANELA_INDISP_INICIO = dtime(13, 0)  # 13:00
JANELA_INDISP_FIM = dtime(19, 0)     # 19:00


def normaliza_cnj(s: Optional[str]) -> str:
    return re.sub(r"\D", "", s or "")


def slug_comarca(s: Optional[str]) -> str:
    s = s or ""
    s = re.sub(r"[^\w\s\-]", "", s, flags=re.UNICODE).strip()
    s = re.sub(r"\s+", "-", s)
    return s[:40] or "sem-comarca"


def extrair_texto_pag1(pdf_path: Path, timeout: int = 45) -> str:
    """Extrai texto da primeira página via pdftotext (Poppler)."""
    try:
        r = subprocess.run(
            ["pdftotext", "-f", "1", "-l", "1", "-layout", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout or ""
    except FileNotFoundError:
        # Windows pode não ter pdftotext no PATH
        return ""
    except Exception:
        return ""


def verificar_conteudo(pdf_path: Path, cnj_esperado: str) -> Tuple[bool, str, str, str]:
    """Verifica se o PDF realmente pertence ao CNJ esperado.

    Retorna (ok, cnj_real, comarca, razao).
      ok = True se CNJ canônico (campo 'Número:') bate com esperado
      cnj_real = CNJ encontrado (canônico se existir, senão primeiro da pág 1)
      comarca = nome extraído de 'Comarca de ...'
      razao = descrição ('match', 'divergente', 'sem_campo_numero', 'sem_texto', ...)
    """
    texto = extrair_texto_pag1(pdf_path)
    if not texto.strip():
        return False, "", "", "sem_texto"

    m_can = CNJ_CANONICO_RE.search(texto)
    cnj_canonico = m_can.group(1) if m_can else ""

    todos = CNJ_GENERICO_RE.findall(texto)
    cnj_real = cnj_canonico or (todos[0] if todos else "")

    comarca = ""
    mc = COMARCA_RE.search(texto)
    if mc:
        comarca = re.sub(r"\s+", " ", mc.group(1)).strip(" .,-")

    if not cnj_canonico:
        return False, cnj_real, comarca, "sem_campo_numero"

    if normaliza_cnj(cnj_canonico) == normaliza_cnj(cnj_esperado):
        return True, cnj_canonico, comarca, "match"
    return False, cnj_canonico, comarca, "divergente"


def janela_disponivel(now: Optional[datetime] = None) -> Tuple[bool, str]:
    """PJe TJMG: download integral indisponível 13h–19h (hora de Brasília).

    Retorna (disponivel, mensagem).
    """
    now = now or datetime.now()
    h = now.time()
    if JANELA_INDISP_INICIO <= h < JANELA_INDISP_FIM:
        falta = (JANELA_INDISP_FIM.hour * 60) - (h.hour * 60 + h.minute)
        return False, (
            f"Janela TJMG indisponível (13h–19h). "
            f"Liberação em ~{falta} min. "
            "Fonte: informe oficial TJMG."
        )
    return True, "Janela liberada"


def esperar_janela_liberar(log_fn=print, check_interval: int = 60) -> None:
    """Aguarda até a janela 13-19h terminar. Imprime status a cada check."""
    while True:
        ok, msg = janela_disponivel()
        if ok:
            return
        log_fn(f"[JANELA] {msg}")
        time.sleep(check_interval)


def notificar_telegram(msg: str, silent: bool = False, log_fn=print) -> bool:
    """Envia mensagem ao bot Telegram. Retorna True se enviou.

    Se token não configurado, apenas loga e retorna False — não levanta.
    """
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "..." or len(TELEGRAM_TOKEN) < 20:
        log_fn(f"[TELEGRAM skip — sem token] {msg[:80]}")
        return False
    if _urlreq is None:
        log_fn("[TELEGRAM skip — urllib indisponível]")
        return False
    try:
        data = _urlparse.urlencode({
            "chat_id": TELEGRAM_CHAT,
            "text": msg,
            "parse_mode": "HTML",
            "disable_notification": "true" if silent else "false",
        }).encode()
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        req = _urlreq.Request(url, data=data, method="POST")
        with _urlreq.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            try:
                j = _json.loads(raw)
                return bool(j.get("ok"))
            except Exception:
                return True
    except Exception as e:
        log_fn(f"[TELEGRAM erro] {e}")
        return False


def ordenar_por_comarca(procs: list, ordem: list) -> list:
    """Ordena lista de procs por código de comarca (últimos 4 dígitos do CNJ).

    procs: lista de dicts com chave 'numero' (CNJ)
    ordem: lista de códigos ['0680','0627','0105','0396'] — demais vão ao fim
    """
    rank = {c: i for i, c in enumerate(ordem)}
    sentinela = len(ordem) + 1

    def chave(p):
        cnj = p.get("numero", "")
        cod = cnj[-4:] if len(cnj) >= 4 else ""
        return (rank.get(cod, sentinela), cnj)

    return sorted(procs, key=chave)


def comarca_de_cnj(cnj: str) -> str:
    """Retorna código de comarca (últimos 4 dígitos do CNJ)."""
    return cnj[-4:] if cnj and len(cnj) >= 4 else ""


def mover_para_quarentena(pdf_path: Path, sub: str, novo_nome: Optional[str] = None) -> Path:
    """Move PDF para pasta de quarentena, criando se necessário."""
    quarentena = pdf_path.parent / sub
    quarentena.mkdir(exist_ok=True)
    destino = quarentena / (novo_nome or pdf_path.name)
    # Evitar sobrescrita
    if destino.exists():
        stem = destino.stem
        suf = destino.suffix
        destino = quarentena / f"{stem}_{int(time.time())}{suf}"
    pdf_path.rename(destino)
    return destino


if __name__ == "__main__":
    # Modo teste: verificar uma pasta inteira
    import argparse
    p = argparse.ArgumentParser(description="Verifica CNJ de cada PDF contra filename")
    p.add_argument("pasta", type=Path)
    args = p.parse_args()
    total = ok = div = sem = 0
    for pdf in sorted(args.pasta.glob("*.pdf")):
        m = CNJ_GENERICO_RE.search(pdf.name)
        if not m:
            continue
        total += 1
        r_ok, cnj_real, comarca, razao = verificar_conteudo(pdf, m.group(1))
        if r_ok:
            ok += 1
            marker = "OK"
        elif razao == "divergente":
            div += 1
            marker = f"DIVERGENTE→{cnj_real}"
        else:
            sem += 1
            marker = razao.upper()
        print(f"{marker:25s}  {pdf.name}")
    print(f"\n--- total={total}  ok={ok}  div={div}  outros={sem} ---")
