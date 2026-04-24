#!/usr/bin/env python3
"""
Gerador de Petição de Aceite
Usa o template DOCX original (com header timbrado, logo, footer).
Só troca os dados variáveis. Formatação fica intacta.
"""

import os
import sys
import subprocess
from datetime import date
from docx import Document
from num2words import num2words

TEMPLATE = os.path.expanduser(
    "~/Desktop/analisador de processos/templates/template-aceite.docx"
)
OUTPUT_DIR = os.path.expanduser("~/Desktop/analisador de processos")

MESES = [
    "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]


def valor_por_extenso(valor: float) -> str:
    reais = int(valor)
    centavos = round((valor - reais) * 100)

    if reais == 0 and centavos > 0:
        return f"{num2words(centavos, lang='pt_BR')} centavos"
    elif centavos == 0:
        if reais == 1:
            return "um real"
        return f"{num2words(reais, lang='pt_BR')} reais"
    else:
        parte_reais = f"{num2words(reais, lang='pt_BR')} {'real' if reais == 1 else 'reais'}"
        parte_centavos = f"{num2words(centavos, lang='pt_BR')} centavos"
        return f"{parte_reais} e {parte_centavos}"


def preencher_template(vara_num, vara_tipo, comarca, processo, id_doc, valor, data_hoje):
    doc = Document(TEMPLATE)

    reais = int(valor)
    centavos = round((valor - reais) * 100)
    extenso = valor_por_extenso(valor)

    substituicoes_p1 = {
        "{{VARA_NUM}}": str(vara_num),
        "{{VARA_TIPO}}": vara_tipo.upper(),
        "{{COMARCA}}": comarca.upper(),
    }

    substituicoes_p3 = {
        "{{PROCESSO}}": processo,
    }

    substituicoes_p7 = {
        "{{ID_DOC}}": id_doc,
        "{{VALOR_INT}}": str(reais),
        ",{{VALOR_CENT}} (": f",{centavos:02d} (",
        "{{VALOR_EXTENSO}}": extenso,
    }

    substituicoes_p19 = {
        "{{DIA}}": str(data_hoje.day),
        "{{MES}}": MESES[data_hoje.month],
        " de {{ANO}}, ": f" de {data_hoje.year}, ",
    }

    mapa = {
        1: substituicoes_p1,
        3: substituicoes_p3,
        7: substituicoes_p7,
        19: substituicoes_p19,
    }

    for idx_p, subs in mapa.items():
        para = doc.paragraphs[idx_p]
        for run in para.runs:
            for placeholder, valor_novo in subs.items():
                if placeholder in run.text:
                    run.text = run.text.replace(placeholder, valor_novo)

    return doc


def main():
    print("=" * 50)
    print("  GERADOR DE PETIÇÃO DE ACEITE")
    print("=" * 50)
    print()

    vara_num = input("Vara (número, ex: 6): ").strip()
    vara_tipo = input("Tipo da vara [Cível]: ").strip() or "Cível"
    comarca = input("Comarca [Governador Valadares]: ").strip() or "Governador Valadares"
    processo = input("Número do processo: ").strip()
    id_doc = input("ID + descrição do documento (ex: 10596334263 - Outros Documentos (NOMEAÇÃO PERITO AJ)): ").strip()

    valor_str = input("Valor dos honorários (ex: 612 ou 612.50): ").strip()
    valor = float(valor_str.replace(",", "."))

    usar_hoje = input(f"Data [hoje = {date.today().strftime('%d/%m/%Y')}] (Enter = hoje, ou dd/mm/aaaa): ").strip()
    if usar_hoje:
        partes = usar_hoje.split("/")
        data_hoje = date(int(partes[2]), int(partes[1]), int(partes[0]))
    else:
        data_hoje = date.today()

    print()
    print(f"Vara: {vara_num}ª Vara {vara_tipo}")
    print(f"Comarca: {comarca}")
    print(f"Processo: {processo}")
    print(f"ID documento: {id_doc}")
    print(f"Valor: R$ {valor:,.2f} ({valor_por_extenso(valor)})")
    print(f"Data: {data_hoje.day} de {MESES[data_hoje.month]} de {data_hoje.year}")
    print()

    nome_arquivo = f"ACEITE-{processo}.docx"
    caminho_saida = os.path.join(OUTPUT_DIR, nome_arquivo)

    doc = preencher_template(vara_num, vara_tipo, comarca, processo, id_doc, valor, data_hoje)
    doc.save(caminho_saida)

    print(f"Arquivo gerado: {caminho_saida}")
    print()

    subprocess.run(["open", caminho_saida])
    print("Pronto! O arquivo foi aberto.")


if __name__ == "__main__":
    main()
