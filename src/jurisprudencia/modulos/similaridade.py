#!/usr/bin/env python3
"""Módulo 3: Busca casos similares e calcula score de matching."""

import re
import logging

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import obter_casos, obter_jurisprudencia, inserir_similaridade
from utils.tribunal_api import buscar_datajud
from utils.tribunal_api import gerar_hash
from utils.parser_valores import extrair_valor, inferir_tipo_pericia
from config import DATAJUD_ASSUNTOS_PERICIA

logger = logging.getLogger("jurisprudencia")


def normalizar_area(area: str) -> str:
    """Normaliza área para comparação."""
    area = (area or "").lower()
    mapa = {
        "previdenciária": "previdenciaria",
        "securitária": "securitaria",
        "cível": "civel",
        "erro médico": "erro_medico",
        "interdição": "curatela",
        "curatela": "curatela",
        "responsabilidade civil": "resp_civil",
        "saúde": "saude",
    }
    for chave, valor in mapa.items():
        if chave in area:
            return valor
    return "outra"


def extrair_cids(texto: str) -> set:
    """Extrai códigos CID do texto."""
    if not texto:
        return set()
    padrao = r'[A-Z]\d{2}(?:\.\d{1,2})?'
    return set(re.findall(padrao, texto.upper()))


def calcular_similaridade(caso: dict, juris: dict) -> tuple:
    """Calcula score de similaridade entre caso local e jurisprudência."""
    score = 0
    motivos = []

    area_caso = normalizar_area(caso.get("area", ""))
    tipo_juris = (juris.get("tipo_pericia_inferido", "") or "").lower()
    ementa = (juris.get("ementa", "") or "").lower()

    # 1. Match de tipo de perícia (30 pts)
    if area_caso and tipo_juris:
        if area_caso == tipo_juris:
            score += 30
            motivos.append(f"Mesmo tipo: {area_caso}")
        elif area_caso in tipo_juris or tipo_juris in area_caso:
            score += 15
            motivos.append(f"Tipo parcial: {area_caso}/{tipo_juris}")

    # 2. Match de área (20 pts)
    area_palavras = {
        "securitaria": ["seguro", "securitária", "apólice", "sinistro"],
        "previdenciaria": ["previdenciário", "aposentadoria", "auxílio", "inss"],
        "curatela": ["interdição", "curatela", "capacidade civil"],
        "erro_medico": ["erro médico", "negligência", "imperícia"],
        "resp_civil": ["responsabilidade civil", "acidente", "indenização"],
    }
    for area_key, palavras in area_palavras.items():
        if area_caso == area_key:
            matches = sum(1 for p in palavras if p in ementa)
            if matches >= 2:
                score += 20
                motivos.append(f"Área confirmada: {area_key}")
            elif matches == 1:
                score += 10
                motivos.append(f"Área parcial: {area_key}")
            break

    # 3. Match de CIDs/condições médicas (15 pts)
    cids_caso = extrair_cids(caso.get("objeto", ""))
    cids_juris = extrair_cids(juris.get("ementa", ""))
    if cids_caso and cids_juris:
        intersecao = cids_caso & cids_juris
        if intersecao:
            score += 15
            motivos.append(f"CIDs comuns: {', '.join(intersecao)}")

    # 4. Mesmo tribunal (15 pts)
    tribunal_caso = (caso.get("tribunal", "") or "").upper()
    tribunal_juris = (juris.get("tribunal", "") or "").upper()
    if tribunal_caso and tribunal_juris and tribunal_caso == tribunal_juris:
        score += 15
        motivos.append(f"Mesmo tribunal: {tribunal_caso}")

    # 5. Menção a honorários (10 pts)
    if "honorários" in ementa or "honorarios" in ementa:
        score += 10
        motivos.append("Menciona honorários")

    # 6. Tem valor monetário (10 pts)
    if juris.get("valor_encontrado") and juris["valor_encontrado"] > 0:
        score += 10
        motivos.append(f"Valor: R$ {juris['valor_encontrado']:,.2f}")

    return score, " | ".join(motivos)


def executar_similaridade(conn) -> dict:
    """Executa análise de similaridade para todos os casos."""
    stats = {"casos": 0, "matches": 0, "datajud_resultados": 0}

    casos = obter_casos(conn)
    jurisprudencia = obter_jurisprudencia(conn)

    logger.info(f"  {len(casos)} casos × {len(jurisprudencia)} decisões")

    # 1. Matching local: cada caso contra toda jurisprudência coletada
    for caso in casos:
        stats["casos"] += 1
        caso_id = caso["id"]
        matches_caso = 0

        for juris in jurisprudencia:
            score, motivo = calcular_similaridade(caso, juris)
            if score >= 30:  # threshold mínimo
                inserir_similaridade(conn, caso_id, juris["id"], score, motivo)
                matches_caso += 1
                stats["matches"] += 1

        if matches_caso > 0:
            logger.debug(f"  {caso['numero_cnj']}: {matches_caso} matches")

    # 2. Busca complementar no DataJud (para casos custeados pelas partes)
    casos_partes = [c for c in casos if c.get("tipo_custeio") == "PARTES"]
    if casos_partes:
        logger.info(f"  DataJud: buscando similares para {len(casos_partes)} casos PARTES")
        for caso in casos_partes:
            try:
                resultados = buscar_datajud(
                    tribunal="TJMG",
                    assuntos_nomes=["honorários periciais", "perícia médica"],
                    limite=20,
                )
                stats["datajud_resultados"] += len(resultados)
            except Exception as e:
                logger.warning(f"  DataJud erro: {e}")

    logger.info(f"  Resultado: {stats['casos']} casos analisados, "
                f"{stats['matches']} matches, {stats['datajud_resultados']} DataJud")
    return stats
