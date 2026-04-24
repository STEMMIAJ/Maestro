#!/usr/bin/env python3
"""
cron_monitor.py — Wrapper para execução automática via crontab.

Roda 2x/dia (07:00 e 18:00):
  1. descobrir_processos.py --salvar --sem-browser (6 fontes incluindo DJEN TJMG+TRF6)
  2. monitorar_movimentacao.py --json (DataJud com rate limiting)
  3. Consolida tudo em data/notificacoes.json
  4. Envia só novidades pro Telegram (dedupe por chave composta)
  5. Grava log em data/logs/

Uso manual:
  python3 cron_monitor.py
  python3 cron_monitor.py --sem-telegram    # Não envia Telegram
  python3 cron_monitor.py --so-djen         # Só consulta DJEN (rápido)
"""

import json
import os
import re
import subprocess
import sys
import time
import uuid
import urllib.request
import urllib.parse
import ssl
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
# PATHS
# ============================================================

DEXTER_DIR = Path(__file__).parent.parent.parent  # STEMMIA Dexter/
SCRIPTS_DIR = Path.home() / "Desktop" / "ANALISADOR FINAL" / "scripts"
NOTIFICACOES_JSON = DEXTER_DIR / "data" / "notificacoes.json"
LOG_DIR = DEXTER_DIR / "data" / "logs"

# DJEN API
DJEN_BASE = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
DJEN_TRIBUNAIS = ["TJMG", "TRF6"]
DJEN_FILTRO = re.compile(r'PERIT|NOMEADO|LAUDO|EXPERT', re.IGNORECASE)
RE_CNJ = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ", "OK": "✓", "ERRO": "✗", "AVISO": "⚠", "NOVO": "★"}.get(level, "·")
    print(f"[{ts}] {prefix} {msg}", file=sys.stderr)


# ============================================================
# CARREGAR / SALVAR NOTIFICAÇÕES
# ============================================================

