#!/usr/bin/env python3
"""
deadline_monitor.py — Monitor de Prazos Inteligente
Lê URGENCIA.json de cada processo e classifica por faixa de prazo.
Dedup via /tmp/stemmia-deadline-alerts.json (não repete alerta no mesmo dia).

Uso:
    python3 deadline_monitor.py              # Mostra alertas no terminal
    python3 deadline_monitor.py --json       # Saída JSON
    python3 deadline_monitor.py --telegram   # Formato Telegram
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(os.path.expanduser("~/Desktop/ANALISADOR FINAL"))
PROCESSOS_DIR = BASE_DIR / "processos"
DEDUP_FILE = Path("/tmp/stemmia-deadline-alerts.json")
HOJE = datetime.now().date()


def carregar_dedup():
    """Carrega alertas já enviados (evita repetição no mesmo dia)."""
    if DEDUP_FILE.exists():
        try:
            data = json.loads(DEDUP_FILE.read_text(encoding="utf-8"))
            if data.get("data") == str(HOJE):
                return data.get("alertas", {})
        except (json.JSONDecodeError, KeyError):
            pass
    return {}


def salvar_dedup(alertas):
    """Salva alertas enviados hoje."""
    DEDUP_FILE.write_text(json.dumps({
        "data": str(HOJE),
        "alertas": alertas,
    }, ensure_ascii=False, indent=2), encoding="utf-8")


def classificar_prazo(data_str):
    """Classifica prazo por faixa de dias restantes."""
    formatos = ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]
    data_prazo = None
    for fmt in formatos:
        try:
            data_prazo = datetime.strptime(data_str.strip(), fmt).date()
            break
        except (ValueError, AttributeError):
            continue

    if data_prazo is None:
        return None, None

    dias = (data_prazo - HOJE).days

    if dias < 0:
        # Prazos vencidos há mais de 90 dias são provavelmente históricos — silenciar
        if dias < -90:
            return "SILENCIO", dias
        return "CRITICAL", dias
    elif dias <= 1:
        return "WARNING", dias
    elif dias <= 3:
        return "INFO", dias
    else:
        return "SILENCIO", dias


def escanear_prazos():
    """Varre processos buscando URGENCIA.json."""
    alertas = []

    if not PROCESSOS_DIR.exists():
        return alertas

    for pasta in sorted(PROCESSOS_DIR.iterdir()):
        if not pasta.is_dir() or pasta.name.startswith('.'):
            continue

        urgencia_path = pasta / "URGENCIA.json"
        if not urgencia_path.exists():
            continue

        try:
            data = json.loads(urgencia_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        cnj = data.get("cnj", pasta.name)
        classificacao = data.get("classificacao", "")

        # Verificar prazos
        for prazo in data.get("prazos", []):
            # Ignorar prazos já realizados ou completados
            status_prazo = prazo.get("status", "").upper()
            if status_prazo in ("REALIZADO", "CUMPRIDO", "COMPLETO"):
                continue

            data_prazo = prazo.get("data_vencimento", prazo.get("data", prazo.get("vencimento", "")))
            descricao = prazo.get("descricao", prazo.get("tipo", "Prazo"))

            nivel, dias = classificar_prazo(data_prazo)
            if nivel is None or nivel == "SILENCIO":
                continue

            alertas.append({
                "cnj": cnj,
                "pasta": pasta.name,
                "nivel": nivel,
                "dias": dias,
                "data_prazo": data_prazo,
                "descricao": descricao,
                "classificacao": classificacao,
            })

        # Alertas genéricos — ignorar, já cobertos pelos prazos estruturados

    # Dedup: manter apenas o prazo mais urgente por CNJ
    por_cnj = {}
    for a in alertas:
        cnj = a["cnj"]
        if cnj not in por_cnj or a["dias"] < por_cnj[cnj]["dias"]:
            por_cnj[cnj] = a

    alertas = list(por_cnj.values())

    # Ordenar por urgência
    ordem = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
    alertas.sort(key=lambda x: (ordem.get(x["nivel"], 9), x["dias"]))

    return alertas


def filtrar_novos(alertas):
    """Filtra apenas alertas que ainda não foram enviados hoje."""
    dedup = carregar_dedup()
    novos = []

    for a in alertas:
        chave = f"{a['cnj']}|{a['nivel']}|{a['descricao'][:50]}"
        if chave not in dedup:
            novos.append(a)
            dedup[chave] = datetime.now().isoformat()

    salvar_dedup(dedup)
    return novos


def formato_terminal(alertas):
    """Formata para terminal."""
    if not alertas:
        print("Nenhum prazo urgente encontrado.")
        return

    icones = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "🔵"}

    print("=" * 60)
    print("MONITOR DE PRAZOS — STEMMIA FORENSE")
    print(f"Data: {HOJE.strftime('%d/%m/%Y')}")
    print("=" * 60)

    for a in alertas:
        icone = icones.get(a["nivel"], "⚪")
        dias_txt = f"{abs(a['dias'])} dias atrás" if a["dias"] < 0 else f"em {a['dias']} dias" if a["dias"] > 0 else "HOJE"
        print(f"  {icone} [{a['nivel']}] {a['cnj']}")
        print(f"    {a['descricao']} — {dias_txt}")
        if a["data_prazo"]:
            print(f"    Vencimento: {a['data_prazo']}")
    print()


def formato_telegram(alertas):
    """Formata para Telegram."""
    if not alertas:
        print("Nenhum prazo urgente.")
        return

    linhas = ["*PRAZOS*\n"]
    for a in alertas:
        emoji = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "🔵"}.get(a["nivel"], "")
        dias_txt = f"{abs(a['dias'])}d atrás" if a["dias"] < 0 else f"em {a['dias']}d" if a["dias"] > 0 else "HOJE"
        linhas.append(f"{emoji} {a['cnj'][:20]} — {a['descricao'][:40]} ({dias_txt})")

    print("\n".join(linhas))


def formato_json(alertas):
    """Saída JSON."""
    print(json.dumps({
        "data": str(HOJE),
        "total_alertas": len(alertas),
        "alertas": alertas,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    alertas = escanear_prazos()

    if "--novos-only" in sys.argv:
        alertas = filtrar_novos(alertas)

    if "--json" in sys.argv:
        formato_json(alertas)
    elif "--telegram" in sys.argv:
        formato_telegram(alertas)
    else:
        formato_terminal(alertas)
