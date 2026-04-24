#!/usr/bin/env python3
"""
Sincronizar AJ + PJe — Orquestrador.

Lê nomeações do AJ TJMG → busca e baixa PDFs do PJe → tudo com 1 comando.

Uso:
  python3 sincronizar_aj_pje.py                     # Lista + baixa novos
  python3 sincronizar_aj_pje.py --so-listar          # Só lista nomeações do AJ
  python3 sincronizar_aj_pje.py --so-baixar CNJ1 CNJ2  # Baixa processos específicos
  python3 sincronizar_aj_pje.py --novos-apenas       # Pula processos que já têm PDF
  python3 sincronizar_aj_pje.py --json               # Saída JSON

Pré-requisitos:
  1. Chrome AJ rodando no Mac com --remote-debugging-port=9223 (logado no AJ)
  2. Chrome PJe rodando no Mac com --remote-debugging-port=9224 (logado no PJe com CPF/senha)
     OU no Windows/Parallels com --remote-debugging-port=9222 (logado com token)

IMPORTANTE: Este script NUNCA clica em Aceitar ou Rejeitar nomeações.
"""

import argparse
import asyncio
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).parent
PROCESSOS_DIR = BASE_DIR / "processos"
BAIXAR_PJE = Path.home() / "Desktop" / "Projetos - Plan Mode" / "processos-pje" / "baixar_pje.py"
CONSULTAR_AJ = BASE_DIR / "consultar_aj.py"
CONSULTAR_AJG = BASE_DIR / "consultar_ajg.py"
PENDENTES_JSON = BASE_DIR / "_pendentes_download.json"
DOWNLOADS_TEMP = BASE_DIR / "_downloads_temp"

# ============================================================
# CORES
# ============================================================

class C:
    R = "\033[0m"
    B = "\033[1m"
    G = "\033[32m"
    Y = "\033[33m"
    RE = "\033[31m"
    CY = "\033[36m"
    DIM = "\033[2m"


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ", "OK": "✓", "ERRO": "✗", "AVISO": "⚠"}.get(level, "·")
    print(f"  [{ts}] {prefix} {msg}", file=sys.stderr)


# ============================================================
# IMPORTAÇÃO DINÂMICA
# ============================================================

def importar_modulo(caminho, nome):
    """Importa módulo Python de caminho absoluto via importlib."""
    if not caminho.exists():
        log(f"Módulo não encontrado: {caminho}", "ERRO")
        sys.exit(1)
    sys.path.insert(0, str(caminho.parent))
    spec = importlib.util.spec_from_file_location(nome, str(caminho))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================================================
# VERIFICAÇÃO DE PDFS EXISTENTES
# ============================================================

def processo_tem_pdf(cnj):
    """Verifica se um processo já tem PDF baixado."""
    # Procura na pasta processos/ (symlinks CNJ → pasta nomeada)
    pasta_cnj = PROCESSOS_DIR / cnj
    if pasta_cnj.exists():
        for nome in ["autos-completos.pdf", "PROCESSO-ORIGINAL.pdf"]:
            if (pasta_cnj / nome).exists():
                return True

    # Procura na raiz (pastas antigas sem gestor)
    pasta_raiz = BASE_DIR / cnj
    if pasta_raiz.exists():
        for nome in ["autos-completos.pdf", "PROCESSO-ORIGINAL.pdf"]:
            if (pasta_raiz / nome).exists():
                return True

    return False


