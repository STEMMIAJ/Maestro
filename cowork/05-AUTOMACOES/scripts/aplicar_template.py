#!/usr/bin/env python3
"""
aplicar_template.py — Motor de preenchimento de templates do cowork.

Lê um TEMPLATE.md do cowork/02-BIBLIOTECA/ + FICHA.json do caso,
substitui {{placeholders}} e blocos {{#lista:...}}, grava MD preenchido
em 01-CASOS-ATIVOS/<CNJ>/peticoes-geradas/.

Uso:
  python3 aplicar_template.py --template <path> --ficha <path> [--saida <path>] [--data "DD de MÊS de AAAA"]

Dependências: somente stdlib.

ref: consultar ~/Desktop/STEMMIA Dexter/PYTHON-BASE/ antes de estender.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

__version__ = "0.2.0"  # 0.2.0 = + bloco condicional + rastreabilidade

MESES_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def data_por_extenso(d: date | None = None) -> str:
    d = d or date.today()
    return f"{d.day:d} de {MESES_PT[d.month - 1]} de {d.year:d}"


def dot_get(obj: dict | list, path: str):
    """Navega path 'a.b.c' em dict/list aninhado. Lança KeyError com caminho."""
    cur = obj
    for parte in path.split("."):
        if isinstance(cur, list):
            try:
                cur = cur[int(parte)]
            except (ValueError, IndexError):
                raise KeyError(f"índice inválido '{parte}' em path '{path}'")
        elif isinstance(cur, dict):
            if parte not in cur:
                raise KeyError(f"chave '{parte}' ausente em path '{path}'")
            cur = cur[parte]
        else:
            raise KeyError(f"não-container ao tentar acessar '{parte}' em '{path}'")
    return cur


# Pattern para placeholders simples: {{a.b}}
RE_SIMPLES = re.compile(r"\{\{([a-zA-Z0-9_.]+)\}\}")

# Pattern para blocos lista: {{#lista:path:prefixo="X":separador="Y"}}
# Aspas duplas nos valores. Prefixo e separador opcionais.
RE_LISTA = re.compile(
    r'\{\{#lista:(?P<path>[a-zA-Z0-9_.]+)'
    r'(?::prefixo="(?P<prefixo>[^"]*)")?'
    r'(?::separador="(?P<separador>[^"]*)")?'
    r'\}\}'
)

# Bloco condicional: {{#se:path}}...{{/se}} e {{#se-nao:path}}...{{/se-nao}}
# Não aninhável (MVP). Usa DOTALL para conteúdo multilinha.
RE_SE = re.compile(
    r'\{\{#se:(?P<path>[a-zA-Z0-9_.]+)\}\}(?P<corpo>.*?)\{\{/se\}\}',
    re.DOTALL,
)
RE_SE_NAO = re.compile(
    r'\{\{#se-nao:(?P<path>[a-zA-Z0-9_.]+)\}\}(?P<corpo>.*?)\{\{/se-nao\}\}',
    re.DOTALL,
)


def _truthy(v) -> bool:
    """Falsey: None, False, '', [], {}, 0. Resto é truthy."""
    if v is None or v is False:
        return False
    if isinstance(v, (str, list, dict)) and len(v) == 0:
        return False
    if isinstance(v, (int, float)) and v == 0:
        return False
    return True


def preencher(template: str, ficha: dict, data_hoje: str) -> tuple[str, list[str]]:
    """
    Retorna (texto_preenchido, lista_de_problemas).
    Problemas não interrompem: o placeholder vira [[FALTA:path]] e sistema sinaliza.
    """
    problemas: list[str] = []

    def resolver_lista(m: re.Match) -> str:
        path = m.group("path")
        prefixo = m.group("prefixo") or ""
        separador = m.group("separador") or ", "
        try:
            valor = dot_get(ficha, path)
        except KeyError as e:
            problemas.append(f"lista: {e}")
            return f"[[FALTA:{path}]]"
        if not isinstance(valor, list):
            problemas.append(f"lista: '{path}' não é lista (é {type(valor).__name__})")
            return f"[[TIPO:{path}]]"
        if not valor:
            problemas.append(f"lista: '{path}' está vazia")
            return f"[[VAZIA:{path}]]"
        return prefixo + separador.join(str(v) for v in valor)

    def resolver_simples(m: re.Match) -> str:
        path = m.group(1)
        # Placeholders especiais do sistema
        if path == "data.por_extenso":
            return data_hoje
        try:
            valor = dot_get(ficha, path)
        except KeyError as e:
            problemas.append(f"simples: {e}")
            return f"[[FALTA:{path}]]"
        return str(valor)

    def resolver_se(m: re.Match) -> str:
        path = m.group("path")
        corpo = m.group("corpo")
        try:
            valor = dot_get(ficha, path)
        except KeyError:
            # Condicional sobre chave ausente: trata como falsey (sem warning)
            return ""
        return corpo if _truthy(valor) else ""

    def resolver_se_nao(m: re.Match) -> str:
        path = m.group("path")
        corpo = m.group("corpo")
        try:
            valor = dot_get(ficha, path)
        except KeyError:
            return corpo  # Chave ausente = se-nao verdadeiro
        return "" if _truthy(valor) else corpo

    # Ordem importa: condicionais primeiro (podem remover blocos inteiros),
    # listas depois (sintaxe mais específica que placeholders simples), simples por último.
    texto = RE_SE.sub(resolver_se, template)
    texto = RE_SE_NAO.sub(resolver_se_nao, texto)
    texto = RE_LISTA.sub(resolver_lista, texto)
    texto = RE_SIMPLES.sub(resolver_simples, texto)
    return texto, problemas


def extrair_corpo(template_texto: str) -> str:
    """Remove frontmatter YAML (--- ... ---) do início do template."""
    if template_texto.startswith("---\n"):
        fim = template_texto.find("\n---\n", 4)
        if fim != -1:
            return template_texto[fim + 5 :].lstrip("\n")
    return template_texto


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--template", required=True, help="Caminho do TEMPLATE.md")
    p.add_argument("--ficha", required=True, help="Caminho da FICHA.json")
    p.add_argument("--saida", help="Caminho do MD de saída (default: stdout)")
    p.add_argument("--data", help='Data por extenso forçada (ex: "17 de março de 2026")')
    p.add_argument("--dry-run", action="store_true", help="Não grava, só imprime")
    args = p.parse_args(argv)

    tpl = Path(args.template).read_text(encoding="utf-8")
    corpo = extrair_corpo(tpl)
    ficha = json.loads(Path(args.ficha).read_text(encoding="utf-8"))
    data_hoje = args.data or data_por_extenso()

    texto, problemas = preencher(corpo, ficha, data_hoje)

    # Rastreabilidade: comentário HTML ao fim
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    rastro = (
        f"\n\n<!-- gerado por aplicar_template.py v{__version__} em {stamp} "
        f"| template={args.template} | ficha={args.ficha} -->\n"
    )
    texto = texto.rstrip() + rastro

    if problemas:
        print("=== PROBLEMAS DETECTADOS ===", file=sys.stderr)
        for pr in problemas:
            print(f"  - {pr}", file=sys.stderr)
        print("=== FIM ===", file=sys.stderr)

    if args.saida and not args.dry_run:
        Path(args.saida).parent.mkdir(parents=True, exist_ok=True)
        Path(args.saida).write_text(texto, encoding="utf-8")
        print(f"Gravado: {args.saida}", file=sys.stderr)
    else:
        sys.stdout.write(texto)

    return 0 if not problemas else 2  # 2 = warnings (não fatal)


if __name__ == "__main__":
    sys.exit(main())
