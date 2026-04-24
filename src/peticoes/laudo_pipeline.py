#!/usr/bin/env python3
"""
laudo_pipeline.py — Pipeline Pós-Perícia
ACHADOS-PERICIA.json → seleciona template → claude gera rascunho → PDF timbrado

Uso:
    python3 laudo_pipeline.py [CNJ]                     # Pipeline completo
    python3 laudo_pipeline.py [CNJ] --so-template       # Só mostra template sugerido
    python3 laudo_pipeline.py [CNJ] --so-rascunho       # Gera rascunho sem PDF
    python3 laudo_pipeline.py [CNJ] --json              # Saída JSON
"""

import json
import os
import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(os.path.expanduser("~/Desktop/ANALISADOR FINAL"))
PROCESSOS_DIR = BASE_DIR / "processos"
SCRIPTS_DIR = BASE_DIR / "scripts"
MODELOS_DIR = BASE_DIR / "modelos-laudo"
CLAUDE_CLI = Path(os.path.expanduser("~/.local/bin/claude"))
CNJ_PATTERN = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')


# Mapeamento tipo de perícia → template
MAPA_TEMPLATES = {
    "acidente de trânsito": "acidente-transito",
    "acidente de trabalho": "acidente-trabalho",
    "acidentário": "acidente-trabalho",
    "securitário": "securitaria",
    "securitária": "securitaria",
    "seguro": "securitaria",
    "invalidez": "invalidez",
    "incapacidade": "incapacidade",
    "trabalhista": "trabalhista",
    "previdenciário": "previdenciario",
    "previdenciária": "previdenciario",
    "psiquiátrico": "psiquiatrica",
    "psiquiátrica": "psiquiatrica",
    "psicológico": "psiquiatrica",
    "cível": "civel",
    "dano moral": "dano-moral",
    "dano corporal": "dano-corporal",
    "indenizatório": "indenizatorio",
    "responsabilidade civil": "responsabilidade-civil",
    "erro médico": "erro-medico",
    "obstetrícia": "obstetricia",
    "ortopedia": "ortopedia",
    "neurologia": "neurologia",
}


def encontrar_pasta(cnj_ou_pasta):
    """Encontra pasta do processo."""
    # Direto
    p = Path(cnj_ou_pasta)
    if p.is_dir():
        return p

    # Por CNJ
    for pasta in PROCESSOS_DIR.iterdir():
        if pasta.is_dir() and cnj_ou_pasta in pasta.name:
            return pasta

    return None


def selecionar_template(pasta):
    """Seleciona template baseado em CLASSIFICACAO.json ou ACHADOS-PERICIA.json."""
    # Tentar ACHADOS-PERICIA.json primeiro
    achados_path = pasta / "ACHADOS-PERICIA.json"
    if achados_path.exists():
        try:
            achados = json.loads(achados_path.read_text(encoding="utf-8"))
            tipo = achados.get("tipo_pericia", "").lower()
            for chave, template in MAPA_TEMPLATES.items():
                if chave in tipo:
                    return template, f"Baseado em ACHADOS-PERICIA.json: {tipo}"
        except (json.JSONDecodeError, OSError):
            pass

    # Tentar CLASSIFICACAO.json
    class_path = pasta / "CLASSIFICACAO.json"
    if class_path.exists():
        try:
            classificacao = json.loads(class_path.read_text(encoding="utf-8"))
            tipo = classificacao.get("tipo", "").lower()
            subtipo = classificacao.get("subtipo", "").lower()
            for chave, template in MAPA_TEMPLATES.items():
                if chave in tipo or chave in subtipo:
                    return template, f"Baseado em CLASSIFICACAO.json: {tipo}/{subtipo}"
        except (json.JSONDecodeError, OSError):
            pass

    # Tentar FICHA.json
    ficha_path = pasta / "FICHA.json"
    if ficha_path.exists():
        try:
            ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
            tipo = ficha.get("tipo_pericia", "").lower()
            for chave, template in MAPA_TEMPLATES.items():
                if chave in tipo:
                    return template, f"Baseado em FICHA.json: {tipo}"
        except (json.JSONDecodeError, OSError):
            pass

    return "generico", "Nenhuma classificação encontrada, usando template genérico"


def encontrar_arquivo_template(template_id):
    """Encontra o arquivo do template nos modelos."""
    if not MODELOS_DIR.exists():
        return None

    for f in MODELOS_DIR.iterdir():
        if template_id in f.name.lower() and f.suffix in (".md", ".txt"):
            return f

    # Fallback: genérico
    for f in MODELOS_DIR.iterdir():
        if "generi" in f.name.lower() or "padrao" in f.name.lower():
            return f

    # Primeiro arquivo .md
    mds = list(MODELOS_DIR.glob("*.md"))
    return mds[0] if mds else None


