#!/usr/bin/env python3
"""
md_para_xml_peticao.py — Converte Markdown de petição para XML (WordprocessingML)
==================================================================================
Converte o rascunho Markdown gerado pelos agentes para o formato XML
esperado pelo gerar_peticao.py (--corpo-arquivo).

Suporta:
- Parágrafos normais
- Negrito (**texto**)
- Títulos de seção em caixa alta (centralizado e negrito)
- Listas numeradas (1. item)
- Listas com bullet (- item ou • item)
- Blocos de dados fixos ([DADOS_BANCARIOS], [ENDERECO_CONSULTORIO])
- Linha em branco → parágrafo vazio

USO:
    python3 md_para_xml_peticao.py --input /tmp/peticao-rascunho.md --output /tmp/corpo.xml
    python3 md_para_xml_peticao.py --input /tmp/peticao-rascunho.md --output /tmp/corpo.xml --gerar-pdf NOME.pdf
"""

import argparse
import os
import re
import subprocess
import sys
import html

# Estilo padrão: AppleSystemUIFont, 13pt (sz=26)
FONT = "AppleSystemUIFont"
SZ = "26"

# Blocos fixos
DADOS_BANCARIOS = """Titular: Jésus Eduardo Nolêto da Penha
Banco: Santander Brasil S.A. — 033
Agência: 2960 (Santander Digital)
Conta corrente: 01035135-5
PIX: perito@drjesus.com.br"""

ENDERECO_CONSULTORIO = """LOCAL: Rua João Pinheiro, número 531, Centro, Edifício Empresarial Maria Costa – Sala 207
       2º andar (última sala do corredor à esquerda) – Governador Valadares – MG

Referências: prédio de esquina entre a Rua Artur Bernardes (onde se encontra o ponto de ônibus) e a Rua João Pinheiro (sendo o prédio em frente ao muro lateral do Colégio Imaculada).

Observação: prédio com elevador e acessibilidade para pessoas com mobilidade reduzida."""

ASSINATURA = """Dr. Jésus Eduardo Nolêto da Penha
Médico – Perito Judicial – CRM-MG 92.148
Membro da ABMLPM – Associação Brasileira de Medicina Legal e Perícia Médica"""


def texto_para_runs(texto):
    """Converte texto com **negrito** em runs XML."""
    runs = []
    partes = re.split(r'(\*\*.*?\*\*)', texto)
    for parte in partes:
        if parte.startswith('**') and parte.endswith('**'):
            conteudo = html.escape(parte[2:-2])
            runs.append(
                f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>'
                f'<w:b/><w:bCs/><w:sz w:val="{SZ}"/><w:szCs w:val="{SZ}"/></w:rPr>'
                f'<w:t xml:space="preserve">{conteudo}</w:t></w:r>'
            )
        elif parte:
            conteudo = html.escape(parte)
            runs.append(
                f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>'
                f'<w:sz w:val="{SZ}"/><w:szCs w:val="{SZ}"/></w:rPr>'
                f'<w:t xml:space="preserve">{conteudo}</w:t></w:r>'
            )
    return ''.join(runs)


def paragrafo(texto, centralizado=False, negrito_todo=False):
    """Gera um parágrafo XML."""
    ppr_extra = ''
    if centralizado:
        ppr_extra = '<w:jc w:val="center"/>'

    ppr = (
        f'<w:pPr><w:autoSpaceDE w:val="0"/><w:autoSpaceDN w:val="0"/>'
        f'<w:adjustRightInd w:val="0"/>{ppr_extra}</w:pPr>'
    )

    if negrito_todo:
        conteudo = html.escape(texto)
        runs = (
            f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>'
            f'<w:b/><w:bCs/><w:sz w:val="{SZ}"/><w:szCs w:val="{SZ}"/></w:rPr>'
            f'<w:t xml:space="preserve">{conteudo}</w:t></w:r>'
        )
    else:
        runs = texto_para_runs(texto)

    return f'<w:p>{ppr}{runs}</w:p>'


def paragrafo_vazio():
    """Parágrafo vazio (espaçamento)."""
    return (
        f'<w:p><w:pPr><w:autoSpaceDE w:val="0"/><w:autoSpaceDN w:val="0"/>'
        f'<w:adjustRightInd w:val="0"/></w:pPr></w:p>'
    )


