#!/usr/bin/env python3
"""
classificar_documento.py — Classifica tipo de documento judicial por indicadores.

Saída: JSON com tipo, subtipo, confiança e metadados.
Pode classificar um documento individual ou todos os documentos listados no TEXTO-EXTRAIDO.txt.

Uso:
    python3 classificar_documento.py --texto "conteúdo do documento"
    python3 classificar_documento.py --arquivo /caminho/documento.txt
    python3 classificar_documento.py --indice 5002424-62.2025.8.13.0309
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


# Categorias com indicadores e pesos
CATEGORIAS = [
    {
        "tipo": "LAUDO_MEDICO",
        "label": "Laudo Médico",
        "indicadores": [
            ("laudo", 3), ("parecer médico", 4), ("exame pericial", 4),
            ("laudo pericial", 5), ("perito", 2), ("diagnóstico", 2),
            ("conclusão médica", 3), ("exame clínico", 3),
        ],
    },
    {
        "tipo": "ATESTADO",
        "label": "Atestado",
        "indicadores": [
            ("atesto que", 5), ("atestado", 4), ("atestado médico", 5),
            ("crm", 2), ("afastamento", 2), ("dias de repouso", 3),
            ("compareceu nesta", 3),
        ],
    },
    {
        "tipo": "RECEITA",
        "label": "Receita/Prescrição",
        "indicadores": [
            ("receituário", 5), ("prescrição", 4), ("uso contínuo", 4),
            ("tomar", 2), ("comprimido", 3), ("cápsula", 3),
            ("mg/dia", 3), ("via oral", 3), ("a cada", 2),
        ],
    },
    {
        "tipo": "EXAME_LABORATORIO",
        "label": "Exame Laboratorial",
        "indicadores": [
            ("hemograma", 5), ("glicemia", 4), ("colesterol", 3),
            ("mg/dl", 4), ("u/l", 4), ("mmol/l", 4),
            ("valores de referência", 5), ("material:", 3),
            ("resultado do exame", 4), ("laboratório", 3),
        ],
    },
    {
        "tipo": "EXAME_IMAGEM",
        "label": "Exame de Imagem",
        "indicadores": [
            ("laudo radiológico", 5), ("impressão diagnóstica", 4),
            ("ressonância magnética", 5), ("tomografia", 4),
            ("ultrassonografia", 4), ("raio-x", 3), ("radiografia", 3),
            ("achados", 2), ("técnica", 2), ("cortes axiais", 4),
        ],
    },
    {
        "tipo": "PRONTUARIO",
        "label": "Prontuário",
        "indicadores": [
            ("evolução", 3), ("anamnese", 5), ("hd:", 4), ("cd:", 4),
            ("hipótese diagnóstica", 5), ("conduta", 3),
            ("prontuário", 5), ("admissão hospitalar", 4),
            ("enfermagem", 2), ("prescrição médica", 3),
        ],
    },
    {
        "tipo": "PETICAO",
        "label": "Petição",
        "indicadores": [
            ("excelentíssimo", 4), ("mm. juiz", 4), ("meritíssimo", 4),
            ("requer", 3), ("requerente", 2), ("vem respeitosamente", 4),
            ("termos em que pede deferimento", 5), ("ante o exposto", 3),
            ("dos fatos", 2), ("do direito", 2), ("dos pedidos", 3),
        ],
    },
    {
        "tipo": "DECISAO",
        "label": "Decisão/Despacho",
        "indicadores": [
            ("vistos", 3), ("decido", 4), ("ante o exposto", 3),
            ("defiro", 4), ("indefiro", 4), ("determino", 4),
            ("nomeio perito", 5), ("fixo prazo", 4),
            ("cumpra-se", 4), ("cite-se", 4), ("intime-se", 4),
        ],
    },
    {
        "tipo": "DEPOIMENTO",
        "label": "Depoimento",
        "indicadores": [
            ("inquirido", 5), ("respondeu que", 4), ("declarou", 3),
            ("depoimento", 4), ("testemunha", 3), ("oitiva", 4),
            ("perguntado sobre", 4), ("disse que", 3),
        ],
    },
    {
        "tipo": "BO_CAT",
        "label": "B.O. / CAT",
        "indicadores": [
            ("boletim de ocorrência", 5), ("comunicação de acidente de trabalho", 5),
            ("cat", 2), ("delegacia", 3), ("registro policial", 4),
            ("ocorrência nº", 4), ("natureza:", 2),
        ],
    },
]

# Padrões para extrair metadados
RE_DATA_DOC = re.compile(
    r"(?:data|emitido em|em)\s*:?\s*(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}\s+de\s+\w+\s+de\s+\d{4})",
    re.IGNORECASE
)
RE_CRM = re.compile(r"CRM[/-]?\s*([A-Z]{2})\s*[\-:]?\s*(\d+[\.\d]*)", re.IGNORECASE)
RE_CRO = re.compile(r"CRO[/-]?\s*([A-Z]{2})\s*[\-:]?\s*(\d+[\.\d]*)", re.IGNORECASE)
RE_OAB = re.compile(r"OAB[/\s]?([A-Z]{2})[\s.]?(\d+[\.\d]*)", re.IGNORECASE)

# Especialidades médicas por contexto
ESPECIALIDADES = {
    "ortopedia": ["ortoped", "fratura", "articulação", "prótese", "coluna"],
    "neurologia": ["neurológ", "avc", "neuropat", "esclerose"],
    "psiquiatria": ["psiquiátr", "depressão", "ansiedade", "transtorno"],
    "cardiologia": ["cardiológ", "infarto", "arritmia", "cardíac"],
    "oftalmologia": ["oftalm", "visão", "acuidade visual"],
    "otorrinolaringologia": ["otorrino", "audiom", "perda auditiva"],
    "radiologia": ["radiolog", "tomografi", "ressonância"],
    "patologia clínica": ["hemograma", "bioquímica", "laboratorial"],
}


def classificar_documento(texto: str, nome_arquivo: str = "") -> dict:
    """Classifica um documento individual."""
    texto_lower = texto.lower()

    # 1. Pontuar cada categoria
    scores = []
    for cat in CATEGORIAS:
        score = 0
        indicadores_encontrados = []

        for indicador, peso in cat["indicadores"]:
            count = texto_lower.count(indicador.lower())
            if count > 0:
                score += peso * min(count, 3)  # Cap em 3 ocorrências
                indicadores_encontrados.append(indicador)

        scores.append({
            "tipo": cat["tipo"],
            "label": cat["label"],
            "score": score,
            "indicadores": indicadores_encontrados,
        })

    # Bonus: nome do arquivo pode indicar tipo
    if nome_arquivo:
        nome_lower = nome_arquivo.lower()
        for s in scores:
            label_lower = s["label"].lower()
            if label_lower in nome_lower or s["tipo"].lower().replace("_", " ") in nome_lower:
                s["score"] += 5

    # 2. Ordenar e selecionar
    scores.sort(key=lambda x: x["score"], reverse=True)

    melhor = scores[0] if scores and scores[0]["score"] > 0 else None
    segundo = scores[1] if len(scores) > 1 and scores[1]["score"] > 0 else None

    # 3. Confiança
    if not melhor or melhor["score"] == 0:
        tipo = "DESCONHECIDO"
        label = "Documento não classificado"
        confianca = "NENHUMA"
        indicadores = []
    else:
        tipo = melhor["tipo"]
        label = melhor["label"]
        indicadores = melhor["indicadores"]

        # Confiança baseada no score e na diferença com o segundo
        diff = melhor["score"] - (segundo["score"] if segundo else 0)
        if melhor["score"] >= 15 and diff >= 5:
            confianca = "ALTA"
        elif melhor["score"] >= 8:
            confianca = "MÉDIA"
        else:
            confianca = "BAIXA"

    # 4. Extrair metadados
    data_doc = ""
    for m in RE_DATA_DOC.finditer(texto):
        data_doc = m.group(1)
        break

    autor_emissor = ""
    registro = ""
    m_crm = RE_CRM.search(texto)
    if m_crm:
        registro = f"CRM/{m_crm.group(1)} {m_crm.group(2)}"
    else:
        m_oab = RE_OAB.search(texto)
        if m_oab:
            registro = f"OAB/{m_oab.group(1)} {m_oab.group(2)}"

    # Buscar nome do autor (perto do registro)
    if registro and m_crm:
        pos = m_crm.start()
        trecho = texto[max(0, pos - 200):pos]
        # Buscar nome em maiúsculas antes do CRM
        nomes = re.findall(r"(?:Dr\.?|Dra\.?)\s*([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+)*)", trecho)
        if nomes:
            autor_emissor = nomes[-1]

    # Especialidade
    especialidade = ""
    for esp, keywords in ESPECIALIDADES.items():
        for kw in keywords:
            if kw in texto_lower:
                especialidade = esp.title()
                break
        if especialidade:
            break

    # Instituição
    instituicao = ""
    padroes_inst = [
        r"(?:Hospital|Clínica|UBS|UPA|Centro Médico|Laboratório)\s+([A-ZÀ-Ú][\w\s]{3,50})",
    ]
    for padrao in padroes_inst:
        m = re.search(padrao, texto)
        if m:
            instituicao = m.group().strip()
            break

    resultado = {
        "tipo": tipo,
        "label": label,
        "confianca": confianca,
        "score": melhor["score"] if melhor else 0,
        "data_documento": data_doc,
        "autor_emissor": autor_emissor,
        "registro": registro,
        "especialidade": especialidade,
        "instituicao": instituicao,
        "indicadores_encontrados": indicadores,
        "nome_arquivo": nome_arquivo,
        "alternativas": [],
    }

    if segundo and segundo["score"] > 0:
        resultado["alternativas"].append({
            "tipo": segundo["tipo"],
            "label": segundo["label"],
            "score": segundo["score"],
        })

    return resultado


def extrair_indice_documentos(texto: str) -> list[dict]:
    """Extrai o índice de documentos do TEXTO-EXTRAIDO.txt do PJe."""
    documentos = []

    # Procurar seção "Documento" seguida de lista de nomes
    linhas = texto.split("\n")
    em_secao_docs = False
    em_secao_tipos = False
    nomes = []
    tipos = []

    for i, linha in enumerate(linhas[:500]):
        linha_strip = linha.strip()

        if linha_strip == "Documento":
            em_secao_docs = True
            continue
        if linha_strip == "Tipo":
            em_secao_docs = False
            em_secao_tipos = True
            continue

        if em_secao_docs and linha_strip and not linha_strip.isdigit():
            # Ignorar IDs e datas
            if not re.match(r"^\d{10,}$", linha_strip) and not re.match(r"^\d{1,2}/\d{1,2}/\d{4}", linha_strip) and "Sem movimento" not in linha_strip:
                nomes.append(linha_strip)

        if em_secao_tipos and linha_strip:
            if linha_strip and not re.match(r"^\d{10,}$", linha_strip) and not re.match(r"^\d{1,2}/\d{1,2}/\d{4}", linha_strip) and "Sem movimento" not in linha_strip:
                tipos.append(linha_strip)
            # Parar quando encontrar outro bloco de IDs
            if re.match(r"^\d{10,}$", linha_strip):
                em_secao_tipos = False

    # Combinar nomes e tipos
    for i, nome in enumerate(nomes):
        tipo_pje = tipos[i] if i < len(tipos) else ""
        documentos.append({
            "nome": nome,
            "tipo_pje": tipo_pje,
        })

    return documentos


def classificar_por_tipo_pje(tipo_pje: str, nome: str) -> dict:
    """Classificação rápida baseada no tipo do PJe (sem ler conteúdo)."""
    tipo_lower = tipo_pje.lower() if tipo_pje else ""
    nome_lower = nome.lower() if nome else ""
    combinado = f"{tipo_lower} {nome_lower}"

    mapa = {
        "petição inicial": ("PETICAO", "Petição Inicial", "ALTA"),
        "contestação": ("PETICAO", "Contestação", "ALTA"),
        "procuração": ("PETICAO", "Procuração", "ALTA"),
        "laudo médico": ("LAUDO_MEDICO", "Laudo Médico", "ALTA"),
        "laudo pericial": ("LAUDO_MEDICO", "Laudo Pericial", "ALTA"),
        "atestado": ("ATESTADO", "Atestado", "MÉDIA"),
        "documento pessoal": ("OUTRO", "Documento Pessoal", "ALTA"),
        "documento de comprovação": ("OUTRO", "Documento de Comprovação", "MÉDIA"),
        "comprovante de endereço": ("OUTRO", "Comprovante de Endereço", "ALTA"),
        "imposto de renda": ("OUTRO", "Imposto de Renda", "ALTA"),
        "declaração de hipossuficiência": ("PETICAO", "Declaração de Hipossuficiência", "ALTA"),
        "documento de identificação": ("OUTRO", "Documento de Identificação", "ALTA"),
    }

    for chave, (tipo, label, conf) in mapa.items():
        if chave in combinado:
            return {
                "tipo": tipo,
                "label": label,
                "confianca": conf,
                "score": 10,
                "fonte": "tipo_pje",
                "nome_arquivo": nome,
                "tipo_pje": tipo_pje,
            }

    return {
        "tipo": "NÃO_CLASSIFICADO",
        "label": f"{tipo_pje or nome}",
        "confianca": "BAIXA",
        "score": 0,
        "fonte": "tipo_pje",
        "nome_arquivo": nome,
        "tipo_pje": tipo_pje,
    }


def gerar_markdown_indice(documentos: list[dict]) -> str:
    """Gera INDICE-DOCUMENTOS.md."""
    md = []
    md.append("## ÍNDICE DE DOCUMENTOS DO PROCESSO\n")
    md.append(f"**Total:** {len(documentos)} documentos\n")

    md.append("| # | Nome | Tipo PJe | Classificação | Confiança |")
    md.append("|---|------|---------|---------------|----------|")
    for i, doc in enumerate(documentos, 1):
        nome = doc.get("nome", "")
        tipo_pje = doc.get("tipo_pje", "")
        classificacao = doc.get("label", doc.get("tipo", ""))
        confianca = doc.get("confianca", "")
        md.append(f"| {i} | {nome} | {tipo_pje} | {classificacao} | {confianca} |")

    md.append(f"\n---\n*Gerado em {datetime.now().isoformat()} por classificar_documento.py*")
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
    parser = argparse.ArgumentParser(description="Classifica tipo de documento judicial")
    parser.add_argument("--texto", "-t", help="Texto do documento para classificar")
    parser.add_argument("--arquivo", "-a", help="Arquivo de texto para classificar")
    parser.add_argument("--indice", "-i", help="CNJ do processo — extrai e classifica índice de documentos")
    parser.add_argument("--output", "-o", help="Pasta de saída")
    parser.add_argument("--json-only", action="store_true", help="Imprimir JSON no stdout")
    args = parser.parse_args()

    # Modo 1: Classificar texto direto
    if args.texto:
        resultado = classificar_documento(args.texto)
        if args.json_only:
            print(json.dumps(resultado, ensure_ascii=False, indent=2))
        else:
            print(f"\n{C.B}CLASSIFICAÇÃO:{C.R} {resultado['label']} ({resultado['confianca']})")
        sys.exit(0)

    # Modo 2: Classificar arquivo
    if args.arquivo:
        arquivo = Path(args.arquivo)
        if not arquivo.exists():
            print(f"{C.RE}Erro: arquivo não encontrado: {arquivo}{C.R}")
            sys.exit(1)
        texto = arquivo.read_text(encoding="utf-8")
        resultado = classificar_documento(texto, arquivo.name)
        if args.json_only:
            print(json.dumps(resultado, ensure_ascii=False, indent=2))
        else:
            print(f"\n{C.B}CLASSIFICAÇÃO:{C.R} {resultado['label']} ({resultado['confianca']})")
            print(f"  Indicadores: {', '.join(resultado['indicadores_encontrados'][:5])}")
        sys.exit(0)

    # Modo 3: Índice de documentos do processo
    if args.indice:
        pasta = encontrar_pasta_processo(args.indice)
        if not pasta:
            print(f"{C.RE}Erro: processo '{args.indice}' não encontrado.{C.R}")
            sys.exit(1)
        arquivo = encontrar_texto_extraido(pasta)
        if not arquivo:
            print(f"{C.RE}Erro: TEXTO-EXTRAIDO.txt não encontrado em {pasta}{C.R}")
            sys.exit(1)

        texto = arquivo.read_text(encoding="utf-8")
        docs_brutos = extrair_indice_documentos(texto)

        # Classificar cada documento pelo tipo PJe
        documentos = []
        for doc in docs_brutos:
            classificado = classificar_por_tipo_pje(doc["tipo_pje"], doc["nome"])
            classificado["nome"] = doc["nome"]
            classificado["tipo_pje"] = doc["tipo_pje"]
            documentos.append(classificado)

        resultado = {
            "total": len(documentos),
            "documentos": documentos,
            "_metadados": {
                "extraido_em": datetime.now().isoformat(),
                "script": "classificar_documento.py",
                "modo": "indice",
            },
        }

        if args.json_only:
            print(json.dumps(resultado, ensure_ascii=False, indent=2))
            sys.exit(0)

        output_dir = Path(args.output) if args.output else pasta

        json_path = output_dir / "INDICE-DOCUMENTOS.json"
        json_path.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

        md_path = output_dir / "INDICE-DOCUMENTOS.md"
        md_path.write_text(gerar_markdown_indice(documentos), encoding="utf-8")

        # Resumo
        tipos_contagem = {}
        for d in documentos:
            t = d.get("label", d.get("tipo", "Outro"))
            tipos_contagem[t] = tipos_contagem.get(t, 0) + 1

        print(f"\n{C.B}ÍNDICE DE DOCUMENTOS{C.R}")
        print(f"  Total: {len(documentos)}")
        for tipo, qtd in sorted(tipos_contagem.items(), key=lambda x: -x[1]):
            print(f"    {C.CY}{tipo}{C.R}: {qtd}")
        print(f"\n  {C.DIM}→ {json_path}{C.R}")
        print(f"  {C.DIM}→ {md_path}{C.R}")
        sys.exit(0)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
