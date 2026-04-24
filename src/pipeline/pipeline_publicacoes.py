#!/usr/bin/env python3
"""
Pipeline de Publicações Judiciais — Stemmia Forense

Consolida resultados do monitor de publicações (DJe + DataJud),
calcula prazos, gera CSV/JSON/Dashboard e notifica via Telegram.

Uso:
    python3 pipeline_publicacoes.py                        # Roda tudo
    python3 pipeline_publicacoes.py --telegram             # Com notificação
    python3 pipeline_publicacoes.py --dashboard            # Gera HTML
    python3 pipeline_publicacoes.py --csv                  # Gera CSV
    python3 pipeline_publicacoes.py --test                 # Gera tudo sem notificar
    python3 pipeline_publicacoes.py --data 2026-04-13      # Data específica

Cron recomendado (após monitor_publicacoes.py):
    20 6 * * 1-6 cd ~/stemmia-forense && python3 src/pipeline/pipeline_publicacoes.py --telegram --dashboard --csv
"""

import argparse
import csv
import importlib.util
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(os.path.expanduser("~/stemmia-forense"))
MONITOR_DIR = BASE_DIR / "src" / "pje" / "monitor-publicacoes"
RESULTADOS_DIR = MONITOR_DIR / "resultados"
OUTPUT_DIR = BASE_DIR / "output" / "publicacoes"
LISTA_PUSH = Path(os.path.expanduser("~/Desktop/STEMMIA Dexter/LISTA-COMPLETA-PUSH.json"))

# ============================================================
# FERIADOS E PRAZOS (extraído de detectar_urgencia.py)
# ============================================================

FERIADOS = {
    date(2025, 1, 1), date(2025, 3, 3), date(2025, 3, 4),
    date(2025, 4, 18), date(2025, 4, 21), date(2025, 5, 1),
    date(2025, 6, 19), date(2025, 9, 7), date(2025, 10, 12),
    date(2025, 11, 2), date(2025, 11, 15), date(2025, 12, 25),
    date(2026, 1, 1), date(2026, 2, 16), date(2026, 2, 17),
    date(2026, 4, 3), date(2026, 4, 21), date(2026, 5, 1),
    date(2026, 6, 4), date(2026, 9, 7), date(2026, 10, 12),
    date(2026, 11, 2), date(2026, 11, 15), date(2026, 12, 25),
    date(2027, 1, 1), date(2027, 2, 8), date(2027, 2, 9),
    date(2027, 3, 26), date(2027, 4, 21), date(2027, 5, 1),
    date(2027, 5, 27), date(2027, 9, 7), date(2027, 10, 12),
    date(2027, 11, 2), date(2027, 11, 15), date(2027, 12, 25),
}

PRAZOS_POR_TIPO = {
    "aceite": 5,          # 5 dias úteis
    "proposta": 5,        # 5 dias corridos
    "laudo": 30,          # 30 dias corridos (padrão, pode variar)
    "intimacao": 15,      # 15 dias úteis
    "quesitos": 15,       # 15 dias úteis
    "escusa": 15,         # 15 dias úteis
    "despacho": 0,        # sem prazo padrão
    "outro": 0,
}

RE_CNJ = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')


def adicionar_dias_uteis(data_base, dias):
    """Adiciona N dias úteis a uma data."""
    resultado = data_base
    adicionados = 0
    while adicionados < dias:
        resultado += timedelta(days=1)
        if resultado.weekday() < 5 and resultado not in FERIADOS:
            adicionados += 1
    return resultado


def dias_uteis_entre(data_inicio, data_fim):
    """Calcula dias úteis entre duas datas."""
    if data_fim <= data_inicio:
        return -(dias_uteis_entre(data_fim, data_inicio))
    dias = 0
    atual = data_inicio + timedelta(days=1)
    while atual <= data_fim:
        if atual.weekday() < 5 and atual not in FERIADOS:
            dias += 1
        atual += timedelta(days=1)
    return dias


