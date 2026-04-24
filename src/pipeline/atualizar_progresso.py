#!/usr/bin/env python3
"""
atualizar_progresso.py — Atualiza o dashboard PROGRESSO.html programaticamente.

Uso:
  python3 atualizar_progresso.py --marcar "Pipeline PDF testado" --status feito
  python3 atualizar_progresso.py --marcar "Configurar credencial Telegram no N8N" --status feito
  python3 atualizar_progresso.py --adicionar "Nova tarefa qualquer" --status pendente
  python3 atualizar_progresso.py --historico "Executei o scanner de processos"
  python3 atualizar_progresso.py --resumo

Statuses válidos: feito, progresso, pendente
"""

import argparse
import re
import sys
import os
from datetime import datetime

PROGRESSO_PATH = os.path.expanduser(
    "~/Desktop/AUTOMAÇÃO PROCESSUAL/PROGRESSO.html"
)


def ler_html():
    """Lê o arquivo PROGRESSO.html e retorna o conteúdo."""
    if not os.path.exists(PROGRESSO_PATH):
        print(f"ERRO: Arquivo não encontrado: {PROGRESSO_PATH}")
        sys.exit(1)
    with open(PROGRESSO_PATH, "r", encoding="utf-8") as f:
        return f.read()


def salvar_html(conteudo):
    """Salva o conteúdo no PROGRESSO.html."""
    with open(PROGRESSO_PATH, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"OK: PROGRESSO.html atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")


def gerar_task_id(nome):
    """Gera um ID de tarefa a partir do nome."""
    return re.sub(r'[^a-z0-9]+', '-', nome.lower()).strip('-')[:40]


def contar_tarefas(html):
    """Conta tarefas por status no HTML."""
    feitas = len(re.findall(r'data-status="feito"', html))
    progresso = len(re.findall(r'data-status="progresso"', html))
    pendentes = len(re.findall(r'data-status="pendente"', html))
    total = feitas + progresso + pendentes
    return feitas, progresso, pendentes, total


def atualizar_contadores(html):
    """Recalcula e atualiza todos os contadores e barra de progresso."""
    feitas, progresso, pendentes, total = contar_tarefas(html)
    pct = int((feitas / total) * 100) if total > 0 else 0

    # Classe da barra
    if pct < 30:
        fill_class = "low"
    elif pct < 55:
        fill_class = "mid"
    elif pct < 80:
        fill_class = "good"
    else:
        fill_class = "great"

    # Atualizar percentual display
    html = re.sub(
        r'<span class="pct" id="pct-display">\d+%</span>',
        f'<span class="pct" id="pct-display">{pct}%</span>',
        html
    )

    # Atualizar barra de progresso
    html = re.sub(
        r'<div class="fill \w+" id="progress-fill" style="width: \d+%;"',
        f'<div class="fill {fill_class}" id="progress-fill" style="width: {pct}%;"',
        html
    )

    # Atualizar contadores
    html = re.sub(
        r'<div class="num" id="count-feito">\d+</div>',
        f'<div class="num" id="count-feito">{feitas}</div>',
        html
    )
    html = re.sub(
        r'<div class="num" id="count-progresso">\d+</div>',
        f'<div class="num" id="count-progresso">{progresso}</div>',
        html
    )
    html = re.sub(
        r'<div class="num" id="count-pendente">\d+</div>',
        f'<div class="num" id="count-pendente">{pendentes}</div>',
        html
    )

    # Atualizar badges das seções
    html = re.sub(
        r'(Feito Hoje <span class="badge verde">)\d+ tarefas',
        f'\\g<1>{feitas} tarefas',
        html
    )
    html = re.sub(
        r'(Em Progresso <span class="badge amarelo">)\d+ tarefas',
        f'\\g<1>{progresso} tarefas',
        html
    )
    html = re.sub(
        r'(Pendente <span class="badge cinza">)\d+ tarefas',
        f'\\g<1>{pendentes} tarefas',
        html
    )

    # Atualizar metadata
    agora = datetime.now().strftime("%Y-%m-%d")
    html = re.sub(
        r'"ultima_atualizacao": "[^"]*"',
        f'"ultima_atualizacao": "{agora}"',
        html
    )
    html = re.sub(
        r'"total_tarefas": \d+',
        f'"total_tarefas": {total}',
        html
    )
    html = re.sub(
        r'"feitas": \d+',
        f'"feitas": {feitas}',
        html
    )
    html = re.sub(
        r'"em_progresso": \d+',
        f'"em_progresso": {progresso}',
        html
    )
    html = re.sub(
        r'"pendentes": \d+',
        f'"pendentes": {pendentes}',
        html
    )

    # Atualizar data de exibição
    agora_display = datetime.now().strftime("%d de %B de %Y").replace(
        "January", "janeiro").replace("February", "fevereiro").replace(
        "March", "mar&ccedil;o").replace("April", "abril").replace(
        "May", "maio").replace("June", "junho").replace(
        "July", "julho").replace("August", "agosto").replace(
        "September", "setembro").replace("October", "outubro").replace(
        "November", "novembro").replace("December", "dezembro")
    html = re.sub(
        r'<span id="last-update">[^<]*</span>',
        f'<span id="last-update">{agora_display}</span>',
        html
    )

    return html


