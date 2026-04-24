#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICADOR DE CIDs (DataSUS) — ETAPA 5.1
Extrai e valida códigos CID-10 contra a base oficial DataSUS (CSV local).
Fallback: dicionário interno dos ~60 CIDs mais comuns em perícias judiciais.

Uso: python3 verificador_cids_datasus.py <TEXTO-LIMPO.txt> <output.json>
"""

import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ============================================================
# CAMINHO DA BASE LOCAL DataSUS
# ============================================================
CSV_DATASUS = Path("/home/n8n/processos/bases-dados/cid10/CID-10-SUBCATEGORIAS.csv")

# ============================================================
# MAPEAMENTO DE ESPECIALIDADE POR LETRA DO CID
# ============================================================
ESPECIALIDADE_POR_LETRA = {
    "A": "Infectologia",
    "B": "Infectologia",
    "C": "Oncologia",
    "D": "Hematologia/Oncologia",
    "E": "Endocrinologia",
    "F": "Psiquiatria",
    "G": "Neurologia",
    "H": "Oftalmologia/Otorrinolaringologia",
    "I": "Cardiologia",
    "J": "Pneumologia",
    "K": "Gastroenterologia",
    "L": "Dermatologia",
    "M": "Ortopedia/Reumatologia",
    "N": "Nefrologia/Urologia",
    "O": "Obstetrícia",
    "P": "Neonatologia",
    "Q": "Genética Médica",
    "R": "Clínica Geral (sinais/sintomas)",
    "S": "Ortopedia/Traumatologia",
    "T": "Ortopedia/Traumatologia",
    "U": "Códigos para propósitos especiais",
    "V": "Medicina Legal (causas externas)",
    "W": "Medicina Legal (causas externas)",
    "X": "Medicina Legal (causas externas)",
    "Y": "Medicina Legal (causas externas)",
    "Z": "Medicina Preventiva/Saúde Pública",
}

# ============================================================
# FALLBACK — CIDs mais comuns em perícias médicas judiciais
# ============================================================
CIDS_FALLBACK = {
    "A00": "Cólera",
    "A15": "Tuberculose respiratória",
    "B20": "Doença pelo HIV",
    "B24": "Doença pelo HIV não especificada",
    "C34": "Neoplasia maligna dos brônquios e pulmões",
    "C50": "Neoplasia maligna da mama",
    "D50": "Anemia por deficiência de ferro",
    "E10": "Diabetes mellitus tipo 1",
    "E11": "Diabetes mellitus tipo 2",
    "E66": "Obesidade",
    "F10": "Transtornos mentais devidos ao uso de álcool",
    "F14": "Transtornos mentais devidos ao uso de cocaína",
    "F19": "Transtornos mentais devidos ao uso de múltiplas drogas",
    "F20": "Esquizofrenia",
    "F30": "Episódio maníaco",
    "F31": "Transtorno afetivo bipolar",
    "F32": "Episódio depressivo",
    "F33": "Transtorno depressivo recorrente",
    "F40": "Transtornos fóbico-ansiosos",
    "F41": "Outros transtornos ansiosos",
    "F43": "Reações ao estresse grave e transtornos de adaptação",
    "F60": "Transtornos específicos da personalidade",
    "F71": "Retardo mental moderado",
    "F84": "Transtornos globais do desenvolvimento",
    "G40": "Epilepsia",
    "G43": "Enxaqueca",
    "G45": "Acidentes vasculares cerebrais isquêmicos transitórios",
    "G47": "Distúrbios do sono",
    "G80": "Paralisia cerebral",
    "G89": "Dor não classificada em outra parte",
    "H53": "Distúrbios visuais",
    "H54": "Cegueira e visão subnormal",
    "H90": "Perda de audição por transtorno de condução e/ou neurossensorial",
    "I10": "Hipertensão essencial (primária)",
    "I25": "Doença isquêmica crônica do coração",
    "I50": "Insuficiência cardíaca",
    "I63": "Infarto cerebral",
    "I64": "Acidente vascular cerebral não especificado",
    "J06": "Infecções agudas das vias aéreas superiores",
    "J44": "Outras doenças pulmonares obstrutivas crônicas",
    "J45": "Asma",
    "K21": "Doença de refluxo gastroesofágico",
    "K29": "Gastrite e duodenite",
    "K80": "Colelitíase",
    "L20": "Dermatite atópica",
    "L89": "Úlcera de decúbito",
    "M05": "Artrite reumatoide soropositiva",
    "M10": "Gota",
    "M15": "Poliartrose",
    "M17": "Gonartrose (artrose do joelho)",
    "M19": "Outras artroses",
    "M45": "Espondilite anquilosante",
    "M50": "Transtornos de discos cervicais",
    "M51": "Outros transtornos de discos intervertebrais",
    "M54": "Dorsalgia",
    "M65": "Sinovite e tenossinovite",
    "M75": "Lesões do ombro",
    "M79": "Outros transtornos de tecidos moles",
    "N18": "Insuficiência renal crônica",
    "N39": "Outros transtornos do trato urinário",
    "R52": "Dor não classificada em outra parte",
    "S06": "Traumatismo intracraniano",
    "S12": "Fratura de vértebra cervical",
    "S32": "Fratura da coluna lombar e da pelve",
    "S42": "Fratura do ombro e do braço",
    "S52": "Fratura do antebraço",
    "S62": "Fratura ao nível do punho e da mão",
    "S72": "Fratura do fêmur",
    "S82": "Fratura da perna incluindo tornozelo",
    "S92": "Fratura do pé",
    "T14": "Traumatismo de região não especificada do corpo",
    "Z73": "Problemas relacionados com a organização de modo de vida",
    "Z76": "Pessoas em contato com os serviços de saúde em outras circunstâncias",
}


# ============================================================
# CARREGAR BASE DataSUS
# ============================================================
def carregar_base_datasus():
    """Carrega CSV DataSUS. Retorna dict {codigo: descricao} e contagem."""
    if not CSV_DATASUS.exists():
        return None, 0

    base = {}
    for enc in ("latin-1", "utf-8", "cp1252"):
        try:
            with open(CSV_DATASUS, "r", encoding=enc) as f:
                leitor = csv.reader(f, delimiter=";")
                cabecalho = next(leitor, None)
                if not cabecalho:
                    continue
                # Detectar índice das colunas SUBCAT e DESCRICAO
                cab_upper = [c.strip().upper() for c in cabecalho]
                idx_subcat = None
                idx_desc = None
                for i, col in enumerate(cab_upper):
                    if col in ("SUBCAT", "SUBCATEGORIA", "CID", "CODIGO"):
                        idx_subcat = i
                    if col in ("DESCRICAO", "DESCRIÇÃO", "DESCR", "NOME"):
                        idx_desc = i
                if idx_subcat is None or idx_desc is None:
                    # Tentar posicional: primeira coluna = código, segunda = descrição
                    idx_subcat = 0
                    idx_desc = 1

                for linha in leitor:
                    if len(linha) <= max(idx_subcat, idx_desc):
                        continue
                    codigo = linha[idx_subcat].strip().upper()
                    descricao = linha[idx_desc].strip()
                    if codigo and descricao:
                        base[codigo] = descricao
            if base:
                return base, len(base)
        except (UnicodeDecodeError, csv.Error):
            continue

    return None, 0


# ============================================================
# VALIDAÇÃO ESTRUTURAL DE CID-10
# ============================================================
def eh_cid_valido(codigo):
    """Valida formato CID-10: letra A-Z + 2 dígitos, opcionalmente .N ou .NN."""
    return bool(re.match(r"^[A-Z]\d{2}(\.\d{1,2})?$", codigo))


def codigo_no_range_valido(codigo):
    """Verifica se o código está dentro dos ranges válidos de CID-10 (A00-Z99)."""
    if not codigo or len(codigo) < 3:
        return False
    letra = codigo[0]
    if letra < "A" or letra > "Z":
        return False
    try:
        num = int(codigo[1:3])
    except ValueError:
        return False
    return 0 <= num <= 99


# ============================================================
# EXTRAÇÃO DE CIDs DO TEXTO
# ============================================================
def extrair_cids(texto):
    """Extrai todos os códigos CID-10 do texto com posição e contexto."""
    # Padrão: [A-Z] + 2 dígitos + opcionalmente . + 1-2 dígitos
    # Precedido e seguido por word boundary ou pontuação/espaço
    padrao = r"(?<![A-Za-z])([A-Z]\d{2}(?:\.\d{1,2})?)(?!\w)"
    matches = list(re.finditer(padrao, texto, re.IGNORECASE))

    cids = []
    for m in matches:
        codigo = m.group(1).upper()
        if not eh_cid_valido(codigo):
            continue

        # Excluir falsos positivos comuns
        # CEP (padrão 5 dígitos-3 dígitos), artigos ("Art. N12"), etc.
        # Se o código base começa com letras que não são CID válidas, pular
        if not codigo_no_range_valido(codigo):
            continue

        # Extrair contexto (80 chars antes e depois)
        inicio_ctx = max(0, m.start() - 80)
        fim_ctx = min(len(texto), m.end() + 80)
        contexto = texto[inicio_ctx:fim_ctx].replace("\n", " ").strip()

        cids.append({
            "codigo": codigo,
            "posicao_char": m.start(),
            "contexto": contexto,
        })

    return cids


# ============================================================
# BUSCA DE DESCRIÇÃO
# ============================================================
def buscar_descricao(codigo, base_datasus, fallback):
    """Busca descrição do CID na base DataSUS, depois no fallback.
    Retorna (descricao, fonte)."""
    # Código exato na base DataSUS
    if base_datasus and codigo in base_datasus:
        return base_datasus[codigo], "datasus-csv"

    # Sem ponto: tentar com ponto (ex: A001 → A00.1)
    if "." not in codigo and len(codigo) > 3 and base_datasus:
        com_ponto = codigo[:3] + "." + codigo[3:]
        if com_ponto in base_datasus:
            return base_datasus[com_ponto], "datasus-csv"

    # Código base (sem subcategoria)
    base_code = codigo.split(".")[0] if "." in codigo else codigo

    if base_datasus and base_code in base_datasus:
        return base_datasus[base_code], "datasus-csv (categoria)"

    # Fallback
    if codigo in fallback:
        return fallback[codigo], "fallback-local"

    if base_code in fallback:
        return fallback[base_code], "fallback-local (categoria)"

    return None, None


# ============================================================
# ESPECIALIDADE POR CID
# ============================================================
def obter_especialidade(codigo):
    """Retorna especialidade médica pela primeira letra do CID."""
    if not codigo:
        return "Desconhecida"
    letra = codigo[0].upper()
    # Refinamento para H (H00-H59 = Oftalmo, H60-H95 = Otorrino)
    if letra == "H":
        try:
            num = int(codigo[1:3])
        except ValueError:
            return "Oftalmologia/Otorrinolaringologia"
        if num <= 59:
            return "Oftalmologia"
        return "Otorrinolaringologia"
    return ESPECIALIDADE_POR_LETRA.get(letra, "Não mapeada")


# ============================================================
# PROCESSAMENTO PRINCIPAL
# ============================================================
def processar_cids(texto_limpo_path, output_path):
    """Processa arquivo de texto e gera relatório JSON de CIDs."""

    agora = datetime.now().isoformat()

    # Carregar base DataSUS
    base_datasus, total_registros_base = carregar_base_datasus()
    fonte_base = "datasus-csv" if base_datasus else "fallback-local"

    # Ler texto
    texto_limpo = Path(texto_limpo_path)
    if not texto_limpo.exists():
        resultado = {
            "status": "erro",
            "erro": f"Arquivo não encontrado: {texto_limpo_path}",
            "timestamp": agora,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        return resultado

    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            texto = texto_limpo.read_text(encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        resultado = {
            "status": "erro",
            "erro": f"Não foi possível decodificar: {texto_limpo_path}",
            "timestamp": agora,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        return resultado

    # Extrair CIDs
    cids_raw = extrair_cids(texto)

    # Deduplicar preservando primeira ocorrência
    vistos = {}
    for cid in cids_raw:
        cod = cid["codigo"]
        if cod not in vistos:
            vistos[cod] = cid
        else:
            # Manter a de menor posição
            if cid["posicao_char"] < vistos[cod]["posicao_char"]:
                vistos[cod] = cid

    # Montar lista de CIDs processados
    cids_saida = []
    validos = 0
    invalidos = 0
    especialidades_set = set()
    fallback = CIDS_FALLBACK if not base_datasus else {}

    for cod, info in vistos.items():
        descricao, fonte = buscar_descricao(cod, base_datasus, CIDS_FALLBACK)
        valido_range = codigo_no_range_valido(cod)
        tem_descricao = descricao is not None

        if valido_range:
            validos += 1
        else:
            invalidos += 1

        esp = obter_especialidade(cod)
        especialidades_set.add(esp)

        cids_saida.append({
            "codigo": cod,
            "descricao": descricao or "Não encontrado na base",
            "valido": valido_range,
            "fonte": fonte or ("range-validado" if valido_range else "nao-encontrado"),
            "contexto": info["contexto"],
            "posicao_char": info["posicao_char"],
            "especialidade": esp,
        })

    # Ordenar por posição de aparição no texto
    cids_saida.sort(key=lambda c: c["posicao_char"])

    # Contagem de especialidades
    contagem_esp = {}
    for c in cids_saida:
        esp = c["especialidade"]
        contagem_esp[esp] = contagem_esp.get(esp, 0) + 1

    # Montar resultado
    resultado = {
        "status": "ok",
        "timestamp": agora,
        "arquivo_entrada": str(texto_limpo_path),
        "base_utilizada": fonte_base,
        "base_local_registros": total_registros_base if base_datasus else len(CIDS_FALLBACK),
        "sumario": {
            "total": len(cids_saida),
            "validos": validos,
            "invalidos": invalidos,
            "com_descricao": sum(1 for c in cids_saida if c["descricao"] != "Não encontrado na base"),
            "sem_descricao": sum(1 for c in cids_saida if c["descricao"] == "Não encontrado na base"),
        },
        "especialidades": contagem_esp,
        "cids": cids_saida,
    }

    # Salvar JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado


# ============================================================
# CLI
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 verificador_cids_datasus.py <TEXTO-LIMPO.txt> <output.json>")
        sys.exit(1)

    texto_path = sys.argv[1]
    output_path = sys.argv[2]

    resultado = processar_cids(texto_path, output_path)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
