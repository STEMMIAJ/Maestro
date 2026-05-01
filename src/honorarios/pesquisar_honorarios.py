#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pesquisador de Honorários Periciais — Stemmia Forense

Consulta múltiplas fontes de dados sobre honorários periciais
em paralelo e gera relatório comparativo com semáforo de risco.

Uso:
    python3 pesquisar_honorarios.py --tipo medica --comarca "Governador Valadares" --valor 4000
    python3 pesquisar_honorarios.py --tipo trabalhista --tribunal TRT3 --relatorio
    python3 pesquisar_honorarios.py --tipo erro_medico --valor 5000 --json --salvar
"""

import argparse
import json
import math
import sqlite3
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = SCRIPT_DIR / "dados" / "honorarios.db"
PESQUISAS_DIR = SCRIPT_DIR / "dados" / "pesquisas"

# Cores ANSI
VERDE = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
AZUL = "\033[94m"
CIANO = "\033[96m"
NEGRITO = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# Mapa de aliases para comarcas
ALIASES_COMARCA = {
    "gv": "Governador Valadares",
    "gov valadares": "Governador Valadares",
    "gov. valadares": "Governador Valadares",
    "governador valadares": "Governador Valadares",
    "bh": "Belo Horizonte",
    "jf": "Juiz de Fora",
}

# Mapa de aliases para tipos de perícia
ALIASES_TIPO = {
    "medica": "Médica",
    "médica": "Médica",
    "erro_medico": "Erro Médico",
    "erro médico": "Erro Médico",
    "erro_médico": "Erro Médico",
    "trabalhista": "Trabalhista",
    "securitaria": "Securitária",
    "securitária": "Securitária",
    "bpc_loas": "BPC/LOAS",
    "bpc": "BPC/LOAS",
    "loas": "BPC/LOAS",
    "curatela": "Curatela",
    "civel": "Cível",
    "cível": "Cível",
    "insalubridade": "Insalubridade",
    "ocupacional": "Ocupacional",
    "gratuidade": "Gratuidade",
}


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════


def formatar_brl(valor):
    """Formata valor numérico em reais (R$ 1.234,56)."""
    if valor is None:
        return "—"
    if valor == int(valor):
        inteiro = int(valor)
        return f"R$ {inteiro:,.0f}".replace(",", ".")
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def normalizar_comarca(comarca):
    """Normaliza nome da comarca usando aliases."""
    if comarca is None:
        return None
    chave = comarca.strip().lower()
    return ALIASES_COMARCA.get(chave, comarca.strip())


def normalizar_tipo(tipo):
    """Normaliza tipo de perícia usando aliases."""
    if tipo is None:
        return None
    chave = tipo.strip().lower()
    return ALIASES_TIPO.get(chave, tipo.strip())


def conectar_db():
    """Conecta ao banco SQLite."""
    if not DB_PATH.exists():
        print(f"{VERMELHO}ERRO: Banco de dados não encontrado em {DB_PATH}{RESET}")
        sys.exit(1)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE CONSULTA
# ═══════════════════════════════════════════════════════════════════════════════


def consultar_base_local(filtros):
    """
    Consulta a tabela honorarios_coletados com filtros.

    Args:
        filtros: dict com chaves tipo, comarca, tribunal, ano_inicio, ano_fim

    Returns:
        dict com 'registros' (lista de dicts) e 'total' (int)
    """
    conn = conectar_db()
    try:
        where = []
        params = []

        if filtros.get("tipo"):
            tipo_norm = normalizar_tipo(filtros["tipo"])
            where.append("tipo_pericia LIKE ?")
            params.append(f"%{tipo_norm}%")

        if filtros.get("comarca"):
            comarca_norm = normalizar_comarca(filtros["comarca"])
            where.append("(comarca LIKE ? OR comarca LIKE ?)")
            params.append(f"%{comarca_norm}%")
            # Adicionar abreviação se for Governador Valadares
            if comarca_norm == "Governador Valadares":
                params.append("%GV%")
            else:
                params.append(f"%{comarca_norm}%")

        if filtros.get("tribunal"):
            where.append("tribunal = ?")
            params.append(filtros["tribunal"].upper())

        if filtros.get("ano_inicio"):
            where.append("ano >= ?")
            params.append(filtros["ano_inicio"])

        if filtros.get("ano_fim"):
            where.append("ano <= ?")
            params.append(filtros["ano_fim"])

        sql = "SELECT * FROM honorarios_coletados"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY ano DESC, valor_fixado DESC"

        cursor = conn.execute(sql, params)
        registros = [dict(row) for row in cursor.fetchall()]

        return {
            "fonte": "base_local",
            "registros": registros,
            "total": len(registros),
        }
    finally:
        conn.close()


def consultar_proprios(filtros):
    """
    Consulta a tabela honorarios_proprios (histórico do perito).

    Args:
        filtros: dict com chaves tipo, comarca, tribunal

    Returns:
        dict com 'registros' (lista de dicts) e 'total' (int)
    """
    conn = conectar_db()
    try:
        where = []
        params = []

        if filtros.get("tipo"):
            tipo_norm = normalizar_tipo(filtros["tipo"])
            where.append("tipo_pericia LIKE ?")
            params.append(f"%{tipo_norm}%")

        if filtros.get("comarca"):
            comarca_norm = normalizar_comarca(filtros["comarca"])
            where.append("(comarca LIKE ? OR comarca LIKE ?)")
            params.append(f"%{comarca_norm}%")
            if comarca_norm == "Governador Valadares":
                params.append("%GV%")
            else:
                params.append(f"%{comarca_norm}%")

        if filtros.get("tribunal"):
            where.append("tribunal = ?")
            params.append(filtros["tribunal"].upper())

        sql = "SELECT * FROM honorarios_proprios"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY data_proposta DESC"

        cursor = conn.execute(sql, params)
        registros = [dict(row) for row in cursor.fetchall()]

        return {
            "fonte": "proprios",
            "registros": registros,
            "total": len(registros),
        }
    finally:
        conn.close()


def consultar_tabelas_oficiais(tribunal=None):
    """
    Consulta tabelas oficiais vigentes.

    Args:
        tribunal: sigla do tribunal (opcional)

    Returns:
        dict com 'registros' (lista de dicts) e 'total' (int)
    """
    conn = conectar_db()
    try:
        where = ["(vigencia_fim = 'atual' OR vigencia_fim IS NULL OR vigencia_fim = '' OR vigencia_fim >= ?)"]
        params = [str(datetime.now().year)]

        if tribunal:
            where.append("fonte LIKE ?")
            params.append(f"%{tribunal.upper()}%")

        sql = "SELECT * FROM tabelas_oficiais"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY fonte"

        cursor = conn.execute(sql, params)
        registros = [dict(row) for row in cursor.fetchall()]

        hoje = datetime.now().date()
        ativos = []
        for r in registros:
            vf = (r.get("vigencia_fim") or "").strip()
            if vf in ("", "atual"):
                ativos.append(r)
                continue
            data_fim = None
            for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y"):
                try:
                    data_fim = datetime.strptime(vf, fmt).date()
                    break
                except ValueError:
                    continue
            if data_fim is None or data_fim >= hoje:
                ativos.append(r)

        return {
            "fonte": "tabelas_oficiais",
            "registros": ativos,
            "total": len(ativos),
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE CÁLCULO
# ═══════════════════════════════════════════════════════════════════════════════


def calcular_estatisticas(valores):
    """
    Calcula estatísticas descritivas de uma lista de valores.

    Args:
        valores: lista de floats

    Returns:
        dict com media, mediana, minimo, maximo, desvio_padrao, q1, q3, n
    """
    if not valores:
        return None

    valores_sorted = sorted(valores)
    n = len(valores_sorted)

    media = statistics.mean(valores_sorted)
    mediana = statistics.median(valores_sorted)
    minimo = min(valores_sorted)
    maximo = max(valores_sorted)

    if n >= 2:
        desvio = statistics.stdev(valores_sorted)
    else:
        desvio = 0.0

    # Quartis
    meio = n // 2
    if n >= 4:
        q1 = statistics.median(valores_sorted[:meio])
        if n % 2 == 0:
            q3 = statistics.median(valores_sorted[meio:])
        else:
            q3 = statistics.median(valores_sorted[meio + 1:])
    elif n >= 2:
        q1 = valores_sorted[0]
        q3 = valores_sorted[-1]
    else:
        q1 = valores_sorted[0]
        q3 = valores_sorted[0]

    return {
        "media": round(media, 2),
        "mediana": round(mediana, 2),
        "minimo": round(minimo, 2),
        "maximo": round(maximo, 2),
        "desvio_padrao": round(desvio, 2),
        "q1": round(q1, 2),
        "q3": round(q3, 2),
        "n": n,
    }


def calcular_percentil(valor, valores_sorted):
    """Calcula o percentil de um valor em relação a uma lista ordenada."""
    if not valores_sorted:
        return 0
    abaixo = sum(1 for v in valores_sorted if v < valor)
    iguais = sum(1 for v in valores_sorted if v == valor)
    return round((abaixo + iguais * 0.5) / len(valores_sorted) * 100, 1)


def gerar_comparativo(resultado_local, resultado_proprios, resultado_oficiais, valor_pretendido=None):
    """
    Consolida resultados de todas as fontes e gera comparativo.

    Args:
        resultado_local: dict retornado por consultar_base_local
        resultado_proprios: dict retornado por consultar_proprios
        resultado_oficiais: dict retornado por consultar_tabelas_oficiais
        valor_pretendido: float (opcional) — valor que o perito quer propor

    Returns:
        dict com todas as informações consolidadas
    """
    comparativo = {
        "data_pesquisa": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "base_local": resultado_local,
        "proprios": resultado_proprios,
        "tabelas_oficiais": resultado_oficiais,
        "estatisticas_local": None,
        "estatisticas_proprios": None,
        "analise_valor": None,
        "argumentos": [],
    }

    # Estatísticas da base local (valor_fixado quando disponível, senão valor_proposto)
    valores_local = []
    for r in resultado_local.get("registros", []):
        v = r.get("valor_fixado") or r.get("valor_proposto")
        if v and v > 0:
            valores_local.append(float(v))

    if valores_local:
        comparativo["estatisticas_local"] = calcular_estatisticas(valores_local)

    # Estatísticas dos honorários próprios
    valores_proprios = []
    for r in resultado_proprios.get("registros", []):
        v = r.get("valor_fixado") or r.get("valor_proposto")
        if v and v > 0:
            valores_proprios.append(float(v))

    if valores_proprios:
        comparativo["estatisticas_proprios"] = calcular_estatisticas(valores_proprios)

    # Análise do valor pretendido
    if valor_pretendido is not None and valor_pretendido > 0:
        analise = {"valor": valor_pretendido}

        # Usar valores da base local para percentil e comparação
        todos_valores = valores_local + valores_proprios
        todos_valores_sorted = sorted(todos_valores) if todos_valores else []

        if todos_valores:
            stats = calcular_estatisticas(todos_valores)
            analise["percentil"] = calcular_percentil(valor_pretendido, todos_valores_sorted)
            analise["vs_media"] = round((valor_pretendido - stats["media"]) / stats["media"] * 100, 1) if stats["media"] > 0 else 0
            analise["vs_mediana"] = round((valor_pretendido - stats["mediana"]) / stats["mediana"] * 100, 1) if stats["mediana"] > 0 else 0

            # Semáforo
            limite_seguro = stats["mediana"] + stats["desvio_padrao"]
            limite_atencao = stats["mediana"] + 2 * stats["desvio_padrao"]

            if valor_pretendido <= limite_seguro:
                analise["semaforo"] = "SEGURO"
                analise["semaforo_cor"] = "verde"
            elif valor_pretendido <= limite_atencao:
                analise["semaforo"] = "ATENCAO"
                analise["semaforo_cor"] = "amarelo"
            else:
                analise["semaforo"] = "RISCO"
                analise["semaforo_cor"] = "vermelho"

            analise["limite_seguro"] = round(limite_seguro, 2)
            analise["limite_atencao"] = round(limite_atencao, 2)
        else:
            analise["percentil"] = None
            analise["vs_media"] = None
            analise["vs_mediana"] = None
            analise["semaforo"] = "SEM_DADOS"
            analise["semaforo_cor"] = "amarelo"

        comparativo["analise_valor"] = analise

        # Gerar argumentos
        argumentos = _gerar_argumentos(
            valor_pretendido, comparativo["estatisticas_local"],
            resultado_oficiais, comparativo["estatisticas_proprios"]
        )
        comparativo["argumentos"] = argumentos

    return comparativo


def _gerar_argumentos(valor, stats_local, resultado_oficiais, stats_proprios):
    """Gera lista de argumentos para fundamentar o valor proposto."""
    argumentos = []

    # Argumento 1: Faixa praticada
    if stats_local and stats_local["n"] >= 3:
        argumentos.append(
            f"Valor dentro da faixa praticada ({formatar_brl(stats_local['minimo'])} – {formatar_brl(stats_local['maximo'])}) "
            f"em {stats_local['n']} decisões analisadas"
        )

    # Argumento 2: Compatível com mediana
    if stats_local and stats_local["mediana"] > 0:
        diff = ((valor - stats_local["mediana"]) / stats_local["mediana"]) * 100
        if abs(diff) <= 30:
            argumentos.append(
                f"Compatível com a mediana da jurisprudência ({formatar_brl(stats_local['mediana'])}), "
                f"diferença de {diff:+.0f}%"
            )

    # Argumento 3: Tabelas oficiais
    for tab in resultado_oficiais.get("registros", []):
        fonte = tab.get("fonte", "")
        vmax = tab.get("valor_maximo", 0)
        normativo = tab.get("normativo", "")
        obs = tab.get("observacoes", "")

        if vmax and vmax > 0:
            # Majoração 5x se mencionada
            if "5x" in (obs or ""):
                majorado = vmax * 5
                argumentos.append(
                    f"Referência {fonte}: até {formatar_brl(vmax)} "
                    f"(majoração 5x = {formatar_brl(majorado)})"
                )
            else:
                argumentos.append(
                    f"Referência {fonte}: até {formatar_brl(vmax)}"
                )

    # Argumento 4: Histórico pessoal
    if stats_proprios and stats_proprios["n"] >= 2:
        argumentos.append(
            f"Histórico pessoal: {stats_proprios['n']} perícias similares, "
            f"média fixada em {formatar_brl(stats_proprios['media'])}"
        )

    # Argumento 5: Complexidade técnica
    argumentos.append(
        "Compatível com a complexidade técnica do caso, conforme "
        "art. 465, §2º, III do CPC e parâmetros do CNJ"
    )

    return argumentos


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE SAÍDA
# ═══════════════════════════════════════════════════════════════════════════════


def imprimir_terminal(comparativo, filtros):
    """
    Imprime relatório formatado no terminal com tabelas e cores ANSI.

    Args:
        comparativo: dict gerado por gerar_comparativo
        filtros: dict com os filtros usados na pesquisa
    """
    tipo = filtros.get("tipo") or "Geral"
    comarca = filtros.get("comarca") or "Todas"
    tribunal = filtros.get("tribunal") or "Todos"

    # Cabeçalho
    print()
    print(f"{NEGRITO}{CIANO}{'═' * 60}{RESET}")
    print(f"{NEGRITO}{CIANO}║  PESQUISADOR DE HONORÁRIOS PERICIAIS — Stemmia{' ' * 11}║{RESET}")
    print(f"{NEGRITO}{CIANO}{'═' * 60}{RESET}")
    print(f"{NEGRITO}{CIANO}║  Tipo: {tipo:<15} | Comarca: {comarca:<12} | {tribunal:<6} ║{RESET}")
    print(f"{NEGRITO}{CIANO}{'═' * 60}{RESET}")
    print()

    # Estatísticas da base local
    stats = comparativo.get("estatisticas_local")
    total_local = comparativo["base_local"]["total"]

    if stats:
        print(f"{NEGRITO}  ESTATÍSTICAS DA BASE LOCAL ({stats['n']} registros com valor){RESET}")
        _imprimir_tabela_stats(stats)
    else:
        print(f"{AMARELO}  BASE LOCAL: Nenhum registro com valor para os filtros aplicados.{RESET}")
        if total_local > 0:
            print(f"{DIM}  ({total_local} registros encontrados, mas sem valores numéricos){RESET}")

    # Estatísticas próprias
    stats_p = comparativo.get("estatisticas_proprios")
    total_proprios = comparativo["proprios"]["total"]

    if stats_p:
        print()
        print(f"{NEGRITO}  SEU HISTÓRICO ({stats_p['n']} perícias com valor){RESET}")
        _imprimir_tabela_stats(stats_p)
    elif total_proprios > 0:
        print()
        print(f"{DIM}  Seu histórico: {total_proprios} perícias encontradas (sem valores numéricos){RESET}")

    # Tabelas oficiais
    oficiais = comparativo["tabelas_oficiais"]["registros"]
    if oficiais:
        print()
        print(f"{NEGRITO}  TABELAS OFICIAIS VIGENTES{RESET}")
        _imprimir_tabela_oficiais(oficiais)

    # Análise do valor
    analise = comparativo.get("analise_valor")
    if analise:
        print()
        valor = analise["valor"]
        print(f"{NEGRITO}  SEU VALOR: {formatar_brl(valor)}{RESET}")

        semaforo = analise.get("semaforo", "SEM_DADOS")
        cor_semaforo = {
            "SEGURO": VERDE,
            "ATENCAO": AMARELO,
            "RISCO": VERMELHO,
            "SEM_DADOS": AMARELO,
        }.get(semaforo, RESET)

        emoji_semaforo = {
            "SEGURO": "SEGURO",
            "ATENCAO": "ATENCAO",
            "RISCO": "RISCO",
            "SEM_DADOS": "SEM DADOS",
        }.get(semaforo, "—")

        print(f"  {'┌' + '─' * 16 + '┬' + '─' * 20 + '┐'}")

        if analise.get("percentil") is not None:
            print(f"  │ {'Percentil':<14} │ {analise['percentil']:>5}%{' ' * 13}│")
        if analise.get("vs_media") is not None:
            sinal = "+" if analise["vs_media"] >= 0 else ""
            print(f"  │ {'vs Média':<14} │ {sinal}{analise['vs_media']:.0f}%{' ' * 14}│")
        if analise.get("vs_mediana") is not None:
            sinal = "+" if analise["vs_mediana"] >= 0 else ""
            print(f"  │ {'vs Mediana':<14} │ {sinal}{analise['vs_mediana']:.0f}%{' ' * 14}│")

        print(f"  │ {'Semáforo':<14} │ {cor_semaforo}{emoji_semaforo:<18}{RESET} │")
        print(f"  {'└' + '─' * 16 + '┴' + '─' * 20 + '┘'}")

    # Argumentos
    argumentos = comparativo.get("argumentos", [])
    if argumentos:
        print()
        print(f"{NEGRITO}  ARGUMENTOS PARA FUNDAMENTAR:{RESET}")
        for i, arg in enumerate(argumentos, 1):
            print(f"  {i}. {arg}")

    # Rodapé
    print()
    print(f"{DIM}  Pesquisa realizada em {comparativo['data_pesquisa']}{RESET}")
    print(f"{DIM}  Base: {DB_PATH}{RESET}")
    print()


def _imprimir_tabela_stats(stats):
    """Imprime tabela de estatísticas formatada."""
    print(f"  {'┌' + '─' * 12 + '┬' + '─' * 16 + '┐'}")
    print(f"  │ {'Métrica':<10} │ {'Valor':>14} │")
    print(f"  {'├' + '─' * 12 + '┼' + '─' * 16 + '┤'}")
    print(f"  │ {'Mínimo':<10} │ {formatar_brl(stats['minimo']):>14} │")
    print(f"  │ {'Q1 (25%)':<10} │ {formatar_brl(stats['q1']):>14} │")
    print(f"  │ {'Média':<10} │ {formatar_brl(stats['media']):>14} │")
    print(f"  │ {'Mediana':<10} │ {formatar_brl(stats['mediana']):>14} │")
    print(f"  │ {'Q3 (75%)':<10} │ {formatar_brl(stats['q3']):>14} │")
    print(f"  │ {'Máximo':<10} │ {formatar_brl(stats['maximo']):>14} │")
    print(f"  │ {'Desvio':<10} │ {formatar_brl(stats['desvio_padrao']):>14} │")
    print(f"  {'└' + '─' * 12 + '┴' + '─' * 16 + '┘'}")


def _imprimir_tabela_oficiais(oficiais):
    """Imprime tabela de referências oficiais."""
    # Calcular largura dinâmica da coluna fonte
    max_fonte = max(len(r.get("fonte", "") or "") for r in oficiais)
    max_fonte = max(max_fonte, 5)  # mínimo "Fonte"
    col_fonte = min(max_fonte + 2, 35)

    print(f"  {'┌' + '─' * col_fonte + '┬' + '─' * 14 + '┬' + '─' * 14 + '┐'}")
    print(f"  │ {'Fonte':<{col_fonte - 2}} │ {'Base':>12} │ {'Máximo':>12} │")
    print(f"  {'├' + '─' * col_fonte + '┼' + '─' * 14 + '┼' + '─' * 14 + '┤'}")

    for r in oficiais:
        fonte = (r.get("fonte", "") or "")[:col_fonte - 2]
        vbase = formatar_brl(r.get("valor_base"))
        vmax = formatar_brl(r.get("valor_maximo"))
        print(f"  │ {fonte:<{col_fonte - 2}} │ {vbase:>12} │ {vmax:>12} │")

    print(f"  {'└' + '─' * col_fonte + '┴' + '─' * 14 + '┴' + '─' * 14 + '┘'}")


def salvar_json(comparativo, path=None):
    """
    Salva resultado em JSON.

    Args:
        comparativo: dict gerado por gerar_comparativo
        path: Path (opcional) — se não informado, gera automaticamente

    Returns:
        Path do arquivo salvo
    """
    if path is None:
        PESQUISAS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H%M")
        path = PESQUISAS_DIR / f"pesquisa-{ts}.json"

    # Converter para serializável
    dados = _tornar_serializavel(comparativo)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f"{VERDE}  JSON salvo em: {path}{RESET}")
    return path


def _tornar_serializavel(obj):
    """Converte objetos para tipos serializáveis em JSON."""
    if isinstance(obj, dict):
        return {k: _tornar_serializavel(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_tornar_serializavel(item) for item in obj]
    elif isinstance(obj, Path):
        return str(obj)
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        return str(obj)


def salvar_md(comparativo, filtros, path=None):
    """
    Salva relatório em Markdown.

    Args:
        comparativo: dict gerado por gerar_comparativo
        filtros: dict com os filtros usados
        path: Path (opcional) — se não informado, gera automaticamente

    Returns:
        Path do arquivo salvo
    """
    if path is None:
        PESQUISAS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H%M")
        path = PESQUISAS_DIR / f"pesquisa-{ts}.md"

    tipo = filtros.get("tipo") or "Geral"
    comarca = filtros.get("comarca") or "Todas"
    tribunal = filtros.get("tribunal") or "Todos"

    linhas = []
    linhas.append(f"# Pesquisa de Honorários Periciais")
    linhas.append(f"")
    linhas.append(f"**Data:** {comparativo['data_pesquisa']}")
    linhas.append(f"**Tipo:** {tipo} | **Comarca:** {comarca} | **Tribunal:** {tribunal}")
    linhas.append(f"")

    # Estatísticas da base local
    stats = comparativo.get("estatisticas_local")
    if stats:
        linhas.append(f"## Estatísticas da Base Local ({stats['n']} registros)")
        linhas.append(f"")
        linhas.append(f"| Métrica | Valor |")
        linhas.append(f"|---------|-------|")
        linhas.append(f"| Mínimo | {formatar_brl(stats['minimo'])} |")
        linhas.append(f"| Q1 (25%) | {formatar_brl(stats['q1'])} |")
        linhas.append(f"| Média | {formatar_brl(stats['media'])} |")
        linhas.append(f"| Mediana | {formatar_brl(stats['mediana'])} |")
        linhas.append(f"| Q3 (75%) | {formatar_brl(stats['q3'])} |")
        linhas.append(f"| Máximo | {formatar_brl(stats['maximo'])} |")
        linhas.append(f"| Desvio padrão | {formatar_brl(stats['desvio_padrao'])} |")
        linhas.append(f"")

    # Histórico próprio
    stats_p = comparativo.get("estatisticas_proprios")
    if stats_p:
        linhas.append(f"## Seu Histórico ({stats_p['n']} perícias)")
        linhas.append(f"")
        linhas.append(f"| Métrica | Valor |")
        linhas.append(f"|---------|-------|")
        linhas.append(f"| Mínimo | {formatar_brl(stats_p['minimo'])} |")
        linhas.append(f"| Média | {formatar_brl(stats_p['media'])} |")
        linhas.append(f"| Mediana | {formatar_brl(stats_p['mediana'])} |")
        linhas.append(f"| Máximo | {formatar_brl(stats_p['maximo'])} |")
        linhas.append(f"")

    # Tabelas oficiais
    oficiais = comparativo["tabelas_oficiais"]["registros"]
    if oficiais:
        linhas.append(f"## Tabelas Oficiais Vigentes")
        linhas.append(f"")
        linhas.append(f"| Fonte | Base | Máximo |")
        linhas.append(f"|-------|------|--------|")
        for r in oficiais:
            fonte = r.get("fonte", "")
            vbase = formatar_brl(r.get("valor_base"))
            vmax = formatar_brl(r.get("valor_maximo"))
            linhas.append(f"| {fonte} | {vbase} | {vmax} |")
        linhas.append(f"")

    # Análise do valor
    analise = comparativo.get("analise_valor")
    if analise:
        linhas.append(f"## Análise do Valor Pretendido: {formatar_brl(analise['valor'])}")
        linhas.append(f"")
        if analise.get("percentil") is not None:
            linhas.append(f"- **Percentil:** {analise['percentil']}%")
        if analise.get("vs_media") is not None:
            sinal = "+" if analise["vs_media"] >= 0 else ""
            linhas.append(f"- **vs Média:** {sinal}{analise['vs_media']:.0f}%")
        if analise.get("vs_mediana") is not None:
            sinal = "+" if analise["vs_mediana"] >= 0 else ""
            linhas.append(f"- **vs Mediana:** {sinal}{analise['vs_mediana']:.0f}%")

        semaforo_texto = {
            "SEGURO": "SEGURO (valor conservador)",
            "ATENCAO": "ATENCAO (valor acima da média, requer fundamentação sólida)",
            "RISCO": "RISCO (valor significativamente acima, alta chance de impugnação)",
            "SEM_DADOS": "SEM DADOS SUFICIENTES",
        }.get(analise.get("semaforo", ""), "—")
        linhas.append(f"- **Semáforo:** {semaforo_texto}")
        linhas.append(f"")

    # Argumentos
    argumentos = comparativo.get("argumentos", [])
    if argumentos:
        linhas.append(f"## Argumentos para Fundamentação")
        linhas.append(f"")
        for i, arg in enumerate(argumentos, 1):
            linhas.append(f"{i}. {arg}")
        linhas.append(f"")

    # Detalhes dos registros
    registros_local = comparativo["base_local"]["registros"]
    if registros_local:
        linhas.append(f"## Detalhes — Base Local ({len(registros_local)} registros)")
        linhas.append(f"")
        linhas.append(f"| Processo | Tribunal | Tipo | Proposto | Fixado | Ano |")
        linhas.append(f"|----------|----------|------|----------|--------|-----|")
        for r in registros_local[:30]:  # Limitar a 30
            proc = r.get("numero_processo", "—") or "—"
            trib = r.get("tribunal", "—") or "—"
            tp = r.get("tipo_pericia", "—") or "—"
            vp = formatar_brl(r.get("valor_proposto"))
            vf = formatar_brl(r.get("valor_fixado"))
            ano = r.get("ano", "—") or "—"
            linhas.append(f"| {proc} | {trib} | {tp} | {vp} | {vf} | {ano} |")
        linhas.append(f"")

    # Rodapé
    linhas.append(f"---")
    linhas.append(f"*Gerado por Pesquisador de Honorários — Stemmia Forense*")
    linhas.append(f"*Base: {DB_PATH}*")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    print(f"{VERDE}  Relatório MD salvo em: {path}{RESET}")
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════


def pesquisar(filtros, valor_pretendido=None, gerar_rel=False, gerar_json_flag=False, salvar_db=False):
    """
    Função principal que orquestra a pesquisa em paralelo.

    Args:
        filtros: dict com tipo, comarca, tribunal, ano_inicio, ano_fim
        valor_pretendido: float (opcional)
        gerar_rel: bool — gerar relatório MD
        gerar_json_flag: bool — gerar JSON
        salvar_db: bool — salvar novos registros no SQLite

    Returns:
        dict comparativo completo
    """
    # Consultas em paralelo com 3 workers
    resultado_local = None
    resultado_proprios = None
    resultado_oficiais = None

    with ThreadPoolExecutor(max_workers=3) as executor:
        futuro_local = executor.submit(consultar_base_local, filtros)
        futuro_proprios = executor.submit(consultar_proprios, filtros)
        futuro_oficiais = executor.submit(consultar_tabelas_oficiais, filtros.get("tribunal"))

        for futuro in as_completed([futuro_local, futuro_proprios, futuro_oficiais]):
            try:
                resultado = futuro.result()
                if futuro == futuro_local:
                    resultado_local = resultado
                elif futuro == futuro_proprios:
                    resultado_proprios = resultado
                elif futuro == futuro_oficiais:
                    resultado_oficiais = resultado
            except Exception as e:
                print(f"{VERMELHO}  Erro na consulta: {e}{RESET}")

    # Fallbacks
    if resultado_local is None:
        resultado_local = {"fonte": "base_local", "registros": [], "total": 0}
    if resultado_proprios is None:
        resultado_proprios = {"fonte": "proprios", "registros": [], "total": 0}
    if resultado_oficiais is None:
        resultado_oficiais = {"fonte": "tabelas_oficiais", "registros": [], "total": 0}

    # Se base local vazia para filtro, buscar dados gerais
    if resultado_local["total"] == 0 and (filtros.get("tipo") or filtros.get("comarca")):
        print(f"{AMARELO}  Nenhum registro para os filtros específicos. Mostrando dados gerais...{RESET}")
        filtros_gerais = {
            "ano_inicio": filtros.get("ano_inicio"),
            "ano_fim": filtros.get("ano_fim"),
        }
        if filtros.get("tribunal"):
            filtros_gerais["tribunal"] = filtros["tribunal"]
        resultado_local_geral = consultar_base_local(filtros_gerais)
        if resultado_local_geral["total"] > 0:
            resultado_local = resultado_local_geral
            resultado_local["aviso"] = "Dados gerais (filtro específico sem resultados)"

    # Gerar comparativo
    comparativo = gerar_comparativo(
        resultado_local, resultado_proprios, resultado_oficiais, valor_pretendido
    )
    comparativo["filtros"] = filtros

    # Imprimir no terminal
    imprimir_terminal(comparativo, filtros)

    # Saídas opcionais
    if gerar_json_flag:
        salvar_json(comparativo)

    if gerar_rel:
        salvar_md(comparativo, filtros)

    return comparativo


def main():
    """Ponto de entrada CLI."""
    parser = argparse.ArgumentParser(
        description="Pesquisador de Honorários Periciais — Stemmia Forense",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python3 pesquisar_honorarios.py --tipo medica --valor 4000
  python3 pesquisar_honorarios.py --tipo trabalhista --tribunal TRT3 --relatorio
  python3 pesquisar_honorarios.py --tipo erro_medico --comarca "Governador Valadares" --valor 5000 --json
  python3 pesquisar_honorarios.py --tipo bpc_loas --tribunal TRF6 --relatorio --json
        """
    )

    parser.add_argument(
        "--tipo",
        type=str,
        default=None,
        help="Tipo de perícia (medica, erro_medico, trabalhista, securitaria, bpc_loas, curatela, civel)"
    )
    parser.add_argument(
        "--comarca",
        type=str,
        default="Governador Valadares",
        help="Comarca (padrão: Governador Valadares)"
    )
    parser.add_argument(
        "--tribunal",
        type=str,
        default=None,
        help="Tribunal (TJMG, TRT3, TRF6)"
    )
    parser.add_argument(
        "--valor",
        type=float,
        default=None,
        help="Valor que pretende propor (para comparação e semáforo)"
    )
    parser.add_argument(
        "--ano-inicio",
        type=int,
        default=2022,
        help="Ano mínimo (padrão: 2022)"
    )
    parser.add_argument(
        "--ano-fim",
        type=int,
        default=2026,
        help="Ano máximo (padrão: 2026)"
    )
    parser.add_argument(
        "--atualizar",
        action="store_true",
        help="Força busca online (DataJud) antes de consultar (não implementado ainda)"
    )
    parser.add_argument(
        "--relatorio",
        action="store_true",
        help="Gera relatório MD detalhado"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_flag",
        help="Saída JSON"
    )
    parser.add_argument(
        "--salvar",
        action="store_true",
        help="Salva novos registros no SQLite (para uso com --atualizar)"
    )

    args = parser.parse_args()

    if args.atualizar:
        print(f"{AMARELO}  --atualizar: Busca online no DataJud ainda não implementada.{RESET}")
        print(f"{AMARELO}  Consultando apenas base local.{RESET}")
        print()

    filtros = {
        "tipo": args.tipo,
        "comarca": args.comarca,
        "tribunal": args.tribunal,
        "ano_inicio": args.ano_inicio,
        "ano_fim": args.ano_fim,
    }

    pesquisar(
        filtros=filtros,
        valor_pretendido=args.valor,
        gerar_rel=args.relatorio,
        gerar_json_flag=args.json_flag,
        salvar_db=args.salvar,
    )


if __name__ == "__main__":
    main()
