#!/usr/bin/env python3
"""
briefing_diario.py — Briefing Diário Stemmia
Combina: scanner + deadline_monitor + INBOX + sites + planner.
Gera resumo compacto para Telegram ou terminal.

Uso:
    python3 briefing_diario.py                    # Terminal
    python3 briefing_diario.py --formato telegram  # Telegram
    python3 briefing_diario.py --formato json      # JSON
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(os.path.expanduser("~/Desktop/ANALISADOR FINAL"))
PROCESSOS_DIR = BASE_DIR / "processos"
SCRIPTS_DIR = BASE_DIR / "scripts"
INBOX_DIR = BASE_DIR / "INBOX"
STATUS_JSON = BASE_DIR / "STATUS-PROCESSOS.json"
HOJE = datetime.now()

SITES = [
    "draanapires.com.br",
    "drachayennemanuelle.com.br",
    "draelizamara.com.br",
    "dratatiane.com.br",
    "lomeuesirio.com.br",
    "perfumarianina.com.br",
    "aessencialfarma.com.br",
]


def rodar_scanner():
    """Roda scanner e retorna estatísticas."""
    try:
        subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "scanner_processos.py"), "--json-only"],
            capture_output=True, text=True, timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError):
        pass

    if STATUS_JSON.exists():
        try:
            return json.loads(STATUS_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return None


def pegar_prazos():
    """Roda deadline_monitor e captura saída."""
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "deadline_monitor.py"), "--json"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        pass
    return {"total_alertas": 0, "alertas": []}


def verificar_inbox():
    """Verifica arquivos na INBOX."""
    if not INBOX_DIR.exists():
        return []
    return [f.name for f in INBOX_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]


def verificar_sites():
    """Verifica status dos 7 sites (timeout curto)."""
    fora = []
    for site in SITES:
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 "--connect-timeout", "5", f"https://{site}"],
                capture_output=True, text=True, timeout=10,
            )
            code = result.stdout.strip()
            if code != "200":
                fora.append(f"{site} ({code})")
        except (subprocess.TimeoutExpired, OSError):
            fora.append(f"{site} (timeout)")
    return fora


def pegar_agenda():
    """Tenta rodar planner_query."""
    planner = SCRIPTS_DIR / "planner_query.py"
    if not planner.exists():
        return None
    try:
        result = subprocess.run(
            [sys.executable, str(planner), "hoje"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        pass
    return None


def montar_briefing():
    """Monta dados do briefing."""
    dados = {
        "data": HOJE.strftime("%d/%m/%Y %H:%M"),
        "periodo": "manhã" if HOJE.hour < 14 else "noite",
    }

    # Scanner
    status = rodar_scanner()
    if status:
        dados["total_processos"] = status.get("total_pastas", 0)
        dados["estatisticas"] = status.get("estatisticas", {})
    else:
        dados["total_processos"] = 0
        dados["estatisticas"] = {}

    # Prazos
    prazos = pegar_prazos()
    dados["total_alertas_prazo"] = prazos.get("total_alertas", 0)
    dados["alertas_prazo"] = prazos.get("alertas", [])[:5]

    # INBOX
    dados["inbox"] = verificar_inbox()

    # Sites
    dados["sites_fora"] = verificar_sites()

    # Agenda
    dados["agenda"] = pegar_agenda()

    return dados


def formato_terminal(dados):
    """Formata para terminal."""
    print("=" * 60)
    print(f"BRIEFING {'MANHÃ' if dados['periodo'] == 'manhã' else 'NOITE'} — {dados['data']}")
    print("=" * 60)

    # Processos
    print(f"\nPROCESSOS ({dados['total_processos']} total):")
    stats = dados["estatisticas"]
    for estado, qtd in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        if qtd > 0:
            print(f"  {estado}: {qtd}")

    # Prazos
    if dados["total_alertas_prazo"] > 0:
        print(f"\nPRAZOS URGENTES ({dados['total_alertas_prazo']}):")
        for a in dados["alertas_prazo"]:
            dias_txt = f"{abs(a['dias'])}d atrás" if a["dias"] < 0 else f"em {a['dias']}d" if a["dias"] > 0 else "HOJE"
            print(f"  [{a['nivel']}] {a['cnj'][:25]} — {dias_txt}")
    else:
        print("\nPRAZOS: Nenhum urgente.")

    # INBOX
    if dados["inbox"]:
        print(f"\nINBOX ({len(dados['inbox'])} arquivos):")
        for f in dados["inbox"][:5]:
            print(f"  {f}")
    else:
        print("\nINBOX: vazia")

    # Sites
    if dados["sites_fora"]:
        print(f"\nSITES FORA ({len(dados['sites_fora'])}):")
        for s in dados["sites_fora"]:
            print(f"  {s}")
    else:
        print("\nSITES: todos online")

    # Ações sugeridas
    print("\nAÇÕES SUGERIDAS:")
    stats = dados["estatisticas"]
    aceites = stats.get("PENDENTE-ACEITE", 0)
    propostas = stats.get("PENDENTE-PROPOSTA", 0)
    contestacoes = stats.get("EM-CONTESTAÇÃO", 0)

    if aceites > 0:
        print(f'  "despacha aceites" → {aceites} PDFs')
    if propostas > 0:
        print(f'  "despacha propostas" → {propostas} propostas')
    if contestacoes > 0:
        print(f'  "despacha contestacoes" → {contestacoes} respostas')
    if dados["inbox"]:
        print(f'  INBOX tem {len(dados["inbox"])} arquivo(s) para processar')

    print()


def formato_telegram(dados):
    """Formata para Telegram (texto simples)."""
    linhas = []
    periodo = "MANHÃ" if dados["periodo"] == "manhã" else "NOITE"
    linhas.append(f"*BRIEFING {periodo}* — {dados['data']}\n")

    # Processos
    stats = dados["estatisticas"]
    aceites = stats.get("PENDENTE-ACEITE", 0)
    propostas = stats.get("PENDENTE-PROPOSTA", 0)
    contestacoes = stats.get("EM-CONTESTAÇÃO", 0)
    agendamento = stats.get("PENDENTE-AGENDAMENTO", 0)

    linhas.append(f"*PROCESSOS:* {aceites} aceites, {propostas} propostas, {contestacoes} contestações, {agendamento} agendamentos")

    # Prazos
    if dados["total_alertas_prazo"] > 0:
        linhas.append(f"\n*PRAZOS ({dados['total_alertas_prazo']}):*")
        for a in dados["alertas_prazo"][:3]:
            emoji = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "🔵"}.get(a["nivel"], "")
            dias_txt = f"{abs(a['dias'])}d atrás" if a["dias"] < 0 else f"em {a['dias']}d" if a["dias"] > 0 else "HOJE"
            linhas.append(f"{emoji} {a['cnj'][:20]} ({dias_txt})")

    # INBOX
    if dados["inbox"]:
        linhas.append(f"\n*INBOX:* {len(dados['inbox'])} arquivo(s)")
    else:
        linhas.append("\n*INBOX:* vazia")

    # Sites fora
    if dados["sites_fora"]:
        linhas.append(f"\n⚠️ *SITES FORA:* {', '.join(dados['sites_fora'])}")

    # Ações
    acoes = []
    if aceites > 0:
        acoes.append(f'"despacha aceites" ({aceites})')
    if propostas > 0:
        acoes.append(f'"despacha propostas" ({propostas})')
    if contestacoes > 0:
        acoes.append(f'"despacha contestacoes" ({contestacoes})')

    if acoes:
        linhas.append(f"\n*AÇÃO:* {' | '.join(acoes)}")

    print("\n".join(linhas))


def formato_json(dados):
    """Saída JSON."""
    print(json.dumps(dados, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    dados = montar_briefing()

    formato = "terminal"
    if "--formato" in sys.argv:
        idx = sys.argv.index("--formato")
        if idx + 1 < len(sys.argv):
            formato = sys.argv[idx + 1]

    if formato == "telegram":
        formato_telegram(dados)
    elif formato == "json":
        formato_json(dados)
    else:
        formato_terminal(dados)
