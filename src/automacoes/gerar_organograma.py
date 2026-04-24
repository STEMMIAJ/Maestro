#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_organograma.py

Gera ORGANOGRAMA.html a partir de ORGANOGRAMA-dados.json para o hub STEMMIA Dexter.

Uso:
    python3 gerar_organograma.py

Defaults:
    --json    ~/Desktop/STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA-dados.json
    --saida   ~/Desktop/STEMMIA Dexter/00-CONTROLE/ORGANOGRAMA.html
    template  ~/Desktop/STEMMIA Dexter/src/automacoes/organograma_template.html

Se o JSON estiver vazio/malformado, aborta SEM sobrescrever (exit 2).
Se o HTML de destino existir, cria backup com sufixo .bak-YYYYMMDD-HHMMSS.

Mantem o mesmo visual do HTML feito manualmente em 20/abr/2026:
- D3.js v7 carregado de assets/d3.v7.min.js (local, relativo ao HTML)
- Grafo force-directed com zoom/pan/drag
- Sidebar com busca + filtros de camada e status
- Painel de detalhes lateral
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import shutil
import sys
from pathlib import Path


HOME = Path.home()
BASE_CONTROLE = HOME / "Desktop" / "STEMMIA Dexter" / "00-CONTROLE"
DEFAULT_JSON = BASE_CONTROLE / "ORGANOGRAMA-dados.json"
DEFAULT_HTML = BASE_CONTROLE / "ORGANOGRAMA.html"
DEFAULT_TEMPLATE = (
    HOME / "Desktop" / "STEMMIA Dexter" / "src" / "automacoes"
    / "organograma_template.html"
)

PLACEHOLDER_DADOS = "__DADOS_JSON__"
PLACEHOLDER_SUBCOUNTS = "__SUBCOUNTS__"
PLACEHOLDER_DATA = "__DATA_GERACAO__"


def carregar_dados(json_path: Path) -> dict:
    """Le e valida o JSON de dados. Levanta ValueError se invalido/vazio."""
    if not json_path.exists():
        raise FileNotFoundError(f"JSON nao encontrado: {json_path}")

    raw = json_path.read_text(encoding="utf-8").strip()
    if not raw:
        raise ValueError("JSON esta vazio")

    try:
        dados = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON malformado: {e}") from e

    if not isinstance(dados, dict):
        raise ValueError("JSON raiz nao e um objeto")

    for chave in ("camadas", "nos", "ligacoes"):
        if chave not in dados:
            raise ValueError(f"JSON sem chave obrigatoria: {chave!r}")
        if not isinstance(dados[chave], list):
            raise ValueError(f"Chave {chave!r} deveria ser lista")

    if not dados["nos"]:
        raise ValueError("Lista 'nos' esta vazia")
    if not dados["camadas"]:
        raise ValueError("Lista 'camadas' esta vazia")

    return dados


def carregar_template(template_path: Path) -> str:
    """Le o template HTML. Valida que contem os placeholders esperados."""
    if not template_path.exists():
        raise FileNotFoundError(f"Template nao encontrado: {template_path}")

    tpl = template_path.read_text(encoding="utf-8")
    faltando = [
        p for p in (PLACEHOLDER_DADOS, PLACEHOLDER_SUBCOUNTS, PLACEHOLDER_DATA)
        if p not in tpl
    ]
    if faltando:
        raise ValueError(
            f"Template sem placeholders obrigatorios: {faltando}"
        )
    return tpl


def contar_fluxos(dados: dict) -> int:
    """Conta quantos nos pertencem a camada 'fluxos'."""
    return sum(1 for n in dados["nos"] if n.get("camada") == "fluxos")


def fazer_backup(html_path: Path) -> Path | None:
    """Se o HTML existir, cria copia com sufixo .bak-YYYYMMDD-HHMMSS."""
    if not html_path.exists():
        return None
    timestamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = html_path.with_name(html_path.name + f".bak-{timestamp}")
    shutil.copy2(html_path, backup_path)
    return backup_path


def renderizar(template: str, dados: dict) -> str:
    """Substitui placeholders no template. ensure_ascii=False preserva acentos."""
    dados_json = json.dumps(dados, ensure_ascii=False)
    subcounts = (
        f"{len(dados['nos'])} nos &middot; "
        f"{len(dados['ligacoes'])} ligacoes &middot; "
        f"{contar_fluxos(dados)} fluxos &middot; "
        f"{len(dados['camadas'])} camadas"
    )
    data_geracao = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    html = template
    html = html.replace(PLACEHOLDER_DADOS, dados_json)
    html = html.replace(PLACEHOLDER_SUBCOUNTS, subcounts)
    html = html.replace(PLACEHOLDER_DATA, data_geracao)
    return html


def validar_html_basico(html: str) -> list[str]:
    """Checagens minimas de sintaxe. Retorna lista de erros (vazia = ok)."""
    erros: list[str] = []
    marcadores = ("<!DOCTYPE html>", "<html", "<body", "</body>", "</html>")
    for m in marcadores:
        if m not in html:
            erros.append(f"marcador ausente: {m}")
    # Parse conservador via html.parser
    try:
        from html.parser import HTMLParser

        class _Check(HTMLParser):
            def error(self, message):  # pragma: no cover
                raise ValueError(message)

        _Check().feed(html)
    except Exception as e:
        erros.append(f"html.parser erro: {e}")
    return erros


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Gera ORGANOGRAMA.html a partir de ORGANOGRAMA-dados.json."
    )
    parser.add_argument(
        "--json", type=Path, default=DEFAULT_JSON,
        help=f"Path do JSON de dados (default: {DEFAULT_JSON})",
    )
    parser.add_argument(
        "--saida", type=Path, default=DEFAULT_HTML,
        help=f"Path do HTML de saida (default: {DEFAULT_HTML})",
    )
    parser.add_argument(
        "--template", type=Path, default=DEFAULT_TEMPLATE,
        help=f"Path do template (default: {DEFAULT_TEMPLATE})",
    )
    parser.add_argument(
        "--sem-backup", action="store_true",
        help="Nao cria backup do HTML anterior (padrao: cria).",
    )
    args = parser.parse_args(argv)

    json_path: Path = args.json.expanduser()
    html_path: Path = args.saida.expanduser()
    template_path: Path = args.template.expanduser()

    # 1. Carrega e valida
    try:
        dados = carregar_dados(json_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERRO dados: {e}", file=sys.stderr)
        print("Nao vou sobrescrever HTML existente.", file=sys.stderr)
        return 2

    try:
        template = carregar_template(template_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERRO template: {e}", file=sys.stderr)
        return 3

    # 2. Renderiza (antes do backup: se falhar, nao mexemos em nada)
    html = renderizar(template, dados)

    erros = validar_html_basico(html)
    if erros:
        print("ERRO validacao HTML:", file=sys.stderr)
        for e in erros:
            print(f"  - {e}", file=sys.stderr)
        return 4

    # 3. Backup do HTML atual
    backup_path: Path | None = None
    if not args.sem_backup:
        backup_path = fazer_backup(html_path)

    # 4. Escreve
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")

    # 5. Relatorio
    tamanho = html_path.stat().st_size
    agora = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[OK] HTML gerado: {html_path}")
    print(f"     Tamanho:     {tamanho} bytes")
    print(f"     Timestamp:   {agora}")
    print(f"     Nos:         {len(dados['nos'])}")
    print(f"     Ligacoes:    {len(dados['ligacoes'])}")
    print(f"     Camadas:     {len(dados['camadas'])}")
    print(f"     Backup:      {backup_path if backup_path else '(nenhum)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
