#!/usr/bin/env python3
"""Módulo 1: Classifica casos como custeados pelas PARTES ou GRATUIDADE."""

import json
import logging
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROCESSOS_DIR, INDICADORES_PARTES, INDICADORES_GRATUIDADE
from db import upsert_caso_local

logger = logging.getLogger("jurisprudencia")


def classificar_custeio(ficha: dict) -> str:
    """Classifica o tipo de custeio com base nos dados da FICHA.json."""
    area = (ficha.get("area", "") or "").lower()
    objeto = (ficha.get("objeto", "") or "").lower()
    tipo = (ficha.get("tipo_pericia", "") or "").lower()
    texto = f"{area} {objeto} {tipo}"

    # Securitária → sempre PARTES
    if "securitária" in area or "securitaria" in area:
        return "PARTES"
    if any(seg in texto for seg in ["seguro", "allianz", "cardif", "prudential",
                                     "tokio marine", "mapfre", "liberty", "zurich"]):
        return "PARTES"

    # Previdenciária → sempre GRATUIDADE
    if "previdenciária" in area or "previdenciaria" in area:
        return "GRATUIDADE"

    # Curatela/Interdição → GRATUIDADE
    if "curatela" in area or "interdição" in area or "interdicao" in area:
        return "GRATUIDADE"

    # Saúde/SUS → GRATUIDADE
    if "sus" in area or "saúde" in area or "saude" in area:
        return "GRATUIDADE"

    # Erro médico contra hospital privado → PARTES
    if "erro médico" in area or "erro medico" in area:
        if "hospital" in objeto and "municipal" not in objeto and "público" not in objeto:
            return "PARTES"
        return "INDEFINIDO"

    # Responsabilidade civil contra Município/Estado → GRATUIDADE
    if "responsabilidade civil" in area:
        if any(w in texto for w in ["município", "municipio", "estado", "fazenda", "cemig"]):
            return "GRATUIDADE"
        return "PARTES"

    # Cível genérico → verificar indicadores
    score_partes = sum(1 for i in INDICADORES_PARTES if i in texto)
    score_grat = sum(1 for i in INDICADORES_GRATUIDADE if i in texto)

    if score_partes > score_grat:
        return "PARTES"
    elif score_grat > score_partes:
        return "GRATUIDADE"

    return "INDEFINIDO"


def executar_classificador(conn) -> dict:
    """Lê todas as FICHA.json e importa para o banco com classificação."""
    stats = {"total": 0, "partes": 0, "gratuidade": 0, "indefinido": 0}

    # Buscar todas as FICHA.json
    fichas = list(PROCESSOS_DIR.rglob("FICHA.json"))
    logger.info(f"  Encontradas {len(fichas)} FICHA.json")

    for ficha_path in fichas:
        try:
            with open(ficha_path, "r", encoding="utf-8") as f:
                ficha = json.load(f)

            cnj = ficha.get("numero_cnj", "")
            if not cnj:
                continue

            tipo_custeio = classificar_custeio(ficha)
            ficha["tipo_custeio"] = tipo_custeio
            ficha["pasta"] = str(ficha_path.parent)

            upsert_caso_local(conn, ficha)
            stats["total"] += 1

            if tipo_custeio == "PARTES":
                stats["partes"] += 1
            elif tipo_custeio == "GRATUIDADE":
                stats["gratuidade"] += 1
            else:
                stats["indefinido"] += 1

            logger.debug(f"  {cnj}: {tipo_custeio} ({ficha.get('area', '')})")

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"  Erro ao ler {ficha_path.name}: {e}")
            continue

    logger.info(f"  Classificados: {stats['partes']} PARTES, "
                f"{stats['gratuidade']} GRATUIDADE, {stats['indefinido']} INDEFINIDO")
    return stats
