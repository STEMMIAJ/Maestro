#!/usr/bin/env python3
"""
pipeline_analise.py — Orquestrador: roda os 5 scripts de análise em paralelo.

Consolida resultados em FICHA.json e gera RESUMO-ANALISE.md.

Uso:
    python3 pipeline_analise.py 5002424-62.2025.8.13.0309
    python3 pipeline_analise.py --todos
    python3 pipeline_analise.py --pendentes
"""

from pathlib import Path
import argparse, json, re, subprocess, sys, time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


BASE_DIR = Path(__file__).parent
PROCESSOS_DIR = BASE_DIR / "processos"
RE_CNJ = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")

class C:
    R = "\033[0m"
    B = "\033[1m"
    G = "\033[32m"
    Y = "\033[33m"
    RE = "\033[31m"
    CY = "\033[36m"
    DIM = "\033[2m"


SCRIPTS = [
    {
        "nome": "extrair_partes",
        "script": "extrair_partes.py",
        "saida_json": "PARTES.json",
        "saida_md": "PARTES.md",
        "descricao": "Extração de partes processuais",
    },
    {
        "nome": "classificar_acao",
        "script": "classificar_acao.py",
        "saida_json": "CLASSIFICACAO.json",
        "saida_md": "CLASSIFICACAO.md",
        "descricao": "Classificação do tipo de ação",
    },
    {
        "nome": "detectar_urgencia",
        "script": "detectar_urgencia.py",
        "saida_json": "URGENCIA.json",
        "saida_md": "URGENCIA.md",
        "descricao": "Detecção de prazos e urgência",
    },
    {
        "nome": "resumir_fatos",
        "script": "resumir_fatos.py",
        "saida_json": "TIMELINE.json",
        "saida_md": "TIMELINE.md",
        "descricao": "Linha do tempo cronológica",
    },
    {
        "nome": "classificar_documento",
        "script": "classificar_documento.py",
        "saida_json": "INDICE-DOCUMENTOS.json",
        "saida_md": "INDICE-DOCUMENTOS.md",
        "descricao": "Índice e classificação de documentos",
        "args_extra": ["--indice"],  # Usa --indice em vez de argumento posicional
    },
]


def encontrar_processos_com_texto() -> list[Path]:
    """Encontra todas as pastas de processo com TEXTO-EXTRAIDO.txt."""
    pastas = []

    # Na raiz do analisador
    for p in sorted(BASE_DIR.iterdir()):
        if p.is_dir() and RE_CNJ.search(p.name):
            texto = p / "TEXTO-EXTRAIDO.txt"
            if texto.exists():
                pastas.append(p)

    # Em processos/
    if PROCESSOS_DIR.exists():
        for p in sorted(PROCESSOS_DIR.iterdir()):
            if p.is_dir() and not p.is_symlink():
                texto = p / "TEXTO-EXTRAIDO.txt"
                if texto.exists() and p not in pastas:
                    pastas.append(p)

    return pastas


def encontrar_pasta_processo(identificador: str) -> Path | None:
    """Encontra pasta do processo."""
    p = Path(identificador)
    if p.is_dir():
        return p

    for pasta in BASE_DIR.iterdir():
        if pasta.is_dir() and identificador in pasta.name:
            return pasta

    if PROCESSOS_DIR.exists():
        for pasta in PROCESSOS_DIR.iterdir():
            if pasta.is_dir() and identificador in pasta.name:
                return pasta

    return None


def rodar_script(script_info: dict, pasta: Path) -> dict:
    """Roda um script individual e retorna resultado."""
    script_path = BASE_DIR / script_info["script"]
    inicio = time.time()

    # Determinar argumento
    cnj_match = RE_CNJ.search(pasta.name)
    argumento = cnj_match.group() if cnj_match else str(pasta)

    # Montar comando
    if "args_extra" in script_info:
        cmd = [sys.executable, str(script_path)] + script_info["args_extra"] + [argumento]
    else:
        cmd = [sys.executable, str(script_path), str(pasta)]

    resultado = {
        "nome": script_info["nome"],
        "descricao": script_info["descricao"],
        "status": "pendente",
        "tempo": 0,
        "erro": "",
    }

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(BASE_DIR),
        )

        duracao = time.time() - inicio
        resultado["tempo"] = round(duracao, 2)

        if proc.returncode == 0:
            resultado["status"] = "ok"
            resultado["saida"] = proc.stdout.strip()[-500:]  # Últimas 500 chars
        else:
            resultado["status"] = "erro"
            resultado["erro"] = proc.stderr.strip()[-300:]

    except subprocess.TimeoutExpired:
        resultado["status"] = "timeout"
        resultado["erro"] = "Script excedeu 60 segundos"
        resultado["tempo"] = 60.0
    except Exception as e:
        resultado["status"] = "erro"
        resultado["erro"] = str(e)
        resultado["tempo"] = time.time() - inicio

    return resultado


