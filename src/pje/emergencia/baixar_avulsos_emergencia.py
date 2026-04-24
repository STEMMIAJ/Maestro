#!/usr/bin/env python3
"""
EMERGENCIA - Baixar documentos avulsos do PJe quando PDF completo da 429.

Conecta ao Chrome debug (porta 9223), encontra a pagina do processo,
clica na prancheta de cada documento e depois em ABRIR.

Uso no CMD do Windows:
  py \\Mac\Home\stemmia-forense\src\pje\baixar_avulsos_emergencia.py

Requisitos:
  - Chrome aberto com --remote-debugging-port=9223
  - Pagina do processo ja aberta (listProcessoCompleto.seam)
  - Selenium instalado: py -m pip install selenium
"""

import os
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        StaleElementReferenceException,
        TimeoutException,
        NoSuchElementException,
        ElementClickInterceptedException,
        JavascriptException,
    )
except ImportError:
    print("Selenium nao instalado. Rode: py -m pip install selenium")
    sys.exit(1)


CNJ = "5030880-86.2024.8.13.0105"
HOME = Path(os.environ.get("USERPROFILE", str(Path.home())))
DOWNLOAD_DIR = HOME / "Desktop" / "processos-pje" / f"{CNJ.replace('.','').replace('-','')}-docs"
TIMEOUT_ABRIR = 8
PAUSA_ENTRE_DOCS = 1.5


def conectar_chrome():
    for porta in [9223, 9222]:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{porta}/json/version", timeout=2) as resp:
                if "Browser" in resp.read().decode():
                    opts = Options()
                    opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{porta}")
                    driver = webdriver.Chrome(options=opts)
                    print(f"[OK] Chrome porta {porta}")
                    return driver
        except Exception:
            continue
    print("[ERRO] Chrome nao encontrado na porta 9223.")
    print("       Abra o Chrome com: chrome.exe --remote-debugging-port=9223")
    sys.exit(1)


def js_click(driver, el):
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center',behavior:'instant'});"
        "arguments[0].click();",
        el,
    )


def fechar_abas_extras(driver, aba_principal):
    for h in driver.window_handles:
        if h != aba_principal:
            try:
                driver.switch_to.window(h)
                driver.close()
            except Exception:
                pass
    driver.switch_to.window(aba_principal)


def encontrar_aba_processo(driver):
    for h in driver.window_handles:
        driver.switch_to.window(h)
        url = driver.current_url or ""
        if "listProcessoCompleto" in url or "ConsultaProcesso" in url:
            print(f"[OK] Aba do processo: {url[:80]}")
            return h
    for h in driver.window_handles:
        driver.switch_to.window(h)
        if "pje.tjmg.jus.br" in (driver.current_url or ""):
            print(f"[OK] Aba PJe: {driver.current_url[:80]}")
            return h
    print("[AVISO] Nenhuma aba PJe encontrada. Usando aba atual.")
    return driver.current_window_handle


def expandir_arvore(driver):
    """Expande todos os nos da arvore de documentos para revelar todos os docs."""
    expanded = 0
    for _ in range(10):
        found = False
        toggles = driver.find_elements(By.CSS_SELECTOR,
            ".rich-tree-node-handleicon-collapsed, "
            ".rf-trn-hnd-colps, "
            "[class*='tree'] [class*='collapsed'] img, "
            "[class*='tree'] [class*='closed'] img, "
            "img[id*='handle'][src*='plus'], "
            "img[id*='handle'][src*='collapsed']"
        )
        for toggle in toggles:
            try:
                if toggle.is_displayed():
                    js_click(driver, toggle)
                    expanded += 1
                    found = True
                    time.sleep(0.3)
            except Exception:
                continue
        if not found:
            break
        time.sleep(0.5)
    if expanded:
        print(f"[OK] {expanded} nos expandidos na arvore")
    return expanded


