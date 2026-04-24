#!/usr/bin/env python3
"""
Monitor de movimentações via DataJud API Pública (CNJ).

Busca movimentações recentes de processos ativos do perito.
NÃO gasta tokens Anthropic — usa API pública gratuita do CNJ.

Uso:
  python3 datajud_api.py                          # Busca todos os processos ativos
  python3 datajud_api.py --cnj 5001615-98.2025.8.13.0074
  python3 datajud_api.py --dias 7                 # Movimentações dos últimos 7 dias
  python3 datajud_api.py --json                   # Saída JSON
  python3 datajud_api.py --salvar                 # Salva resultado em arquivo

Fontes de CNJs:
  1. STATUS-PROCESSOS.json (scanner automático)
  2. FICHA.json de cada pasta de processo
  3. --cnj manual
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("requests não instalado. Rode: pip install requests")
    sys.exit(1)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
try:
    from src.pje.datajud_client import consultar_processo as _consultar_processo
    from src.pje.datajud_client import buscar_movimentacoes as _buscar_movimentacoes_client
    from src.pje.datajud_client import _cnj_sem_formatacao, _detectar_tribunal, TRIBUNAL_MAP
except ImportError as e:
    print(f"ERRO FATAL: datajud_client.py nao encontrado: {e}", file=_sys.stderr)
    print("Certifique-se de estar no diretorio ~/stemmia-forense/", file=_sys.stderr)
    _consultar_processo = None
    _buscar_movimentacoes_client = None
    TRIBUNAL_MAP = {}

try:
    from src.config import DATAJUD_API_KEY as API_KEY
except ImportError:
    import os as _os
    API_KEY = _os.getenv("DATAJUD_API_KEY", "")

BASE_DIR = Path(__file__).parent.parent.parent  # ~/stemmia-forense/data/
SAIDA_DIR = BASE_DIR / "scripts" / "monitor-publicacoes" / "resultados"
STATUS_JSON = BASE_DIR / "STATUS-PROCESSOS.json"

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
    DIM = "\033[2m"


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ", "OK": "✓", "ERRO": "✗", "AVISO": "⚠", "NOVO": "★"}.get(level, "·")
    print(f"  [{ts}] {prefix} {msg}", file=sys.stderr)


# ============================================================
# UTILITÁRIOS
# ============================================================

def carregar_cnjs_ativos():
    """Carrega CNJs de processos ativos do STATUS-PROCESSOS.json."""
    cnjs = []
    if not STATUS_JSON.exists():
        log("STATUS-PROCESSOS.json não encontrado", "AVISO")
        return cnjs

    try:
        with open(STATUS_JSON, encoding="utf-8") as f:
            data = json.load(f)

        processos = data.get("processos", [])
        for p in processos:
            cnj = p.get("cnj", "")
            estado = p.get("estado", "")
            # Pular processos sem CNJ ou já realizados
            if cnj and RE_CNJ.match(cnj) and "REALIZADO" not in estado:
                cnjs.append(cnj)
    except (json.JSONDecodeError, OSError) as e:
        log(f"Erro ao ler STATUS-PROCESSOS.json: {e}", "ERRO")

    return list(set(cnjs))  # Remove duplicatas


# ============================================================
# CONSULTA API
# ============================================================

def buscar_processo(cnj, timeout=15):
    """Busca um processo na API DataJud via datajud_client unificado."""
    if _consultar_processo is None:
        log("datajud_client nao disponivel — import falhou", "ERRO")
        return None
    try:
        return _consultar_processo(cnj, timeout=timeout)
    except Exception as e:
        log(f"Erro datajud_client ao buscar {cnj}: {e}", "ERRO")
        return None


def extrair_movimentacoes(dados_processo, dias=30):
    """Extrai movimentações recentes de um processo."""
    movs = dados_processo.get("movimentos", [])
    if not movs:
        return []

    data_limite = datetime.now() - timedelta(days=dias)
    recentes = []

    for mov in movs:
        data_str = mov.get("dataHora", "")
        try:
            # Formato: 2025-03-01T00:00:00.000Z ou similar
            data_mov = datetime.fromisoformat(data_str.replace("Z", "+00:00").replace("+00:00", ""))
        except (ValueError, AttributeError):
            try:
                data_mov = datetime.strptime(data_str[:19], "%Y-%m-%dT%H:%M:%S")
            except (ValueError, AttributeError):
                continue

        if data_mov >= data_limite:
            nome = mov.get("nome", mov.get("descricao", "Sem descrição"))
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

    # Ordenar por data (mais recente primeiro)
    recentes.sort(key=lambda x: x.get("data_iso", ""), reverse=True)
    return recentes


# ============================================================
# MONITOR PRINCIPAL
# ============================================================

def monitorar(cnjs, dias=30, modo_json=False, salvar=False):
    """Monitora movimentações de uma lista de CNJs."""
    resultados = []
    total = len(cnjs)

    if not modo_json:
        print(f"\n  {C.B}MONITOR DataJud — {total} processo(s), últimos {dias} dia(s){C.R}", file=sys.stderr)
        print(f"  {'═' * 60}", file=sys.stderr)

    for i, cnj in enumerate(cnjs, 1):
        if not modo_json:
            print(f"\n  [{i}/{total}] {C.B}{cnj}{C.R}", file=sys.stderr)

        dados = buscar_processo(cnj)
        if not dados:
            log(f"Processo não encontrado na API", "AVISO")
            resultados.append({"cnj": cnj, "encontrado": False, "movimentacoes": []})
            continue

        # Dados básicos
        classe = dados.get("classe", {})
        classe_nome = classe.get("nome", "") if isinstance(classe, dict) else str(classe)

        orgao = dados.get("orgaoJulgador", {})
        orgao_nome = orgao.get("nome", "") if isinstance(orgao, dict) else str(orgao)

        assuntos = dados.get("assuntos", [])
        assunto_texto = "; ".join(
            [a.get("nome", "") for a in assuntos if isinstance(a, dict)]
        ) if assuntos else ""

        # Movimentações recentes
        movs = extrair_movimentacoes(dados, dias=dias)

        resultado = {
            "cnj": cnj,
            "encontrado": True,
            "classe": classe_nome,
            "orgao_julgador": orgao_nome,
            "assuntos": assunto_texto,
            "total_movimentacoes": len(dados.get("movimentos", [])),
            "movimentacoes_recentes": len(movs),
            "movimentacoes": movs,
        }
        resultados.append(resultado)

        if not modo_json:
            log(f"Classe: {classe_nome}", "OK")
            log(f"Órgão: {orgao_nome}")
            if movs:
                log(f"{C.G}{len(movs)} movimentação(ões) nos últimos {dias} dias{C.R}", "NOVO")
                for m in movs[:5]:  # Mostra até 5
                    compl = f" — {m['complemento']}" if m['complemento'] else ""
                    print(f"    {C.CY}{m['data']}{C.R}  {m['nome']}{compl}", file=sys.stderr)
                if len(movs) > 5:
                    print(f"    ... e mais {len(movs) - 5}", file=sys.stderr)
            else:
                log(f"Sem movimentações nos últimos {dias} dias", "INFO")

    # Resumo
    encontrados = sum(1 for r in resultados if r["encontrado"])
    com_movs = sum(1 for r in resultados if r.get("movimentacoes_recentes", 0) > 0)
    total_movs = sum(r.get("movimentacoes_recentes", 0) for r in resultados)

    resumo = {
        "data_consulta": datetime.now().isoformat(),
        "dias_filtro": dias,
        "total_processos": total,
        "encontrados": encontrados,
        "com_movimentacoes": com_movs,
        "total_movimentacoes": total_movs,
        "resultados": resultados,
    }

    if not modo_json:
        print(f"\n  {'═' * 60}", file=sys.stderr)
        print(f"  {C.B}RESUMO{C.R}", file=sys.stderr)
        print(f"  Processos consultados: {total}", file=sys.stderr)
        print(f"  Encontrados na API:    {encontrados}", file=sys.stderr)
        print(f"  Com movimentações:     {C.G}{com_movs}{C.R}" if com_movs else f"  Com movimentações:     {com_movs}", file=sys.stderr)
        print(f"  Total movimentações:   {total_movs}", file=sys.stderr)
        print(f"  {'═' * 60}\n", file=sys.stderr)

    if modo_json:
        print(json.dumps(resumo, ensure_ascii=False, indent=2))

    if salvar:
        SAIDA_DIR.mkdir(parents=True, exist_ok=True)
        data_str = datetime.now().strftime("%Y-%m-%d_%H%M")
        saida = SAIDA_DIR / f"datajud-{data_str}.json"
        saida.write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"Resultado salvo em {saida}", "OK")

    return resumo


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Monitor de movimentações processuais via DataJud API (CNJ)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python3 datajud_api.py                    # Todos os processos ativos\n"
            "  python3 datajud_api.py --cnj 5001615-98.2025.8.13.0074\n"
            "  python3 datajud_api.py --dias 7 --salvar  # Últimos 7 dias, salva JSON\n"
        )
    )
    parser.add_argument("--cnj", nargs="+", help="CNJ(s) específico(s) para buscar")
    parser.add_argument("--dias", type=int, default=30, help="Filtrar movimentações dos últimos N dias (padrão: 30)")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    parser.add_argument("--salvar", action="store_true", help="Salvar resultado em arquivo JSON")
    parser.add_argument("--limite", type=int, default=0, help="Limitar a N processos (0 = todos)")

    args = parser.parse_args()

    # Determinar CNJs
    if args.cnj:
        cnjs = args.cnj
    else:
        cnjs = carregar_cnjs_ativos()
        if not cnjs:
            log("Nenhum processo ativo encontrado. Use --cnj para especificar.", "ERRO")
            sys.exit(1)

    if args.limite > 0:
        cnjs = cnjs[:args.limite]

    log(f"Consultando {len(cnjs)} processo(s) na API DataJud...")
    monitorar(cnjs, dias=args.dias, modo_json=args.json, salvar=args.salvar)


if __name__ == "__main__":
    main()
