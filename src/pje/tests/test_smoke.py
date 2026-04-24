"""
Smoke tests: os 4 pontos criticos do pipeline PJe importam e respondem
a chamadas basicas sem side-effects.

Cada teste roda em < 1s (sem I/O de rede, sem browser).
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_import_config_pje():
    """config_pje: PERITO_CPF e a constante canonical do CPF do perito."""
    import config_pje

    assert config_pje.PERITO_CPF == "12785885660"


def test_import_filtro_perito():
    """filtro_perito.classificar: CNJ fake sem sinais -> PAPEL_INDETERMINADO."""
    import filtro_perito

    cnj_fake = "0000000-00.0000.0.00.0000"
    resultado = filtro_perito.classificar(
        cnj_fake,
        datajud_hit=None,
        blacklist_tjmg=None,
    )
    assert resultado["papel"] == filtro_perito.PAPEL_INDETERMINADO
    assert resultado["papel"] == "INDETERMINADO"


def test_import_consulta_publica_tjmg():
    """consulta_publica_tjmg._extrair_cnjs: entrada vazia -> set vazio."""
    import consulta_publica_tjmg

    assert consulta_publica_tjmg._extrair_cnjs("") == set()


def test_fluxos_parsing():
    """AST-parse dos 3 fluxos principais + mapear_paginas_push (sintaxe valida)."""
    fluxos = [
        ROOT / "descoberta" / "descobrir_processos.py",
        ROOT / "download" / "baixar_push_pje.py",
        ROOT / "cadastro" / "incluir_push.py",
        ROOT / "cadastro" / "mapear_paginas_push.py",
    ]
    for caminho in fluxos:
        assert caminho.exists(), f"arquivo nao existe: {caminho}"
        source = caminho.read_text(encoding="utf-8")
        ast.parse(source, filename=str(caminho))
