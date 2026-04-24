#!/usr/bin/env python3
"""
classificar_acao.py — Classifica tipo de ação judicial via palavras-chave.

Saída: CLASSIFICACAO.json + CLASSIFICACAO.md na pasta do processo.
Atualiza FICHA.json se existir.

Uso:
    python3 classificar_acao.py 5002424-62.2025.8.13.0309
    python3 classificar_acao.py /caminho/para/pasta
    python3 classificar_acao.py --arquivo /caminho/TEXTO-EXTRAIDO.txt
"""

from pathlib import Path
import argparse, json, re, sys
from datetime import datetime


BASE_DIR = Path(__file__).parent

class C:
    R = "\033[0m"
    B = "\033[1m"
    G = "\033[32m"
    Y = "\033[33m"
    RE = "\033[31m"
    CY = "\033[36m"
    DIM = "\033[2m"


# Tabela de classificação: tipo → (subtipo, palavras-chave, peso)
CLASSIFICACOES = [
    {
        "tipo": "PREVIDENCIÁRIA",
        "subtipos": [
            ("Auxílio-doença / Auxílio por Incapacidade Temporária",
             ["auxílio-doença", "auxílio doença", "auxílio por incapacidade temporária", "incapacidade temporária"]),
            ("Aposentadoria por Invalidez / Incapacidade Permanente",
             ["aposentadoria por invalidez", "incapacidade permanente", "aposentadoria por incapacidade"]),
            ("BPC/LOAS",
             ["bpc", "loas", "benefício de prestação continuada", "benefício assistencial"]),
            ("Auxílio-Acidente",
             ["auxílio-acidente", "auxílio acidente"]),
            ("Aposentadoria Especial",
             ["aposentadoria especial", "insalubridade", "periculosidade"]),
        ],
        "keywords_gerais": ["inss", "previdenciário", "previdenciária", "benefício previdenciário", "segurado", "autarquia previdenciária"],
    },
    {
        "tipo": "TRABALHISTA",
        "subtipos": [
            ("Acidente de Trabalho",
             ["acidente de trabalho", "acidente do trabalho", "doença ocupacional", "doença profissional", "cat ", "nexo causal", "nexo técnico"]),
            ("Insalubridade/Periculosidade",
             ["insalubridade", "periculosidade", "adicional de insalubridade"]),
            ("Danos Morais Trabalhistas",
             ["danos morais", "assédio moral", "assédio sexual"]),
            ("Rescisão Indireta",
             ["rescisão indireta"]),
        ],
        "keywords_gerais": ["reclamação trabalhista", "reclamatória", "ctps", "clt", "vínculo empregatício", "rescisão", "verbas rescisórias", "fgts"],
    },
    {
        "tipo": "CÍVEL — INDENIZATÓRIA",
        "subtipos": [
            ("Danos Morais",
             ["danos morais", "dano moral", "indenização por dano moral"]),
            ("Danos Materiais",
             ["danos materiais", "dano material", "lucros cessantes"]),
            ("Danos Estéticos",
             ["danos estéticos", "dano estético"]),
            ("Pensão Vitalícia",
             ["pensão vitalícia", "pensionamento", "pensão mensal"]),
        ],
        "keywords_gerais": ["indenização", "indenizatória", "reparação de danos", "responsabilidade civil"],
    },
    {
        "tipo": "CÍVEL — ACIDENTE DE TRÂNSITO",
        "subtipos": [
            ("Colisão",
             ["colisão", "abalroamento"]),
            ("Atropelamento",
             ["atropelamento", "atropelado"]),
        ],
        "keywords_gerais": ["acidente de trânsito", "acidente automobilístico", "veículo", "sinistro", "ctb", "código de trânsito"],
    },
    {
        "tipo": "CÍVEL — ERRO MÉDICO",
        "subtipos": [
            ("Negligência",
             ["negligência médica", "erro médico"]),
            ("Imperícia",
             ["imperícia", "imperícia médica"]),
            ("Imprudência",
             ["imprudência médica"]),
        ],
        "keywords_gerais": ["erro médico", "responsabilidade médica", "malpractice", "iatrogenia"],
    },
    {
        "tipo": "CÍVEL — CURATELA/INTERDIÇÃO",
        "subtipos": [
            ("Interdição",
             ["interdição", "interditando"]),
            ("Curatela",
             ["curatela", "curador"]),
        ],
        "keywords_gerais": ["incapacidade civil", "capacidade civil", "exercício de direitos"],
    },
    {
        "tipo": "SECURITÁRIA",
        "subtipos": [
            ("Seguro de Vida",
             ["seguro de vida", "cobertura por morte", "cobertura por invalidez"]),
            ("DPVAT",
             ["dpvat"]),
            ("Seguro Prestamista",
             ["seguro prestamista", "seguro habitacional"]),
        ],
        "keywords_gerais": ["seguro", "apólice", "seguradora", "sinistro", "cobertura securitária", "indenização securitária", "prêmio do seguro"],
    },
    {
        "tipo": "CRIMINAL",
        "subtipos": [
            ("Lesão Corporal",
             ["lesão corporal", "lesões corporais"]),
            ("Homicídio",
             ["homicídio"]),
            ("Corpo de Delito",
             ["corpo de delito", "exame de corpo de delito"]),
        ],
        "keywords_gerais": ["crime", "criminal", "réu preso", "inquérito policial", "ação penal", "denúncia criminal"],
    },
]