def converter_md_para_xml(texto_md):
    """Converte Markdown de petição para XML WordprocessingML."""
    # Substituir blocos fixos
    texto_md = texto_md.replace('[DADOS_BANCARIOS]', DADOS_BANCARIOS)
    texto_md = texto_md.replace('[ENDERECO_CONSULTORIO]', ENDERECO_CONSULTORIO)
    texto_md = texto_md.replace('[ASSINATURA]', ASSINATURA)

    # Remover metadados do template (linhas entre ---)
    texto_md = re.sub(r'^---\s*$.*?^---\s*$', '', texto_md, flags=re.MULTILINE | re.DOTALL)
    # Remover linhas de cabeçalho markdown (# Template:...)
    texto_md = re.sub(r'^#.*$', '', texto_md, flags=re.MULTILINE)
    # Remover seções ## Metadados, ## Campos variáveis, ## Notas
    texto_md = re.sub(r'^## (Metadados|Campos variáveis|Notas|Template).*?(?=^AO JUÍZO|^Aos Exce|\Z)',
                      '', texto_md, flags=re.MULTILINE | re.DOTALL)

    linhas = texto_md.strip().split('\n')
    xml_parts = []

    for linha in linhas:
        linha_strip = linha.strip()

        # Linha vazia → parágrafo vazio
        if not linha_strip:
            xml_parts.append(paragrafo_vazio())
            continue

        # Detectar se é endereçamento (AO JUÍZO...)
        if linha_strip.startswith('AO JUÍZO') or linha_strip.startswith('Aos Excelentíssimos'):
            xml_parts.append(paragrafo(linha_strip, negrito_todo=True))
            continue

        # Detectar processo
        if linha_strip.startswith('Processo nº'):
            xml_parts.append(paragrafo(linha_strip, negrito_todo=True))
            continue

        # Detectar título de seção (MANIFESTAÇÃO, DA COMPLEXIDADE, etc.)
        if (linha_strip.startswith('MANIFESTAÇÃO') or
            linha_strip.startswith('DA ') or
            linha_strip.startswith('DAS ') or
            linha_strip.startswith('DO ') or
            linha_strip.startswith('DOS ') or
            linha_strip == 'CONCLUSÃO'):
            xml_parts.append(paragrafo(linha_strip, centralizado=True, negrito_todo=True))
            continue

        # Detectar "DATA E HORÁRIO:"
        if linha_strip.startswith('DATA E HORÁRIO:'):
            xml_parts.append(paragrafo(linha_strip, negrito_todo=True))
            continue

        # Detectar "LOCAL:"
        if linha_strip.startswith('LOCAL:'):
            xml_parts.append(paragrafo(linha_strip, negrito_todo=True))
            continue

        # Lista numerada (1. texto)
        match_num = re.match(r'^(\d+)\.\s+(.+)', linha_strip)
        if match_num:
            num = match_num.group(1)
            texto = match_num.group(2)
            xml_parts.append(paragrafo(f'{num}. {texto}'))
            continue

        # Lista com bullet
        match_bullet = re.match(r'^[-•]\s+(.+)', linha_strip)
        if match_bullet:
            texto = match_bullet.group(1)
            xml_parts.append(paragrafo(f'• {texto}'))
            continue

        # Parágrafo normal
        xml_parts.append(paragrafo(linha_strip))

    # Assinatura NÃO é adicionada automaticamente — já vem no modelo/rascunho
    # Bug corrigido em 05/03/2026: assinatura duplicava quando o rascunho já incluía

    return '\n'.join(xml_parts)


def main():
    parser = argparse.ArgumentParser(description='Converte MD de petição para XML')
    parser.add_argument('--input', required=True, help='Arquivo Markdown de entrada')
    parser.add_argument('--output', required=True, help='Arquivo XML de saída')
    parser.add_argument('--gerar-pdf', help='Se informado, chama gerar_peticao.py com este nome de PDF')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        md = f.read()

    xml = converter_md_para_xml(md)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(xml)

    print(f"XML gerado: {args.output}")

    if args.gerar_pdf:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gerar_py = os.path.join(script_dir, 'gerar_peticao.py')
        cmd = [sys.executable, gerar_py, '--output', args.gerar_pdf, '--corpo-arquivo', args.output]
        print(f"Gerando PDF: {args.gerar_pdf}")
        resultado = subprocess.run(cmd, capture_output=True, text=True)
        if resultado.returncode == 0:
            print(resultado.stdout)
        else:
            print(f"ERRO: {resultado.stderr}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
