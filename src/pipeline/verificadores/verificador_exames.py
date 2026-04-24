#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICADOR DE EXAMES — ETAPA 5.5
Extrai exames mencionados, datas e identifica anexos faltantes.
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Tipos de exames comuns em perícias médicas judiciais
TIPOS_EXAMES = {
    'ressonância magnética': {'alias': ['RM', 'ressonância', 'RMN'], 'categoria': 'Imagem'},
    'tomografia': {'alias': ['TC', 'tomografia computadorizada', 'TOMO'], 'categoria': 'Imagem'},
    'tomografia computadorizada': {'alias': ['TC', 'tomografia', 'TOMO'], 'categoria': 'Imagem'},
    'radiografia': {'alias': ['raio-x', 'raio x', 'RX', 'X-ray'], 'categoria': 'Imagem'},
    'raio-x': {'alias': ['rx', 'radiografia', 'X-ray'], 'categoria': 'Imagem'},
    'ultrassom': {'alias': ['US', 'eco', 'ultrassonia'], 'categoria': 'Imagem'},
    'eletrocardiograma': {'alias': ['ECG', 'EKG'], 'categoria': 'Cardiologia'},
    'eletroencefalograma': {'alias': ['EEG'], 'categoria': 'Neurologia'},
    'eletromiografia': {'alias': ['EMG'], 'categoria': 'Neurologia'},
    'teste ergométrico': {'alias': ['ergometria', 'teste de esforço'], 'categoria': 'Cardiologia'},
    'ecocardiograma': {'alias': ['eco', 'ecocardio'], 'categoria': 'Cardiologia'},
    'hemograma': {'alias': ['CBC', 'hemácias', 'leucócitos'], 'categoria': 'Laboratorial'},
    'bioquímica sérica': {'alias': ['enzimas hepáticas', 'creatinina', 'glicemia'], 'categoria': 'Laboratorial'},
    'hormônios tireoidianos': {'alias': ['T3', 'T4', 'TSH'], 'categoria': 'Laboratorial'},
    'sorologias': {'alias': ['HIV', 'hepatite', 'sífilis'], 'categoria': 'Laboratorial'},
    'urina': {'alias': ['EAS', 'sumário de urina'], 'categoria': 'Laboratorial'},
    'densidade mineral óssea': {'alias': ['DEXA', 'densitometria'], 'categoria': 'Imagem'},
    'artroscopia': {'alias': ['artro'], 'categoria': 'Procedimento'},
    'endoscopia': {'alias': ['gastroscopia', 'colonoscopia'], 'categoria': 'Procedimento'},
    'colonoscopia': {'alias': ['colono'], 'categoria': 'Procedimento'},
    'gastroscopia': {'alias': ['gastro'], 'categoria': 'Procedimento'},
    'broncoscopia': {'alias': ['bronco'], 'categoria': 'Procedimento'},
    'laparoscopia': {'alias': ['laparo'], 'categoria': 'Procedimento'},
    'biopsia': {'alias': ['biópsia', 'biopsy'], 'categoria': 'Procedimento'},
    'teste neuropsicológico': {'alias': ['neuropsico', 'cognitivo'], 'categoria': 'Psicologia'},
    'teste psicológico': {'alias': ['psi', 'rorschach', 'WISC'], 'categoria': 'Psicologia'},
    'espirometria': {'alias': ['prova de função pulmonar', 'PFP'], 'categoria': 'Respiratório'},
    'ressonância magnética funcional': {'alias': ['fMRI', 'RMf'], 'categoria': 'Imagem'},
    'cintilografia': {'alias': ['cinti'], 'categoria': 'Imagem'},
    'angiografia': {'alias': ['angio'], 'categoria': 'Imagem'},
    'mamografia': {'alias': ['mamografia digital'], 'categoria': 'Imagem'},
    'densitometria óssea': {'alias': ['DEXA', 'DXA'], 'categoria': 'Imagem'},
}

def extrair_exames(texto):
    """Extrai todos os exames mencionados do texto."""
    exames = []

    for exame_nome, info in TIPOS_EXAMES.items():
        # Busca nome principal
        padrao_principal = r'\b' + re.escape(exame_nome) + r'\b'
        for match in re.finditer(padrao_principal, texto, re.IGNORECASE):
            data_exame = extrair_data_exame(texto, match.start())
            exames.append({
                'nome': exame_nome,
                'nome_encontrado': match.group(0),
                'categoria': info['categoria'],
                'data': data_exame,
                'posicao': match.start(),
                'contexto': texto[max(0, match.start()-80):match.end()+80]
            })

        # Busca alias
        for alias in info['alias']:
            padrao_alias = r'\b' + re.escape(alias) + r'\b'
            for match in re.finditer(padrao_alias, texto, re.IGNORECASE):
                data_exame = extrair_data_exame(texto, match.start())
                # Evita duplicatas
                if not any(e['nome_encontrado'].lower() == match.group(0).lower() and
                          e['posicao'] == match.start() for e in exames):
                    exames.append({
                        'nome': exame_nome,
                        'nome_encontrado': match.group(0),
                        'categoria': info['categoria'],
                        'data': data_exame,
                        'posicao': match.start(),
                        'contexto': texto[max(0, match.start()-80):match.end()+80]
                    })

    return exames

