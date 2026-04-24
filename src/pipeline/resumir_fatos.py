#!/usr/bin/env python3
"""
resumir_fatos.py — Extrai linha do tempo cronológica do processo via datas.

Saída: TIMELINE.json + TIMELINE.md na pasta do processo.

Uso:
    python3 resumir_fatos.py 5002424-62.2025.8.13.0309
    python3 resumir_fatos.py /caminho/para/pasta
    python3 resumir_fatos.py --arquivo /caminho/TEXTO-EXTRAIDO.txt
"""

from pathlib import Path
import argparse, json, re, sys
from datetime import date, datetime
from collections import defaultdict


BASE_DIR = Path(__file__).parent

class C:
    R = "\033[0m"
    B = "\033[1m"
    G = "\033[32m"
    Y = "\033[33m"
    RE = "\033[31m"
    CY = "\033[36m"
    DIM = "\033[2m"


MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

# Padrões de data
RE_DATA_BARRA = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
RE_DATA_EXTENSO = re.compile(
    r"\b(\d{1,2})\s+de\s+(" + "|".join(MESES.keys()) + r")\s+de\s+(\d{4})\b",
    re.IGNORECASE
)
RE_DATA_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")

# Palavras que indicam seção do texto
MARCADORES_SECAO = {
    "petição inicial": "Petição Inicial",
    "inicial": "Petição Inicial",
    "contestação": "Contestação",
    "contesta": "Contestação",
    "réu alega": "Contestação",
    "réu afirma": "Contestação",
    "decisão": "Decisão",
    "despacho": "Despacho",
    "sentença": "Sentença",
    "laudo": "Laudo",
    "parecer": "Parecer",
    "boletim de ocorrência": "Boletim de Ocorrência",
    "depoimento": "Depoimento",
    "atestado": "Atestado Médico",
    "prontuário": "Prontuário",
}

# Palavras-chave de eventos relevantes para perícia
KEYWORDS_EVENTOS = [
    "acidente", "lesão", "lesões", "fratura", "cirurgia", "internação", "internado",
    "alta hospitalar", "alta médica", "atendimento", "emergência", "urgência",
    "diagnóstico", "diagnosticado", "tratamento", "medicação", "medicamento",
    "afastamento", "afastado", "incapacidade", "incapaz", "aposentadoria",
    "benefício", "perícia", "perito", "exame", "ressonância", "tomografia",
    "raio-x", "radiografia", "ultrassom", "consulta", "retorno", "óbito",
    "falecimento", "nascimento", "contrato", "admissão", "demissão", "rescisão",
    "nomeação", "intimação", "audiência", "contestação", "sentença",
    "recurso", "apelação", "agravo",
]


def parse_data_barra(m) -> date | None:
    try:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    except ValueError:
        return None

def parse_data_extenso(m) -> date | None:
    mes = MESES.get(m.group(2).lower())
    if mes:
        try:
            return date(int(m.group(3)), mes, int(m.group(1)))
        except ValueError:
            return None
    return None

def parse_data_iso(m) -> date | None:
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def identificar_secao(texto: str, posicao: int, linhas: list[str]) -> str:
    """Identifica a seção do texto com base no contexto ao redor."""
    # Olhar 2000 caracteres antes da posição
    inicio = max(0, posicao - 2000)
    trecho = texto[inicio:posicao].lower()

    # Verificar marcadores de seção (do mais recente ao mais antigo)
    melhor_marcador = ""
    melhor_pos = -1
    for marcador, secao in MARCADORES_SECAO.items():
        pos = trecho.rfind(marcador)
        if pos > melhor_pos:
            melhor_pos = pos
            melhor_marcador = secao

    return melhor_marcador or "Texto do processo"


def extrair_contexto(texto: str, posicao: int, raio: int = 300) -> str:
    """Extrai contexto ao redor de uma posição no texto."""
    inicio = max(0, posicao - raio)
    fim = min(len(texto), posicao + raio)

    # Ajustar para não cortar palavras
    while inicio > 0 and texto[inicio] not in " \n\t":
        inicio -= 1
    while fim < len(texto) and texto[fim] not in " \n\t":
        fim += 1

    trecho = texto[inicio:fim].strip()
    # Limpar quebras de linha excessivas
    trecho = re.sub(r"\s+", " ", trecho)
    return trecho


def calcular_relevancia(contexto: str) -> float:
    """Calcula relevância do evento para a perícia (0-1)."""
    contexto_lower = contexto.lower()
    score = 0

    for kw in KEYWORDS_EVENTOS:
        if kw in contexto_lower:
            score += 1

    # Normalizar (máximo ~10 keywords)
    return min(score / 5, 1.0)


def calcular_linha_no_texto(texto: str, posicao: int) -> int:
    """Calcula o número da linha para uma posição no texto."""
    return texto[:posicao].count("\n") + 1


