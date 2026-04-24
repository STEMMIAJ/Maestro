#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extrator_completo.py — TJMG Guia Judiciário
Extrai dados completos (cabeçalho do fórum + setores + emails) de 1621 PDFs.

Estratégia para emails truncados (aprovada pelo Dr. Jesus — Time A):
- PyMuPDF dict/blocks devolve o texto literal armazenado no PDF, que é
  truncado pela coluna visual no momento da geração (ex.: "chssecretaria@tjmg.j").
- Como o domínio padrão TJMG é "@tjmg.jus.br", quando detectar truncagem
  (final em "@tj", "@tjm", "@tjmg.j", "@tjmg.jus.b", etc.), completar o
  sufixo até "tjmg.jus.br" e marcar email_completado_inferencia=True.
- Quando o PDF cortou totalmente o "@" (ex.: "admforum"), o prefixo é a
  própria sigla — registrar email como "<sigla_lower>@tjmg.jus.br" também
  marcado como inferência.

Refs falhas conhecidas:
- ref: GL-002  (encoding utf-8 padrão para evitar perda de acento ao logar)
- ref: PJE-019 (sanitização de path; aqui só leitura, não geramos arquivos com nome do PDF)

Uso:
  python3 extrator_completo.py [--limit N] [--pdfs A.pdf,B.pdf] [--resume]
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF

# ---------------------------------------------------------------------------
# Constantes / paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
LOGS_DIR = ROOT / "logs"
PDF_DIR = Path("/Users/jesus/Desktop/_MESA/30-DOCS/guia-judiciario-TJMG")

OUT_JSON = DATA_DIR / "contatos_completo.json"
LOG_FILE = LOGS_DIR / "extrator_completo.log"
ORFAOS_FILE = LOGS_DIR / "extrator_orfaos.json"
LOCALIDADES_JSON = DATA_DIR / "localidades.json"

DOMINIO_PADRAO = "tjmg.jus.br"
SUFIXO_COMPLETO = "@" + DOMINIO_PADRAO

# Sufixos truncados conhecidos -> indicam que precisamos completar
SUFIXOS_TRUNCADOS = (
    "@tj", "@tjm", "@tjmg", "@tjmg.", "@tjmg.j", "@tjmg.ju",
    "@tjmg.jus", "@tjmg.jus.", "@tjmg.jus.b",
)