# ============================================================
# CARREGAR DADOS
# ============================================================

def carregar_lista_push():
    """Carrega LISTA-COMPLETA-PUSH.json → dict {cnj: dados}."""
    if not LISTA_PUSH.exists():
        return {}
    data = json.loads(LISTA_PUSH.read_text(encoding="utf-8"))
    return {p["cnj"]: p for p in data.get("processos", []) if p.get("cnj")}


def carregar_resultados_monitor(data_alvo=None):
    """Carrega resultados mais recentes do monitor de publicações."""
    if data_alvo is None:
        data_alvo = datetime.now().strftime("%Y-%m-%d")

    resultados_dje = []
    resultados_datajud = []

    # Buscar arquivos do dia (ou mais recentes)
    if RESULTADOS_DIR.exists():
        dje_files = sorted(RESULTADOS_DIR.glob("dje-tjmg-*.json"), reverse=True)
        monitor_files = sorted(RESULTADOS_DIR.glob("monitor-completo-*.json"), reverse=True)

        # DJe TJMG
        for f in dje_files:
            if data_alvo in f.name or not resultados_dje:
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    resultados_dje = data.get("matches", [])
                    break
                except (json.JSONDecodeError, OSError):
                    continue

        # Monitor completo (DataJud + outros)
        for f in monitor_files:
            if data_alvo in f.name or not resultados_datajud:
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    # Extrair CNJs com movimentação do resumo
                    cnjs_detectados = data.get("cnjs_detectados", [])
                    fontes = data.get("fontes", {})
                    datajud_info = fontes.get("datajud", {})
                    resultados_datajud = {
                        "cnjs_detectados": cnjs_detectados,
                        "com_movimentacoes": datajud_info.get("com_movimentacoes", 0),
                        "total_movimentacoes": datajud_info.get("total_movimentacoes", 0),
                    }
                    break
                except (json.JSONDecodeError, OSError):
                    continue

    return resultados_dje, resultados_datajud


# ============================================================
# CLASSIFICAÇÃO DE TIPO
# ============================================================

def classificar_tipo_publicacao(texto):
    """Classifica tipo de publicação pelo conteúdo."""
    texto_lower = texto.lower()

    if any(t in texto_lower for t in ["nomeado perito", "nomeação", "nomear perito", "nomeio"]):
        return "aceite"
    if any(t in texto_lower for t in ["proposta de honorários", "honorários periciais", "arbitramento"]):
        return "proposta"
    if any(t in texto_lower for t in ["laudo", "apresente o laudo", "prazo para laudo"]):
        return "laudo"
    if any(t in texto_lower for t in ["quesito", "quesitos suplementar"]):
        return "quesitos"
    if any(t in texto_lower for t in ["escusa", "recusa", "escusar"]):
        return "escusa"
    if any(t in texto_lower for t in ["intim", "ciência", "notificad"]):
        return "intimacao"
    if any(t in texto_lower for t in ["despacho", "decisão", "decido"]):
        return "despacho"
    return "outro"


