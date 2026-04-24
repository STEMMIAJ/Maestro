#!/usr/bin/env python3
"""
gerar_aceite_rapido.py — Gera petição de aceite com 1 comando
=============================================================
Autor: Jésus Eduardo Nolêto da Penha (CRM-MG 92.148)
Versão: 1.0 — 15/03/2026

USO:
    python3 gerar_aceite_rapido.py 5000506-10.2025.8.13.0184
    python3 gerar_aceite_rapido.py 5000506-10.2025.8.13.0184 --pdf

Busca a FICHA.json do processo, preenche o template de aceite,
salva PETICAO-ACEITE.md na pasta do processo, e opcionalmente gera PDF.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

BASE_PROCESSOS = Path.home() / "Desktop" / "ANALISADOR FINAL" / "processos"
SCRIPTS_DIR = Path.home() / "Desktop" / "ANALISADOR FINAL" / "scripts"
MD_PARA_PDF = SCRIPTS_DIR / "md_para_pdf.py"

MESES = [
    "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]


def encontrar_pasta(cnj: str) -> Optional[Path]:
    """Encontra a pasta do processo pelo CNJ (busca nos dois formatos)."""
    # Formato 1: pasta com nome = CNJ
    direto = BASE_PROCESSOS / cnj
    if direto.is_dir():
        return direto

    # Formato 2: pasta "Perícia XX - Cidade - Vara" com FICHA.json contendo o CNJ
    for pasta in BASE_PROCESSOS.iterdir():
        if not pasta.is_dir():
            continue
        ficha = pasta / "FICHA.json"
        if ficha.exists():
            try:
                with open(ficha, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                if dados.get("numero_cnj") == cnj:
                    return pasta
            except (json.JSONDecodeError, KeyError):
                continue
    return None


def ler_ficha(pasta: Path) -> Dict[str, Any]:
    """Lê e retorna os dados da FICHA.json."""
    ficha = pasta / "FICHA.json"
    if not ficha.exists():
        print(f"ERRO: FICHA.json não encontrada em {pasta}", file=sys.stderr)
        sys.exit(1)
    with open(ficha, "r", encoding="utf-8") as f:
        return json.load(f)


def formatar_vara_completa(dados: Dict[str, Any]) -> str:
    """Monta o nome completo da vara (ex: 1ª VARA CCEP DA COMARCA DE CONSELHEIRO PENA)."""
    vara = dados.get("vara", "")
    comarca = dados.get("comarca", "")
    if vara and comarca:
        return "{} DA COMARCA DE {}".format(vara.upper(), comarca.upper())
    if vara:
        return vara.upper()
    return "[NÃO ENCONTRADO]"


def formatar_data() -> str:
    """Retorna a data atual formatada (ex: 15 de março de 2026)."""
    hoje = datetime.now()
    return "{} de {} de {}".format(hoje.day, MESES[hoje.month], hoje.year)


def detectar_genero_juiz(dados: Dict[str, Any]) -> str:
    """Tenta detectar gênero do juiz. Retorna tratamento ou marcador."""
    # FICHA.json não tem esse campo — marcar para preenchimento manual
    return "[NÃO ENCONTRADO — verificar gênero do juiz no despacho]"


def gerar_aceite(dados: Dict[str, Any]) -> str:
    """Gera o texto da petição de aceite a partir dos dados da FICHA.json."""
    vara_completa = formatar_vara_completa(dados)
    cnj = dados.get("numero_cnj", "[NÃO ENCONTRADO]")
    genero = detectar_genero_juiz(dados)
    data_atual = formatar_data()

    # Honorários
    valor_hon = dados.get("honorarios", {}).get("valor", 0)
    if valor_hon and valor_hon > 0:
        valor_str = "R$ {:.2f}".format(valor_hon).replace(".", ",")
    else:
        valor_str = "[NÃO ENCONTRADO — verificar valor no despacho]"

    # ID do documento
    id_doc = "[NÃO ENCONTRADO — verificar ID no PJe]"

    texto = """AO JUÍZO DA {vara} – MG