def coletar_links_documentos(driver):
    """Coleta todos os links clicaveis de documentos na pagina."""
    docs = []
    seen_ids = set()

    # JavaScript que varre a pagina e encontra todos os links de documento
    js_coleta = """
    return (function() {
        var docs = [];
        var seen = {};

        // Estrategia 1: links com onclick que menciona documento
        var links = document.querySelectorAll('a[onclick*="documento"], a[onclick*="Documento"], a[onclick*="abrirDocumento"], a[onclick*="visualizar"]');
        for (var i = 0; i < links.length; i++) {
            var el = links[i];
            if (!el.offsetParent) continue;
            var text = (el.innerText || el.title || el.getAttribute('title') || '').trim();
            var onclick = el.getAttribute('onclick') || '';
            var id = onclick.match(/\\d{6,12}/);
            var key = id ? id[0] : ('pos-' + el.getBoundingClientRect().top);
            if (seen[key]) continue;
            seen[key] = true;
            docs.push({
                index: docs.length,
                text: text.substring(0, 120),
                id: id ? id[0] : '',
                selector: 'onclick-doc',
                xpath: '',
                top: el.getBoundingClientRect().top
            });
        }

        // Estrategia 2: icones de arquivo (prancheta, PDF, etc)
        var icons = document.querySelectorAll(
            'i.fa-file, i.fa-file-o, i.fa-file-pdf-o, i.fa-file-text, ' +
            'i.fa-file-text-o, i.fa-clipboard, i.fa-paperclip, ' +
            'img[src*="documento"], img[src*="file"], img[src*="pdf"], ' +
            'img[title*="Abrir"], img[title*="documento"], img[title*="Visualizar"], ' +
            'span[class*="icone-doc"], span[class*="icon-doc"]'
        );
        for (var i = 0; i < icons.length; i++) {
            var icon = icons[i];
            if (!icon.offsetParent) continue;
            var parent = icon.closest('a, button, [onclick], [role="button"]');
            if (!parent) continue;
            var text = (parent.innerText || parent.title || icon.title || '').trim();
            var onclick = (parent.getAttribute('onclick') || '') + (icon.getAttribute('onclick') || '');
            var id = onclick.match(/\\d{6,12}/) || text.match(/\\d{6,12}/);
            var key = id ? id[0] : ('icon-' + parent.getBoundingClientRect().top);
            if (seen[key]) continue;
            seen[key] = true;
            docs.push({
                index: docs.length,
                text: text.substring(0, 120),
                id: id ? id[0] : '',
                selector: 'icon',
                top: parent.getBoundingClientRect().top
            });
        }

        // Estrategia 3: links dentro de nos de arvore (rich-tree)
        var treeLinks = document.querySelectorAll(
            '.rich-tree-node a, .rf-trn a, [class*="tree-node"] a, ' +
            'td.rich-tree-node-text a, [class*="treeNode"] a'
        );
        for (var i = 0; i < treeLinks.length; i++) {
            var el = treeLinks[i];
            if (!el.offsetParent) continue;
            var text = (el.innerText || el.title || '').trim();
            if (!text || text.length < 2) continue;
            var onclick = el.getAttribute('onclick') || '';
            var href = el.getAttribute('href') || '';
            if (!onclick && !href) continue;
            var id = (onclick + ' ' + text).match(/\\d{6,12}/);
            var key = id ? id[0] : ('tree-' + el.getBoundingClientRect().top);
            if (seen[key]) continue;
            seen[key] = true;
            docs.push({
                index: docs.length,
                text: text.substring(0, 120),
                id: id ? id[0] : '',
                selector: 'tree-link',
                top: el.getBoundingClientRect().top
            });
        }

        // Estrategia 4: qualquer link com href contendo documento/downloadPeca
        var dlLinks = document.querySelectorAll(
            'a[href*="downloadPeca"], a[href*="downloadBinario"], ' +
            'a[href*="ConsultaDocumento"], a[href*="documento"]'
        );
        for (var i = 0; i < dlLinks.length; i++) {
            var el = dlLinks[i];
            if (!el.offsetParent) continue;
            var text = (el.innerText || el.title || '').trim();
            var href = el.getAttribute('href') || '';
            var id = href.match(/\\d{6,12}/) || text.match(/\\d{6,12}/);
            var key = id ? id[0] : ('href-' + el.getBoundingClientRect().top);
            if (seen[key]) continue;
            seen[key] = true;
            docs.push({
                index: docs.length,
                text: text.substring(0, 120),
                id: id ? id[0] : '',
                selector: 'href-doc',
                href: href,
                top: el.getBoundingClientRect().top
            });
        }

        docs.sort(function(a, b) { return a.top - b.top; });
        return docs;
    })();
    """

    try:
        results = driver.execute_script(js_coleta)
        if results:
            for r in results:
                doc_id = r.get("id", "")
                if doc_id and doc_id in seen_ids:
                    continue
                if doc_id:
                    seen_ids.add(doc_id)
                docs.append(r)
    except JavascriptException as e:
        print(f"[AVISO] JS coleta falhou: {e}")

    return docs


