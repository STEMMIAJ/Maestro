#!/usr/bin/env python3
"""
usar_template_pericia.py

Copia template de laudo pericial e substitui placeholders {{CHAVE}}
com dados de FICHA.json (se existir na mesma pasta do output).

Uso:
    python3 usar_template_pericia.py --tipo acidente --cnj 0001234-56.2026.5.03.0001 \\
            --output ~/Desktop/_MESA/10-PERICIA/laudos/0001234/laudo.md

Tipos disponiveis:
    acidente      -> formatos-laudo/acidente-trabalho.md
    securitario   -> formatos-laudo/securitario-invalidez.md
    inss          -> formatos-laudo/inss.md  (a criar)

FICHA.json esperado (na pasta do --output):
    {
        "NOME_PERICIANDO": "Fulano de Tal",
        "DATA_NASCIMENTO": "01/01/1980",
        "IDADE": "45",
        "PROFISSAO": "Pedreiro",
        "DATA_EXAME": "20/04/2026",
        "LOCAL_EXAME": "Governador Valadares/MG",
        "VARA": "1a Vara do Trabalho de GV",
        "REQUERENTE": "...",
        "REQUERIDO": "...",
        "DATA_ACIDENTE": "10/05/2025",
        "CID_PRINCIPAL": "M54.5"
    }

CNJ vem da linha de comando e sobrescreve qualquer CNJ do FICHA.json.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

TEMPLATES_ROOT = Path.home() / "Desktop" / "_MESA" / "10-PERICIA" / "templates-reaproveitaveis"

TIPO_MAP = {
    "acidente": "formatos-laudo/acidente-trabalho.md",
    "securitario": "formatos-laudo/securitario-invalidez.md",
    "inss": "formatos-laudo/inss.md",
}

PLACEHOLDER_RE = re.compile(r"\{\{([A-Z_][A-Z0-9_]*)\}\}")


def carregar_ficha(output_path: Path) -> dict:
    ficha = output_path.parent / "FICHA.json"
    if ficha.exists():
        try:
            return json.loads(ficha.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[aviso] FICHA.json invalido ({e}). Placeholders ficarao vazios.", file=sys.stderr)
    return {}


def substituir(conteudo: str, dados: dict):
    nao_preenchidos = set()

    def repl(m):
        chave = m.group(1)
        if chave in dados and dados[chave] not in (None, ""):
            return str(dados[chave])
        nao_preenchidos.add(chave)
        return m.group(0)  # mantem placeholder

    novo = PLACEHOLDER_RE.sub(repl, conteudo)
    return novo, sorted(nao_preenchidos)


def main():
    ap = argparse.ArgumentParser(description="Aplica template de laudo pericial")
    ap.add_argument("--tipo", required=True, choices=list(TIPO_MAP.keys()),
                    help="tipo de laudo (acidente/securitario/inss)")
    ap.add_argument("--cnj", required=True, help="numero CNJ do processo")
    ap.add_argument("--output", required=True, help="caminho do laudo de saida (.md)")
    ap.add_argument("--force", action="store_true", help="sobrescrever se ja existir")
    args = ap.parse_args()

    template_rel = TIPO_MAP[args.tipo]
    template_path = TEMPLATES_ROOT / template_rel
    if not template_path.exists():
        print(f"[erro] template nao encontrado: {template_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output).expanduser().resolve()
    if output_path.exists() and not args.force:
        print(f"[erro] output ja existe: {output_path}. Use --force para sobrescrever.", file=sys.stderr)
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    dados = carregar_ficha(output_path)
    dados["CNJ"] = args.cnj  # CNJ da CLI sempre vence

    conteudo = template_path.read_text(encoding="utf-8")
    novo, faltando = substituir(conteudo, dados)
    output_path.write_text(novo, encoding="utf-8")

    print(f"[ok] laudo gerado: {output_path}")
    print(f"     template: {template_path}")
    if not (output_path.parent / "FICHA.json").exists():
        print(f"     FICHA.json ausente em {output_path.parent}/ -- placeholders vazios.")
    if faltando:
        print(f"[aviso] placeholders nao preenchidos ({len(faltando)}): {', '.join(faltando)}")
    else:
        print("[ok] todos placeholders preenchidos.")


if __name__ == "__main__":
    main()
