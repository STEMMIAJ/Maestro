#!/usr/bin/env python3
"""
detectar_urgencia.py — Detecta prazos processuais e classifica urgência.

Saída: URGENCIA.json + URGENCIA.md na pasta do processo.
Atualiza FICHA.json se existir.

Uso:
    python3 detectar_urgencia.py 5002424-62.2025.8.13.0309
    python3 detectar_urgencia.py /caminho/para/pasta
    python3 detectar_urgencia.py --arquivo /caminho/TEXTO-EXTRAIDO.txt
"""

from pathlib import Path
import argparse, json, re, sys
from datetime import date, datetime, timedelta


BASE_DIR = Path(__file__).parent

class C:
    R = "\033[0m"
    B = "\033[1m"
    G = "\033[32m"
    Y = "\033[33m"
    RE = "\033[31m"
    CY = "\033[36m"
    DIM = "\033[2m"


# Meses em português
MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

# Prazos legais padrão (em dias úteis)
PRAZOS_LEGAIS = {
    "aceite": {"dias": 5, "base_legal": "Art. 465 §2º CPC", "descricao": "Aceite da nomeação"},
    "proposta": {"dias": 5, "base_legal": "Art. 465 §2º CPC", "descricao": "Proposta de honorários"},
    "escusa": {"dias": 15, "base_legal": "Art. 157 §1º CPC", "descricao": "Escusa (recusa)"},
    "quesitos_supl": {"dias": 15, "base_legal": "Art. 469 CPC", "descricao": "Manifestação sobre quesitos suplementares"},
    "laudo": {"dias": 30, "base_legal": "Art. 477 CPC", "descricao": "Entrega do laudo (prazo padrão, verificar decisão)"},
}

# Feriados nacionais 2025-2026
FERIADOS = {
    date(2025, 1, 1), date(2025, 3, 3), date(2025, 3, 4),
    date(2025, 4, 18), date(2025, 4, 21), date(2025, 5, 1),
    date(2025, 6, 19), date(2025, 9, 7), date(2025, 10, 12),
    date(2025, 11, 2), date(2025, 11, 15), date(2025, 12, 25),
    date(2026, 1, 1), date(2026, 2, 16), date(2026, 2, 17),
    date(2026, 4, 3), date(2026, 4, 21), date(2026, 5, 1),
    date(2026, 6, 4), date(2026, 9, 7), date(2026, 10, 12),
    date(2026, 11, 2), date(2026, 11, 15), date(2026, 12, 25),
}


def parse_data(texto_data: str) -> date | None:
    """Converte texto de data para objeto date."""
    texto_data = texto_data.strip().strip(".")

    # Formato dd/mm/yyyy
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", texto_data)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None

    # Formato dd/mm/yy
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2})\b", texto_data)
    if m:
        ano = int(m.group(3))
        ano = ano + 2000 if ano < 50 else ano + 1900
        try:
            return date(ano, int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None

    # Formato dd de mês de yyyy
    m = re.match(r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})", texto_data, re.IGNORECASE)
    if m:
        mes = MESES.get(m.group(2).lower())
        if mes:
            try:
                return date(int(m.group(3)), mes, int(m.group(1)))
            except ValueError:
                return None

    # Formato yyyy-mm-dd
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", texto_data)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None

    return None


def dias_uteis_entre(data_inicio: date, data_fim: date) -> int:
    """Calcula dias úteis entre duas datas."""
    if data_fim <= data_inicio:
        return -(dias_uteis_entre(data_fim, data_inicio))

    dias = 0
    atual = data_inicio + timedelta(days=1)
    while atual <= data_fim:
        if atual.weekday() < 5 and atual not in FERIADOS:
            dias += 1
        atual += timedelta(days=1)
    return dias


def adicionar_dias_uteis(data_base: date, dias: int) -> date:
    """Adiciona N dias úteis a uma data."""
    resultado = data_base
    adicionados = 0
    while adicionados < dias:
        resultado += timedelta(days=1)
        if resultado.weekday() < 5 and resultado not in FERIADOS:
            adicionados += 1
    return resultado


