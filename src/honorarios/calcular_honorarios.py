#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculadora de Honorários Periciais — Stemmia Forense

Implementa a fórmula de cálculo de honorários descrita no FLUXO-C-PROPOSTA.md,
com conferências cruzadas obrigatórias e comparativo com base local SQLite.

Uso:
    python3 calcular_honorarios.py --processo /caminho/para/FICHA.json
    python3 calcular_honorarios.py --cnj 5015391-72.2025.8.13.0105
    python3 calcular_honorarios.py --interativo
    python3 calcular_honorarios.py --processo FICHA.json --comparar

Autor: Sistema Stemmia
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES DA FÓRMULA
# ═══════════════════════════════════════════════════════════════════════════════

VALOR_BASE = 2000
VALOR_POR_PAGINA = 15
VALOR_POR_QUESITO = 120
VALOR_POR_ESPECIALIDADE = 400
VALOR_POR_ASSISTENTE = 300

# Adicional por tipo de ação
ADICIONAL_TIPO_ACAO = {
    "previdenciaria":       0,
    "civel_simples":        0,
    "civel_indenizatoria":  500,
    "trabalhista":          500,
    "erro_medico":          1000,
    "securitaria":          500,
}

# Adicional por complexidade (score de 0 a 50)
FAIXAS_COMPLEXIDADE = [
    (10, 0),
    (20, 300),
    (30, 600),
    (40, 1000),
    (50, 1500),
]

# Tabela TJMG 2025 (Portaria 7231/2025)
TJMG_BASE = 585.66
TJMG_MAXIMO = 2928.30  # até 5x

# Faixa aceitável de valor/hora
VALOR_HORA_MIN = 150
VALOR_HORA_MAX = 500

# Caminho do banco SQLite
DB_PATH = Path(__file__).resolve().parent / "dados" / "honorarios.db"

# Raiz dos processos (tenta ambos os caminhos)
PROCESSOS_PATHS = [
    Path.home() / "Desktop" / "ANALISADOR FINAL" / "processos",
    Path.home() / "Desktop" / "ANALISADOR FINAL" / "analisador de processos" / "processos",
]

# ═══════════════════════════════════════════════════════════════════════════════
# MAPEAMENTO DE TIPO DE AÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

def classificar_tipo_acao(area: str, tipo_pericia: str) -> tuple:
    """
    Classifica o tipo de ação a partir dos campos 'area' e 'tipo_pericia' da FICHA.json.
    Retorna (chave_interna, nome_legivel).
    """
    area_lower = (area or "").lower()
    tipo_lower = (tipo_pericia or "").lower()

    # Erro médico
    if "erro" in tipo_lower and "médic" in tipo_lower:
        return "erro_medico", "Erro médico"
    if "erro" in area_lower and "médic" in area_lower:
        return "erro_medico", "Erro médico"
    if "negligên" in tipo_lower or "imperícia" in tipo_lower:
        return "erro_medico", "Erro médico"

    # Securitária
    if "securitária" in area_lower or "seguro" in tipo_lower:
        return "securitaria", "Securitária"

    # Trabalhista / acidentária (TRT)
    if "trabalhista" in area_lower or "acidentária" in area_lower:
        return "trabalhista", "Trabalhista (acidentária)"
    if "insalubridade" in tipo_lower or "periculosidade" in tipo_lower:
        return "trabalhista", "Trabalhista (acidentária)"

    # Previdenciária
    if "previdenciária" in area_lower or "previdenci" in area_lower:
        return "previdenciaria", "Previdenciária"
    if any(x in tipo_lower for x in ["auxílio", "aposentadoria", "bpc", "loas", "b31", "b32", "b36", "b87", "b91", "b92", "b94"]):
        return "previdenciaria", "Previdenciária"

    # Cível indenizatória
    if "indeniza" in tipo_lower or "dano" in tipo_lower or "pensão" in tipo_lower:
        return "civel_indenizatoria", "Cível indenizatória"

    # Cível simples (curatela, interdição, capacidade)
    if any(x in tipo_lower for x in ["curatela", "interdição", "capacidade", "obrigação de fazer"]):
        return "civel_simples", "Cível simples"
    if "cível" in area_lower or "civel" in area_lower:
        # Se chegou aqui sem match mais específico, assume cível simples
        return "civel_simples", "Cível simples"

    # Fallback: previdenciária (tipo mais comum)
    return "previdenciaria", "Previdenciária (presumido)"


