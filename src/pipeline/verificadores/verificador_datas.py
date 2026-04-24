#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICADOR DE DATAS E CRONOLOGIA — ETAPA 5.2
Extrai datas, constrói timeline e detecta inconsistências.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

MESES = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5,
    'junho': 6, 'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10,
    'novembro': 11, 'dezembro': 12,
    'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12,
}

PALAVRAS_CHAVE_DATA = {
    'der': 'Data Entrada Requerimento',
    'dib': 'Data Início Benefício',
    'dcb': 'Data Cessação Benefício',
    'acidente': 'Data do Acidente',
    'nomeação': 'Data da Nomeação',
    'diagnóstico': 'Data do Diagnóstico',
    'cirurgia': 'Data da Cirurgia',
    'alta': 'Data da Alta',
    'internação': 'Data de Internação',
}

def extrair_datas(texto):
    """Extrai todas as datas em vários formatos do texto."""
    datas = []

    # Padrão 1: DD/MM/YYYY
    padrao1 = r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b'
    for match in re.finditer(padrao1, texto):
        dia, mes, ano = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if 1 <= dia <= 31 and 1 <= mes <= 12:
            datas.append({
                'data_str': match.group(0),
                'dia': dia,
                'mes': mes,
                'ano': ano,
                'formato': 'DD/MM/YYYY',
                'posicao': match.start(),
                'contexto': texto[max(0, match.start()-50):match.end()+50]
            })

    # Padrão 2: DD.MM.YYYY
    padrao2 = r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b'
    for match in re.finditer(padrao2, texto):
        dia, mes, ano = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if 1 <= dia <= 31 and 1 <= mes <= 12:
            datas.append({
                'data_str': match.group(0),
                'dia': dia,
                'mes': mes,
                'ano': ano,
                'formato': 'DD.MM.YYYY',
                'posicao': match.start(),
                'contexto': texto[max(0, match.start()-50):match.end()+50]
            })

    # Padrão 3: "X de [mês] de YYYY" ou "X de [mês] do YYYY"
    padrao3 = r'\b(\d{1,2})\s+de\s+(' + '|'.join(MESES.keys()) + r')\s+d[eoa]\s+(\d{4})\b'
    for match in re.finditer(padrao3, texto, re.IGNORECASE):
        dia = int(match.group(1))
        mes = MESES[match.group(2).lower()]
        ano = int(match.group(3))
        if 1 <= dia <= 31 and 1 <= mes <= 12:
            datas.append({
                'data_str': match.group(0),
                'dia': dia,
                'mes': mes,
                'ano': ano,
                'formato': 'dia de mês de ano',
                'posicao': match.start(),
                'contexto': texto[max(0, match.start()-50):match.end()+50]
            })

    # Padrão 4: YYYY-MM-DD (ISO)
    padrao4 = r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b'
    for match in re.finditer(padrao4, texto):
        ano, mes, dia = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if 1 <= dia <= 31 and 1 <= mes <= 12:
            datas.append({
                'data_str': match.group(0),
                'dia': dia,
                'mes': mes,
                'ano': ano,
                'formato': 'YYYY-MM-DD',
                'posicao': match.start(),
                'contexto': texto[max(0, match.start()-50):match.end()+50]
            })

    return datas

def validar_data(dia, mes, ano):
    """Valida se a data é plausível."""
    erros = []

    if ano < 1940 or ano > datetime.now().year:
        erros.append('ano fora do intervalo plausível')

    if mes < 1 or mes > 12:
        erros.append('mês inválido')

    if dia < 1 or dia > 31:
        erros.append('dia inválido')

    # Verifica dias em meses com 30 dias
    if mes in [4, 6, 9, 11] and dia > 30:
        erros.append('dia inválido para mês com 30 dias')

    # Verifica fevereiro
    if mes == 2:
        eh_bissexto = (ano % 4 == 0 and ano % 100 != 0) or (ano % 400 == 0)
        max_dia = 29 if eh_bissexto else 28
        if dia > max_dia:
            erros.append(f'fevereiro tem no máximo {max_dia} dias')

    return len(erros) == 0, erros

