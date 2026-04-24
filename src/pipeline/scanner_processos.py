#!/usr/bin/env python3
"""
Scanner de Processos — Stemmia Forense
Varre todas as pastas de processo e classifica o estado de cada um.
Gera STATUS-PROCESSOS.json na raiz do ANALISADOR FINAL.

Uso:
    python3 scanner_processos.py
    python3 scanner_processos.py --resumo     # Mostra resumo no terminal
    python3 scanner_processos.py --json-only  # Só gera JSON, sem output
"""

import os
import sys
import json
import re
import glob
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(os.path.expanduser("~/Desktop/ANALISADOR FINAL"))
PROCESSOS_DIR = BASE_DIR / "processos"
OUTPUT_JSON = BASE_DIR / "STATUS-PROCESSOS.json"

# Padrão CNJ: 7 dígitos - 2 dígitos . 4 dígitos . 1 dígito . 2 dígitos . 4 dígitos
CNJ_PATTERN = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')

# Padrão pasta Perícia
PERICIA_PATTERN = re.compile(r'^Perícia\s+(\d+|\?\?)\s*-\s*(.+?)(?:\s*-\s*(.+))?$')


def extrair_cnj_da_pasta(nome_pasta):
    """Extrai número CNJ do nome da pasta."""
    match = CNJ_PATTERN.search(nome_pasta)
    return match.group(0) if match else None


def extrair_info_pericia(nome_pasta):
    """Extrai número e cidade de pasta tipo 'Perícia XX - Cidade - Vara'."""
    match = PERICIA_PATTERN.match(nome_pasta)
    if match:
        return {
            "numero_pericia": match.group(1),
            "cidade": match.group(2).strip() if match.group(2) else "",
            "vara": match.group(3).strip() if match.group(3) else ""
        }
    return None


def detectar_arquivos(pasta):
    """Detecta quais arquivos/artefatos existem na pasta do processo."""
    resultado = {
        "texto_extraido": False,
        "analise": False,
        "resumo": False,
        "proposta": False,
        "aceite": False,
        "agendamento": False,
        "laudo": False,
        "contestacao": False,
        "verificacoes": [],
        "verificacao_html": False,
        "ficha_json": False,
        "processo_pdf": False,
        "argumentos": False,
        "partes": False,
        "timeline": False,
        "classificacao": False,
        "urgencia": False,
        "score_complexidade": False,
    }

    if not pasta.exists():
        return resultado

    # Listar tudo na pasta (raiz e subpastas conhecidas)
    arquivos_raiz = set()
    for item in pasta.iterdir():
        arquivos_raiz.add(item.name.upper())

    # Subpasta petições/
    peticoes_dir = pasta / "petições"
    arquivos_peticoes = set()
    if peticoes_dir.exists():
        for item in peticoes_dir.iterdir():
            arquivos_peticoes.add(item.name.upper())

    # Subpasta verificações/
    verificacoes_dir = pasta / "verificações"
    arquivos_verificacoes = set()
    if verificacoes_dir.exists():
        for item in verificacoes_dir.iterdir():
            arquivos_verificacoes.add(item.name.upper())

    todos = arquivos_raiz | arquivos_peticoes | arquivos_verificacoes

    # Texto extraído
    resultado["texto_extraido"] = any(
        "TEXTO-EXTRAIDO" in a or "TEXTO_EXTRAIDO" in a for a in todos
    )

    # Análise
    resultado["analise"] = any(
        a.startswith("ANALISE") and (a.endswith(".MD") or a.endswith(".PDF"))
        for a in todos
    ) or any("RESUMO-ANALISE" in a for a in todos)

    # Resumo rápido
    resultado["resumo"] = any(
        "RESUMO" in a for a in todos
    )

    # Proposta
    resultado["proposta"] = any(
        "PROPOSTA" in a for a in todos
    ) or any(
        "DADOS-PROPOSTA" in a or "RELATORIO-DADOS-PROPOSTA" in a for a in todos
    )

    # Aceite
    resultado["aceite"] = any(
        "ACEITE" in a for a in todos
    )

    # Agendamento
    resultado["agendamento"] = any(
        "AGENDAMENTO" in a for a in todos
    )

    # Laudo
    resultado["laudo"] = any(
        "LAUDO" in a for a in todos
    )

    # Contestação
    resultado["contestacao"] = any(
        "CONTESTACAO" in a or "CONTESTAÇÃO" in a or "IMPUGNACAO" in a or "IMPUGNAÇÃO" in a
        for a in todos
    )

    # Verificações específicas
    verificacoes_encontradas = []
    for a in todos:
        if a.startswith("VERIFICACAO-") or a.startswith("VERIFICAÇÃO-"):
            verificacoes_encontradas.append(a)
    resultado["verificacoes"] = verificacoes_encontradas

    # Verificação HTML (verificador-100)
    resultado["verificacao_html"] = any(
        a.startswith("VERIFICACAO") and a.endswith(".HTML") for a in todos
    )

    # FICHA.json
    resultado["ficha_json"] = "FICHA.JSON" in arquivos_raiz

    # PDF do processo
    resultado["processo_pdf"] = any(
        a.endswith(".PDF") and ("PROCESSO" in a or "ORIGINAL" in a)
        for a in arquivos_raiz
    )

    # Argumentos
    resultado["argumentos"] = any(
        a.startswith("ARGUMENTOS") for a in arquivos_raiz
    )

    # Partes
    resultado["partes"] = "PARTES.JSON" in arquivos_raiz or "PARTES.MD" in arquivos_raiz

    # Timeline
    resultado["timeline"] = "TIMELINE.JSON" in arquivos_raiz or "TIMELINE.MD" in arquivos_raiz

    # Classificação
    resultado["classificacao"] = "CLASSIFICACAO.JSON" in arquivos_raiz or "CLASSIFICACAO.MD" in arquivos_raiz

    # Urgência
    resultado["urgencia"] = "URGENCIA.JSON" in arquivos_raiz or "URGENCIA.MD" in arquivos_raiz

    # Score complexidade
    resultado["score_complexidade"] = any(
        "SCORE" in a or "COMPLEXIDADE" in a for a in arquivos_raiz
    )

    return resultado


