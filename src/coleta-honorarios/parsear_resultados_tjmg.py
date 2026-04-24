#!/usr/bin/env python3
"""Parser de HTML salvo da lista de resultados TJMG (pos-captcha).

Uso:
  python3 parsear_resultados_tjmg.py _raw_html/pos-captcha-20260420-203636.html \
      --busca "honorarios periciais Governador Valadares"

Extrai 19 acordaos do HTML sem precisar de novo captcha:
- Ementa inline
- Identificadores (procAno, procNumero, procSequencial, procSeqAcordao)
- CNJ quando aparecer na ementa
- Valor quando aparecer na ementa (senao classifica PARCIAL)
- Salva trinity em Casos-Reais/<regiao>/
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from datetime import datetime
from html import unescape
from pathlib import Path

OUTPUT_DIR = Path("/Users/jesus/Desktop/STEMMIA Dexter/banco-de-dados/Banco-Transversal/Honorarios-Periciais/Casos-Reais")
BASE_TJMG = "https://www5.tjmg.jus.br/jurisprudencia/"


def slugify_params(ano: str, numero: str, seq: str, seq_acordao: str) -> str:
    return f"tjmg-{ano}-{numero}-{seq}-{seq_acordao}"


def extract_valor(texto: str) -> tuple[int | None, str | None]:
    """Procura R$ SO em contexto PERICIAL estrito. Retorna (centavos, trecho)."""
    # Whitelist rigorosa — termos que SO aparecem em honorario pericial
    whitelist = re.compile(
        r"honor[aá]rios?\s+(pericia[li]|do\s+perito|ao\s+perito)|"
        r"verba\s+pericial|"
        r"remunera[cç][aã]o\s+do\s+perito|"
        r"honor[aá]rios?\s+arbitrad[oa]s?\s+(ao|em\s+favor\s+do)\s+perito|"
        r"perito.{0,40}honor[aá]rios?|"
        r"honor[aá]rios?.{0,40}perito",
        re.IGNORECASE,
    )
    # Blacklist — contexto que INVALIDA
    blacklist = re.compile(
        r"honor[aá]rios?\s+(advocat[ií]cios?|sucumbencia[li]s?|contratua[li]s?)|"
        r"danos?\s+morais|"
        r"indeniza[cç][aã]o",
        re.IGNORECASE,
    )

    # Procura cada R$ e valida contexto (±150 chars)
    for m in re.finditer(r"R\$\s*([\d\.]+,\d{2})", texto):
        start = max(0, m.start() - 150)
        end = min(len(texto), m.end() + 150)
        janela = texto[start:end]

        if not whitelist.search(janela):
            continue
        if blacklist.search(janela):
            continue

        raw = m.group(1).replace(".", "").replace(",", ".")
        try:
            centavos = int(float(raw) * 100)
        except ValueError:
            continue

        # Sanidade: honorario pericial raramente > R$ 50.000 (teto com majoracao 5x)
        if centavos > 5_000_000:
            continue
        # Raramente < R$ 50
        if centavos < 5_000:
            continue

        return centavos, janela

    return None, None


def extract_cnj(texto: str) -> str | None:
    m = re.search(r"\d{7}-?\d{2}\.?\d{4}\.?8?\.?13\.?\d{4}", texto)
    return m.group(0) if m else None


def classificar_comarca(texto: str) -> str:
    lower = texto.lower()
    if any(c in lower for c in ["governador valadares", "ipatinga", "coronel fabriciano",
                                 "timoteo", "caratinga", "aimores", "mantena",
                                 "teofilo otoni", "nanuque"]):
        return "GV-e-regiao"
    if any(c in lower for c in ["juiz de fora", "barbacena", "muriae", "manhuacu",
                                 "ponte nova", "santos dumont"]):
        return "Zona-Mata-Sul"
    if any(c in lower for c in ["uberlandia", "uberaba", "ituiutaba", "araxa", "patos de minas"]):
        return "Triangulo-Alto-Paranaiba"
    if any(c in lower for c in ["belo horizonte", "contagem", "betim", "santa luzia",
                                 "ribeirao das neves", "nova lima", "lagoa santa", "sete lagoas"]):
        return "BH-metropolitana"
    if any(c in lower for c in ["montes claros", "pirapora", "januaria", "janauba", "salinas"]):
        return "Norte-Mineiro"
    return "Outros-regiao-MG"


def tipo_pericia_heuristica(texto: str) -> str:
    lower = texto.lower()
    if "insalubridade" in lower or "periculosidade" in lower:
        return "insalubridade-periculosidade"
    if "erro medico" in lower or "erro médico" in lower:
        return "erro-medico"
    if "dpvat" in lower:
        return "dpvat"
    if "grafotecnic" in lower:
        return "grafotecnica"
    if "acidente" in lower and "trabalho" in lower:
        return "acidente-trabalho"
    if "psiquiatric" in lower or "mental" in lower:
        return "psiquiatrica"
    if "ortoped" in lower or "fratura" in lower or "coluna" in lower:
        return "ortopedica"
    if "vicios construtiv" in lower or "engenh" in lower:
        return "engenharia-civil"
    if "contabil" in lower or "revisional" in lower:
        return "contabil"
    return "indeterminada"


def parse_acordaos(html: str):
    """Divide HTML em blocos por acordao e extrai campos."""
    # Cada acordao comeca com <a ...class="linkListaEspelhoAcordaos">
    # Uso split pra quebrar em blocos
    blocos = re.split(r'class="linkListaEspelhoAcordaos"', html)
    if len(blocos) < 2:
        return []

    resultados = []
    # blocos[0] = lixo antes do primeiro link
    for idx, bloco in enumerate(blocos[1:], start=1):
        entry = {"index": idx}

        # Parametros identificadores do ementaSemFormatacao
        m_ident = re.search(
            r"ementaSemFormatacao\.do\?procAno=(\d+)&(?:amp;)?procCodigo=\d+&(?:amp;)?procCodigoOrigem=\d+&(?:amp;)?procNumero=(\d+)&(?:amp;)?procSequencial=(\d+)&(?:amp;)?procSeqAcordao=(\d+)",
            bloco,
        )
        if m_ident:
            entry["procAno"] = m_ident.group(1)
            entry["procNumero"] = m_ident.group(2)
            entry["procSequencial"] = m_ident.group(3)
            entry["procSeqAcordao"] = m_ident.group(4)
            entry["url_ementa_semformato"] = (
                f"{BASE_TJMG}ementaSemFormatacao.do?"
                f"procAno={entry['procAno']}&procCodigo=1&procCodigoOrigem=0"
                f"&procNumero={entry['procNumero']}&procSequencial={entry['procSequencial']}"
                f"&procSeqAcordao={entry['procSeqAcordao']}"
            )

        # Ementa: primeiro bloco <strong>Ementa:</strong>...</div> (ou ateh proximo linkListaEspelhoAcordaos)
        m_ement = re.search(
            r'<strong>Ementa:</strong>(.+?)(?=<a[^>]+class="linkListaEspelhoAcordaos"|<td[^>]*>\d+</td>|</body>)',
            bloco, re.DOTALL,
        )
        ementa_raw = m_ement.group(1) if m_ement else bloco[:5000]
        # Limpar HTML tags e entidades
        ementa_txt = re.sub(r"<[^>]+>", " ", ementa_raw)
        ementa_txt = unescape(ementa_txt)
        ementa_txt = re.sub(r"\s+", " ", ementa_txt).strip()
        entry["ementa"] = ementa_txt[:5000]

        # Numero de processo CNJ na ementa
        entry["cnj"] = extract_cnj(ementa_txt)

        # Valor na ementa (pode ser nulo) — com contexto honorario/perito
        v, trecho = extract_valor(ementa_txt)
        entry["valor_centavos"] = v
        entry["valor_reais"] = v / 100 if v else None
        entry["valor_trecho_contexto"] = trecho

        # Comarca e tipo
        entry["comarca_classificada"] = classificar_comarca(ementa_txt)
        entry["tipo_pericia"] = tipo_pericia_heuristica(ementa_txt)

        resultados.append(entry)

    return resultados


def salvar_trinity(entry: dict, busca: str):
    """Salva MD + FICHA.json (PDF fica pra fase posterior de abrir no browser)."""
    slug = slugify_params(
        entry.get("procAno", "x"),
        entry.get("procNumero", "x"),
        entry.get("procSequencial", "x"),
        entry.get("procSeqAcordao", "x"),
    )
    regiao = entry["comarca_classificada"]
    destino = OUTPUT_DIR / regiao
    destino.mkdir(parents=True, exist_ok=True)

    # Classificacao anti-falso-resultado
    if entry["valor_reais"] and entry["cnj"]:
        classif = "REAL_COM_CNJ_E_VALOR"
    elif entry["valor_reais"]:
        classif = "PARCIAL_COM_VALOR_SEM_CNJ"
    elif entry["cnj"]:
        classif = "PARCIAL_COM_CNJ_SEM_VALOR_NA_EMENTA"
    else:
        classif = "PARCIAL_APENAS_EMENTA"

    ficha = {
        "cnj": entry.get("cnj"),
        "tribunal": "TJMG",
        "comarca_classificada": regiao,
        "tipo_pericia_heuristica": entry["tipo_pericia"],
        "valor_fixado_reais": entry["valor_reais"],
        "valor_fonte": "ementa_lista_resultados" if entry["valor_reais"] else None,
        "valor_trecho_contexto": entry.get("valor_trecho_contexto"),
        "data_coleta": datetime.now().isoformat(),
        "fonte_url": entry.get("url_ementa_semformato"),
        "identificadores_tjmg": {
            "procAno": entry.get("procAno"),
            "procNumero": entry.get("procNumero"),
            "procSequencial": entry.get("procSequencial"),
            "procSeqAcordao": entry.get("procSeqAcordao"),
        },
        "classificacao": classif,
        "busca_origem": busca,
        "necessita_inteiro_teor": entry["valor_reais"] is None,
    }

    md_path = destino / f"{slug}.md"
    md_path.write_text(
        f"# Acordao TJMG — {slug}\n\n"
        f"- CNJ: {entry.get('cnj') or 'NAO APARECE NA EMENTA (precisa inteiro teor)'}\n"
        f"- Valor na ementa: {('R$ ' + format(entry['valor_reais'], '.2f')) if entry['valor_reais'] else 'NAO (precisa inteiro teor)'}\n"
        f"- Comarca classificada (heuristica): {regiao}\n"
        f"- Tipo pericia (heuristica): {entry['tipo_pericia']}\n"
        f"- Classificacao anti-falso: **{classif}**\n"
        f"- URL ementa sem formato: {entry.get('url_ementa_semformato')}\n"
        f"- Busca origem: {busca}\n"
        f"- Coletado: {datetime.now().isoformat()}\n\n"
        f"## Ementa (extraida da lista, trecho ateh 5000 chars)\n\n{entry['ementa']}\n",
        encoding="utf-8",
    )
    (destino / f"{slug}.FICHA.json").write_text(
        json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return regiao, slug, classif


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html_path")
    ap.add_argument("--busca", required=True)
    args = ap.parse_args()

    html = Path(args.html_path).read_text(encoding="utf-8", errors="replace")
    acordaos = parse_acordaos(html)
    print(f"[parser] {len(acordaos)} acordaos extraidos de {args.html_path}")

    stats = {"REAL_COM_CNJ_E_VALOR": 0, "PARCIAL_COM_VALOR_SEM_CNJ": 0,
             "PARCIAL_COM_CNJ_SEM_VALOR_NA_EMENTA": 0, "PARCIAL_APENAS_EMENTA": 0}
    por_regiao = {}

    for entry in acordaos:
        regiao, slug, classif = salvar_trinity(entry, args.busca)
        stats[classif] += 1
        por_regiao.setdefault(regiao, []).append(slug)
        print(f"  [{classif}] {regiao}/{slug}")

    print("\n=== RESUMO ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print("\nPor regiao:")
    for r, lista in por_regiao.items():
        print(f"  {r}: {len(lista)}")


if __name__ == "__main__":
    main()
