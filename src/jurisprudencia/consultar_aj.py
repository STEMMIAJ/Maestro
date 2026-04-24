#!/usr/bin/env python3
"""
Consulta automatizada de nomeações no sistema AJ (Auxiliar da Justiça) TJMG.
Conecta ao Chrome via CDP (já autenticado com CPF/senha).

Uso:
  1. Abra o Chrome AJ com o atalho na Mesa (ou manualmente com --remote-debugging-port=9223)
  2. Faça login no AJ (aj.tjmg.jus.br) com CPF e senha
  3. Execute: python3 consultar_aj.py [opções]

Opções:
  --porta       Porta do Chrome debug (padrão: 9223)
  --listar      Lista todas as nomeações
  --pendentes   Lista apenas nomeações AGUARDANDO ACEITE
  --detalhar N  Detalha a nomeação de número N (abre e extrai dados)
  --json        Saída em JSON (padrão: tabela formatada)

IMPORTANTE: Este script NUNCA clica em Aceitar ou Rejeitar.
            Apenas consulta e extrai dados (somente leitura).
"""

import asyncio
import argparse
import json
import re
import sys
from datetime import datetime

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright não instalado. Rode:")
    print("  pip install playwright")
    sys.exit(1)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

AJ_BASE = "https://aj.tjmg.jus.br/aj/internet"
AJ_PENDENCIAS = f"{AJ_BASE}/pendenciasinternet.jsf"
AJ_CONSULTA = f"{AJ_BASE}/consultarNomeacoes.jsf"

# Regex para converter número de processo AJ (sem formatação) → CNJ
# Entrada:  50024246220258130309
# Saída:    5002424-62.2025.8.13.0309
RE_AJ_PARA_CNJ = re.compile(r'^(\d{7})(\d{2})(\d{4})(\d)(\d{2})(\d{4})$')

# Regex para número CNJ formatado
RE_CNJ = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ", "OK": "✓", "ERRO": "✗", "AVISO": "⚠"}.get(level, "·")
    print(f"  [{ts}] {prefix} {msg}", file=sys.stderr)


def converter_cnj(numero_raw):
    """Converte número do AJ (sem formatação) para formato CNJ."""
    numero_limpo = re.sub(r'[^0-9]', '', numero_raw)
    m = RE_AJ_PARA_CNJ.match(numero_limpo)
    if m:
        return f"{m.group(1)}-{m.group(2)}.{m.group(3)}.{m.group(4)}.{m.group(5)}.{m.group(6)}"
    # Se já estiver formatado, retorna como está
    if RE_CNJ.match(numero_raw):
        return numero_raw
    return numero_raw


# ============================================================
# CONEXÃO CDP
# ============================================================

async def conectar_aj(porta=9223):
    """Conecta ao Chrome via CDP e retorna (playwright, browser, page)."""
    cdp_url = f"http://localhost:{porta}"
    log(f"Conectando ao Chrome em {cdp_url}...")

    pw = await async_playwright().start()
    try:
        browser = await pw.chromium.connect_over_cdp(cdp_url)
    except Exception as e:
        log(f"Não consegui conectar ao Chrome: {e}", "ERRO")
        print(file=sys.stderr)
        print("Verifique:", file=sys.stderr)
        print(f"  1. Chrome está rodando com --remote-debugging-port={porta}", file=sys.stderr)
        print("  2. Você fez login no AJ (aj.tjmg.jus.br)", file=sys.stderr)
        print(f"  3. Teste: curl http://localhost:{porta}/json/version", file=sys.stderr)
        print(file=sys.stderr)
        print("Para abrir o Chrome com CDP, use o atalho 'Abrir Chrome AJ.command' na Mesa.", file=sys.stderr)
        await pw.stop()
        sys.exit(1)

    log("Conectado ao Chrome!", "OK")

    contexts = browser.contexts
    if not contexts:
        log("Nenhum contexto encontrado no Chrome", "ERRO")
        await pw.stop()
        sys.exit(1)

    context = contexts[0]
    pages = context.pages
    page = pages[0] if pages else await context.new_page()

    return pw, browser, page


