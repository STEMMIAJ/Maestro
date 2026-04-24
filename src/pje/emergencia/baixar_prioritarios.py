#!/usr/bin/env python3
"""
EMERGENCIA - Baixa documentos PRIORITARIOS do processo 5030880-86.2024.8.13.0105
via Chrome debug port. Clica na prancheta de cada doc e depois ABRIR.

Uso no CMD do Windows:
  py \\Mac\Home\stemmia-forense\src\pje\\baixar_prioritarios.py

Pre-requisitos:
  - Chrome com --remote-debugging-port=9223
  - Logado no PJe
  - Pagina do processo aberta em listProcessoCompleto.seam
  - Selenium: py -m pip install selenium
"""

import os
import sys
import time
import urllib.request
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import (
        StaleElementReferenceException,
        JavascriptException,
        WebDriverException,
        NoAlertPresentException,
        UnexpectedAlertPresentException,
    )
except ImportError:
    print("ERRO: Selenium nao instalado.")
    print("Rode:  py -m pip install selenium")
    sys.exit(1)

# ── Documentos prioritarios (ordem de importancia para a pericia) ──
PRIORITARIOS = [
    ("10323492348", "Peticao Inicial"),
    ("10323493105", "Prontuario 1-14"),
    ("10323510374", "Prontuario 15-28"),
    ("10323515264", "Docs Medicos 1"),
    ("10323490152", "Docs Medicos 2"),
    ("10555375620", "Decisao Nomeacao Perito"),
    ("10555414547", "Dados Nomeacao Jesus"),
    ("10555399172", "Dados Complementares Jesus"),
    ("10323506485", "BO REDS"),
    ("10323497984", "Fotos Lesao Juarez"),
    ("10323486913", "Fotos Local Acidente"),
    ("10453335977", "Impugnacao"),
    ("10632051928", "Reagendamento Pericia"),
    ("10624374734", "Reagendamento Pericia Medica"),
    ("10587693301", "Agendamento Pericia"),
    ("10323511880", "Comprovante Fisioterapias"),
    ("10323515015", "Comprovante Concerto Moto"),
    ("10323481712", "Video"),
    ("10331570621", "Manifestacao com procuracao"),
    ("10331565184", "Declaracao Hipossuficiencia"),
    ("10331550810", "Procuracao autor"),
    ("10326905474", "Despacho inicial"),
    ("10397991170", "Despacho"),
    ("10399252962", "Citacao"),
]