def extrair_timeline(texto: str) -> dict:
    """Pipeline principal de extração de timeline."""
    eventos = []
    datas_vistas = set()

    # 1. Extrair datas no formato dd/mm/yyyy
    for m in RE_DATA_BARRA.finditer(texto):
        data = parse_data_barra(m)
        if not data:
            continue
        # Filtrar datas absurdas
        if data.year < 1950 or data.year > 2030:
            continue

        posicao = m.start()
        contexto = extrair_contexto(texto, posicao)
        relevancia = calcular_relevancia(contexto)

        # Deduplicar por data + contexto similar
        chave = f"{data.isoformat()}:{contexto[:50]}"
        if chave in datas_vistas:
            continue
        datas_vistas.add(chave)

        linha = calcular_linha_no_texto(texto, posicao)
        secao = identificar_secao(texto, posicao, [])

        eventos.append({
            "data": data.isoformat(),
            "data_obj": data,
            "texto": contexto,
            "fonte": secao,
            "linha": linha,
            "relevancia": relevancia,
            "formato_original": m.group(),
        })

    # 2. Extrair datas por extenso
    for m in RE_DATA_EXTENSO.finditer(texto):
        data = parse_data_extenso(m)
        if not data or data.year < 1950 or data.year > 2030:
            continue

        posicao = m.start()
        contexto = extrair_contexto(texto, posicao)
        relevancia = calcular_relevancia(contexto)

        chave = f"{data.isoformat()}:{contexto[:50]}"
        if chave in datas_vistas:
            continue
        datas_vistas.add(chave)

        linha = calcular_linha_no_texto(texto, posicao)
        secao = identificar_secao(texto, posicao, [])

        eventos.append({
            "data": data.isoformat(),
            "data_obj": data,
            "texto": contexto,
            "fonte": secao,
            "linha": linha,
            "relevancia": relevancia,
            "formato_original": m.group(),
        })

    # 3. Ordenar cronologicamente
    eventos.sort(key=lambda x: x["data_obj"])

    # 4. Filtrar eventos mais relevantes (top N)
    eventos_relevantes = [e for e in eventos if e["relevancia"] >= 0.2]
    eventos_menores = [e for e in eventos if e["relevancia"] < 0.2]

    # 5. Agrupar por fonte
    por_fonte = defaultdict(list)
    for e in eventos:
        por_fonte[e["fonte"]].append(e)

    # 6. Identificar versões divergentes
    versoes = {
        "autor": "",
        "reu": "",
        "pontos_incontroversos": "",
    }

    # Extrair resumo do autor (petição inicial)
    eventos_autor = [e for e in eventos if e["fonte"] == "Petição Inicial" and e["relevancia"] >= 0.4]
    if eventos_autor:
        versoes["autor"] = " → ".join(e["texto"][:100] for e in eventos_autor[:3])

    # Extrair resumo do réu (contestação)
    eventos_reu = [e for e in eventos if e["fonte"] == "Contestação" and e["relevancia"] >= 0.4]
    if eventos_reu:
        versoes["reu"] = " → ".join(e["texto"][:100] for e in eventos_reu[:3])

    # 7. Limpar data_obj (não serializável)
    for e in eventos:
        del e["data_obj"]

    resultado = {
        "total_eventos": len(eventos),
        "eventos_relevantes": len(eventos_relevantes),
        "periodo": {
            "inicio": eventos[0]["data"] if eventos else "",
            "fim": eventos[-1]["data"] if eventos else "",
        },
        "eventos": eventos,
        "por_fonte": {fonte: len(evs) for fonte, evs in por_fonte.items()},
        "versoes_divergentes": versoes,
        "_metadados": {
            "extraido_em": datetime.now().isoformat(),
            "script": "resumir_fatos.py",
        },
    }

    return resultado