def calcular_adicional_complexidade(score: float) -> int:
    """Calcula o adicional baseado no score de complexidade (0-50)."""
    score = max(0, min(50, score))
    for limite, valor in FAIXAS_COMPLEXIDADE:
        if score <= limite:
            return valor
    return FAIXAS_COMPLEXIDADE[-1][1]


def estimar_horas(paginas: int, quesitos: int, especialidades: int, tipo_key: str) -> float:
    """
    Estima horas de trabalho para a perícia.
    Base: 4h (mínimo para qualquer perícia).
    + 0.1h por página relevante
    + 0.5h por quesito
    + 1h por especialidade adicional (além da primeira)
    + bônus por tipo de ação
    """
    horas = 4.0  # base mínima
    horas += paginas * 0.1
    horas += quesitos * 0.5
    horas += max(0, especialidades - 1) * 1.0

    # Bônus por tipo
    bonus_tipo = {
        "erro_medico": 4.0,
        "securitaria": 2.0,
        "trabalhista": 2.0,
        "civel_indenizatoria": 2.0,
        "civel_simples": 0.0,
        "previdenciaria": 0.0,
    }
    horas += bonus_tipo.get(tipo_key, 0.0)
    return round(horas, 1)


def arredondar_multiplo_500(valor: float) -> int:
    """Arredonda para o múltiplo de R$ 500 mais próximo."""
    return int(round(valor / 500) * 500)


# ═══════════════════════════════════════════════════════════════════════════════
# BUSCA DE FICHA.JSON POR CNJ
# ═══════════════════════════════════════════════════════════════════════════════

def buscar_ficha_por_cnj(cnj: str) -> Path | None:
    """Busca FICHA.json em todas as pastas de processos pelo número CNJ."""
    for base in PROCESSOS_PATHS:
        if not base.exists():
            continue
        for pasta in base.iterdir():
            if not pasta.is_dir():
                continue
            ficha = pasta / "FICHA.json"
            if ficha.exists():
                try:
                    dados = json.loads(ficha.read_text(encoding="utf-8"))
                    if dados.get("numero_cnj") == cnj:
                        return ficha
                except (json.JSONDecodeError, OSError):
                    continue
            # Também verificar se o CNJ está no nome da pasta
            if cnj in pasta.name:
                if ficha.exists():
                    return ficha
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# CONSULTA À BASE LOCAL (SQLite)
# ═══════════════════════════════════════════════════════════════════════════════