def detectar_datas_chave(texto, datas):
    """Detecta datas importantes pelo contexto."""
    datas_chave = {}

    for palavra_chave, descricao in PALAVRAS_CHAVE_DATA.items():
        # Busca a palavra-chave perto de uma data
        padrao = r'\b' + palavra_chave + r'\b.*?(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
        for match in re.finditer(padrao, texto, re.IGNORECASE):
            dia = int(match.group(1))
            mes = int(match.group(2))
            ano = int(match.group(3))
            datas_chave[palavra_chave] = {
                'descricao': descricao,
                'data': f'{dia:02d}/{mes:02d}/{ano}',
                'ano': ano
            }

    return datas_chave

def processar_datas(texto_limpo_path, output_path):
    """Processa arquivo de texto e gera relatório de datas."""

    resultado = {
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'datas_encontradas': [],
        'datas_invalidas': [],
        'timeline': [],
        'inconsistencias': [],
        'datas_chave': {},
        'sumario': {}
    }

    # Lê arquivo
    try:
        with open(texto_limpo_path, 'r', encoding='utf-8') as f:
            texto = f.read()
    except FileNotFoundError:
        resultado['erro'] = f'Arquivo não encontrado: {texto_limpo_path}'
        return resultado

    # Extrai datas
    datas = extrair_datas(texto)

    # Valida e organiza
    datas_unicas = {}
    for data_obj in datas:
        chave = f"{data_obj['dia']}/{data_obj['mes']}/{data_obj['ano']}"
        if chave not in datas_unicas:
            valida, erros = validar_data(data_obj['dia'], data_obj['mes'], data_obj['ano'])
            datas_unicas[chave] = {
                'data_str': chave,
                'dia': data_obj['dia'],
                'mes': data_obj['mes'],
                'ano': data_obj['ano'],
                'valida': valida,
                'erros': erros,
                'ocorrencias': 1,
                'contexto_exemplos': [data_obj['contexto'][:100]]
            }
        else:
            datas_unicas[chave]['ocorrencias'] += 1

    # Ordena chronologicamente
    datas_ordenadas = sorted(
        datas_unicas.values(),
        key=lambda x: (x['ano'], x['mes'], x['dia'])
    )

    resultado['datas_encontradas'] = datas_ordenadas
    resultado['timeline'] = [
        f"{d['dia']:02d}/{d['mes']:02d}/{d['ano']}"
        for d in datas_ordenadas if d['valida']
    ]

    # Detecta inconsistências
    inconsistencias = []

    # Data no futuro
    hoje = datetime.now()
    for data_obj in datas_ordenadas:
        if data_obj['valida']:
            data = datetime(data_obj['ano'], data_obj['mes'], data_obj['dia'])
            if data > hoje:
                inconsistencias.append({
                    'tipo': 'data futura',
                    'data': f"{data_obj['dia']:02d}/{data_obj['mes']:02d}/{data_obj['ano']}",
                    'severidade': '⚠️'
                })

    # Datas muito antigas (antes de 1940)
    for data_obj in datas_ordenadas:
        if data_obj['ano'] < 1940:
            inconsistencias.append({
                'tipo': 'data muito antiga',
                'data': f"{data_obj['dia']:02d}/{data_obj['mes']:02d}/{data_obj['ano']}",
                'severidade': '❌'
            })

    resultado['inconsistencias'] = inconsistencias
    resultado['datas_chave'] = detectar_datas_chave(texto, datas_ordenadas)

    resultado['sumario'] = {
        'total_datas': len(resultado['datas_encontradas']),
        'datas_validas': sum(1 for d in resultado['datas_encontradas'] if d['valida']),
        'datas_invalidas': sum(1 for d in resultado['datas_encontradas'] if not d['valida']),
        'inconsistencias_detectadas': len(inconsistencias)
    }

    # Salva resultado
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Uso: verificador_datas.py <texto_limpo.txt> <output.json>')
        sys.exit(1)

    texto_path = sys.argv[1]
    output_path = sys.argv[2]

    resultado = processar_datas(texto_path, output_path)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
