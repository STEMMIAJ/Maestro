#!/usr/bin/env python3
# DATAJUD_GUIA: ~/Desktop/STEMMIA Dexter/DOCS/datajud/DATAJUD-GUIA.md — ler antes de alterar chamadas DataJud
"""
Cliente unificado para a API DataJud (CNJ).

Centraliza TODAS as chamadas HTTP ao DataJud, eliminando duplicacao
entre monitor.py, monitorar_movimentacao.py, datajud_api.py,
descobrir_processos.py e tribunal_api.py.

Uso:
    from src.pje.datajud_client import consultar_processo, consultar_lote, buscar_movimentacoes
"""

import json
import logging
import random
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    _HAS_REQUESTS = False

# ============================================================
# CONFIGURACAO
# ============================================================

import os
try:
    from src.config import DATAJUD_API_KEY
except ImportError:
    DATAJUD_API_KEY = os.getenv("DATAJUD_API_KEY", "")

if not DATAJUD_API_KEY:
    raise RuntimeError(
        "DATAJUD_API_KEY não setada. Execute: "
        'export DATAJUD_API_KEY="<chave>" '
        "(chave pública documentada em "
        "https://datajud-wiki.cnj.jus.br/api-publica/acesso)"
    )

BASE_URL = "https://api-publica.datajud.cnj.jus.br"

# Mapa segmento CNJ -> alias do tribunal
# CNJ: NNNNNNN-DD.AAAA.J.TT.OOOO
# J = Justiça (1=STF, 2=CNJ, 3=STJ, 4=JFederal, 5=JMilitarUniao, 6=JEleitoral, 7=JTrabalho, 8=JEstadual, 9=JMilitarEstadual)
# TT = Tribunal (para JEstadual: 01-27 UFs; para JFederal: TRFs 01-06)
TRIBUNAL_MAP = {
    # Justiça Federal (TRFs)
    "4.01": "api_publica_trf1",
    "4.02": "api_publica_trf2",
    "4.03": "api_publica_trf3",
    "4.04": "api_publica_trf4",
    "4.05": "api_publica_trf5",
    "4.06": "api_publica_trf6",
    # Justiça do Trabalho (TRTs 01-24)
    "5.01": "api_publica_trt1",  "5.02": "api_publica_trt2",  "5.03": "api_publica_trt3",
    "5.04": "api_publica_trt4",  "5.05": "api_publica_trt5",  "5.06": "api_publica_trt6",
    "5.07": "api_publica_trt7",  "5.08": "api_publica_trt8",  "5.09": "api_publica_trt9",
    "5.10": "api_publica_trt10", "5.11": "api_publica_trt11", "5.12": "api_publica_trt12",
    "5.13": "api_publica_trt13", "5.14": "api_publica_trt14", "5.15": "api_publica_trt15",
    "5.16": "api_publica_trt16", "5.17": "api_publica_trt17", "5.18": "api_publica_trt18",
    "5.19": "api_publica_trt19", "5.20": "api_publica_trt20", "5.21": "api_publica_trt21",
    "5.22": "api_publica_trt22", "5.23": "api_publica_trt23", "5.24": "api_publica_trt24",
    # Justiça Estadual (TJs 01-27 + DF)
    "8.01": "api_publica_tjac", "8.02": "api_publica_tjal", "8.03": "api_publica_tjap",
    "8.04": "api_publica_tjam", "8.05": "api_publica_tjba", "8.06": "api_publica_tjce",
    "8.07": "api_publica_tjdft","8.08": "api_publica_tjes", "8.09": "api_publica_tjgo",
    "8.10": "api_publica_tjma", "8.11": "api_publica_tjmt", "8.12": "api_publica_tjms",
    "8.13": "api_publica_tjmg", "8.14": "api_publica_tjpa", "8.15": "api_publica_tjpb",
    "8.16": "api_publica_tjpr", "8.17": "api_publica_tjpe", "8.18": "api_publica_tjpi",
    "8.19": "api_publica_tjrj", "8.20": "api_publica_tjrn", "8.21": "api_publica_tjrs",
    "8.22": "api_publica_tjro", "8.23": "api_publica_tjrr", "8.24": "api_publica_tjsc",
    "8.25": "api_publica_tjse", "8.26": "api_publica_tjsp", "8.27": "api_publica_tjto",
}

# Alias curto -> alias completo (para compatibilidade)
TRIBUNAL_ALIAS = {v.replace("api_publica_", ""): v for v in TRIBUNAL_MAP.values()}
TRIBUNAL_ALIAS.update({
    "stf": "api_publica_stf",
    "stj": "api_publica_stj",
    "tst": "api_publica_tst",
    "tse": "api_publica_tse",
    "stm": "api_publica_stm",
})

