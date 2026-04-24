#!/usr/bin/env python3
"""
Consolidador de Processos — Stemmia Forense

Carrega 5 fontes de dados JSON, faz merge por CNJ, retorna lista
enriquecida de todos os processos do perito.

Uso:
    python3 consolidar_processos.py                  # Gera PROCESSOS-CONSOLIDADO.json
    python3 consolidar_processos.py --dashboard      # Também regenera dashboard HTML
    python3 consolidar_processos.py --telegram       # Envia resumo se houver mudanças
    python3 consolidar_processos.py --dry-run        # Mostra o que faria sem salvar

Fontes:
    1. LISTA-MESTRE-PROCESSOS.json      (139 processos, base)
    2. NOMEACOES-COMPLETAS.json         (88 nomeações AJ+AJG, valor/prazo)
    3. STATUS-PROCESSOS.json            (83 pastas, estado pipeline)
    4. consolidacao_bruta_*.json         (DataJud: classe, órgão, movimentos)
    5. comunica_pje_bruto.json          (70 CNJs com comunicações)
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(os.path.expanduser("~/stemmia-forense"))
DATA_DIR = BASE_DIR / "data"

LISTA_MESTRE = DATA_DIR / "LISTA-MESTRE-PROCESSOS.json"
NOMEACOES = DATA_DIR / "NOMEACOES-COMPLETAS.json"
STATUS_PROCESSOS = Path(os.path.expanduser(
    "~/Desktop/ANALISADOR FINAL/STATUS-PROCESSOS.json"
))
CONSOLIDADO_DIR = Path(os.path.expanduser(
    "~/Desktop/ANALISADOR FINAL/scripts/consolidado"
))
FONTES_DIR = Path(os.path.expanduser(
    "~/Desktop/ANALISADOR FINAL/scripts/fontes"
))
COMUNICA_PJE = FONTES_DIR / "comunica_pje_bruto.json"

OUTPUT_JSON = DATA_DIR / "PROCESSOS-CONSOLIDADO.json"

NORMALIZAR_CIDADES = {
    "Gov Valadares": "Governador Valadares",
    "Gov. Valadares": "Governador Valadares",
    "Cons Pena": "Conselheiro Pena",
    "Cons. Pena": "Conselheiro Pena",
    "Cel Fabriciano": "Coronel Fabriciano",
    "Cel. Fabriciano": "Coronel Fabriciano",
    "Rib. das Neves": "Ribeirão das Neves",
    "R. das Neves": "Ribeirão das Neves",
}


def normalizar_cidade(nome):
    return NORMALIZAR_CIDADES.get(nome, nome)


# ============================================================
# CARREGADORES
# ============================================================

def carregar_json(path):
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def carregar_lista_mestre():
    """Retorna dict {cnj: {dados}} da lista mestre."""
    data = carregar_json(LISTA_MESTRE)
    if not data:
        return {}
    result = {}
    for p in data.get("processos", []):
        cnj = p.get("cnj", "")
        if cnj:
            result[cnj] = p
    return result


def carregar_nomeacoes():
    """Retorna dict {cnj: {dados}} das nomeações AJ+AJG."""
    data = carregar_json(NOMEACOES)
    if not data:
        return {}
    result = {}
    for n in data.get("nomeacoes", []):
        cnj = n.get("cnj", "")
        if cnj:
            result[cnj] = n
    return result


def carregar_status_pipeline():
    """Retorna dict {cnj: {dados}} do scanner de pastas."""
    data = carregar_json(STATUS_PROCESSOS)
    if not data:
        return {}
    result = {}
    processos = data.get("processos", [])
    for p in processos:
        cnj = p.get("cnj", "")
        if cnj:
            result[cnj] = p
    return result


def carregar_datajud():
    """Retorna dict {cnj: {dados}} da consolidação DataJud mais recente."""
    pattern = str(CONSOLIDADO_DIR / "consolidacao_bruta_*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        return {}
    data = carregar_json(Path(files[-1]))
    if not data:
        return {}
    result = {}
    for p in data.get("processos", []):
        cnj = p.get("numero_processo", "")
        if cnj:
            result[cnj] = p
    return result


def carregar_comunica_pje():
    """Retorna set de CNJs que têm comunicações pendentes."""
    data = carregar_json(COMUNICA_PJE)
    if not data:
        return set()
    return set(data.get("cnjs", []))


# ============================================================
# MERGE
# ============================================================

ETAPAS_PIPELINE = [
    "NOMEAÇÃO",
    "PENDENTE-PDF",
    "PENDENTE-ACEITE",
    "PENDENTE-AGENDAMENTO",
    "PERÍCIA-AGENDADA",
    "PENDENTE-LAUDO",
    "PENDENTE-PROPOSTA",
    "COMPLETO",
]

ESTADOS_INATIVOS = {"EXPIRADO", "CANCELADO", "RECUSADO"}


def inferir_etapa_pipeline(situacao_aj, estado_local):
    """Infere etapa do pipeline a partir da situação AJ/AJG e estado local."""
    if estado_local:
        mapa = {
            "PENDENTE-ACEITE": "PENDENTE-ACEITE",
            "PENDENTE-PDF": "PENDENTE-PDF",
            "PENDENTE-AGENDAMENTO": "PENDENTE-AGENDAMENTO",
            "PERICIA-AGENDADA": "PERÍCIA-AGENDADA",
            "PENDENTE-LAUDO": "PENDENTE-LAUDO",
            "PENDENTE-PROPOSTA": "PENDENTE-PROPOSTA",
            "PENDENTE-EXTRACAO": "PENDENTE-PDF",
            "PENDENTE-ANALISE": "PENDENTE-PDF",
            "EM-CONTESTAÇÃO": "PENDENTE-PROPOSTA",
            "COMPLETO": "COMPLETO",
        }
        return mapa.get(estado_local, estado_local)

    if not situacao_aj:
        return "NOMEAÇÃO"

    mapa_aj = {
        "ACEITA": "PENDENTE-PDF",
        "SERVIÇO PRESTADO": "COMPLETO",
        "PERDA DE PRAZO": "EXPIRADO",
        "CANCELADA PELO JUIZ": "CANCELADO",
        "RECUSADA": "RECUSADO",
        "AGUARDANDO ACEITE": "PENDENTE-ACEITE",
    }
    return mapa_aj.get(situacao_aj, "NOMEAÇÃO")


def consolidar_tudo():
    """Merge todas as fontes. Retorna lista de dicts enriquecidos."""
    mestre = carregar_lista_mestre()
    nomeacoes = carregar_nomeacoes()
    pipeline = carregar_status_pipeline()
    datajud = carregar_datajud()
    comunica_cnjs = carregar_comunica_pje()

    resultado = []

    for cnj, base in mestre.items():
        proc = {
            "cnj": cnj,
            "cidade": normalizar_cidade(base.get("cidade", "")),
            "data_nomeacao": base.get("data_nomeacao", ""),
            "situacao_aj": base.get("situacao_aj", ""),
            "sistema": base.get("sistema", ""),
            "estado_local": base.get("estado_local", ""),
            # DataJud
            "verificado_datajud": base.get("verificado_datajud", False),
            "classe": base.get("classe", ""),
            "orgao_julgador": base.get("orgao_julgador", ""),
            "data_ajuizamento": base.get("data_ajuizamento", ""),
            # Nomeação (AJ/AJG)
            "valor_honorario": "",
            "dias_aceite": "",
            "vara": "",
            "numero_nomeacao": "",
            # Pipeline
            "etapa_pipeline": "",
            "tem_pasta": False,
            "arquivos": {},
            "proxima_acao": "",
            # DataJud enriquecido
            "ultima_atualizacao_datajud": "",
            "total_movimentos": 0,
            # Comunicações
            "tem_comunicacao_pendente": cnj in comunica_cnjs,
        }

        # Enriquecer com nomeações
        nom = nomeacoes.get(cnj)
        if nom:
            proc["valor_honorario"] = nom.get("valor_honorario", "")
            proc["dias_aceite"] = nom.get("dias_aceite", "")
            proc["vara"] = nom.get("vara", "")
            proc["numero_nomeacao"] = nom.get("numero_nomeacao", "")

        # Enriquecer com pipeline/scanner
        pip = pipeline.get(cnj)
        if pip:
            proc["tem_pasta"] = True
            proc["arquivos"] = pip.get("arquivos", {})
            proc["estado_local"] = pip.get("estado", proc["estado_local"])
            proc["proxima_acao"] = pip.get("proxima_acao", "")

        # Enriquecer com DataJud consolidado
        dj = datajud.get(cnj)
        if dj:
            proc["classe"] = proc["classe"] or dj.get("classe", "")
            proc["orgao_julgador"] = proc["orgao_julgador"] or dj.get("orgaoJulgador", "")
            proc["ultima_atualizacao_datajud"] = dj.get("ultima_atualizacao", "")
            proc["total_movimentos"] = dj.get("total_movimentos", 0)
            proc["verificado_datajud"] = True

        # Inferir etapa do pipeline
        proc["etapa_pipeline"] = inferir_etapa_pipeline(
            proc["situacao_aj"], proc["estado_local"]
        )

        resultado.append(proc)

    return resultado


# ============================================================
# ESTATÍSTICAS
# ============================================================

def estatisticas(processos):
    """Calcula contagens e alertas."""
    stats = {
        "total": len(processos),
        "por_situacao": {},
        "por_cidade": {},
        "por_sistema": {},
        "por_etapa": {},
        "alertas": [],
        "valor_total_honorarios": 0.0,
    }

    for p in processos:
        # Por situação
        sit = p["situacao_aj"] or "PJe direto"
        stats["por_situacao"][sit] = stats["por_situacao"].get(sit, 0) + 1

        # Por cidade
        cid = p["cidade"] or "Desconhecida"
        stats["por_cidade"][cid] = stats["por_cidade"].get(cid, 0) + 1

        # Por sistema
        sis = p["sistema"] or "?"
        stats["por_sistema"][sis] = stats["por_sistema"].get(sis, 0) + 1

        # Por etapa pipeline
        etapa = p["etapa_pipeline"]
        stats["por_etapa"][etapa] = stats["por_etapa"].get(etapa, 0) + 1

        # Honorários
        val = p.get("valor_honorario", "")
        if val:
            try:
                stats["valor_total_honorarios"] += float(
                    val.replace(".", "").replace(",", ".")
                )
            except (ValueError, AttributeError):
                pass

        # Alertas
        if p["tem_comunicacao_pendente"]:
            stats["alertas"].append({
                "tipo": "COMUNICAÇÃO",
                "cnj": p["cnj"],
                "cidade": p["cidade"],
                "msg": "Comunicação PJe pendente",
            })

        if p["etapa_pipeline"] == "PENDENTE-ACEITE":
            stats["alertas"].append({
                "tipo": "ACEITE",
                "cnj": p["cnj"],
                "cidade": p["cidade"],
                "msg": "Aguardando aceite",
            })

        if p["etapa_pipeline"] == "PENDENTE-PDF" and p["situacao_aj"] == "ACEITA":
            stats["alertas"].append({
                "tipo": "PDF",
                "cnj": p["cnj"],
                "cidade": p["cidade"],
                "msg": "Aceita sem PDF baixado",
            })

        if p["etapa_pipeline"] == "PENDENTE-LAUDO":
            stats["alertas"].append({
                "tipo": "LAUDO",
                "cnj": p["cnj"],
                "cidade": p["cidade"],
                "msg": "Perícia feita, laudo pendente",
            })

    return stats


# ============================================================
# COMPARAÇÃO DE SNAPSHOTS
# ============================================================

def comparar_snapshots(anterior, atual):
    """Compara dois snapshots e retorna mudanças."""
    if not anterior:
        return {"novos": len(atual), "mudancas": [], "resumo": "Primeiro snapshot"}

    ant_map = {p["cnj"]: p for p in anterior}
    atu_map = {p["cnj"]: p for p in atual}

    novos = [cnj for cnj in atu_map if cnj not in ant_map]
    removidos = [cnj for cnj in ant_map if cnj not in atu_map]

    mudancas = []
    for cnj in atu_map:
        if cnj in ant_map:
            a = ant_map[cnj]
            b = atu_map[cnj]
            if a.get("etapa_pipeline") != b.get("etapa_pipeline"):
                mudancas.append({
                    "cnj": cnj,
                    "campo": "etapa_pipeline",
                    "de": a.get("etapa_pipeline"),
                    "para": b.get("etapa_pipeline"),
                })
            if a.get("situacao_aj") != b.get("situacao_aj"):
                mudancas.append({
                    "cnj": cnj,
                    "campo": "situacao_aj",
                    "de": a.get("situacao_aj"),
                    "para": b.get("situacao_aj"),
                })

    return {
        "novos": novos,
        "removidos": removidos,
        "mudancas": mudancas,
        "resumo": f"{len(novos)} novos, {len(mudancas)} mudanças",
    }


# ============================================================
# SALVAR
# ============================================================

def salvar_consolidado(processos, stats):
    """Salva PROCESSOS-CONSOLIDADO.json."""
    output = {
        "ultima_atualizacao": datetime.now().isoformat(),
        "total": len(processos),
        "estatisticas": stats,
        "processos": processos,
    }
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    return OUTPUT_JSON


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Consolidar processos periciais")
    parser.add_argument("--dashboard", action="store_true", help="Regenerar dashboard HTML")
    parser.add_argument("--telegram", action="store_true", help="Enviar resumo Telegram")
    parser.add_argument("--dry-run", action="store_true", help="Não salvar, só mostrar")
    parser.add_argument("--json", action="store_true", help="Saída JSON puro")
    args = parser.parse_args()

    # Carregar snapshot anterior
    anterior = []
    if OUTPUT_JSON.exists():
        old = carregar_json(OUTPUT_JSON)
        if old:
            anterior = old.get("processos", [])

    # Consolidar
    processos = consolidar_tudo()
    stats = estatisticas(processos)

    # Comparar
    diff = comparar_snapshots(anterior, processos)

    if args.json:
        print(json.dumps({
            "total": len(processos),
            "estatisticas": stats,
            "mudancas": diff,
        }, ensure_ascii=False, indent=2))
        return

    # Resumo
    print(f"Total: {stats['total']} processos")
    print(f"Pipeline: {json.dumps(stats['por_etapa'], ensure_ascii=False)}")
    print(f"Alertas: {len(stats['alertas'])}")
    print(f"Honorários estimados: R$ {stats['valor_total_honorarios']:,.2f}")
    if diff.get("novos"):
        novos = diff["novos"]
        if isinstance(novos, list):
            print(f"Novos: {len(novos)} → {', '.join(novos[:5])}")
        else:
            print(f"Novos: {novos}")
    if diff.get("mudancas"):
        print(f"Mudanças: {len(diff['mudancas'])}")
        for m in diff["mudancas"][:5]:
            print(f"  {m['cnj']}: {m['campo']} {m['de']} → {m['para']}")

    if args.dry_run:
        print("\n[DRY-RUN] Nenhum arquivo salvo.")
        return

    # Salvar
    path = salvar_consolidado(processos, stats)
    print(f"\nSalvo: {path}")

    # Dashboard
    if args.dashboard:
        dashboard_script = BASE_DIR / "src" / "pipeline" / "gerar_dashboard_processos.py"
        if dashboard_script.exists():
            subprocess.run([sys.executable, str(dashboard_script)], check=False)
        else:
            print(f"[AVISO] Dashboard não encontrado: {dashboard_script}")

    # Telegram
    if args.telegram and (diff.get("novos") or diff.get("mudancas")):
        telegram_script = Path(os.path.expanduser(
            "~/Desktop/ANALISADOR FINAL/scripts/notificar_telegram.py"
        ))
        if telegram_script.exists():
            msg = f"📋 Monitor Processos\n{stats['total']} processos | {diff['resumo']}\n"
            msg += f"Alertas: {len(stats['alertas'])}"
            subprocess.run(
                [sys.executable, str(telegram_script), "--mensagem", msg],
                check=False,
            )


if __name__ == "__main__":
    main()
