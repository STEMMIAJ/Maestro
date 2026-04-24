#!/usr/bin/env python3
"""
Consulta automatizada de nomeações no sistema AJG (Auxiliar da Justiça Federal).
Conecta ao Chrome via CDP (já autenticado com CPF/senha).

Uso:
  1. Abra o Chrome AJ com o atalho na Mesa (--remote-debugging-port=9223)
  2. Faça login no AJG (ajg.cjf.jus.br) em uma aba
  3. Execute: python3 consultar_ajg.py [opções]

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

AJG_BASE = "https://ajg.cjf.jus.br/ajg2/internet"
AJG_PENDENCIAS = f"{AJG_BASE}/pendenciasinternet.jsf"
AJG_CONSULTA = f"{AJG_BASE}/nomeacoes/consultanomeacoes.jsf"

# Regex para converter número de processo AJG (sem formatação) → CNJ
# Entrada:  50001628220228130362
# Saída:    5000162-82.2022.8.13.0362
RE_AJG_PARA_CNJ = re.compile(r'^(\d{7})(\d{2})(\d{4})(\d)(\d{2})(\d{4})$')

# Regex para número CNJ formatado
RE_CNJ = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')

# Mapa de situações → valores dos checkboxes no AJG
# form:checkBoxSituacao:0 = 1 = AGUARDANDO ACEITE
# form:checkBoxSituacao:1 = 2 = RECUSADA
# form:checkBoxSituacao:2 = 3 = CANCELADA PELO JUIZ
# form:checkBoxSituacao:3 = 4 = PERDA DE PRAZO
# form:checkBoxSituacao:4 = 5 = ACEITA
# form:checkBoxSituacao:5 = 6 = BAIXADA
# form:checkBoxSituacao:6 = 7 = SERVIÇO PRESTADO
SITUACAO_CHECKBOX = {
    "AGUARDANDO ACEITE": 0,
    "RECUSADA": 1,
    "CANCELADA PELO JUIZ": 2,
    "PERDA DE PRAZO": 3,
    "ACEITA": 4,
    "BAIXADA": 5,
    "SERVIÇO PRESTADO": 6,
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ", "OK": "✓", "ERRO": "✗", "AVISO": "⚠"}.get(level, "·")
    print(f"  [{ts}] {prefix} {msg}", file=sys.stderr)


def converter_cnj(numero_raw):
    """Converte número do AJG (sem formatação) para formato CNJ."""
    numero_limpo = re.sub(r'[^0-9]', '', numero_raw)
    m = RE_AJG_PARA_CNJ.match(numero_limpo)
    if m:
        return f"{m.group(1)}-{m.group(2)}.{m.group(3)}.{m.group(4)}.{m.group(5)}.{m.group(6)}"
    if RE_CNJ.match(numero_raw):
        return numero_raw
    return numero_raw


def detectar_tribunal(cnj):
    """Detecta o tribunal pelo segmento do CNJ (posição 14-15)."""
    limpo = re.sub(r'[^0-9]', '', cnj)
    if len(limpo) >= 16:
        justica = limpo[13]  # 5 = federal, 8 = estadual
        ramo = limpo[14:16]
        if justica == "5":
            return f"TRF{ramo}" if ramo != "00" else "TRF"
        elif justica == "8":
            return f"TJ{ramo}" if ramo != "00" else "TJ"
    return "JF"


# ============================================================
# CONEXÃO CDP
# ============================================================

async def conectar_ajg(porta=9223):
    """Conecta ao Chrome via CDP e retorna (playwright, browser, page) com a aba do AJG."""
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
        print("  2. Você fez login no AJG (ajg.cjf.jus.br)", file=sys.stderr)
        print(f"  3. Teste: curl http://localhost:{porta}/json/version", file=sys.stderr)
        print(file=sys.stderr)
        print("Para abrir o Chrome com CDP, use o atalho 'Abrir Chrome AJ.command' na Mesa.", file=sys.stderr)
        await pw.stop()
        sys.exit(1)

    log("Conectado ao Chrome!", "OK")

    # Encontra a aba do AJG (pode ter AJ e AJG abertos no mesmo Chrome)
    page = None
    for ctx in browser.contexts:
        for p in ctx.pages:
            if "ajg" in p.url.lower():
                page = p
                break
        if page:
            break

    if not page:
        log("Aba do AJG não encontrada. Abrindo...", "AVISO")
        contexts = browser.contexts
        if contexts:
            page = await contexts[0].new_page()
            await page.goto(AJG_CONSULTA, wait_until="networkidle", timeout=30000)
        else:
            log("Nenhum contexto no Chrome", "ERRO")
            await pw.stop()
            sys.exit(1)

    return pw, browser, page


# ============================================================
# NAVEGAÇÃO
# ============================================================

async def navegar_consulta(page):
    """Navega até a tela de Consulta de Nomeações do AJG."""
    url_atual = page.url

    if "consultanomeacoes" in url_atual.lower():
        log("Já na tela de consulta de nomeações")
        return

    log("Navegando para consulta de nomeações...", "INFO")
    await page.goto(AJG_CONSULTA, wait_until="networkidle", timeout=30000)
    await page.wait_for_timeout(2000)

    content = await page.content()
    if "Consulta" in content and "Nomeaç" in content:
        log("Tela de consulta de nomeações carregada", "OK")
    else:
        log("Pode não estar na tela correta", "AVISO")


# ============================================================
# LISTAR NOMEAÇÕES
# ============================================================

async def listar_nomeacoes(page, situacao="TODAS"):
    """
    Filtra e extrai a lista de nomeações da tabela do AJG.

    O AJG usa checkboxes (não dropdown) para filtrar situação.
    Checkbox "TODAS" marca/desmarca todos.

    Args:
        page: Página Playwright
        situacao: Filtro (TODAS, ACEITA, AGUARDANDO ACEITE, etc.)

    Returns:
        Lista de dicts com dados de cada nomeação
    """
    log(f"Filtrando nomeações por situação: {situacao}...")

    if situacao.upper() == "TODAS":
        # Clica em "TODAS" para marcar todos os checkboxes
        try:
            todas_label = page.locator("text=TODAS").first
            if await todas_label.is_visible(timeout=3000):
                # Verificar se já está marcado
                todas_cb = page.locator("#form\\:j_idt93_input")
                is_checked = await todas_cb.is_checked()
                if not is_checked:
                    await todas_label.click()
                    await page.wait_for_timeout(500)
                log("Filtro TODAS ativado", "OK")
        except Exception as e:
            log(f"Erro ao marcar TODAS: {e}", "AVISO")
            # Fallback: marcar via JS
            await page.evaluate("""() => {
                var cb = document.getElementById('form:j_idt93_input');
                if (cb && !cb.checked) { cb.click(); }
            }""")
            await page.wait_for_timeout(500)
    else:
        # Desmarcar TODAS primeiro, depois marcar só a desejada
        await page.evaluate("""() => {
            var todas = document.getElementById('form:j_idt93_input');
            if (todas && todas.checked) { todas.click(); }
        }""")
        await page.wait_for_timeout(300)

        idx = SITUACAO_CHECKBOX.get(situacao.upper())
        if idx is not None:
            cb_id = f"form:checkBoxSituacao:{idx}"
            await page.evaluate(f"""() => {{
                var cb = document.getElementById('{cb_id}');
                if (cb && !cb.checked) {{ cb.click(); }}
            }}""")
            await page.wait_for_timeout(300)
            log(f"Filtro {situacao} ativado (checkbox {idx})", "OK")
        else:
            log(f"Situação '{situacao}' não reconhecida", "AVISO")

    # Clicar em Consultar
    try:
        btn = page.locator("#form\\:comandoConsultar")
        await btn.click()
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        log("Consulta executada", "OK")
    except Exception as e:
        log(f"Erro ao clicar Consultar: {e}", "ERRO")
        return []

    # Extrair dados da tabela de resultados
    nomeacoes = []

    # O AJG tem uma tabela com headers:
    # Número da nomeação | Número do processo | Unidade | Data de nomeação | Data prestação serviço | Situação
    body_text = await page.inner_text("body")

    # Verificar se não há resultados
    if "Nenhum registro encontrado" in body_text:
        log("Nenhuma nomeação encontrada com este filtro", "INFO")
        return []

    # Extrair tabela via JS (mais confiável que seletores com PrimeFaces)
    dados = await page.evaluate("""() => {
        var resultado = [];
        var tabelas = document.querySelectorAll('table');
        for (var tab of tabelas) {
            var ths = tab.querySelectorAll('th');
            var headers = [];
            for (var th of ths) { headers.push(th.textContent.trim()); }

            if (headers.includes('Número da nomeação') || headers.includes('Número do processo')) {
                var rows = tab.querySelectorAll('tbody tr, tr');
                for (var row of rows) {
                    var tds = row.querySelectorAll('td');
                    if (tds.length >= 5) {
                        var cells = [];
                        for (var td of tds) { cells.push(td.textContent.trim()); }
                        resultado.push(cells);
                    }
                }
                break;
            }
        }
        return resultado;
    }""")

    for cells in dados:
        if not cells or len(cells) < 5:
            continue
        # Ignorar "Nenhum registro"
        if "Nenhum" in cells[0]:
            continue

        nomeacao = {
            "numero_nomeacao": cells[0],
            "numero_processo_raw": cells[1],
            "unidade": cells[2],
            "data_nomeacao": cells[3],
            "data_prestacao_servico": cells[4] if len(cells) > 4 else "",
            "situacao": cells[5] if len(cells) > 5 else "",
            "sistema": "AJG",
            "tribunal": "JF",
        }

        # Converte número do processo para CNJ
        if nomeacao["numero_processo_raw"]:
            nomeacao["numero_processo_cnj"] = converter_cnj(nomeacao["numero_processo_raw"])
            nomeacao["tribunal"] = detectar_tribunal(nomeacao["numero_processo_cnj"])

        nomeacoes.append(nomeacao)

    log(f"Total de nomeações extraídas: {len(nomeacoes)}", "OK")
    return nomeacoes


# ============================================================
# DETALHAR NOMEAÇÃO
# ============================================================

async def detalhar_nomeacao(page, numero_nomeacao):
    """
    Abre o detalhe de uma nomeação e extrai todos os dados.
    NÃO clica em Aceitar nem Rejeitar.
    """
    log(f"Abrindo detalhe da nomeação {numero_nomeacao}...")

    # Clica na linha da nomeação na tabela
    try:
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
    detalhe = {"numero_nomeacao": numero_nomeacao, "sistema": "AJG"}

    # Extrair todos os campos visíveis via JS
    campos = await page.evaluate("""() => {
        var result = {};
        // Procurar pares label/valor em panelgrid ou qualquer tabela
        var tds = document.querySelectorAll('td');
        for (var i = 0; i < tds.length - 1; i++) {
            var texto = tds[i].textContent.trim();
            if (texto.endsWith(':') || texto.endsWith(' :')) {
                var chave = texto.replace(/[:\\s]+$/, '').trim();
                var valor = tds[i+1].textContent.trim();
                if (chave && valor && valor !== chave) {
                    result[chave] = valor;
                }
            }
        }
        // Procurar em labels
        var labels = document.querySelectorAll('label');
        for (var lbl of labels) {
            var chave = lbl.textContent.trim().replace(/[:\\s]+$/, '');
            var next = lbl.parentElement ? lbl.parentElement.nextElementSibling : null;
            if (next) {
                var valor = next.textContent.trim();
                if (chave && valor) { result[chave] = valor; }
            }
        }
        return result;
    }""")

    detalhe.update(campos)

    # Extrair tabela de processos (se houver)
    processos = await page.evaluate("""() => {
        var resultado = [];
        var tabelas = document.querySelectorAll('table');
        for (var tab of tabelas) {
            var ths = tab.querySelectorAll('th');
            var headers = [];
            for (var th of ths) { headers.push(th.textContent.trim()); }
            // Tabela de processos dentro do detalhe
            if (headers.some(h => h.toLowerCase().includes('processo'))) {
                var rows = tab.querySelectorAll('tbody tr, tr');
                for (var row of rows) {
                    var tds = row.querySelectorAll('td');
                    if (tds.length >= 2) {
                        var cells = [];
                        for (var td of tds) { cells.push(td.textContent.trim()); }
                        resultado.push(cells);
                    }
                }
            }
        }
        return resultado;
    }""")

    if processos:
        detalhe["processos"] = []
        for cells in processos:
            proc = {
                "numero_processo_raw": cells[0] if len(cells) > 0 else "",
            }
            if proc["numero_processo_raw"]:
                proc["numero_processo_cnj"] = converter_cnj(proc["numero_processo_raw"])
            if len(cells) > 1:
                proc["juiz"] = cells[1]
            if len(cells) > 2:
                proc["email_juiz"] = cells[2]
            if len(cells) > 3:
                proc["reu"] = cells[3]
            if len(cells) > 4:
                proc["autor"] = cells[4]
            detalhe["processos"].append(proc)
        log(f"Encontrados {len(detalhe['processos'])} processos no detalhe", "OK")

    # Voltar para a lista
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
        # Fallback: voltar via navegação
        await page.goto(AJG_CONSULTA, wait_until="networkidle", timeout=30000)

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
    print("=" * 105)
    print("  NOMEAÇÕES - AJG (JUSTIÇA FEDERAL)")
    print("=" * 105)
    print()
    print(f"  {'Nomeação':<16} {'Processo CNJ':<25} {'Unidade':<35} {'Data':<12} {'Situação'}")
    print(f"  {'─' * 16} {'─' * 25} {'─' * 35} {'─' * 12} {'─' * 20}")

    for n in nomeacoes:
        num_nom = n.get("numero_nomeacao", "?")[:16]
        cnj = n.get("numero_processo_cnj", n.get("numero_processo_raw", "?"))[:25]
        unidade = n.get("unidade", "?")[:35]
        data = n.get("data_nomeacao", "?")[:12]
        sit = n.get("situacao", "?")

        print(f"  {num_nom:<16} {cnj:<25} {unidade:<35} {data:<12} {sit}")

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
    print("  DETALHE DA NOMEAÇÃO (AJG)")
    print("=" * 80)
    print()

    for chave, valor in detalhe.items():
        if chave in ("processos", "sistema"):
            continue
        if isinstance(valor, str) and valor:
            print(f"  {chave + ':':<25} {valor}")

    processos = detalhe.get("processos", [])
    if processos:
        print()
        print("  PROCESSOS VINCULADOS:")
        print(f"  {'─' * 70}")
        for p in processos:
            cnj = p.get("numero_processo_cnj", p.get("numero_processo_raw", "?"))
            print(f"  Processo:  {cnj}")
            if p.get("juiz"):
                print(f"  Juiz:      {p['juiz']}")
            if p.get("autor"):
                print(f"  Autor:     {p['autor']}")
            if p.get("reu"):
                print(f"  Réu:       {p['reu']}")
            print()

    print("=" * 80)
    print()


# ============================================================
# MAIN
# ============================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Consulta nomeações no AJG - Justiça Federal (somente leitura)",
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
    parser.add_argument("--debug", action="store_true",
                        help="Modo debug: mostra seletores encontrados")
    args = parser.parse_args()

    # Se nenhuma ação especificada, mostra pendentes
    if not args.listar and not args.pendentes and not args.detalhar:
        args.pendentes = True

    # Conecta ao Chrome
    pw, browser, page = await conectar_ajg(args.porta)

    try:
        # Navega à tela de consulta
        await navegar_consulta(page)

        if args.debug:
            # Modo debug: mostra estrutura da página
            content = await page.content()
            print("=== DEBUG: Conteúdo da página ===")
            print(content[:5000])
            return

        if args.detalhar:
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

            # Se pediu pendentes, filtra localmente por segurança
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
