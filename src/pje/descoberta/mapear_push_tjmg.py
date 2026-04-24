#!/usr/bin/env python3
"""
SCRIPT 2 — Push PJe TJMG
Controla o Safari já logado via AppleScript/JavaScript.
Zero dependências externas. Só stdlib.

python mapear_push_tjmg.py
"""
import csv, re, subprocess, time
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
DATA_COLETA = datetime.now().strftime("%Y-%m-%d %H:%M")
CNJ_RE = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')
PUSH_URL = "https://pje.tjmg.jus.br/pje/Push/listView.seam"
COMARCAS = {
    "0005":"Acucena","0024":"Belo Horizonte","0042":"Arcos","0059":"Barroso",
    "0089":"Bracopolis","0105":"Governador Valadares","0112":"Campo Belo",
    "0134":"Governador Valadares","0184":"Conselheiro Pena","0194":"Coronel Fabriciano",
    "0231":"Ribeirao das Neves","0245":"Santa Luzia","0309":"Ibiapim","0329":"Itamogi",
    "0344":"Ituiutaba","0362":"Joao Monlevade","0396":"Mantena","0471":"Para de Minas",
    "0627":"Taiobeiras","0674":"Bom Despacho","0680":"Taiobeiras","0694":"Tres Pontas",
    "0701":"Uberaba","0702":"Uberlandia",
}

def js(code: str) -> str:
    code_escaped = code.replace("\\", "\\\\").replace('"', '\\"')
    script = f'tell application "Safari" to do JavaScript "{code_escaped}" in current tab of front window'
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return (r.stdout or "").strip()

def log(msg, level="INFO"):
    p = {"OK": "+", "ERRO": "X", "AVISO": "!"}.get(level, "i")
    print(f"  [{datetime.now().strftime('%H:%M:%S')}] {p} {msg}", flush=True)

def get_comarca(cnj):
    return COMARCAS.get(cnj[-4:], f"Foro {cnj[-4:]}")

def extrair_cnjs_push_pagina() -> list[str]:
    return CNJ_RE.findall(js('''
        (function(){
            var r=[];
            document.querySelectorAll(
                "table[id*=dataTableProcessosCadastrados] tbody tr"
            ).forEach(function(tr){
                var cells=tr.querySelectorAll("td");
                if(cells[1]) r.push(cells[1].innerText.trim());
            });
            return r.join("|");
        })()
    '''))

def proxima_pagina() -> bool:
    resultado = js('''
        (function(){
            var ds=document.querySelector(
                "div[id*=scrollerListaProcessosCadastrados],div.rich-datascr"
            );
            if(!ds) return "false";
            var act=ds.querySelector("td.rich-datascr-act");
            if(!act) return "false";
            var cur=parseInt(act.innerText.trim());
            var inacts=ds.querySelectorAll("td.rich-datascr-inact");
            for(var i=0;i<inacts.length;i++){
                if(parseInt(inacts[i].innerText.trim())===cur+1){
                    inacts[i].click(); return "true";
                }
            }
            return "false";
        })()
    ''')
    if resultado == "true":
        time.sleep(3)
        return True
    return False

def mapear_push(max_paginas=100) -> list[dict]:
    log("Abrindo aba PUSH...")
    js(f'window.location.href = "{PUSH_URL}"')
    time.sleep(5)

    mapa = {}
    pag = 1
    while pag <= max_paginas:
        cnjs = extrair_cnjs_push_pagina()
        novos = sum(1 for c in cnjs if c not in mapa)
        for c in cnjs:
            if c not in mapa:
                mapa[c] = pag
        log(f"  Página {pag}: {len(cnjs)} CNJs ({novos} novos, total {len(mapa)})")
        if not cnjs:
            break
        if not proxima_pagina():
            break
        pag += 1

    log(f"PUSH: {len(mapa)} processos em {pag} páginas", "OK")

    linhas = []
    for cnj, pagina in sorted(mapa.items()):
        linhas.append({"numero_cnj": cnj, "origem_painel": "push",
                       "pagina_push": pagina, "comarca": get_comarca(cnj),
                       "data_coleta": DATA_COLETA})
    return linhas

def main():
    print()
    print("=" * 60)
    print("  MAPEAR PUSH — Safari já logado")
    print("=" * 60)

    url_atual = js("window.location.href")
    if "pje.tjmg.jus.br" not in url_atual:
        print("  Safari não está no PJe. Abra e logue primeiro.")
        return

    dados = mapear_push()

    path = OUTPUT_DIR / "push_raw.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["numero_cnj","origem_painel","pagina_push","comarca","data_coleta"])
        w.writeheader()
        w.writerows(dados)
    log(f"Salvo: {path} ({len(dados)} CNJs)", "OK")

    por_comarca: dict[str,int] = {}
    for d in dados:
        por_comarca[d["comarca"]] = por_comarca.get(d["comarca"], 0) + 1

    print()
    print(f"  Total: {len(dados)} processos na PUSH")
    for comarca, qtd in sorted(por_comarca.items(), key=lambda x: -x[1]):
        print(f"    {comarca}: {qtd}")
    print()
    print("  PRÓXIMO: python cruzar_listas_processos.py")

if __name__ == "__main__":
    main()