def extrair_intimacoes(texto: str) -> list[dict]:
    """Extrai intimações e suas datas."""
    resultados = []

    # Padrões de intimação
    padroes = [
        (r"(?:intimad[oa]|ciência|notificad[oa])\s+(?:em|na data de)\s+(\d{1,2}/\d{1,2}/\d{4})", "intimação"),
        (r"(?:publicação|publicado)\s+(?:em|na data de)\s+(\d{1,2}/\d{1,2}/\d{4})", "publicação"),
        (r"(?:intimação|intimação eletrônica).+?(\d{1,2}/\d{1,2}/\d{4})", "intimação"),
        (r"leitura\s+(?:confirmada\s+)?em\s+(\d{1,2}/\d{1,2}/\d{4})", "leitura"),
    ]

    for padrao, tipo in padroes:
        for m in re.finditer(padrao, texto, re.IGNORECASE):
            data = parse_data(m.group(1))
            if data:
                # Extrair contexto (±200 chars)
                inicio = max(0, m.start() - 100)
                fim = min(len(texto), m.end() + 200)
                contexto = texto[inicio:fim].replace("\n", " ").strip()

                resultados.append({
                    "tipo": tipo,
                    "data": data.isoformat(),
                    "data_obj": data,
                    "contexto": contexto,
                    "posicao": m.start(),
                })

    return resultados


def extrair_prazos_fixados(texto: str) -> list[dict]:
    """Extrai prazos fixados pelo juiz."""
    resultados = []

    padroes = [
        (r"prazo\s+de\s+(\d+)\s*(?:dias?\s+(?:úteis)?)", "prazo fixado"),
        (r"no\s+prazo\s+de\s+(\d+)\s*(?:dias?)", "prazo fixado"),
        (r"concedo\s+(?:o\s+)?prazo\s+de\s+(\d+)\s*dias?", "prazo judicial"),
        (r"(?:apresent|entreg)\w+\s+(?:o\s+)?laudo\s+(?:em|no prazo de)\s+(\d+)\s*dias?", "prazo do laudo"),
    ]

    for padrao, tipo in padroes:
        for m in re.finditer(padrao, texto, re.IGNORECASE):
            dias = int(m.group(1))
            inicio = max(0, m.start() - 100)
            fim = min(len(texto), m.end() + 200)
            contexto = texto[inicio:fim].replace("\n", " ").strip()

            resultados.append({
                "tipo": tipo,
                "dias": dias,
                "contexto": contexto,
                "posicao": m.start(),
            })

    return resultados


def extrair_audiencias(texto: str) -> list[dict]:
    """Extrai audiências e exames agendados."""
    resultados = []

    padroes = [
        (r"(?:audiência|exame pericial|perícia)\s+(?:designada?|marcad[ao]|agendad[ao])\s+para\s+(?:o\s+dia\s+)?(\d{1,2}/\d{1,2}/\d{4})", "audiência/exame"),
        (r"(?:audiência|exame pericial|perícia)\s+(?:designada?|marcad[ao]|agendad[ao])\s+para\s+(?:o\s+dia\s+)?(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})", "audiência/exame"),
    ]

    for padrao, tipo in padroes:
        for m in re.finditer(padrao, texto, re.IGNORECASE):
            data = parse_data(m.group(1))
            if data:
                inicio = max(0, m.start() - 50)
                fim = min(len(texto), m.end() + 200)
                contexto = texto[inicio:fim].replace("\n", " ").strip()

                resultados.append({
                    "tipo": tipo,
                    "data": data.isoformat(),
                    "data_obj": data,
                    "contexto": contexto,
                })

    return resultados


def extrair_ultima_movimentacao(texto: str) -> dict:
    """Identifica a última movimentação processual."""
    # Buscar datas de assinatura no cabeçalho PJe
    re_assinatura = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})\s+\d{2}:\d{2}")
    datas = []
    for m in re_assinatura.finditer(texto[:5000]):
        d = parse_data(m.group(1))
        if d:
            datas.append(d)

    # Buscar "Assinado eletronicamente por"
    re_assinado = re.compile(
        r"Assinado\s+eletronicamente\s+por:?\s*(.+?)\s*-\s*(\d{1,2}/\d{1,2}/\d{4})",
        re.IGNORECASE
    )
    ultima_mov = {"data": "", "tipo": "", "conteudo": ""}

    for m in re_assinado.finditer(texto):
        d = parse_data(m.group(2))
        if d:
            datas.append(d)
            if not ultima_mov["data"] or d > parse_data(ultima_mov["data"]):
                ultima_mov = {
                    "data": d.isoformat(),
                    "tipo": "Assinatura eletrônica",
                    "conteudo": f"Por: {m.group(1).strip()}",
                }

    if datas and not ultima_mov["data"]:
        mais_recente = max(datas)
        ultima_mov["data"] = mais_recente.isoformat()
        ultima_mov["tipo"] = "Movimentação identificada por data"

    return ultima_mov