# Todos os 77 documentos (para --todos)
TODOS_DOCS = [
    ("10644658587", "Manifestacao Advocacia Publica mar2026"),
    ("10644656451", "Procuracao mar2026"),
    ("10639991496", "Manifestacao mar2026"),
    ("10639147831", "Juntada Mandado mar2026"),
    ("10635151978", "Intimacao fev2026"),
    ("10634528306", "Certidao Remessa fev2026"),
    ("10634531634", "Intimacao fev2026b"),
    ("10632051928", "Reagendamento Pericia"),
    ("10631384157", "Manifestacao Advocacia Publica fev2026"),
    ("10631383016", "Procuracao PGM 2026"),
    ("10626864279", "Intimacao Despacho fev2026"),
    ("10625491752", "Despacho fev2026"),
    ("10624382032", "Intimacao fev2026c"),
    ("10624374734", "Reagendamento Pericia Medica"),
    ("10600138317", "Manifestacao Advocacia Publica dez2025"),
    ("10600007297", "Juntada Mandado dez2025"),
    ("10600008884", "Mandado Digitalizado Juarez"),
    ("10600006051", "Certidao Oficial Justica"),
    ("10591116747", "Intimacao dez2025"),
    ("10590930981", "Certidao Remessa dez2025"),
    ("10590930633", "Intimacao dez2025b"),
    ("10587693301", "Agendamento Pericia"),
    ("10585612686", "Intimacao nov2025"),
    ("10582196449", "Manifestacao Advocacia Publica nov2025"),
    ("10573541251", "Manifestacao nov2025"),
    ("10555824473", "Intimacao out2025"),
    ("10555375620", "Decisao Nomeacao Perito"),
    ("10555414547", "Dados Nomeacao Jesus"),
    ("10555399172", "Dados Complementares Jesus"),
    ("10554435114", "Certidao Decurso Prazo"),
    ("10551092652", "Manifestacao Advocacia Publica out2025"),
    ("10551091202", "Documento Comprovacao"),
    ("10522557447", "Intimacao ago2025"),
    ("10519669785", "Manifestacao Advocacia Publica ago2025"),
    ("10516230607", "Manifestacao ago2025"),
    ("10506058119", "Intimacao jul2025"),
    ("10504471239", "Decisao Nomeacao Otavio"),
    ("10504471242", "Outros Otavio Teixeira"),
    ("10504471244", "Nomeacao Otavio"),
    ("10501373779", "Certidao Conclusao jul2025"),
    ("10501400708", "Juntada Recusa Perito"),
    ("10501366294", "Recusa Perito"),
    ("10499570663", "Intimacao jul2025b"),
    ("10498285515", "Decisao Nomeacao Luiz"),
    ("10498394191", "Nomeacao Luiz Campos"),
    ("10498430212", "Outros Luiz Campos"),
    ("10486555055", "Certidao Conclusao jul2025b"),
    ("10484598949", "Manifestacao Advocacia Publica jul2025"),
    ("10484834477", "Procuracao PGM jul2025"),
    ("10465992107", "Manifestacao jun2025"),
    ("10453784846", "Intimacao mai2025"),
    ("10453335977", "Impugnacao"),
    ("10435137344", "Intimacao abr2025"),
    ("10433671881", "Manifestacao Advocacia Publica abr2025"),
    ("10433678001", "Procuracao PGM abr2025"),
    ("10399252962", "Citacao"),
    ("10397991170", "Despacho fev2025"),
    ("10332367079", "Certidao Conclusao out2024"),
    ("10331570621", "Manifestacao out2024"),
    ("10331565184", "Declaracao Hipossuficiencia"),
    ("10331550810", "Procuracao autor"),
    ("10327850926", "Intimacao out2024"),
    ("10326905474", "Despacho out2024"),
    ("10324196311", "Certidao Triagem"),
    ("10323492348", "Peticao Inicial"),
    ("10323488611", "Documentos Pessoais"),
    ("10323483797", "Comprovante Residencia"),
    ("10323506485", "BO REDS"),
    ("10323515264", "Docs Medicos 1"),
    ("10323490152", "Docs Medicos 2"),
    ("10323486913", "Fotos Local Acidente"),
    ("10323511880", "Comprovante Fisioterapias"),
    ("10323515015", "Comprovante Concerto Moto"),
    ("10323497984", "Fotos Lesao Juarez"),
    ("10323493105", "Prontuario 1-14"),
    ("10323510374", "Prontuario 15-28"),
    ("10323481712", "Video"),
]


def conectar():
    for porta in [9223, 9222]:
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{porta}/json/version", timeout=2
            ) as r:
                if "Browser" in r.read().decode():
                    opts = Options()
                    opts.add_experimental_option(
                        "debuggerAddress", f"127.0.0.1:{porta}"
                    )
                    d = webdriver.Chrome(options=opts)
                    print(f"[OK] Chrome porta {porta}")
                    return d
        except Exception:
            pass
    print("[ERRO] Chrome debug nao encontrado.")
    print("  1. Feche o Chrome")
    print('  2. Abra: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9223')
    print("  3. Logue no PJe")
    print("  4. Rode este script novamente")
    sys.exit(1)


def encontrar_aba(driver):
    for h in driver.window_handles:
        driver.switch_to.window(h)
        url = driver.current_url or ""
        if "listProcessoCompleto" in url or "ConsultaProcesso" in url:
            print(f"[OK] Aba processo: ...{url[-50:]}")
            return h
    for h in driver.window_handles:
        driver.switch_to.window(h)
        if "pje.tjmg.jus.br" in (driver.current_url or ""):
            print(f"[OK] Aba PJe: ...{(driver.current_url or '')[-50:]}")
            return h
    return driver.current_window_handle


def fechar_extras(driver, principal):
    for h in list(driver.window_handles):
        if h != principal:
            try:
                driver.switch_to.window(h)
                driver.close()
            except Exception:
                pass
    try:
        driver.switch_to.window(principal)
    except Exception:
        pass