def detectar_tribunal(cnj):
    """Detecta tribunal pelo código no CNJ."""
    m = re.match(r'\d{7}-\d{2}\.\d{4}\.(\d)\.(\d{2})\.\d{4}', cnj)
    if not m:
        return "?"
    justica = m.group(1)
    tribunal = m.group(2)
    if justica == "8" and tribunal == "13":
        return "TJMG"
    if justica == "5":
        if tribunal == "06":
            return "TRF6"
        if tribunal == "03":
            return "TRF3"
    return f"J{justica}.{tribunal}"


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar_publicacao_dje(match, lista_push):
    """Normaliza um match do DJe TJMG para formato unificado."""
    cnjs = match.get("cnjs_no_contexto", [])
    cnj = cnjs[0] if cnjs else ""
    contexto = match.get("contexto", "")

    # Enriquecer com lista push
    push_data = lista_push.get(cnj, {}) if cnj else {}

    # Parse da data
    data_pub_str = match.get("data", "")
    data_pub = None
    try:
        data_pub = datetime.strptime(data_pub_str, "%d/%m/%Y").date()
    except (ValueError, TypeError):
        pass

    tipo = classificar_tipo_publicacao(contexto)
    tribunal = detectar_tribunal(cnj) if cnj else "TJMG"

    # Calcular prazo
    prazo_calculado = ""
    dias_restantes = ""
    urgencia = "SEM_PRAZO"

    prazo_dias = PRAZOS_POR_TIPO.get(tipo, 0)
    if prazo_dias > 0 and data_pub:
        if tipo in ("aceite", "intimacao", "quesitos", "escusa"):
            vencimento = adicionar_dias_uteis(data_pub, prazo_dias)
            dias_restantes = dias_uteis_entre(date.today(), vencimento)
        else:
            vencimento = data_pub + timedelta(days=prazo_dias)
            dias_restantes = (vencimento - date.today()).days

        prazo_calculado = vencimento.strftime("%d/%m/%Y")

        if dias_restantes < 0:
            urgencia = "VENCIDO"
        elif dias_restantes <= 3:
            urgencia = "URGENTE"
        else:
            urgencia = "NO_PRAZO"

    return {
        "cnj": cnj,
        "tribunal": tribunal,
        "comarca": match.get("comarca", push_data.get("cidade", "?")),
        "vara": push_data.get("vara_full", push_data.get("vara_abrev", "")),
        "data_publicacao": data_pub_str,
        "conteudo": contexto,
        "tipo": tipo,
        "prazo_calculado": prazo_calculado,
        "dias_restantes": dias_restantes if dias_restantes != "" else None,
        "urgencia": urgencia,
        "fonte": "DJe TJMG",
        "termo_busca": match.get("termo", ""),
        # Campos enriquecidos do PUSH
        "status_processo": push_data.get("status", ""),
        "pericia_num": push_data.get("pericia_num", ""),
    }


def normalizar_movimentacao_datajud(cnj, lista_push):
    """Cria registro de publicação para CNJ com movimentação DataJud."""
    push_data = lista_push.get(cnj, {})
    tribunal = detectar_tribunal(cnj)

    return {
        "cnj": cnj,
        "tribunal": tribunal,
        "comarca": push_data.get("cidade", "?"),
        "vara": push_data.get("vara_full", push_data.get("vara_abrev", "")),
        "data_publicacao": datetime.now().strftime("%d/%m/%Y"),
        "conteudo": f"Movimentação detectada via DataJud API para {cnj}",
        "tipo": "despacho",
        "prazo_calculado": "",
        "dias_restantes": None,
        "urgencia": "SEM_PRAZO",
        "fonte": "DataJud API",
        "termo_busca": "",
        "status_processo": push_data.get("status", ""),
        "pericia_num": push_data.get("pericia_num", ""),
    }


# ============================================================
# PIPELINE PRINCIPAL
# ============================================================

