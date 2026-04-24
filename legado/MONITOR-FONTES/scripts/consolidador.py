#!/usr/bin/env python3
"""Consolida resultados de todas as fontes em lista unica deduplicada por CNJ.

Entrada: dados/por-fonte/*.json
Saida:   dados/processos-consolidados.json  (ordem cronologica desc)
         dados/processos-consolidados.csv   (mesma lista em CSV)
"""
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

RAIZ = Path.home() / "Desktop" / "MONITOR-FONTES"
POR_FONTE = RAIZ / "dados" / "por-fonte"
SAIDA_JSON = RAIZ / "dados" / "processos-consolidados.json"
SAIDA_CSV = RAIZ / "dados" / "processos-consolidados.csv"

CNJ_RE = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")


def _normalizar_cnj(raw: str) -> Optional[str]:
    """Aceita CNJ formatado ou sem pontuacao; retorna formatado ou None."""
    if not raw:
        return None
    raw = str(raw).strip()
    m = CNJ_RE.search(raw)
    if m:
        return m.group(0)
    # Tenta converter 20 digitos puros para CNJ
    digitos = re.sub(r"\D", "", raw)
    if len(digitos) == 20:
        return f"{digitos[0:7]}-{digitos[7:9]}.{digitos[9:13]}.{digitos[13]}.{digitos[14:16]}.{digitos[16:20]}"
    return None


def _data_iso(raw) -> str:
    """Converte varios formatos de data em YYYY-MM-DD. Retorna '' se nao reconhecer."""
    if not raw:
        return ""
    s = str(raw)[:19]
    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%d/%m/%Y %H:%M",
    ):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # ISO com timezone "2026-04-15T10:00:00-03:00"
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        pass
    return ""


def _extrair_campo(item: dict, candidatos: tuple) -> Optional[str]:
    for k in candidatos:
        v = item.get(k)
        if v:
            return v
    return None


def consolidar() -> list:
    merged = {}
    if not POR_FONTE.exists():
        return []
    for arq in sorted(POR_FONTE.glob("*.json")):
        fonte_id = arq.stem
        try:
            dados = json.loads(arq.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(dados, list):
            continue
        for item in dados:
            if not isinstance(item, dict):
                continue
            cnj_raw = _extrair_campo(
                item,
                ("cnj", "numero_processo", "numeroProcesso", "processo", "CNJ"),
            )
            cnj = _normalizar_cnj(cnj_raw) if cnj_raw else None
            if not cnj:
                continue
            data_raw = _extrair_campo(
                item,
                (
                    "data",
                    "data_intimacao",
                    "dataDisponibilizacao",
                    "data_nomeacao",
                    "dataNomeacao",
                    "data_mais_recente",
                ),
            )
            data = _data_iso(data_raw)

            if cnj not in merged:
                merged[cnj] = {
                    "cnj": cnj,
                    "data_mais_recente": data,
                    "fontes": [],
                    "detalhes": [],
                    "resumo": {},
                }
            entry = merged[cnj]
            if fonte_id not in entry["fontes"]:
                entry["fontes"].append(fonte_id)
            entry["detalhes"].append({"fonte": fonte_id, "data": data, "item": item})
            if data and data > entry["data_mais_recente"]:
                entry["data_mais_recente"] = data
            # Campos de resumo: pegue o primeiro que aparecer nao-vazio
            for campo, chaves in [
                ("classe", ("classe", "class", "classeProcessual")),
                ("orgao", ("orgao", "vara", "comarca", "orgaoJulgador")),
                ("assunto", ("assunto", "descricao", "titulo")),
                ("tribunal", ("tribunal", "siglaTribunal", "sigla_tribunal")),
            ]:
                if not entry["resumo"].get(campo):
                    v = _extrair_campo(item, chaves)
                    if v:
                        entry["resumo"][campo] = str(v)[:200]

    lista = list(merged.values())
    # Ordem cronologica: mais recente primeiro; empates sem data vao pro fim
    lista.sort(
        key=lambda x: (bool(x["data_mais_recente"]), x["data_mais_recente"]),
        reverse=True,
    )

    SAIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_JSON.write_text(json.dumps(lista, ensure_ascii=False, indent=2))

    with open(SAIDA_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "cnj",
                "data_mais_recente",
                "fontes",
                "n_intimacoes",
                "classe",
                "orgao",
                "assunto",
                "tribunal",
            ]
        )
        for p in lista:
            r = p.get("resumo", {})
            w.writerow(
                [
                    p["cnj"],
                    p["data_mais_recente"],
                    "+".join(p["fontes"]),
                    len(p["detalhes"]),
                    r.get("classe", ""),
                    r.get("orgao", ""),
                    r.get("assunto", ""),
                    r.get("tribunal", ""),
                ]
            )
    return lista


if __name__ == "__main__":
    lista = consolidar()
    print(f"{len(lista)} processos unicos consolidados em {SAIDA_JSON.name}")
