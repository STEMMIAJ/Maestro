#!/usr/bin/env python3
"""
faltam_baixar.py — Cruza PDF de pericias (125) com PDFs ja baixados no Windows/Parallels
                   e gera lista do que falta baixar.

USO:
    python3 faltam_baixar.py

ENTRADAS (fixas):
    ~/Desktop/LISTA PERICIAS CERTA.pdf          (fonte de verdade: AJ + AJG)
    ~/Desktop/processos-pje/*.pdf               (baixados via Windows/Parallels)
    ~/Desktop/ANALISADOR FINAL/processos/**/*.pdf (baixados em sessoes anteriores)

SAIDAS:
    ~/Desktop/FALTA-BAIXAR-YYYYMMDD.md                            (relatorio legivel)
    ~/Desktop/Projetos - Plan Mode/processos-pje/processos_hoje.txt  (60 CNJs top prioridade)
    ~/Desktop/Projetos - Plan Mode/processos-pje/processos_amanha.txt (resto)

PRIORIDADE:
    1. TAIOBEIRAS
    2. GOVERNADOR VALADARES
    3. MANTENA
    4. Resto (por data de nomeacao crescente)

Exclui: RECUSADA, CANCELADA PELO JUIZ (nao precisam de PDF).
"""
import re, json, subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime

HOME = Path.home()
PDF_FONTE = HOME / 'Desktop/LISTA PERICIAS CERTA.pdf'
DIR_WINDOWS = HOME / 'Desktop/processos-pje'
DIR_ANALISADOR = HOME / 'Desktop/ANALISADOR FINAL/processos'
DIR_OUT_LISTAS = HOME / 'Desktop/Projetos - Plan Mode/processos-pje'
MESA = HOME / 'Desktop'

CNJ_RE = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')
LIMITE_DIARIO = 60

def extrair_pdf_fonte():
    """Extrai os 125 CNJs do PDF de pericias com metadados."""
    txt = subprocess.check_output(['pdftotext', str(PDF_FONTE), '-']).decode()
    linhas = [l.strip() for l in txt.split('\n')]
    registros = []
    i = 0
    while i < len(linhas):
        m = CNJ_RE.fullmatch(linhas[i])
        if m:
            cnj = linhas[i]
            bloco = []
            j = i + 1
            while j < len(linhas) and not CNJ_RE.fullmatch(linhas[j]) and len(bloco) < 10:
                if linhas[j]:
                    bloco.append(linhas[j])
                j += 1
            unidade = bloco[0] if len(bloco) > 0 else ''
            data_nom = next((b for b in bloco if re.match(r'\d{2}/\d{2}/\d{4}', b)), '')
            situacao = ''
            fonte = ''
            for b in bloco:
                if b in ('ACEITA', 'RECUSADA', 'CANCELADA PELO JUIZ', 'PERDA DE PRAZO',
                         'SERVICO PRESTADO', 'SERVIÇO PRESTADO', 'CANCELADA'):
                    situacao = b
                if b in ('AJ', 'AJG'):
                    fonte = b
            # heuristica: se tiver situacao com sufixo " (2 pericias?)"
            for b in bloco:
                if b.startswith('ACEITA') and b != 'ACEITA':
                    situacao = b
            registros.append({
                'cnj': cnj, 'unidade': unidade, 'data_nom': data_nom,
                'situacao': situacao, 'fonte': fonte
            })
            i = j
        else:
            i += 1
    return registros

def cnjs_baixados():
    """Retorna set de CNJs com PDF ja baixado (Windows + Analisador)."""
    baixados = set()
    for d in (DIR_WINDOWS, DIR_ANALISADOR):
        if not d.exists():
            continue
        for p in d.rglob('*.pdf'):
            m = CNJ_RE.search(p.name)
            if m:
                baixados.add(m.group())
    return baixados

def cidade(unidade):
    if not unidade:
        return 'SEM CIDADE'
    return unidade.split(' - ')[0].strip().upper()

def prioridade(c):
    if 'TAIOBEIRAS' in c: return 1
    if 'VALADARES' in c: return 2
    if 'MANTENA' in c: return 3
    return 4

def data_key(d):
    try:
        return datetime.strptime(d, '%d/%m/%Y')
    except Exception:
        return datetime.max

