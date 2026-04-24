#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICADOR DE NOMES, CPFs E OABs — ETAPA 5.3
Extrai e valida nomes, CPFs e inscrições OAB.
"""

import json
import re
import sys
from pathlib import Path

def calcular_digito_cpf(cpf_parcial):
    """Calcula o dígito verificador do CPF."""
    if len(cpf_parcial) == 9:
        # Primeiro dígito
        soma = sum(int(cpf_parcial[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        primeiro = 0 if resto < 2 else 11 - resto
        return str(primeiro)
    elif len(cpf_parcial) == 10:
        # Segundo dígito
        soma = sum(int(cpf_parcial[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        segundo = 0 if resto < 2 else 11 - resto
        return str(segundo)
    return None

def validar_cpf(cpf_str):
    """Valida um CPF removendo formatação e checando dígitos."""
    # Remove formatação
    cpf_limpo = re.sub(r'\D', '', cpf_str)

    if len(cpf_limpo) != 11:
        return False, 'CPF não possui 11 dígitos'

    # Verifica se todos os dígitos são iguais (CPF inválido)
    if len(set(cpf_limpo)) == 1:
        return False, 'CPF com todos dígitos iguais'

    # Valida primeiro dígito
    primeiro_calculado = calcular_digito_cpf(cpf_limpo[:9])
    if primeiro_calculado != cpf_limpo[9]:
        return False, f'Primeiro dígito verificador incorreto (esperado {primeiro_calculado}, encontrado {cpf_limpo[9]})'

    # Valida segundo dígito
    segundo_calculado = calcular_digito_cpf(cpf_limpo[:10])
    if segundo_calculado != cpf_limpo[10]:
        return False, f'Segundo dígito verificador incorreto (esperado {segundo_calculado}, encontrado {cpf_limpo[10]})'

    return True, 'CPF válido'

def extrair_cpfs(texto):
    """Extrai todos os CPFs do texto."""
    cpfs = []

    # Padrão com formatação: XXX.XXX.XXX-XX
    padrao = r'\b(\d{3}\.\d{3}\.\d{3}-\d{2})\b'
    for match in re.finditer(padrao, texto):
        cpf_str = match.group(1)
        valido, msg = validar_cpf(cpf_str)
        cpfs.append({
            'cpf': cpf_str,
            'cpf_limpo': re.sub(r'\D', '', cpf_str),
            'valido': valido,
            'mensagem': msg,
            'posicao': match.start(),
            'contexto': texto[max(0, match.start()-50):match.end()+50]
        })

    return cpfs

def extrair_oabs(texto):
    """Extrai inscrições OAB do texto."""
    oabs = []

    # Padrão: OAB/UF NUMERO ou OAB/UF nº NUMERO ou OAB nº XXXXXXX/UF
    padrao1 = r'\bOAB\s*/\s*([A-Z]{2})\s*(?:n[º]|nº)?\s*(\d+)\b'
    for match in re.finditer(padrao1, texto, re.IGNORECASE):
        uf = match.group(1).upper()
        numero = match.group(2)
        oabs.append({
            'oab': f'{match.group(0)}',
            'uf': uf,
            'numero': numero,
            'formato': 'OAB/UF NUMERO',
            'posicao': match.start(),
            'contexto': texto[max(0, match.start()-50):match.end()+50]
        })

    # Padrão: nº XXXXXXX/UF
    padrao2 = r'(?:n[º]|nº)\s*(\d+)\s*/\s*([A-Z]{2})\b'
    for match in re.finditer(padrao2, texto, re.IGNORECASE):
        numero = match.group(1)
        uf = match.group(2).upper()
        oabs.append({
            'oab': f'{match.group(0)}',
            'uf': uf,
            'numero': numero,
            'formato': 'nº NUMERO/UF',
            'posicao': match.start(),
            'contexto': texto[max(0, match.start()-50):match.end()+50]
        })

    return oabs

def extrair_nomes(texto):
    """Extrai nomes de pessoas (sequências capitalizadas de 2+ palavras)."""
    nomes = []

    # Padrão: Palavra Capitada Palavra
    padrao = r'\b([A-Z][a-záéíóúâêôãõçñ]+(?:\s+[A-Z][a-záéíóúâêôãõçñ]+)+)\b'
    for match in re.finditer(padrao, texto):
        nome = match.group(1)
        # Filtra palavras-chave que não são nomes
        palavras_filtro = ['De', 'Da', 'Do', 'Dos', 'E', 'A', 'O', 'Por', 'Para']
        partes = nome.split()
        if len(partes) >= 2 and nome not in ['De', 'Da', 'Do', 'Dos']:
            nomes.append({
                'nome': nome,
                'partes': partes,
                'posicao': match.start(),
                'contexto': texto[max(0, match.start()-30):match.end()+30]
            })

    return nomes

def agrupar_nomes_similares(nomes):
    """Agrupa nomes que provavelmente são a mesma pessoa com variações."""
    grupos = {}

    for nome_obj in nomes:
        nome = nome_obj['nome'].upper()
        # Usa as primeiras 3 palavras como chave
        partes = nome_obj['partes']
        if len(partes) >= 2:
            chave = f"{partes[0].upper()} {partes[1].upper()}"
        else:
            chave = nome

        if chave not in grupos:
            grupos[chave] = []
        grupos[chave].append(nome_obj['nome'])

    return grupos

def processar_nomes(texto_limpo_path, output_path):
    """Processa arquivo de texto e gera relatório de nomes, CPFs e OABs."""

    resultado = {
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'cpfs_encontrados': [],
        'oabs_encontrados': [],
        'nomes_encontrados': [],
        'grupos_nomes': {},
        'sumario': {}
    }

    # Lê arquivo
    try:
        with open(texto_limpo_path, 'r', encoding='utf-8') as f:
            texto = f.read()
    except FileNotFoundError:
        resultado['erro'] = f'Arquivo não encontrado: {texto_limpo_path}'
        return resultado

    # Extrai CPFs
    cpfs = extrair_cpfs(texto)
    resultado['cpfs_encontrados'] = [
        {
            'cpf': c['cpf'],
            'valido': c['valido'],
            'status': '✅' if c['valido'] else '❌',
            'mensagem': c['mensagem'],
            'ocorrencias': sum(1 for x in cpfs if x['cpf'] == c['cpf'])
        }
        for c in {c['cpf']: c for c in cpfs}.values()
    ]

    # Extrai OABs
    oabs = extrair_oabs(texto)
    oabs_unicos = {}
    for oab in oabs:
        chave = f"{oab['uf']}/{oab['numero']}"
        if chave not in oabs_unicos:
            oabs_unicos[chave] = {
                'oab': chave,
                'uf': oab['uf'],
                'numero': oab['numero'],
                'formato': oab['formato'],
                'status': '✅ Formato válido',
                'ocorrencias': 1
            }
        else:
            oabs_unicos[chave]['ocorrencias'] += 1

    resultado['oabs_encontrados'] = list(oabs_unicos.values())

    # Extrai nomes
    nomes = extrair_nomes(texto)
    nomes_unicos = {n['nome']: n for n in nomes}
    resultado['nomes_encontrados'] = [
        {
            'nome': nome,
            'ocorrencias': sum(1 for n in nomes if n['nome'] == nome),
            'partes': n['partes']
        }
        for nome, n in nomes_unicos.items()
    ]

    # Agrupa nomes similares
    grupos = agrupar_nomes_similares(nomes)
    resultado['grupos_nomes'] = grupos

    # Sumário
    resultado['sumario'] = {
        'total_cpfs': len(resultado['cpfs_encontrados']),
        'cpfs_validos': sum(1 for c in resultado['cpfs_encontrados'] if c['valido']),
        'cpfs_invalidos': sum(1 for c in resultado['cpfs_encontrados'] if not c['valido']),
        'total_oabs': len(resultado['oabs_encontrados']),
        'total_nomes': len(resultado['nomes_encontrados']),
        'grupos_nomes': len(grupos)
    }

    # Salva resultado
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Uso: verificador_nomes.py <texto_limpo.txt> <output.json>')
        sys.exit(1)

    texto_path = sys.argv[1]
    output_path = sys.argv[2]

    resultado = processar_nomes(texto_path, output_path)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
