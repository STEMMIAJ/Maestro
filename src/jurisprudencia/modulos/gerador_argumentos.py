#!/usr/bin/env python3
"""Módulo 4: Gera argumentos de honorários para cada caso pendente."""

import logging
import re
from datetime import datetime
from pathlib import Path
from statistics import median, mean

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import obter_casos, obter_similares, obter_jurisprudencia, inserir_argumentos
from config import TABELA_TJMG, FAIXAS_MERCADO

logger = logging.getLogger("jurisprudencia")


def formatar_valor(valor: float) -> str:
    """Formata valor como R$ X.XXX,XX."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_estatisticas_tipo(conn, tipo: str) -> dict:
    """Calcula estatísticas de valores para um tipo de perícia."""
    todos = obter_jurisprudencia(conn, com_valor=True)
    valores_tipo = [
        j["valor_encontrado"] for j in todos
        if j.get("tipo_pericia_inferido", "") == tipo and j["valor_encontrado"] > 0
    ]

    if not valores_tipo:
        # Usar todos os valores se não houver específicos do tipo
        valores_tipo = [j["valor_encontrado"] for j in todos if j["valor_encontrado"] > 0]

    if not valores_tipo:
        return {"mediana": 0, "media": 0, "min": 0, "max": 0, "qtd": 0}

    return {
        "mediana": median(valores_tipo),
        "media": mean(valores_tipo),
        "min": min(valores_tipo),
        "max": max(valores_tipo),
        "qtd": len(valores_tipo),
    }


def normalizar_tipo(area: str) -> str:
    """Converte área para chave de tipo."""
    area = (area or "").lower()
    if "securitária" in area or "securitaria" in area:
        return "securitaria"
    if "erro médico" in area or "erro medico" in area:
        return "erro_medico"
    if "curatela" in area or "interdição" in area:
        return "curatela"
    if "previdenciária" in area or "previdenciaria" in area:
        return "previdenciaria"
    if "responsabilidade" in area or "acidente" in area:
        return "acidente_transito"
    return "outra"


def gerar_markdown(caso: dict, similares: list, estatisticas: dict, conn) -> str:
    """Gera conteúdo Markdown dos argumentos para um caso."""
    cnj = caso["numero_cnj"]
    area = caso.get("area", "N/D")
    vara = caso.get("vara", "N/D")
    cidade = caso.get("cidade", "N/D")
    tipo_custeio = caso.get("tipo_custeio", "INDEFINIDO")
    tipo = normalizar_tipo(area)

    linhas = []
    linhas.append(f"# ARGUMENTOS PARA PROPOSTA DE HONORÁRIOS")
    linhas.append(f"")
    linhas.append(f"**Processo:** {cnj}")
    linhas.append(f"**Vara:** {vara} — {cidade}")
    linhas.append(f"**Área:** {area}")
    linhas.append(f"**Classificação de custeio:** {tipo_custeio}")
    linhas.append(f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    linhas.append(f"")

    # Seção 1: Precedentes similares
    linhas.append(f"---")
    linhas.append(f"## 1. PRECEDENTES SIMILARES")
    linhas.append(f"")

    if similares:
        for i, s in enumerate(similares[:5], 1):
            valor_str = formatar_valor(s["valor_encontrado"]) if s.get("valor_encontrado") else "Não informado"
            ementa_resumo = (s.get("ementa", "") or "")[:300]
            if len(s.get("ementa", "")) > 300:
                ementa_resumo += "..."

            linhas.append(f"### Precedente {i} (Score: {s['score']:.0f})")
            linhas.append(f"- **Tribunal:** {s.get('tribunal', 'N/D')}")
            linhas.append(f"- **Número:** {s.get('numero', 'N/D')}")
            linhas.append(f"- **Data:** {s.get('data_decisao', 'N/D')}")
            linhas.append(f"- **Valor mencionado:** {valor_str}")
            linhas.append(f"- **Tipo de decisão:** {s.get('tipo_decisao', 'N/D')}")
            linhas.append(f"- **Similaridade:** {s.get('motivo', '')}")
            linhas.append(f"- **Ementa:** {ementa_resumo}")
            if s.get("url"):
                linhas.append(f"- **Link:** {s['url']}")
            linhas.append(f"")
    else:
        linhas.append("*Nenhum precedente similar encontrado na coleta atual.*")
        linhas.append("")

    # Seção 2: Faixas de mercado
    linhas.append(f"---")
    linhas.append(f"## 2. FAIXAS DE MERCADO")
    linhas.append(f"")

    if estatisticas["qtd"] > 0:
        linhas.append(f"**Baseado em {estatisticas['qtd']} decisões coletadas:**")
        linhas.append(f"- Mediana: {formatar_valor(estatisticas['mediana'])}")
        linhas.append(f"- Média: {formatar_valor(estatisticas['media'])}")
        linhas.append(f"- Faixa: {formatar_valor(estatisticas['min'])} a {formatar_valor(estatisticas['max'])}")
        linhas.append(f"")

    # Tabela TJMG (referência)
    tabela_ref = TABELA_TJMG.get("outras", 612.00)
    if tipo == "erro_medico":
        tabela_ref = TABELA_TJMG.get("erro_medico", 1253.96)
    elif tipo == "curatela":
        tabela_ref = TABELA_TJMG.get("interdicao", 612.00)

    linhas.append(f"**Tabela TJMG 2025 (gratuidade — apenas referência):** {formatar_valor(tabela_ref)}")
    linhas.append(f"**Com majoração máxima (5x):** {formatar_valor(tabela_ref * 5)}")
    linhas.append(f"")

    # Faixas de mercado para depósito
    if tipo_custeio == "PARTES":
        faixa = FAIXAS_MERCADO.get("medio", {})
        linhas.append(f"**Faixas de mercado (custeado pelas partes):**")
        for nivel, dados in FAIXAS_MERCADO.items():
            linhas.append(f"- {nivel.title()}: {formatar_valor(dados['min'])} a {formatar_valor(dados['max'])} ({dados['descricao']})")
        linhas.append(f"")
        linhas.append(f"*Nota: Propostas custeadas pelas partes não estão limitadas à tabela de gratuidade.*")
    else:
        linhas.append(f"*Este caso é custeado por gratuidade. Valores limitados à tabela TJMG com majoração justificada.*")
    linhas.append(f"")

    # Seção 3: Fundamentação legal
    linhas.append(f"---")
    linhas.append(f"## 3. FUNDAMENTAÇÃO LEGAL")
    linhas.append(f"")

    if tipo_custeio == "PARTES":
        linhas.append(f"- **Art. 95, caput, CPC:** A remuneração do perito será paga pela parte que requerer a perícia ou rateada quando ambas requererem.")
        linhas.append(f"- **Art. 95, §3º, CPC:** *Não se aplica* ao presente caso (custeio pelas partes, não por gratuidade).")
        linhas.append(f"- **Nota:** Não se aplica a Portaria TJMG 7.231/2025 (tabela de gratuidade), pois o custeio é pelas partes (art. 95, caput, CPC).")
        linhas.append(f"")

    linhas.append(f"- **Art. 465, §2º, CPC:** O perito deve apresentar proposta de honorários em até 5 dias.")
    linhas.append(f"- **Art. 468, CPC:** O juiz pode arbitrar os honorários, observada a complexidade do caso, as peculiaridades regionais e os custos necessários.")
    linhas.append(f"- **Art. 473, CPC:** Requisitos do laudo pericial (fundamentação, método, respostas aos quesitos).")
    linhas.append(f"- **Resolução CFM 2.430/2025:** Obrigatoriedade do ato médico pericial presencial.")
    linhas.append(f"")

    # Seção 4: Parágrafos prontos
    linhas.append(f"---")
    linhas.append(f"## 4. PARÁGRAFOS PRONTOS PARA PROPOSTA")
    linhas.append(f"")

    if tipo_custeio == "PARTES":
        linhas.append(f"### Para proposta (custeado pelas partes):")
        linhas.append(f"")
        linhas.append(f"> Os honorários periciais propostos baseiam-se na complexidade técnica do caso, "
                      f"no volume de documentação a ser analisada, nas especialidades médicas envolvidas "
                      f"e no tempo estimado para execução de todas as etapas periciais. "
                      f"Tratando-se de perícia custeada pelas partes (art. 95, caput, CPC), "
                      f"os valores não estão sujeitos aos limites da tabela de remuneração "
                      f"para justiça gratuita (Portaria TJMG nº 7.231/PR/2025), "
                      f"devendo ser fixados conforme os critérios de razoabilidade, "
                      f"proporcionalidade e complexidade do caso (art. 468, CPC).")
        linhas.append(f"")
    else:
        linhas.append(f"### Para proposta (gratuidade):")
        linhas.append(f"")
        linhas.append(f"> Os honorários periciais propostos consideram a complexidade técnica do caso, "
                      f"o número de especialidades médicas envolvidas e o volume de documentação. "
                      f"Embora a tabela de referência do TJMG (Portaria nº 7.231/PR/2025) "
                      f"estabeleça o valor base de {formatar_valor(tabela_ref)}, a complexidade "
                      f"do presente caso justifica a majoração prevista na própria portaria, "
                      f"que permite ampliação de até 5 vezes o valor de referência "
                      f"em casos de maior complexidade técnica.")
        linhas.append(f"")

    if similares:
        linhas.append(f"### Para defesa (se contestarem):")
        linhas.append(f"")
        linhas.append(f"> Os honorários propostos encontram respaldo na jurisprudência pátria. "
                      f"Em caso similar ({similares[0].get('tribunal', '')} — "
                      f"{similares[0].get('numero', '')}), os honorários periciais foram "
                      f"fixados/mantidos, reconhecendo-se a complexidade do trabalho pericial "
                      f"e a necessidade de remuneração condizente com a qualificação técnica "
                      f"exigida do profissional.")
        linhas.append(f"")

    linhas.append(f"---")
    linhas.append(f"*Gerado automaticamente pelo Sistema de Jurisprudência e Honorários — Stemmia Forense*")

    return "\n".join(linhas)


def executar_gerador_argumentos(conn) -> dict:
    """Gera argumentos para todos os casos pendentes."""
    stats = {"gerados": 0, "sem_dados": 0}

    casos = obter_casos(conn)

    for caso in casos:
        caso_id = caso["id"]
        cnj = caso["numero_cnj"]
        tipo = normalizar_tipo(caso.get("area", ""))

        # Buscar similares
        similares = obter_similares(conn, caso_id, limite=5)

        # Calcular estatísticas
        estatisticas = calcular_estatisticas_tipo(conn, tipo)

        # Gerar markdown
        conteudo = gerar_markdown(caso, similares, estatisticas, conn)

        # Salvar no banco
        inserir_argumentos(conn, caso_id, conteudo)

        # Salvar como arquivo na pasta do processo
        pasta = caso.get("pasta", "")
        if pasta and Path(pasta).exists():
            # Limpar CNJ para nome de arquivo
            cnj_limpo = cnj.replace(".", "-")
            arquivo = Path(pasta) / f"ARGUMENTOS-{cnj_limpo}.md"
            arquivo.write_text(conteudo, encoding="utf-8")
            logger.debug(f"  {cnj}: salvo em {arquivo.name}")
            stats["gerados"] += 1
        else:
            stats["sem_dados"] += 1
            logger.debug(f"  {cnj}: pasta não encontrada, salvo apenas no banco")

    logger.info(f"  Resultado: {stats['gerados']} arquivos gerados, "
                f"{stats['sem_dados']} sem pasta")
    return stats
