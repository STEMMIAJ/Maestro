#!/usr/bin/env python3
"""
Monitor de publicações no Diário do Judiciário Eletrônico TJMG.

Duas estratégias:
  1. Busca no diário HTML antigo (www8.tjmg.jus.br) — sem CAPTCHA
  2. Busca no DJEN (comunica.pje.jus.br) — requer cadastro (ver comunica_pje.py)

Este script implementa a estratégia 1: baixa as edições HTML do dia
e busca por nome do perito, CPF e números de processo.

NÃO gasta tokens Anthropic — é Python puro com requests.

Uso:
  python3 dje_tjmg.py                    # Busca no diário de hoje
  python3 dje_tjmg.py --data 06/03/2026  # Data específica
  python3 dje_tjmg.py --dias 3           # Últimos 3 dias
  python3 dje_tjmg.py --historico 730    # Backfill 2 anos (todas comarcas)
  python3 dje_tjmg.py --json             # Saída JSON
  python3 dje_tjmg.py --salvar           # Salva resultado
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("requests não instalado. Rode: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


# ============================================================
# CONFIGURAÇÃO
# ============================================================

# Diário HTML antigo (sem CAPTCHA)
BASE_URL_DIARIO = "https://www8.tjmg.jus.br/juridico/diario/"
INDEX_URL = f"{BASE_URL_DIARIO}index.jsp"

# Termos de busca do perito — ENV override obrigatório para evitar PII hardcoded
_PERITO_NOMES = [n.strip() for n in os.getenv("STEMMIA_PERITO_NOMES", "").split(",") if n.strip()]
_PERITO_CPF = os.getenv("STEMMIA_PERITO_CPF", "").strip()  # só dígitos
_PERITO_CPF_FMT = os.getenv("STEMMIA_PERITO_CPF_FMT", "").strip()  # formatado
_PERITO_CRM = os.getenv("STEMMIA_PERITO_CRM", "").strip()
_PERITO_CRM_FMT = os.getenv("STEMMIA_PERITO_CRM_FMT", "").strip()
TERMOS_BUSCA = [t for t in (_PERITO_NOMES + [_PERITO_CPF_FMT, _PERITO_CPF, _PERITO_CRM_FMT, _PERITO_CRM]) if t]
if not TERMOS_BUSCA:
    print("[AVISO] Nenhum termo de busca configurado. Exporte STEMMIA_PERITO_NOMES/CPF/CRM.", file=sys.stderr)

# Comarcas com códigos DJe (formato: interior|CODIGO)
COMARCAS_DJE = {
    "Governador Valadares": "interior|0105",
    "Taiobeiras": "interior|0680",
    "Conselheiro Pena": "interior|0184",
    "Inhapim": "interior|0309",
    "Mantena": "interior|0396",
    "Itamogi": "interior|0329",
    "Barroso": "interior|0059",
    "Bom Despacho": "interior|0074",
    "Ribeirão das Neves": "interior|0231",
    "Caratinga": "interior|0134",
    "Ipatinga": "interior|0245",
    "Teófilo Otoni": "interior|0694",
    "Uberlândia": "interior|0702",
    "João Monlevade": "interior|0362",
    "Aimorés": "interior|0005",
    "Araguari": "interior|0042",
    "Barbacena": "interior|0089",
    "Carangola": "interior|0194",
    "Itabirito": "interior|0471",
    "São Lourenço": "interior|0627",
}

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # ~/stemmia-forense/
BASE_DIR = Path(os.getenv("STEMMIA_DATA_DIR", str(REPO_ROOT / "data")))
SAIDA_DIR = Path(__file__).resolve().parent / "resultados"
STATUS_JSON = BASE_DIR / "STATUS-PROCESSOS.json"
BACKFILL_PROGRESSO = SAIDA_DIR / "backfill_progresso.json"

USER_AGENT = os.getenv(
    "STEMMIA_USER_AGENT",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 stemmia-forense/1.0",
)
HTTP_HEADERS = {"User-Agent": USER_AGENT}

RE_CNJ = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')


# ============================================================
# CORES
# ============================================================

class C:
    R = "\033[0m"
    B = "\033[1m"
    G = "\033[32m"
    Y = "\033[33m"
    RE = "\033[31m"
    CY = "\033[36m"


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ", "OK": "✓", "ERRO": "✗", "AVISO": "⚠", "NOVO": "★"}.get(level, "·")
    print(f"  [{ts}] {prefix} {msg}", file=sys.stderr)


# ============================================================
# CARREGAR CNJs ATIVOS
# ============================================================

def carregar_cnjs_ativos():
    """Carrega CNJs de processos ativos para incluir na busca."""
    cnjs = []
    if not STATUS_JSON.exists():
        return cnjs
    try:
        with open(STATUS_JSON, encoding="utf-8") as f:
            data = json.load(f)
        for p in data.get("processos", []):
            cnj = p.get("cnj", "")
            if cnj and RE_CNJ.match(cnj):
                cnjs.append(cnj)
    except (json.JSONDecodeError, OSError):
        pass
    return list(set(cnjs))


# ============================================================
# BUSCA NO DIÁRIO HTML
# ============================================================

def _data_para_param_dje(data_str):
    """Converte dd/mm/yyyy para DDMM (formato do DJe)."""
    partes = data_str.split("/")
    if len(partes) != 3:
        return None
    return partes[0] + partes[1]  # DDMM


def buscar_no_diario_html(data_str, comarcas=None):
    """
    Baixa o diário do dia e busca por termos relevantes.

    O DJe TJMG antigo (www8.tjmg.jus.br) usa parâmetros:
      - dia=DDMM (4 dígitos, dia+mês)
      - completa=interior|CODIGO (código numérico da comarca)

    Args:
        data_str: Data no formato dd/mm/yyyy
        comarcas: Dict de comarcas a buscar (default: COMARCAS_DJE)

    Returns:
        Lista de matches encontrados
    """
    log(f"Buscando no DJe TJMG de {data_str}...")

    if comarcas is None:
        comarcas = COMARCAS_DJE

    dia_param = _data_para_param_dje(data_str)
    if not dia_param:
        log(f"Data inválida: {data_str}", "ERRO")
        return []

    # Montar termos de busca completos
    termos = list(TERMOS_BUSCA)
    cnjs = carregar_cnjs_ativos()
    termos.extend(cnjs)

    # Compilar padrões (case insensitive)
    padroes = [re.compile(re.escape(t), re.IGNORECASE) for t in termos]

    matches = []

    for comarca_nome, comarca_codigo in comarcas.items():
        try:
            params = {
                "dia": dia_param,
                "completa": comarca_codigo,
            }
            resp = requests.get(INDEX_URL, params=params, timeout=20, verify=True, headers=HTTP_HEADERS)

            if resp.status_code != 200:
                continue

            html = resp.text
            if not html or len(html) < 100:
                continue

            # Detectar "publicação não disponível"
            if "nao esta disponivel" in html.lower() or "não está disponível" in html.lower():
                continue

            # Limpar HTML para texto puro
            if HAS_BS4:
                soup = BeautifulSoup(html, "html.parser")
                for tag in soup(["script", "style"]):
                    tag.decompose()
                texto = soup.get_text(separator="\n")
            else:
                texto = re.sub(r'<[^>]+>', ' ', html)
                texto = re.sub(r'\s+', ' ', texto)

            # Buscar cada termo
            for i, padrao in enumerate(padroes):
                for match in padrao.finditer(texto):
                    inicio = max(0, match.start() - 200)
                    fim = min(len(texto), match.end() + 200)
                    contexto = texto[inicio:fim].strip()
                    contexto = re.sub(r'\s+', ' ', contexto)

                    # Extrair CNJs do contexto
                    cnjs_encontrados = RE_CNJ.findall(contexto)

                    matches.append({
                        "data": data_str,
                        "comarca": comarca_nome,
                        "termo": termos[i],
                        "contexto": contexto,
                        "posicao": match.start(),
                        "cnjs_no_contexto": cnjs_encontrados,
                    })

            if any(p.search(texto) for p in padroes):
                log(f"  {C.G}ENCONTRADO em {comarca_nome}!{C.R}", "NOVO")

        except requests.exceptions.Timeout:
            log(f"  Timeout em {comarca_nome}", "AVISO")
        except Exception as e:
            log(f"  Erro em {comarca_nome}: {e}", "AVISO")

    return matches


# ============================================================
# BACKFILL HISTÓRICO
# ============================================================

def carregar_progresso_backfill():
    """Carrega progresso do backfill para retomada."""
    if BACKFILL_PROGRESSO.exists():
        try:
            return json.loads(BACKFILL_PROGRESSO.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"processados": {}, "matches": [], "cnjs_descobertos": []}


def salvar_progresso_backfill(progresso):
    """Salva progresso do backfill."""
    BACKFILL_PROGRESSO.parent.mkdir(parents=True, exist_ok=True)
    BACKFILL_PROGRESSO.write_text(
        json.dumps(progresso, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def backfill_dje(dias=730, delay=0.5):
    """
    Escaneia DJe histórico buscando publicações do perito.

    Percorre cada dia útil (pula domingos) nos últimos N dias,
    para cada comarca do COMARCAS_DJE. Salva progresso incremental
    para permitir retomada se interrompido.

    Args:
        dias: Quantos dias pra trás escanear
        delay: Segundos entre requests (rate limit)

    Returns:
        Dict com resultados consolidados
    """
    progresso = carregar_progresso_backfill()
    processados = progresso.get("processados", {})
    todos_matches = progresso.get("matches", [])
    cnjs_descobertos = set(progresso.get("cnjs_descobertos", []))

    hoje = datetime.now()
    total_consultas = 0
    novas_consultas = 0

    log(f"Backfill DJe: {dias} dias, {len(COMARCAS_DJE)} comarcas", "INFO")
    log(f"Progresso anterior: {len(processados)} datas já processadas", "INFO")

    try:
        for i in range(dias):
            d = hoje - timedelta(days=i)
            if d.weekday() == 6:  # Pular domingos
                continue

            data_str = d.strftime("%d/%m/%Y")
            chave = data_str

            if chave in processados:
                continue

            matches = buscar_no_diario_html(data_str)
            todos_matches.extend(matches)

            # Extrair CNJs novos
            for m in matches:
                for cnj in m.get("cnjs_no_contexto", []):
                    cnjs_descobertos.add(cnj)

            processados[chave] = {
                "data": data_str,
                "matches": len(matches),
                "timestamp": datetime.now().isoformat(),
            }

            novas_consultas += 1
            total_consultas += 1

            # Salvar progresso a cada 10 datas
            if novas_consultas % 10 == 0:
                progresso["processados"] = processados
                progresso["matches"] = todos_matches
                progresso["cnjs_descobertos"] = sorted(list(cnjs_descobertos))
                salvar_progresso_backfill(progresso)
                pct = (i / dias) * 100
                log(f"Progresso: {pct:.0f}% ({i}/{dias} dias, {len(todos_matches)} matches, {len(cnjs_descobertos)} CNJs)", "INFO")

            time.sleep(delay)

    except KeyboardInterrupt:
        log("Interrompido pelo usuário. Salvando progresso...", "AVISO")

    # Salvar progresso final
    progresso["processados"] = processados
    progresso["matches"] = todos_matches
    progresso["cnjs_descobertos"] = sorted(list(cnjs_descobertos))
    progresso["ultima_execucao"] = datetime.now().isoformat()
    salvar_progresso_backfill(progresso)

    log(f"Backfill concluído: {novas_consultas} datas novas, {len(todos_matches)} matches total, {len(cnjs_descobertos)} CNJs descobertos", "OK")

    return progresso


# ============================================================
# MONITOR PRINCIPAL
# ============================================================

def monitorar(datas, modo_json=False, salvar=False):
    """Monitora publicações em uma ou mais datas."""
    todos_matches = []

    if not modo_json:
        print(f"\n  {C.B}MONITOR DJe TJMG — {len(datas)} dia(s){C.R}", file=sys.stderr)
        print(f"  {'═' * 60}", file=sys.stderr)
        print(f"  Termos: {', '.join(TERMOS_BUSCA[:3])}...", file=sys.stderr)
        cnjs = carregar_cnjs_ativos()
        print(f"  CNJs monitorados: {len(cnjs)}", file=sys.stderr)
        print(f"  Comarcas: {len(COMARCAS_DJE)}", file=sys.stderr)

    for data in datas:
        matches = buscar_no_diario_html(data)
        todos_matches.extend(matches)

        if not modo_json:
            if matches:
                log(f"{len(matches)} publicação(ões) encontrada(s) em {data}", "NOVO")
                for m in matches[:5]:
                    print(f"    {C.CY}{m['comarca']}{C.R}: {m['termo']}", file=sys.stderr)
                    print(f"    ...{m['contexto'][:150]}...", file=sys.stderr)
                    if m.get("cnjs_no_contexto"):
                        print(f"    CNJs: {', '.join(m['cnjs_no_contexto'])}", file=sys.stderr)
                    print(file=sys.stderr)

    # Extrair CNJs descobertos
    cnjs_descobertos = set()
    for m in todos_matches:
        for cnj in m.get("cnjs_no_contexto", []):
            cnjs_descobertos.add(cnj)

    resumo = {
        "data_consulta": datetime.now().isoformat(),
        "datas_pesquisadas": datas,
        "total_matches": len(todos_matches),
        "matches": todos_matches,
        "termos_buscados": TERMOS_BUSCA,
        "cnjs_monitorados": len(carregar_cnjs_ativos()),
        "cnjs_descobertos": sorted(list(cnjs_descobertos)),
        "comarcas_pesquisadas": list(COMARCAS_DJE.keys()),
    }

    if not modo_json:
        print(f"\n  {'═' * 60}", file=sys.stderr)
        if todos_matches:
            print(f"  {C.G}{C.B}ATENÇÃO: {len(todos_matches)} publicação(ões) encontrada(s)!{C.R}", file=sys.stderr)
            if cnjs_descobertos:
                print(f"  CNJs encontrados: {len(cnjs_descobertos)}", file=sys.stderr)
                for cnj in sorted(cnjs_descobertos):
                    print(f"    {cnj}", file=sys.stderr)
        else:
            print(f"  Nenhuma publicação encontrada nos dias pesquisados.", file=sys.stderr)
        print(f"  {'═' * 60}\n", file=sys.stderr)

    if modo_json:
        print(json.dumps(resumo, ensure_ascii=False, indent=2))

    if salvar:
        SAIDA_DIR.mkdir(parents=True, exist_ok=True)
        data_str = datetime.now().strftime("%Y-%m-%d_%H%M")
        saida = SAIDA_DIR / f"dje-tjmg-{data_str}.json"
        saida.write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"Salvo em {saida}", "OK")

    return resumo


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Monitor de publicações no DJe TJMG",
    )
    parser.add_argument("--data", type=str, help="Data específica (dd/mm/yyyy)")
    parser.add_argument("--dias", type=int, default=1, help="Últimos N dias (padrão: 1 = hoje)")
    parser.add_argument("--historico", type=int, metavar="N", help="Backfill: escanear últimos N dias (todas comarcas)")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    parser.add_argument("--salvar", action="store_true", help="Salvar resultado")

    args = parser.parse_args()

    if args.historico:
        resultado = backfill_dje(dias=args.historico)
        if args.json:
            print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return

    if args.data:
        datas = [args.data]
    else:
        hoje = datetime.now()
        datas = []
        for i in range(args.dias):
            d = hoje - timedelta(days=i)
            if d.weekday() != 6:
                datas.append(d.strftime("%d/%m/%Y"))

    monitorar(datas, modo_json=args.json, salvar=args.salvar)


if __name__ == "__main__":
    main()
