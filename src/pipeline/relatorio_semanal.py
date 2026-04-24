#!/usr/bin/env python3
"""
relatorio_semanal.py — Relatório Semanal Stemmia
Compara STATUS atual vs snapshot anterior.
Snapshots salvos em ~/Desktop/ANALISADOR FINAL/snapshots/

Uso:
    python3 relatorio_semanal.py                    # Terminal
    python3 relatorio_semanal.py --formato telegram  # Telegram
    python3 relatorio_semanal.py --formato json      # JSON
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(os.path.expanduser("~/Desktop/ANALISADOR FINAL"))
SCRIPTS_DIR = BASE_DIR / "scripts"
STATUS_JSON = BASE_DIR / "STATUS-PROCESSOS.json"
SNAPSHOTS_DIR = BASE_DIR / "snapshots"
HOJE = datetime.now()


def garantir_snapshot_dir():
    """Cria pasta de snapshots se necessário."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def salvar_snapshot(status_data):
    """Salva snapshot da semana atual."""
    garantir_snapshot_dir()
    nome = f"snapshot-{HOJE.strftime('%Y-%m-%d')}.json"
    path = SNAPSHOTS_DIR / nome
    path.write_text(json.dumps(status_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def carregar_snapshot_anterior():
    """Carrega snapshot da semana anterior (mais recente antes de hoje)."""
    garantir_snapshot_dir()

    snapshots = sorted(SNAPSHOTS_DIR.glob("snapshot-*.json"), reverse=True)
    for s in snapshots:
        # Pular o de hoje
        if HOJE.strftime('%Y-%m-%d') in s.name:
            continue
        try:
            return json.loads(s.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
    return None


def carregar_status_atual():
    """Carrega STATUS-PROCESSOS.json atualizado."""
    try:
        subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "scanner_processos.py"), "--json-only"],
            capture_output=True, timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError):
        pass

    if STATUS_JSON.exists():
        return json.loads(STATUS_JSON.read_text(encoding="utf-8"))
    return None


def comparar(atual, anterior):
    """Compara snapshots e gera diferenças."""
    stats_atual = atual.get("estatisticas", {})
    stats_anterior = anterior.get("estatisticas", {}) if anterior else {}

    # Processos novos
    cnjs_atual = {p.get("cnj") for p in atual.get("processos", []) if p.get("cnj")}
    cnjs_anterior = {p.get("cnj") for p in anterior.get("processos", []) if p.get("cnj")} if anterior else set()
    novos = cnjs_atual - cnjs_anterior

    # Calcular deltas
    deltas = {}
    todos_estados = set(list(stats_atual.keys()) + list(stats_anterior.keys()))
    for estado in todos_estados:
        v_atual = stats_atual.get(estado, 0)
        v_anterior = stats_anterior.get(estado, 0)
        delta = v_atual - v_anterior
        deltas[estado] = {"atual": v_atual, "anterior": v_anterior, "delta": delta}

    # Valor total de honorários propostos (se disponível)
    valor_total = 0
    for p in atual.get("processos", []):
        ficha = p.get("ficha", {})
        valor = ficha.get("honorarios_valor", 0)
        if isinstance(valor, (int, float)):
            valor_total += valor

    return {
        "novos_processos": len(novos),
        "cnjs_novos": list(novos)[:10],
        "deltas": deltas,
        "total_atual": atual.get("total_pastas", 0),
        "total_anterior": anterior.get("total_pastas", 0) if anterior else 0,
        "valor_honorarios": valor_total,
    }


def formato_terminal(dados, comparacao):
    """Formata para terminal."""
    print("=" * 60)
    print(f"RELATÓRIO SEMANAL — {HOJE.strftime('%d/%m/%Y')}")
    print("=" * 60)

    print(f"\nTotal: {comparacao['total_atual']} processos (antes: {comparacao['total_anterior']})")
    print(f"Novos esta semana: {comparacao['novos_processos']}")

    if comparacao['valor_honorarios'] > 0:
        print(f"Honorários propostos: R$ {comparacao['valor_honorarios']:,.2f}")

    print("\nESTADO              | ATUAL | DELTA")
    print("-" * 45)
    for estado, info in sorted(comparacao["deltas"].items()):
        delta_str = f"+{info['delta']}" if info["delta"] > 0 else str(info["delta"]) if info["delta"] < 0 else "="
        print(f"  {estado:<20} | {info['atual']:>5} | {delta_str}")

    if comparacao["cnjs_novos"]:
        print(f"\nNOVOS:")
        for cnj in comparacao["cnjs_novos"]:
            print(f"  {cnj}")

    print()


def formato_telegram(dados, comparacao):
    """Formata para Telegram."""
    linhas = [f"*SEMANA {HOJE.strftime('%d/%m/%Y')}*\n"]

    linhas.append(f"Total: {comparacao['total_atual']} processos")
    linhas.append(f"Novos: {comparacao['novos_processos']}")

    if comparacao['valor_honorarios'] > 0:
        linhas.append(f"Honorários: R$ {comparacao['valor_honorarios']:,.2f}")

    # Resumo por estado (só com mudanças)
    mudancas = []
    for estado, info in comparacao["deltas"].items():
        if info["delta"] != 0:
            sinal = "+" if info["delta"] > 0 else ""
            mudancas.append(f"{estado}: {sinal}{info['delta']}")

    if mudancas:
        linhas.append(f"\n*Mudanças:* {', '.join(mudancas)}")

    # Estado atual resumido
    stats = dados.get("estatisticas", {})
    aceites = stats.get("PENDENTE-ACEITE", 0)
    propostas = stats.get("PENDENTE-PROPOSTA", 0)
    contestacoes = stats.get("EM-CONTESTAÇÃO", 0)

    linhas.append(f"\n*Pendentes:* {aceites} aceites, {propostas} propostas, {contestacoes} contestações")

    print("\n".join(linhas))


if __name__ == "__main__":
    atual = carregar_status_atual()
    if not atual:
        print("Erro: não foi possível carregar STATUS-PROCESSOS.json")
        sys.exit(1)

    anterior = carregar_snapshot_anterior()
    comparacao = comparar(atual, anterior)

    # Salvar snapshot atual
    salvar_snapshot(atual)

    formato = "terminal"
    if "--formato" in sys.argv:
        idx = sys.argv.index("--formato")
        if idx + 1 < len(sys.argv):
            formato = sys.argv[idx + 1]

    if formato == "telegram":
        formato_telegram(atual, comparacao)
    elif formato == "json":
        print(json.dumps({
            "data": HOJE.isoformat(),
            "comparacao": comparacao,
            "estatisticas": atual.get("estatisticas", {}),
        }, ensure_ascii=False, indent=2))
    else:
        formato_terminal(atual, comparacao)
