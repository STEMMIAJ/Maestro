#!/usr/bin/env python3
"""
localizar_nomeacao.py — Localiza a nomeação pericial em processo judicial.
Busca do FINAL para o INÍCIO e extrai dados estruturados do formulário AJ/TJMG.

Uso:
    python3 localizar_nomeacao.py [CNJ]
    python3 localizar_nomeacao.py --arquivo /caminho/TEXTO-EXTRAIDO.txt
"""
import sys, re, subprocess
from pathlib import Path
from typing import Optional, Dict, List, Tuple

BASE = Path.home() / "Desktop" / "ANALISADOR FINAL" / "processos"

PADROES_AJ = [
    re.compile(r"NOMEA[CÇ][AÃ]O DE PROFISSIONAL", re.I),
    re.compile(r"Nomea[cç][aã]o n\.?:\s*\d+", re.I),
    re.compile(r"Data da nomea[cç][aã]o:", re.I),
    re.compile(r"profissional aqui identificado foi nomeado", re.I),
]
PADROES_DECISAO = [
    re.compile(r"nomeio\b.*perit[oa]", re.I),
    re.compile(r"Defiro a produ[cç][aã]o de prova pericial", re.I),
    re.compile(r"Proceda.se.*nomea[cç][aã]o.*Sistema AJ", re.I),
    re.compile(r"determino.*nomea[cç][aã]o de perit", re.I),
    re.compile(r"J[EÉ]SUS EDUARDO.*perit", re.I),
]
RE_ACEITE = re.compile(r"(?:prazo de|em)\s*(\d+)\s*\(?.*?\)?\s*dias.*?(?:aceite|aceita|encargo|manifestar)", re.I)
RE_LAUDO = re.compile(r"laudo.*?prazo de\s*(\d+)\s*\(?.*?\)?\s*dias", re.I)
ROTULOS_MAP = [
    ("e-mail juiz requisitante", None), ("juiz requisitante", "juiz_requisitante"),
    ("unidade", "unidade"), ("endere", None),
    ("data da nomeacao", "data_nomeacao"), ("data da nomeação", "data_nomeacao"),
    ("valor requisitado", "valor_requisitado"),
    ("observacao", "observacao"), ("observação", "observacao"),
    ("tipo de processo judicial", "tipo_custeio"),
    ("tipo de atua", None), ("assistido", None), ("n. do processo", None),
    ("assunto", None), ("classe", None), ("tipo de natureza", None), ("advogado", None),
]
CABECALHOS = {"dados processuais", "dados do profissional",
              "beneficiário dos honorários", "beneficiario dos honorarios"}


def encontrar_pasta(cnj: str) -> Optional[Path]:
    d = BASE / cnj
    if d.is_dir(): return d
    for p in sorted(BASE.iterdir()):
        if p.is_dir() and cnj in p.name: return p
    return None


def carregar(caminho: Path) -> List[str]:
    if caminho.suffix.lower() == ".pdf":
        r = subprocess.run(["pdftotext", "-layout", str(caminho), "-"], capture_output=True, text=True)
        if r.returncode != 0: print(f"ERRO: pdftotext falhou: {r.stderr}"); sys.exit(1)
        return r.stdout.splitlines()
    return caminho.read_text(encoding="utf-8", errors="replace").splitlines()


def buscar_nomeacao(linhas: List[str]) -> Tuple[Optional[int], str]:
    total = len(linhas)
    # 1) Formulário AJ (do fim pro início)
    for i in range(total - 1, -1, -1):
        for p in PADROES_AJ:
            if p.search(linhas[i]):
                # Recuar até cabeçalho "Auxiliares da Justiça - AJ"
                for j in range(i, max(i - 120, -1), -1):
                    if re.search(r"Auxiliares da Justi[cç]a\s*-\s*AJ", linhas[j], re.I):
                        return j, "formulario_aj"
                return i, "formulario_aj"
    # 2) Decisão do juiz (do fim pro início)
    for i in range(total - 1, -1, -1):
        for p in PADROES_DECISAO:
            if p.search(linhas[i]): return i, "decisao_juiz"
    return None, ""


