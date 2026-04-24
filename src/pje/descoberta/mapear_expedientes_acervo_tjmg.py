#!/usr/bin/env python3
"""
SCRIPT 1 — Expedientes + Acervo PJe TJMG
Controla o Safari já logado via AppleScript/JavaScript.
Zero dependências externas. Só stdlib.

python mapear_expedientes_acervo_tjmg.py
"""
import csv, re, subprocess, time
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
DATA_COLETA = datetime.now().strftime("%Y-%m-%d %H:%M")
CNJ_RE = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')
PAINEL = "https://pje.tjmg.jus.br/pje/Painel/painel_usuario/advogado.seam"

def js(code: str) -> str:
    """Executa JavaScript no Safari e retorna o resultado como string."""
    # Escapa aspas duplas para o osascript
    code_escaped = code.replace("\\", "\\\\").replace('"', '\\"')
    script = f'tell application "Safari" to do JavaScript "{code_escaped}" in current tab of front window'
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return (r.stdout or "").strip()

def log(msg, level="INFO"):
    p = {"OK": "+", "ERRO": "X", "AVISO": "!"}.get(level, "i")
    print(f"  [{datetime.now().strftime('%H:%M:%S')}] {p} {msg}", flush=True)

def aguardar(seg=3):
    time.sleep(seg)

def extrair_cnjs() -> list[str]:
    texto = js("document.body.innerText")
    return list(set(CNJ_RE.findall(texto)))

# ── EXPEDIENTES ──────────────────────────────────────────────

def mapear_expedientes() -> list[dict]:
    log("Abrindo Expedientes...")
    js('window.location.href = "' + PAINEL + '"')
    aguardar(5)
    js('document.getElementById("tabExpedientes_lbl").click()')
    aguardar(3)

    n_n1 = int(js('document.querySelectorAll("div[id*=linhaN1] a[href]").length') or "0")
    log(f"Categorias N1: {n_n1}")

    todos = []

    for idx in range(n_n1):
        # Clica N1 e pega o label
        label_n1 = js(f'''
            var els = document.querySelectorAll("div[id*=linhaN1] a[href]");
            if (els[{idx}]) {{ els[{idx}].click(); els[{idx}].innerText.trim().substring(0,60) }}
            else {{ "skip" }}
        ''')
        if not label_n1 or label_n1 == "skip":
            continue
        log(f"  N1 [{idx+1}/{n_n1}]: {label_n1}")
        aguardar(3)

        # Conta comarcas N2
        n_n2 = int(js('document.querySelectorAll("a[id*=jNp]").length') or "0")
        log(f"    Comarcas N2: {n_n2}")

        if n_n2 == 0:
            # Sem subcategorias — extrai direto
            for cnj in extrair_cnjs():
                todos.append({"numero_cnj": cnj, "categoria": label_n1,
                               "subcategoria": "", "comarca_ou_caixa": "",
                               "data_coleta": DATA_COLETA})
            continue

        for jdx in range(n_n2):
            label_n2 = js(f'''
                var els = document.querySelectorAll("a[id*=jNp]");
                if (els[{jdx}]) {{ els[{jdx}].click(); els[{jdx}].innerText.trim().substring(0,60) }}
                else {{ "skip" }}
            ''')
            if not label_n2 or label_n2 == "skip":
                continue
            log(f"      N2 [{jdx+1}/{n_n2}]: {label_n2}")
            aguardar(4)

            for cnj in extrair_cnjs():
                todos.append({"numero_cnj": cnj, "categoria": label_n1,
                               "subcategoria": label_n2, "comarca_ou_caixa": label_n2,
                               "data_coleta": DATA_COLETA})
            log(f"        {len(extrair_cnjs())} CNJs")

    log(f"Expedientes: {len(todos)} registros", "OK")
    return todos

# ── ACERVO ───────────────────────────────────────────────────

