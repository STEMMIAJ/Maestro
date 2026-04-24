"""
filtro_perito.py — Classificador PERITO / PARTE / INDETERMINADO por CNJ.

Usa 2 sinais:
  1. DataJud estruturado: auxiliaresDaJustica[*].papel == PERITO → PERITO
                          poloAtivo/poloPassivo com CPF         → PARTE
  2. Blacklist Consulta Pública TJMG: se CNJ está lá → PARTE (veto final)

Regras de precedência (mais forte vence):
  - Blacklist TJMG → PARTE (final)
  - DataJud auxiliar=PERITO e CPF não em polo → PERITO
  - DataJud CPF em polo → PARTE
  - Sem sinal → INDETERMINADO (vai pra revisão manual)

Fix 2026-04-19: antes, descobrir_processos.py coletava 160 CNJs sem
classificar. Dr. Jesus perdia tempo descartando manualmente os que era
parte (familiares, pessoais). Agora separa em 3 CSVs.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Set

_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
if str(_CONFIG_DIR) not in sys.path:
    sys.path.insert(0, str(_CONFIG_DIR))

from config_pje import PERITO_CPF, PERITO_NOME


PAPEL_PERITO = "PERITO"
PAPEL_PARTE = "PARTE"
PAPEL_INDETERMINADO = "INDETERMINADO"


def _normalizar(s: str) -> str:
    return (s or "").upper().strip()


def _cpf_so_numeros(s: str) -> str:
    return "".join(c for c in (s or "") if c.isdigit())


def _eh_dr_jesus(pessoa: Dict[str, Any]) -> bool:
    """Checa se uma entrada de pessoa (do DataJud) é o Dr. Jesus."""
    if not pessoa:
        return False
    cpf = _cpf_so_numeros(
        pessoa.get("cpf") or pessoa.get("documento") or ""
    )
    if cpf and cpf == PERITO_CPF:
        return True
    nome = _normalizar(pessoa.get("nome") or "")
    if PERITO_NOME in nome:
        return True
    return False


def _extrair_papeis_datajud(datajud_hit: Dict[str, Any]) -> Dict[str, bool]:
    """
    Varre resposta DataJud (_source) e devolve flags:
      - aux_perito: Dr. Jesus aparece em auxiliaresDaJustica como PERITO
      - em_polo:    Dr. Jesus aparece em poloAtivo/poloPassivo
    """
    src = datajud_hit.get("_source") or datajud_hit  # aceita hit ou source
    aux_perito = False
    em_polo = False

    # auxiliaresDaJustica (lista)
    for aux in src.get("auxiliaresDaJustica") or []:
        if _eh_dr_jesus(aux):
            papel = _normalizar(aux.get("papel") or aux.get("tipo") or "")
            if "PERIT" in papel:
                aux_perito = True

    # polos (estruturas variam por tribunal — tentamos ambos)
    polos = []
    for key in ("poloAtivo", "poloPassivo", "polos"):
        v = src.get(key)
        if isinstance(v, list):
            polos.extend(v)
        elif isinstance(v, dict):
            polos.append(v)

    for polo in polos:
        # polo pode ter "partes" ou ser direto uma pessoa
        partes = polo.get("partes") if isinstance(polo, dict) else None
        candidatos = partes if partes else [polo]
        for p in candidatos:
            if isinstance(p, dict) and _eh_dr_jesus(p):
                em_polo = True
                break
        if em_polo:
            break

    return {"aux_perito": aux_perito, "em_polo": em_polo}


def classificar(
    cnj: str,
    datajud_hit: Dict[str, Any] | None = None,
    blacklist_tjmg: Set[str] | None = None,
) -> Dict[str, Any]:
    """
    Classifica um CNJ como PERITO / PARTE / INDETERMINADO.

    Args:
        cnj: número CNJ no formato NNNNNNN-NN.AAAA.J.TR.OOOO
        datajud_hit: resposta DataJud (dict com _source ou source direto)
        blacklist_tjmg: set de CNJs em que Dr. Jesus é parte (Consulta Pública)

    Returns:
        dict com:
          - papel: str (PERITO/PARTE/INDETERMINADO)
          - razao: str (explicação)
          - sinais: dict (bandeiras que foram levantadas)
    """
    sinais = {
        "blacklist_tjmg": False,
        "datajud_aux_perito": False,
        "datajud_em_polo": False,
        "datajud_disponivel": datajud_hit is not None,
    }

    # Sinal 1 — blacklist (precedência máxima)
    if blacklist_tjmg and cnj in blacklist_tjmg:
        sinais["blacklist_tjmg"] = True
        return {
            "papel": PAPEL_PARTE,
            "razao": "CNJ consta na Consulta Pública TJMG por CPF do perito",
            "sinais": sinais,
        }

    # Sinal 2 — DataJud estruturado
    if datajud_hit:
        papeis = _extrair_papeis_datajud(datajud_hit)
        sinais["datajud_aux_perito"] = papeis["aux_perito"]
        sinais["datajud_em_polo"] = papeis["em_polo"]

        # Em polo vence aux_perito (improvável, mas se ambos, trata como parte)
        if papeis["em_polo"]:
            return {
                "papel": PAPEL_PARTE,
                "razao": "CPF/nome do perito em poloAtivo/poloPassivo no DataJud",
                "sinais": sinais,
            }
        if papeis["aux_perito"]:
            return {
                "papel": PAPEL_PERITO,
                "razao": "auxiliaresDaJustica.papel == PERITO no DataJud",
                "sinais": sinais,
            }

    return {
        "papel": PAPEL_INDETERMINADO,
        "razao": "sem sinais claros (revisão manual)",
        "sinais": sinais,
    }


def classificar_lote(
    cnjs: list,
    datajud_hits_by_cnj: Dict[str, Dict[str, Any]] | None = None,
    blacklist_tjmg: Set[str] | None = None,
) -> Dict[str, Dict[str, Any]]:
    """Aplica classificar() em lote. Retorna {cnj: resultado}."""
    datajud_hits_by_cnj = datajud_hits_by_cnj or {}
    resultados = {}
    for cnj in cnjs:
        resultados[cnj] = classificar(
            cnj,
            datajud_hit=datajud_hits_by_cnj.get(cnj),
            blacklist_tjmg=blacklist_tjmg,
        )
    return resultados


if __name__ == "__main__":
    # Smoke test — sem chamadas de rede
    cnj_teste = "0000000-00.0000.0.00.0000"

    r1 = classificar(cnj_teste, blacklist_tjmg={cnj_teste})
    print(f"Teste blacklist: {r1}")
    assert r1["papel"] == PAPEL_PARTE

    r2 = classificar(cnj_teste, datajud_hit={
        "_source": {
            "auxiliaresDaJustica": [
                {"cpf": PERITO_CPF, "papel": "PERITO"},
            ],
        }
    })
    print(f"Teste PERITO: {r2}")
    assert r2["papel"] == PAPEL_PERITO

    r3 = classificar(cnj_teste, datajud_hit={
        "_source": {
            "poloAtivo": [{"partes": [{"cpf": PERITO_CPF, "nome": "NOLETO"}]}],
        }
    })
    print(f"Teste PARTE (polo): {r3}")
    assert r3["papel"] == PAPEL_PARTE

    r4 = classificar(cnj_teste)
    print(f"Teste INDETERMINADO: {r4}")
    assert r4["papel"] == PAPEL_INDETERMINADO

    print("\nTODOS OS SMOKE TESTS OK")