def extrair_dados(linhas: List[str], inicio: int) -> Dict[str, str]:
    fim = min(inicio + 120, len(linhas))
    dados = {}  # type: Dict[str, str]
    # Número AJ
    for i in range(inicio, fim):
        if re.search(r"Nomea[cç][aã]o n\.?:", linhas[i], re.I):
            m = re.search(r"Nomea[cç][aã]o n\.?:\s*(\d+)", linhas[i], re.I)
            if m: dados["numero_aj"] = m.group(1)
            else:
                for j in range(i + 1, min(i + 4, fim)):
                    m2 = re.search(r"(\d{10,})", linhas[j])
                    if m2: dados["numero_aj"] = m2.group(1); break
            break
    # Blocos tabulares AJ (rótulos agrupados + valores agrupados)
    i = inicio
    while i < fim:
        rot_seq, j = [], i
        while j < fim:
            s = linhas[j].strip()
            if s.endswith(":") and len(s) > 2:
                rl = s[:-1].strip().lower()
                if rl not in CABECALHOS: rot_seq.append(rl)
                j += 1
            elif not s and rot_seq: j += 1; break
            elif rot_seq: break
            else: j += 1; break
        if len(rot_seq) >= 2:
            vals, k = [], j
            while k < fim:
                s = linhas[k].strip()
                if not s:
                    if vals: break
                    k += 1; continue
                if s.endswith(":") and len(s) > 2:
                    nxt = linhas[k + 1].strip() if k + 1 < fim else ""
                    if nxt.endswith(":"): break
                vals.append(s); k += 1
            n = len(rot_seq)
            for idx, rotulo in enumerate(rot_seq):
                if idx >= len(vals): break
                for chave_b, chave_d in ROTULOS_MAP:
                    if chave_b in rotulo:
                        if chave_d is None: break
                        dados[chave_d] = " ".join(vals[idx:]) if idx == n - 1 else vals[idx]
                        break
        i = j
    # Limpeza: data
    if "data_nomeacao" in dados:
        m = re.search(r"\d{2}/\d{2}/\d{4}", dados["data_nomeacao"])
        dados["data_nomeacao"] = m.group(0) if m else ""
    if not dados.get("data_nomeacao"):
        for i in range(inicio, fim):
            if re.search(r"Data da nomea[cç][aã]o:", linhas[i], re.I):
                for j in range(i, min(i + 15, fim)):
                    m = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", linhas[j])
                    if m: dados["data_nomeacao"] = m.group(1); break
                break
    if not dados.get("data_nomeacao"): dados.pop("data_nomeacao", None)
    # Limpeza: valor
    if "valor_requisitado" in dados:
        m = re.search(r"[\d.,]+", dados["valor_requisitado"])
        dados["valor_requisitado"] = m.group(0) if m else ""
    if not dados.get("valor_requisitado"):
        for i in range(inicio, fim):
            if re.search(r"Valor requisitado:", linhas[i], re.I):
                for j in range(i, min(i + 5, fim)):
                    m = re.search(r"([\d]+[.,][\d]{2})", linhas[j])
                    if m: dados["valor_requisitado"] = m.group(1); break
                break
    if not dados.get("valor_requisitado"): dados.pop("valor_requisitado", None)
    # Prazos (bloco amplo — pode estar na decisão antes do AJ)
    bloco = "\n".join(linhas[max(0, inicio - 80):fim])
    m = RE_ACEITE.search(bloco)
    if m: dados["prazo_aceite"] = m.group(1) + " dias"
    m = RE_LAUDO.search(bloco)
    if m: dados["prazo_laudo"] = m.group(1) + " dias"
    return dados