def carregar_notificacoes():
    """Carrega notificacoes.json existente."""
    if NOTIFICACOES_JSON.exists():
        try:
            return json.loads(NOTIFICACOES_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def salvar_notificacoes(notificacoes):
    """Salva notificacoes.json (nunca remove, só adiciona)."""
    NOTIFICACOES_JSON.parent.mkdir(parents=True, exist_ok=True)
    NOTIFICACOES_JSON.write_text(
        json.dumps(notificacoes, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def chave_notificacao(n):
    """Gera chave única para dedupe: (tribunal, processo, tipo, data)."""
    return (
        n.get("tribunal", ""),
        n.get("processo", ""),
        n.get("tipo", ""),
        n.get("data_movimentacao", ""),
    )


# ============================================================
# BUSCAR DJEN API (PÚBLICO)
# ============================================================

def buscar_djen_tribunal(tribunal, nome="JESUS EDUARDO"):
    """Busca comunicações periciais em um tribunal via DJEN API pública."""
    params = urllib.parse.urlencode({
        "nomeParte": nome,
        "siglaTribunal": tribunal,
        "itensPorPagina": 100,
    })
    url = f"{DJEN_BASE}?{params}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
            remaining = resp.headers.get("x-ratelimit-remaining")
            if remaining and int(remaining) < 3:
                log(f"DJEN {tribunal}: rate limit baixo ({remaining}), aguardando 5s", "AVISO")
                time.sleep(5)
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            log(f"DJEN {tribunal}: 429 — aguardando 60s", "AVISO")
            time.sleep(60)
            try:
                with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except Exception:
                return []
        else:
            log(f"DJEN {tribunal}: HTTP {e.code}", "ERRO")
            return []
    except Exception as e:
        log(f"DJEN {tribunal}: {e}", "ERRO")
        return []

    items = data.get("items", [])
    resultados = []

    for item in items:
        texto = item.get("texto", "")
        if not DJEN_FILTRO.search(texto):
            continue

        num = item.get("numero_processo", "")
        if len(num) == 20:
            cnj = f"{num[:7]}-{num[7:9]}.{num[9:13]}.{num[13]}.{num[14:16]}.{num[16:]}"
        else:
            cnj = num

        resultados.append({
            "tipo": "publicacao",
            "tribunal": tribunal,
            "processo": cnj,
            "titulo": item.get("tipoComunicacao", "Comunicação"),
            "texto": texto[:300] if texto else "",
            "fonte": "DJEN",
            "data_movimentacao": item.get("data_disponibilizacao", ""),
            "orgao": item.get("nomeOrgao", ""),
        })

    log(f"DJEN {tribunal}: {len(resultados)} periciais de {len(items)} total", "OK")
    return resultados


def buscar_djen_todos():
    """Busca DJEN em TJMG e TRF6 em paralelo."""
    todos = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(buscar_djen_tribunal, t): t for t in DJEN_TRIBUNAIS}
        for f in as_completed(futures):
            try:
                todos.extend(f.result())
            except Exception as e:
                log(f"DJEN erro: {e}", "ERRO")
    return todos


# ============================================================
# RODAR SCRIPTS EXISTENTES
# ============================================================

def rodar_descobrir_processos():
    """Roda descobrir_processos.py --salvar --sem-browser."""
    script = SCRIPTS_DIR / "descobrir_processos.py"
    if not script.exists():
        log(f"Script não encontrado: {script}", "ERRO")
        return []

    log("Rodando descobrir_processos.py...")
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--salvar", "--sem-browser", "--json"],
            capture_output=True, text=True, timeout=600,
            cwd=str(SCRIPTS_DIR)
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            novos = data.get("novos_cnjs", [])
            return [{
                "tipo": "descoberta",
                "tribunal": "TJMG",
                "processo": cnj,
                "titulo": "Processo novo descoberto",
                "texto": "",
                "fonte": "descobrir_processos",
                "data_movimentacao": datetime.now().strftime("%Y-%m-%d"),
            } for cnj in novos]
    except subprocess.TimeoutExpired:
        log("descobrir_processos.py: timeout (5 min)", "ERRO")
    except Exception as e:
        log(f"descobrir_processos.py: {e}", "ERRO")
    return []


def rodar_monitorar_movimentacoes():
    """Roda monitorar_movimentacao.py --json."""
    script = SCRIPTS_DIR / "monitorar_movimentacao.py"
    if not script.exists():
        log(f"Script não encontrado: {script}", "ERRO")
        return []

    log("Rodando monitorar_movimentacao.py...")
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--json"],
            capture_output=True, text=True, timeout=300,
            cwd=str(SCRIPTS_DIR)
        )
        if result.returncode == 0 and result.stdout.strip():
            novidades = json.loads(result.stdout)
            return [{
                "tipo": "movimentacao",
                "tribunal": n.get("tribunal", "TJMG"),
                "processo": n.get("cnj", ""),
                "titulo": n.get("nome_movimentacao", "Movimentação"),
                "texto": f"PDF: {n.get('data_pdf', '?')} → Mov: {n.get('data_movimentacao', '?')}",
                "fonte": "DataJud",
                "data_movimentacao": n.get("data_movimentacao", ""),
            } for n in novidades]
    except subprocess.TimeoutExpired:
        log("monitorar_movimentacao.py: timeout (5 min)", "ERRO")
    except Exception as e:
        log(f"monitorar_movimentacao.py: {e}", "ERRO")
    return []


# ============================================================
# ENVIAR TELEGRAM
# ============================================================

def enviar_telegram(novas):
    """Envia resumo das novidades pro Telegram."""
    if not novas:
        return

    try:
        sys.path.insert(0, str(SCRIPTS_DIR))
        from notificar_telegram import enviar
    except ImportError:
        log("notificar_telegram não encontrado — pulando", "AVISO")
        return

    linhas = [f"🔔 *{len(novas)} novidade(s) detectada(s)*\n"]
    for n in novas[:10]:
        emoji = {"movimentacao": "📋", "descoberta": "🆕", "publicacao": "📰"}.get(n["tipo"], "📌")
        linhas.append(f"{emoji} *{n['titulo']}*")
        linhas.append(f"   {n['processo']} ({n['tribunal']})")
        if n.get("orgao"):
            linhas.append(f"   _{n['orgao']}_")
        linhas.append("")

    if len(novas) > 10:
        linhas.append(f"... e mais {len(novas) - 10}")

    linhas.append(f"\n_{datetime.now().strftime('%d/%m/%Y %H:%M')}_")

    try:
        enviar("\n".join(linhas))
        log(f"Telegram: {len(novas)} notificações enviadas", "OK")
    except Exception as e:
        log(f"Telegram: {e}", "ERRO")


# ============================================================
# MAIN
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Monitor automático de processos (cron)")
    parser.add_argument("--sem-telegram", action="store_true", help="Não enviar Telegram")
    parser.add_argument("--so-djen", action="store_true", help="Só consultar DJEN (rápido)")
    args = parser.parse_args()

    inicio = datetime.now()
    log(f"=== CRON MONITOR — {inicio.strftime('%d/%m/%Y %H:%M')} ===")

    # Carregar notificações existentes
    existentes = carregar_notificacoes()
    chaves_existentes = set(chave_notificacao(n) for n in existentes)
    log(f"Notificações existentes: {len(existentes)}")

    # Coletar de todas as fontes
    todas_novas = []

    if args.so_djen:
        # Modo rápido: só DJEN
        todas_novas.extend(buscar_djen_todos())
    else:
        # Modo completo: 3 fontes em paralelo
        with ThreadPoolExecutor(max_workers=3) as pool:
            f_djen = pool.submit(buscar_djen_todos)
            f_descobrir = pool.submit(rodar_descobrir_processos)
            f_monitorar = pool.submit(rodar_monitorar_movimentacoes)

            for future, nome in [(f_djen, "DJEN"), (f_descobrir, "Descobrir"), (f_monitorar, "Monitorar")]:
                try:
                    todas_novas.extend(future.result())
                except Exception as e:
                    log(f"{nome}: {e}", "ERRO")

    # Dedupe: só adicionar o que é realmente novo
    novas_de_verdade = []
    for n in todas_novas:
        chave = chave_notificacao(n)
        if chave not in chaves_existentes:
            n["id"] = str(uuid.uuid4())
            n["timestamp_detectado"] = datetime.now().isoformat()
            n["notificado_telegram"] = not args.sem_telegram
            novas_de_verdade.append(n)
            chaves_existentes.add(chave)

    log(f"Novas notificações: {len(novas_de_verdade)} (de {len(todas_novas)} candidatas)")

    # Telegram
    if novas_de_verdade and not args.sem_telegram:
        enviar_telegram(novas_de_verdade)

    # Salvar (append, nunca remove)
    existentes.extend(novas_de_verdade)
    salvar_notificacoes(existentes)
    log(f"Total salvo: {len(existentes)} notificações")

    # Log
    duracao = (datetime.now() - inicio).total_seconds()
    log(f"=== CONCLUÍDO em {duracao:.0f}s ===")

    # Salvar log
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"cron_{inicio.strftime('%Y%m%d_%H%M')}.log"
    resumo = {
        "timestamp": inicio.isoformat(),
        "duracao_segundos": round(duracao),
        "existentes": len(existentes) - len(novas_de_verdade),
        "novas": len(novas_de_verdade),
        "total": len(existentes),
        "fontes": {
            "djen": sum(1 for n in novas_de_verdade if n["fonte"] == "DJEN"),
            "datajud": sum(1 for n in novas_de_verdade if n["fonte"] == "DataJud"),
            "descobrir": sum(1 for n in novas_de_verdade if n["fonte"] == "descobrir_processos"),
        },
    }
    log_file.write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")

    # Retornar código de saída
    return 0


if __name__ == "__main__":
    sys.exit(main())
