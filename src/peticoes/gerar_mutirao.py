#!/usr/bin/env python3
"""
gerar_mutirao.py — Gera petição de mutirão de perícias
=======================================================
Autor: Jésus Eduardo Nolêto da Penha (CRM-MG 92.148)
Versão: 1.0 — 22/03/2026

USO:
    python3 gerar_mutirao.py --comarca "Taiobeiras" --data "07/04/2026" --local "Fórum" --cnjs 5000123-45.2025.8.13.0680 5000456-78.2025.8.13.0680
    python3 gerar_mutirao.py --comarca "Taiobeiras" --data "07/04/2026" --local "Fórum" --cnjs-arquivo lista.txt
    python3 gerar_mutirao.py --comarca "Taiobeiras" --data "07/04/2026" --local "Fórum" --cnjs-arquivo lista.txt --pdf
    python3 gerar_mutirao.py --comarca "Taiobeiras" --data "07/04/2026" --local "Fórum" --cnjs-arquivo lista.txt --horario-inicio 13:00 --intervalo 45

Gera petição de mutirão com horários automáticos (30 min entre cada).
Busca vara de cada processo na FICHA.json ou DataJud.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple

BASE_PROCESSOS = Path.home() / "Desktop" / "ANALISADOR FINAL" / "analisador de processos" / "processos"
SCRIPTS_DIR = Path.home() / "Desktop" / "ANALISADOR FINAL" / "scripts"
MD_PARA_XML = SCRIPTS_DIR / "md_para_xml_peticao.py"
GERAR_PDF = SCRIPTS_DIR / "gerar_peticao.py"
SAIDA_DIR = Path.home() / "Desktop" / "ANALISADOR FINAL" / "analisador de processos" / "PETIÇÕES COWORK"

MESES = [
    "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]


def buscar_vara(cnj: str) -> str:
    """Busca a vara do processo na FICHA.json."""
    for pasta in BASE_PROCESSOS.iterdir():
        if not pasta.is_dir():
            continue
        ficha = pasta / "FICHA.json"
        if ficha.exists():
            try:
                with open(ficha, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                if dados.get("numero_cnj") == cnj:
                    return dados.get("vara", "[VARA]")
            except (json.JSONDecodeError, KeyError):
                continue
    return "[VARA — verificar no PJe]"


def formatar_data_extenso(data_str: str) -> str:
    """Converte '07/04/2026' para '07 de abril de 2026'."""
    try:
        dt = datetime.strptime(data_str, "%d/%m/%Y")
        return "{} de {} de {}".format(dt.day, MESES[dt.month], dt.year)
    except ValueError:
        return data_str


def gerar_horarios(inicio: str, intervalo: int, quantidade: int) -> List[str]:
    """Gera lista de horários com intervalo em minutos."""
    try:
        h, m = map(int, inicio.split(":"))
        base = datetime(2026, 1, 1, h, m)
    except (ValueError, IndexError):
        base = datetime(2026, 1, 1, 13, 0)

    horarios = []
    for i in range(quantidade):
        t = base + timedelta(minutes=intervalo * i)
        horarios.append(t.strftime("%H:%M"))
    return horarios


def gerar_texto_mutirao(
    comarca: str,
    data: str,
    local: str,
    processos: List[Tuple[str, str]],
    horarios: List[str]
) -> str:
    """Gera o texto da petição de mutirão."""
    data_extenso = formatar_data_extenso(data)

    linhas_processos = []
    for i, ((cnj, vara), horario) in enumerate(zip(processos, horarios)):
        linhas_processos.append(
            "- **{}** ({}) – às **{} horas**".format(cnj, vara, horario)
        )

    texto = """Aos Excelentíssimos Senhores Doutores Juízes das Varas da Comarca de {comarca} – MG e da Justiça Federal

Tendo em vista o mutirão de perícias médicas a ser realizado no {local}, no dia **{data}**, ficam designados os seguintes horários:

{processos}

Solicito que as partes sejam devidamente intimadas.

Atenciosamente,

Dr. Jésus Eduardo Nolêto da Penha
Médico – Perito Judicial – CRM-MG 92.148
Membro da ABMLPM – Associação Brasileira de Medicina Legal e Perícia Médica