def extrair_cabecalho(linhas: list[str]) -> dict:
    """Extrai dados do cabeçalho PJe."""
    dados = {
        "classe_pje": "",
        "valor_causa": "",
        "valor_causa_float": 0.0,
        "assuntos": "",
        "segredo_justica": False,
        "justica_gratuita": False,
    }

    for linha in linhas[:30]:
        linha = linha.strip()

        if linha.startswith("Classe:"):
            dados["classe_pje"] = linha.replace("Classe:", "").strip()

        elif linha.startswith("Valor da causa:"):
            m = re.search(r"R\$\s*([\d.,]+)", linha)
            if m:
                dados["valor_causa"] = "R$ " + m.group(1)
                try:
                    valor_str = m.group(1).replace(".", "").replace(",", ".")
                    dados["valor_causa_float"] = float(valor_str)
                except ValueError:
                    pass

        elif linha.startswith("Assuntos:"):
            dados["assuntos"] = linha.replace("Assuntos:", "").strip()

        elif "Segredo de justiça?" in linha:
            dados["segredo_justica"] = "SIM" in linha.upper()

        elif "Justiça gratuita?" in linha or "gratuita?" in linha:
            dados["justica_gratuita"] = "SIM" in linha.upper()

    return dados


def classificar(texto: str) -> dict:
    """Classifica o tipo de ação judicial."""
    texto_lower = texto.lower()
    linhas = texto.split("\n")

    # 1. Extrair cabeçalho
    cabecalho = extrair_cabecalho(linhas)

    # 2. Pontuar cada tipo
    scores = []
    for cat in CLASSIFICACOES:
        score = 0
        subtipo_melhor = ""
        subtipo_score = 0

        # Keywords gerais
        for kw in cat["keywords_gerais"]:
            count = texto_lower.count(kw.lower())
            score += count * 2  # Peso 2 para keywords gerais

        # Subtipos
        for sub_nome, sub_keywords in cat["subtipos"]:
            sub_score = 0
            for kw in sub_keywords:
                count = texto_lower.count(kw.lower())
                sub_score += count * 3  # Peso 3 para subtipos (mais específicos)
            if sub_score > subtipo_score:
                subtipo_score = sub_score
                subtipo_melhor = sub_nome
            score += sub_score

        # Bonus: classe PJe confirma
        classe = cabecalho["classe_pje"].lower()
        if "cível" in classe and "CÍVEL" in cat["tipo"]:
            score += 5
        elif "trabalh" in classe and cat["tipo"] == "TRABALHISTA":
            score += 10
        elif "criminal" in classe and cat["tipo"] == "CRIMINAL":
            score += 10
        elif "previden" in classe and cat["tipo"] == "PREVIDENCIÁRIA":
            score += 10

        # Bonus: assuntos confirmam
        assuntos = cabecalho["assuntos"].lower()
        if "seguro" in assuntos and cat["tipo"] == "SECURITÁRIA":
            score += 8
        if "indenização" in assuntos and "INDENIZATÓRIA" in cat["tipo"]:
            score += 5
        if "previdenciár" in assuntos and cat["tipo"] == "PREVIDENCIÁRIA":
            score += 8

        scores.append({
            "tipo": cat["tipo"],
            "subtipo": subtipo_melhor,
            "score": score,
        })

    # 3. Ordenar por score
    scores.sort(key=lambda x: x["score"], reverse=True)

    melhor = scores[0] if scores and scores[0]["score"] > 0 else {"tipo": "NÃO CLASSIFICADA", "subtipo": "", "score": 0}
    segundo = scores[1] if len(scores) > 1 and scores[1]["score"] > 0 else None

    # 4. Confiança
    if melhor["score"] >= 20:
        confianca = "ALTA"
    elif melhor["score"] >= 8:
        confianca = "MÉDIA"
    elif melhor["score"] > 0:
        confianca = "BAIXA"
    else:
        confianca = "NENHUMA"

    # 5. Extrair objeto da perícia
    objeto = extrair_objeto_pericia(texto)

    # 6. Identificar especialidades médicas
    especialidades = identificar_especialidades(texto_lower)

    # 7. Rito
    rito = identificar_rito(texto_lower, cabecalho)

    resultado = {
        "tipo": melhor["tipo"],
        "subtipo": melhor["subtipo"],
        "confianca": confianca,
        "score": melhor["score"],
        "classe_pje": cabecalho["classe_pje"],
        "valor_causa": cabecalho["valor_causa"],
        "justica_gratuita": cabecalho["justica_gratuita"],
        "segredo_justica": cabecalho["segredo_justica"],
        "assuntos": cabecalho["assuntos"],
        "objeto_pericia": objeto,
        "especialidades_medicas": especialidades,
        "rito": rito,
        "alternativas": [],
        "_metadados": {
            "extraido_em": datetime.now().isoformat(),
            "script": "classificar_acao.py",
            "scores": scores[:3],
        },
    }

    if segundo and segundo["score"] > 0:
        resultado["alternativas"].append({
            "tipo": segundo["tipo"],
            "subtipo": segundo["subtipo"],
            "score": segundo["score"],
        })

    return resultado


