#!/usr/bin/env python3
"""Buscador de Oportunidades para Perito — CLI principal."""

import asyncio
import argparse
import logging
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import LOG_DIR, DATA_DIR
from db import (
    init_db, inserir_oportunidade, registrar_busca, get_estatisticas,
    limpar_antigos, atualizar_data_titulo_existentes,
)
from buscadores.jusbrasil import BuscadorJusBrasil
from notifier import notificar_resultados, tocar_som
from dashboard import gerar_html, iniciar_dashboard


def setup_logging(silencioso=False):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"busca_{datetime.now().strftime('%Y-%m-%d')}.log")

    level = logging.WARNING if silencioso else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


async def executar_busca():
    logger = logging.getLogger(__name__)
    init_db()

    total_encontrados = 0
    total_novos = 0
    data_inicio = datetime.now().isoformat()

    buscador = BuscadorJusBrasil()
    logger.info("=== Iniciando busca: JusBrasil (comarcas 200km de GV) ===")

    try:
        resultados = await buscador.buscar_todos()
    except Exception as e:
        logger.error(f"Erro no buscador: {e}")
        resultados = []

    for op in resultados:
        status, oport_id = inserir_oportunidade(op)
        total_encontrados += 1
        if status == "novo":
            total_novos += 1
            logger.info(f"  NOVO: {op.titulo[:80]} | {op.comarca} | {op.categoria}")

    registrar_busca(
        data_inicio=data_inicio,
        data_fim=datetime.now().isoformat(),
        total_encontrados=total_encontrados,
        total_novos=total_novos,
        termos_buscados=total_encontrados,
        fonte="jusbrasil",
    )

    logger.info(f"\n{'='*50}")
    logger.info(f"Busca finalizada: {total_encontrados} encontrado(s), {total_novos} novo(s)")
    logger.info(f"{'='*50}")

    notificar_resultados(total_novos, total_encontrados)
    return total_novos, total_encontrados


def mostrar_status():
    init_db()
    stats = get_estatisticas()
    print(f"""
{'='*50}
 BUSCADOR DE OPORTUNIDADES PARA PERITO
 (Comarcas até 200km de Gov. Valadares)
{'='*50}

 Total de oportunidades: {stats['total']}
 Recentes (últimos 12 meses): {stats.get('recentes', 0)}
 Pendentes (não contatadas): {stats['pendentes']}
 Contatadas: {stats['contatados']}
 Comarcas diferentes: {stats['comarcas']}
 Última busca: {stats['ultima_busca'] or 'Nunca'}

 Por categoria:""")

    for cat, qtd in stats.get('por_categoria', {}).items():
        print(f"   {cat}: {qtd}")

    print(f"{'='*50}")


def executar_limpeza():
    init_db()
    # Preencher data_titulo nos registros existentes
    atualizados = atualizar_data_titulo_existentes()
    print(f"Data extraída de {atualizados} registros existentes")

    antigos, fora_mg, fora_raio = limpar_antigos()
    print(f"Ignorados: {antigos} antigos (>12 meses), {fora_mg} fora de MG, {fora_raio} fora do raio 200km")


def gerar_dashboard_html():
    """Gera HTML estático do dashboard e abre no navegador."""
    init_db()
    html = gerar_html()
    html_path = os.path.join(DATA_DIR, "dashboard.html")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard salvo em {html_path}")
    import webbrowser
    webbrowser.open(f"file://{html_path}")


def main():
    parser = argparse.ArgumentParser(description="Buscador de Oportunidades para Perito")
    parser.add_argument("--buscar", action="store_true", help="Executar busca")
    parser.add_argument("--dashboard", action="store_true", help="Gerar e abrir dashboard HTML")
    parser.add_argument("--servidor", action="store_true", help="Rodar servidor dashboard (interativo)")
    parser.add_argument("--status", action="store_true", help="Mostrar status")
    parser.add_argument("--limpar", action="store_true", help="Limpar resultados antigos/fora de MG")
    parser.add_argument("--auto", action="store_true", help="Modo automático (silencioso)")

    args = parser.parse_args()

    # Se nenhum argumento, faz busca + dashboard
    if not any([args.buscar, args.dashboard, args.servidor, args.status, args.limpar, args.auto]):
        args.buscar = True
        args.dashboard = True

    setup_logging(silencioso=args.auto)

    if args.buscar or args.auto:
        novos, total = asyncio.run(executar_busca())
        if not args.auto:
            print(f"\nResultado: {novos} nova(s) oportunidade(s), {total} total encontrado(s)")

    if args.limpar:
        executar_limpeza()

    if args.status:
        mostrar_status()

    if args.dashboard:
        gerar_dashboard_html()

    if args.servidor:
        init_db()
        iniciar_dashboard()


if __name__ == "__main__":
    main()