Governador Valadares – MG, {data_extenso}.""".format(
        comarca=comarca,
        local=local,
        data=data,
        processos="\n".join(linhas_processos),
        data_extenso=data_extenso,
    )
    return texto


def main():
    parser = argparse.ArgumentParser(
        description="Gera petição de mutirão de perícias"
    )
    parser.add_argument("--comarca", required=True, help="Nome da comarca")
    parser.add_argument("--data", required=True, help="Data do mutirão (DD/MM/AAAA)")
    parser.add_argument("--local", default="Prédio do Fórum desta Comarca",
                        help="Local do mutirão (padrão: Fórum)")
    parser.add_argument("--cnjs", nargs="+", help="Lista de CNJs")
    parser.add_argument("--cnjs-arquivo", help="Arquivo com CNJs (um por linha)")
    parser.add_argument("--horario-inicio", default="13:00",
                        help="Horário da primeira perícia (padrão: 13:00)")
    parser.add_argument("--intervalo", type=int, default=30,
                        help="Intervalo em minutos entre perícias (padrão: 30)")
    parser.add_argument("--pdf", action="store_true",
                        help="Gerar PDF com timbrado")
    parser.add_argument("--output", help="Nome do arquivo de saída (sem extensão)")

    args = parser.parse_args()

    # Coletar CNJs
    cnjs = []
    if args.cnjs:
        cnjs = args.cnjs
    elif args.cnjs_arquivo:
        with open(args.cnjs_arquivo, "r") as f:
            cnjs = [linha.strip() for linha in f if linha.strip()]
    else:
        print("ERRO: forneça --cnjs ou --cnjs-arquivo", file=sys.stderr)
        sys.exit(1)

    if not cnjs:
        print("ERRO: nenhum CNJ fornecido", file=sys.stderr)
        sys.exit(1)

    print("[INFO] Mutirão: {} processos em {} no dia {}".format(
        len(cnjs), args.comarca, args.data
    ))

    # Buscar varas
    processos = []
    for cnj in cnjs:
        vara = buscar_vara(cnj)
        processos.append((cnj, vara))
        print("  {} → {}".format(cnj, vara))

    # Gerar horários
    horarios = gerar_horarios(args.horario_inicio, args.intervalo, len(cnjs))

    # Gerar texto
    texto = gerar_texto_mutirao(args.comarca, args.data, args.local, processos, horarios)

    # Nome do arquivo
    data_limpa = args.data.replace("/", "-")
    comarca_limpa = args.comarca.replace(" ", "-")
    nome_base = args.output or "MUTIRAO-{}-{}".format(comarca_limpa, data_limpa)

    # Salvar MD
    saida_md = SAIDA_DIR / "{}.md".format(nome_base)
    saida_md.parent.mkdir(parents=True, exist_ok=True)
    with open(saida_md, "w", encoding="utf-8") as f:
        f.write(texto)
    print("\n[OK] Salvo: {}".format(saida_md))

    # Gerar PDF
    if args.pdf and GERAR_PDF.exists():
        saida_pdf = SAIDA_DIR / "{}.pdf".format(nome_base)
        # Converter MD → XML
        xml_tmp = "/tmp/mutirao-corpo.xml"
        if MD_PARA_XML.exists():
            r1 = subprocess.run(
                ["python3", str(MD_PARA_XML), str(saida_md), xml_tmp],
                capture_output=True, text=True, timeout=30
            )
            if r1.returncode != 0:
                print("[AVISO] Erro ao converter MD→XML: {}".format(r1.stderr))
                print("[INFO] Apenas .md gerado")
                return

        print("[...] Gerando PDF com timbrado...")
        r2 = subprocess.run(
            ["python3", str(GERAR_PDF), "--output", str(saida_pdf), "--corpo-arquivo", xml_tmp],
            capture_output=True, text=True, timeout=120
        )
        if r2.returncode == 0:
            print("[OK] PDF: {}".format(saida_pdf))
        else:
            print("[ERRO] {}".format(r2.stderr))

    # Resumo
    print()
    print("=" * 60)
    print("MUTIRÃO — {}".format(args.comarca))
    print("=" * 60)
    print("  Data:       {}".format(args.data))
    print("  Local:      {}".format(args.local))
    print("  Processos:  {}".format(len(cnjs)))
    print("  Início:     {}".format(args.horario_inicio))
    print("  Intervalo:  {} min".format(args.intervalo))
    for (cnj, vara), h in zip(processos, horarios):
        print("  {} {} → {}".format(h, cnj, vara))
    print("=" * 60)

    # Alertas
    alertas = [cnj for cnj, vara in processos if "[VARA" in vara]
    if alertas:
        print("\n  ATENÇÃO — varas não encontradas (verificar no PJe):")
        for cnj in alertas:
            print("    - {}".format(cnj))


if __name__ == "__main__":
    main()