**Processo nº: {cnj}**

MANIFESTAÇÃO – ACEITE DE ENCARGO E HONORÁRIOS

**{genero}**,

Em atenção ao documento de **ID {id_doc}**, venho ratificar meu aceite dos encargos e honorários periciais, já fixados em {valor}.

Aguardo os trâmites necessários para prosseguir com o agendamento da perícia médica, caso não haja suspeição ou impedimento sobre minha atuação.

Termos em que,
Pede deferimento.

Dr. Jésus Eduardo Nolêto da Penha
Médico – Perito Judicial – CRM-MG 92.148
Membro da ABMLPM – Associação Brasileira de Medicina Legal e Perícia Médica

{data},
Governador Valadares – MG.""".format(
        vara=vara_completa,
        cnj=cnj,
        genero=genero,
        id_doc=id_doc,
        valor=valor_str,
        data=data_atual,
    )
    return texto


def main():
    parser = argparse.ArgumentParser(
        description="Gera petição de aceite a partir da FICHA.json do processo"
    )
    parser.add_argument("cnj", help="Número CNJ do processo")
    parser.add_argument(
        "--pdf", action="store_true",
        help="Gerar PDF via md_para_pdf.py (requer LibreOffice)"
    )
    args = parser.parse_args()

    cnj = args.cnj.strip()

    # 1. Encontrar pasta
    pasta = encontrar_pasta(cnj)
    if pasta is None:
        print("ERRO: pasta não encontrada para CNJ {}".format(cnj), file=sys.stderr)
        print("  Procurei em: {}".format(BASE_PROCESSOS), file=sys.stderr)
        sys.exit(1)
    print("[OK] Pasta: {}".format(pasta.name))

    # 2. Ler FICHA.json
    dados = ler_ficha(pasta)
    print("[OK] FICHA.json lida — {} | {} | {}".format(
        dados.get("comarca", "?"), dados.get("vara", "?"), cnj
    ))

    # 3. Gerar texto
    texto = gerar_aceite(dados)

    # 4. Salvar .md
    saida_md = pasta / "PETICAO-ACEITE.md"
    with open(saida_md, "w", encoding="utf-8") as f:
        f.write(texto)
    print("[OK] Salvo: {}".format(saida_md))

    # 5. Gerar PDF (se solicitado e se md_para_pdf.py existir)
    if args.pdf:
        if MD_PARA_PDF.exists():
            nome_pdf = "ACEITE-{}.pdf".format(cnj)
            saida_pdf = pasta / nome_pdf
            print("[...] Gerando PDF...")
            resultado = subprocess.run(
                ["python3", str(MD_PARA_PDF), "--input", str(saida_md), "--output", str(saida_pdf)],
                capture_output=True, text=True, timeout=120
            )
            if resultado.returncode == 0:
                print("[OK] PDF: {}".format(saida_pdf))
                if resultado.stdout.strip():
                    print("     {}".format(resultado.stdout.strip()))
            else:
                print("[ERRO] Falha ao gerar PDF:", file=sys.stderr)
                print(resultado.stderr, file=sys.stderr)
        else:
            print("[AVISO] md_para_pdf.py não encontrado — apenas .md gerado")

    # 6. Resumo
    print()
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)
    print("  Processo:  {}".format(cnj))
    print("  Comarca:   {}".format(dados.get("comarca", "?")))
    print("  Vara:      {}".format(dados.get("vara", "?")))
    print("  Área:      {}".format(dados.get("area", "?")))
    print("  Arquivo:   {}".format(saida_md.name))

    # Alertar sobre campos não preenchidos
    alertas = []  # type: List[str]
    if "[NÃO ENCONTRADO" in texto:
        import re
        campos = re.findall(r'\[NÃO ENCONTRADO[^]]*\]', texto)
        alertas = list(set(campos))
    if alertas:
        print()
        print("  ATENÇÃO — campos para preencher manualmente:")
        for a in alertas:
            print("    - {}".format(a))
    print("=" * 60)


if __name__ == "__main__":
    main()
