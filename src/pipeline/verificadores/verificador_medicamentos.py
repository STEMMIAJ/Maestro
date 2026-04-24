#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICADOR DE MEDICAMENTOS — ETAPA 5.4
Extrai medicamentos, dosagens e detecta contraindições.
"""

import json
import re
import sys
from pathlib import Path

# Medicamentos comuns em perícias médicas judiciais
MEDICAMENTOS_CONHECIDOS = {
    'dipirona': {'tipo': 'analgésico', 'via': ['oral', 'intravenosa', 'intramuscular']},
    'paracetamol': {'tipo': 'analgésico', 'via': ['oral']},
    'ibuprofeno': {'tipo': 'anti-inflamatório', 'via': ['oral']},
    'naproxeno': {'tipo': 'anti-inflamatório', 'via': ['oral']},
    'diclofenaco': {'tipo': 'anti-inflamatório', 'via': ['oral', 'intravenosa', 'intramuscular']},
    'clopidogrel': {'tipo': 'antiagregante', 'via': ['oral']},
    'ácido acetilsalicílico': {'tipo': 'antiagregante', 'via': ['oral']},
    'atorvastatina': {'tipo': 'hipolipemiante', 'via': ['oral']},
    'sinvastatina': {'tipo': 'hipolipemiante', 'via': ['oral']},
    'losartana': {'tipo': 'anti-hipertensivo', 'via': ['oral']},
    'atenolol': {'tipo': 'anti-hipertensivo', 'via': ['oral']},
    'nifedipino': {'tipo': 'anti-hipertensivo', 'via': ['oral']},
    'captopril': {'tipo': 'anti-hipertensivo', 'via': ['oral']},
    'lisinopril': {'tipo': 'anti-hipertensivo', 'via': ['oral']},
    'omeprazol': {'tipo': 'antiácido', 'via': ['oral']},
    'metformina': {'tipo': 'hipoglicemiante', 'via': ['oral']},
    'glibenclamida': {'tipo': 'hipoglicemiante', 'via': ['oral']},
    'insulina': {'tipo': 'hipoglicemiante', 'via': ['intravenosa', 'subcutânea']},
    'amoxicilina': {'tipo': 'antibiótico', 'via': ['oral']},
    'penicilina': {'tipo': 'antibiótico', 'via': ['oral', 'intramuscular', 'intravenosa']},
    'azitromicina': {'tipo': 'antibiótico', 'via': ['oral']},
    'levofloxacino': {'tipo': 'antibiótico', 'via': ['oral']},
    'cefalexina': {'tipo': 'antibiótico', 'via': ['oral']},
    'fluconazol': {'tipo': 'antifúngico', 'via': ['oral', 'intravenosa']},
    'sertralina': {'tipo': 'antidepressivo', 'via': ['oral']},
    'fluoxetina': {'tipo': 'antidepressivo', 'via': ['oral']},
    'paroxetina': {'tipo': 'antidepressivo', 'via': ['oral']},
    'venlafaxina': {'tipo': 'antidepressivo', 'via': ['oral']},
    'bupropiona': {'tipo': 'antidepressivo', 'via': ['oral']},
    'citalopram': {'tipo': 'antidepressivo', 'via': ['oral']},
    'lorazepam': {'tipo': 'ansiolítico', 'via': ['oral', 'intramuscular']},
    'diazepam': {'tipo': 'ansiolítico', 'via': ['oral', 'intramuscular']},
    'clonazepam': {'tipo': 'ansiolítico', 'via': ['oral']},
    'alprazolam': {'tipo': 'ansiolítico', 'via': ['oral']},
    'bromazepam': {'tipo': 'ansiolítico', 'via': ['oral']},
    'amitriptilina': {'tipo': 'antidepressivo', 'via': ['oral']},
    'nortriptilina': {'tipo': 'antidepressivo', 'via': ['oral']},
    'gabapentina': {'tipo': 'anticonvulsivante', 'via': ['oral']},
    'pregabalina': {'tipo': 'anticonvulsivante', 'via': ['oral']},
    'carbamazepina': {'tipo': 'anticonvulsivante', 'via': ['oral']},
    'fenitóina': {'tipo': 'anticonvulsivante', 'via': ['oral']},
    'ácido valproico': {'tipo': 'anticonvulsivante', 'via': ['oral']},
    'levotiroxina': {'tipo': 'hormônio', 'via': ['oral']},
    'prednisona': {'tipo': 'corticoide', 'via': ['oral']},
    'dexametasona': {'tipo': 'corticoide', 'via': ['oral', 'intravenosa']},
    'metilprednisolona': {'tipo': 'corticoide', 'via': ['intravenosa']},
    'furosemida': {'tipo': 'diurético', 'via': ['oral', 'intravenosa']},
    'hidroclorotiazida': {'tipo': 'diurético', 'via': ['oral']},
    'espironolactona': {'tipo': 'diurético', 'via': ['oral']},
    'tramadol': {'tipo': 'analgésico opioide', 'via': ['oral', 'intramuscular']},
    'morfina': {'tipo': 'analgésico opioide', 'via': ['oral', 'intravenosa', 'intramuscular']},
    'codeína': {'tipo': 'analgésico opioide', 'via': ['oral']},
    'metadona': {'tipo': 'analgésico opioide', 'via': ['oral']},
    'metotrexato': {'tipo': 'imunossupressor', 'via': ['oral', 'intramuscular']},
    'ciclofosfamida': {'tipo': 'imunossupressor', 'via': ['intravenosa', 'oral']},
    'azatioprina': {'tipo': 'imunossupressor', 'via': ['oral']},
    'tacrolimo': {'tipo': 'imunossupressor', 'via': ['oral']},
    'ciclosporina': {'tipo': 'imunossupressor', 'via': ['oral', 'intravenosa']},
}

# Contraindições conhecidas (simplificado para 50 principais)
CONTRACOES = [
    {'droga1': 'ácido acetilsalicílico', 'droga2': 'ibuprofeno', 'risco': 'aumento do risco de sangramento e toxicidade GI'},
    {'droga1': 'warfarina', 'droga2': 'ácido acetilsalicílico', 'risco': 'aumento do risco de sangramento'},
    {'droga1': 'metformina', 'droga2': 'glibenclamida', 'risco': 'aumento do risco de hipoglicemia'},
    {'droga1': 'sertralina', 'droga2': 'tramadol', 'risco': 'síndrome da serotonina'},
    {'droga1': 'fluoxetina', 'droga2': 'tramadol', 'risco': 'síndrome da serotonina'},
    {'droga1': 'paroxetina', 'droga2': 'tramadol', 'risco': 'síndrome da serotonina'},
    {'droga1': 'venlafaxina', 'droga2': 'tramadol', 'risco': 'síndrome da serotonina'},
    {'droga1': 'amitriptilina', 'droga2': 'citalopram', 'risco': 'aumento do risco de síndrome da serotonina'},
    {'droga1': 'lorazepam', 'droga2': 'morfina', 'risco': 'depressão do SNC'},
    {'droga1': 'diazepam', 'droga2': 'morfina', 'risco': 'depressão do SNC'},
    {'droga1': 'clonazepam', 'droga2': 'álcool', 'risco': 'depressão do SNC'},
    {'droga1': 'ácido valproico', 'droga2': 'carbamazepina', 'risco': 'redução dos níveis de ambas'},
    {'droga1': 'captopril', 'droga2': 'furosemida', 'risco': 'hipotensão severa'},
    {'droga1': 'lisinopril', 'droga2': 'losartana', 'risco': 'hipotensão severa'},
    {'droga1': 'atenolol', 'droga2': 'verapamil', 'risco': 'atraso AV'},
    {'droga1': 'omeprazol', 'droga2': 'clopidogrel', 'risco': 'redução do efeito antiagregante'},
    {'droga1': 'metotrexato', 'droga2': 'ibuprofeno', 'risco': 'aumento da toxicidade do metotrexato'},
    {'droga1': 'ciclosporina', 'droga2': 'nifedipino', 'risco': 'aumento dos níveis de ciclosporina'},
    {'droga1': 'prednisona', 'droga2': 'fluconazol', 'risco': 'aumento dos efeitos de prednisona'},
]

def extrair_medicamentos(texto):
    """Extrai medicamentos do texto."""
    medicamentos = []

    for med_nome in MEDICAMENTOS_CONHECIDOS.keys():
        # Busca exato (case-insensitive)
        padrao = r'\b' + re.escape(med_nome) + r'\b'
        for match in re.finditer(padrao, texto, re.IGNORECASE):
            # Busca dosagem próxima
            contexto = texto[match.start():min(match.end()+100, len(texto))]
            dosagem_match = re.search(r'(\d+(?:\.\d+)?)\s*(mg|ml|g|ui|unidades|comprimido|cápsula|gotas?)', contexto, re.IGNORECASE)

            dosagem = None
            unidade = None
            if dosagem_match:
                dosagem = dosagem_match.group(1)
                unidade = dosagem_match.group(2)

            medicamentos.append({
                'nome': med_nome,
                'nome_encontrado': match.group(0),
                'dosagem': dosagem,
                'unidade': unidade,
                'tipo': MEDICAMENTOS_CONHECIDOS[med_nome]['tipo'],
                'vias_conhecidas': MEDICAMENTOS_CONHECIDOS[med_nome]['via'],
                'posicao': match.start(),
                'contexto': texto[max(0, match.start()-50):match.end()+100]
            })

    return medicamentos

def detectar_contracoes(medicamentos):
    """Detecta contraindições entre medicamentos encontrados."""
    nomes_encontrados = [m['nome'].lower() for m in medicamentos]
    contracoes_detectadas = []

    for contra in CONTRACOES:
        droga1 = contra['droga1'].lower()
        droga2 = contra['droga2'].lower()

        if droga1 in nomes_encontrados and droga2 in nomes_encontrados:
            contracoes_detectadas.append({
                'droga1': droga1,
                'droga2': droga2,
                'risco': contra['risco'],
                'severidade': '❌ Potencial',
                'recomendacao': 'Avaliar necessidade clínica da associação'
            })

    return contracoes_detectadas

def processar_medicamentos(texto_limpo_path, output_path):
    """Processa arquivo de texto e gera relatório de medicamentos."""

    resultado = {
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'medicamentos_encontrados': [],
        'contracoes_detectadas': [],
        'sumario': {}
    }

    # Lê arquivo
    try:
        with open(texto_limpo_path, 'r', encoding='utf-8') as f:
            texto = f.read()
    except FileNotFoundError:
        resultado['erro'] = f'Arquivo não encontrado: {texto_limpo_path}'
        return resultado

    # Extrai medicamentos
    meds = extrair_medicamentos(texto)

    # Agrupa por nome
    meds_unicos = {}
    for med in meds:
        chave = med['nome']
        if chave not in meds_unicos:
            meds_unicos[chave] = {
                'nome': med['nome'],
                'tipo': med['tipo'],
                'ocorrencias': 1,
                'dosagens': [med['dosagem']] if med['dosagem'] else [],
                'unidades': [med['unidade']] if med['unidade'] else [],
                'status': '✅ Conhecida'
            }
        else:
            meds_unicos[chave]['ocorrencias'] += 1
            if med['dosagem']:
                meds_unicos[chave]['dosagens'].append(med['dosagem'])
            if med['unidade']:
                meds_unicos[chave]['unidades'].append(med['unidade'])

    resultado['medicamentos_encontrados'] = list(meds_unicos.values())

    # Detecta contraindições
    contracoes = detectar_contracoes(meds)
    resultado['contracoes_detectadas'] = contracoes

    # Sumário
    resultado['sumario'] = {
        'total_medicamentos': len(resultado['medicamentos_encontrados']),
        'total_ocorrencias': sum(m['ocorrencias'] for m in resultado['medicamentos_encontrados']),
        'contracoes_potenciais': len(contracoes),
        'tipos_representados': len(set(m['tipo'] for m in resultado['medicamentos_encontrados']))
    }

    # Salva resultado
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Uso: verificador_medicamentos.py <texto_limpo.txt> <output.json>')
        sys.exit(1)

    texto_path = sys.argv[1]
    output_path = sys.argv[2]

    resultado = processar_medicamentos(texto_path, output_path)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