def gerar_resumo(pasta: Path, resultados: list[dict]) -> str:
    """Gera RESUMO-ANALISE.md consolidando todos os resultados."""
    md = []
    md.append("# RESUMO DA ANÁLISE AUTOMATIZADA\n")
    md.append(f"**Processo:** {pasta.name}")
    md.append(f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    # Status dos scripts
    md.append("## Status da Análise\n")
    md.append("| Script | Status | Tempo |")
    md.append("|--------|--------|-------|")
    for r in resultados:
        status_icon = "OK" if r["status"] == "ok" else "ERRO" if r["status"] == "erro" else "TIMEOUT"
        md.append(f"| {r['descricao']} | {status_icon} | {r['tempo']}s |")
    md.append("")

    # Partes
    partes_path = pasta / "PARTES.json"
    if partes_path.exists():
        try:
            partes = json.loads(partes_path.read_text(encoding="utf-8"))
            md.append("## Partes\n")
            for p in partes.get("polo_ativo", []):
                md.append(f"- **Autor:** {p['nome']}")
            for p in partes.get("polo_passivo", []):
                md.append(f"- **Réu:** {p['nome']}")
            juiz = partes.get("juizo", {}).get("juiz", "")
            if juiz:
                md.append(f"- **Juiz:** {juiz}")
            md.append("")
        except (json.JSONDecodeError, OSError):
            pass

    # Classificação
    class_path = pasta / "CLASSIFICACAO.json"
    if class_path.exists():
        try:
            classificacao = json.loads(class_path.read_text(encoding="utf-8"))
            md.append("## Classificação\n")
            md.append(f"- **Tipo:** {classificacao['tipo']}")
            md.append(f"- **Subtipo:** {classificacao.get('subtipo', '—')}")
            md.append(f"- **Confiança:** {classificacao['confianca']}")
            md.append(f"- **Valor da causa:** {classificacao.get('valor_causa', '—')}")
            md.append(f"- **Justiça gratuita:** {'Sim' if classificacao.get('justica_gratuita') else 'Não'}")
            if classificacao.get("especialidades_medicas"):
                md.append(f"- **Especialidades:** {', '.join(classificacao['especialidades_medicas'])}")
            md.append("")
        except (json.JSONDecodeError, OSError):
            pass

    # Urgência
    urg_path = pasta / "URGENCIA.json"
    if urg_path.exists():
        try:
            urgencia = json.loads(urg_path.read_text(encoding="utf-8"))
            md.append("## Urgência\n")
            md.append(f"- **Classificação:** {urgencia['classificacao']}")
            md.append(f"- **Prazos:** {len(urgencia.get('prazos', []))}")
            for a in urgencia.get("alertas", [])[:3]:
                md.append(f"- {a}")
            md.append(f"- **Recomendação:** {urgencia.get('recomendacao', '')}")
            md.append("")
        except (json.JSONDecodeError, OSError):
            pass

    # Timeline
    tl_path = pasta / "TIMELINE.json"
    if tl_path.exists():
        try:
            timeline = json.loads(tl_path.read_text(encoding="utf-8"))
            md.append("## Linha do Tempo\n")
            md.append(f"- **Total eventos:** {timeline['total_eventos']}")
            md.append(f"- **Relevantes:** {timeline['eventos_relevantes']}")
            periodo = timeline.get("periodo", {})
            if periodo.get("inicio"):
                md.append(f"- **Período:** {periodo['inicio']} a {periodo['fim']}")
            # Top 5 eventos relevantes
            eventos_top = [e for e in timeline.get("eventos", []) if e.get("relevancia", 0) >= 0.4][:5]
            if eventos_top:
                md.append("\n**Eventos principais:**")
                for e in eventos_top:
                    md.append(f"- {e['data']}: {e['texto'][:100]}...")
            md.append("")
        except (json.JSONDecodeError, OSError):
            pass

    # Documentos
    docs_path = pasta / "INDICE-DOCUMENTOS.json"
    if docs_path.exists():
        try:
            docs = json.loads(docs_path.read_text(encoding="utf-8"))
            md.append("## Documentos\n")
            md.append(f"- **Total:** {docs.get('total', 0)} documentos")
            md.append("")
        except (json.JSONDecodeError, OSError):
            pass

    md.append("---")
    md.append(f"*Gerado em {datetime.now().isoformat()} por pipeline_analise.py*")
    md.append("*Scripts rodaram em paralelo (ThreadPoolExecutor, 5 workers)*")

    return "\n".join(md)


def analisar_processo(pasta: Path, verbose: bool = True) -> dict:
    """Analisa um processo completo rodando os 5 scripts em paralelo."""
    cnj = RE_CNJ.search(pasta.name)
    cnj_str = cnj.group() if cnj else pasta.name

    if verbose:
        print(f"\n{C.B}{'='*60}{C.R}")
        print(f"{C.B}ANÁLISE: {cnj_str}{C.R}")
        print(f"{C.B}{'='*60}{C.R}")

    # Verificar TEXTO-EXTRAIDO.txt
    texto_path = pasta / "TEXTO-EXTRAIDO.txt"
    if not texto_path.exists():
        if verbose:
            print(f"  {C.RE}TEXTO-EXTRAIDO.txt não encontrado. Pulando.{C.R}")
        return {"cnj": cnj_str, "status": "sem_texto", "resultados": []}

    inicio_total = time.time()

    # Rodar scripts em paralelo
    resultados = []
    if verbose:
        print(f"  Rodando 5 scripts em paralelo...")

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for script_info in SCRIPTS:
            future = executor.submit(rodar_script, script_info, pasta)
            futures[future] = script_info["nome"]

        for future in as_completed(futures):
            resultado = future.result()
            resultados.append(resultado)
            if verbose:
                nome = resultado["nome"]
                if resultado["status"] == "ok":
                    print(f"    {C.G}OK{C.R}  {resultado['descricao']} ({resultado['tempo']}s)")
                else:
                    print(f"    {C.RE}ERR{C.R} {resultado['descricao']}: {resultado['erro'][:80]}")

    tempo_total = time.time() - inicio_total

    # Gerar resumo consolidado
    resumo_md = gerar_resumo(pasta, resultados)
    resumo_path = pasta / "RESUMO-ANALISE.md"
    resumo_path.write_text(resumo_md, encoding="utf-8")

    # Contagem
    ok = sum(1 for r in resultados if r["status"] == "ok")
    erros = sum(1 for r in resultados if r["status"] != "ok")

    if verbose:
        print(f"\n  {C.G}Concluído:{C.R} {ok}/5 scripts OK, {erros} erros, {tempo_total:.1f}s total")
        print(f"  {C.DIM}→ {resumo_path}{C.R}")

    return {
        "cnj": cnj_str,
        "pasta": str(pasta),
        "status": "ok" if erros == 0 else "parcial" if ok > 0 else "erro",
        "scripts_ok": ok,
        "scripts_erro": erros,
        "tempo_total": round(tempo_total, 2),
        "resultados": resultados,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Orquestrador: roda 5 scripts de análise em paralelo para processos judiciais"
    )
    parser.add_argument("processo", nargs="?", help="Número CNJ ou caminho da pasta")
    parser.add_argument("--todos", action="store_true", help="Analisar todos os processos com TEXTO-EXTRAIDO.txt")
    parser.add_argument("--pendentes", action="store_true", help="Analisar apenas processos sem PARTES.json")
    parser.add_argument("--json-only", action="store_true", help="Imprimir JSON no stdout")
    parser.add_argument("--silencioso", action="store_true", help="Sem output visual")
    args = parser.parse_args()

    verbose = not args.json_only and not args.silencioso

    if args.processo:
        # Modo: processo único
        pasta = encontrar_pasta_processo(args.processo)
        if not pasta:
            print(f"{C.RE}Erro: processo '{args.processo}' não encontrado.{C.R}")
            sys.exit(1)

        resultado = analisar_processo(pasta, verbose)

        if args.json_only:
            print(json.dumps(resultado, ensure_ascii=False, indent=2))

    elif args.todos or args.pendentes:
        # Modo: múltiplos processos
        pastas = encontrar_processos_com_texto()

        if args.pendentes:
            pastas = [p for p in pastas if not (p / "PARTES.json").exists()]

        if not pastas:
            if verbose:
                print(f"{C.Y}Nenhum processo encontrado para análise.{C.R}")
            sys.exit(0)

        if verbose:
            print(f"\n{C.B}PIPELINE DE ANÁLISE — {len(pastas)} processos{C.R}\n")

        inicio_geral = time.time()
        resultados_gerais = []

        for i, pasta in enumerate(pastas, 1):
            if verbose:
                print(f"\n[{i}/{len(pastas)}]", end="")
            resultado = analisar_processo(pasta, verbose)
            resultados_gerais.append(resultado)

        tempo_geral = time.time() - inicio_geral

        # Resumo geral
        ok_total = sum(1 for r in resultados_gerais if r["status"] == "ok")
        parcial = sum(1 for r in resultados_gerais if r["status"] == "parcial")
        erros_total = sum(1 for r in resultados_gerais if r["status"] == "erro")

        if verbose:
            print(f"\n{C.B}{'='*60}{C.R}")
            print(f"{C.B}RESUMO GERAL{C.R}")
            print(f"  Processos analisados: {len(resultados_gerais)}")
            print(f"  {C.G}Completos: {ok_total}{C.R}")
            print(f"  {C.Y}Parciais:  {parcial}{C.R}")
            print(f"  {C.RE}Erros:     {erros_total}{C.R}")
            print(f"  Tempo total: {tempo_geral:.1f}s")
            print(f"{C.B}{'='*60}{C.R}")

        if args.json_only:
            print(json.dumps(resultados_gerais, ensure_ascii=False, indent=2))

    else:
        parser.print_help()
        sys.exit(1)

    # Som de notificação
    if verbose:
        try:
            subprocess.run(
                ["afplay", "/System/Library/Sounds/Glass.aiff"],
                capture_output=True,
                timeout=5,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass


if __name__ == "__main__":
    main()