def extrair_data_exame(texto, posicao):
    """Tenta extrair a data de um exame a partir de sua posição."""
    # Busca data dentro de 200 caracteres antes ou depois
    inicio = max(0, posicao - 200)
    fim = min(len(texto), posicao + 200)
    trecho = texto[inicio:fim]

    # Padrão DD/MM/YYYY
    match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', trecho)
    if match:
        return match.group(0)

    # Padrão DD de mês de YYYY
    meses = {
        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5,
        'junho': 6, 'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10,
        'novembro': 11, 'dezembro': 12,
    }
    padrao = r'(\d{1,2})\s+de\s+(' + '|'.join(meses.keys()) + r')\s+de\s+(\d{4})'
    match = re.search(padrao, trecho, re.IGNORECASE)
    if match:
        return match.group(0)

    return None

def validar_data_exame(data_str):
    """Valida se a data do exame é plausível (não muito antiga)."""
    if not data_str:
        return None, 'Sem data'

    # Tenta parsing
    try:
        # Formato DD/MM/YYYY
        partes = data_str.split('/')
        if len(partes) == 3:
            dia, mes, ano = int(partes[0]), int(partes[1]), int(partes[2])
            data = datetime(ano, mes, dia)

            # Verifica se não é muito antiga
            dias_ago = (datetime.now() - data).days
            if dias_ago > 730:  # 2 anos
                return data, f'⚠️ Exame antigo ({dias_ago} dias atrás)'
            else:
                return data, '✅ Recente'
    except:
        pass

    return None, '⚠️ Data inválida'

def processar_exames(texto_limpo_path, output_path):
    """Processa arquivo de texto e gera relatório de exames."""

    resultado = {
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'exames_encontrados': [],
        'exames_antigos': [],
        'exames_sem_data': [],
        'sumario': {}
    }

    # Lê arquivo
    try:
        with open(texto_limpo_path, 'r', encoding='utf-8') as f:
            texto = f.read()
    except FileNotFoundError:
        resultado['erro'] = f'Arquivo não encontrado: {texto_limpo_path}'
        return resultado

    # Extrai exames
    exames = extrair_exames(texto)

    # Agrupa e valida
    exames_unicos = {}
    for exame in exames:
        chave = f"{exame['nome']}_{exame['data']}"
        if chave not in exames_unicos:
            data_obj, status = validar_data_exame(exame['data'])
            exames_unicos[chave] = {
                'nome': exame['nome'],
                'categoria': exame['categoria'],
                'data': exame['data'],
                'status': status,
                'dias_decorridos': (datetime.now() - data_obj).days if data_obj else None,
                'ocorrencias': 1
            }
        else:
            exames_unicos[chave]['ocorrencias'] += 1

    # Organiza na saída
    for chave, exame in exames_unicos.items():
        resultado['exames_encontrados'].append(exame)

        # Separa antigos
        if 'antigo' in exame['status'].lower():
            resultado['exames_antigos'].append(exame)

        # Separa sem data
        if exame['data'] is None:
            resultado['exames_sem_data'].append(exame)

    # Ordena por data (mais recentes primeiro)
    resultado['exames_encontrados'].sort(
        key=lambda x: x['dias_decorridos'] if x['dias_decorridos'] is not None else float('inf')
    )

    # Sumário
    resultado['sumario'] = {
        'total_exames': len(resultado['exames_encontrados']),
        'exames_com_data': sum(1 for e in resultado['exames_encontrados'] if e['data']),
        'exames_sem_data': len(resultado['exames_sem_data']),
        'exames_antigos': len(resultado['exames_antigos']),
        'categorias_representadas': len(set(e['categoria'] for e in resultado['exames_encontrados']))
    }

    # Salva resultado
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Uso: verificador_exames.py <texto_limpo.txt> <output.json>')
        sys.exit(1)

    texto_path = sys.argv[1]
    output_path = sys.argv[2]

    resultado = processar_exames(texto_path, output_path)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