def extrair_objeto_pericia(texto: str) -> str:
    """Extrai o objeto da perícia do texto."""
    padroes = [
        r"(?:objeto\s+da\s+perícia|perícia\s+(?:deverá|deverão)\s+apurar)\s*:?\s*(.{10,200}?)(?:\.|$)",
        r"nomeio.+?perito.+?(?:para|a\s+fim\s+de)\s+(.{10,200}?)(?:\.|$)",
        r"(?:deverá\s+o\s+perito|o\s+perito\s+deverá)\s+(.{10,200}?)(?:\.|$)",
        r"quesitos.+?(?:apurar|verificar|constatar|avaliar)\s+(.{10,200}?)(?:\.|$)",
    ]

    texto_lower = texto.lower()
    for padrao in padroes:
        m = re.search(padrao, texto_lower)
        if m:
            return m.group(1).strip().capitalize()

    return ""


def identificar_especialidades(texto_lower: str) -> list[str]:
    """Identifica especialidades médicas mencionadas."""
    especialidades_map = {
        "ortopedia": ["ortoped", "fratura", "articulação", "coluna vertebral", "prótese", "osteossíntese"],
        "neurologia": ["neurológ", "avc", "epilepsia", "neuropatia", "esclerose"],
        "psiquiatria": ["psiquiátr", "depressão", "ansiedade", "transtorno mental", "bipolar", "esquizofrenia"],
        "cardiologia": ["cardiol", "infarto", "arritmia", "insuficiência cardíaca"],
        "pneumologia": ["pneumol", "asma", "dpoc", "fibrose pulmonar"],
        "oftalmologia": ["oftalm", "cegueira", "visão", "glaucoma", "catarata"],
        "otorrinolaringologia": ["otorrino", "surdez", "audição", "perda auditiva"],
        "dermatologia": ["dermatol", "pele", "queimadura"],
        "reumatologia": ["reumatol", "artrite", "fibromialgia", "lúpus"],
        "oncologia": ["oncol", "câncer", "tumor", "neoplasia"],
        "traumatologia": ["trauma", "traumat", "politraumatismo"],
        "medicina do trabalho": ["medicina do trabalho", "ocupacional", "saúde do trabalhador"],
    }

    encontradas = []
    for esp, keywords in especialidades_map.items():
        for kw in keywords:
            if kw in texto_lower:
                if esp not in encontradas:
                    encontradas.append(esp.title())
                break

    return encontradas


def identificar_rito(texto_lower: str, cabecalho: dict) -> str:
    """Identifica o rito processual."""
    classe = cabecalho["classe_pje"].lower()
    valor = cabecalho.get("valor_causa_float", 0)

    if "sumaríssimo" in classe or "sumarissimo" in classe:
        return "Sumaríssimo"
    if "sumário" in classe or "sumario" in classe:
        return "Sumário"
    if "especial" in classe:
        return "Especial"
    if "juizado" in texto_lower or "pequenas causas" in texto_lower:
        return "Juizado Especial"

    # Heurística por valor
    if valor > 0 and valor <= 40 * 1412:  # 40 salários mínimos (aprox)
        return "Ordinário (possível Juizado)"

    return "Ordinário"