def classificar_estado(arquivos):
    """Classifica o estado do processo baseado nos arquivos encontrados."""
    if arquivos["laudo"]:
        return "COMPLETO"

    if arquivos["contestacao"]:
        return "EM-CONTESTAÇÃO"

    if arquivos["aceite"] and not arquivos["laudo"]:
        if arquivos["agendamento"]:
            return "PENDENTE-LAUDO"
        return "PENDENTE-AGENDAMENTO"

    if arquivos["proposta"] and not arquivos["aceite"]:
        return "PENDENTE-ACEITE"

    if arquivos["analise"] and not arquivos["proposta"]:
        return "PENDENTE-PROPOSTA"

    if arquivos["texto_extraido"] and not arquivos["analise"]:
        return "PENDENTE-ANÁLISE"

    if arquivos["processo_pdf"] and not arquivos["texto_extraido"]:
        return "PENDENTE-EXTRAÇÃO"

    if arquivos["ficha_json"] and not arquivos["texto_extraido"] and not arquivos["processo_pdf"]:
        return "PENDENTE-PDF"

    if not any([
        arquivos["texto_extraido"], arquivos["analise"], arquivos["proposta"],
        arquivos["aceite"], arquivos["laudo"], arquivos["processo_pdf"]
    ]):
        return "VAZIO"

    return "INDEFINIDO"


def determinar_proxima_acao(estado):
    """Retorna a próxima ação recomendada."""
    acoes = {
        "PENDENTE-PDF": "Colocar PDF do processo na pasta",
        "PENDENTE-EXTRAÇÃO": "Extrair texto do PDF com pdftotext",
        "PENDENTE-ANÁLISE": "Rodar análise completa (/cowork ou análise rápida)",
        "PENDENTE-PROPOSTA": "Gerar proposta de honorários (/proposta)",
        "PENDENTE-ACEITE": "Gerar petição de aceite (/aceite)",
        "PENDENTE-AGENDAMENTO": "Gerar petição de agendamento (/agendar)",
        "PENDENTE-LAUDO": "Elaborar laudo pericial",
        "EM-CONTESTAÇÃO": "Responder contestação (/contestar)",
        "COMPLETO": "Nenhuma — processo concluído",
        "VAZIO": "Iniciar processamento — colocar PDF ou rodar /nomeacao",
        "INDEFINIDO": "Verificar manualmente a pasta",
    }
    return acoes.get(estado, "Verificar manualmente")


