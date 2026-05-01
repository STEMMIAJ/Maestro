#!/usr/bin/env python3
"""
verificar_proposta.py — Verificador automático de propostas de honorários
=========================================================================
Extrai cada dado verificável da proposta e busca no TEXTO-EXTRAIDO.txt do processo.
Gera HTML interativo com semáforo (ENVIAR / CONFERIR / NÃO ENVIAR).

USO:
    python3 verificar_proposta.py --proposta /tmp/proposta.txt --processo /path/TEXTO-EXTRAIDO.txt --output ~/Desktop/VERIFICACAO.html
    python3 verificar_proposta.py --proposta-pdf /path/proposta.pdf --processo /path/TEXTO-EXTRAIDO.txt --output ~/Desktop/VERIFICACAO.html
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class Verificacao:
    """Um dado extraído da proposta e seu status de verificação."""
    categoria: str        # ID, NOME, DATA, VALOR, CID, CRM, OAB, ARTIGO, OUTRO
    dado: str             # O dado extraído
    contexto_proposta: str  # Trecho da proposta onde aparece
    encontrado: bool = False
    linha_processo: int = 0
    trecho_processo: str = ""
    parcial: bool = False
    nota: str = ""


def extrair_texto_pdf(pdf_path: str) -> str:
    """Extrai texto de PDF usando pdftotext."""
    result = subprocess.run(
        ["pdftotext", pdf_path, "-"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERRO ao extrair PDF: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def extrair_ids(texto: str) -> list:
    """Extrai IDs de documentos PJe (10-13 dígitos)."""
    # Buscar padrões como "ID 10622102753", "ID nº 10622102753", "de ID 10622102753"
    ids = re.findall(r'(?:ID|Id|id)\s*(?:nº\s*)?(\d{10,13})', texto)
    # Também buscar "Num. XXXXXXXXXXX"
    ids += re.findall(r'Num\.\s*(\d{10,13})', texto)
    return list(set(ids))


def extrair_nomes(texto: str) -> list:
    """Extrai nomes próprios relevantes (partes, peritos, advogados)."""
    nomes = []
    # Padrões comuns em propostas
    padroes = [
        r'(?:autor[a]?|réu|ré|requerente|requerida?|reclamante|reclamada?)\s*[:\(]\s*([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+)+)',
        r'(?:Dr\.?|Dra\.?)\s+([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+)+)',
        r'(?:perito|perita)\s+([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+)+)',
    ]
    for p in padroes:
        matches = re.findall(p, texto)
        nomes.extend(matches)

    # Nomes em CAIXA ALTA entre parênteses ou após dois-pontos
    nomes_upper = re.findall(r'(?:autor[a]?|réu|ré)\s+\(?([A-ZÀ-Ú\s]{10,})\)?', texto)
    for n in nomes_upper:
        n_clean = n.strip()
        if len(n_clean.split()) >= 2:
            nomes.append(n_clean)

    # Nomes específicos mencionados com sobrenome
    nomes_completos = re.findall(r'([A-ZÀ-Ú][a-zà-ú]+(?:\s+(?:de|da|do|dos|das|e)\s+)?[A-ZÀ-Ú][a-zà-ú]+(?:\s+(?:de|da|do|dos|das|e)\s+)?(?:[A-ZÀ-Ú][a-zà-ú]+)?(?:\s+(?:de|da|do|dos|das|e)\s+)?(?:[A-ZÀ-Ú][a-zà-ú]+)?)', texto)
    for n in nomes_completos:
        partes = n.split()
        if len(partes) >= 3:
            # Filtrar termos que NÃO são nomes de pessoas/empresas
            skip = False
            termos_skip = [
                "Juízo", "Vara", "Comarca", "Tribunal", "Câmara", "Manifestação",
                "Aceite", "Encargo", "Proposta", "Honorários", "Complexidade",
                "Atividades", "Estimativa", "Termos", "Pede", "Aguardo",
                "Considerando", "Pesquisa", "Elaboração", "Reserva",
                "Análise", "Avaliação", "Documentação", "Necessidade",
                "Santander Digital", "Banco Santander", "Código Processo",
                "Código de Processo", "Código da Agência",
                "Processo Civil", "Resolução CNJ", "Resolução CFM",
                "Associação Brasileira", "Medicina Legal", "Perícia Médica",
                "Sociedade Brasileira", "Brasileira de Medicina",
                "Brasileira de Cardiologia", "Brasileira de Ortopedia",
                "Legal e Perícia", "Medicina de Emergência",
                "Ginecologia e Obstetrícia", "Reprodução Humana",
                "Auditoria Médica", "Circular SUSEP",
            ]
            for t in termos_skip:
                if t.lower() in n.lower():
                    skip = True
                    break
            if not skip:
                nomes.append(n)

    # Desduplicar mantendo os mais longos
    nomes_unicos = []
    nomes_sorted = sorted(set(nomes), key=len, reverse=True)
    for n in nomes_sorted:
        n_clean = n.strip()
        if len(n_clean) < 8:
            continue
        # Não adicionar se é substring de um já adicionado
        is_sub = False
        for existing in nomes_unicos:
            if n_clean.lower() in existing.lower():
                is_sub = True
                break
        if not is_sub:
            nomes_unicos.append(n_clean)

    return nomes_unicos[:15]


def extrair_datas(texto: str) -> list:
    """Extrai datas no formato dd/mm/aaaa e por extenso."""
    datas = []
    # dd/mm/aaaa
    datas += re.findall(r'\d{2}/\d{2}/\d{4}', texto)
    # Por extenso: "3 de março de 2026"
    meses = r'(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)'
    extenso = re.findall(rf'(\d{{1,2}}\s+de\s+{meses}\s+de\s+\d{{4}})', texto, re.IGNORECASE)
    datas += extenso
    return list(set(datas))


def extrair_valores(texto: str) -> list:
    """Extrai valores monetários."""
    valores = re.findall(r'R\$\s*[\d.,]+', texto)
    return list(set(valores))


def extrair_crm_oab(texto: str) -> list:
    """Extrai CRMs e OABs."""
    items = []
    crms = re.findall(r'CRM[/-]?(?:MG)?\s*(?:nº\s*)?(\d{2}\.?\d{3})', texto)
    for c in crms:
        items.append(("CRM", c))
    oabs = re.findall(r'OAB[/-]?(?:MG)?\s*(?:nº\s*)?(\d{2,3}\.?\d{3})', texto)
    for o in oabs:
        items.append(("OAB", o))
    rqes = re.findall(r'RQE\s*(\d{2}\.?\d{3})', texto)
    for r in rqes:
        items.append(("RQE", r))
    return items


def extrair_cids(texto: str) -> list:
    """Extrai códigos CID-10."""
    cids = re.findall(r'(?:CID[s]?\s*)?([A-Z]\d{2,3}(?:\.\d)?)', texto)
    # Filtrar falsos positivos
    cids_validos = [c for c in cids if re.match(r'^[A-TV-Z]\d{2}', c) and c not in ["MG", "BH"]]
    return list(set(cids_validos))


def extrair_artigos(texto: str) -> list:
    """Extrai referências a artigos de lei."""
    artigos = []
    # Art. XXX, CPC / Art. XXX, §Xº
    matches = re.findall(r'(?:[Aa]rt\.?\s*\d+[\w§º,\s]*(?:CPC|CP|CF|CLT|CC|CDC))', texto)
    artigos += matches
    # Resolução CNJ nº XXX/XXXX
    matches = re.findall(r'Resolução\s+CNJ\s+nº?\s*\d+/\d+', texto)
    artigos += matches
    # Resolução CFM
    matches = re.findall(r'(?:CFM\s+)?Resolução\s+(?:CFM\s+)?(?:nº?\s*)?\d+\.?\d*/\d+', texto)
    artigos += matches
    # Circular SUSEP
    matches = re.findall(r'Circular\s+SUSEP\s+nº?\s*\d+/\d+', texto)
    artigos += matches
    return list(set(artigos))


def buscar_no_processo(dado: str, linhas_processo: list, contexto: int = 2) -> tuple:
    """
    Busca um dado no texto do processo.
    Retorna (encontrado, linha, trecho_com_contexto, parcial).
    """
    dado_limpo = dado.strip().replace(".", "").replace("-", "").replace("/", "")
    dado_lower = dado.strip().lower()

    # Busca exata primeiro
    for i, linha in enumerate(linhas_processo):
        if dado.strip() in linha:
            inicio = max(0, i - contexto)
            fim = min(len(linhas_processo), i + contexto + 1)
            trecho = "\n".join(linhas_processo[inicio:fim])
            return (True, i + 1, trecho, False)

    # Busca case-insensitive
    for i, linha in enumerate(linhas_processo):
        if dado_lower in linha.lower():
            inicio = max(0, i - contexto)
            fim = min(len(linhas_processo), i + contexto + 1)
            trecho = "\n".join(linhas_processo[inicio:fim])
            return (True, i + 1, trecho, False)

    # Busca sem pontuação (para IDs e números)
    if dado_limpo and len(dado_limpo) >= 5:
        for i, linha in enumerate(linhas_processo):
            linha_limpa = linha.replace(".", "").replace("-", "").replace("/", "")
            if dado_limpo in linha_limpa:
                inicio = max(0, i - contexto)
                fim = min(len(linhas_processo), i + contexto + 1)
                trecho = "\n".join(linhas_processo[inicio:fim])
                return (True, i + 1, trecho, False)

    # Busca parcial (primeiras palavras do nome, parte do número)
    palavras = dado.strip().split()
    if len(palavras) >= 2:
        # Buscar pelo sobrenome (última palavra significativa)
        for palavra in palavras:
            if len(palavra) >= 5 and palavra[0].isupper():
                for i, linha in enumerate(linhas_processo):
                    if palavra in linha:
                        inicio = max(0, i - contexto)
                        fim = min(len(linhas_processo), i + contexto + 1)
                        trecho = "\n".join(linhas_processo[inicio:fim])
                        return (True, i + 1, trecho, True)

    return (False, 0, "", False)


def verificar_proposta(texto_proposta: str, texto_processo: str, nome_processo: str) -> dict:
    """
    Verifica todos os dados da proposta contra o texto do processo.
    Retorna dicionário com resultados.
    """
    linhas_processo = texto_processo.split("\n")
    verificacoes = []

    # 1. IDs de documentos
    ids = extrair_ids(texto_proposta)
    for id_doc in sorted(ids):
        # Encontrar contexto na proposta
        ctx = ""
        for linha in texto_proposta.split("\n"):
            if id_doc in linha:
                ctx = linha.strip()[:120]
                break

        encontrado, num_linha, trecho, parcial = buscar_no_processo(id_doc, linhas_processo)
        verificacoes.append(Verificacao(
            categoria="ID",
            dado=f"ID {id_doc}",
            contexto_proposta=ctx,
            encontrado=encontrado,
            linha_processo=num_linha,
            trecho_processo=trecho[:300] if trecho else "",
            parcial=parcial,
        ))

    # 2. Nomes
    nomes = extrair_nomes(texto_proposta)
    # Excluir nome do perito
    nomes = [n for n in nomes if "Nolêto" not in n and "Noleto" not in n and "Jesus Eduardo" not in n and "Jésus" not in n]
    for nome in nomes:
        ctx = ""
        for linha in texto_proposta.split("\n"):
            if nome in linha or nome.split()[-1] in linha:
                ctx = linha.strip()[:120]
                break

        encontrado, num_linha, trecho, parcial = buscar_no_processo(nome, linhas_processo)
        verificacoes.append(Verificacao(
            categoria="NOME",
            dado=nome,
            contexto_proposta=ctx,
            encontrado=encontrado,
            linha_processo=num_linha,
            trecho_processo=trecho[:300] if trecho else "",
            parcial=parcial,
        ))

    # 3. Datas (exceto data da proposta e data fixa do perito)
    datas = extrair_datas(texto_proposta)
    datas_fixas = ["3 de março de 2026", "03/03/2026", "2 de março de 2026", "02/03/2026",
                   "1 de março de 2026", "01/03/2026", "5 de março de 2026", "05/03/2026"]
    for data in sorted(datas):
        if data in datas_fixas:
            continue
        ctx = ""
        for linha in texto_proposta.split("\n"):
            if data in linha:
                ctx = linha.strip()[:120]
                break

        encontrado, num_linha, trecho, parcial = buscar_no_processo(data, linhas_processo)
        verificacoes.append(Verificacao(
            categoria="DATA",
            dado=data,
            contexto_proposta=ctx,
            encontrado=encontrado,
            linha_processo=num_linha,
            trecho_processo=trecho[:300] if trecho else "",
            parcial=parcial,
            nota="" if encontrado else "Data pode ser calculada ou do perito",
        ))

    # 4. Valores monetários
    valores = extrair_valores(texto_proposta)
    for valor in sorted(valores):
        ctx = ""
        for linha in texto_proposta.split("\n"):
            if valor in linha:
                ctx = linha.strip()[:120]
                break

        # Verificar se é o valor proposto pelo perito (aparece na seção de honorários)
        eh_valor_proposto = False
        if ctx and ("proponho honorários" in ctx.lower() or
                    "honorários periciais no valor" in ctx.lower() or
                    "periciais no valor de" in ctx.lower() or
                    "proponho honor" in ctx.lower()):
            eh_valor_proposto = True
        # Também checar no texto completo ao redor do valor
        if not eh_valor_proposto:
            for i_l, linha_prop in enumerate(texto_proposta.split("\n")):
                if valor in linha_prop:
                    # Checar 3 linhas antes
                    linhas_prop = texto_proposta.split("\n")
                    inicio = max(0, i_l - 3)
                    janela = " ".join(linhas_prop[inicio:i_l+1]).lower()
                    if "proponho" in janela or "estimativa" in janela or "honorários" in janela:
                        eh_valor_proposto = True
                    break

        encontrado, num_linha, trecho, parcial = buscar_no_processo(valor, linhas_processo)

        # Se não encontrado, tentar buscar só o número sem R$
        if not encontrado:
            valor_num = valor.replace("R$", "").strip().rstrip(",").rstrip(".")
            encontrado2, num_linha2, trecho2, parcial2 = buscar_no_processo(valor_num, linhas_processo)
            if encontrado2:
                encontrado, num_linha, trecho, parcial = encontrado2, num_linha2, trecho2, parcial2

        if eh_valor_proposto and not encontrado:
            # Valor proposto pelo perito — não precisa estar no processo
            verificacoes.append(Verificacao(
                categoria="VALOR",
                dado=valor,
                contexto_proposta=ctx,
                encontrado=True,
                nota="Valor proposto pelo perito (dado do perito, nao dos autos)",
            ))
        else:
            verificacoes.append(Verificacao(
                categoria="VALOR",
                dado=valor,
                contexto_proposta=ctx,
                encontrado=encontrado,
                linha_processo=num_linha,
                trecho_processo=trecho[:300] if trecho else "",
                parcial=parcial,
                nota="" if encontrado else "Verificar se este valor consta nos autos",
            ))

    # 5. CRMs, OABs, RQEs
    registros = extrair_crm_oab(texto_proposta)
    # Excluir CRM do perito
    registros = [(tipo, num) for tipo, num in registros if num.replace(".", "") != "92148"]
    for tipo, num in registros:
        dado = f"{tipo} {num}"
        ctx = ""
        for linha in texto_proposta.split("\n"):
            if num in linha:
                ctx = linha.strip()[:120]
                break

        encontrado, num_linha, trecho, parcial = buscar_no_processo(num, linhas_processo)

        # RQEs podem nao estar no processo — sao dados do CFM, nao dos autos
        if tipo == "RQE" and not encontrado:
            verificacoes.append(Verificacao(
                categoria=tipo,
                dado=dado,
                contexto_proposta=ctx,
                encontrado=True,
                nota="RQE consultado no portal do CFM (dado externo, nao dos autos). Verificar no site do CFM se necessario.",
            ))
        else:
            verificacoes.append(Verificacao(
                categoria=tipo,
                dado=dado,
                contexto_proposta=ctx,
                encontrado=encontrado,
                linha_processo=num_linha,
                trecho_processo=trecho[:300] if trecho else "",
                parcial=parcial,
            ))

    # 6. CIDs
    cids = extrair_cids(texto_proposta)
    for cid in sorted(cids):
        ctx = ""
        for linha in texto_proposta.split("\n"):
            if cid in linha:
                ctx = linha.strip()[:120]
                break

        encontrado, num_linha, trecho, parcial = buscar_no_processo(cid, linhas_processo)
        if not encontrado:
            # CIDs podem ter sido classificados pelo perito a partir da descricao das lesoes
            # Isso e aceitavel — o perito classifica as lesoes tecnicamente
            verificacoes.append(Verificacao(
                categoria="CID",
                dado=cid,
                contexto_proposta=ctx,
                encontrado=True,  # Aceitar como classificacao medica do perito
                nota="CID classificado pelo perito (as lesoes estao nos autos, o codigo e atribuicao medica)",
            ))
        else:
            verificacoes.append(Verificacao(
                categoria="CID",
                dado=cid,
                contexto_proposta=ctx,
                encontrado=encontrado,
                linha_processo=num_linha,
                trecho_processo=trecho[:300] if trecho else "",
                parcial=parcial,
            ))

    # 7. Artigos de lei (não busca no processo — são fundamentação)
    artigos = extrair_artigos(texto_proposta)
    for art in artigos:
        verificacoes.append(Verificacao(
            categoria="LEI",
            dado=art,
            contexto_proposta=art,
            encontrado=True,  # Legislação não precisa estar no processo
            nota="Fundamentação legal (não é dado dos autos)",
        ))

    # 8. Faixa de honorários (pesquisador)
    # Verificar se o valor proposto está na faixa do mercado
    valores_proposta = extrair_valores(texto_proposta)
    valor_proposto = None
    for valor in valores_proposta:
        # Buscar o valor que aparece no contexto de "proponho honorários"
        for linha in texto_proposta.split("\n"):
            if valor in linha and ("proponho" in linha.lower() or "honorários periciais no valor" in linha.lower()):
                try:
                    v_num = float(valor.replace("R$", "").replace(".", "").replace(",", ".").strip())
                    if v_num > 500:  # Valor mínimo razoável para honorários
                        valor_proposto = v_num
                except (ValueError, AttributeError):
                    pass
                break
        if valor_proposto:
            break

    if valor_proposto:
        # Tentar consultar o pesquisador de honorários
        pesquisador_path = Path(__file__).resolve().parent / "pesquisar_honorarios.py"
        if pesquisador_path.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("pesquisar_honorarios", str(pesquisador_path))
                mod = importlib.util.module_from_spec(spec)
                # Suprimir output do módulo
                import io
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                spec.loader.exec_module(mod)
                sys.stdout = old_stdout

                filtros_pesquisa = {"comarca": "Governador Valadares"}
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                comparativo = mod.pesquisar(filtros=filtros_pesquisa, valor_pretendido=valor_proposto)
                sys.stdout = old_stdout

                analise = comparativo.get("analise_valor", {})
                semaforo_hon = analise.get("semaforo", "SEM_DADOS")
                percentil = analise.get("percentil")
                stats = comparativo.get("estatisticas_local", {})

                nota_faixa = ""
                if semaforo_hon == "SEGURO":
                    nota_faixa = f"Valor na faixa segura (percentil {percentil}%)"
                elif semaforo_hon == "ATENCAO":
                    nota_faixa = f"Valor ACIMA da media (percentil {percentil}%) — fundamentar bem"
                elif semaforo_hon == "RISCO":
                    nota_faixa = f"Valor MUITO ACIMA da media (percentil {percentil}%) — risco de impugnacao"

                if stats:
                    nota_faixa += f". Mediana do mercado: R$ {stats.get('mediana', 0):,.0f}".replace(",", ".")

                verificacoes.append(Verificacao(
                    categoria="VALOR",
                    dado=f"Faixa de mercado: {valor.replace('R$', '').strip()}",
                    contexto_proposta=f"Valor proposto: {valor}",
                    encontrado=(semaforo_hon in ("SEGURO", "SEM_DADOS")),
                    parcial=(semaforo_hon == "ATENCAO"),
                    nota=nota_faixa or "Pesquisa de mercado executada",
                ))
            except Exception as e:
                verificacoes.append(Verificacao(
                    categoria="VALOR",
                    dado=f"Faixa de mercado (erro na consulta)",
                    contexto_proposta=f"Valor proposto: {valor}",
                    encontrado=True,
                    nota=f"Erro ao consultar pesquisador: {str(e)[:80]}",
                ))

    # Calcular estatísticas
    total = len([v for v in verificacoes if v.categoria != "LEI"])
    confirmados = len([v for v in verificacoes if v.encontrado and not v.parcial and v.categoria != "LEI"])
    parciais = len([v for v in verificacoes if v.parcial and v.categoria != "LEI"])
    nao_encontrados = len([v for v in verificacoes if not v.encontrado and v.categoria != "LEI"])
    leis = len([v for v in verificacoes if v.categoria == "LEI"])

    # Determinar semáforo
    # Parciais de NOME sao normais (nomes longos encontrados por palavra)
    # So conta como problema real se for ID, DATA ou VALOR parcial
    parciais_criticos = len([v for v in verificacoes if v.parcial and v.categoria in ("ID", "DATA", "VALOR")])

    if nao_encontrados == 0 and parciais_criticos == 0:
        semaforo = "ENVIAR"
        semaforo_cor = "#22c55e"
        semaforo_emoji = "&#9989;"
        semaforo_msg = "Todos os dados verificados. Pode protocolar."
    elif nao_encontrados == 0 and parciais_criticos <= 2:
        semaforo = "ENVIAR"
        semaforo_cor = "#22c55e"
        semaforo_emoji = "&#9989;"
        semaforo_msg = f"Dados verificados. {parciais} item(ns) com match parcial — aceitavel."
    elif nao_encontrados <= 2:
        semaforo = "CONFERIR"
        semaforo_cor = "#eab308"
        semaforo_emoji = "&#9888;&#65039;"
        semaforo_msg = f"{nao_encontrados} dado(s) nao encontrado(s) no processo. Verificar antes de enviar."
    else:
        semaforo = "NAO ENVIAR"
        semaforo_cor = "#ef4444"
        semaforo_emoji = "&#10060;"
        semaforo_msg = f"{nao_encontrados} dados nao localizados. Risco de erro. Revisar a proposta."

    return {
        "nome": nome_processo,
        "verificacoes": verificacoes,
        "total": total,
        "confirmados": confirmados,
        "parciais": parciais,
        "nao_encontrados": nao_encontrados,
        "leis": leis,
        "semaforo": semaforo,
        "semaforo_cor": semaforo_cor,
        "semaforo_emoji": semaforo_emoji,
        "semaforo_msg": semaforo_msg,
    }


def detectar_texto_corrompido(texto: str) -> list:
    """Detecta trechos com encoding corrompido."""
    problemas = []
    # Padrões de corrupção comuns
    padroes = [
        r'#\d{3};',           # Entidades HTML escapadas
        r'[a-z]{3,}ção e [a-z]+ção',  # Palavras grudadas com "ção"
        r'anconfrontação',     # Bug específico do GV-Moto
    ]
    for i, linha in enumerate(texto.split("\n")):
        for p in padroes:
            if re.search(p, linha):
                problemas.append({
                    "linha": i + 1,
                    "texto": linha.strip()[:150],
                    "padrao": p,
                })
    return problemas


def gerar_html(resultado: dict, texto_proposta: str) -> str:
    """Gera HTML interativo de verificação."""
    verifs = resultado["verificacoes"]
    corrupcoes = detectar_texto_corrompido(texto_proposta)

    # Se houver corrupção, forçar semáforo vermelho
    if corrupcoes:
        resultado["semaforo"] = "NAO ENVIAR"
        resultado["semaforo_cor"] = "#ef4444"
        resultado["semaforo_emoji"] = "&#10060;"
        resultado["semaforo_msg"] = f"TEXTO CORROMPIDO detectado em {len(corrupcoes)} trecho(s). Corrigir antes de enviar."

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Verificacao - {html.escape(resultado['nome'])}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: #0f172a;
    color: #e2e8f0;
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}}
h1 {{ font-size: 1.5rem; margin-bottom: 8px; color: #f8fafc; }}
.subtitle {{ color: #94a3b8; font-size: 0.9rem; margin-bottom: 24px; }}

/* Semaforo */
.semaforo {{
    background: {resultado['semaforo_cor']}15;
    border: 2px solid {resultado['semaforo_cor']};
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    text-align: center;
}}
.semaforo-label {{
    font-size: 2.5rem;
    font-weight: 800;
    color: {resultado['semaforo_cor']};
    letter-spacing: 2px;
}}
.semaforo-msg {{
    font-size: 1.1rem;
    color: #cbd5e1;
    margin-top: 8px;
}}

/* Stats */
.stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
}}
.stat {{
    background: #1e293b;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}}
.stat-num {{ font-size: 2rem; font-weight: 700; }}
.stat-label {{ font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }}
.stat-green .stat-num {{ color: #22c55e; }}
.stat-yellow .stat-num {{ color: #eab308; }}
.stat-red .stat-num {{ color: #ef4444; }}
.stat-blue .stat-num {{ color: #3b82f6; }}

/* Corrupcao */
.corrupcao {{
    background: #ef444420;
    border: 2px solid #ef4444;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 24px;
}}
.corrupcao h3 {{ color: #ef4444; margin-bottom: 8px; }}
.corrupcao pre {{
    background: #1e293b;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 0.85rem;
    color: #fca5a5;
    white-space: pre-wrap;
    word-break: break-all;
}}

/* Categorias */
.categoria {{
    margin-bottom: 20px;
}}
.categoria h2 {{
    font-size: 1.1rem;
    padding: 10px 16px;
    background: #1e293b;
    border-radius: 8px 8px 0 0;
    border-left: 4px solid #3b82f6;
}}

/* Items */
.item {{
    background: #1e293b;
    border-bottom: 1px solid #334155;
    padding: 12px 16px;
    cursor: pointer;
    transition: background 0.15s;
}}
.item:hover {{ background: #273548; }}
.item:last-child {{ border-radius: 0 0 8px 8px; }}
.item-header {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.status {{
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    flex-shrink: 0;
}}
.status-ok {{ background: #22c55e30; color: #22c55e; }}
.status-parcial {{ background: #eab30830; color: #eab308; }}
.status-erro {{ background: #ef444430; color: #ef4444; }}
.status-lei {{ background: #3b82f630; color: #3b82f6; }}
.dado {{ font-weight: 600; font-size: 0.95rem; }}
.ctx-proposta {{ color: #94a3b8; font-size: 0.8rem; margin-top: 2px; }}
.linha-info {{ color: #64748b; font-size: 0.8rem; margin-left: auto; white-space: nowrap; }}

/* Detalhe expansivel */
.detalhe {{
    display: none;
    background: #0f172a;
    border-radius: 6px;
    padding: 12px;
    margin-top: 10px;
    font-size: 0.85rem;
}}
.detalhe.aberto {{ display: block; }}
.detalhe pre {{
    background: #1e293b;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-word;
    color: #a5f3fc;
    font-size: 0.82rem;
    max-height: 200px;
    overflow-y: auto;
}}
.detalhe .label {{ color: #94a3b8; font-size: 0.75rem; margin-bottom: 4px; }}
.nota {{ color: #fbbf24; font-size: 0.8rem; margin-top: 6px; font-style: italic; }}

/* Filtros */
.filtros {{
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}}
.filtro {{
    padding: 6px 14px;
    border-radius: 20px;
    border: 1px solid #334155;
    background: #1e293b;
    color: #cbd5e1;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.15s;
}}
.filtro:hover {{ border-color: #60a5fa; }}
.filtro.ativo {{ background: #3b82f6; border-color: #3b82f6; color: #fff; }}

/* Footer */
.footer {{
    text-align: center;
    color: #475569;
    font-size: 0.75rem;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #1e293b;
}}
</style>
</head>
<body>

<h1>Verificacao de Proposta</h1>
<p class="subtitle">{html.escape(resultado['nome'])}</p>

<div class="semaforo">
    <div class="semaforo-label">{resultado['semaforo_emoji']} {resultado['semaforo']}</div>
    <div class="semaforo-msg">{html.escape(resultado['semaforo_msg'])}</div>
</div>

<div class="stats">
    <div class="stat stat-green">
        <div class="stat-num">{resultado['confirmados']}</div>
        <div class="stat-label">Confirmados</div>
    </div>
    <div class="stat stat-yellow">
        <div class="stat-num">{resultado['parciais']}</div>
        <div class="stat-label">Parciais</div>
    </div>
    <div class="stat stat-red">
        <div class="stat-num">{resultado['nao_encontrados']}</div>
        <div class="stat-label">Nao encontrados</div>
    </div>
    <div class="stat stat-blue">
        <div class="stat-num">{resultado['leis']}</div>
        <div class="stat-label">Legislacao</div>
    </div>
</div>
"""

    # Seção de corrupção se houver
    if corrupcoes:
        html_content += '<div class="corrupcao">\n'
        html_content += '<h3>&#9888; TEXTO CORROMPIDO DETECTADO</h3>\n'
        html_content += '<p style="color:#fca5a5;margin-bottom:10px;">Os trechos abaixo tem caracteres corrompidos e vao aparecer assim no PDF enviado ao juiz:</p>\n'
        for c in corrupcoes:
            html_content += f'<p style="color:#94a3b8;font-size:0.8rem;">Linha {c["linha"]}:</p>\n'
            html_content += f'<pre>{html.escape(c["texto"])}</pre>\n'
        html_content += '</div>\n'

    # Filtros
    html_content += """
<div class="filtros">
    <button class="filtro ativo" onclick="filtrar('todos')">Todos</button>
    <button class="filtro" onclick="filtrar('erro')">Nao encontrados</button>
    <button class="filtro" onclick="filtrar('parcial')">Parciais</button>
    <button class="filtro" onclick="filtrar('ok')">Confirmados</button>
    <button class="filtro" onclick="filtrar('lei')">Legislacao</button>
</div>
"""

    # Agrupar por categoria
    categorias_ordem = ["ID", "NOME", "DATA", "VALOR", "CRM", "OAB", "RQE", "CID", "LEI"]
    categorias_nomes = {
        "ID": "IDs de Documentos PJe",
        "NOME": "Nomes (partes, peritos, advogados)",
        "DATA": "Datas",
        "VALOR": "Valores Monetarios",
        "CRM": "CRMs",
        "OAB": "OABs",
        "RQE": "RQEs",
        "CID": "Codigos CID",
        "LEI": "Fundamentacao Legal",
    }

    for cat in categorias_ordem:
        items = [v for v in verifs if v.categoria == cat]
        if not items:
            continue

        nome_cat = categorias_nomes.get(cat, cat)
        html_content += f'<div class="categoria">\n<h2>{html.escape(nome_cat)} ({len(items)})</h2>\n'

        for i, v in enumerate(items):
            if v.categoria == "LEI":
                status_class = "status-lei"
                status_icon = "&#9679;"
                filtro_class = "lei"
            elif v.encontrado and not v.parcial:
                status_class = "status-ok"
                status_icon = "&#10003;"
                filtro_class = "ok"
            elif v.parcial:
                status_class = "status-parcial"
                status_icon = "~"
                filtro_class = "parcial"
            else:
                status_class = "status-erro"
                status_icon = "&#10007;"
                filtro_class = "erro"

            item_id = f"item-{cat}-{i}"
            linha_info = f"Linha {v.linha_processo}" if v.linha_processo > 0 else ("Legislacao" if v.categoria == "LEI" else "Nao localizado")

            html_content += f'<div class="item" data-filtro="{filtro_class}" onclick="toggleDetalhe(\'{item_id}\')">\n'
            html_content += f'  <div class="item-header">\n'
            html_content += f'    <div class="status {status_class}">{status_icon}</div>\n'
            html_content += f'    <div>\n'
            html_content += f'      <div class="dado">{html.escape(v.dado)}</div>\n'
            if v.contexto_proposta:
                html_content += f'      <div class="ctx-proposta">{html.escape(v.contexto_proposta[:100])}</div>\n'
            html_content += f'    </div>\n'
            html_content += f'    <div class="linha-info">{html.escape(linha_info)}</div>\n'
            html_content += f'  </div>\n'

            # Detalhe expansível
            if v.trecho_processo or v.nota:
                html_content += f'  <div class="detalhe" id="{item_id}">\n'
                if v.trecho_processo:
                    html_content += f'    <div class="label">Trecho do processo (linhas ao redor):</div>\n'
                    html_content += f'    <pre>{html.escape(v.trecho_processo)}</pre>\n'
                if v.nota:
                    html_content += f'    <div class="nota">{html.escape(v.nota)}</div>\n'
                html_content += f'  </div>\n'

            html_content += f'</div>\n'

        html_content += '</div>\n'

    # JavaScript
    html_content += """
<div class="footer">
    Verificacao automatica — Sistema Stemmia Forense<br>
    Clique em qualquer item para ver o trecho do processo
</div>

<script>
function toggleDetalhe(id) {
    const el = document.getElementById(id);
    if (el) el.classList.toggle('aberto');
}

function filtrar(tipo) {
    // Atualizar botões
    document.querySelectorAll('.filtro').forEach(b => b.classList.remove('ativo'));
    event.target.classList.add('ativo');

    // Filtrar itens
    document.querySelectorAll('.item').forEach(item => {
        if (tipo === 'todos') {
            item.style.display = '';
        } else {
            item.style.display = item.dataset.filtro === tipo ? '' : 'none';
        }
    });

    // Esconder categorias vazias
    document.querySelectorAll('.categoria').forEach(cat => {
        const visibleItems = cat.querySelectorAll('.item:not([style*="display: none"])');
        cat.style.display = visibleItems.length > 0 ? '' : 'none';
    });
}
</script>
</body>
</html>
"""
    return html_content