RE_CNJ = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")

logger = logging.getLogger("datajud_client")

DEFAULT_TIMEOUT = 15
MAX_RETRIES = 3


# ============================================================
# FUNCOES INTERNAS
# ============================================================

def _cnj_sem_formatacao(cnj: str) -> str:
    """Remove formatacao: 5001615-98.2025.8.13.0074 -> 50016159820258130074"""
    return re.sub(r"[^0-9]", "", cnj)


def _detectar_tribunal(cnj: str) -> Optional[str]:
    """Detecta alias completo do tribunal pelo CNJ."""
    limpo = _cnj_sem_formatacao(cnj)
    if len(limpo) >= 16:
        justica = limpo[13]
        ramo = limpo[14:16]
        chave = f"{justica}.{ramo}"
        return TRIBUNAL_MAP.get(chave)
    return None


def _resolver_tribunal(cnj: str = "", tribunal: str = "") -> str:
    """Resolve o alias completo do tribunal. Fallback: TJMG."""
    if tribunal:
        tribunal_lower = tribunal.lower().replace("-", "")
        # Tentar alias curto
        alias = TRIBUNAL_ALIAS.get(tribunal_lower)
        if alias:
            return alias
        # Tentar como alias completo
        if tribunal_lower.startswith("api_publica_"):
            return tribunal_lower
        # Construir alias
        return f"api_publica_{tribunal_lower}"

    if cnj:
        alias = _detectar_tribunal(cnj)
        if alias:
            return alias

    return "api_publica_tjmg"