def calcular_urgencia(texto: str) -> dict:
    """Pipeline principal de detecção de urgência."""
    hoje = date.today()

    intimacoes = extrair_intimacoes(texto)
    prazos_fixados = extrair_prazos_fixados(texto)
    audiencias = extrair_audiencias(texto)
    ultima_mov = extrair_ultima_movimentacao(texto)

    prazos = []

    # 1. Calcular prazos a partir de intimações
    for intim in intimacoes:
        data_intim = intim["data_obj"]

        # Para cada prazo legal, calcular vencimento
        for tipo_prazo, info in PRAZOS_LEGAIS.items():
            vencimento = adicionar_dias_uteis(data_intim, info["dias"])
            dias_restantes = dias_uteis_entre(hoje, vencimento)

            # Determinar se é relevante (não muito antigo)
            if dias_restantes < -60:
                continue

            status = "VENCIDO" if dias_restantes < 0 else "EM PRAZO"

            prazos.append({
                "tipo": info["descricao"],
                "base_legal": info["base_legal"],
                "data_intimacao": data_intim.isoformat(),
                "data_vencimento": vencimento.isoformat(),
                "dias_restantes": dias_restantes,
                "status": status,
                "contexto_intimacao": intim["contexto"][:200],
            })

    # 2. Adicionar prazos fixados pelo juiz
    for pf in prazos_fixados:
        # Tentar achar a intimação mais próxima anterior
        data_base = None
        for intim in sorted(intimacoes, key=lambda x: x["data_obj"], reverse=True):
            if intim["posicao"] <= pf["posicao"] + 2000:
                data_base = intim["data_obj"]
                break

        if not data_base and intimacoes:
            data_base = max(i["data_obj"] for i in intimacoes)

        if data_base:
            vencimento = adicionar_dias_uteis(data_base, pf["dias"])
            dias_restantes = dias_uteis_entre(hoje, vencimento)

            prazos.append({
                "tipo": f"Prazo judicial ({pf['dias']} dias)",
                "base_legal": "Decisão judicial",
                "data_intimacao": data_base.isoformat(),
                "data_vencimento": vencimento.isoformat(),
                "dias_restantes": dias_restantes,
                "status": "VENCIDO" if dias_restantes < 0 else "EM PRAZO",
                "contexto_intimacao": pf["contexto"][:200],
            })

    # 3. Adicionar audiências como prazos
    for aud in audiencias:
        data_aud = aud["data_obj"]
        dias_restantes = (data_aud - hoje).days

        prazos.append({
            "tipo": f"Audiência/Exame agendado",
            "base_legal": "Designação judicial",
            "data_intimacao": "",
            "data_vencimento": data_aud.isoformat(),
            "dias_restantes": dias_restantes,
            "status": "REALIZADO" if dias_restantes < 0 else "AGENDADO",
            "contexto_intimacao": aud["contexto"][:200],
        })

    # 4. Ordenar por urgência
    prazos.sort(key=lambda x: x["dias_restantes"])

    # 5. Classificar urgência geral
    if not prazos:
        classificacao = "SEM PRAZO"
    else:
        menor = prazos[0]["dias_restantes"]
        vencidos = [p for p in prazos if p["dias_restantes"] < 0 and p["status"] != "REALIZADO"]
        if vencidos:
            classificacao = "URGENTE"
        elif menor <= 3:
            classificacao = "URGENTE"
        elif menor <= 10:
            classificacao = "NORMAL"
        else:
            classificacao = "FOLGA"

    # 6. Gerar alertas
    alertas = []
    for p in prazos:
        if p["status"] == "VENCIDO":
            alertas.append(f"PRAZO VENCIDO: {p['tipo']} venceu em {p['data_vencimento']} ({abs(p['dias_restantes'])} dias úteis atrás)")
        elif 0 <= p["dias_restantes"] <= 3:
            alertas.append(f"URGENTE: {p['tipo']} vence em {p['data_vencimento']} ({p['dias_restantes']} dias úteis)")

    # 7. Recomendação
    if classificacao == "URGENTE":
        recomendacao = "Ação imediata necessária. Verificar prazos vencidos ou próximos do vencimento."
    elif classificacao == "NORMAL":
        recomendacao = "Prazos dentro do normal. Planejar ações para os próximos dias."
    elif classificacao == "FOLGA":
        recomendacao = "Sem urgência imediata. Prazos confortáveis."
    else:
        recomendacao = "Nenhum prazo identificado no texto. Verificar manualmente se há intimações pendentes."

    resultado = {
        "classificacao": classificacao,
        "data_analise": hoje.isoformat(),
        "prazos": prazos,
        "audiencias": [{"data": a["data"], "tipo": a["tipo"], "contexto": a["contexto"][:200]} for a in audiencias],
        "alertas": alertas,
        "ultima_movimentacao": ultima_mov,
        "recomendacao": recomendacao,
        "_metadados": {
            "extraido_em": datetime.now().isoformat(),
            "script": "detectar_urgencia.py",
            "total_intimacoes": len(intimacoes),
            "total_prazos": len(prazos),
        },
    }

    return resultado