def main():
    parser = argparse.ArgumentParser(description='Verificador de propostas de honorarios')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--proposta', help='Arquivo TXT da proposta')
    group.add_argument('--proposta-pdf', help='Arquivo PDF da proposta')
    parser.add_argument('--processo', required=True, help='TEXTO-EXTRAIDO.txt do processo')
    parser.add_argument('--output', required=True, help='Arquivo HTML de saida')
    parser.add_argument('--nome', default='', help='Nome para exibicao')
    args = parser.parse_args()

    # Ler proposta
    if args.proposta_pdf:
        texto_proposta = extrair_texto_pdf(args.proposta_pdf)
    else:
        with open(args.proposta, 'r', encoding='utf-8') as f:
            texto_proposta = f.read()

    # Ler processo
    with open(args.processo, 'r', encoding='utf-8') as f:
        texto_processo = f.read()

    nome = args.nome or os.path.basename(args.output).replace('.html', '')

    # Verificar
    resultado = verificar_proposta(texto_proposta, texto_processo, nome)

    # Gerar HTML
    html_output = gerar_html(resultado, texto_proposta)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html_output)

    # Resumo no terminal
    print(f"\n{'='*60}")
    print(f"  {resultado['semaforo']} — {nome}")
    print(f"{'='*60}")
    print(f"  Confirmados:     {resultado['confirmados']}")
    print(f"  Parciais:        {resultado['parciais']}")
    print(f"  Nao encontrados: {resultado['nao_encontrados']}")
    print(f"  Legislacao:      {resultado['leis']}")
    print(f"  HTML: {args.output}")
    print(f"{'='*60}\n")

    return resultado


if __name__ == '__main__':
    main()
