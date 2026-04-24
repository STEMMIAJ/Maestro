#!/usr/bin/env python3
"""
Módulo 2: Coleta jurisprudência de múltiplas fontes sobre honorários periciais.

Fontes:
1. Precedentes locais (Markdown com decisões reais verificadas)
2. DataJud API (CNJ) — processos com assuntos de perícia
3. Google Scholar — jurisprudência brasileira
4. Tribunais diretos (STJ, STF, TJMG) — com fallback
"""

import logging
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import QUERIES_GERAIS, QUERIES_POR_TIPO, DELAY_ENTRE_BUSCAS
from db import inserir_jurisprudencia, obter_casos
from utils.tribunal_api import (
    importar_precedentes_locais,
    buscar_datajud,
    buscar_google_scholar,
    buscar_tribunal,
)
from utils.parser_valores import (
    extrair_valor, identificar_tipo_decisao,
    inferir_tipo_custeio, inferir_tipo_pericia,
)

logger = logging.getLogger("jurisprudencia")


def processar_resultado(item: dict, query: str = "") -> dict:
    """Enriquece resultado com valor, tipo decisão, custeio e tipo perícia."""
    ementa = item.get("ementa", "")

    # Se já tem valor (precedentes locais), não recalcular
    if not item.get("valor_encontrado"):
        item["valor_encontrado"] = extrair_valor(ementa) if ementa else None

    if not item.get("tipo_decisao"):
        item["tipo_decisao"] = identificar_tipo_decisao(ementa) if ementa else "indefinido"

    if not item.get("tipo_custeio_inferido"):
        item["tipo_custeio_inferido"] = inferir_tipo_custeio(ementa) if ementa else "indefinido"

    if not item.get("tipo_pericia_inferido"):
        item["tipo_pericia_inferido"] = inferir_tipo_pericia(ementa) if ementa else "outra"

    if query and not item.get("query_origem"):
        item["query_origem"] = query

    # Score de relevância
    if not item.get("relevancia_score"):
        score = 0
        ementa_lower = ementa.lower() if ementa else ""
        if item.get("valor_encontrado"):
            score += 30
        if "honorários" in ementa_lower or "honorarios" in ementa_lower:
            score += 20
        if "perito" in ementa_lower or "pericial" in ementa_lower:
            score += 15
        if "depósito" in ementa_lower or "deposito" in ementa_lower:
            score += 10
        if "complexidade" in ementa_lower:
            score += 10
        if "razoabilidade" in ementa_lower:
            score += 5
        if "art. 95" in ementa_lower or "art. 465" in ementa_lower:
            score += 10
        item["relevancia_score"] = score

    return item


def _inserir_batch(conn, itens: list, stats: dict):
    """Insere batch de resultados no banco."""
    for item in itens:
        item = processar_resultado(item)
        inserido = inserir_jurisprudencia(conn, item)
        if inserido:
            stats["novos"] += 1
            if item.get("valor_encontrado"):
                stats["com_valor"] += 1
        else:
            stats["duplicados"] += 1