def marcar_tarefa(html, nome_tarefa, novo_status):
    """
    Encontra uma tarefa pelo texto (busca parcial, case-insensitive)
    e muda seu status.
    """
    # Mapear status para ícone e classe
    status_map = {
        "feito": {"icon_class": "feito", "icon_char": "&#10003;"},
        "progresso": {"icon_class": "progresso", "icon_char": "&#8943;"},
        "pendente": {"icon_class": "pendente", "icon_char": "&bull;"},
    }

    if novo_status not in status_map:
        print(f"ERRO: Status inválido '{novo_status}'. Use: feito, progresso, pendente")
        sys.exit(1)

    # Buscar a tarefa pelo texto (case-insensitive, parcial)
    # Procura por data-task-id ou pelo texto dentro do <strong>
    nome_lower = nome_tarefa.lower()

    # Padrão: encontrar o <li> que contém o texto da tarefa
    pattern = re.compile(
        r'(<li\s+data-task-id="[^"]*"\s+data-status=")(\w+)(".*?</li>)',
        re.DOTALL
    )

    encontrou = False
    def substituir(match):
        nonlocal encontrou
        bloco = match.group(0)
        # Extrair o texto visível do bloco
        texto_visivel = re.sub(r'<[^>]+>', '', bloco).lower()
        texto_visivel = texto_visivel.replace('&amp;', '&').replace('&mdash;', '—')

        if nome_lower in texto_visivel or nome_lower.replace(' ', '-') in bloco.lower():
            encontrou = True
            info = status_map[novo_status]

            # Substituir data-status
            novo_bloco = re.sub(
                r'data-status="\w+"',
                f'data-status="{novo_status}"',
                bloco
            )
            # Substituir classe do ícone
            novo_bloco = re.sub(
                r'<div class="icon \w+">',
                f'<div class="icon {info["icon_class"]}">',
                novo_bloco
            )
            # Substituir char do ícone
            novo_bloco = re.sub(
                r'<div class="icon [^"]*">[^<]*</div>',
                f'<div class="icon {info["icon_class"]}">{info["icon_char"]}</div>',
                novo_bloco
            )
            return novo_bloco
        return bloco

    html = pattern.sub(substituir, html)

    if encontrou:
        # Se mudou de seção (ex: pendente -> feito), mover o bloco
        # Por simplicidade, apenas atualiza o status inline
        print(f"OK: '{nome_tarefa}' marcado como [{novo_status}]")
    else:
        print(f"AVISO: Tarefa '{nome_tarefa}' não encontrada no HTML.")
        print("       Tente usar parte do nome da tarefa (busca parcial).")
        return html

    return atualizar_contadores(html)


def adicionar_tarefa(html, nome_tarefa, status="pendente"):
    """Adiciona uma nova tarefa na seção correspondente ao status."""
    status_map = {
        "feito": {"icon_class": "feito", "icon_char": "&#10003;", "section_id": "feito"},
        "progresso": {"icon_class": "progresso", "icon_char": "&#8943;", "section_id": "em-progresso"},
        "pendente": {"icon_class": "pendente", "icon_char": "&bull;", "section_id": "pendente"},
    }

    if status not in status_map:
        print(f"ERRO: Status inválido '{status}'. Use: feito, progresso, pendente")
        sys.exit(1)

    info = status_map[status]
    task_id = gerar_task_id(nome_tarefa)

    nova_tarefa = f'''      <li data-task-id="{task_id}" data-status="{status}">
        <div class="icon {info['icon_class']}">{info['icon_char']}</div>
        <div class="task-text">
          <strong>{nome_tarefa}</strong>
          <span class="detail">Adicionado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
        </div>
      </li>'''

    # Encontrar o final da lista da seção correspondente
    section_id = info["section_id"]
    # Inserir antes do </ul> da seção
    pattern = f'(id="{section_id}".*?)(</ul>)'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        pos = match.start(2)
        html = html[:pos] + nova_tarefa + "\n    " + html[pos:]
        print(f"OK: Tarefa '{nome_tarefa}' adicionada como [{status}]")
    else:
        print(f"ERRO: Não encontrou seção '{section_id}' no HTML")
        return html

    return atualizar_contadores(html)