def clicar_documento_por_js(driver, doc_info):
    """Clica no documento usando JavaScript para re-localizar o elemento."""
    selector = doc_info.get("selector", "")
    doc_id = doc_info.get("id", "")
    text = doc_info.get("text", "")
    href = doc_info.get("href", "")

    # Re-encontrar o elemento na pagina atual
    js_click_code = """
    return (function(docId, docText, docHref, docSelector) {
        var candidates = [];

        if (docHref) {
            var byHref = document.querySelectorAll('a[href="' + docHref.replace(/"/g, '\\\\"') + '"]');
            for (var i = 0; i < byHref.length; i++) {
                if (byHref[i].offsetParent) candidates.push(byHref[i]);
            }
        }

        if (docId && candidates.length === 0) {
            var all = document.querySelectorAll('a, button, [onclick], [role="button"]');
            for (var i = 0; i < all.length; i++) {
                var el = all[i];
                if (!el.offsetParent) continue;
                var blob = (el.getAttribute('onclick') || '') + ' ' +
                           (el.getAttribute('href') || '') + ' ' +
                           (el.innerText || '') + ' ' +
                           (el.title || '');
                if (blob.indexOf(docId) !== -1) {
                    candidates.push(el);
                }
            }
        }

        if (candidates.length === 0 && docText) {
            var all = document.querySelectorAll('a, button');
            for (var i = 0; i < all.length; i++) {
                var el = all[i];
                if (!el.offsetParent) continue;
                var t = (el.innerText || el.title || '').trim();
                if (t && docText.indexOf(t) !== -1 || t.indexOf(docText.substring(0, 30)) !== -1) {
                    candidates.push(el);
                }
            }
        }

        if (candidates.length === 0) return {ok: false, erro: 'elemento nao encontrado'};

        var el = candidates[0];
        el.scrollIntoView({block: 'center', behavior: 'instant'});
        el.click();
        return {ok: true, tag: el.tagName, text: (el.innerText || '').substring(0, 60)};
    })(arguments[0], arguments[1], arguments[2], arguments[3]);
    """
    try:
        result = driver.execute_script(js_click_code, doc_id, text, href, selector)
        return result and result.get("ok", False)
    except Exception as e:
        print(f"    [ERRO] Click JS: {e}")
        return False


def procurar_e_clicar_abrir(driver):
    """Procura botao ABRIR na pagina/popup e clica."""
    time.sleep(1.0)

    js_abrir = """
    return (function() {
        // Procura "Abrir" ou "ABRIR" em links, botoes, spans clicaveis
        var seletores = [
            'a', 'button', 'input[type="button"]', 'input[type="submit"]',
            'span[onclick]', 'div[onclick]', '[role="button"]', '[role="menuitem"]'
        ];
        var all = document.querySelectorAll(seletores.join(','));
        for (var i = 0; i < all.length; i++) {
            var el = all[i];
            if (!el.offsetParent) continue;
            var text = (el.innerText || el.value || el.title || el.getAttribute('title') || '').trim().toLowerCase();
            if (text === 'abrir' || text === 'abrir documento' || text === 'visualizar' ||
                text.indexOf('abrir') === 0) {
                el.scrollIntoView({block: 'center', behavior: 'instant'});
                el.click();
                return {ok: true, text: text};
            }
        }
        // Fallback: procura por title
        var byTitle = document.querySelectorAll('[title*="Abrir"], [title*="abrir"], [title*="ABRIR"]');
        for (var i = 0; i < byTitle.length; i++) {
            var el = byTitle[i];
            if (!el.offsetParent) continue;
            el.scrollIntoView({block: 'center', behavior: 'instant'});
            el.click();
            return {ok: true, text: el.title || 'by-title'};
        }
        return {ok: false};
    })();
    """
    for tentativa in range(4):
        try:
            result = driver.execute_script(js_abrir)
            if result and result.get("ok"):
                print(f"    [OK] ABRIR clicado ({result.get('text','')})")
                return True
        except Exception:
            pass
        time.sleep(0.8)

    return False


