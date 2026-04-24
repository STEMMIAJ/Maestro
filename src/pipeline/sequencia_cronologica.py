#!/usr/bin/env python3
"""
Sequência Cronológica Unificada — AJ + AJG
Busca nomeações nos dois sistemas e gera numeração sequencial por data.

Uso:
  python3 sequencia_cronologica.py                # Mostra sequência (sem alterar nada)
  python3 sequencia_cronologica.py --aplicar       # Atualiza FICHA.json de cada processo
  python3 sequencia_cronologica.py --json          # Saída JSON
  python3 sequencia_cronologica.py --offline        # Usa dados locais (FICHA.json) sem consultar AJ/AJG

IMPORTANTE: Sem --aplicar, apenas exibe. Não renomeia pastas (isso é feito pelo gestor-processos.py organizar --confirmar).
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
PROCESSOS_DIR = SCRIPTS_DIR / "processos"


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ", "OK": "✓", "ERRO": "✗", "AVISO": "⚠"}.get(level, "·")
    print(f"  [{ts}] {prefix} {msg}", file=sys.stderr)


def parse_data(data_str):
    """Converte data dd/mm/aaaa para datetime."""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(data_str, fmt)
        except ValueError:
            continue
    return None


def buscar_nomeacoes_script(script_name):
    """Executa um script de consulta e retorna o JSON."""
    script = SCRIPTS_DIR / script_name
    if not script.exists():
        log(f"Script {script_name} não encontrado", "AVISO")
        return []
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--listar", "--json"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
        log(f"Erro ao executar {script_name}: {e}", "ERRO")
    return []


def buscar_nomeacoes_locais():
    """Busca dados de nomeação das FICHA.json locais."""
    nomeacoes = []
    if not PROCESSOS_DIR.exists():
        return nomeacoes

    for pasta in PROCESSOS_DIR.iterdir():
        if not pasta.is_dir() or pasta.is_symlink():
            continue
        ficha_path = pasta / "FICHA.json"
        if not ficha_path.exists():
            continue
        try:
            ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
            nomeacoes.append({
                "numero_processo_cnj": ficha.get("numero_cnj", ""),
                "data_nomeacao": ficha.get("data_nomeacao", ""),
                "unidade": ficha.get("vara", ""),
                "situacao": ficha.get("status", ""),
                "sistema": "AJG" if ficha.get("tribunal", "").startswith("TRF") else "AJ",
                "pasta": str(pasta),
                "ficha": ficha,
            })
        except Exception:
            continue
    return nomeacoes


def unificar_e_ordenar(aj_nomeacoes, ajg_nomeacoes):
    """Une nomeações dos dois sistemas e ordena cronologicamente."""
    todas = []

    for n in aj_nomeacoes:
        n["sistema"] = n.get("sistema", "AJ")
        todas.append(n)

    for n in ajg_nomeacoes:
        n["sistema"] = n.get("sistema", "AJG")
        todas.append(n)

    # Deduplica por CNJ (mesmo processo pode aparecer nos dois)
    vistos = set()
    unicas = []
    for n in todas:
        cnj = n.get("numero_processo_cnj", n.get("numero_processo_raw", ""))
        if cnj and cnj not in vistos:
            vistos.add(cnj)
            unicas.append(n)
        elif not cnj:
            unicas.append(n)

    # Ordena por data de nomeação
    def chave_ordenacao(n):
        data = parse_data(n.get("data_nomeacao", ""))
        return data if data else datetime.max

    unicas.sort(key=chave_ordenacao)
    return unicas


def gerar_sequencia(nomeacoes, filtro_situacao=None):
    """Gera numeração sequencial. Retorna lista com numero_pericia adicionado."""
    # Filtrar apenas aceitas/ativas por padrão
    if filtro_situacao is None:
        filtro_situacao = {"ACEITA", "SERVIÇO PRESTADO", "AGUARDANDO ACEITE"}

    filtradas = [
        n for n in nomeacoes
        if n.get("situacao", "").upper() in filtro_situacao
    ]

    for i, n in enumerate(filtradas, 1):
        n["numero_pericia"] = i

    return filtradas


def aplicar_em_fichas(sequencia):
    """Atualiza o numero_pericia nas FICHA.json locais."""
    if not PROCESSOS_DIR.exists():
        log("Pasta processos/ não existe", "ERRO")
        return 0

    # Montar mapa CNJ → numero_pericia
    mapa = {}
    for n in sequencia:
        cnj = n.get("numero_processo_cnj", n.get("numero_processo_raw", ""))
        if cnj:
            mapa[cnj] = n["numero_pericia"]

    atualizados = 0
    for pasta in PROCESSOS_DIR.iterdir():
        if not pasta.is_dir() or pasta.is_symlink():
            continue
        ficha_path = pasta / "FICHA.json"
        if not ficha_path.exists():
            continue
        try:
            ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
            cnj = ficha.get("numero_cnj", "")
            if cnj in mapa:
                novo_num = mapa[cnj]
                if ficha.get("numero_pericia") != novo_num:
                    ficha["numero_pericia"] = novo_num
                    ficha["atualizado_em"] = datetime.now().isoformat()
                    ficha_path.write_text(
                        json.dumps(ficha, ensure_ascii=False, indent=2),
                        encoding="utf-8"
                    )
                    log(f"Perícia {novo_num:02d} ← {cnj}", "OK")
                    atualizados += 1
        except Exception as e:
            log(f"Erro em {pasta.name}: {e}", "AVISO")

    return atualizados


def formatar_sequencia(sequencia):
    """Mostra a sequência cronológica no terminal."""
    print()
    print("=" * 110)
    print("  SEQUÊNCIA CRONOLÓGICA UNIFICADA — AJ + AJG")
    print("=" * 110)
    print()
    print(f"  {'Nº':<5} {'Sistema':<6} {'Processo CNJ':<25} {'Unidade':<35} {'Data':<12} {'Situação'}")
    print(f"  {'─'*5} {'─'*6} {'─'*25} {'─'*35} {'─'*12} {'─'*20}")

    for n in sequencia:
        num = f"{n.get('numero_pericia', '?'):>3}"
        sistema = n.get("sistema", "?")[:6]
        cnj = n.get("numero_processo_cnj", n.get("numero_processo_raw", "?"))[:25]
        unidade = n.get("unidade", "?")[:35]
        data = n.get("data_nomeacao", "?")[:12]
        sit = n.get("situacao", "?")

        print(f"  {num:<5} {sistema:<6} {cnj:<25} {unidade:<35} {data:<12} {sit}")

    print()
    print(f"  Total: {len(sequencia)} perícia(s) na sequência")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Sequência cronológica unificada AJ + AJG"
    )
    parser.add_argument("--aplicar", action="store_true",
                        help="Atualiza FICHA.json com os números")
    parser.add_argument("--json", action="store_true",
                        help="Saída em JSON")
    parser.add_argument("--offline", action="store_true",
                        help="Usa dados locais (FICHA.json) sem consultar AJ/AJG")
    parser.add_argument("--todas", action="store_true",
                        help="Inclui canceladas e recusadas na sequência")
    args = parser.parse_args()

    if args.offline:
        log("Modo offline — usando FICHA.json locais")
        nomeacoes = buscar_nomeacoes_locais()
        sequencia = gerar_sequencia(nomeacoes,
                                     filtro_situacao=None if args.todas else {"ACEITA", "SERVIÇO PRESTADO", "AGUARDANDO ACEITE"})
    else:
        log("Consultando AJ (TJMG)...")
        aj = buscar_nomeacoes_script("consultar_aj.py")
        log(f"AJ: {len(aj)} nomeações")

        log("Consultando AJG (Justiça Federal)...")
        ajg = buscar_nomeacoes_script("consultar_ajg.py")
        log(f"AJG: {len(ajg)} nomeações")

        nomeacoes = unificar_e_ordenar(aj, ajg)
        log(f"Total unificado (sem duplicatas): {len(nomeacoes)}")

        filtro = None if args.todas else {"ACEITA", "SERVIÇO PRESTADO", "AGUARDANDO ACEITE"}
        sequencia = gerar_sequencia(nomeacoes, filtro_situacao=filtro)

    log(f"Sequência gerada: {len(sequencia)} perícias")

    if args.aplicar:
        atualizados = aplicar_em_fichas(sequencia)
        log(f"FICHA.json atualizadas: {atualizados}", "OK")
        log("Agora rode: python3 gestor-processos.py organizar --confirmar", "INFO")

    if args.json:
        # Limpar campos internos antes de serializar
        saida = []
        for n in sequencia:
            saida.append({
                "numero_pericia": n.get("numero_pericia"),
                "numero_processo_cnj": n.get("numero_processo_cnj", n.get("numero_processo_raw", "")),
                "sistema": n.get("sistema"),
                "unidade": n.get("unidade"),
                "data_nomeacao": n.get("data_nomeacao"),
                "situacao": n.get("situacao"),
            })
        print(json.dumps(saida, ensure_ascii=False, indent=2))
    else:
        formatar_sequencia(sequencia)


if __name__ == "__main__":
    main()