def executar_pipeline(data_alvo=None, gerar_csv=False, gerar_dashboard=False,
                      notificar_telegram=False, upload_ftp=False):
    """Pipeline completo de publicações."""
    print(f"  Pipeline Publicações — {datetime.now().strftime('%d/%m/%Y %H:%M')}", file=sys.stderr)
    print(f"  {'=' * 50}", file=sys.stderr)

    # 1. Carregar dados
    print("  [1/5] Carregando dados...", file=sys.stderr)
    lista_push = carregar_lista_push()
    print(f"        {len(lista_push)} processos em LISTA-COMPLETA-PUSH.json", file=sys.stderr)

    # 2. Carregar resultados do monitor
    print("  [2/5] Carregando resultados do monitor...", file=sys.stderr)
    resultados_dje, resultados_datajud = carregar_resultados_monitor(data_alvo)
    print(f"        DJe: {len(resultados_dje)} matches", file=sys.stderr)
    if isinstance(resultados_datajud, dict):
        print(f"        DataJud: {resultados_datajud.get('com_movimentacoes', 0)} processos com movimentação", file=sys.stderr)

    # 3. Normalizar
    print("  [3/5] Normalizando publicações...", file=sys.stderr)
    publicacoes = []

    # DJe
    cnjs_vistos = set()
    for match in resultados_dje:
        pub = normalizar_publicacao_dje(match, lista_push)
        if pub["cnj"]:
            cnjs_vistos.add(pub["cnj"])
        publicacoes.append(pub)

    # DataJud (CNJs com movimentação que não vieram do DJe)
    if isinstance(resultados_datajud, dict):
        for cnj in resultados_datajud.get("cnjs_detectados", []):
            if cnj not in cnjs_vistos:
                pub = normalizar_movimentacao_datajud(cnj, lista_push)
                publicacoes.append(pub)

    # Ordenar: mais urgente primeiro
    def sort_key(p):
        d = p.get("dias_restantes")
        if d is None:
            return 9999
        return d

    publicacoes.sort(key=sort_key)
    print(f"        {len(publicacoes)} publicações normalizadas", file=sys.stderr)

    # 4. Gerar saídas
    print("  [4/5] Gerando saídas...", file=sys.stderr)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data_str = datetime.now().strftime("%Y%m%d")

    # JSON sempre
    json_path = OUTPUT_DIR / f"publicacoes_{data_str}.json"
    output_data = {
        "gerado_em": datetime.now().isoformat(),
        "total": len(publicacoes),
        "vencidos": sum(1 for p in publicacoes if p.get("urgencia") == "VENCIDO"),
        "urgentes": sum(1 for p in publicacoes if p.get("urgencia") == "URGENTE"),
        "no_prazo": sum(1 for p in publicacoes if p.get("urgencia") == "NO_PRAZO"),
        "sem_prazo": sum(1 for p in publicacoes if p.get("urgencia") == "SEM_PRAZO"),
        "publicacoes": publicacoes,
    }
    json_path.write_text(json.dumps(output_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"        JSON: {json_path}", file=sys.stderr)

    # CSV
    if gerar_csv:
        csv_path = OUTPUT_DIR / f"publicacoes_{data_str}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([
                "CNJ", "Tribunal", "Comarca", "Vara", "Data Publicação",
                "Tipo", "Prazo", "Dias Restantes", "Urgência",
                "Status Processo", "Perícia Nº", "Fonte", "Conteúdo"
            ])
            for p in publicacoes:
                writer.writerow([
                    p.get("cnj", ""),
                    p.get("tribunal", ""),
                    p.get("comarca", ""),
                    p.get("vara", ""),
                    p.get("data_publicacao", ""),
                    p.get("tipo", ""),
                    p.get("prazo_calculado", ""),
                    p.get("dias_restantes", ""),
                    p.get("urgencia", ""),
                    p.get("status_processo", ""),
                    p.get("pericia_num", ""),
                    p.get("fonte", ""),
                    p.get("conteudo", "")[:200],
                ])
        print(f"        CSV: {csv_path}", file=sys.stderr)

    # Dashboard HTML
    if gerar_dashboard:
        sys.path.insert(0, str(Path(__file__).parent))
        from gerar_dashboard_publicacoes import gerar
        gerar(publicacoes, upload=upload_ftp)

    # 5. Notificação Telegram
    if notificar_telegram:
        print("  [5/5] Notificando Telegram...", file=sys.stderr)
        _notificar_telegram(publicacoes)
    else:
        print("  [5/5] Telegram: desativado", file=sys.stderr)

    print(f"\n  Pipeline concluído: {len(publicacoes)} publicações processadas.", file=sys.stderr)
    return publicacoes