def executar_harvester(conn) -> dict:
    """Executa coleta completa de jurisprudência."""
    stats = {"buscas": 0, "novos": 0, "duplicados": 0, "erros": 0, "com_valor": 0}

    # ==============================
    # FASE 1: Precedentes locais
    # ==============================
    logger.info("  Fase 1: Importando precedentes locais (decisões reais verificadas)")
    try:
        locais = importar_precedentes_locais()
        _inserir_batch(conn, locais, stats)
        stats["buscas"] += 1
    except Exception as e:
        logger.warning(f"  Erro precedentes locais: {e}")
        stats["erros"] += 1

    # ==============================
    # FASE 2: DataJud (CNJ)
    # ==============================
    logger.info("  Fase 2: DataJud — buscando processos com assuntos de perícia/honorários")

    datajud_queries = [
        # Códigos de assunto CNJ
        {"codigos": ["10028"], "nomes": [], "desc": "Honorários periciais"},
        {"codigos": ["9985"], "nomes": [], "desc": "Perícia"},
        {"codigos": ["7771"], "nomes": [], "desc": "Perícia médica"},
        # Busca por nome de assunto
        {"codigos": [], "nomes": ["honorários periciais"], "desc": "Honorários periciais (nome)"},
        {"codigos": [], "nomes": ["perícia médica"], "desc": "Perícia médica (nome)"},
    ]

    for tribunal in ["TJMG", "TRF6", "TRT3"]:
        for dq in datajud_queries:
            stats["buscas"] += 1
            try:
                itens = buscar_datajud(
                    tribunal,
                    assuntos_codigos=dq["codigos"] if dq["codigos"] else None,
                    assuntos_nomes=dq["nomes"] if dq["nomes"] else None,
                    limite=30,
                )
                _inserir_batch(conn, itens, stats)
                logger.debug(f"  DataJud {tribunal}/{dq['desc']}: {len(itens)} resultados")
            except Exception as e:
                stats["erros"] += 1
                logger.warning(f"  Erro DataJud {tribunal}: {e}")

            time.sleep(1)

    # ==============================
    # FASE 3: Google Scholar
    # ==============================
    logger.info(f"  Fase 3: Google Scholar — {len(QUERIES_GERAIS)} queries de honorários periciais")

    for query in QUERIES_GERAIS:
        stats["buscas"] += 1
        try:
            itens = buscar_google_scholar(query, limite=10)
            _inserir_batch(conn, itens, stats)
        except Exception as e:
            stats["erros"] += 1
            logger.warning(f"  Erro Scholar/{query[:30]}: {e}")

        time.sleep(DELAY_ENTRE_BUSCAS)

    # ==============================
    # FASE 4: Queries por tipo de perícia
    # ==============================
    casos = obter_casos(conn)
    tipos_encontrados = set()
    for caso in casos:
        area = (caso.get("area", "") or "").lower()
        if "securitária" in area or "securitaria" in area:
            tipos_encontrados.add("securitaria")
        elif "erro médico" in area or "erro medico" in area:
            tipos_encontrados.add("erro_medico")
        elif "responsabilidade civil" in area:
            tipos_encontrados.add("acidente_transito")
        elif "curatela" in area or "interdição" in area:
            tipos_encontrados.add("curatela")
        elif "previdenciária" in area or "previdenciaria" in area:
            tipos_encontrados.add("previdenciaria")

    if tipos_encontrados:
        logger.info(f"  Fase 4: Queries por tipo ({', '.join(tipos_encontrados)})")
        for tipo in tipos_encontrados:
            queries_tipo = QUERIES_POR_TIPO.get(tipo, [])
            for query in queries_tipo:
                stats["buscas"] += 1
                try:
                    # Buscar via Google Scholar (mais confiável que APIs bloqueadas)
                    itens = buscar_google_scholar(query, limite=10)
                    _inserir_batch(conn, itens, stats)
                except Exception as e:
                    stats["erros"] += 1
                    logger.warning(f"  Erro tipo/{query[:30]}: {e}")

                time.sleep(DELAY_ENTRE_BUSCAS)

    # ==============================
    # FASE 5: Tribunais diretos (com fallback)
    # ==============================
    logger.info("  Fase 5: Buscas diretas nos tribunais (STJ, STF, TJMG)")
    queries_diretas = [
        "honorários periciais perito médico",
        "honorários perito complexidade perícia",
        "impugnação honorários perito valor",
    ]

    for query in queries_diretas:
        for tribunal in ["STJ", "STF", "TJMG"]:
            stats["buscas"] += 1
            try:
                itens = buscar_tribunal(tribunal, query, limite=10)
                _inserir_batch(conn, itens, stats)
            except Exception as e:
                stats["erros"] += 1
                logger.warning(f"  Erro {tribunal}/{query[:30]}: {e}")

            time.sleep(DELAY_ENTRE_BUSCAS)

    logger.info(f"  Resultado: {stats['buscas']} buscas, {stats['novos']} novos, "
                f"{stats['com_valor']} com valor, {stats['duplicados']} duplicados, "
                f"{stats['erros']} erros")
    return stats
