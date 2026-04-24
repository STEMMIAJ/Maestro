#!/usr/bin/env python3
"""Orquestrador MONITOR-FONTES.

Roda todas as fontes em sequencia e salva resultado bruto em
dados/por-fonte/<id>.json, depois dispara consolidador + alerta + dashboard.
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path.home() / "Desktop" / "MONITOR-FONTES"
POR_FONTE = RAIZ / "dados" / "por-fonte"
HISTORICO = RAIZ / "dados" / "historico"
LOGS = RAIZ / "logs"

# Scripts existentes no stemmia-forense
STEMMIA = Path.home() / "stemmia-forense"
AJ_PY = STEMMIA / "src" / "pje" / "consultar_aj.py"
AJG_PY = STEMMIA / "src" / "pje" / "consultar_ajg.py"
HUB_PY = STEMMIA / "automacoes" / "hub.py"
DOMICILIO_PY = STEMMIA / "src" / "pje" / "monitor-publicacoes" / "dje_tjmg.py"

FONTES = [
    {
        "id": "aj",
        "nome": "AJ TJMG",
        "cmd": ["python3", str(AJ_PY), "--listar", "--json", "--porta", "9223"],
        "timeout": 180,
        "opcional": False,
    },
    {
        "id": "ajg",
        "nome": "AJG Justica Federal",
        "cmd": ["python3", str(AJG_PY), "--listar", "--json", "--porta", "9223"],
        "timeout": 180,
        "opcional": False,
    },
    {
        "id": "djen",
        "nome": "DJEN / Comunica PJe",
        "cmd": ["python3", str(HUB_PY), "--discovery-only", "--no-telegram", "--no-ftp"],
        "timeout": 300,
        "opcional": True,
        "fallback_json": HUB_PY.parent / "estado_hub.json",
        "fallback_chave": ("fontes", "comunica_pje"),
    },
    {
        "id": "domicilio",
        "nome": "DJE-TJMG",
        "cmd": ["python3", str(DOMICILIO_PY), "--dias", "1", "--json"],
        "timeout": 120,
        "opcional": True,
    },
    {
        "id": "datajud",
        "nome": "DataJud CNJ",
        "cmd": ["python3", str(HUB_PY), "--status-only", "--no-telegram", "--no-ftp"],
        "timeout": 180,
        "opcional": True,
        "fallback_json": HUB_PY.parent / "estado_hub.json",
        "fallback_chave": ("fontes", "datajud"),
    },
]


def _caminho_saida(fid: str) -> Path:
    return POR_FONTE / f"{fid}.json"


def _log(msg: str) -> None:
    linha = f"[{datetime.now():%H:%M:%S}] {msg}"
    print(linha)
    LOGS.mkdir(parents=True, exist_ok=True)
    log_file = LOGS / f"orquestrador-{datetime.now():%Y-%m-%d}.log"
    with open(log_file, "a") as f:
        f.write(linha + "\n")


def rodar_fonte(fonte: dict) -> dict:
    """Executa comando da fonte, salva saida em dados/por-fonte/<id>.json.

    Retorna dict com {status, itens, erro}.
    """
    _log(f"→ {fonte['nome']}: iniciando")
    # Script ausente
    script_path = Path(fonte["cmd"][1])
    if not script_path.exists():
        msg = f"script ausente: {script_path}"
        _log(f"  ✗ {fonte['nome']}: {msg}")
        return {"status": "erro", "erro": msg, "itens": 0}
    try:
        r = subprocess.run(
            fonte["cmd"],
            capture_output=True,
            text=True,
            timeout=fonte.get("timeout", 300),
            env={**os.environ, "PYTHONPATH": str(STEMMIA)},
        )
    except subprocess.TimeoutExpired:
        _log(f"  ✗ {fonte['nome']}: TIMEOUT")
        return {"status": "timeout", "erro": "timeout", "itens": 0}
    except FileNotFoundError as e:
        _log(f"  ✗ {fonte['nome']}: {e}")
        return {"status": "erro", "erro": str(e), "itens": 0}

    if r.returncode != 0:
        _log(f"  ✗ {fonte['nome']}: exit {r.returncode} — {r.stderr[:200]}")
        return {"status": "erro", "erro": r.stderr[:500], "itens": 0}

    # Tenta JSON
    try:
        dados = json.loads(r.stdout) if r.stdout.strip() else []
    except json.JSONDecodeError:
        # Fallback: se o script nao cuspiu JSON, tenta arquivo auxiliar
        dados = _ler_fallback(fonte)

    # Normaliza para lista
    if isinstance(dados, dict):
        dados = (
            dados.get("items")
            or dados.get("resultados")
            or dados.get("cnjs")
            or dados.get("matches")
            or dados.get("processos")
            or []
        )
    if not isinstance(dados, list):
        dados = []

    saida = _caminho_saida(fonte["id"])
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(dados, ensure_ascii=False, indent=2))
    _log(f"  ✓ {fonte['nome']}: {len(dados)} itens → {saida.name}")
    return {"status": "ok", "itens": len(dados), "arquivo": str(saida)}


def _ler_fallback(fonte: dict) -> list:
    fb = fonte.get("fallback_json")
    if not fb or not fb.exists():
        return []
    try:
        raw = json.loads(fb.read_text())
    except json.JSONDecodeError:
        return []
    chave = fonte.get("fallback_chave")
    if not chave:
        return []
    cur = raw
    for k in chave:
        if not isinstance(cur, dict):
            return []
        cur = cur.get(k, {})
    # cur pode ser dict com dados ou lista
    if isinstance(cur, list):
        return cur
    if isinstance(cur, dict):
        return cur.get("cnjs") or cur.get("items") or []
    return []


def main():
    _log("=" * 60)
    _log("MONITOR-FONTES — orquestrador iniciado")
    resultados = {}
    for f in FONTES:
        resultados[f["id"]] = rodar_fonte(f)

    # Snapshot do dia (status de cada fonte)
    HISTORICO.mkdir(parents=True, exist_ok=True)
    snap = HISTORICO / f"{datetime.now():%Y-%m-%d}.json"
    snap.write_text(json.dumps(resultados, ensure_ascii=False, indent=2))
    _log(f"Snapshot: {snap.name}")

    # Chama consolidador
    consolidador = Path(__file__).parent / "consolidador.py"
    if consolidador.exists():
        _log("→ consolidador")
        subprocess.run(["python3", str(consolidador)])

    # Chama dashboard
    dashboard = Path(__file__).parent / "gerar_dashboard.py"
    if dashboard.exists():
        _log("→ dashboard")
        subprocess.run(["python3", str(dashboard)])

    # Chama alerta
    alerta = Path(__file__).parent / "alerta_telegram.py"
    if alerta.exists():
        _log("→ alerta telegram")
        subprocess.run(["python3", str(alerta)])

    _log("Concluido.")
    return resultados


if __name__ == "__main__":
    main()
