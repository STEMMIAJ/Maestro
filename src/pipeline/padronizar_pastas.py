#!/usr/bin/env python3
"""
padronizar_pastas.py — Padronização e Dedup de Pastas de Processos
Detecta duplicatas (CNJ em pasta Perícia + pasta CNJ puro).
Renomeia para padrão: "Perícia [NN] - [Cidade] - [Vara] - [CNJ]"

Uso:
    python3 padronizar_pastas.py --dry-run     # Mostra o que faria
    python3 padronizar_pastas.py --executar    # Executa (com confirmação)
    python3 padronizar_pastas.py --json        # Saída JSON
"""

import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(os.path.expanduser("~/Desktop/ANALISADOR FINAL"))
PROCESSOS_DIR = BASE_DIR / "processos"

CNJ_PATTERN = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')
PERICIA_PATTERN = re.compile(r'^Perícia\s+(\d+|\?\?)\s*-\s*(.+?)(?:\s*-\s*(.+?))?(?:\s*-\s*(.+))?$')


def escanear_pastas():
    """Escaneia todas as pastas e identifica duplicatas."""
    pastas = []

    for item in sorted(PROCESSOS_DIR.iterdir()):
        if not item.is_dir() or item.name.startswith('.'):
            continue

        cnj_match = CNJ_PATTERN.search(item.name)
        cnj = cnj_match.group(0) if cnj_match else None

        pericia_match = PERICIA_PATTERN.match(item.name)

        # Tentar ler FICHA.json
        ficha = {}
        ficha_path = item / "FICHA.json"
        if ficha_path.exists():
            try:
                ficha = json.loads(ficha_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        # Se não tem CNJ no nome, tentar da FICHA
        if not cnj and ficha.get("cnj"):
            cnj = ficha["cnj"]

        # Contar arquivos
        n_files = sum(1 for _ in item.rglob("*") if _.is_file())

        info = {
            "pasta": item.name,
            "caminho": str(item),
            "cnj": cnj,
            "is_pericia": pericia_match is not None,
            "numero_pericia": pericia_match.group(1) if pericia_match else None,
            "cidade": pericia_match.group(2).strip() if pericia_match and pericia_match.group(2) else ficha.get("cidade", ""),
            "vara": pericia_match.group(3).strip() if pericia_match and pericia_match.group(3) else ficha.get("vara", ""),
            "n_files": n_files,
            "tem_texto": (item / "TEXTO-EXTRAIDO.txt").exists(),
            "data_nomeacao": ficha.get("data_nomeacao", ""),
        }
        pastas.append(info)

    return pastas


def detectar_duplicatas(pastas):
    """Agrupa pastas pelo mesmo CNJ."""
    grupos = {}
    for p in pastas:
        cnj = p.get("cnj")
        if cnj:
            if cnj not in grupos:
                grupos[cnj] = []
            grupos[cnj].append(p)

    # Duplicatas = CNJs com 2+ pastas
    duplicatas = {cnj: grupo for cnj, grupo in grupos.items() if len(grupo) > 1}
    return duplicatas


def escolher_principal(grupo):
    """Escolhe a pasta principal (mais completa) de um grupo de duplicatas."""
    # Preferir: pasta Perícia > pasta CNJ pura
    # Em caso de empate: mais arquivos > texto extraído
    grupo.sort(key=lambda x: (
        x["is_pericia"],          # Preferir Perícia
        x["n_files"],             # Mais arquivos
        x["tem_texto"],           # Com texto
    ), reverse=True)

    return grupo[0], grupo[1:]  # principal, secundárias


def gerar_nome_padrao(info, numero):
    """Gera nome padronizado."""
    cidade = info.get("cidade", "Desconhecida").strip()
    vara = info.get("vara", "").strip()
    cnj = info.get("cnj", "")

    partes = [f"Perícia {numero:02d}"]
    if cidade:
        partes.append(cidade)
    if vara:
        partes.append(vara)
    if cnj:
        partes.append(cnj)

    return " - ".join(partes)


def planejar_acoes(pastas, duplicatas):
    """Planeja todas as ações (merge + rename)."""
    acoes = []

    # 1. Merge de duplicatas
    for cnj, grupo in duplicatas.items():
        principal, secundarias = escolher_principal(grupo)
        for sec in secundarias:
            acoes.append({
                "tipo": "merge",
                "cnj": cnj,
                "de": sec["pasta"],
                "para": principal["pasta"],
                "arquivos_a_mover": sec["n_files"],
            })

    # 2. Renomear pastas fora do padrão
    # Atribuir números sequenciais baseados na data de nomeação
    pastas_unicas = []
    cnjs_vistos = set()
    for p in pastas:
        cnj = p.get("cnj")
        if cnj and cnj not in cnjs_vistos:
            cnjs_vistos.add(cnj)
            pastas_unicas.append(p)
        elif not cnj:
            pastas_unicas.append(p)

    # Numerar por data de nomeação (ou ordem alfabética se não houver)
    pastas_unicas.sort(key=lambda x: x.get("data_nomeacao", "") or "9999")

    for i, p in enumerate(pastas_unicas, start=1):
        if p.get("cnj"):
            nome_novo = gerar_nome_padrao(p, i)
            if nome_novo != p["pasta"]:
                acoes.append({
                    "tipo": "rename",
                    "de": p["pasta"],
                    "para": nome_novo,
                })

    return acoes


def executar_merge(de_path, para_path):
    """Move arquivos de uma pasta para outra (sem sobrescrever)."""
    de = Path(de_path)
    para = Path(para_path)

    if not de.exists() or not para.exists():
        return False

    movidos = 0
    for item in de.iterdir():
        destino = para / item.name
        if not destino.exists():
            shutil.move(str(item), str(destino))
            movidos += 1

    # Se pasta vazia, remover
    if de.exists() and not any(de.iterdir()):
        de.rmdir()

    return movidos


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Padronização de pastas de processos")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar o que faria sem executar")
    parser.add_argument("--executar", action="store_true", help="Executar as ações")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    args = parser.parse_args()

    pastas = escanear_pastas()
    duplicatas = detectar_duplicatas(pastas)
    acoes = planejar_acoes(pastas, duplicatas)

    resultado = {
        "data": datetime.now().isoformat(),
        "total_pastas": len(pastas),
        "duplicatas": len(duplicatas),
        "acoes": acoes,
    }

    if args.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return

    print("=" * 60)
    print("PADRONIZADOR DE PASTAS — STEMMIA FORENSE")
    print(f"Total de pastas: {len(pastas)}")
    print(f"Duplicatas encontradas: {len(duplicatas)}")
    print(f"Ações planejadas: {len(acoes)}")
    print("=" * 60)

    if not acoes:
        print("\nNenhuma ação necessária. Pastas já organizadas.")
        return

    # Listar ações
    for i, acao in enumerate(acoes, 1):
        if acao["tipo"] == "merge":
            print(f"\n  {i}. MERGE: {acao['de']}")
            print(f"     → {acao['para']} ({acao['arquivos_a_mover']} arquivos)")
        elif acao["tipo"] == "rename":
            print(f"\n  {i}. RENAME: {acao['de']}")
            print(f"     → {acao['para']}")

    if args.dry_run:
        print("\n*** DRY-RUN — nada foi executado ***")
        return

    if args.executar:
        print("\n⚠️  EXECUTANDO AÇÕES...")
        for acao in acoes:
            if acao["tipo"] == "merge":
                de_path = PROCESSOS_DIR / acao["de"]
                para_path = PROCESSOS_DIR / acao["para"]
                movidos = executar_merge(de_path, para_path)
                print(f"  MERGE: {acao['de']} → {acao['para']} ({movidos} arquivos)")
            elif acao["tipo"] == "rename":
                de_path = PROCESSOS_DIR / acao["de"]
                para_path = PROCESSOS_DIR / acao["para"]
                if de_path.exists() and not para_path.exists():
                    de_path.rename(para_path)
                    print(f"  RENAME: {acao['de']} → {acao['para']}")
                else:
                    print(f"  SKIP: {acao['de']} (destino já existe ou origem não encontrada)")
        print("\nConcluído.")
    else:
        print("\nUse --dry-run para ver ou --executar para aplicar.")


if __name__ == "__main__":
    main()