def gerar_markdown(dados: dict) -> str:
    """Gera URGENCIA.md."""
    md = []
    cls = dados["classificacao"]

    # Emoji por urgência
    icone = {"URGENTE": "!!!", "NORMAL": "---", "FOLGA": "...", "SEM PRAZO": "???"}

    md.append(f"## ANÁLISE DE URGÊNCIA\n")
    md.append(f"### Classificação: {icone.get(cls, '')} {cls}\n")

    # Prazos
    if dados["prazos"]:
        md.append("### Prazos encontrados\n")
        md.append("| # | Tipo | Vencimento | Dias restantes | Status |")
        md.append("|---|------|-----------|----------------|--------|")
        for i, p in enumerate(dados["prazos"], 1):
            dias = f"{p['dias_restantes']} dias úteis"
            md.append(f"| {i} | {p['tipo']} | {p['data_vencimento']} | {dias} | {p['status']} |")
        md.append("")

    # Audiências
    if dados["audiencias"]:
        md.append("### Audiências/Exames agendados")
        for a in dados["audiencias"]:
            md.append(f"- {a['data']} — {a['tipo']}")
        md.append("")

    # Alertas
    if dados["alertas"]:
        md.append("### Alertas")
        for alerta in dados["alertas"]:
            md.append(f"1. {alerta}")
        md.append("")

    # Última movimentação
    mov = dados["ultima_movimentacao"]
    if mov.get("data"):
        md.append("### Última movimentação processual")
        md.append(f"- Data: {mov['data']}")
        md.append(f"- Tipo: {mov['tipo']}")
        md.append(f"- Conteúdo: {mov['conteudo']}")
        md.append("")

    # Recomendação
    md.append("### Recomendação")
    md.append(dados["recomendacao"])

    meta = dados.get("_metadados", {})
    md.append(f"\n---\n*Analisado em {meta.get('extraido_em', '')} por detectar_urgencia.py*")

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

    # Atualizar prazos
    if dados["prazos"]:
        proximo = dados["prazos"][0]
        if "prazos" not in ficha:
            ficha["prazos"] = {}
        ficha["prazos"]["proximo"] = proximo["data_vencimento"]
        ficha["prazos"]["tipo"] = proximo["tipo"]
        ficha["prazos"]["dias_restantes"] = proximo["dias_restantes"]

    # Atualizar status se urgente
    if dados["classificacao"] == "URGENTE":
        ficha["urgencia"] = "URGENTE"

    ficha["atualizado_em"] = datetime.now().isoformat()
    ficha_path.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="Detecta prazos processuais e classifica urgência")
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
    dados = calcular_urgencia(texto)

    if args.json_only:
        print(json.dumps(dados, ensure_ascii=False, indent=2))
        sys.exit(0)

    output_dir = Path(args.output) if args.output else pasta

    json_path = output_dir / "URGENCIA.json"
    json_path.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    md_path = output_dir / "URGENCIA.md"
    md_path.write_text(gerar_markdown(dados), encoding="utf-8")

    ficha_ok = atualizar_ficha(pasta, dados)

    # Cor por classificação
    cores = {"URGENTE": C.RE, "NORMAL": C.Y, "FOLGA": C.G, "SEM PRAZO": C.DIM}
    cor = cores.get(dados["classificacao"], C.R)

    print(f"\n{C.B}ANÁLISE DE URGÊNCIA{C.R}")
    print(f"  Classificação: {cor}{dados['classificacao']}{C.R}")
    print(f"  Prazos:        {len(dados['prazos'])}")
    print(f"  Alertas:       {len(dados['alertas'])}")
    for a in dados["alertas"][:3]:
        print(f"    {C.RE}! {a}{C.R}")
    print(f"  Recomendação:  {dados['recomendacao']}")
    print(f"\n  {C.DIM}→ {json_path}{C.R}")
    print(f"  {C.DIM}→ {md_path}{C.R}")
    if ficha_ok:
        print(f"  {C.DIM}→ FICHA.json atualizada{C.R}")


if __name__ == "__main__":
    main()