def _post_request(url: str, body: dict, timeout: int = DEFAULT_TIMEOUT) -> Optional[dict]:
    """Executa POST ao DataJud. Suporta requests e urllib como fallback."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"APIKey {DATAJUD_API_KEY}",
    }

    if _HAS_REQUESTS:
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout ao consultar {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Erro HTTP {e.response.status_code}: {url}")
            return None
        except Exception as e:
            logger.warning(f"Erro requisicao: {e}")
            return None
    else:
        # Fallback urllib
        try:
            data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(
                url, data=data, headers=headers, method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            logger.warning(f"Erro urllib: {e}")
            return None
        except Exception as e:
            logger.warning(f"Erro requisicao: {e}")
            return None


def _extrair_hits(data: Optional[dict]) -> list:
    """Extrai hits de uma resposta do Elasticsearch."""
    if not data:
        return []
    return data.get("hits", {}).get("hits", [])


# ============================================================
# API PUBLICA
# ============================================================

def consultar_processo(cnj: str, tribunal: str = "",
                       timeout: int = DEFAULT_TIMEOUT,
                       retries: int = MAX_RETRIES) -> Optional[dict]:
    """
    Consulta um processo pelo CNJ na API DataJud.

    Args:
        cnj: Numero CNJ formatado ou nao.
        tribunal: Alias curto do tribunal (ex: 'tjmg', 'trf6').
                  Se vazio, detecta automaticamente pelo CNJ.
        timeout: Timeout em segundos.
        retries: Numero de tentativas em caso de falha de rede.

    Returns:
        dict com _source do Elasticsearch ou None se nao encontrado.
    """
    alias = _resolver_tribunal(cnj=cnj, tribunal=tribunal)
    url = f"{BASE_URL}/{alias}/_search"
    numero = _cnj_sem_formatacao(cnj)

    body = {
        "query": {"match": {"numeroProcesso": numero}},
        "size": 1,
    }

    for tentativa in range(retries):
        data = _post_request(url, body, timeout=timeout)
        if data is not None:
            hits = _extrair_hits(data)
            return hits[0].get("_source", {}) if hits else None
        if tentativa < retries - 1:
            time.sleep((2 ** tentativa) + random.uniform(0, 1))

    return None


def consultar_lote(cnjs: List[str], tribunal: str = "",
                   delay: float = 0.3, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Optional[dict]]:
    """
    Consulta varios CNJs no DataJud.

    Args:
        cnjs: Lista de CNJs.
        tribunal: Tribunal fixo (se vazio, detecta por CNJ).
        delay: Delay entre requisicoes em segundos.
        timeout: Timeout por requisicao.

    Returns:
        Dict mapeando CNJ -> dados do processo (ou None se nao encontrado).
    """
    resultados = {}

    for i, cnj in enumerate(cnjs):
        resultados[cnj] = consultar_processo(cnj, tribunal=tribunal, timeout=timeout)

        if delay > 0 and i < len(cnjs) - 1:
            time.sleep(delay)

    return resultados


def buscar_movimentacoes(cnj: str, dias: int = 30,
                         tribunal: str = "", timeout: int = DEFAULT_TIMEOUT) -> list:
    """
    Busca movimentacoes recentes de um processo.

    Args:
        cnj: Numero CNJ.
        dias: Filtrar movimentacoes dos ultimos N dias (0 = todas).
        tribunal: Alias curto do tribunal.
        timeout: Timeout em segundos.

    Returns:
        Lista de dicts com movimentacoes (ordenadas por data desc).
        Cada dict: {data, data_iso, nome, codigo, complemento}
    """
    dados = consultar_processo(cnj, tribunal=tribunal, timeout=timeout)
    if not dados:
        return []

    movs = dados.get("movimentos", [])
    if not movs:
        return []

    data_limite = None
    if dias > 0:
        data_limite = datetime.now() - timedelta(days=dias)

    recentes = []
    for mov in movs:
        data_str = mov.get("dataHora", "")
        data_mov = None

        try:
            data_mov = datetime.fromisoformat(
                data_str.replace("Z", "+00:00").replace("+00:00", "")
            )
        except (ValueError, AttributeError):
            try:
                data_mov = datetime.strptime(data_str[:19], "%Y-%m-%dT%H:%M:%S")
            except (ValueError, AttributeError):
                continue

        if data_limite and data_mov < data_limite:
            continue

        nome = mov.get("nome", mov.get("descricao", "Sem descricao"))
        complementos = mov.get("complementosTabelados", [])
        compl_texto = "; ".join(
            [c.get("descricao", c.get("nome", "")) for c in complementos if isinstance(c, dict)]
        ) if complementos else ""

        recentes.append({
            "data": data_mov.strftime("%d/%m/%Y %H:%M"),
            "data_iso": data_str,
            "nome": nome,
            "codigo": mov.get("codigo", ""),
            "complemento": compl_texto,
        })

    recentes.sort(key=lambda x: x.get("data_iso", ""), reverse=True)
    return recentes


def detectar_nomeacao(movimentos: list) -> bool:
    """
    Detecta se ha nomeacao de perito nas movimentacoes.

    Verifica:
      - Codigo TPU 60011 (nomeacao de perito)
      - Texto contendo 'nomeação' ou 'perito' no nome/complementos
    """
    for mov in movimentos:
        if mov.get("codigo") == 60011:
            return True
        texto = mov.get("nome", "")
        complementos = mov.get("complementosTabelados", [])
        if isinstance(complementos, list):
            texto += " " + " ".join(
                c.get("nome", "") for c in complementos if isinstance(c, dict)
            )
        texto_lower = texto.lower()
        if "nomeação" in texto_lower or "perito" in texto_lower:
            return True
    return False


def buscar_por_assunto(tribunal: str, assuntos_codigos: List[str] = None,
                       assuntos_nomes: List[str] = None, limite: int = 50,
                       timeout: int = 30) -> list:
    """
    Busca processos por codigos/nomes de assunto no DataJud.

    Usado pelo modulo de jurisprudencia para buscar por tipo de pericia.

    Args:
        tribunal: Alias curto (ex: 'TJMG', 'TRF6', 'TRT3').
        assuntos_codigos: Lista de codigos de assunto CNJ.
        assuntos_nomes: Lista de nomes de assunto.
        limite: Maximo de resultados.
        timeout: Timeout em segundos.

    Returns:
        Lista de dicts _source do Elasticsearch.
    """
    alias = _resolver_tribunal(tribunal=tribunal)
    url = f"{BASE_URL}/{alias}/_search"

    should = []
    if assuntos_codigos:
        for codigo in assuntos_codigos:
            should.append({"match": {"assuntos.codigo": str(codigo)}})
    if assuntos_nomes:
        for nome in assuntos_nomes:
            should.append({"match_phrase": {"assuntos.nome": nome}})

    body = {
        "size": limite,
        "query": {
            "bool": {
                "should": should if should else [{"match_all": {}}],
                "minimum_should_match": 1,
                "filter": [
                    {"range": {"dataAjuizamento": {"gte": "2020-01-01"}}}
                ],
            }
        },
        "sort": [{"dataAjuizamento": {"order": "desc"}}],
    }

    for tentativa in range(MAX_RETRIES):
        data = _post_request(url, body, timeout=timeout)
        if data is not None:
            hits = _extrair_hits(data)
            return [h.get("_source", {}) for h in hits]
        time.sleep((2 ** tentativa) + random.uniform(0, 1))

    return []