def clicar_doc_por_id(driver, doc_id):
    """Encontra e clica no documento pelo ID numerico."""
    js = """
    return (function(docId) {
        // Busca em TODOS os elementos visiveis que contenham o ID
        var all = document.querySelectorAll('a, span, td, div, button, [onclick]');
        var candidatos = [];
        for (var i = 0; i < all.length; i++) {
            var el = all[i];
            if (!el.offsetParent && el.offsetWidth === 0) continue;

            var texto = (el.innerText || el.textContent || '').trim();
            var onclick = el.getAttribute('onclick') || '';
            var href = el.getAttribute('href') || '';
            var title = el.getAttribute('title') || '';
            var blob = texto + ' ' + onclick + ' ' + href + ' ' + title;

            if (blob.indexOf(docId) === -1) continue;

            // Encontrou elemento com o ID do documento
            // Procura o link/botao clicavel mais proximo
            var clicavel = el.closest('a, button, [onclick], [role="button"]') || el;
            if (clicavel.tagName === 'TD' || clicavel.tagName === 'DIV' || clicavel.tagName === 'SPAN') {
                // Procura link dentro
                var link = el.querySelector('a, button, [onclick]');
                if (link) clicavel = link;
            }

            candidatos.push({
                tag: clicavel.tagName,
                text: (clicavel.innerText || '').substring(0, 80),
                rect: clicavel.getBoundingClientRect()
            });

            clicavel.scrollIntoView({block: 'center', behavior: 'instant'});
            clicavel.click();
            return {ok: true, tag: clicavel.tagName, text: (clicavel.innerText || '').substring(0, 60)};
        }
        return {ok: false, candidatos: candidatos.length};
    })(arguments[0]);
    """
    try:
        r = driver.execute_script(js, doc_id)
        return r and r.get("ok", False)
    except Exception as e:
        print(f"    JS erro: {e}")
        return False


def procurar_abrir(driver):
    """Procura e clica em ABRIR."""
    time.sleep(1.2)
    js = """
    return (function() {
        // Busca ampla por "Abrir" em qualquer elemento clicavel
        var seletores = 'a, button, input[type="button"], input[type="submit"], span[onclick], [role="button"], [role="menuitem"], [role="link"]';
        var all = document.querySelectorAll(seletores);
        for (var i = 0; i < all.length; i++) {
            var el = all[i];
            if (!el.offsetParent && el.offsetWidth === 0) continue;
            var t = (el.innerText || el.value || el.title || el.getAttribute('title') || '').trim();
            var tl = t.toLowerCase();
            if (tl === 'abrir' || tl === 'abrir documento' || tl.indexOf('abrir') === 0 || tl === 'visualizar documento') {
                el.scrollIntoView({block: 'center', behavior: 'instant'});
                el.click();
                return {ok: true, text: t};
            }
        }
        // Fallback: title contendo Abrir
        var byTitle = document.querySelectorAll('[title*="Abrir"], [title*="abrir"], [title*="ABRIR"], [title*="Visualizar"]');
        for (var i = 0; i < byTitle.length; i++) {
            var el = byTitle[i];
            if (!el.offsetParent && el.offsetWidth === 0) continue;
            el.scrollIntoView({block: 'center', behavior: 'instant'});
            el.click();
            return {ok: true, text: el.title || 'title-match'};
        }
        // Fallback 2: link com href de download
        var dlLinks = document.querySelectorAll('a[href*="downloadPeca"], a[href*="downloadBinario"], a[href*="ConsultaDocumento"]');
        for (var i = 0; i < dlLinks.length; i++) {
            var el = dlLinks[i];
            if (!el.offsetParent && el.offsetWidth === 0) continue;
            el.scrollIntoView({block: 'center', behavior: 'instant'});
            el.click();
            return {ok: true, text: 'download-link'};
        }
        return {ok: false};
    })();
    """
    for tentativa in range(5):
        try:
            r = driver.execute_script(js)
            if r and r.get("ok"):
                return True
        except Exception:
            pass
        time.sleep(0.7)
    return False