def consultar_base_local(tipo_key: str, tipo_pericia: str, comarca: str, valor_bruto: float) -> dict:
    """
    Consulta a base local de honorários para calcular o percentil
    do valor proposto em relação a perícias similares.

    Retorna dict com: valores, percentil, media, mediana, status.
    """
    resultado = {
        "valores": [],
        "percentil": None,
        "media": None,
        "mediana": None,
        "status": "sem_dados",
        "total_registros": 0,
    }

    if not DB_PATH.exists():
        resultado["status"] = "banco_nao_encontrado"
        return resultado

    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Buscar em honorários coletados + próprios
        valores = []

        # Mapear tipo_key para tipo_pericia do banco coletados
        mapa_coletados = {
            "previdenciaria": ["BPC/LOAS", "Gratuidade"],
            "civel_simples": ["Civel"],
            "civel_indenizatoria": ["Civel"],
            "trabalhista": ["Trabalhista", "Ocupacional", "Insalubridade"],
            "erro_medico": ["Erro Médico"],
            "securitaria": ["Civel"],
        }

        tipos_busca = mapa_coletados.get(tipo_key, [])
        if tipos_busca:
            placeholders = ",".join(["?" for _ in tipos_busca])
            query = f"""
                SELECT valor_fixado FROM honorarios_coletados
                WHERE tipo_pericia IN ({placeholders})
                AND valor_fixado > 0
            """
            cursor.execute(query, tipos_busca)
            valores.extend([row[0] for row in cursor.fetchall()])

        # Buscar nos próprios (pela comarca, se possível)
        cursor.execute("""
            SELECT valor_fixado FROM honorarios_proprios
            WHERE valor_fixado > 0
        """)
        valores.extend([row[0] for row in cursor.fetchall()])

        # Se não tem dados fixados, buscar propostos
        if not valores:
            if tipos_busca:
                placeholders = ",".join(["?" for _ in tipos_busca])
                query = f"""
                    SELECT valor_proposto FROM honorarios_coletados
                    WHERE tipo_pericia IN ({placeholders})
                    AND valor_proposto > 0
                """
                cursor.execute(query, tipos_busca)
                valores.extend([row[0] for row in cursor.fetchall()])

            cursor.execute("""
                SELECT valor_proposto FROM honorarios_proprios
                WHERE valor_proposto > 0
            """)
            valores.extend([row[0] for row in cursor.fetchall()])

        conn.close()

        if not valores:
            return resultado

        valores.sort()
        resultado["valores"] = valores
        resultado["total_registros"] = len(valores)
        resultado["media"] = round(sum(valores) / len(valores), 2)

        # Mediana
        n = len(valores)
        if n % 2 == 0:
            resultado["mediana"] = round((valores[n // 2 - 1] + valores[n // 2]) / 2, 2)
        else:
            resultado["mediana"] = valores[n // 2]

        # Percentil
        abaixo = sum(1 for v in valores if v < valor_bruto)
        resultado["percentil"] = round((abaixo / len(valores)) * 100)

        # Status
        if resultado["percentil"] <= 25:
            resultado["status"] = "abaixo_da_media"
        elif resultado["percentil"] <= 75:
            resultado["status"] = "ok"
        else:
            resultado["status"] = "acima_da_media"

        return resultado

    except sqlite3.Error as e:
        resultado["status"] = f"erro_banco: {e}"
        return resultado


# ═══════════════════════════════════════════════════════════════════════════════
# MODO INTERATIVO
# ═══════════════════════════════════════════════════════════════════════════════

def perguntar_int(prompt: str, default: int = 0) -> int:
    """Pergunta um inteiro ao usuário, com valor padrão."""
    try:
        resp = input(f"  {prompt} [{default}]: ").strip()
        return int(resp) if resp else default
    except (ValueError, EOFError):
        return default


def perguntar_float(prompt: str, default: float = 0.0) -> float:
    """Pergunta um float ao usuário, com valor padrão."""
    try:
        resp = input(f"  {prompt} [{default}]: ").strip()
        return float(resp) if resp else default
    except (ValueError, EOFError):
        return default


def perguntar_texto(prompt: str, default: str = "") -> str:
    """Pergunta texto ao usuário, com valor padrão."""
    try:
        resp = input(f"  {prompt} [{default}]: ").strip()
        return resp if resp else default
    except EOFError:
        return default


def escolher_tipo_acao() -> tuple:
    """Menu interativo para escolher o tipo de ação."""
    opcoes = [
        ("previdenciaria", "Previdenciária (BPC/LOAS, auxílio)"),
        ("civel_simples", "Cível simples (curatela, interdição)"),
        ("civel_indenizatoria", "Cível indenizatória"),
        ("trabalhista", "Trabalhista (acidentária)"),
        ("erro_medico", "Erro médico"),
        ("securitaria", "Securitária"),
    ]
    print("\n  Tipo de ação:")
    for i, (_, nome) in enumerate(opcoes, 1):
        print(f"    {i}) {nome}")
    try:
        resp = input("  Escolha [1]: ").strip()
        idx = int(resp) - 1 if resp else 0
        if 0 <= idx < len(opcoes):
            return opcoes[idx]
    except (ValueError, EOFError):
        pass
    return opcoes[0]


# ═══════════════════════════════════════════════════════════════════════════════
# CÁLCULO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def calcular_honorarios(
    paginas: int,
    quesitos: int,
    especialidades: int,
    assistentes: int,
    tipo_key: str,
    score_complexidade: float,
) -> dict:
    """
    Aplica a fórmula de cálculo e retorna dicionário com todos os fatores.

    Fórmula:
        Base + (páginas x 15) + (quesitos x 120) + (especialidades x 400)
        + (assistentes x 300) + adicional tipo + adicional complexidade
    """
    valor_paginas = paginas * VALOR_POR_PAGINA
    valor_quesitos = quesitos * VALOR_POR_QUESITO
    valor_especialidades = especialidades * VALOR_POR_ESPECIALIDADE
    valor_assistentes = assistentes * VALOR_POR_ASSISTENTE
    valor_tipo = ADICIONAL_TIPO_ACAO.get(tipo_key, 0)
    valor_complexidade = calcular_adicional_complexidade(score_complexidade)

    valor_bruto = (
        VALOR_BASE
        + valor_paginas
        + valor_quesitos
        + valor_especialidades
        + valor_assistentes
        + valor_tipo
        + valor_complexidade
    )

    return {
        "base": VALOR_BASE,
        "paginas": {"qtd": paginas, "valor": valor_paginas},
        "quesitos": {"qtd": quesitos, "valor": valor_quesitos},
        "especialidades": {"qtd": especialidades, "valor": valor_especialidades},
        "assistentes": {"qtd": assistentes, "valor": valor_assistentes},
        "tipo_acao": {"tipo_key": tipo_key, "valor": valor_tipo},
        "complexidade": {"score": score_complexidade, "valor": valor_complexidade},
        "valor_bruto": valor_bruto,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CONFERÊNCIAS CRUZADAS
# ═══════════════════════════════════════════════════════════════════════════════

def conferencias_cruzadas(
    valor_bruto: float,
    horas_estimadas: float,
    valor_causa: float | None,
    tipo_key: str,
    tipo_pericia: str,
    comarca: str,
    comparar_base: bool = False,
) -> dict:
    """Executa as 4 conferências cruzadas obrigatórias."""
    conferencias = {}

    # 1. Valor/hora
    valor_hora = round(valor_bruto / horas_estimadas, 2) if horas_estimadas > 0 else 0
    if VALOR_HORA_MIN <= valor_hora <= VALOR_HORA_MAX:
        status_hora = "ok"
    elif valor_hora < VALOR_HORA_MIN:
        status_hora = "abaixo"
    else:
        status_hora = "acima"
    conferencias["valor_hora"] = {
        "valor": valor_hora,
        "horas_estimadas": horas_estimadas,
        "faixa": f"R${VALOR_HORA_MIN}-{VALOR_HORA_MAX}",
        "status": status_hora,
    }

    # 2. Tabela TJMG 2025
    if valor_bruto <= TJMG_MAXIMO:
        status_tjmg = "dentro_tabela"
    else:
        status_tjmg = "majoracao"
    conferencias["tabela_tjmg"] = {
        "referencia_base": TJMG_BASE,
        "referencia_maxima": TJMG_MAXIMO,
        "status": status_tjmg,
    }

    # 3. 5% do valor da causa
    if valor_causa and valor_causa > 0:
        percentual = round((valor_bruto / valor_causa) * 100, 2)
        if percentual <= 5:
            status_causa = "ok"
        else:
            status_causa = "alerta"
        conferencias["valor_causa"] = {
            "valor_causa": valor_causa,
            "percentual": percentual,
            "status": status_causa,
        }
    else:
        conferencias["valor_causa"] = {
            "valor_causa": None,
            "percentual": None,
            "status": "nao_informado",
        }

    # 4. Base local (SQLite)
    if comparar_base:
        resultado_base = consultar_base_local(tipo_key, tipo_pericia, comarca, valor_bruto)
        conferencias["base_local"] = {
            "percentil": resultado_base["percentil"],
            "media": resultado_base["media"],
            "mediana": resultado_base["mediana"],
            "total_registros": resultado_base["total_registros"],
            "status": resultado_base["status"],
        }
    else:
        conferencias["base_local"] = {
            "percentil": None,
            "status": "nao_consultado",
        }

    return conferencias


# ═══════════════════════════════════════════════════════════════════════════════
# FORMATAÇÃO DE SAÍDA NO TERMINAL
# ═══════════════════════════════════════════════════════════════════════════════

def formatar_moeda(valor: float) -> str:
    """Formata valor como R$ X.XXX."""
    if valor >= 1000:
        return f"R$ {valor:,.0f}".replace(",", ".")
    return f"R$ {valor:,.0f}".replace(",", ".")


def imprimir_resultado(
    ficha: dict,
    fatores: dict,
    tipo_nome: str,
    horas_estimadas: float,
    valor_sugerido: int,
    conferencias: dict,
):
    """Imprime o resultado formatado no terminal."""
    # Cabeçalho
    num_pericia = ficha.get("numero_pericia", "?")
    cidade = ficha.get("cidade", ficha.get("comarca", "?"))
    vara = ficha.get("vara", "?")
    cnj = ficha.get("numero_cnj", "?")

    titulo_pericia = f"Perícia {num_pericia} | {cidade} | {vara}"

    print()
    print("+" + "=" * 57 + "+")
    print("|  CALCULADORA DE HONORÁRIOS — Stemmia" + " " * 20 + "|")
    print("+" + "=" * 57 + "+")
    print(f"|  {titulo_pericia:<55}|")
    print(f"|  CNJ: {cnj:<51}|")
    print("+" + "=" * 57 + "+")
    print()

    # Fatores de cálculo
    valor_bruto = fatores["valor_bruto"]
    COL1 = 34  # largura da coluna de nomes

    print("  FATORES DE CÁLCULO")
    print("  +" + "-" * (COL1 + 2) + "+" + "-" * 9 + "+" + "-" * 12 + "+")
    print(f"  | {'Fator':<{COL1}} | {'Qtd':>7} | {'Valor':>10} |")
    print("  +" + "-" * (COL1 + 2) + "+" + "-" * 9 + "+" + "-" * 12 + "+")

    # Truncar tipo_nome se necessário para caber na coluna
    tipo_display = tipo_nome if len(tipo_nome) <= 18 else tipo_nome[:18]
    linhas = [
        ("Base", "-", fatores["base"]),
        ("Páginas relevantes", str(fatores["paginas"]["qtd"]), fatores["paginas"]["valor"]),
        ("Quesitos", str(fatores["quesitos"]["qtd"]), fatores["quesitos"]["valor"]),
        ("Especialidades médicas", str(fatores["especialidades"]["qtd"]), fatores["especialidades"]["valor"]),
        ("Assistentes técnicos", str(fatores["assistentes"]["qtd"]), fatores["assistentes"]["valor"]),
        (f"Adicional tipo ({tipo_display})", "-", fatores["tipo_acao"]["valor"]),
        ("Adicional complexidade", f"{int(fatores['complexidade']['score'])}/50", fatores["complexidade"]["valor"]),
    ]

    for nome, qtd, valor in linhas:
        nome_trunc = nome[:COL1]
        print(f"  | {nome_trunc:<{COL1}} | {qtd:>7} | {formatar_moeda(valor):>10} |")

    print("  +" + "-" * (COL1 + 2) + "+" + "-" * 9 + "+" + "-" * 12 + "+")
    print(f"  | {'TOTAL':<{COL1}} | {'':>7} | {formatar_moeda(valor_bruto):>10} |")
    print("  +" + "-" * (COL1 + 2) + "+" + "-" * 9 + "+" + "-" * 12 + "+")
    print()

    # Conferências cruzadas
    print("  CONFERÊNCIAS CRUZADAS")

    # Valor/hora
    vh = conferencias["valor_hora"]
    icone = "OK" if vh["status"] == "ok" else "!!"
    print(f"    [{icone}] Valor/hora: {formatar_moeda(vh['valor'])}/h ({vh['horas_estimadas']}h estimadas) — {vh['faixa']}")

    # Tabela TJMG
    tj = conferencias["tabela_tjmg"]
    if tj["status"] == "dentro_tabela":
        print(f"    [OK] Tabela TJMG: {formatar_moeda(valor_bruto)} <= {formatar_moeda(tj['referencia_maxima'])} — Dentro da tabela")
    else:
        print(f"    [!!] Tabela TJMG: {formatar_moeda(valor_bruto)} > {formatar_moeda(tj['referencia_maxima'])} — Precisa fundamentar majoração")

    # 5% valor da causa
    vc = conferencias["valor_causa"]
    if vc["status"] == "nao_informado":
        print(f"    [??] 5% valor da causa: valor da causa não informado — Verificar manualmente")
    elif vc["status"] == "ok":
        print(f"    [OK] 5% valor da causa: {vc['percentual']}% ({formatar_moeda(vc['valor_causa'])}) — OK")
    else:
        print(f"    [!!] 5% valor da causa: {vc['percentual']}% ({formatar_moeda(vc['valor_causa'])}) — Acima de 5%!")

    # Base local
    bl = conferencias["base_local"]
    if bl["status"] == "nao_consultado":
        print(f"    [--] Base local: não consultada (use --comparar)")
    elif bl["status"] == "sem_dados":
        print(f"    [??] Base local: sem dados suficientes para comparação")
    elif bl["status"] == "banco_nao_encontrado":
        print(f"    [!!] Base local: banco honorarios.db não encontrado")
    elif "erro_banco" in bl["status"]:
        print(f"    [!!] Base local: {bl['status']}")
    else:
        p = bl["percentil"]
        status_txt = {
            "ok": "dentro da faixa",
            "abaixo_da_media": "abaixo da média (considere aumentar)",
            "acima_da_media": "acima da média (revisar fundamentação)",
        }.get(bl["status"], bl["status"])
        media_str = formatar_moeda(bl["media"]) if bl["media"] else "?"
        mediana_str = formatar_moeda(bl["mediana"]) if bl["mediana"] else "?"
        print(f"    [{'OK' if bl['status'] == 'ok' else '!!'}] Base local: percentil {p}, média {media_str}, mediana {mediana_str} ({bl['total_registros']} registros) — {status_txt}")

    print()
    print(f"  VALOR BRUTO:    {formatar_moeda(valor_bruto)}")
    print(f"  VALOR SUGERIDO: {formatar_moeda(valor_sugerido)}")
    print(f"  (arredondado para múltiplo de R$ 500)")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# SALVAR JSON
# ═══════════════════════════════════════════════════════════════════════════════

def salvar_json(
    ficha: dict,
    fatores: dict,
    tipo_nome: str,
    horas_estimadas: float,
    valor_sugerido: int,
    conferencias: dict,
    pasta_processo: Path | None,
):
    """Salva calculo-honorarios.json na pasta do processo."""
    saida = {
        "numero_cnj": ficha.get("numero_cnj", ""),
        "numero_pericia": ficha.get("numero_pericia", ""),
        "comarca": ficha.get("comarca", ficha.get("cidade", "")),
        "vara": ficha.get("vara", ""),
        "data_calculo": datetime.now().isoformat(),
        "fatores": {
            "base": fatores["base"],
            "paginas": fatores["paginas"],
            "quesitos": fatores["quesitos"],
            "especialidades": fatores["especialidades"],
            "assistentes": fatores["assistentes"],
            "tipo_acao": {"tipo": tipo_nome, "valor": fatores["tipo_acao"]["valor"]},
            "complexidade": {
                "score": fatores["complexidade"]["score"],
                "valor": fatores["complexidade"]["valor"],
            },
        },
        "valor_bruto": fatores["valor_bruto"],
        "valor_sugerido": valor_sugerido,
        "horas_estimadas": horas_estimadas,
        "conferencias": conferencias,
    }

    # Determinar onde salvar
    if pasta_processo and pasta_processo.is_dir():
        destino = pasta_processo / "calculo-honorarios.json"
    elif pasta_processo and pasta_processo.is_file():
        destino = pasta_processo.parent / "calculo-honorarios.json"
    else:
        destino = Path.cwd() / "calculo-honorarios.json"

    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Salvo em: {destino}")
    print()

    return destino


# ═══════════════════════════════════════════════════════════════════════════════
# FLUXO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Calculadora de Honorários Periciais — Stemmia Forense",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python3 calcular_honorarios.py --processo ~/Desktop/ANALISADOR\\ FINAL/processos/Perícia\\ 14/FICHA.json
  python3 calcular_honorarios.py --cnj 5015391-72.2025.8.13.0105
  python3 calcular_honorarios.py --interativo --comparar
  python3 calcular_honorarios.py --processo FICHA.json --paginas 60 --quesitos 15
        """,
    )
    parser.add_argument("--processo", type=str, help="Caminho para FICHA.json do processo")
    parser.add_argument("--cnj", type=str, help="Número CNJ (busca FICHA.json automaticamente)")
    parser.add_argument("--paginas", type=int, default=None, help="Páginas relevantes (override manual)")
    parser.add_argument("--quesitos", type=int, default=None, help="Número de quesitos (override manual)")
    parser.add_argument("--interativo", action="store_true", help="Modo interativo (pergunta cada valor)")
    parser.add_argument("--comparar", action="store_true", help="Compara com base local automaticamente")
    parser.add_argument("--valor-causa", type=float, default=None, help="Valor da causa (para conferência de 5%%)")
    parser.add_argument("--assistentes", type=int, default=None, help="Número de assistentes técnicos")
    parser.add_argument("--score", type=float, default=None, help="Score de complexidade (0-50)")

    args = parser.parse_args()

    ficha = {}
    pasta_processo = None

    # ─── Carregar FICHA.json ───────────────────────────────────────────────
    if args.processo:
        caminho = Path(args.processo).expanduser().resolve()
        if caminho.is_dir():
            caminho = caminho / "FICHA.json"
        if not caminho.exists():
            print(f"  ERRO: Arquivo não encontrado: {caminho}")
            sys.exit(1)
        try:
            ficha = json.loads(caminho.read_text(encoding="utf-8"))
            pasta_processo = caminho.parent
        except json.JSONDecodeError as e:
            print(f"  ERRO: JSON inválido em {caminho}: {e}")
            sys.exit(1)

    elif args.cnj:
        caminho = buscar_ficha_por_cnj(args.cnj)
        if caminho:
            ficha = json.loads(caminho.read_text(encoding="utf-8"))
            pasta_processo = caminho.parent
            print(f"  FICHA encontrada: {caminho}")
        else:
            print(f"  AVISO: FICHA.json não encontrada para CNJ {args.cnj}")
            ficha = {"numero_cnj": args.cnj}

    elif args.interativo:
        print("\n  Modo interativo — informe os dados da perícia:\n")
        ficha["numero_cnj"] = perguntar_texto("Número CNJ")
        ficha["numero_pericia"] = perguntar_int("Número da perícia")
        ficha["comarca"] = perguntar_texto("Comarca")
        ficha["vara"] = perguntar_texto("Vara")

    else:
        # Verificar se há FICHA.json no diretório atual
        ficha_local = Path.cwd() / "FICHA.json"
        if ficha_local.exists():
            try:
                ficha = json.loads(ficha_local.read_text(encoding="utf-8"))
                pasta_processo = ficha_local.parent
                print(f"  FICHA encontrada no diretório atual: {ficha_local}")
            except json.JSONDecodeError:
                pass
        if not ficha:
            parser.print_help()
            print("\n  ERRO: Informe --processo, --cnj ou --interativo")
            sys.exit(1)

    # ─── Extrair dados da FICHA ────────────────────────────────────────────
    area = ficha.get("area", "")
    tipo_pericia = ficha.get("tipo_pericia", "")
    areas_medicas = ficha.get("areas_medicas", [])
    if isinstance(areas_medicas, str):
        try:
            areas_medicas = json.loads(areas_medicas)
        except json.JSONDecodeError:
            areas_medicas = [areas_medicas] if areas_medicas else []

    # Classificar tipo de ação
    tipo_key, tipo_nome = classificar_tipo_acao(area, tipo_pericia)

    # Valores com override e fallback
    paginas = args.paginas if args.paginas is not None else ficha.get("num_paginas", 0)
    quesitos = args.quesitos if args.quesitos is not None else ficha.get("num_quesitos", 0)
    especialidades = len(areas_medicas) if areas_medicas else ficha.get("num_especialidades", 1)
    assistentes = args.assistentes if args.assistentes is not None else ficha.get("num_assistentes", 0)
    score = args.score if args.score is not None else ficha.get("score_complexidade", 0)
    valor_causa = args.valor_causa if args.valor_causa is not None else ficha.get("valor_causa", None)

    # ─── Modo interativo: preencher campos faltantes ───────────────────────
    if args.interativo:
        print(f"\n  Tipo de ação detectado: {tipo_nome}")
        resp = perguntar_texto("Alterar tipo? (s/N)", "n")
        if resp.lower() in ("s", "sim"):
            tipo_key, tipo_nome = escolher_tipo_acao()

        if paginas == 0:
            paginas = perguntar_int("Páginas relevantes", 20)
        else:
            novo = perguntar_int(f"Páginas relevantes (atual: {paginas})", paginas)
            paginas = novo

        if quesitos == 0:
            quesitos = perguntar_int("Número de quesitos", 8)
        else:
            novo = perguntar_int(f"Número de quesitos (atual: {quesitos})", quesitos)
            quesitos = novo

        novo = perguntar_int(f"Especialidades médicas (atual: {especialidades})", especialidades)
        especialidades = novo

        novo = perguntar_int(f"Assistentes técnicos (atual: {assistentes})", assistentes)
        assistentes = novo

        if score == 0:
            score = perguntar_float("Score de complexidade (0-50)", 15)
        else:
            novo = perguntar_float(f"Score de complexidade (atual: {score})", score)
            score = novo

        if valor_causa is None:
            resp = perguntar_texto("Valor da causa (deixe vazio se não houver)", "")
            if resp:
                try:
                    valor_causa = float(resp.replace(".", "").replace(",", "."))
                except ValueError:
                    valor_causa = None

    # Garantir mínimos razoáveis quando não há dados
    if paginas == 0 and not args.interativo:
        paginas = 20  # default razoável
    if quesitos == 0 and not args.interativo:
        quesitos = 8  # default razoável
    if especialidades == 0:
        especialidades = 1
    if score == 0 and not args.interativo:
        score = 15  # default razoável (complexidade média-baixa)

    # ─── Calcular ──────────────────────────────────────────────────────────
    fatores = calcular_honorarios(
        paginas=paginas,
        quesitos=quesitos,
        especialidades=especialidades,
        assistentes=assistentes,
        tipo_key=tipo_key,
        score_complexidade=score,
    )

    valor_bruto = fatores["valor_bruto"]
    valor_sugerido = arredondar_multiplo_500(valor_bruto)

    # Horas estimadas
    horas_estimadas = estimar_horas(paginas, quesitos, especialidades, tipo_key)

    # ─── Conferências cruzadas ─────────────────────────────────────────────
    conferencias = conferencias_cruzadas(
        valor_bruto=valor_bruto,
        horas_estimadas=horas_estimadas,
        valor_causa=valor_causa,
        tipo_key=tipo_key,
        tipo_pericia=tipo_pericia,
        comarca=ficha.get("comarca", ficha.get("cidade", "")),
        comparar_base=args.comparar,
    )

    # ─── Saída ─────────────────────────────────────────────────────────────
    imprimir_resultado(ficha, fatores, tipo_nome, horas_estimadas, valor_sugerido, conferencias)
    salvar_json(ficha, fatores, tipo_nome, horas_estimadas, valor_sugerido, conferencias, pasta_processo)


if __name__ == "__main__":
    main()