def salvar_pendentes(cnjs):
    """Salva lista de CNJs pendentes para o script Windows pegar."""
    PENDENTES_JSON.write_text(
        json.dumps(cnjs, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    log(f"Pendentes salvos em _pendentes_download.json ({len(cnjs)} processos)", "OK")


def limpar_pendentes():
    """Limpa o arquivo de pendentes após download."""
    PENDENTES_JSON.write_text("[]", encoding="utf-8")


def importar_downloads_temp():
    """Importa PDFs baixados pelo Windows de _downloads_temp para processos/."""
    if not DOWNLOADS_TEMP.exists():
        return []

    importados = []
    for subpasta in DOWNLOADS_TEMP.iterdir():
        if not subpasta.is_dir():
            continue
        pdf = subpasta / "autos-completos.pdf"
        if not pdf.exists():
            continue

        # Identificar CNJ pelo nome da subpasta
        cnj = subpasta.name.replace("_", "-")
        # Validar formato CNJ
        if not re.match(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', cnj):
            # Tentar o nome literal
            cnj = subpasta.name

        pasta = obter_pasta_processo(cnj)
        pdf_destino = pasta / "autos-completos.pdf"

        # Backup se já existir
        if pdf_destino.exists():
            data = datetime.now().strftime("%Y-%m-%d")
            backup = pasta / f"autos-completos-{data}.pdf"
            shutil.move(str(pdf_destino), str(backup))

        shutil.move(str(pdf), str(pdf_destino))
        log(f"Importado: {cnj} → {pasta.name}/", "OK")

        # Extrair texto
        txt = pasta / "TEXTO-EXTRAIDO.txt"
        try:
            subprocess.run(
                ["pdftotext", "-layout", str(pdf_destino), str(txt)],
                capture_output=True, timeout=120
            )
            if txt.exists() and txt.stat().st_size > 0:
                log(f"  Texto extraído ({txt.stat().st_size / 1024:.0f}KB)", "OK")
        except Exception:
            log("  Falha ao extrair texto (pdftotext)", "AVISO")

        importados.append({"cnj": cnj, "pasta": str(pasta), "tamanho_mb": round(pdf_destino.stat().st_size / (1024 * 1024), 1)})

        # Limpar subpasta temporária
        shutil.rmtree(subpasta, ignore_errors=True)

    # Limpar pasta temp se vazia
    if DOWNLOADS_TEMP.exists() and not any(DOWNLOADS_TEMP.iterdir()):
        DOWNLOADS_TEMP.rmdir()

    return importados


def obter_pasta_processo(cnj):
    """Retorna o Path da pasta do processo. Cria se não existir."""
    # Primeiro tenta processos/ (gestor)
    pasta_cnj = PROCESSOS_DIR / cnj
    if pasta_cnj.exists():
        # Resolve symlink se for
        return pasta_cnj.resolve()

    # Tenta raiz
    pasta_raiz = BASE_DIR / cnj
    if pasta_raiz.exists():
        return pasta_raiz

    # Cria em processos/ se existir, senão na raiz
    if PROCESSOS_DIR.exists():
        pasta_nova = PROCESSOS_DIR / cnj
        pasta_nova.mkdir(parents=True, exist_ok=True)
        return pasta_nova
    else:
        pasta_nova = BASE_DIR / cnj
        pasta_nova.mkdir(parents=True, exist_ok=True)
        return pasta_nova


def criar_ou_atualizar_ficha(pasta, cnj, dados_nomeacao=None):
    """Cria ou atualiza FICHA.json com dados da nomeação."""
    ficha_path = pasta / "FICHA.json"

    if ficha_path.exists():
        try:
            ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            ficha = {}
    else:
        ficha = {}

    ficha["numero_cnj"] = cnj
    ficha["atualizado_em"] = datetime.now().isoformat()

    if dados_nomeacao:
        ficha["nomeacao"] = {
            "numero": dados_nomeacao.get("numero_nomeacao", ""),
            "unidade": dados_nomeacao.get("unidade", ""),
            "data": dados_nomeacao.get("data_nomeacao", ""),
            "situacao": dados_nomeacao.get("situacao", ""),
            "valor_honorario": dados_nomeacao.get("valor_honorario", ""),
            "dias_aceite": dados_nomeacao.get("dias_aceite", ""),
        }

    ficha_path.write_text(
        json.dumps(ficha, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return ficha


# ============================================================
# ETAPA 1: LISTAR NOMEAÇÕES DO AJ
# ============================================================

async def etapa_listar_aj(porta_aj=9223):
    """Conecta ao AJ e lista todas as nomeações."""
    log(f"Conectando ao Chrome AJ (porta {porta_aj})...")

    mod_aj = importar_modulo(CONSULTAR_AJ, "consultar_aj")

    pw, browser, page = await mod_aj.conectar_aj(porta=porta_aj)

    try:
        await mod_aj.navegar_consulta(page)
        nomeacoes = await mod_aj.listar_nomeacoes(page, situacao="TODAS")

        # Ordenar por data (mais recentes primeiro)
        def parse_data(n):
            data_str = n.get("data_nomeacao", "")
            try:
                return datetime.strptime(data_str, "%d/%m/%Y")
            except (ValueError, TypeError):
                return datetime.min

        nomeacoes.sort(key=parse_data, reverse=True)

        log(f"Total de nomeações: {len(nomeacoes)}", "OK")
        return nomeacoes

    finally:
        await pw.stop()


# ============================================================
# ETAPA 1B: LISTAR NOMEAÇÕES DO AJG
# ============================================================

async def etapa_listar_ajg(porta_ajg=9223):
    """Conecta ao AJG Federal e lista nomeações pendentes."""
    log(f"Conectando ao Chrome AJG (porta {porta_ajg})...")

    mod_ajg = importar_modulo(CONSULTAR_AJG, "consultar_ajg")

    pw, browser, page = await mod_ajg.conectar_ajg(porta=porta_ajg)

    try:
        await mod_ajg.navegar_consulta(page)
        nomeacoes = await mod_ajg.listar_nomeacoes(page, situacao="AGUARDANDO ACEITE")

        for n in nomeacoes:
            n["_origem"] = "AJG"

        log(f"Total de nomeações AJG: {len(nomeacoes)}", "OK")
        return nomeacoes

    finally:
        await pw.stop()


# ============================================================
# ETAPA 2: BAIXAR DO PJe
# ============================================================

async def etapa_baixar_pje(cnjs, ip_pje="10.211.55.3", porta_pje=9222):
    """Conecta ao PJe e baixa os processos."""
    if not cnjs:
        log("Nenhum processo para baixar.", "INFO")
        return []

    log(f"Conectando ao Chrome PJe ({ip_pje}:{porta_pje})...")

    mod_pje = importar_modulo(BAIXAR_PJE, "baixar_pje")

    from playwright.async_api import async_playwright

    resultados = []
    temp_download = BASE_DIR / "_downloads_temp"
    temp_download.mkdir(exist_ok=True)

    async with async_playwright() as p:
        try:
            cdp_url = f"http://{ip_pje}:{porta_pje}"
            browser = await p.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            log(f"Não consegui conectar ao Chrome PJe: {e}", "ERRO")
            print(file=sys.stderr)
            print("Verifique:", file=sys.stderr)
            print(f"  1. Chrome rodando no Windows com --remote-debugging-port={porta_pje}", file=sys.stderr)
            print(f"  2. IP correto: {ip_pje}", file=sys.stderr)
            print("  3. Token digital logado no PJe", file=sys.stderr)
            return resultados

        log("Conectado ao Chrome PJe!", "OK")

        contexts = browser.contexts
        if not contexts:
            log("Nenhum contexto no Chrome PJe", "ERRO")
            return resultados

        context = contexts[0]
        pages = context.pages
        page = pages[0] if pages else await context.new_page()

        for i, cnj in enumerate(cnjs, 1):
            print(f"\n  [{i}/{len(cnjs)}] {C.B}{cnj}{C.R}", file=sys.stderr)

            pasta = obter_pasta_processo(cnj)

            ok = await mod_pje.baixar_processo(page, cnj, temp_download)

            resultado = {"cnj": cnj, "sucesso": False, "pasta": str(pasta)}

            if ok:
                pdf_temp = temp_download / mod_pje.sanitize(cnj) / "autos-completos.pdf"
                if pdf_temp.exists():
                    # Backup de PDF existente
                    pdf_destino = pasta / "autos-completos.pdf"
                    if pdf_destino.exists():
                        data = datetime.now().strftime("%Y-%m-%d")
                        backup = pasta / f"autos-completos-{data}.pdf"
                        shutil.move(str(pdf_destino), str(backup))
                        log(f"Backup: {backup.name}", "INFO")

                    shutil.move(str(pdf_temp), str(pdf_destino))
                    log(f"PDF salvo em {pasta.name}/", "OK")

                    # Extrair texto
                    txt = pasta / "TEXTO-EXTRAIDO.txt"
                    try:
                        subprocess.run(
                            ["pdftotext", "-layout", str(pdf_destino), str(txt)],
                            capture_output=True, timeout=120
                        )
                        if txt.exists() and txt.stat().st_size > 0:
                            log(f"Texto extraído ({txt.stat().st_size / 1024:.0f}KB)", "OK")
                    except Exception:
                        log("Falha ao extrair texto (pdftotext)", "AVISO")

                    resultado["sucesso"] = True
                    resultado["pdf"] = str(pdf_destino)
                    resultado["tamanho_mb"] = round(pdf_destino.stat().st_size / (1024 * 1024), 1)
                else:
                    log("baixar_processo retornou OK mas PDF não encontrado", "AVISO")
            else:
                log(f"Falha ao baixar {cnj}", "ERRO")

            resultados.append(resultado)

            # Pausa entre processos
            if i < len(cnjs):
                await page.wait_for_timeout(2000)

    # Limpar temp
    shutil.rmtree(temp_download, ignore_errors=True)

    return resultados


# ============================================================
# ORQUESTRADOR PRINCIPAL
# ============================================================

async def sincronizar(args):
    """Fluxo principal: AJ → PJe."""

    # MODO IMPORTAR: traz PDFs do _downloads_temp
    if args.importar:
        print(f"\n{C.B}  IMPORTANDO PDFs de _downloads_temp{C.R}", file=sys.stderr)
        print(f"{'─' * 50}", file=sys.stderr)
        importados = importar_downloads_temp()
        if importados:
            for imp in importados:
                log(f"  {imp['cnj']} ({imp['tamanho_mb']}MB)")
            log(f"Total importados: {len(importados)}", "OK")
            limpar_pendentes()
        else:
            log("Nenhum PDF encontrado em _downloads_temp.", "AVISO")
        if args.json:
            print(json.dumps({"importados": importados}, ensure_ascii=False, indent=2))
        return

    # ETAPA 1: Listar nomeações (ou usar --so-baixar)
    if args.so_baixar:
        # Modo direto: pula AJ, baixa CNJs específicos
        cnjs_para_baixar = args.so_baixar
        nomeacoes = []
        log(f"Modo direto: {len(cnjs_para_baixar)} processos para baixar")
    else:
        # Listar do AJ
        print(f"\n{C.B}  ETAPA 1 — Listando nomeações do AJ{C.R}", file=sys.stderr)
        print(f"{'─' * 50}", file=sys.stderr)

        nomeacoes = await etapa_listar_aj(porta_aj=args.aj_porta)

        # ETAPA 1B: Listar AJG se solicitado
        if args.incluir_ajg:
            print(f"\n{C.B}  ETAPA 1B — Listando nomeações do AJG{C.R}", file=sys.stderr)
            print(f"{'─' * 50}", file=sys.stderr)
            try:
                nomeacoes_ajg = await etapa_listar_ajg(porta_ajg=args.aj_porta)
                # Unificar sem duplicar CNJs
                cnjs_existentes = {n.get("numero_processo_cnj") for n in nomeacoes}
                for n in nomeacoes_ajg:
                    if n.get("numero_processo_cnj") not in cnjs_existentes:
                        nomeacoes.append(n)
                log(f"Unificado: {len(nomeacoes)} nomeações (AJ + AJG)", "OK")
            except Exception as e:
                log(f"Erro ao consultar AJG: {e}", "AVISO")

        if not nomeacoes:
            log("Nenhuma nomeação encontrada.", "AVISO")
            return

        # Exibir tabela de nomeações
        if not args.json:
            print(file=sys.stderr)
            print(f"  {'CNJ':<27} {'Situação':<22} {'Data':<12} {'Valor':>10} {'PDF?'}", file=sys.stderr)
            print(f"  {'─' * 27} {'─' * 22} {'─' * 12} {'─' * 10} {'─' * 5}", file=sys.stderr)

            for n in nomeacoes:
                cnj = n.get("numero_processo_cnj", n.get("numero_processo_raw", "?"))[:27]
                sit = n.get("situacao", "?")[:22]
                data = n.get("data_nomeacao", "?")[:12]
                valor = n.get("valor_honorario", "")[:10]
                tem = f"{C.G}SIM{C.R}" if processo_tem_pdf(cnj) else f"{C.RE}NÃO{C.R}"
                print(f"  {cnj:<27} {sit:<22} {data:<12} {valor:>10} {tem}", file=sys.stderr)

            print(f"\n  Total: {len(nomeacoes)} nomeação(ões)", file=sys.stderr)
            print(file=sys.stderr)

        # Se --so-listar, para aqui
        if args.so_listar:
            if args.json:
                print(json.dumps(nomeacoes, ensure_ascii=False, indent=2))
            # Sempre salvar pendentes ao listar (para pipeline Windows)
            cnjs_sem_pdf = []
            for n in nomeacoes:
                cnj = n.get("numero_processo_cnj", "")
                if cnj and re.match(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', cnj) and not processo_tem_pdf(cnj):
                    cnjs_sem_pdf.append(cnj)
            if cnjs_sem_pdf:
                salvar_pendentes(cnjs_sem_pdf)
            return

        # Determinar quais processos baixar
        cnjs_para_baixar = []
        mapa_nomeacao = {}  # cnj → dados da nomeação

        for n in nomeacoes:
            cnj = n.get("numero_processo_cnj", "")
            if not cnj or not re.match(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', cnj):
                continue

            mapa_nomeacao[cnj] = n

            if args.novos_apenas and processo_tem_pdf(cnj):
                continue

            cnjs_para_baixar.append(cnj)

        # Criar/atualizar FICHA.json para todas as nomeações
        for cnj, dados in mapa_nomeacao.items():
            pasta = obter_pasta_processo(cnj)
            criar_ou_atualizar_ficha(pasta, cnj, dados_nomeacao=dados)

    if not cnjs_para_baixar:
        log("Todos os processos já têm PDF (use sem --novos-apenas para forçar).", "OK")
        limpar_pendentes()
        if args.json:
            resumo = {
                "nomeacoes": len(nomeacoes),
                "novos": 0,
                "baixados": 0,
                "mensagem": "Todos já têm PDF"
            }
            print(json.dumps(resumo, ensure_ascii=False, indent=2))
        return

    # Salvar pendentes para pipeline Windows
    if args.exportar_pendentes or not args.so_baixar:
        salvar_pendentes(cnjs_para_baixar)

    if args.exportar_pendentes:
        log(f"{len(cnjs_para_baixar)} processos exportados para _pendentes_download.json", "OK")
        log("Agora rode sincronizar-pje-windows.cmd no Windows para baixar.", "INFO")
        log("Depois rode: python3 sincronizar_aj_pje.py --importar", "INFO")
        if args.json:
            print(json.dumps({"pendentes": cnjs_para_baixar}, ensure_ascii=False, indent=2))
        return

    # ETAPA 2: Baixar do PJe
    print(f"\n{C.B}  ETAPA 2 — Baixando {len(cnjs_para_baixar)} processos do PJe{C.R}", file=sys.stderr)
    print(f"{'─' * 50}", file=sys.stderr)

    for cnj in cnjs_para_baixar:
        log(f"  → {cnj}")

    resultados = await etapa_baixar_pje(
        cnjs_para_baixar,
        ip_pje=args.pje_ip,
        porta_pje=args.pje_porta
    )

    # Atualizar FICHA.json dos processos baixados com sucesso
    for r in resultados:
        if r["sucesso"]:
            cnj = r["cnj"]
            pasta = Path(r["pasta"])
            dados_nom = mapa_nomeacao.get(cnj) if not args.so_baixar else None
            criar_ou_atualizar_ficha(pasta, cnj, dados_nomeacao=dados_nom)

    # RESUMO
    sucesso = sum(1 for r in resultados if r["sucesso"])
    falha = sum(1 for r in resultados if not r["sucesso"])

    if args.json:
        resumo = {
            "nomeacoes": len(nomeacoes),
            "para_baixar": len(cnjs_para_baixar),
            "baixados": sucesso,
            "falhas": falha,
            "resultados": resultados,
        }
        print(json.dumps(resumo, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'═' * 50}", file=sys.stderr)
        print(f"  {C.B}RESUMO{C.R}", file=sys.stderr)
        print(f"{'─' * 50}", file=sys.stderr)
        print(f"  Nomeações no AJ:  {len(nomeacoes)}", file=sys.stderr)
        print(f"  Para baixar:      {len(cnjs_para_baixar)}", file=sys.stderr)
        print(f"  {C.G}Baixados:{C.R}        {sucesso}", file=sys.stderr)
        if falha:
            print(f"  {C.RE}Falhas:{C.R}          {falha}", file=sys.stderr)
        print(f"{'═' * 50}\n", file=sys.stderr)


# ============================================================
# DIAGNÓSTICO
# ============================================================

def diagnostico():
    """Verifica pré-requisitos do pipeline."""
    import urllib.request

    print(f"\n{C.B}  DIAGNÓSTICO DO PIPELINE PJe{C.R}")
    print(f"{'═' * 50}")

    # 1. Chrome AJ
    try:
        urllib.request.urlopen("http://localhost:9223/json/version", timeout=3)
        print(f"  {C.G}✓{C.R} Chrome AJ (porta 9223): conectado")
    except Exception:
        print(f"  {C.RE}✗{C.R} Chrome AJ (porta 9223): NÃO conectado")
        print(f"    → Abra: ~/Desktop/Abrir Chrome AJ.command")

    # 2. Pendentes
    if PENDENTES_JSON.exists():
        try:
            pendentes = json.loads(PENDENTES_JSON.read_text(encoding="utf-8"))
            if pendentes:
                print(f"  {C.G}✓{C.R} Pendentes JSON: {len(pendentes)} processos")
            else:
                print(f"  {C.Y}⚠{C.R} Pendentes JSON: vazio (rode --so-listar primeiro)")
        except Exception:
            print(f"  {C.RE}✗{C.R} Pendentes JSON: arquivo inválido")
    else:
        print(f"  {C.Y}⚠{C.R} Pendentes JSON: não existe (rode --so-listar primeiro)")

    # 3. Downloads temp
    if DOWNLOADS_TEMP.exists():
        pdfs = list(DOWNLOADS_TEMP.glob("*/autos-completos.pdf"))
        if pdfs:
            print(f"  {C.G}✓{C.R} Downloads temp: {len(pdfs)} PDFs prontos para importar")
        else:
            print(f"  {C.DIM}·{C.R} Downloads temp: pasta existe mas sem PDFs")
    else:
        print(f"  {C.DIM}·{C.R} Downloads temp: não existe (criada pelo Windows)")

    # 4. Flag de conclusão
    flag = BASE_DIR / "_download_concluido.flag"
    if flag.exists():
        conteudo = flag.read_text(encoding="utf-8", errors="ignore").strip()
        print(f"  {C.G}✓{C.R} Flag de conclusão: {conteudo}")
    else:
        print(f"  {C.DIM}·{C.R} Flag de conclusão: não existe")

    # 5. Processos
    total = 0
    com_pdf = 0
    sem_pdf = 0
    cnjs_sem = []

    if PROCESSOS_DIR.exists():
        for item in PROCESSOS_DIR.iterdir():
            if not item.is_dir():
                continue
            # Pular pastas Perícia (contamos via symlink)
            if item.name.startswith("Perícia"):
                continue
            total += 1
            resolved = item.resolve()
            tem = False
            for nome in ["autos-completos.pdf", "PROCESSO-ORIGINAL.pdf"]:
                if (resolved / nome).exists():
                    tem = True
                    break
            if tem:
                com_pdf += 1
            else:
                sem_pdf += 1
                cnjs_sem.append(item.name)

    print(f"\n  {C.B}Processos:{C.R}")
    print(f"    Total:    {total}")
    print(f"    Com PDF:  {C.G}{com_pdf}{C.R}")
    print(f"    Sem PDF:  {C.RE}{sem_pdf}{C.R}")

    if cnjs_sem and sem_pdf <= 10:
        print(f"\n  CNJs sem PDF:")
        for cnj in cnjs_sem[:10]:
            print(f"    · {cnj}")
    elif cnjs_sem:
        print(f"\n  Primeiros 10 CNJs sem PDF:")
        for cnj in cnjs_sem[:10]:
            print(f"    · {cnj}")
        print(f"    ... e mais {len(cnjs_sem) - 10}")

    # 6. Ferramentas
    print(f"\n  {C.B}Ferramentas:{C.R}")
    for cmd, nome in [("pdftotext", "pdftotext"), ("pdfinfo", "pdfinfo")]:
        ok = shutil.which(cmd)
        if ok:
            print(f"    {C.G}✓{C.R} {nome}: {ok}")
        else:
            print(f"    {C.RE}✗{C.R} {nome}: NÃO encontrado (brew install poppler)")

    print(f"\n{'═' * 50}\n")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Sincronizar nomeações AJ + download PJe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python3 sincronizar_aj_pje.py --so-listar\n"
            "  python3 sincronizar_aj_pje.py --novos-apenas\n"
            "  python3 sincronizar_aj_pje.py --so-baixar 5001615-98.2025.8.13.0074\n"
            "  python3 sincronizar_aj_pje.py --novos-apenas --json\n"
        )
    )

    # Conexão AJ (Chrome Mac)
    parser.add_argument("--aj-porta", type=int, default=9223,
                        help="Porta CDP do Chrome AJ no Mac (padrão: 9223)")

    # Conexão PJe (Chrome Mac ou Windows/Parallels)
    parser.add_argument("--pje-ip", default="localhost",
                        help="IP do Chrome PJe (padrão: localhost)")
    parser.add_argument("--pje-porta", type=int, default=9224,
                        help="Porta CDP do Chrome PJe (padrão: 9224)")

    # Modos de operação
    parser.add_argument("--so-listar", action="store_true",
                        help="Só lista nomeações do AJ, não baixa")
    parser.add_argument("--so-baixar", nargs="+", metavar="CNJ",
                        help="Baixa processos específicos (pula AJ)")
    parser.add_argument("--novos-apenas", action="store_true",
                        help="Pula processos que já têm PDF")
    parser.add_argument("--exportar-pendentes", action="store_true",
                        help="Salva CNJs sem PDF em _pendentes_download.json (para Windows)")
    parser.add_argument("--importar", action="store_true",
                        help="Importa PDFs de _downloads_temp (baixados pelo Windows)")
    parser.add_argument("--incluir-ajg", action="store_true",
                        help="Também consulta AJG Federal (mesma porta 9223)")
    parser.add_argument("--diagnostico", action="store_true",
                        help="Verifica pré-requisitos do pipeline")

    # Saída
    parser.add_argument("--json", action="store_true",
                        help="Saída em formato JSON")

    args = parser.parse_args()

    if args.diagnostico:
        diagnostico()
        return

    asyncio.run(sincronizar(args))


if __name__ == "__main__":
    main()