# ============================================================
# NAVEGAÇÃO AO MENU CONSULTAR NOMEAÇÕES
# ============================================================

async def navegar_consulta(page):
    """Navega até a tela de Consulta de Nomeações."""
    url_atual = page.url

    # Se já está na tela de consulta, não precisa navegar
    if "consultarNomeacoes" in url_atual:
        log("Já na tela de consulta de nomeações")
        return

    # Verifica se está logado (deve estar em alguma página do AJ)
    if "aj.tjmg.jus.br" not in url_atual:
        log("Navegando ao AJ...", "AVISO")
        await page.goto(AJ_PENDENCIAS, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

    # Tenta navegar pelo menu lateral → Nomeações → Consultar
    menu_seletores = [
        # Link direto "Consultar" no menu de Nomeações
        "//a[contains(text(), 'Consultar') and ancestor::*[contains(@class, 'menu') or contains(@id, 'menu')]]",
        "//a[text()='Consultar']",
        "//a[contains(@href, 'consultarNomeacoes')]",
        # Menu "Nomeações" primeiro, depois "Consultar"
        "a[href*='consultarNomeacoes']",
    ]

    clicou = False
    for seletor in menu_seletores:
        try:
            elem = page.locator(seletor).first
            if await elem.is_visible(timeout=3000):
                await elem.click()
                clicou = True
                await page.wait_for_timeout(2000)
                break
        except Exception:
            continue

    if not clicou:
        # Tenta expandir o menu "Nomeações" primeiro
        try:
            menu_nomeacoes = page.locator(
                "//span[contains(text(), 'Nomeaç')]/parent::a, "
                "//a[contains(text(), 'Nomeaç')]"
            ).first
            if await menu_nomeacoes.is_visible(timeout=3000):
                await menu_nomeacoes.click()
                await page.wait_for_timeout(1000)

                # Agora clica em "Consultar"
                consultar = page.locator("//a[text()='Consultar']").first
                if await consultar.is_visible(timeout=3000):
                    await consultar.click()
                    clicou = True
                    await page.wait_for_timeout(2000)
        except Exception:
            pass

    if not clicou:
        # Último recurso: acesso direto pela URL
        log("Menu não encontrado, tentando URL direta...", "AVISO")
        await page.goto(AJ_CONSULTA, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

    # Verifica se chegou na tela certa
    content = await page.content()
    if "Consulta" in content and ("Nomeaç" in content or "Situaç" in content):
        log("Tela de consulta de nomeações carregada", "OK")
    else:
        log("Pode não estar na tela correta — continuando mesmo assim", "AVISO")


# ============================================================
# LISTAR NOMEAÇÕES
# ============================================================

async def listar_nomeacoes(page, situacao="TODAS"):
    """
    Filtra e extrai a lista de nomeações da tabela.

    Args:
        page: Página Playwright
        situacao: Filtro (TODAS, ACEITA, AGUARDANDO ACEITE, RECUSADA, etc.)

    Returns:
        Lista de dicts com dados de cada nomeação
    """
    log(f"Filtrando nomeações por situação: {situacao}...")

    # Muda o dropdown "Situação"
    # Mapa de situação → value do dropdown do AJ TJMG
    SITUACAO_VALUES = {
        "TODAS": "0",
        "AGUARDANDO ACEITE": "1",
        "RECUSADA": "2",
        "CANCELADA PELO JUIZ": "3",
        "PERDA DE PRAZO": "4",
        "ACEITA": "5",
        "SERVIÇO PRESTADO": "7",
        "PRAZO RENOVADO": "8",
    }

    dropdown_seletores = [
        "[id='form:situacao_input']",
        "select[id*='situacao']",
        "select[id*='Situacao']",
        "//select[contains(@id, 'situacao')]",
    ]

    dropdown_ok = False
    valor = SITUACAO_VALUES.get(situacao.upper(), "0")

    # PrimeFaces esconde o <select> nativo — usar JS para alterar valor
    try:
        changed = await page.evaluate("""(valor) => {
            var el = document.getElementById('form:situacao_input');
            if (!el) return false;
            el.value = valor;
            el.dispatchEvent(new Event('change', {bubbles: true}));
            return true;
        }""", valor)
        if changed:
            log(f"Situação alterada para: {situacao} (via JS)", "OK")
            dropdown_ok = True
    except Exception:
        pass

    if not dropdown_ok:
        # Fallback: tenta via Playwright select_option com force
        for seletor in dropdown_seletores:
            try:
                dropdown = page.locator(seletor).first
                count = await dropdown.count()
                if count > 0:
                    await dropdown.select_option(value=valor, force=True)
                    log(f"Situação alterada para: {situacao} (via force)", "OK")
                    dropdown_ok = True
                    break
            except Exception:
                continue

    if not dropdown_ok:
        log("Dropdown de situação não encontrado — continuando com filtro atual", "AVISO")

    await page.wait_for_timeout(500)

    # Clica no botão "Consultar"
    btn_seletores = [
        "input[value='Consultar']",
        "button:has-text('Consultar')",
        "//input[@value='Consultar']",
        "//button[contains(text(), 'Consultar')]",
        "input[type='submit'][value*='onsultar']",
    ]

    for seletor in btn_seletores:
        try:
            btn = page.locator(seletor).first
            if await btn.is_visible(timeout=3000):
                await btn.click()
                await page.wait_for_timeout(3000)
                log("Consulta executada", "OK")
                break
        except Exception:
            continue

    # Extrai dados da tabela de resultados
    nomeacoes = []

    # Procura a tabela de resultados
    tabela_seletores = [
        # AJ TJMG: tabela de dados é a que NÃO é o formulário de filtro
        "table:not([id='form:pgFiltro']):not([class*='panelgrid'])",
        "table[id*='lista']",
        "table[id*='nomeac']",
        "table[id*='resultado']",
        "//table[contains(@class, 'rich-table') or contains(@class, 'dataTable')]",
        "table.rich-table",
        "table.dataTable",
        "//table[.//th[contains(text(), 'mero')]]",
    ]

    tabela = None
    for seletor in tabela_seletores:
        try:
            t = page.locator(seletor).first
            if await t.is_visible(timeout=3000):
                # Confirma que tem pelo menos 2 rows com 7 cells (dados reais)
                rows = await t.locator("tr").all()
                if len(rows) >= 2:
                    cells = await rows[1].locator("td").all()
                    if len(cells) >= 7:
                        tabela = t
                        log(f"Tabela encontrada ({len(rows)} rows)", "OK")
                        break
        except Exception:
            continue

    if not tabela:
        log("Tabela de nomeações não encontrada", "AVISO")
        content = await page.content()
        if "Não existem" in content or "nenhum resultado" in content.lower():
            log("Nenhuma nomeação encontrada com este filtro", "INFO")
            return []
        log("Tentando extrair dados do HTML...", "AVISO")
        return await _extrair_nomeacoes_html(page)

    # Extrai linhas da tabela (pula rows sem 7 cells — header vazio, etc.)
    todas_linhas = await tabela.locator("tr").all()
    linhas = []
    for row in todas_linhas:
        cells = await row.locator("td").all()
        if len(cells) >= 7:
            linhas.append(row)
    log(f"Encontradas {len(linhas)} linhas com dados na tabela")

    for linha in linhas:
        try:
            celulas = await linha.locator("td").all()
            if len(celulas) < 4:
                continue

            textos = []
            for cel in celulas:
                texto = (await cel.inner_text()).strip()
                textos.append(texto)

            # Monta o dict com os campos conhecidos
            # Colunas esperadas: Nomeação | Processo | Unidade | Data | Dias | Valor | Situação
            nomeacao = {
                "numero_nomeacao": textos[0] if len(textos) > 0 else "",
                "numero_processo_raw": textos[1] if len(textos) > 1 else "",
                "unidade": textos[2] if len(textos) > 2 else "",
                "data_nomeacao": textos[3] if len(textos) > 3 else "",
                "dias_aceite": textos[4] if len(textos) > 4 else "",
                "valor_honorario": textos[5] if len(textos) > 5 else "",
                "situacao": textos[6] if len(textos) > 6 else "",
            }

            # Converte número do processo para CNJ
            if nomeacao["numero_processo_raw"]:
                nomeacao["numero_processo_cnj"] = converter_cnj(nomeacao["numero_processo_raw"])

            nomeacoes.append(nomeacao)

        except Exception as e:
            log(f"Erro ao extrair linha: {e}", "AVISO")
            continue

    log(f"Total de nomeações extraídas: {len(nomeacoes)}", "OK")
    return nomeacoes


async def _extrair_nomeacoes_html(page):
    """Fallback: extrai nomeações parseando o HTML bruto."""
    nomeacoes = []
    content = await page.content()

    # Tenta encontrar todas as linhas de tabela com dados numéricos
    # Padrão: número de nomeação (14 dígitos) seguido de outros dados
    import re as _re
    padrao_nomeacao = _re.compile(r'(\d{14})\s*</td>', _re.IGNORECASE)
    padrao_processo = _re.compile(r'(\d{20})\s*</td>', _re.IGNORECASE)

    nums_nomeacao = padrao_nomeacao.findall(content)
    nums_processo = padrao_processo.findall(content)

    for i, num in enumerate(nums_nomeacao):
        nomeacao = {
            "numero_nomeacao": num,
            "numero_processo_raw": nums_processo[i] if i < len(nums_processo) else "",
        }
        if nomeacao["numero_processo_raw"]:
            nomeacao["numero_processo_cnj"] = converter_cnj(nomeacao["numero_processo_raw"])
        nomeacoes.append(nomeacao)

    if nomeacoes:
        log(f"Extraídas {len(nomeacoes)} nomeações via HTML bruto", "OK")
    return nomeacoes


# ============================================================
# DETALHAR NOMEAÇÃO
# ============================================================

async def detalhar_nomeacao(page, numero_nomeacao):
    """
    Abre o detalhe de uma nomeação e extrai todos os dados.
    NÃO clica em Aceitar nem Rejeitar.

    Returns:
        Dict com todos os campos do detalhe
    """
    log(f"Abrindo detalhe da nomeação {numero_nomeacao}...")

    # Clica na linha da nomeação na tabela
    try:
        # Tenta clicar na linha que contém o número
        linha = page.locator(f"//tr[contains(., '{numero_nomeacao}')]").first
        if await linha.is_visible(timeout=5000):
            await linha.click()
            await page.wait_for_timeout(3000)
        else:
            log(f"Nomeação {numero_nomeacao} não encontrada na tabela", "ERRO")
            return None
    except Exception as e:
        log(f"Erro ao clicar na nomeação: {e}", "ERRO")
        return None

    # Extrai dados da tela de detalhe
    detalhe = {"numero_nomeacao": numero_nomeacao}

    # Campos do detalhe
    campos_mapeamento = {
        "Número": "numero",
        "Situação": "situacao",
        "Data da nomeação": "data_nomeacao",
        "Prazo": "prazo_dias",
        "Unidade": "unidade",
        "E-mail": "email_unidade",
        "Telefone": "telefone",
        "Categoria": "categoria",
        "Profissão": "profissao",
        "Especialidade": "especialidade",
    }

    content = await page.content()

    for label, campo in campos_mapeamento.items():
        try:
            # Tenta extrair valor ao lado do label
            elem = page.locator(f"//*[contains(text(), '{label}')]/following-sibling::*[1]").first
            if await elem.is_visible(timeout=1000):
                detalhe[campo] = (await elem.inner_text()).strip()
                continue
        except Exception:
            pass

        try:
            # Tenta com td seguinte
            elem = page.locator(
                f"//td[contains(text(), '{label}')]/following-sibling::td[1], "
                f"//th[contains(text(), '{label}')]/following-sibling::td[1], "
                f"//label[contains(text(), '{label}')]/parent::*/following-sibling::*[1]"
            ).first
            if await elem.is_visible(timeout=1000):
                detalhe[campo] = (await elem.inner_text()).strip()
        except Exception:
            pass

    # Extrai "Lista de Processos" (tabela dentro do detalhe)
    try:
        tabela_processos = page.locator(
            "//table[.//th[contains(text(), 'processo') or contains(text(), 'Processo')]]"
        ).last  # .last porque pode haver outra tabela antes

        if await tabela_processos.is_visible(timeout=3000):
            linhas = await tabela_processos.locator("tbody tr, tr:not(:first-child)").all()
            processos = []

            for linha in linhas:
                celulas = await linha.locator("td").all()
                if not celulas:
                    continue

                textos = []
                for cel in celulas:
                    textos.append((await cel.inner_text()).strip())

                proc = {
                    "numero_processo_raw": textos[0] if len(textos) > 0 else "",
                    "juiz_requisitante": textos[1] if len(textos) > 1 else "",
                    "email_juiz": textos[2] if len(textos) > 2 else "",
                    "nome_reu": textos[3] if len(textos) > 3 else "",
                    "advogado_reu": textos[4] if len(textos) > 4 else "",
                    "autor_principal": textos[5] if len(textos) > 5 else "",
                }

                if proc["numero_processo_raw"]:
                    proc["numero_processo_cnj"] = converter_cnj(proc["numero_processo_raw"])

                processos.append(proc)

            detalhe["processos"] = processos
            log(f"Encontrados {len(processos)} processos no detalhe", "OK")

    except Exception as e:
        log(f"Erro ao extrair lista de processos: {e}", "AVISO")

    # Clica em "Voltar" para retornar à lista
    try:
        voltar = page.locator(
            "input[value='Voltar'], button:has-text('Voltar'), "
            "//input[@value='Voltar'], //a[text()='Voltar']"
        ).first
        if await voltar.is_visible(timeout=3000):
            await voltar.click()
            await page.wait_for_timeout(2000)
            log("Voltou para a lista", "OK")
    except Exception:
        pass

    return detalhe


# ============================================================
# FORMATAÇÃO DE SAÍDA
# ============================================================

def formatar_tabela(nomeacoes):
    """Formata nomeações como tabela legível no terminal."""
    if not nomeacoes:
        print("\nNenhuma nomeação encontrada.\n")
        return

    print()
    print("=" * 100)
    print("  NOMEAÇÕES - AJ TJMG")
    print("=" * 100)
    print()
    print(f"  {'Nomeação':<16} {'Processo CNJ':<25} {'Situação':<22} {'Data':<12} {'Valor':>10}")
    print(f"  {'─' * 16} {'─' * 25} {'─' * 22} {'─' * 12} {'─' * 10}")

    for n in nomeacoes:
        num_nom = n.get("numero_nomeacao", "?")[:16]
        cnj = n.get("numero_processo_cnj", n.get("numero_processo_raw", "?"))[:25]
        sit = n.get("situacao", "?")[:22]
        data = n.get("data_nomeacao", "?")[:12]
        valor = n.get("valor_honorario", "")[:10]

        print(f"  {num_nom:<16} {cnj:<25} {sit:<22} {data:<12} {valor:>10}")

    print()
    print(f"  Total: {len(nomeacoes)} nomeação(ões)")
    print()


def formatar_detalhe(detalhe):
    """Formata detalhe de nomeação para o terminal."""
    if not detalhe:
        print("\nDetalhe não encontrado.\n")
        return

    print()
    print("=" * 80)
    print("  DETALHE DA NOMEAÇÃO")
    print("=" * 80)

    campos = [
        ("Número", "numero"),
        ("Situação", "situacao"),
        ("Data", "data_nomeacao"),
        ("Prazo (dias)", "prazo_dias"),
        ("Unidade", "unidade"),
        ("E-mail", "email_unidade"),
        ("Telefone", "telefone"),
        ("Categoria", "categoria"),
        ("Profissão", "profissao"),
        ("Especialidade", "especialidade"),
    ]

    print()
    for label, campo in campos:
        valor = detalhe.get(campo, "—")
        if valor:
            print(f"  {label + ':':<20} {valor}")

    processos = detalhe.get("processos", [])
    if processos:
        print()
        print("  PROCESSOS VINCULADOS:")
        print(f"  {'─' * 70}")
        for p in processos:
            cnj = p.get("numero_processo_cnj", p.get("numero_processo_raw", "?"))
            print(f"  Processo:  {cnj}")
            if p.get("juiz_requisitante"):
                print(f"  Juiz:      {p['juiz_requisitante']}")
            if p.get("autor_principal"):
                print(f"  Autor:     {p['autor_principal']}")
            if p.get("nome_reu"):
                print(f"  Réu:       {p['nome_reu']}")
            if p.get("advogado_reu"):
                print(f"  Advogado:  {p['advogado_reu']}")
            print()

    print("=" * 80)
    print()


# ============================================================
# MAIN
# ============================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Consulta nomeações no AJ TJMG (somente leitura)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="IMPORTANTE: Este script NUNCA aceita ou rejeita nomeações."
    )
    parser.add_argument("--porta", type=int, default=9223,
                        help="Porta do Chrome debug (padrão: 9223)")
    parser.add_argument("--listar", action="store_true",
                        help="Lista todas as nomeações")
    parser.add_argument("--pendentes", action="store_true",
                        help="Lista apenas AGUARDANDO ACEITE")
    parser.add_argument("--detalhar", type=str, metavar="NUM",
                        help="Detalha nomeação pelo número")
    parser.add_argument("--json", action="store_true",
                        help="Saída em JSON")
    parser.add_argument("--situacao", type=str, default=None,
                        help="Filtro de situação (ex: ACEITA, RECUSADA)")
    args = parser.parse_args()

    # Se nenhuma ação especificada, mostra pendentes
    if not args.listar and not args.pendentes and not args.detalhar:
        args.pendentes = True

    # Conecta ao Chrome
    pw, browser, page = await conectar_aj(args.porta)

    try:
        # Navega à tela de consulta
        await navegar_consulta(page)

        if args.detalhar:
            # Detalha uma nomeação específica
            # Primeiro lista todas para encontrar a linha
            await listar_nomeacoes(page, situacao="TODAS")
            detalhe = await detalhar_nomeacao(page, args.detalhar)

            if args.json:
                print(json.dumps(detalhe, ensure_ascii=False, indent=2))
            else:
                formatar_detalhe(detalhe)

        else:
            # Define filtro
            if args.pendentes:
                situacao = "AGUARDANDO ACEITE"
            elif args.situacao:
                situacao = args.situacao.upper()
            else:
                situacao = "TODAS"

            # Lista nomeações
            nomeacoes = await listar_nomeacoes(page, situacao=situacao)

            # Se filtrou por "TODAS" mas quer só pendentes, filtra localmente
            if args.pendentes and situacao == "TODAS":
                nomeacoes = [n for n in nomeacoes if "AGUARDANDO" in n.get("situacao", "").upper()]

            # Se filtrou como "AGUARDANDO ACEITE" mas o dropdown não tinha essa opção,
            # pode ter listado TODAS — filtra localmente por segurança
            if args.pendentes:
                nomeacoes = [n for n in nomeacoes if "AGUARDANDO" in n.get("situacao", "").upper()]

            if args.json:
                print(json.dumps(nomeacoes, ensure_ascii=False, indent=2))
            else:
                formatar_tabela(nomeacoes)

                # Resumo das pendentes
                pendentes = [n for n in nomeacoes if "AGUARDANDO" in n.get("situacao", "").upper()]
                if pendentes and not args.pendentes:
                    print(f"  ⚠ {len(pendentes)} nomeação(ões) AGUARDANDO ACEITE")
                    print()

    finally:
        await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())