def gerar_markdown(dados: dict) -> str:
    """Gera TIMELINE.md."""
    md = []
    md.append("## LINHA DO TEMPO DO PROCESSO\n")

    periodo = dados["periodo"]
    if periodo["inicio"]:
        md.append(f"**Período:** {periodo['inicio']} a {periodo['fim']}")
        md.append(f"**Total de eventos:** {dados['total_eventos']} ({dados['eventos_relevantes']} relevantes)\n")

    # Eventos relevantes
    md.append("### Eventos Principais (relevância >= 0.2)\n")

    eventos_rel = [e for e in dados["eventos"] if e["relevancia"] >= 0.2]
    if eventos_rel:
        for e in eventos_rel:
            rel = f"[{e['relevancia']:.1f}]" if e["relevancia"] < 1.0 else "[1.0]"
            fonte = f" ({e['fonte']})" if e["fonte"] != "Texto do processo" else ""
            md.append(f"- **{e['data']}** {rel}{fonte}")
            # Truncar texto longo
            texto = e["texto"][:200] + "..." if len(e["texto"]) > 200 else e["texto"]
            md.append(f"  {texto}")
            md.append("")
    else:
        md.append("Nenhum evento com relevância suficiente encontrado.\n")

    # Todos os eventos (tabela compacta)
    md.append("### Todos os Eventos (cronológico)\n")
    md.append("| Data | Fonte | Linha | Relevância |")
    md.append("|------|-------|-------|-----------|")
    for e in dados["eventos"]:
        md.append(f"| {e['data']} | {e['fonte']} | {e['linha']} | {e['relevancia']:.1f} |")
    md.append("")

    # Fontes
    md.append("### Eventos por Fonte\n")
    for fonte, qtd in dados["por_fonte"].items():
        md.append(f"- **{fonte}:** {qtd} eventos")
    md.append("")

    # Versões divergentes
    versoes = dados["versoes_divergentes"]
    if versoes["autor"] or versoes["reu"]:
        md.append("### Versões Divergentes\n")
        if versoes["autor"]:
            md.append(f"**Autor alega:** {versoes['autor']}")
        if versoes["reu"]:
            md.append(f"\n**Réu alega:** {versoes['reu']}")
        if versoes["pontos_incontroversos"]:
            md.append(f"\n**Pontos incontroversos:** {versoes['pontos_incontroversos']}")

    meta = dados.get("_metadados", {})
    md.append(f"\n---\n*Extraído em {meta.get('extraido_em', '')} por resumir_fatos.py*")
    md.append(f"\n*NOTA: Esta é uma extração automática por regex. O agente Resumidor de Fatos pode refinar com análise semântica.*")

    return "\n".join(md)


def encontrar_pasta_processo(identificador: str) -> Path:
    p = Path(identificador)
    if p.is_dir():
        return p
    for pasta in BASE_DIR.iterdir():
        if pasta.is_dir() and identificador in pasta.name:
            return pasta
    processos_dir = BASE_DIR / "processos"
    if processos_dir.exists():
        for pasta in processos_dir.iterdir():
            if pasta.is_dir() and identificador in pasta.name:
                return pasta
    return None


def encontrar_texto_extraido(pasta: Path) -> Path:
    for nome in ("TEXTO-EXTRAIDO.txt", "texto-extraido.txt", "TEXTO_EXTRAIDO.txt"):
        p = pasta / nome
        if p.exists():
            return p
    for f in pasta.glob("*.txt"):
        if f.stat().st_size > 5000:
            return f
    return None


def main():
    parser = argparse.ArgumentParser(description="Extrai linha do tempo cronológica do processo")
    parser.add_argument("processo", nargs="?", help="Número CNJ ou caminho da pasta")
    parser.add_argument("--arquivo", "-a", help="Caminho direto para TEXTO-EXTRAIDO.txt")
    parser.add_argument("--output", "-o", help="Pasta de saída")
    parser.add_argument("--json-only", action="store_true", help="Imprimir JSON no stdout")
    parser.add_argument("--min-relevancia", type=float, default=0.0, help="Relevância mínima (0-1)")
    args = parser.parse_args()

    if args.arquivo:
        arquivo = Path(args.arquivo)
        pasta = arquivo.parent
    elif args.processo:
        pasta = encontrar_pasta_processo(args.processo)
        if not pasta:
            print(f"{C.RE}Erro: processo '{args.processo}' não encontrado.{C.R}")
            sys.exit(1)
        arquivo = encontrar_texto_extraido(pasta)
    else:
        parser.print_help()
        sys.exit(1)

    if not arquivo or not arquivo.exists():
        print(f"{C.RE}Erro: TEXTO-EXTRAIDO.txt não encontrado em {pasta}{C.R}")
        sys.exit(1)

    texto = arquivo.read_text(encoding="utf-8")
    dados = extrair_timeline(texto)

    # Filtrar por relevância mínima se solicitado
    if args.min_relevancia > 0:
        dados["eventos"] = [e for e in dados["eventos"] if e["relevancia"] >= args.min_relevancia]

    if args.json_only:
        print(json.dumps(dados, ensure_ascii=False, indent=2))
        sys.exit(0)

    output_dir = Path(args.output) if args.output else pasta

    json_path = output_dir / "TIMELINE.json"
    json_path.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    md_path = output_dir / "TIMELINE.md"
    md_path.write_text(gerar_markdown(dados), encoding="utf-8")

    # Resumo
    print(f"\n{C.B}LINHA DO TEMPO{C.R}")
    print(f"  Total eventos:     {dados['total_eventos']}")
    print(f"  Relevantes (≥0.2): {dados['eventos_relevantes']}")
    if dados["periodo"]["inicio"]:
        print(f"  Período:           {dados['periodo']['inicio']} a {dados['periodo']['fim']}")
    print(f"  Fontes:")
    for fonte, qtd in dados["por_fonte"].items():
        print(f"    {C.CY}{fonte}{C.R}: {qtd}")
    print(f"\n  {C.DIM}→ {json_path}{C.R}")
    print(f"  {C.DIM}→ {md_path}{C.R}")


if __name__ == "__main__":
    main()