def main():
    pdf = extrair_pdf_fonte()
    baixados = cnjs_baixados()

    faltam = [p for p in pdf if p['cnj'] not in baixados]
    ja = [p for p in pdf if p['cnj'] in baixados]
    precisam = [p for p in faltam if p['situacao'] not in ('RECUSADA', 'CANCELADA PELO JUIZ', 'CANCELADA')]
    nao_precisam = [p for p in faltam if p not in precisam]

    # ordem prioritaria
    precisam.sort(key=lambda p: (prioridade(cidade(p['unidade'])), data_key(p['data_nom']), p['cnj']))

    cnjs_hoje = [p['cnj'] for p in precisam[:LIMITE_DIARIO]]
    cnjs_amanha = [p['cnj'] for p in precisam[LIMITE_DIARIO:]]

    DIR_OUT_LISTAS.mkdir(parents=True, exist_ok=True)
    (DIR_OUT_LISTAS / 'processos_hoje.txt').write_text('\n'.join(cnjs_hoje) + '\n')
    (DIR_OUT_LISTAS / 'processos_amanha.txt').write_text('\n'.join(cnjs_amanha) + ('\n' if cnjs_amanha else ''))

    # relatorio
    today = datetime.now().strftime('%d%m%Y')
    md = []
    md.append(f"# FALTA BAIXAR — {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    md.append(f"**PDF (AJ+AJG)**: {len(pdf)} | **Já baixados**: {len(ja)} | **Faltam**: {len(faltam)} | **Precisam baixar**: {len(precisam)}")
    md.append(f"(+{len(nao_precisam)} RECUSADA/CANCELADA — ignorar)\n")
    md.append("---\n## POR CIDADE (faltam)\n")
    md.append("| Cidade | Faltam | Baixados | Total |")
    md.append("|--------|--------|----------|-------|")
    por_c_falta = defaultdict(list)
    for p in precisam: por_c_falta[cidade(p['unidade'])].append(p)
    por_c_ja = defaultdict(list)
    for p in ja: por_c_ja[cidade(p['unidade'])].append(p)
    todas = set(por_c_falta) | set(por_c_ja)
    for c in sorted(todas, key=lambda x: (prioridade(x), -len(por_c_falta.get(x, [])))):
        f = len(por_c_falta.get(c, []))
        b = len(por_c_ja.get(c, []))
        md.append(f"| {c} | **{f}** | {b} | {f+b} |")
    md.append(f"| **TOTAL** | **{len(precisam)}** | **{len(ja)}** | **{len(precisam)+len(ja)}** |\n")

    md.append("---\n## DETALHE — FALTAM BAIXAR\n")
    for c in sorted(por_c_falta, key=lambda x: (prioridade(x), -len(por_c_falta[x]))):
        lst = por_c_falta[c]
        md.append(f"\n### {c} ({len(lst)})\n")
        md.append("| # | CNJ | Vara | Data Nom. | Situação | AJ/AJG |")
        md.append("|---|-----|------|-----------|----------|--------|")
        for i, p in enumerate(sorted(lst, key=lambda x: data_key(x['data_nom'])), 1):
            vara = p['unidade'].split(' - ', 1)[1] if ' - ' in (p['unidade'] or '') else ''
            md.append(f"| {i} | `{p['cnj']}` | {vara} | {p['data_nom']} | {p['situacao']} | {p['fonte']} |")

    md.append("\n---\n## JÁ BAIXADOS (não repetir)\n")
    for c in sorted(por_c_ja, key=lambda x: -len(por_c_ja[x])):
        lst = por_c_ja[c]
        md.append(f"\n### {c} ({len(lst)})")
        for p in lst:
            md.append(f"- `{p['cnj']}` — {p['situacao']}")

    out_md = MESA / f'FALTA-BAIXAR-{today}.md'
    out_md.write_text('\n'.join(md))

    print(f"✓ Relatório: {out_md}")
    print(f"✓ Hoje: {len(cnjs_hoje)} CNJs → {DIR_OUT_LISTAS/'processos_hoje.txt'}")
    print(f"✓ Amanhã: {len(cnjs_amanha)} CNJs → {DIR_OUT_LISTAS/'processos_amanha.txt'}")
    print(f"\nPDF: {len(pdf)} | Baixados: {len(ja)} | Faltam baixar: {len(precisam)}")

if __name__ == '__main__':
    main()