def gerar_rascunho_claude(pasta, template_path, achados_path=None):
    """Gera rascunho de laudo via Claude CLI."""
    if not CLAUDE_CLI.exists():
        return {"ok": False, "erro": "Claude CLI não encontrado"}

    texto_path = pasta / "TEXTO-EXTRAIDO.txt"
    prompt_parts = []

    prompt_parts.append(f"Você é um perito médico judicial. Gere um rascunho de laudo pericial.")
    prompt_parts.append(f"Use o template em {template_path} como modelo de estrutura.")

    if texto_path.exists():
        prompt_parts.append(f"O processo está em {texto_path}.")

    if achados_path and achados_path.exists():
        prompt_parts.append(f"Os achados do exame pericial estão em {achados_path}.")

    prompt_parts.append(f"Salve o rascunho como {pasta}/LAUDO-RASCUNHO.md")
    prompt_parts.append("Estrutura obrigatória: Preâmbulo, Histórico, Exame Pericial, Discussão, Conclusão, Respostas aos Quesitos.")

    prompt = " ".join(prompt_parts)

    try:
        result = subprocess.run(
            [str(CLAUDE_CLI), "-p", prompt, "--model", "sonnet"],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode == 0:
            return {"ok": True, "saida": result.stdout[-500:]}
        else:
            return {"ok": False, "erro": result.stderr[-300:]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "erro": "Timeout (>5 min)"}
    except OSError as e:
        return {"ok": False, "erro": str(e)}


def converter_pdf(pasta):
    """Converte LAUDO-RASCUNHO.md para PDF via md_para_pdf.py."""
    md_path = pasta / "LAUDO-RASCUNHO.md"
    if not md_path.exists():
        return {"ok": False, "erro": "LAUDO-RASCUNHO.md não encontrado"}

    md_para_pdf = SCRIPTS_DIR / "md_para_pdf.py"
    if not md_para_pdf.exists():
        return {"ok": False, "erro": "md_para_pdf.py não encontrado"}

    try:
        result = subprocess.run(
            [sys.executable, str(md_para_pdf), str(md_path)],
            capture_output=True, text=True, timeout=60,
        )
        return {"ok": result.returncode == 0, "saida": result.stdout[-200:]}
    except (subprocess.TimeoutExpired, OSError) as e:
        return {"ok": False, "erro": str(e)}


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Pipeline pós-perícia: achados → laudo → PDF")
    parser.add_argument("processo", help="CNJ ou caminho da pasta")
    parser.add_argument("--so-template", action="store_true", help="Só mostra template sugerido")
    parser.add_argument("--so-rascunho", action="store_true", help="Gera rascunho sem PDF")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    pasta = encontrar_pasta(args.processo)
    if not pasta:
        print(f"Erro: processo '{args.processo}' não encontrado.")
        sys.exit(1)

    # 1. Selecionar template
    template_id, motivo = selecionar_template(pasta)
    template_path = encontrar_arquivo_template(template_id)

    resultado = {
        "cnj": args.processo,
        "pasta": str(pasta),
        "template_id": template_id,
        "template_motivo": motivo,
        "template_path": str(template_path) if template_path else None,
    }

    if args.so_template:
        if args.json:
            print(json.dumps(resultado, ensure_ascii=False, indent=2))
        else:
            print(f"Template: {template_id}")
            print(f"Motivo: {motivo}")
            print(f"Arquivo: {template_path}")
        return

    # 2. Gerar rascunho via Claude
    achados_path = pasta / "ACHADOS-PERICIA.json"
    rascunho_result = gerar_rascunho_claude(pasta, template_path, achados_path)
    resultado["rascunho"] = rascunho_result

    if args.so_rascunho or not rascunho_result.get("ok"):
        if args.json:
            print(json.dumps(resultado, ensure_ascii=False, indent=2))
        else:
            if rascunho_result.get("ok"):
                print(f"Rascunho gerado: {pasta}/LAUDO-RASCUNHO.md")
            else:
                print(f"Erro no rascunho: {rascunho_result.get('erro')}")
        return

    # 3. Converter para PDF
    pdf_result = converter_pdf(pasta)
    resultado["pdf"] = pdf_result

    if args.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        if pdf_result.get("ok"):
            print(f"Laudo gerado com sucesso:")
            print(f"  Rascunho: {pasta}/LAUDO-RASCUNHO.md")
            print(f"  PDF: gerado via md_para_pdf.py")
        else:
            print(f"Rascunho gerado mas PDF falhou: {pdf_result.get('erro')}")


if __name__ == "__main__":
    main()