def gerar_markdown(dados: dict) -> str:
    """Gera CLASSIFICACAO.md."""
    md = []
    md.append("## CLASSIFICAÇÃO DA AÇÃO\n")

    md.append(f"- **Tipo:** {dados['tipo']}")
    md.append(f"- **Subtipo:** {dados['subtipo'] or 'não identificado'}")
    md.append(f"- **Confiança:** {dados['confianca']}")
    md.append(f"- **Classe PJe:** {dados['classe_pje']}")
    md.append(f"- **Valor da causa:** {dados['valor_causa']}")
    md.append(f"- **Justiça gratuita:** {'Sim' if dados['justica_gratuita'] else 'Não'}")
    md.append(f"- **Segredo de justiça:** {'Sim' if dados['segredo_justica'] else 'Não'}")
    md.append(f"- **Rito:** {dados['rito']}")
    md.append(f"- **Assuntos:** {dados['assuntos']}")

    md.append("")

    if dados["objeto_pericia"]:
        md.append(f"### Objeto da Perícia")
        md.append(f"{dados['objeto_pericia']}")
        md.append("")

    if dados["especialidades_medicas"]:
        md.append(f"### Especialidades Médicas Identificadas")
        for esp in dados["especialidades_medicas"]:
            md.append(f"- {esp}")
        md.append("")

    if dados["alternativas"]:
        md.append("### Classificações Alternativas")
        for alt in dados["alternativas"]:
            md.append(f"- {alt['tipo']} — {alt['subtipo']} (score: {alt['score']})")
        md.append("")

    # Resumo em uma frase
    md.append("### Resumo")
    tipo = dados["tipo"]
    subtipo = f" ({dados['subtipo']})" if dados['subtipo'] else ""
    valor = f", valor {dados['valor_causa']}" if dados['valor_causa'] else ""
    gratuita = ", com justiça gratuita" if dados["justica_gratuita"] else ""
    md.append(f"Ação {tipo}{subtipo}{valor}{gratuita}.")

    meta = dados.get("_metadados", {})
    md.append(f"\n---\n*Classificado em {meta.get('extraido_em', '')} por classificar_acao.py*")

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


def atualizar_ficha(pasta: Path, dados: dict):
    ficha_path = pasta / "FICHA.json"
    if not ficha_path.exists():
        processos_dir = BASE_DIR / "processos"
        if processos_dir.exists():
            for p in processos_dir.iterdir():
                if p.is_dir() and (p / "FICHA.json").exists():
                    ficha_path = p / "FICHA.json"
                    break
    if not ficha_path.exists():
        return False

    try:
        ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False

    if dados["tipo"] != "NÃO CLASSIFICADA":
        ficha["area"] = dados["tipo"]
    if dados["subtipo"]:
        ficha["tipo_pericia"] = dados["subtipo"]
    if dados["objeto_pericia"]:
        ficha["objeto"] = dados["objeto_pericia"]
    if dados["especialidades_medicas"]:
        ficha["areas_medicas"] = dados["especialidades_medicas"]

    ficha["atualizado_em"] = datetime.now().isoformat()
    ficha_path.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="Classifica tipo de ação judicial")
    parser.add_argument("processo", nargs="?", help="Número CNJ ou caminho da pasta")
    parser.add_argument("--arquivo", "-a", help="Caminho direto para TEXTO-EXTRAIDO.txt")
    parser.add_argument("--output", "-o", help="Pasta de saída")
    parser.add_argument("--json-only", action="store_true", help="Imprimir JSON no stdout")
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
    dados = classificar(texto)

    if args.json_only:
        print(json.dumps(dados, ensure_ascii=False, indent=2))
        sys.exit(0)

    output_dir = Path(args.output) if args.output else pasta

    json_path = output_dir / "CLASSIFICACAO.json"
    json_path.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    md_path = output_dir / "CLASSIFICACAO.md"
    md_path.write_text(gerar_markdown(dados), encoding="utf-8")

    ficha_ok = atualizar_ficha(pasta, dados)

    # Cor por confiança
    cor = C.G if dados["confianca"] == "ALTA" else C.Y if dados["confianca"] == "MÉDIA" else C.RE
    print(f"\n{C.B}CLASSIFICAÇÃO DA AÇÃO{C.R}")
    print(f"  Tipo:       {cor}{dados['tipo']}{C.R}")
    print(f"  Subtipo:    {dados['subtipo'] or '—'}")
    print(f"  Confiança:  {cor}{dados['confianca']}{C.R} (score: {dados['score']})")
    print(f"  Valor:      {dados['valor_causa']}")
    print(f"  Gratuita:   {'Sim' if dados['justica_gratuita'] else 'Não'}")
    if dados["especialidades_medicas"]:
        print(f"  Medicina:   {', '.join(dados['especialidades_medicas'])}")
    print(f"\n  {C.DIM}→ {json_path}{C.R}")
    print(f"  {C.DIM}→ {md_path}{C.R}")
    if ficha_ok:
        print(f"  {C.DIM}→ FICHA.json atualizada{C.R}")


if __name__ == "__main__":
    main()