# ============================================================
# TELEGRAM
# ============================================================

def _notificar_telegram(publicacoes):
    """Formata e envia resumo para Telegram."""
    # Importar módulo de notificação
    try:
        sys.path.insert(0, str(BASE_DIR / "src" / "utilidades"))
        from notificar_telegram import enviar
    except ImportError:
        print("  notificar_telegram.py não encontrado", file=sys.stderr)
        return

    hoje = datetime.now().strftime("%d/%m/%Y")
    total = len(publicacoes)

    vencidos = [p for p in publicacoes if p.get("urgencia") == "VENCIDO"]
    urgentes = [p for p in publicacoes if p.get("urgencia") == "URGENTE"]
    no_prazo = [p for p in publicacoes if p.get("urgencia") == "NO_PRAZO"]

    if total == 0:
        enviar(f"*PUBLICAÇÕES — {hoje}*\n\nNenhuma publicação encontrada.")
        return

    linhas = [f"*PUBLICAÇÕES — {hoje}*", ""]

    if vencidos:
        linhas.append(f"*VENCIDO ({len(vencidos)}):*")
        for p in vencidos[:5]:
            cnj_curto = p['cnj'][:25] if p.get('cnj') else '?'
            linhas.append(f"  `{cnj_curto}` — {p.get('tipo','')} venceu {p.get('prazo_calculado','')}")
        if len(vencidos) > 5:
            linhas.append(f"  _...e mais {len(vencidos)-5}_")
        linhas.append("")

    if urgentes:
        linhas.append(f"*URGENTE ({len(urgentes)}):*")
        for p in urgentes[:5]:
            cnj_curto = p['cnj'][:25] if p.get('cnj') else '?'
            linhas.append(f"  `{cnj_curto}` — {p.get('tipo','')}: {p.get('dias_restantes','')} dias")
        if len(urgentes) > 5:
            linhas.append(f"  _...e mais {len(urgentes)-5}_")
        linhas.append("")

    if no_prazo:
        linhas.append(f"*NO PRAZO ({len(no_prazo)}):*")
        for p in no_prazo[:3]:
            cnj_curto = p['cnj'][:25] if p.get('cnj') else '?'
            linhas.append(f"  `{cnj_curto}` — {p.get('tipo','')}: {p.get('dias_restantes','')} dias")
        if len(no_prazo) > 3:
            linhas.append(f"  _...e mais {len(no_prazo)-3}_")
        linhas.append("")

    sem_prazo = total - len(vencidos) - len(urgentes) - len(no_prazo)
    linhas.append(f"Total: {total} | Sem prazo: {sem_prazo}")

    texto = "\n".join(linhas)

    # Telegram tem limite de 4096 chars
    if len(texto) > 4000:
        texto = texto[:3990] + "\n..."

    enviar(texto)
    print("  Telegram: enviado", file=sys.stderr)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Pipeline de publicações judiciais")
    parser.add_argument("--data", "-d", help="Data alvo (YYYY-MM-DD, padrão: hoje)")
    parser.add_argument("--telegram", "-t", action="store_true", help="Notificar Telegram")
    parser.add_argument("--dashboard", action="store_true", help="Gerar dashboard HTML")
    parser.add_argument("--csv", action="store_true", help="Gerar CSV")
    parser.add_argument("--upload", action="store_true", help="Upload FTP do dashboard")
    parser.add_argument("--test", action="store_true", help="Gera tudo (JSON+CSV+HTML) sem notificar")

    args = parser.parse_args()

    if args.test:
        args.csv = True
        args.dashboard = True

    executar_pipeline(
        data_alvo=args.data,
        gerar_csv=args.csv,
        gerar_dashboard=args.dashboard,
        notificar_telegram=args.telegram,
        upload_ftp=args.upload,
    )


if __name__ == "__main__":
    main()
