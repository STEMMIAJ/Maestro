#!/usr/bin/env python3
"""
md_para_pdf.py — Converte Markdown de petição para PDF timbrado
================================================================
Autor: Jésus Eduardo Nolêto da Penha (CRM-MG 92.148)
Versão: 1.0 — 05/03/2026

USO:
    python3 md_para_pdf.py --input peticao.md --output ACEITE-CIDADE.pdf
    python3 md_para_pdf.py --input peticao.md --xml-only --output /tmp/corpo.xml

COMO FUNCIONA:
    1. Lê arquivo Markdown
    2. Converte cada linha para XML WordML (com negrito, alinhamento, entidades)
    3. Salva XML em /tmp/corpo-peticao-auto.xml
    4. Chama gerar_peticao.py para montar DOCX + converter PDF via LibreOffice
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT = 'AppleSystemUIFont'
SZ = '26'

# === WINDOWS 11 (Parallels) ===
WIN_DESKTOP = os.path.expanduser(
    "~/Library/Group Containers/4C6364ACXT.com.parallels.desktop.appstore/"
    "Windows Disks/{a39d82e7-a1b0-4733-aace-5111a022b4d9}/"
    "[C] Windows 11.hidden/Users/jesusnoleto/Desktop"
)

# === NOMEADOR INTELIGENTE DE PETIÇÕES ===
# Detecta tipo + modificadores contextuais → nome descritivo para Windows

TIPOS_BASE = [
    (re.compile(r'ACEITE', re.IGNORECASE), 'aceite'),
    (re.compile(r'AGENDAMENTO|AGENDAR', re.IGNORECASE), 'agendamento'),
    (re.compile(r'PROPOSTA DE HONOR', re.IGNORECASE), 'proposta'),
    (re.compile(r'PRORROGA[ÇC][ÃA]O', re.IGNORECASE), 'prorrogacao'),
    (re.compile(r'REQUISI[ÇC][ÃA]O', re.IGNORECASE), 'requisicao'),
    (re.compile(r'ESCLARECIMENTO', re.IGNORECASE), 'esclarecimentos'),
    (re.compile(r'CONTESTA[ÇC][ÃA]O|IMPUGNA[ÇC][ÃA]O', re.IGNORECASE), 'contestacao'),
    (re.compile(r'ESCUSA', re.IGNORECASE), 'escusa'),
    (re.compile(r'CI[ÊE]NCIA', re.IGNORECASE), 'ciencia'),
    (re.compile(r'JUSTIFICATIVA', re.IGNORECASE), 'justificativa'),
]

MODIFICADORES = [
    (re.compile(r'mutir[ãa]o|agrupamento.*exames|deslocamento|500\s*km', re.IGNORECASE), 'mutirao'),
    (re.compile(r'majora[çc][ãa]o|majorar|tabela TJMG', re.IGNORECASE), 'majoracao'),
    (re.compile(r'condicionado|condi[çc][ãa]o de', re.IGNORECASE), 'condicionado'),
    (re.compile(r'antecipado|antecipadamente', re.IGNORECASE), 'antecipado'),
    (re.compile(r'quesitos|pertin[êe]ncia', re.IGNORECASE), 'quesitos'),
    (re.compile(r'reagend|nova data', re.IGNORECASE), 'reagendamento'),
    (re.compile(r'informa[çc][õo]es preliminares', re.IGNORECASE), 'info_preliminar'),
    (re.compile(r'indica[çc][ãa]o de perito|indico o profissional', re.IGNORECASE), 'indica_perito'),
    (re.compile(r'duas per[íi]cias|tr[êe]s per[íi]cias|nomea[çc][õo]es', re.IGNORECASE), 'plural'),
]

TABELA_NOMES = {
    ('aceite', frozenset()): 'Aceite de Encargos e Honorários Periciais',
    ('aceite', frozenset(['mutirao'])): 'Aceite de Encargos e Honorários - Aguardando Data de Mutirão',
    ('aceite', frozenset(['majoracao'])): 'Aceite de Perícia com Pedido de Majoração de Honorários',
    ('aceite', frozenset(['condicionado'])): 'Aceite Condicionado à Majoração de Honorários',
    ('aceite', frozenset(['condicionado', 'mutirao'])): 'Aceite Condicionado à Majoração - Aguardando Data de Mutirão',
    ('aceite', frozenset(['majoracao', 'mutirao'])): 'Aceite com Pedido de Majoração - Aguardando Data de Mutirão',
    ('aceite', frozenset(['info_preliminar'])): 'Aceite de Nomeação e Honorários e Informações Preliminares',
    ('aceite', frozenset(['plural'])): 'Aceite de Nomeações - Aguardando Data de Mutirão',
    ('aceite', frozenset(['plural', 'mutirao'])): 'Aceite de Nomeações - Aguardando Data de Mutirão',
    ('aceite', frozenset(['antecipado'])): 'Aceites Antecipados e Sugestões para Melhor Andamento Processual',
    ('agendamento', frozenset()): 'Agendamento de Perícia',
    ('agendamento', frozenset(['mutirao'])): 'Agendamento de Perícia - Mutirão',
    ('agendamento', frozenset(['quesitos'])): 'Agendamento de Perícia e Apreciação de Pertinência de Quesitos',
    ('agendamento', frozenset(['reagendamento'])): 'Confirmação de Data e Reagendamento de Perícia',
    ('proposta', frozenset()): 'Proposta de Honorários Periciais',
    ('prorrogacao', frozenset()): 'Prorrogação de Prazo',
    ('requisicao', frozenset()): 'Requisição de Documentos',
    ('esclarecimentos', frozenset()): 'Esclarecimentos Periciais',
    ('contestacao', frozenset()): 'Contestação de Impugnação',
    ('contestacao', frozenset(['quesitos'])): 'Contestação de Impugnação de Quesitos',
    ('escusa', frozenset()): 'Escusa do Encargo',
    ('escusa', frozenset(['indica_perito'])): 'Escusa e Indicação de Perito',
    ('ciencia', frozenset()): 'Ciência de Intimação',
    ('justificativa', frozenset()): 'Justificativa de Honorários',
}


def detectar_nome_bonito(conteudo):
    """Detecta tipo + modificadores e retorna nome descritivo para o Windows."""
    # 1. Detectar tipo base
    tipo = None
    for regex, t in TIPOS_BASE:
        if regex.search(conteudo):
            tipo = t
            break
    if not tipo:
        return 'Petição'

    # 2. Detectar modificadores
    mods = set()
    for regex, mod in MODIFICADORES:
        if regex.search(conteudo):
            mods.add(mod)

    # 3. Buscar na tabela (match exato)
    chave = (tipo, frozenset(mods))
    if chave in TABELA_NOMES:
        return TABELA_NOMES[chave]

    # 4. Fallback: tentar só com modificadores individuais
    for mod in mods:
        chave_parcial = (tipo, frozenset([mod]))
        if chave_parcial in TABELA_NOMES:
            return TABELA_NOMES[chave_parcial]

    # 5. Fallback: só o tipo
    chave_base = (tipo, frozenset())
    return TABELA_NOMES.get(chave_base, 'Petição')


def copiar_para_windows(pdf_origem, nome_bonito):
    """Copia o PDF para o Desktop do Windows 11 com nome descritivo."""
    if not os.path.isdir(WIN_DESKTOP):
        print("  ⚠ Windows 11 não acessível (Parallels desligado?)", file=sys.stderr)
        return None

    nome_arquivo = f"{nome_bonito}.pdf"
    destino = os.path.join(WIN_DESKTOP, nome_arquivo)
    shutil.copy2(pdf_origem, destino)
    return destino

# === REGRAS DE ALINHAMENTO E NEGRITO AUTOMÁTICO ===
# (regex compilado, alinhamento, forçar_negrito_linha_inteira)
REGRAS = [
    (re.compile(r'^AO JUÍZO', re.IGNORECASE), 'left', True),
    (re.compile(r'^Processo n', re.IGNORECASE), 'left', True),
    (re.compile(r'MANIFESTAÇÃO|PETIÇÃO|ACEITE DE ENCARGOS', re.IGNORECASE), 'center', True),
    (re.compile(r'^Meritíssim', re.IGNORECASE), 'left', True),
    (re.compile(r'^Termos em que'), 'left', False),
    (re.compile(r'^Pede deferimento'), 'left', False),
    (re.compile(r'^Dr\.'), 'left', False),
    (re.compile(r'^Médico'), 'left', False),
    (re.compile(r'^Membro'), 'left', False),
    (re.compile(r'^\d+ de \w+ de \d{4}'), 'left', False),
    (re.compile(r'^Governador Valadares'), 'left', False),
]

# Padrão para detectar **negrito** no Markdown
RE_BOLD = re.compile(r'\*\*(.+?)\*\*')

# Padrão para detectar IDs de documentos (ex: ID 10637847896)
RE_ID = re.compile(r'(ID\s+\d{5,})')


def escapar_xml(texto):
    """Escapa caracteres especiais para entidades XML."""
    # & primeiro para não escapar entidades já criadas
    texto = texto.replace('&', '&amp;')
    texto = texto.replace('<', '&lt;')
    texto = texto.replace('>', '&gt;')
    texto = texto.replace('"', '&quot;')
    # Caracteres acentuados → entidades numéricas
    mapa = {
        'é': '&#233;', 'ê': '&#234;', 'ã': '&#227;', 'õ': '&#245;',
        'ç': '&#231;', 'á': '&#225;', 'à': '&#224;', 'â': '&#226;',
        'í': '&#237;', 'ó': '&#243;', 'ú': '&#250;', 'ü': '&#252;',
        'É': '&#201;', 'Ê': '&#202;', 'Ã': '&#195;', 'Õ': '&#213;',
        'Ç': '&#199;', 'Á': '&#193;', 'À': '&#192;', 'Â': '&#194;',
        'Í': '&#205;', 'Ó': '&#211;', 'Ú': '&#218;', 'Ü': '&#220;',
        'ô': '&#244;', 'Ô': '&#212;',
        '–': '&#8211;', '—': '&#8212;', 'º': '&#186;', 'ª': '&#170;',
        '\u201c': '&#8220;', '\u201d': '&#8221;',
        '\u2018': '&#8216;', '\u2019': '&#8217;',
    }
    for char, entidade in mapa.items():
        texto = texto.replace(char, entidade)
    return texto


def fazer_run(texto, negrito=False):
    """Cria um <w:r> com texto, opcionalmente em negrito."""
    texto_escapado = escapar_xml(texto)
    bold_tag = '<w:b/>' if negrito else ''
    preserve = ' xml:space="preserve"' if texto.startswith(' ') or texto.endswith(' ') else ''
    return (
        f'<w:r><w:rPr>'
        f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/>'
        f'<w:sz w:val="{SZ}"/><w:szCs w:val="{SZ}"/>'
        f'{bold_tag}'
        f'</w:rPr><w:t{preserve}>{texto_escapado}</w:t></w:r>'
    )


def processar_segmentos(texto, forcar_negrito=False):
    """Converte texto com **negrito** Markdown em lista de runs XML."""
    if forcar_negrito:
        # Linha inteira em negrito, remover ** se houver
        texto_limpo = texto.replace('**', '')
        return [fazer_run(texto_limpo, negrito=True)]

    runs = []
    pos = 0
    for match in RE_BOLD.finditer(texto):
        # Texto antes do negrito
        antes = texto[pos:match.start()]
        if antes:
            # Verificar se há IDs no texto normal para colocar em negrito
            runs.extend(_processar_ids(antes))
        # Texto em negrito
        runs.append(fazer_run(match.group(1), negrito=True))
        pos = match.end()

    # Texto restante após último negrito
    restante = texto[pos:]
    if restante:
        runs.extend(_processar_ids(restante))

    # Se não tinha nenhum **, processar IDs no texto inteiro
    if not runs:
        runs.extend(_processar_ids(texto))

    return runs


def _processar_ids(texto):
    """Detecta 'ID XXXXXXX' e coloca em negrito automaticamente."""
    runs = []
    pos = 0
    for match in RE_ID.finditer(texto):
        antes = texto[pos:match.start()]
        if antes:
            runs.append(fazer_run(antes))
        runs.append(fazer_run(match.group(1), negrito=True))
        pos = match.end()
    restante = texto[pos:]
    if restante:
        runs.append(fazer_run(restante))
    return runs


def linha_para_xml(linha):
    """Converte uma linha Markdown em um parágrafo XML WordML."""
    # Linha vazia
    if not linha.strip():
        return '<w:p><w:pPr><w:spacing w:after="0"/></w:pPr></w:p>'

    # Ignorar linhas que são só metadata do modelo (# MODELO, ---, **Fonte:**, etc.)
    stripped = linha.strip()
    if stripped.startswith('# ') or stripped == '---' or stripped.startswith('## '):
        return None

    # Remover ** para testar regras de alinhamento (mas manter no texto original)
    stripped_sem_bold = stripped.replace('**', '')

    # Determinar alinhamento e negrito
    alinhamento = 'both'
    forcar_negrito = False

    for regex, align, bold in REGRAS:
        if regex.search(stripped_sem_bold):
            alinhamento = align
            forcar_negrito = bold
            break

    # Gerar runs
    runs = processar_segmentos(stripped, forcar_negrito)
    runs_xml = ''.join(runs)

    return (
        f'<w:p><w:pPr>'
        f'<w:jc w:val="{alinhamento}"/>'
        f'<w:spacing w:after="0"/>'
        f'</w:pPr>{runs_xml}</w:p>'
    )


def converter_md_para_xml(conteudo_md):
    """Converte conteúdo Markdown completo em corpo XML WordML."""
    linhas = conteudo_md.split('\n')
    paragrafos = []

    for linha in linhas:
        xml = linha_para_xml(linha)
        if xml is not None:
            paragrafos.append(xml)

    return '\n'.join(paragrafos)


def main():
    parser = argparse.ArgumentParser(description='Converte Markdown para PDF timbrado')
    parser.add_argument('--input', required=True, help='Arquivo Markdown de entrada')
    parser.add_argument('--output', required=True, help='Nome do arquivo de saída (PDF ou XML)')
    parser.add_argument('--xml-only', action='store_true', help='Gerar apenas o XML, sem PDF')
    parser.add_argument('--nome-bonito', help='Nome descritivo para o Windows (auto-detectado se omitido)')
    args = parser.parse_args()

    # Ler Markdown
    if not os.path.exists(args.input):
        print(f"ERRO: arquivo não encontrado: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Converter para XML
    corpo_xml = converter_md_para_xml(conteudo)

    if args.xml_only:
        # Salvar apenas XML
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(corpo_xml)
        print(f"XML gerado: {args.output}")
        return

    # Salvar XML temporário
    xml_tmp = '/tmp/corpo-peticao-auto.xml'
    with open(xml_tmp, 'w', encoding='utf-8') as f:
        f.write(corpo_xml)

    # Chamar gerar_peticao.py
    gerar_script = os.path.join(SCRIPT_DIR, 'gerar_peticao.py')
    nome_pdf = args.output if args.output.endswith('.pdf') else args.output + '.pdf'

    resultado = subprocess.run(
        ['python3', gerar_script, '--output', nome_pdf, '--corpo-arquivo', xml_tmp],
        capture_output=True, text=True, timeout=120
    )

    if resultado.returncode != 0:
        print(f"ERRO ao gerar PDF:\n{resultado.stderr}", file=sys.stderr)
        sys.exit(1)

    print(resultado.stdout)

    # Copiar para Windows com nome bonito
    nome_bonito = args.nome_bonito or detectar_nome_bonito(conteudo)
    pdf_gerado = os.path.join(SCRIPT_DIR, nome_pdf)
    if os.path.exists(pdf_gerado):
        destino_win = copiar_para_windows(pdf_gerado, nome_bonito)
        if destino_win:
            print(f"  → Windows: {os.path.basename(destino_win)}")


if __name__ == '__main__':
    main()