def adicionar_historico(html, acao):
    """Adiciona uma entrada no histórico."""
    agora = datetime.now()
    periodo = "Manhã" if agora.hour < 12 else "Tarde" if agora.hour < 18 else "Noite"
    data_str = agora.strftime(f"%d/%b/%Y").replace(
        "Jan", "jan").replace("Feb", "fev").replace("Mar", "mar").replace(
        "Apr", "abr").replace("May", "mai").replace("Jun", "jun").replace(
        "Jul", "jul").replace("Aug", "ago").replace("Sep", "set").replace(
        "Oct", "out").replace("Nov", "nov").replace("Dec", "dez")

    nova_entrada = f'''      <li>
        <div class="time">{data_str} &mdash; {periodo}</div>
        <div class="action">{acao}</div>
      </li>'''

    # Inserir no início da timeline (após <ul class="timeline">)
    pattern = r'(<ul class="timeline">)\s*\n'
    match = re.search(pattern, html)
    if match:
        pos = match.end()
        html = html[:pos] + nova_entrada + "\n" + html[pos:]
        print(f"OK: Histórico adicionado: '{acao}'")
    else:
        print("ERRO: Não encontrou a timeline no HTML")

    return html


def mostrar_resumo(html):
    """Mostra um resumo do progresso atual."""
    feitas, progresso, pendentes, total = contar_tarefas(html)
    pct = int((feitas / total) * 100) if total > 0 else 0

    print("=" * 50)
    print("  PROGRESSO — AUTOMAÇÃO PROCESSUAL")
    print("=" * 50)
    print(f"  Total de tarefas: {total}")
    print(f"  Concluídas:       {feitas} ({pct}%)")
    print(f"  Em progresso:     {progresso}")
    print(f"  Pendentes:        {pendentes}")
    print("=" * 50)

    # Listar tarefas pendentes
    if pendentes > 0:
        print("\n  PENDENTES:")
        for m in re.finditer(r'data-status="pendente".*?<strong>(.*?)</strong>', html, re.DOTALL):
            texto = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            print(f"    - {texto}")

    # Listar em progresso
    if progresso > 0:
        print("\n  EM PROGRESSO:")
        for m in re.finditer(r'data-status="progresso".*?<strong>(.*?)</strong>', html, re.DOTALL):
            texto = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            print(f"    - {texto}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Atualizar o dashboard PROGRESSO.html da Stemmia Forense"
    )
    parser.add_argument(
        "--marcar", type=str,
        help="Nome (parcial) da tarefa a ser atualizada"
    )
    parser.add_argument(
        "--status", type=str, choices=["feito", "progresso", "pendente"],
        help="Novo status da tarefa"
    )
    parser.add_argument(
        "--adicionar", type=str,
        help="Adicionar nova tarefa ao dashboard"
    )
    parser.add_argument(
        "--historico", type=str,
        help="Adicionar entrada ao histórico de ações"
    )
    parser.add_argument(
        "--resumo", action="store_true",
        help="Mostrar resumo do progresso atual"
    )

    args = parser.parse_args()

    if not any([args.marcar, args.adicionar, args.historico, args.resumo]):
        parser.print_help()
        sys.exit(0)

    html = ler_html()

    if args.resumo:
        mostrar_resumo(html)
        return

    if args.marcar:
        if not args.status:
            print("ERRO: --marcar requer --status (feito|progresso|pendente)")
            sys.exit(1)
        html = marcar_tarefa(html, args.marcar, args.status)
        salvar_html(html)

    elif args.adicionar:
        status = args.status or "pendente"
        html = adicionar_tarefa(html, args.adicionar, status)
        # Também adicionar ao histórico
        html = adicionar_historico(html, f"Tarefa adicionada: {args.adicionar}")
        salvar_html(html)

    elif args.historico:
        html = adicionar_historico(html, args.historico)
        salvar_html(html)


if __name__ == "__main__":
    main()
