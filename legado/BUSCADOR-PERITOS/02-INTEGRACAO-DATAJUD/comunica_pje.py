#!/usr/bin/env python3
"""
Monitor de comunicações processuais via API pública do Comunica PJe (CNJ).

Estratégia de 3 camadas:
  Layer 1 — CPF broad sweep (1 request): busca por CPF + TJMG, filtra localmente com scoring
  Layer 2 — CNJs recentes (10-30 requests): consulta CNJs com movimentação recente no DataJud
  Layer 3 — Varredura total (140 requests, semanal): consulta todos os CNJs

Scoring local:
  MATCH_CNJ (texto cita CNJ conhecido)     → 3 pontos
  MATCH_NOME (NOLETO ou JESUS EDUARDO)     → 2 pontos
  MATCH_PERITO (perito, nomeação, nomeado)  → 1 ponto
  MATCH_COMARCA (cidade conhecida)          → 1 ponto
  ≥2 pontos = confirmado | 1 = possível | 0 = descartado

API: https://comunicaapi.pje.jus.br/api/v1 (pública, sem autenticação)
Rate limit: ~100 req/min, delay 1s entre requests, checar headers ratelimit-*

Uso:
  python3 comunica_pje.py                    # Layers 1+2 (diário)
  python3 comunica_pje.py --layer 3          # Layer 3 (varredura semanal)
  python3 comunica_pje.py --cnj 5001615-98.2025.8.13.0074
  python3 comunica_pje.py --teste            # 3 CNJs para validar
  python3 comunica_pje.py --json             # Saída JSON
  python3 comunica_pje.py --telegram         # Envia novidades pro Telegram
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("requests não instalado. Rode: pip install requests")
    sys.exit(1)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

API_BASE = "https://comunicaapi.pje.jus.br/api/v1"

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # stemmia-forense/
DATA_DIR = Path(os.getenv("STEMMIA_DATA_DIR", str(BASE_DIR / "data")))
ESTADO_PATH = DATA_DIR / "_estado_comunica.json"
LISTA_PATH = Path(os.getenv(
    "STEMMIA_LISTA_PUSH",
    str(BASE_DIR / "data" / "LISTA-COMPLETA-PUSH.json"),
))
ESTADO_DATAJUD = DATA_DIR / "_estado_monitor.json"
SAIDA_DIR = Path(__file__).resolve().parent / "resultados"

PERITO_CPF = os.getenv("STEMMIA_PERITO_CPF", "").strip()
PERITO_NOMES = [n.strip().upper() for n in os.getenv("STEMMIA_PERITO_NOMES", "").split(",") if n.strip()]
PERITO_TERMOS = ["perito", "nomeação", "nomeado", "perícia", "perita"]
if not PERITO_CPF or not PERITO_NOMES:
    print("[AVISO] STEMMIA_PERITO_CPF e STEMMIA_PERITO_NOMES devem ser configurados.", file=sys.stderr)

RE_CNJ = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")
RE_CNJ_DIGITOS = re.compile(r"\d{20}")

DELAY_ENTRE_REQUESTS = 1.0  # segundos
RATE_LIMIT_MARGEM = 5       # parar quando remaining < 5


# ============================================================
# LOG
# ============================================================

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "·", "OK": "✓", "ERRO": "✗", "AVISO": "⚠", "NOVO": "★"}.get(level, "·")
    print(f"[{ts}] {prefix} {msg}", file=sys.stderr)


# ============================================================
# ESTADO PERSISTENTE
# ============================================================

def carregar_estado() -> dict:
    if ESTADO_PATH.exists():
        try:
            return json.loads(ESTADO_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "ids_vistos": [],
        "ultima_layer1": None,
        "ultima_layer2": None,
        "ultima_layer3": None,
        "total_confirmados": 0,
        "total_possiveis": 0,
    }


def salvar_estado(estado: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ESTADO_PATH.write_text(
        json.dumps(estado, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ============================================================
# CARREGAR DADOS DE REFERÊNCIA
# ============================================================

def carregar_cnjs_lista() -> list:
    """Carrega processos da LISTA-COMPLETA-PUSH.json."""
    if not LISTA_PATH.exists():
        log(f"Lista não encontrada: {LISTA_PATH}", "ERRO")
        return []
    try:
        data = json.loads(LISTA_PATH.read_text(encoding="utf-8"))
        return data.get("processos", [])
    except (json.JSONDecodeError, OSError) as e:
        log(f"Erro ao ler lista: {e}", "ERRO")
        return []


def carregar_estado_datajud() -> dict:
    """Carrega estado do monitor DataJud para identificar CNJs com movimentação recente."""
    if not ESTADO_DATAJUD.exists():
        return {}
    try:
        return json.loads(ESTADO_DATAJUD.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def cnjs_com_movimentacao_recente(dias: int = 30) -> list:
    """Retorna CNJs que tiveram movimentação nos últimos N dias no DataJud."""
    estado = carregar_estado_datajud()
    limite = datetime.now() - timedelta(days=dias)
    recentes = []
    for cnj, info in estado.items():
        if not isinstance(info, dict):
            continue
        ult_mov = info.get("ultima_movimentacao", "")
        if not ult_mov:
            continue
        try:
            dt = datetime.fromisoformat(ult_mov.replace("Z", "+00:00")).replace(tzinfo=None)
            if dt >= limite:
                recentes.append(cnj)
        except (ValueError, TypeError):
            continue
    return recentes


# ============================================================
# API — REQUEST COM RATE LIMIT
# ============================================================

def api_get(endpoint: str, params: dict, timeout: int = 15, _tentativa: int = 0) -> tuple:
    """
    GET na API pública. Retorna (dados_json, headers_rate_limit).
    Retorna (None, {}) em caso de erro. Máximo 3 tentativas em 429.
    """
    url = f"{API_BASE}/{endpoint}" if not endpoint.startswith("http") else endpoint
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        rate = {
            "limit": int(resp.headers.get("ratelimit-limit", 100)),
            "remaining": int(resp.headers.get("ratelimit-remaining", 99)),
            "reset": int(resp.headers.get("ratelimit-reset", 60)),
        }
        if resp.status_code == 429:
            if _tentativa >= 2:
                log(f"Rate limit persistente após {_tentativa+1} tentativas — abortando", "ERRO")
                return None, rate
            espera = min(rate["reset"], 120)
            log(f"Rate limit 429 (tentativa {_tentativa+1}/3). Esperando {espera}s...", "AVISO")
            time.sleep(espera)
            return api_get(endpoint, params, timeout, _tentativa=_tentativa + 1)
        resp.raise_for_status()
        return resp.json(), rate
    except requests.exceptions.Timeout:
        log(f"Timeout: {url}", "ERRO")
        return None, {}
    except requests.exceptions.HTTPError as e:
        log(f"HTTP {e.response.status_code}: {url}", "ERRO")
        return None, {}
    except Exception as e:
        log(f"Erro request: {e}", "ERRO")
        return None, {}


def respeitar_rate_limit(rate: dict):
    """Aplica delay e espera extra se rate limit estiver perto."""
    time.sleep(DELAY_ENTRE_REQUESTS)
    remaining = rate.get("remaining", 99)
    if remaining < RATE_LIMIT_MARGEM:
        reset = rate.get("reset", 60)
        log(f"Rate limit próximo ({remaining} restantes). Esperando {reset}s...", "AVISO")
        time.sleep(reset)


# ============================================================
# SCORING LOCAL
# ============================================================

def calcular_score(item: dict, cnjs_conhecidos: set, cidades_conhecidas: set) -> dict:
    """
    Pontua uma comunicação com base em matches locais.
    Retorna dict com score, matches encontrados e classificação.
    """
    texto = (item.get("texto") or "").upper()
    orgao = (item.get("nomeOrgao") or "").upper()
    num_proc = item.get("numero_processo", "")

    matches = []
    score = 0

    # MATCH_CNJ: número do processo bate com CNJ conhecido
    cnj_limpo = re.sub(r"[^0-9]", "", num_proc)
    for cnj_ref in cnjs_conhecidos:
        ref_limpo = re.sub(r"[^0-9]", "", cnj_ref)
        if cnj_limpo == ref_limpo:
            matches.append("MATCH_CNJ")
            score += 3
            break

    # MATCH_NOME: texto contém nome do perito
    for nome in PERITO_NOMES:
        if nome.upper() in texto:
            matches.append("MATCH_NOME")
            score += 2
            break

    # MATCH_PERITO: texto contém termos de perícia
    for termo in PERITO_TERMOS:
        if termo.upper() in texto:
            matches.append("MATCH_PERITO")
            score += 1
            break

    # MATCH_COMARCA: órgão contém cidade conhecida
    for cidade in cidades_conhecidas:
        if cidade.upper() in orgao:
            matches.append("MATCH_COMARCA")
            score += 1
            break

    if score >= 2:
        classificacao = "confirmado"
    elif score == 1:
        classificacao = "possivel"
    else:
        classificacao = "descartado"

    return {
        "score": score,
        "matches": matches,
        "classificacao": classificacao,
    }


# ============================================================
# LAYER 1 — CPF BROAD SWEEP (1 request)
# ============================================================

def layer1_cpf_sweep(cnjs_conhecidos: set, cidades_conhecidas: set, ids_vistos: set) -> list[dict]:
    """
    Busca comunicações por CPF + TJMG.
    Filtra localmente com scoring. Retorna apenas confirmados e possíveis.
    """
    log("LAYER 1 — CPF broad sweep", "INFO")

    params = {
        "cpf": PERITO_CPF,
        "siglaTribunal": "TJMG",
        "size": 100,
    }

    data, rate = api_get("comunicacao", params)
    if not data:
        log("Layer 1 falhou", "ERRO")
        return []

    items = data.get("items", [])
    total_api = data.get("count", 0)
    log(f"  API retornou {total_api} itens ({len(items)} nesta página)")

    resultados = []
    novos = 0
    for item in items:
        item_id = item.get("id")
        if item_id in ids_vistos:
            continue

        scoring = calcular_score(item, cnjs_conhecidos, cidades_conhecidas)
        if scoring["classificacao"] == "descartado":
            continue

        novos += 1
        resultados.append({
            "id": item_id,
            "cnj_raw": item.get("numero_processo", ""),
            "data": item.get("data_disponibilizacao", ""),
            "tipo": item.get("tipoComunicacao", ""),
            "orgao": item.get("nomeOrgao", ""),
            "texto_preview": (item.get("texto") or "")[:300],
            "meio": item.get("meio", ""),
            "score": scoring["score"],
            "matches": scoring["matches"],
            "classificacao": scoring["classificacao"],
            "layer": 1,
        })

    confirmados = sum(1 for r in resultados if r["classificacao"] == "confirmado")
    possiveis = sum(1 for r in resultados if r["classificacao"] == "possivel")
    log(f"  Layer 1: {novos} novos → {confirmados} confirmados, {possiveis} possíveis", "OK")

    return resultados


# ============================================================
# LAYER 2 — CNJs COM MOVIMENTAÇÃO RECENTE
# ============================================================

def layer2_cnjs_recentes(cnjs_recentes: list[str], ids_vistos: set,
                         cnjs_conhecidos: set, cidades_conhecidas: set) -> list[dict]:
    """
    Consulta CNJs que tiveram movimentação recente no DataJud.
    """
    if not cnjs_recentes:
        log("LAYER 2 — Nenhum CNJ com movimentação recente", "INFO")
        return []

    log(f"LAYER 2 — {len(cnjs_recentes)} CNJs com movimentação recente")

    resultados = []
    for i, cnj in enumerate(cnjs_recentes):
        cnj_limpo = re.sub(r"[^0-9]", "", cnj)
        params = {"numeroProcesso": cnj_limpo, "size": 10}

        data, rate = api_get("comunicacao", params)
        if data:
            items = data.get("items", [])
            for item in items:
                item_id = item.get("id")
                if item_id in ids_vistos:
                    continue

                scoring = calcular_score(item, cnjs_conhecidos, cidades_conhecidas)
                # Em layer 2 já estamos buscando por CNJ conhecido, score mínimo garantido
                resultados.append({
                    "id": item_id,
                    "cnj_raw": item.get("numero_processo", ""),
                    "cnj_buscado": cnj,
                    "data": item.get("data_disponibilizacao", ""),
                    "tipo": item.get("tipoComunicacao", ""),
                    "orgao": item.get("nomeOrgao", ""),
                    "texto_preview": (item.get("texto") or "")[:300],
                    "meio": item.get("meio", ""),
                    "score": scoring["score"],
                    "matches": scoring["matches"],
                    "classificacao": scoring["classificacao"],
                    "layer": 2,
                })

            if items:
                log(f"  [{i+1}/{len(cnjs_recentes)}] {cnj}: {len(items)} comunicação(ões)", "OK")

        respeitar_rate_limit(rate)

    log(f"  Layer 2: {len(resultados)} comunicações encontradas", "OK")
    return resultados


# ============================================================
# LAYER 3 — VARREDURA TOTAL (SEMANAL)
# ============================================================

def layer3_varredura_total(processos: list[dict], ids_vistos: set,
                           cnjs_conhecidos: set, cidades_conhecidas: set) -> list[dict]:
    """
    Consulta TODOS os CNJs da lista. Usar apenas semanalmente.
    """
    total = len(processos)
    log(f"LAYER 3 — Varredura total: {total} CNJs")

    resultados = []
    com_comunicacao = 0

    for i, proc in enumerate(processos):
        cnj = proc.get("cnj", "")
        if not cnj:
            continue

        cnj_limpo = re.sub(r"[^0-9]", "", cnj)
        params = {"numeroProcesso": cnj_limpo, "size": 10}

        data, rate = api_get("comunicacao", params)
        if data:
            items = data.get("items", [])
            if items:
                com_comunicacao += 1

            for item in items:
                item_id = item.get("id")
                if item_id in ids_vistos:
                    continue

                scoring = calcular_score(item, cnjs_conhecidos, cidades_conhecidas)
                resultados.append({
                    "id": item_id,
                    "cnj_raw": item.get("numero_processo", ""),
                    "cnj_buscado": cnj,
                    "data": item.get("data_disponibilizacao", ""),
                    "tipo": item.get("tipoComunicacao", ""),
                    "orgao": item.get("nomeOrgao", ""),
                    "texto_preview": (item.get("texto") or "")[:300],
                    "meio": item.get("meio", ""),
                    "score": scoring["score"],
                    "matches": scoring["matches"],
                    "classificacao": scoring["classificacao"],
                    "layer": 3,
                })

        # Progresso a cada 20
        if (i + 1) % 20 == 0:
            pct = (i + 1) / total * 100
            log(f"  [{i+1}/{total}] {pct:.0f}% — {com_comunicacao} com comunicação")

        respeitar_rate_limit(rate)

    log(f"  Layer 3: {len(resultados)} comunicações de {com_comunicacao}/{total} processos", "OK")
    return resultados


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def executar(layers: Optional[list] = None, cnjs_especificos: Optional[list] = None,
             modo_json: bool = False, salvar: bool = False,
             enviar_telegram: bool = False) -> dict:
    """
    Executa as layers solicitadas e retorna resultado consolidado.

    Args:
        layers: [1,2] para diário, [3] para semanal. Default: [1,2]
        cnjs_especificos: se fornecido, busca apenas esses CNJs (ignora layers)
        modo_json: saída JSON no stdout
        salvar: salvar resultado em arquivo
        enviar_telegram: enviar novidades confirmadas pro Telegram
    """
    if layers is None:
        layers = [1, 2]

    inicio = time.time()
    estado = carregar_estado()
    ids_vistos = set(estado.get("ids_vistos", []))

    # Carregar referências
    processos = carregar_cnjs_lista()
    cnjs_conhecidos = {p["cnj"] for p in processos if p.get("cnj")}
    cidades_conhecidas = {p["cidade"] for p in processos if p.get("cidade")}

    log(f"Referências: {len(cnjs_conhecidos)} CNJs, {len(cidades_conhecidas)} cidades")
    log(f"IDs já vistos: {len(ids_vistos)}")

    todos_resultados = []

    # CNJs específicos (--cnj)
    if cnjs_especificos:
        log(f"Busca direta: {len(cnjs_especificos)} CNJ(s)")
        for cnj in cnjs_especificos:
            cnj_limpo = re.sub(r"[^0-9]", "", cnj)
            data, rate = api_get("comunicacao", {"numeroProcesso": cnj_limpo, "size": 50})
            if data:
                for item in data.get("items", []):
                    scoring = calcular_score(item, cnjs_conhecidos, cidades_conhecidas)
                    todos_resultados.append({
                        "id": item.get("id"),
                        "cnj_raw": item.get("numero_processo", ""),
                        "cnj_buscado": cnj,
                        "data": item.get("data_disponibilizacao", ""),
                        "tipo": item.get("tipoComunicacao", ""),
                        "orgao": item.get("nomeOrgao", ""),
                        "texto_preview": (item.get("texto") or "")[:300],
                        "meio": item.get("meio", ""),
                        "score": scoring["score"],
                        "matches": scoring["matches"],
                        "classificacao": scoring["classificacao"],
                        "layer": 0,
                    })
                log(f"  {cnj}: {data.get('count', 0)} comunicação(ões)", "OK")
            respeitar_rate_limit(rate)
    else:
        # Layer 1
        if 1 in layers:
            r1 = layer1_cpf_sweep(cnjs_conhecidos, cidades_conhecidas, ids_vistos)
            todos_resultados.extend(r1)
            estado["ultima_layer1"] = datetime.now().isoformat()

        # Layer 2
        if 2 in layers:
            recentes = cnjs_com_movimentacao_recente(dias=30)
            r2 = layer2_cnjs_recentes(recentes, ids_vistos, cnjs_conhecidos, cidades_conhecidas)
            todos_resultados.extend(r2)
            estado["ultima_layer2"] = datetime.now().isoformat()

        # Layer 3
        if 3 in layers:
            r3 = layer3_varredura_total(processos, ids_vistos, cnjs_conhecidos, cidades_conhecidas)
            todos_resultados.extend(r3)
            estado["ultima_layer3"] = datetime.now().isoformat()

    # Deduplicar por ID
    vistos_agora = {}
    for r in todos_resultados:
        rid = r.get("id")
        if rid and rid not in vistos_agora:
            vistos_agora[rid] = r

    resultados_unicos = list(vistos_agora.values())

    # Atualizar estado
    novos_ids = [r["id"] for r in resultados_unicos if r["id"] not in ids_vistos]
    estado["ids_vistos"] = list(ids_vistos | set(novos_ids))
    # Limitar a últimos 5000 IDs para não crescer infinito
    if len(estado["ids_vistos"]) > 5000:
        estado["ids_vistos"] = estado["ids_vistos"][-5000:]

    confirmados = [r for r in resultados_unicos if r["classificacao"] == "confirmado"]
    possiveis = [r for r in resultados_unicos if r["classificacao"] == "possivel"]
    estado["total_confirmados"] = len(confirmados)
    estado["total_possiveis"] = len(possiveis)

    duracao = time.time() - inicio

    resumo = {
        "data_execucao": datetime.now().isoformat(),
        "layers_executadas": layers,
        "duracao_segundos": round(duracao, 1),
        "total_comunicacoes": len(resultados_unicos),
        "novos": len(novos_ids),
        "confirmados": len(confirmados),
        "possiveis": len(possiveis),
        "comunicacoes": sorted(resultados_unicos, key=lambda x: x.get("data", ""), reverse=True),
    }

    # Salvar estado
    salvar_estado(estado)

    # Output
    if not modo_json:
        log(f"Concluído em {duracao:.1f}s", "OK")
        log(f"  Total: {len(resultados_unicos)} | Novos: {len(novos_ids)}")
        log(f"  Confirmados: {len(confirmados)} | Possíveis: {len(possiveis)}")
        if confirmados:
            log("Comunicações confirmadas:", "NOVO")
            for c in confirmados[:10]:
                log(f"  {c['data']} | {c['tipo']} | {c.get('cnj_buscado', c['cnj_raw'])} | {', '.join(c['matches'])}")
    else:
        print(json.dumps(resumo, ensure_ascii=False, indent=2))

    if salvar:
        SAIDA_DIR.mkdir(parents=True, exist_ok=True)
        data_str = datetime.now().strftime("%Y-%m-%d_%H%M")
        saida = SAIDA_DIR / f"comunica-pje-{data_str}.json"
        saida.write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"Salvo em {saida}", "OK")

    if enviar_telegram and novos_ids and confirmados:
        _enviar_telegram(confirmados)

    return resumo


# ============================================================
# TELEGRAM
# ============================================================

def _enviar_telegram(comunicacoes: list):
    """Envia resumo de comunicações confirmadas para o Telegram."""
    try:
        from pathlib import Path
        token_file = Path.home() / "stemmia-forense" / ".telegram-token"
        if not token_file.exists():
            log("Token Telegram não encontrado", "AVISO")
            return

        bot_token = token_file.read_text().strip()
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        if not chat_id:
            log("TELEGRAM_CHAT_ID não configurado no ambiente", "AVISO")
            return

        linhas = ["📋 *Comunica PJe — Novidades*\n"]
        for c in comunicacoes[:10]:
            cnj = c.get("cnj_buscado", c.get("cnj_raw", "?"))
            linhas.append(
                f"• *{c['tipo']}* — {c['data']}\n"
                f"  CNJ: `{cnj}`\n"
                f"  {c['orgao']}\n"
                f"  Score: {c['score']} ({', '.join(c['matches'])})"
            )

        if len(comunicacoes) > 10:
            linhas.append(f"\n... e mais {len(comunicacoes) - 10} comunicações")

        texto = "\n".join(linhas)
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"},
            timeout=10,
        )
        log("Telegram enviado", "OK")
    except Exception as e:
        log(f"Erro Telegram: {e}", "AVISO")


# ============================================================
# ALIASES PARA COMPATIBILIDADE COM ORQUESTRADOR
# ============================================================

def carregar_cnjs_ativos() -> list:
    """Alias esperado pelo orquestrador monitor_publicacoes.py."""
    processos = carregar_cnjs_lista()
    return [p["cnj"] for p in processos if p.get("cnj")]


def monitorar(cnjs: list, dias: int = 7, modo_json: bool = False, salvar: bool = False) -> dict:
    """Wrapper compatível com a assinatura chamada por monitor_publicacoes.py."""
    if cnjs:
        return executar(cnjs_especificos=cnjs, modo_json=modo_json, salvar=salvar)
    return executar(layers=[1, 2], modo_json=modo_json, salvar=salvar)


# ============================================================
# INTERFACE PARA HUB.PY
# ============================================================

def executar_para_hub() -> dict:
    """
    Interface simplificada para o hub de automações.
    Executa layers 1+2, retorna dict compatível com hub.
    """
    resultado = executar(layers=[1, 2], modo_json=False, salvar=False)
    return {
        "status": "ok" if resultado["total_comunicacoes"] >= 0 else "erro",
        "resultados": resultado["total_comunicacoes"],
        "novos": resultado["novos"],
        "confirmados": resultado["confirmados"],
        "possiveis": resultado["possiveis"],
        "ultima_execucao": resultado["data_execucao"],
        "erro": None,
    }


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Monitor de comunicações processuais — API pública Comunica PJe",
    )
    parser.add_argument("--cnj", nargs="+", help="CNJ(s) específico(s) para buscar")
    parser.add_argument("--layer", type=int, choices=[1, 2, 3], help="Executar layer específica")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    parser.add_argument("--salvar", action="store_true", help="Salvar resultado em arquivo")
    parser.add_argument("--telegram", action="store_true", help="Enviar novidades pro Telegram")
    parser.add_argument("--teste", action="store_true", help="Teste com 3 CNJs reais")

    args = parser.parse_args()

    if args.teste:
        log("=== MODO TESTE — 3 CNJs ===", "INFO")
        cnjs_teste = [
            "5001615-98.2025.8.13.0074",   # Bom Despacho
            "5034347-39.2025.8.13.0105",    # Gov Valadares
            "5039279-07.2024.8.13.0105",    # Gov Valadares
        ]
        executar(cnjs_especificos=cnjs_teste, modo_json=args.json, salvar=args.salvar)
        return

    if args.cnj:
        executar(cnjs_especificos=args.cnj, modo_json=args.json,
                 salvar=args.salvar, enviar_telegram=args.telegram)
    else:
        layers = [args.layer] if args.layer else [1, 2]
        executar(layers=layers, modo_json=args.json,
                 salvar=args.salvar, enviar_telegram=args.telegram)


if __name__ == "__main__":
    main()