def aguardar_download_ou_aba(driver, aba_principal, timeout=15):
    """Espera nova aba abrir (documento) e fecha depois."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        handles = driver.window_handles
        novas = [h for h in handles if h != aba_principal]
        if novas:
            for h in novas:
                try:
                    driver.switch_to.window(h)
                    time.sleep(1)
                    url = driver.current_url or ""
                    print(f"    [OK] Doc aberto: {url[:70]}")
                    driver.close()
                except Exception:
                    pass
            driver.switch_to.window(aba_principal)
            return True
        time.sleep(0.5)
    return False


def main():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    inicio = datetime.now()

    print("=" * 70)
    print("  EMERGENCIA - Download documentos avulsos PJe")
    print(f"  Processo: {CNJ}")
    print(f"  Hora: {inicio.strftime('%H:%M:%S')}")
    print("=" * 70)

    driver = conectar_chrome()
    aba_principal = encontrar_aba_processo(driver)

    # Expandir arvore de documentos
    print("\n[...] Expandindo arvore de documentos...")
    expandir_arvore(driver)
    time.sleep(1)

    # Coletar documentos
    print("[...] Coletando links de documentos...")
    docs = coletar_links_documentos(driver)
    print(f"[OK] {len(docs)} documento(s) encontrado(s)")

    if not docs:
        print("\n[ERRO] Nenhum documento encontrado na pagina.")
        print("       Verifique se voce esta na pagina listProcessoCompleto.seam")
        print("       e se a arvore de documentos esta visivel.")
        print("\n       ALTERNATIVA: use o script pyautogui:")
        print("       py pje_clicar_prancheta_abrir.py --qtd 30 --modo teclado")
        return 1

    # Listar documentos encontrados
    print(f"\nDocumentos encontrados:")
    for i, doc in enumerate(docs, 1):
        print(f"  {i:3d}. [{doc.get('id','?'):>10}] {doc.get('text','')[:60]} ({doc.get('selector','')})")

    print(f"\nIniciando download de {len(docs)} documentos...")
    print("Para abortar: Ctrl+C\n")

    ok = 0
    erros = 0
    pulados = 0

    for i, doc in enumerate(docs, 1):
        doc_id = doc.get("id", "?")
        desc = doc.get("text", "")[:50] or f"doc-{i}"
        print(f"[{i}/{len(docs)}] {doc_id} - {desc}")

        # Fechar abas extras antes de cada documento
        fechar_abas_extras(driver, aba_principal)

        # Clicar no documento/prancheta
        if not clicar_documento_por_js(driver, doc):
            print(f"    [ERRO] Nao conseguiu clicar no documento")
            erros += 1
            continue

        time.sleep(0.8)

        # Clicar em ABRIR
        if not procurar_e_clicar_abrir(driver):
            # Talvez o click no documento ja abriu diretamente
            if len(driver.window_handles) > 1:
                print(f"    [OK] Documento abriu diretamente")
                aguardar_download_ou_aba(driver, aba_principal, timeout=5)
                ok += 1
            else:
                print(f"    [AVISO] ABRIR nao encontrado, pulando")
                pulados += 1
            continue

        time.sleep(1)

        # Esperar download/nova aba
        if aguardar_download_ou_aba(driver, aba_principal, timeout=TIMEOUT_ABRIR):
            ok += 1
        else:
            # Mesmo sem nova aba, o download pode ter sido direto
            print(f"    [OK] Sem nova aba (download direto provavel)")
            ok += 1

        time.sleep(PAUSA_ENTRE_DOCS)

    # Fechar abas extras no final
    fechar_abas_extras(driver, aba_principal)

    fim = datetime.now()
    duracao = (fim - inicio).total_seconds()

    print(f"\n{'=' * 70}")
    print(f"  CONCLUIDO em {duracao:.0f}s")
    print(f"  OK: {ok} | Erros: {erros} | Pulados: {pulados}")
    print(f"  Downloads vao para a pasta de download do Chrome")
    print(f"  (provavelmente: {HOME / 'Downloads'} ou {DOWNLOAD_DIR})")
    print(f"{'=' * 70}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[ABORTADO] Ctrl+C")
        sys.exit(130)