# Regexes
RE_EMAIL_FRAG = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]*")
RE_EMAIL_FULL = re.compile(r"^[a-zA-Z0-9._%+-]+@" + re.escape(DOMINIO_PADRAO) + r"$")
RE_TELEFONE = re.compile(r"\(?\s*\d{2}\s*\)?\s*\d{4,5}-\s*\d{4}")
RE_RAMAIS = re.compile(r"Ramais:\s*([0-9 /\n]+)")
RE_CEP = re.compile(r"CEP:\s*(\d{8})")
RE_FAX = re.compile(r"Fax:\s*\(?\s*(\d{2})\s*\)?\s*(\d{4,5}-\s*\d{4})")
RE_TEL_PRINC = re.compile(r"Telefones:\s*\(?\s*(\d{2})\s*\)?\s*(\d{4,5}-\s*\d{4})")
RE_FORUM = re.compile(r"^F[óo]rum\s+(.+?)$", re.M)
RE_CODIGO_NOME = re.compile(r"^(\d{4})\s+(.+?)\s*$", re.M)
RE_FERIADOS = re.compile(r"Feriados Municipais:\s*([0-9/\s]+)")
RE_ENDERECO_LINHA = re.compile(
    r"^(.+?),\s*(\d+|S/?\s*N°?|0\s*\(S/?N°\))\s*(?:\(.*?\))?\s+(.+?)\s*$",
    re.M,
)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def setup_logging() -> logging.Logger:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("extrator")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def clean(s: str | None) -> str:
    if s is None:
        return ""
    s = s.replace("\xa0", " ").replace("\u200b", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def slug_lower(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


def normalizar_telefone(raw: str) -> str:
    if not raw:
        return ""
    m = re.search(r"\(?\s*(\d{2})\s*\)?\s*(\d{4,5})-?\s*(\d{4})", raw)
    if not m:
        return clean(raw)
    return f"({m.group(1)}) {m.group(2)}-{m.group(3)}"


def email_completar(raw: str, sigla_fallback: str = "") -> tuple[str, bool]:
    """Recebe fragmento de email do PDF; retorna (email_final, foi_inferido)."""
    raw = clean(raw)
    if not raw:
        return "", False

    # Caso 1: email já completo e válido
    m = RE_EMAIL_FRAG.search(raw)
    if m:
        cand = m.group(0).rstrip(".")
        # já termina com domínio completo?
        if cand.lower().endswith(SUFIXO_COMPLETO):
            return cand.lower(), False
        # truncado conhecido?
        low = cand.lower()
        for sfx in SUFIXOS_TRUNCADOS:
            if low.endswith(sfx):
                prefixo = low[: low.index("@")]
                return f"{prefixo}{SUFIXO_COMPLETO}", True
        # outro domínio (ex.: gmail), aceitar como-é
        if "@" in cand and "." in cand.split("@", 1)[1]:
            return cand.lower(), False
        # tem @ mas sem ponto de domínio — completar
        if "@" in cand:
            prefixo = cand.split("@", 1)[0].lower()
            return f"{prefixo}{SUFIXO_COMPLETO}", True

    # Caso 2: sem @ no fragmento, mas string parece prefixo de email
    # (3-30 chars alfa-numéricos, sem espaço) -> tratar como sigla truncada
    candidato = raw.strip().lower()
    if (
        2 <= len(candidato) <= 40
        and re.fullmatch(r"[a-z0-9._-]+", candidato)
        and "fórum" not in candidato
    ):
        return f"{candidato}{SUFIXO_COMPLETO}", True

    # Caso 3: fallback usando sigla
    if sigla_fallback:
        s = slug_lower(sigla_fallback)
        if s:
            return f"{s}{SUFIXO_COMPLETO}", True

    return "", False


# ---------------------------------------------------------------------------
# Parsing de cabeçalho do fórum (PDFs de comarca)
# ---------------------------------------------------------------------------
def parse_cabecalho_forum(texto_pg0: str) -> dict[str, Any]:
    out: dict[str, Any] = {
        "codigo_tjmg": None,
        "forum_nome": None,
        "endereco": {},
        "telefone_principal": None,
        "fax_principal": None,
        "feriados_municipais": [],
    }
    # Codigo + nome localidade
    m = re.search(r"\n(\d{4})\s+([^\n]+?)\nEntrancia", texto_pg0)
    if m:
        out["codigo_tjmg"] = m.group(1)

    m = re.search(r"\n(F[óo]rum [^\n]+)", texto_pg0)
    if m:
        out["forum_nome"] = clean(m.group(1))

    m = RE_TEL_PRINC.search(texto_pg0)
    if m:
        out["telefone_principal"] = f"({m.group(1)}) {m.group(2).replace(' ', '')}"

    m = RE_FAX.search(texto_pg0)
    if m:
        out["fax_principal"] = f"({m.group(1)}) {m.group(2).replace(' ', '')}"

    m = RE_CEP.search(texto_pg0)
    if m:
        out["endereco"]["cep"] = m.group(1)

    # Endereço — linha logo após "Fórum ..." e antes de "Telefones:"
    m = re.search(
        r"\nGrupo Jurisdicional JESP:[^\n]+\n([^\n]+)\nTelefones:", texto_pg0
    )
    if m:
        linha = clean(m.group(1))
        # Ex.: "Praça do XX Aniversário, 0 (S/N°) Centro"
        em = re.match(
            r"^(.+?),\s*(\d+|0\s*\(S/?N°?\)|S/?\s*N°?)\s*\(?[^)]*\)?\s+(.+)$",
            linha,
        )
        if em:
            out["endereco"]["logradouro"] = clean(em.group(1))
            out["endereco"]["numero"] = clean(em.group(2))
            out["endereco"]["bairro"] = clean(em.group(3))
        else:
            out["endereco"]["logradouro"] = linha

    # Cidade/UF
    m = re.search(r"\n([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^\n]+?)\s*-\s*MG\nFax:", texto_pg0)
    if m:
        out["endereco"]["cidade"] = clean(m.group(1))
        out["endereco"]["uf"] = "MG"

    m = RE_FERIADOS.search(texto_pg0)
    if m:
        out["feriados_municipais"] = re.findall(r"\d{2}/\d{2}/\d{4}", m.group(1))

    return out


# ---------------------------------------------------------------------------
# Parsing de blocos de setor
# ---------------------------------------------------------------------------
PALAVRAS_VARA = (
    "Vara ", "Vara,", "Juizado", "Turma Recursal", "Tribunal do Júri",
    "Unidade Jurisdicional",
)
SECAO_INICIO_PADROES = (
    "Orgãos e Setores",
    "Resultado da Busca pelo(s) Juizado(s)",
    "Resultado da Busca pela(s) Vara(s)",
    "Resultado da Busca pelos Juízos",
)
SECAO_FIM_PADROES = (
    "Resultado da Busca pelos Municípios",
    "Resultado da Busca por Substituição",
    "Resultado da Busca por Serviços",
    "Serviços Notariais",
    "Distância entre as Comarcas",
)

# Cabeçalhos espúrios que ocasionalmente parecem ter "2-3 linhas + sigla"
NOMES_INVALIDOS_PREFIX = (
    "rua ", "avenida ", "praça ", "praca ", "estrada ", "rodovia ",
    "andar:", "sala", "ramais:", "comp.:", "fax:", "tel.", "telefone",
    "e-mail:", "tel ",
    "ir para",
    "municípios", "municipios", "distritos", "distância",
    "data de", "código", "codigo", "entrancia",
    "grupo jurisdicional",
)


def is_cabecalho_setor(linhas: list[str]) -> bool:
    """Heurística: bloco de 2-3 linhas curtas onde:
    - linha 0 = nome do setor (Letra maiúscula, sem ser endereço/label)
    - linha 1 = sigla curta (até 25 chars, sem espaços longos nem dois-pontos)
    - linha 2 (opcional) = email truncado/completo OU vazio
    """
    if len(linhas) < 2 or len(linhas) > 4:
        return False
    nome = clean(linhas[0])
    sigla = clean(linhas[1])
    email_raw = clean(linhas[2]) if len(linhas) >= 3 else ""

    if not nome or not sigla:
        return False

    nlow = nome.lower()
    if any(nlow.startswith(p) for p in NOMES_INVALIDOS_PREFIX):
        return False

    # nome típico: começa por letra maiúscula OU dígito ordinal (1ª, 2ª…)
    primeiro = nome[:1]
    if primeiro.isalpha():
        if not primeiro.isupper():
            return False
    elif primeiro.isdigit():
        # exigir ordinal feminino logo após (ª) — característico de "1ª Vara"
        if not re.match(r"^\d+ª\s", nome) and not re.match(r"^\d+\s", nome):
            return False
    else:
        return False

    # sigla: curta, sem ":" (não pode ser label tipo "Comp.:"), sem números de tel
    if len(sigla) > 28:
        return False
    if ":" in sigla:
        return False
    if RE_TELEFONE.search(sigla):
        return False
    # sigla não pode ser puramente numérica (são distâncias km)
    if sigla.isdigit():
        return False
    # sigla não pode ser "-"
    if sigla in ("-", "—"):
        return False

    # se tem 3ª linha, ela precisa parecer email OU prefixo email (sem espaço)
    if email_raw:
        if " " in email_raw:
            return False
        # ok: contém @ OU é alfanumérico curto (prefixo cortado)
        if "@" not in email_raw and not re.fullmatch(r"[a-zA-Z0-9._-]{2,40}", email_raw):
            return False

    # Cabeçalho do fórum (página 0) tem padrão "Fórum <Nome>" — só rejeitar
    # exatamente quando o nome inteiro começa com "Fórum " (e não "Administração do Fórum")
    if nome.startswith("Fórum ") or "Grupo Jurisdicional JESP" in nome:
        return False
    return True


def parse_setores_e_varas(doc: fitz.Document) -> tuple[list[dict], list[dict], int]:
    """Varre todas as páginas, identifica blocos de cabeçalho de setor.
    Retorna (setores, varas, total_inferidos)."""
    setores: list[dict] = []
    varas: list[dict] = []
    inferidos = 0

    em_secao = False
    pendente: dict | None = None  # último cabeçalho aguardando subdivisões

    for pg in doc:
        blocks = pg.get_text("blocks")
        # ordenar por y, depois x
        blocks = sorted(blocks, key=lambda b: (round(b[1], 1), round(b[0], 1)))
        for b in blocks:
            txt = b[4]
            if any(p in txt for p in SECAO_INICIO_PADROES):
                em_secao = True
                pendente = None
                continue
            if any(p in txt for p in SECAO_FIM_PADROES):
                em_secao = False
                pendente = None
                continue
            if not em_secao:
                continue

            linhas = [l for l in txt.split("\n") if l.strip()]

            if is_cabecalho_setor(linhas):
                nome = clean(linhas[0])
                # nomes de setor podem quebrar em 2 linhas se forem muito longos
                # neste PDF observamos casos como "Vara Criminal, da Infância e da\nJuventude"
                # mas isso aparece como 2 blocos distintos. Heurística simples:
                # se segunda linha NÃO parece sigla (tem espaços + minúsculas começando), pode ser continuação.
                sigla_idx = 1
                if (
                    len(linhas) >= 3
                    and " " in linhas[1].strip()
                    and linhas[1][:1].islower() is False
                    and len(linhas[1]) > 25
                ):
                    nome = nome + " " + clean(linhas[1])
                    sigla_idx = 2
                if sigla_idx >= len(linhas):
                    continue
                sigla = clean(linhas[sigla_idx])
                email_raw = (
                    clean(linhas[sigla_idx + 1])
                    if sigla_idx + 1 < len(linhas)
                    else ""
                )

                email, foi_inf = email_completar(email_raw, sigla_fallback=sigla)
                if foi_inf:
                    inferidos += 1

                registro = {
                    "nome": nome,
                    "sigla": sigla,
                    "email": email,
                    "email_raw": email_raw,
                    "email_completado_inferencia": foi_inf,
                    "andar": "",
                    "telefone": "",
                    "ramais": [],
                    "fax": "",
                }
                pendente = registro
                if any(p in nome for p in PALAVRAS_VARA):
                    varas.append(registro)
                else:
                    setores.append(registro)
                continue

            # Bloco de detalhe (sub-unidade) -> agrega ao pendente
            if pendente is not None:
                full = txt
                m = re.search(r"Andar:\s*([A-Z0-9ºª°][^\n]*)", full)
                if m and not pendente["andar"]:
                    val = clean(m.group(1))
                    if val and val.lower() not in ("sala", "sala:"):
                        pendente["andar"] = val
                m = re.search(r"Telefone:\s*([^\n]+)", full)
                if m and not pendente["telefone"]:
                    pendente["telefone"] = normalizar_telefone(m.group(1))
                m = re.search(r"Tel\. da Edificação:\s*([^\n]+)", full)
                if m and not pendente["telefone"]:
                    pendente["telefone"] = normalizar_telefone(m.group(1))
                m = RE_RAMAIS.search(full)
                if m:
                    ramais = [r.strip() for r in re.split(r"[/\s]+", m.group(1)) if r.strip().isdigit()]
                    if ramais and not pendente["ramais"]:
                        pendente["ramais"] = ramais
                m = re.search(r"\nFax:\s*([^\n]+)", full)
                if m:
                    f = clean(m.group(1))
                    if RE_TELEFONE.search(f):
                        pendente["fax"] = normalizar_telefone(f)

    return setores, varas, inferidos


# ---------------------------------------------------------------------------
# Parsing de PDF de município/distrito (sem fórum)
# ---------------------------------------------------------------------------
def parse_comarca_mae(doc: fitz.Document) -> str | None:
    txt = doc[0].get_text()
    m = re.search(r"\n([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\w\sÁ-ú]+)\(Comarca\)", txt)
    if m:
        return clean(m.group(1))
    return None


# ---------------------------------------------------------------------------
# Pipeline principal por PDF
# ---------------------------------------------------------------------------
def processar_pdf(
    pdf_path: Path, info_loc: dict, logger: logging.Logger
) -> dict[str, Any]:
    doc = fitz.open(pdf_path)
    try:
        nome = info_loc["nome"]
        tipo = info_loc["tipo"]
        registro: dict[str, Any] = {
            "codigo_tjmg": info_loc.get("codigo_tjmg"),
            "tipo": tipo,
            "arquivo_origem": pdf_path.name,
            "paginas_processadas": len(doc),
            "extracao_timestamp": datetime.now().isoformat(timespec="seconds"),
        }

        if tipo == "comarca":
            texto_pg0 = doc[0].get_text()
            cab = parse_cabecalho_forum(texto_pg0)
            registro.update(cab)
            # pre-popular endereço.cidade se faltar
            registro.setdefault("endereco", {})
            registro["endereco"].setdefault("cidade", nome)
            registro["endereco"].setdefault("uf", "MG")

            setores, varas, inferidos = parse_setores_e_varas(doc)
            registro["setores"] = setores
            registro["varas"] = varas
            registro["emails_inferidos_neste_pdf"] = inferidos

            # contagem de emails
            emails_validos = [
                s["email"] for s in (setores + varas) if s["email"]
            ]
            registro["total_emails"] = len(emails_validos)
        else:
            # município/distrito: registrar comarca-mãe
            registro["comarca_mae"] = info_loc.get("comarca_mae") or parse_comarca_mae(
                doc
            )
            registro["setores"] = []
            registro["varas"] = []
            registro["emails_inferidos_neste_pdf"] = 0
            registro["total_emails"] = 0

        return registro
    finally:
        doc.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Extrator completo TJMG")
    parser.add_argument("--limit", type=int, default=0, help="processar só N PDFs")
    parser.add_argument("--pdfs", type=str, default="", help="lista A.pdf,B.pdf")
    parser.add_argument("--resume", action="store_true", help="pula já processados")
    args = parser.parse_args()

    logger = setup_logging()
    logger.info("=" * 70)
    logger.info("INICIO extrator_completo")

    if not LOCALIDADES_JSON.exists():
        logger.error("localidades.json nao encontrado em %s", LOCALIDADES_JSON)
        return 2
    localidades = json.loads(LOCALIDADES_JSON.read_text(encoding="utf-8"))
    map_loc = {x["arquivo"]: x for x in localidades}

    pdfs_dir = sorted(PDF_DIR.glob("*.pdf"))
    logger.info("Encontrados %d PDFs em %s", len(pdfs_dir), PDF_DIR)

    if args.pdfs:
        subset = {p.strip() for p in args.pdfs.split(",") if p.strip()}
        pdfs_dir = [p for p in pdfs_dir if p.name in subset]
        logger.info("Filtro --pdfs ativo: %d PDFs", len(pdfs_dir))

    if args.limit and args.limit > 0:
        pdfs_dir = pdfs_dir[: args.limit]
        logger.info("Filtro --limit=%d ativo", args.limit)

    # Carrega resultado parcial se --resume
    saida: dict[str, dict] = {}
    if args.resume and OUT_JSON.exists():
        saida = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        logger.info("Resume ativo: %d entradas já presentes", len(saida))

    orfaos: list[dict] = []
    if ORFAOS_FILE.exists():
        try:
            orfaos = json.loads(ORFAOS_FILE.read_text(encoding="utf-8"))
        except Exception:
            orfaos = []

    total = len(pdfs_dir)
    erros = 0
    processados = 0
    inicio = time.time()

    for i, pdf in enumerate(pdfs_dir, start=1):
        info = map_loc.get(pdf.name)
        if info is None:
            logger.warning("PDF %s sem entrada em localidades.json — pulando", pdf.name)
            orfaos.append({"arquivo": pdf.name, "erro": "ausente em localidades.json"})
            continue

        nome_canonico = info["nome"]
        if args.resume and nome_canonico in saida:
            continue

        try:
            registro = processar_pdf(pdf, info, logger)
            saida[nome_canonico] = registro
            processados += 1
        except Exception as exc:  # ref: GL-002
            erros += 1
            logger.exception("Erro em %s: %s", pdf.name, exc)
            orfaos.append({"arquivo": pdf.name, "erro": f"{type(exc).__name__}: {exc}"})

        if i % 50 == 0 or i == total:
            logger.info(
                "[%d/%d] processados=%d, erros=%d", i, total, processados, erros
            )

    # Salvar
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    ORFAOS_FILE.write_text(
        json.dumps(orfaos, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Métricas
    comarcas = [v for v in saida.values() if v["tipo"] == "comarca"]
    com_email = sum(1 for c in comarcas if c.get("total_emails", 0) > 0)
    sem_email = len(comarcas) - com_email
    setores_total = sum(len(c.get("setores", [])) for c in comarcas)
    varas_total = sum(len(c.get("varas", [])) for c in comarcas)
    inferidos_total = sum(c.get("emails_inferidos_neste_pdf", 0) for c in comarcas)
    duracao = time.time() - inicio

    logger.info("-" * 70)
    logger.info("FIM. Duração: %.1fs", duracao)
    logger.info("Comarcas com email:   %d", com_email)
    logger.info("Comarcas sem email:   %d", sem_email)
    logger.info("Setores extraídos:    %d", setores_total)
    logger.info("Varas extraídas:      %d", varas_total)
    logger.info("Emails completados por inferência: %d", inferidos_total)
    logger.info("Arquivo: %s", OUT_JSON)
    logger.info("Órfãos:  %s (%d)", ORFAOS_FILE, len(orfaos))

    return 0


if __name__ == "__main__":
    sys.exit(main())