def ler_ficha_json(pasta):
    """Lê FICHA.json se existir e retorna dados úteis."""
    ficha_path = pasta / "FICHA.json"
    if ficha_path.exists():
        try:
            with open(ficha_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {
                "numero_pericia": data.get("numero_pericia", ""),
                "cidade": data.get("cidade", ""),
                "vara": data.get("vara", ""),
                "area": data.get("area", ""),
                "tipo_pericia": data.get("tipo_pericia", ""),
                "objeto": data.get("objeto", ""),
                "status_ficha": data.get("status", ""),
                "etapa_ficha": data.get("etapa_atual", ""),
                "data_nomeacao": data.get("data_nomeacao", ""),
                "honorarios_valor": data.get("honorarios", {}).get("valor", 0),
                "honorarios_status": data.get("honorarios", {}).get("status", ""),
            }
        except (json.JSONDecodeError, KeyError):
            return {}
    return {}


def contar_arquivos_pasta(pasta):
    """Conta total de arquivos na pasta (recursivo)."""
    total = 0
    if pasta.exists():
        for _ in pasta.rglob("*"):
            if _.is_file():
                total += 1
    return total


def scanear():
    """Função principal de scan."""
    if not PROCESSOS_DIR.exists():
        print(f"ERRO: Pasta não encontrada: {PROCESSOS_DIR}")
        sys.exit(1)

    processos = []
    cnjs_vistos = {}  # Para detectar duplicatas (CNJ → pasta principal)

    for item in sorted(PROCESSOS_DIR.iterdir()):
        if not item.is_dir():
            continue
        if item.name.startswith('.'):
            continue

        nome = item.name
        cnj = extrair_cnj_da_pasta(nome)
        info_pericia = extrair_info_pericia(nome)
        is_pericia_folder = info_pericia is not None

        # Detectar arquivos
        arquivos = detectar_arquivos(item)

        # Classificar estado
        estado = classificar_estado(arquivos)

        # Ler FICHA.json
        ficha = ler_ficha_json(item)

        # Contar arquivos
        total_arquivos = contar_arquivos_pasta(item)

        # Montar registro
        registro = {
            "pasta": nome,
            "caminho": str(item),
            "cnj": cnj or ficha.get("numero_cnj", ""),
            "estado": estado,
            "proxima_acao": determinar_proxima_acao(estado),
            "is_pericia_folder": is_pericia_folder,
            "total_arquivos": total_arquivos,
            "arquivos": {
                "texto_extraido": arquivos["texto_extraido"],
                "analise": arquivos["analise"],
                "proposta": arquivos["proposta"],
                "aceite": arquivos["aceite"],
                "agendamento": arquivos["agendamento"],
                "laudo": arquivos["laudo"],
                "contestacao": arquivos["contestacao"],
                "verificacao_html": arquivos["verificacao_html"],
                "verificacoes": len(arquivos["verificacoes"]),
                "ficha_json": arquivos["ficha_json"],
                "processo_pdf": arquivos["processo_pdf"],
                "partes": arquivos["partes"],
                "timeline": arquivos["timeline"],
                "classificacao": arquivos["classificacao"],
            },
        }

        if info_pericia:
            registro["pericia"] = info_pericia

        if ficha:
            registro["ficha"] = ficha

        # Detectar duplicata
        if cnj:
            if cnj in cnjs_vistos:
                registro["duplicata_de"] = cnjs_vistos[cnj]
            else:
                cnjs_vistos[cnj] = nome

        processos.append(registro)

    # Estatísticas
    estados = {}
    for p in processos:
        est = p["estado"]
        estados[est] = estados.get(est, 0) + 1

    resultado = {
        "data_scan": datetime.now().isoformat(),
        "total_pastas": len(processos),
        "total_cnjs_unicos": len(cnjs_vistos),
        "estatisticas": estados,
        "processos": processos,
    }

    # Salvar JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado


def mostrar_resumo(resultado):
    """Mostra resumo no terminal."""
    print("=" * 50)
    print("SCANNER DE PROCESSOS — STEMMIA FORENSE")
    print("=" * 50)
    print(f"Data: {resultado['data_scan'][:19]}")
    print(f"Total de pastas: {resultado['total_pastas']}")
    print(f"CNJs únicos: {resultado['total_cnjs_unicos']}")
    print()
    print("ESTADO                  | QTD")
    print("-" * 40)

    # Ordenar por prioridade
    ordem = [
        "PENDENTE-PDF", "PENDENTE-EXTRAÇÃO", "PENDENTE-ANÁLISE",
        "PENDENTE-PROPOSTA", "PENDENTE-ACEITE", "PENDENTE-AGENDAMENTO",
        "PENDENTE-LAUDO", "EM-CONTESTAÇÃO", "COMPLETO", "VAZIO", "INDEFINIDO"
    ]
    for estado in ordem:
        qtd = resultado["estatisticas"].get(estado, 0)
        if qtd > 0:
            emoji = {
                "PENDENTE-PDF": "📄",
                "PENDENTE-EXTRAÇÃO": "📝",
                "PENDENTE-ANÁLISE": "🔍",
                "PENDENTE-PROPOSTA": "💰",
                "PENDENTE-ACEITE": "✋",
                "PENDENTE-AGENDAMENTO": "📅",
                "PENDENTE-LAUDO": "📋",
                "EM-CONTESTAÇÃO": "⚔️",
                "COMPLETO": "✅",
                "VAZIO": "📂",
                "INDEFINIDO": "❓",
            }.get(estado, "")
            print(f"  {emoji} {estado:<22} | {qtd}")

    print()

    # Listar processos que precisam de ação
    pendentes = [p for p in resultado["processos"] if p["estado"] not in ("COMPLETO", "VAZIO")]
    if pendentes:
        print("PROCESSOS QUE PRECISAM DE AÇÃO:")
        print("-" * 60)
        for p in pendentes:
            cnj = p.get("cnj", "sem CNJ")
            cidade = ""
            if "ficha" in p:
                cidade = p["ficha"].get("cidade", "")
            elif "pericia" in p:
                cidade = p["pericia"].get("cidade", "")

            info = f"{cnj}"
            if cidade:
                info += f" ({cidade})"

            print(f"  [{p['estado']}] {info}")
            print(f"    → {p['proxima_acao']}")
        print()

    print(f"JSON salvo em: {OUTPUT_JSON}")


if __name__ == "__main__":
    resultado = scanear()

    if "--json-only" not in sys.argv:
        mostrar_resumo(resultado)
    elif "--resumo" in sys.argv:
        mostrar_resumo(resultado)