def salvar(pasta: Path, linhas: List[str], inicio: int, tipo: str, dados: Dict[str, str]):
    total = len(linhas)
    trecho = linhas[max(0, inicio - 20):min(total, inicio + 21)]
    ROTULOS = [("numero_aj", "Nomeação AJ n.º"), ("data_nomeacao", "Data da nomeação"),
               ("valor_requisitado", "Valor requisitado (R$)"), ("tipo_custeio", "Tipo de custeio"),
               ("juiz_requisitante", "Juiz requisitante"), ("unidade", "Unidade/Vara"),
               ("observacao", "Observação"), ("prazo_aceite", "Prazo para aceite"),
               ("prazo_laudo", "Prazo para laudo")]
    md = [f"# Nomeação Pericial\n", f"**Tipo de detecção:** {tipo}",
          f"**Linha no texto:** {inicio + 1} de {total}\n"]
    if dados:
        md.append("## Dados Extraídos\n")
        for k, r in ROTULOS:
            if k in dados: md.append(f"- **{r}:** {dados[k]}")
        md.append("")
    md.append("## Trecho da Nomeação\n"); md.append("```")
    md.extend(trecho); md.append("```\n")
    (pasta / "NOMEACAO.md").write_text("\n".join(md), encoding="utf-8")
    (pasta / "TEXTO-POS-NOMEACAO.txt").write_text("\n".join(linhas[inicio:]), encoding="utf-8")


def resumo(inicio: int, total: int, tipo: str, dados: Dict[str, str], pasta: Path):
    print(f"\n{'='*60}\n  NOMEAÇÃO LOCALIZADA\n{'='*60}")
    print(f"  Tipo:   {tipo}")
    print(f"  Linha:  {inicio + 1} de {total} ({100*(inicio+1)//total}% do documento)")
    campos = [("numero_aj", "AJ n.º"), ("data_nomeacao", "Data"), ("valor_requisitado", "Valor", "R$ "),
              ("tipo_custeio", "Custeio"), ("juiz_requisitante", "Juiz"), ("unidade", "Vara"),
              ("prazo_aceite", "Prazo aceite"), ("prazo_laudo", "Prazo laudo")]
    if dados:
        print(f"\n  --- Dados extraídos ---")
        for item in campos:
            k, label = item[0], item[1]
            prefix = item[2] if len(item) > 2 else ""
            if k in dados: print(f"  {label:15s}{prefix}{dados[k]}")
        if "observacao" in dados: print(f"  {'Obs':15s}{dados['observacao'][:80]}")
    print(f"\n  Salvos em: {pasta}\n    - NOMEACAO.md\n    - TEXTO-POS-NOMEACAO.txt\n{'='*60}\n")


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 localizar_nomeacao.py [CNJ]")
        print("     python3 localizar_nomeacao.py --arquivo /caminho/TEXTO-EXTRAIDO.txt"); sys.exit(1)
    if sys.argv[1] == "--arquivo":
        if len(sys.argv) < 3: print("ERRO: informe o caminho."); sys.exit(1)
        arquivo, pasta = Path(sys.argv[2]), Path(sys.argv[2]).parent
    else:
        cnj = sys.argv[1]
        pasta = encontrar_pasta(cnj)
        if not pasta: print(f"ERRO: processo {cnj} não encontrado em {BASE}"); sys.exit(1)
        arquivo = pasta / "TEXTO-EXTRAIDO.txt"
        if not arquivo.exists():
            pdfs = list(pasta.glob("*.pdf"))
            if pdfs: arquivo = pdfs[0]; print(f"Usando PDF: {arquivo.name}")
            else: print(f"ERRO: nenhum TEXTO-EXTRAIDO.txt ou PDF em {pasta}"); sys.exit(1)
    if not arquivo.exists(): print(f"ERRO: arquivo não encontrado: {arquivo}"); sys.exit(1)

    linhas = carregar(arquivo)
    total = len(linhas)
    print(f"Arquivo: {arquivo.name} ({total} linhas)")
    inicio, tipo = buscar_nomeacao(linhas)

    if inicio is None:
        print("\nNOMEAÇÃO NÃO ENCONTRADA. Salvando texto completo para análise manual.")
        (pasta / "TEXTO-POS-NOMEACAO.txt").write_text("\n".join(linhas), encoding="utf-8")
        (pasta / "NOMEACAO.md").write_text(
            "# Nomeação Pericial\n\n**NOMEAÇÃO NÃO LOCALIZADA AUTOMATICAMENTE.**\n\n"
            "Revisar manualmente o texto do processo.\n", encoding="utf-8")
        sys.exit(0)

    dados = extrair_dados(linhas, inicio)
    salvar(pasta, linhas, inicio, tipo, dados)
    resumo(inicio, total, tipo, dados, pasta)


if __name__ == "__main__":
    main()