def mapear_acervo() -> list[dict]:
    log("Abrindo Acervo...")
    js('window.location.href = "' + PAINEL + '"')
    aguardar(5)
    js('document.getElementById("tabAcervo_lbl").click()')
    aguardar(3)

    # Conta comarcas (a[id*=trAc][id*=jNd])
    n_comarca = int(js('''
        document.querySelectorAll("a[id*=\\'jNd\\']").length
    ''') or "0")
    # Filtra só trAc
    ids_comarca = js('''
        var r = [];
        document.querySelectorAll("a[href]").forEach(function(a) {
            if (a.id && a.id.indexOf("trAc") >= 0 && a.id.indexOf("jNd") >= 0)
                r.push(a.id);
        });
        r.join("|");
    ''')
    lista_ids = [i for i in ids_comarca.split("|") if i]
    log(f"Comarcas no Acervo: {len(lista_ids)}")

    todos = []

    for idx, comarca_id in enumerate(lista_ids):
        label_comarca = js(f'var a=document.getElementById("{comarca_id}"); a ? a.innerText.trim().substring(0,60) : "?";')
        log(f"  Comarca [{idx+1}/{len(lista_ids)}]: {label_comarca}")

        js(f'var a=document.getElementById("{comarca_id}"); if(a) a.click();')
        aguardar(3)

        # Caixas que aparecem
        ids_caixa = js('''
            var r = [];
            document.querySelectorAll("a[id*=\\'cxItem\\']").forEach(function(a){ r.push(a.id); });
            r.join("|");
        ''')
        lista_caixas = [i for i in ids_caixa.split("|") if i]
        log(f"    Caixas: {len(lista_caixas)}")

        if not lista_caixas:
            for cnj in extrair_cnjs():
                todos.append({"numero_cnj": cnj, "jurisdicao_ou_comarca": label_comarca,
                               "classe_se_visivel": "", "data_coleta": DATA_COLETA})
            continue

        for caixa_id in lista_caixas:
            label_caixa = js(f'var a=document.getElementById("{caixa_id}"); a ? a.innerText.trim().substring(0,40) : "?";')
            log(f"      Caixa: {label_caixa}")

            js(f'var a=document.getElementById("{caixa_id}"); if(a) a.click();')
            aguardar(4)

            cnjs = extrair_cnjs()
            for cnj in cnjs:
                todos.append({"numero_cnj": cnj, "jurisdicao_ou_comarca": label_comarca,
                               "classe_se_visivel": label_caixa, "data_coleta": DATA_COLETA})
            log(f"        {len(cnjs)} CNJs")

    log(f"Acervo: {len(todos)} registros", "OK")
    return todos

# ── SALVAR ───────────────────────────────────────────────────

def salvar(dados, path, campos):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        w.writerows(dados)
    log(f"Salvo: {path} ({len(dados)} linhas)", "OK")

# ── MAIN ─────────────────────────────────────────────────────

def abrir_safari_pje():
    """Abre o Safari e navega pro PJe. Aguarda login se necessário."""
    subprocess.run(["open", "-a", "Safari"], check=False)
    time.sleep(2)
    # Navega pro painel
    subprocess.run(["osascript", "-e",
        f'tell application "Safari" to set URL of current tab of front window to "{PAINEL}"'],
        capture_output=True)
    time.sleep(5)
    # Se caiu no SSO, aguarda login manual
    url = js("window.location.href")
    if "sso.cloud.pje.jus.br" in url or "cas/login" in url:
        print()
        print("  >> FAÇA LOGIN NO PJe AGORA (Safari aberto) <<")
        print("  Aguardando até 3 minutos...")
        for _ in range(60):
            time.sleep(3)
            url = js("window.location.href")
            if "pje.tjmg.jus.br" in url and "sso" not in url and "cas" not in url:
                log("Login detectado!", "OK")
                return True
        log("Timeout de login.", "ERRO")
        return False
    return True

def main():
    print()
    print("=" * 60)
    print("  MAPEAR EXPEDIENTES + ACERVO — PJe TJMG")
    print("=" * 60)

    url_atual = js("window.location.href")
    if "pje.tjmg.jus.br" not in url_atual or "sso" in url_atual:
        if not abrir_safari_pje():
            return

    exp = mapear_expedientes()
    salvar(exp, OUTPUT_DIR / "expedientes_raw.csv",
           ["numero_cnj", "categoria", "subcategoria", "comarca_ou_caixa", "data_coleta"])

    acv = mapear_acervo()
    salvar(acv, OUTPUT_DIR / "acervo_raw.csv",
           ["numero_cnj", "jurisdicao_ou_comarca", "classe_se_visivel", "data_coleta"])

    # Parcial unificado
    vistos = set()
    unif = []
    for r in exp + acv:
        c = r["numero_cnj"]
        if c not in vistos:
            vistos.add(c)
            unif.append({"numero_cnj": c,
                         "em_expedientes": "sim" if r in exp else "nao",
                         "em_acervo": "sim" if r in acv else "nao",
                         "em_push": "pendente", "data_coleta": DATA_COLETA})
    salvar(unif, OUTPUT_DIR / "processos_unificados_parcial.csv",
           ["numero_cnj", "em_expedientes", "em_acervo", "em_push", "data_coleta"])

    print()
    print(f"  Expedientes: {len(set(r['numero_cnj'] for r in exp))} CNJs únicos")
    print(f"  Acervo:      {len(set(r['numero_cnj'] for r in acv))} CNJs únicos")
    print(f"  Saída:       {OUTPUT_DIR}/")
    print()
    print("  PRÓXIMO: python mapear_push_tjmg.py")

if __name__ == "__main__":
    main()