def aceitar_alert(driver, timeout=3):
    """Aceita alert/confirm do JavaScript (clica OK). Retorna True se havia alert."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            alert = driver.switch_to.alert
            texto = alert.text
            print(f"    [ALERT] '{texto}' -> OK")
            alert.accept()
            return True
        except NoAlertPresentException:
            time.sleep(0.3)
        except Exception:
            time.sleep(0.3)
    return False


def baixar_doc(driver, doc_id, desc, indice, total, aba_principal):
    """Fluxo: clicar prancheta -> clicar ABRIR -> aceitar OK no dialog -> esperar download."""
    print(f"\n[{indice}/{total}] {doc_id} - {desc}")

    fechar_extras(driver, aba_principal)
    handles_antes = set(driver.window_handles)

    # Passo 1: clicar no documento (prancheta)
    if not clicar_doc_por_id(driver, doc_id):
        print(f"    [ERRO] Doc {doc_id} nao encontrado na pagina")
        return False

    time.sleep(0.8)

    # Checar se ja apareceu alert apos clicar prancheta
    aceitar_alert(driver, timeout=1)

    # Passo 2: clicar ABRIR
    abriu = procurar_abrir(driver)

    # Passo 3: aceitar o dialog "Confirma o download do documento?" -> OK
    time.sleep(0.5)
    alert_ok = aceitar_alert(driver, timeout=3)
    if alert_ok:
        print(f"    [OK] Download confirmado")

    # Esperar download iniciar
    time.sleep(2)

    # Checar se abriu nova aba
    handles_agora = set(driver.window_handles)
    novas = handles_agora - handles_antes

    if novas:
        for h in novas:
            try:
                driver.switch_to.window(h)
                # Pode ter alert na nova aba tambem
                aceitar_alert(driver, timeout=1)
                time.sleep(1.5)
                url = driver.current_url or ""
                print(f"    [OK] Aberto: ...{url[-60:]}")
                driver.close()
            except Exception:
                pass
        driver.switch_to.window(aba_principal)
        return True
    elif abriu or alert_ok:
        print(f"    [OK] Download direto (sem nova aba)")
        time.sleep(1)
        fechar_extras(driver, aba_principal)
        return True
    else:
        print(f"    [AVISO] ABRIR nao encontrado — tente manualmente este doc")
        return False


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--todos", action="store_true", help="Baixar todos os 77 documentos")
    p.add_argument("--a-partir-de", type=int, default=1, help="Comecar do documento N")
    p.add_argument("--pausa", type=float, default=1.5, help="Pausa entre documentos (seg)")
    args = p.parse_args()

    docs = TODOS_DOCS if args.todos else PRIORITARIOS
    if args.a_partir_de > 1:
        docs = docs[args.a_partir_de - 1:]

    print("=" * 70)
    print("  EMERGENCIA - Baixar documentos processo 5030880-86.2024.8.13.0105")
    print(f"  Modo: {'TODOS (77 docs)' if args.todos else 'PRIORITARIOS (24 docs)'}")
    print(f"  A partir de: #{args.a_partir_de}")
    print("=" * 70)
    print()
    print("  Os documentos vao para a pasta de Downloads do Chrome.")
    print("  Ctrl+C para abortar a qualquer momento.")
    print()

    driver = conectar()
    aba = encontrar_aba(driver)

    ok = 0
    erros = 0
    total = len(docs)

    for i, (doc_id, desc) in enumerate(docs, args.a_partir_de):
        try:
            if baixar_doc(driver, doc_id, desc, i, total + args.a_partir_de - 1, aba):
                ok += 1
            else:
                erros += 1
        except KeyboardInterrupt:
            print("\n\n[ABORTADO] Ctrl+C")
            break
        except WebDriverException as e:
            print(f"    [ERRO] WebDriver: {e}")
            erros += 1
            try:
                fechar_extras(driver, aba)
            except Exception:
                pass
        except Exception as e:
            print(f"    [ERRO] {e}")
            erros += 1

        time.sleep(args.pausa)

    print(f"\n{'=' * 70}")
    print(f"  RESULTADO: {ok} baixados, {erros} erros")
    print(f"  Verifique a pasta de Downloads do Chrome")
    print(f"{'=' * 70}")
    return 0 if erros == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
