#!/usr/bin/env python3
"""
extrair_partes.py — Extrai partes processuais do TEXTO-EXTRAIDO.txt via regex.

Saída: PARTES.json + PARTES.md na pasta do processo.
Atualiza FICHA.json se existir.

Uso:
    python3 extrair_partes.py 5002424-62.2025.8.13.0309
    python3 extrair_partes.py /caminho/para/pasta/do/processo
    python3 extrair_partes.py --arquivo /caminho/TEXTO-EXTRAIDO.txt
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


# Regex patterns
RE_CNJ = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")
RE_CPF = re.compile(r"\d{3}\.?\d{3}\.?\d{3}[-.]?\d{2}")
RE_CNPJ = re.compile(r"\d{2}\.?\d{3}\.?\d{3}[/.]?\d{4}[-.]?\d{2}")
RE_OAB = re.compile(r"OAB[/\s]?([A-Z]{2})[\s.]?(\d+[\.\d]*)", re.IGNORECASE)
RE_CRM = re.compile(r"CRM[/-]?\s*([A-Z]{2})\s*[\-:]?\s*(\d+[\.\d]*)", re.IGNORECASE)

# Roles no PJe
ROLES_ATIVO = {"REQUERENTE", "AUTOR", "AUTORA", "RECLAMANTE", "EXEQUENTE", "IMPETRANTE", "APELANTE", "AGRAVANTE", "EMBARGANTE", "SUPLICANTE"}
ROLES_PASSIVO = {"REQUERIDO", "REQUERIDO(A)", "REQUERIDA", "RÉU", "RÉ", "RÉU/RÉ", "RECLAMADO", "RECLAMADO(A)", "RECLAMADA", "EXECUTADO", "EXECUTADO(A)", "EXECUTADA", "IMPETRADO", "APELADO", "AGRAVADO", "EMBARGADO"}
ROLES_ADV = {"ADVOGADO", "ADVOGADO(A)", "ADVOGADA"}
ROLES_PERITO = {"PERITO", "PERITO(A)", "PERITA"}
ROLES_ASSIST = {"ASSISTENTE TÉCNICO", "ASSISTENTE TÉCNICO(A)", "ASSISTENTE TÉCNICA"}


def encontrar_pasta_processo(identificador: str) -> Path:
    """Encontra pasta do processo pelo CNJ ou caminho."""
    p = Path(identificador)
    if p.is_dir():
        return p
    # Buscar na raiz do analisador
    for pasta in BASE_DIR.iterdir():
        if pasta.is_dir() and identificador in pasta.name:
            return pasta
    # Buscar em processos/
    processos_dir = BASE_DIR / "processos"
    if processos_dir.exists():
        for pasta in processos_dir.iterdir():
            if pasta.is_dir() and identificador in pasta.name:
                return pasta
    return None


def encontrar_texto_extraido(pasta: Path) -> Path:
    """Encontra TEXTO-EXTRAIDO.txt na pasta."""
    candidatos = [
        pasta / "TEXTO-EXTRAIDO.txt",
        pasta / "texto-extraido.txt",
        pasta / "TEXTO_EXTRAIDO.txt",
    ]
    for c in candidatos:
        if c.exists():
            return c
    # Buscar qualquer .txt grande
    for f in pasta.glob("*.txt"):
        if f.stat().st_size > 5000:
            return f
    return None


def extrair_cabecalho(linhas: list[str]) -> dict:
    """Extrai metadados do cabeçalho PJe (primeiras ~15 linhas)."""
    dados = {
        "numero_cnj": "",
        "classe": "",
        "orgao_julgador": "",
        "vara": "",
        "comarca": "",
        "valor_causa": "",
        "assuntos": "",
        "segredo_justica": False,
        "justica_gratuita": False,
    }

    for i, linha in enumerate(linhas[:30]):
        linha = linha.strip()

        if linha.startswith("Número:"):
            m = RE_CNJ.search(linha)
            if m:
                dados["numero_cnj"] = m.group()

        elif linha.startswith("Classe:"):
            dados["classe"] = linha.replace("Classe:", "").strip()

        elif linha.startswith("Órgão julgador:"):
            orgao = linha.replace("Órgão julgador:", "").strip()
            dados["orgao_julgador"] = orgao
            # Extrair vara e comarca
            m_vara = re.match(r"(.+?)\s+da\s+Comarca\s+de\s+(.+?)(?:\s*-.*)?$", orgao)
            if m_vara:
                dados["vara"] = m_vara.group(1).strip()
                dados["comarca"] = m_vara.group(2).strip()
            else:
                # Tentar variações
                m_vara2 = re.match(r"(.+?Vara.+?)\s+(?:da\s+)?(?:Comarca\s+(?:de\s+)?)?(.+?)(?:\s*-.*)?$", orgao)
                if m_vara2:
                    dados["vara"] = m_vara2.group(1).strip()
                    dados["comarca"] = m_vara2.group(2).strip()

        elif linha.startswith("Valor da causa:"):
            m_val = re.search(r"R\$\s*([\d.,]+)", linha)
            if m_val:
                dados["valor_causa"] = "R$ " + m_val.group(1)

        elif linha.startswith("Assuntos:"):
            dados["assuntos"] = linha.replace("Assuntos:", "").strip()

        elif "Segredo de justiça?" in linha:
            dados["segredo_justica"] = "SIM" in linha.upper()

        elif "Justiça gratuita?" in linha or "gratuita?" in linha:
            dados["justica_gratuita"] = "SIM" in linha.upper()

    return dados


def extrair_partes_pje(linhas: list[str]) -> dict:
    """Extrai partes da seção de partes do PJe."""
    resultado = {
        "polo_ativo": [],
        "polo_passivo": [],
        "advogados": [],
        "peritos": [],
        "assistentes_tecnicos": [],
        "outros": [],
    }

    # Padrão: NOME (ROLE) — lida com parênteses aninhados como REQUERIDO(A), PERITO(A)
    # Captura tudo entre o ÚLTIMO par de parênteses
    re_parte = re.compile(r"^(.+)\s+\(([^()]*(?:\([^()]*\))?[^()]*)\)\s*$")

    # Procurar seção de partes (linhas 15-50 tipicamente)
    em_secao_partes = False
    secao_docs = False

    for i, linha in enumerate(linhas[:200]):
        linha = linha.strip()

        if linha == "Partes":
            em_secao_partes = True
            continue
        if linha == "Documentos" or linha.startswith("Id."):
            secao_docs = True
            break
        if linha in ("Advogados", "Outros participantes", ""):
            continue

        if not em_secao_partes:
            continue

        m = re_parte.match(linha)
        if not m:
            continue

        nome = m.group(1).strip()
        role = m.group(2).strip().upper()

        entrada = {"nome": nome, "role_original": m.group(2).strip()}

        # Extrair CPF/CNPJ do nome se presente
        cpf_m = RE_CPF.search(nome)
        if cpf_m:
            entrada["cpf"] = cpf_m.group()
            entrada["nome"] = RE_CPF.sub("", nome).strip(" -,")

        cnpj_m = RE_CNPJ.search(nome)
        if cnpj_m:
            entrada["cnpj"] = cnpj_m.group()
            entrada["nome"] = RE_CNPJ.sub("", nome).strip(" -,")

        # Classificar
        if role in ROLES_ATIVO:
            resultado["polo_ativo"].append(entrada)
        elif role in ROLES_PASSIVO:
            resultado["polo_passivo"].append(entrada)
        elif role in ROLES_ADV:
            resultado["advogados"].append(entrada)
        elif role in ROLES_PERITO:
            resultado["peritos"].append(entrada)
        elif role in ROLES_ASSIST:
            resultado["assistentes_tecnicos"].append(entrada)
        else:
            entrada["role"] = role
            resultado["outros"].append(entrada)

    return resultado


def vincular_advogados(partes: dict) -> dict:
    """Vincula advogados aos seus clientes pela ordem no texto PJe."""
    polo_ativo = partes["polo_ativo"]
    polo_passivo = partes["polo_passivo"]
    advogados = partes["advogados"]

    # No PJe, advogados aparecem logo após sua parte
    # Simplificação: construir a ordem original
    # Primeiro advogado após última parte ativa → polo ativo
    # Primeiro advogado após última parte passiva → polo passivo

    resultado = {
        "polo_ativo": [],
        "polo_passivo": [],
        "juizo": {"juiz": "", "vara": "", "comarca": ""},
        "pericia": {
            "perito_nomeado": "",
            "perito_anterior": "",
            "assistentes": [],
        },
        "outros": {"mp": False, "litisconsortes": []},
    }

    # Copiar partes com advogados vazios
    for p in polo_ativo:
        resultado["polo_ativo"].append({
            "nome": p["nome"],
            "cpf": p.get("cpf", ""),
            "cnpj": p.get("cnpj", ""),
            "advogados": [],
        })

    for p in polo_passivo:
        resultado["polo_passivo"].append({
            "nome": p["nome"],
            "cpf": p.get("cpf", ""),
            "cnpj": p.get("cnpj", ""),
            "advogados": [],
        })

    # Vincular advogados: dividir proporcionalmente
    # Heurística: se 1 parte ativa e 1 passiva com N advogados,
    # os primeiros são do ativo, os últimos do passivo
    if polo_ativo and polo_passivo and advogados:
        idx_corte = len(polo_ativo)  # Número de advogados para o polo ativo
        # Contar quantos advogados antes da primeira parte passiva
        # Usar heurística: primeiro adv é do ativo, segundo pode ser do passivo
        # Melhor: atribuir por posição relativa
        advs_por_polo = _atribuir_advogados_por_posicao(partes)
        for adv in advs_por_polo.get("ativo", []):
            for pa in resultado["polo_ativo"]:
                pa["advogados"].append({"nome": adv["nome"], "oab": ""})
        for adv in advs_por_polo.get("passivo", []):
            for pp in resultado["polo_passivo"]:
                pp["advogados"].append({"nome": adv["nome"], "oab": ""})

    # Peritos
    for p in partes["peritos"]:
        if not resultado["pericia"]["perito_nomeado"]:
            resultado["pericia"]["perito_nomeado"] = p["nome"]
        else:
            resultado["pericia"]["perito_anterior"] = p["nome"]

    # Assistentes técnicos
    for a in partes["assistentes_tecnicos"]:
        resultado["pericia"]["assistentes"].append(a["nome"])

    # Outros
    for o in partes["outros"]:
        if "MINISTÉRIO PÚBLICO" in o["nome"].upper() or "MP" in o.get("role", ""):
            resultado["outros"]["mp"] = True
        else:
            resultado["outros"]["litisconsortes"].append(o["nome"])

    return resultado


def _atribuir_advogados_por_posicao(partes: dict) -> dict:
    """Atribui advogados ao polo correto baseado na ordem original do PJe.

    No PJe, a ordem é:
    PARTE ATIVA (REQUERENTE)
    ADV DO ATIVO (ADVOGADO)
    PARTE PASSIVA (RÉU)
    ADV DO PASSIVO (ADVOGADO)
    """
    # Reconstruir ordem original
    todos = []
    for p in partes["polo_ativo"]:
        todos.append(("ativo", p))
    for p in partes["polo_passivo"]:
        todos.append(("passivo", p))

    # Os advogados ficam intercalados
    advs = partes["advogados"]
    resultado = {"ativo": [], "passivo": []}

    if not advs:
        return resultado

    # Heurística simples: cada advogado pertence ao polo da última parte vista
    # Mas no PJe a seção é separada...
    # Alternativa pragmática: dividir pela metade
    n_ativos = len(partes["polo_ativo"])
    n_passivos = len(partes["polo_passivo"])
    n_advs = len(advs)

    if n_ativos > 0 and n_passivos > 0:
        # Primeiros advogados são do polo ativo
        corte = max(1, n_advs * n_ativos // (n_ativos + n_passivos))
        resultado["ativo"] = advs[:corte]
        resultado["passivo"] = advs[corte:]
    elif n_ativos > 0:
        resultado["ativo"] = advs
    else:
        resultado["passivo"] = advs

    return resultado


def buscar_oab_no_texto(texto: str, nome_adv: str) -> str:
    """Busca número OAB associado a um advogado no texto completo."""
    nome_partes = nome_adv.upper().split()
    if len(nome_partes) < 2:
        return ""

    # Buscar OAB próximo ao nome (±500 caracteres)
    texto_upper = texto.upper()
    pos = texto_upper.find(nome_partes[0])
    while pos != -1:
        # Verificar se é o nome completo (pelo menos primeiro e último)
        trecho = texto_upper[pos:pos + len(nome_adv) + 50]
        if nome_partes[-1] in trecho:
            # Buscar OAB nas proximidades
            vizinhanca = texto[max(0, pos - 200):pos + len(nome_adv) + 500]
            m = RE_OAB.search(vizinhanca)
            if m:
                return f"OAB/{m.group(1)} {m.group(2)}"
        pos = texto_upper.find(nome_partes[0], pos + 1)

    # Busca global por padrão OAB seguido de UF
    for m in RE_OAB.finditer(texto):
        return f"OAB/{m.group(1)} {m.group(2)}"

    return ""


def buscar_juiz_no_texto(texto: str, nomes_conhecidos: list[str] = None) -> str:
    """Busca nome do juiz no texto completo.

    nomes_conhecidos: lista de nomes de partes/advogados para filtrar.
    """
    if nomes_conhecidos is None:
        nomes_conhecidos = []

    # Nomes a filtrar sempre
    filtrar = {"JESUS EDUARDO", "NOLETO"}
    for nome in nomes_conhecidos:
        for parte in nome.upper().split():
            if len(parte) > 3:
                filtrar.add(parte)

    # Padrões específicos de juiz (mais restritivos)
    padroes_juiz = [
        r"(?:Juiz|Juíza|Juiz\(a\)|Magistrado|Magistrada)\s*(?:de Direito\s*)?:?\s*([A-ZÀ-Ú][A-ZÀ-Ú\s]{5,50})",
        r"(?:Dr|Dra|Dr\.|Dra\.)\s*([A-ZÀ-Ú][A-ZÀ-Ú\s]{5,50}?)(?:\s*,?\s*Juiz)",
        # Assinatura em decisões/despachos — buscar perto de "Vistos", "Decido", "Defiro"
        r"(?:Vistos|Decido|Defiro|Indefiro|Determino).{0,500}Assinado\s+(?:eletronicamente\s+)?por:?\s*([A-ZÀ-Ú][A-ZÀ-Ú\s]+?)(?:\s*-\s*\d)",
    ]

    for padrao in padroes_juiz:
        matches = re.findall(padrao, texto, re.DOTALL)
        for m in matches:
            nome = m.strip()
            nome_upper = nome.upper()
            # Filtrar nomes conhecidos (partes, advogados, perito)
            if any(parte in nome_upper for parte in filtrar):
                continue
            if len(nome.split()) >= 2:
                return nome

    return ""


def extrair(texto: str) -> dict:
    """Pipeline principal de extração."""
    linhas = texto.split("\n")

    # 1. Cabeçalho
    cabecalho = extrair_cabecalho(linhas)

    # 2. Partes brutas
    partes_brutas = extrair_partes_pje(linhas)

    # 3. Vincular e estruturar
    resultado = vincular_advogados(partes_brutas)

    # 4. Preencher juízo
    resultado["juizo"]["vara"] = cabecalho["vara"]
    resultado["juizo"]["comarca"] = cabecalho["comarca"]
    # Coletar nomes conhecidos para filtrar da busca de juiz
    nomes_conhecidos = []
    for polo in ("polo_ativo", "polo_passivo"):
        for parte in resultado[polo]:
            nomes_conhecidos.append(parte["nome"])
            for adv in parte.get("advogados", []):
                nomes_conhecidos.append(adv["nome"])
    for p in partes_brutas["advogados"]:
        nomes_conhecidos.append(p["nome"])
    resultado["juizo"]["juiz"] = buscar_juiz_no_texto(texto, nomes_conhecidos)

    # 5. Buscar OABs
    for polo in ("polo_ativo", "polo_passivo"):
        for parte in resultado[polo]:
            for adv in parte["advogados"]:
                if not adv.get("oab"):
                    adv["oab"] = buscar_oab_no_texto(texto, adv["nome"])

    # 6. Metadados extras
    resultado["_metadados"] = {
        "numero_cnj": cabecalho["numero_cnj"],
        "classe": cabecalho["classe"],
        "valor_causa": cabecalho["valor_causa"],
        "assuntos": cabecalho["assuntos"],
        "segredo_justica": cabecalho["segredo_justica"],
        "justica_gratuita": cabecalho["justica_gratuita"],
        "extraido_em": datetime.now().isoformat(),
        "script": "extrair_partes.py",
    }

    return resultado


def gerar_markdown(dados: dict) -> str:
    """Gera PARTES.md a partir dos dados extraídos."""
    md = []
    md.append("## PARTES DO PROCESSO\n")
    meta = dados.get("_metadados", {})
    if meta.get("numero_cnj"):
        md.append(f"**Processo:** {meta['numero_cnj']}\n")

    # Polo ativo
    md.append("### POLO ATIVO (Autor)")
    for p in dados["polo_ativo"]:
        md.append(f"- **Nome:** {p['nome']}")
        if p.get("cpf"):
            md.append(f"  - CPF: {p['cpf']}")
        if p.get("cnpj"):
            md.append(f"  - CNPJ: {p['cnpj']}")
        for adv in p.get("advogados", []):
            oab = f" ({adv['oab']})" if adv.get("oab") else ""
            md.append(f"  - Advogado: {adv['nome']}{oab}")
    if not dados["polo_ativo"]:
        md.append("- Não identificado no texto")

    md.append("")

    # Polo passivo
    md.append("### POLO PASSIVO (Réu)")
    for p in dados["polo_passivo"]:
        md.append(f"- **Nome:** {p['nome']}")
        if p.get("cpf"):
            md.append(f"  - CPF: {p['cpf']}")
        if p.get("cnpj"):
            md.append(f"  - CNPJ: {p['cnpj']}")
        for adv in p.get("advogados", []):
            oab = f" ({adv['oab']})" if adv.get("oab") else ""
            md.append(f"  - Advogado: {adv['nome']}{oab}")
    if not dados["polo_passivo"]:
        md.append("- Não identificado no texto")

    md.append("")

    # Juízo
    md.append("### JUÍZO")
    j = dados["juizo"]
    md.append(f"- **Juiz(a):** {j['juiz'] or 'não identificado no texto'}")
    md.append(f"- **Vara:** {j['vara'] or 'não identificada'}")
    md.append(f"- **Comarca:** {j['comarca'] or 'não identificada'}")

    md.append("")

    # Perícia
    md.append("### PERÍCIA")
    per = dados["pericia"]
    md.append(f"- **Perito nomeado:** {per['perito_nomeado'] or 'não identificado'}")
    md.append(f"- **Perito anterior:** {per['perito_anterior'] or 'primeiro perito'}")
    for a in per.get("assistentes", []):
        md.append(f"- **Assistente técnico:** {a}")
    if not per.get("assistentes"):
        md.append("- **Assistentes técnicos:** não indicados")

    md.append("")

    # Outros
    md.append("### OUTROS")
    outros = dados["outros"]
    md.append(f"- **Ministério Público:** {'Sim' if outros['mp'] else 'Não'}")
    if outros.get("litisconsortes"):
        for l in outros["litisconsortes"]:
            md.append(f"- **Litisconsorte:** {l}")
    else:
        md.append("- **Litisconsortes:** não há")

    md.append("")

    # Metadados
    md.append("### DADOS PROCESSUAIS")
    md.append(f"- **Classe:** {meta.get('classe', '')}")
    md.append(f"- **Valor da causa:** {meta.get('valor_causa', '')}")
    md.append(f"- **Assuntos:** {meta.get('assuntos', '')}")
    md.append(f"- **Segredo de justiça:** {'Sim' if meta.get('segredo_justica') else 'Não'}")
    md.append(f"- **Justiça gratuita:** {'Sim' if meta.get('justica_gratuita') else 'Não'}")

    md.append(f"\n---\n*Extraído em {meta.get('extraido_em', '')} por extrair_partes.py*")

    return "\n".join(md)


def atualizar_ficha(pasta: Path, dados: dict):
    """Atualiza FICHA.json com dados extraídos (se existir)."""
    ficha_path = pasta / "FICHA.json"
    if not ficha_path.exists():
        # Tentar em processos/
        processos_dir = BASE_DIR / "processos"
        if processos_dir.exists():
            cnj = dados.get("_metadados", {}).get("numero_cnj", "")
            for p in processos_dir.iterdir():
                if p.is_dir() and cnj in str(p):
                    ficha_path = p / "FICHA.json"
                    break

    if not ficha_path.exists():
        return False

    try:
        ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False

    # Atualizar campos
    meta = dados.get("_metadados", {})
    if meta.get("numero_cnj"):
        ficha["numero_cnj"] = meta["numero_cnj"]

    juizo = dados.get("juizo", {})
    if juizo.get("vara"):
        ficha["vara"] = juizo["vara"]
    if juizo.get("comarca"):
        ficha["comarca"] = juizo["comarca"]

    # Partes
    if "partes" not in ficha:
        ficha["partes"] = {}

    if dados["polo_ativo"]:
        ficha["partes"]["autor"] = dados["polo_ativo"][0]["nome"]
    if dados["polo_passivo"]:
        ficha["partes"]["reu"] = dados["polo_passivo"][0]["nome"]

    ficha["atualizado_em"] = datetime.now().isoformat()

    ficha_path.write_text(
        json.dumps(ficha, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Extrai partes processuais do TEXTO-EXTRAIDO.txt"
    )
    parser.add_argument(
        "processo",
        nargs="?",
        help="Número CNJ ou caminho da pasta do processo"
    )
    parser.add_argument(
        "--arquivo", "-a",
        help="Caminho direto para TEXTO-EXTRAIDO.txt"
    )
    parser.add_argument(
        "--output", "-o",
        help="Pasta de saída (default: pasta do processo)"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Imprimir JSON no stdout e sair"
    )
    args = parser.parse_args()

    # Resolver arquivo de entrada
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

    # Ler texto
    texto = arquivo.read_text(encoding="utf-8")

    # Extrair
    dados = extrair(texto)

    # Saída JSON no stdout
    if args.json_only:
        print(json.dumps(dados, ensure_ascii=False, indent=2))
        sys.exit(0)

    # Pasta de saída
    output_dir = Path(args.output) if args.output else pasta

    # Salvar JSON
    json_path = output_dir / "PARTES.json"
    json_path.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # Salvar Markdown
    md_path = output_dir / "PARTES.md"
    md_path.write_text(gerar_markdown(dados), encoding="utf-8")

    # Atualizar FICHA.json
    ficha_ok = atualizar_ficha(pasta, dados)

    # Resumo
    n_ativo = len(dados["polo_ativo"])
    n_passivo = len(dados["polo_passivo"])
    n_advs = sum(len(p.get("advogados", [])) for p in dados["polo_ativo"] + dados["polo_passivo"])
    perito = dados["pericia"]["perito_nomeado"]

    print(f"\n{C.B}PARTES EXTRAÍDAS{C.R}")
    print(f"  Polo ativo:  {C.G}{n_ativo}{C.R} parte(s)")
    print(f"  Polo passivo: {C.G}{n_passivo}{C.R} parte(s)")
    print(f"  Advogados:   {C.G}{n_advs}{C.R}")
    print(f"  Perito:      {C.CY}{perito or 'não identificado'}{C.R}")
    print(f"  Juiz:        {dados['juizo']['juiz'] or 'não identificado'}")
    print(f"\n  {C.DIM}→ {json_path}{C.R}")
    print(f"  {C.DIM}→ {md_path}{C.R}")
    if ficha_ok:
        print(f"  {C.DIM}→ FICHA.json atualizada{C.R}")


if __name__ == "__main__":
    main()
