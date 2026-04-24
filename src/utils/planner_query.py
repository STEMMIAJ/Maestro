#!/usr/bin/env python3
"""Consulta o planner_state.json via linha de comando.
Uso: python3 planner_query.py <comando> [args]

Comandos:
  hoje       Próxima ação + urgentes + atrasadas
  urgentes   Tarefas urgentes pendentes
  atrasadas  Tarefas com deadline vencido
  semana     Vencendo nos próximos 7 dias
  blocos     Resumo por bloco
  bloco X    Tarefas de um bloco específico
  inbox      Itens na inbox
  meds       Medicamentos contínuos
  stats      Estatísticas gerais
  add "txt"  Adicionar à inbox
  feito ID   Marcar/desmarcar como feito
"""

import json
import os
import sys
from datetime import datetime, date

STATE_PATH = os.path.expanduser("~/Desktop/Projetos - Plan Mode/agenda-pericial/data/planner_state.json")
PATCHES_PATH = os.path.join(os.path.dirname(STATE_PATH), "telegram_patches.json")
SKIP_TYPES = {"today", "medications", "inbox", "pericial"}


def load_state():
    if not os.path.exists(STATE_PATH):
        print("ERRO: planner_state.json não encontrado")
        sys.exit(1)
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def save_patch(patch):
    patches = []
    if os.path.exists(PATCHES_PATH):
        try:
            with open(PATCHES_PATH, "r", encoding="utf-8") as f:
                patches = json.load(f)
        except (json.JSONDecodeError, ValueError):
            patches = []
    patch["timestamp"] = datetime.now().isoformat()
    patches.append(patch)
    with open(PATCHES_PATH, "w", encoding="utf-8") as f:
        json.dump(patches, f, ensure_ascii=False, indent=2)


def all_tasks(state):
    results = []
    for block in state.get("blocks", []):
        if block.get("type", "") in SKIP_TYPES:
            continue
        for section in block.get("sections", []):
            for task in section.get("tasks", []):
                results.append((block["name"], block.get("icon", ""), section["name"], task))
    return results


def cmd_hoje(state):
    today = date.today()
    # Próxima ação
    candidates = []
    for bname, bicon, sname, t in all_tasks(state):
        if t.get("done"):
            continue
        dl_days = 9999
        if t.get("deadline"):
            try:
                dl_days = (date.fromisoformat(t["deadline"]) - today).days
            except (ValueError, TypeError):
                pass
        if t.get("urgency") == "high":
            candidates.append((dl_days, bname, bicon, sname, t))
    if not candidates:
        for bname, bicon, sname, t in all_tasks(state):
            if not t.get("done"):
                dl_days = 9999
                if t.get("deadline"):
                    try:
                        dl_days = (date.fromisoformat(t["deadline"]) - today).days
                    except (ValueError, TypeError):
                        pass
                candidates.append((dl_days, bname, bicon, sname, t))
    if candidates:
        candidates.sort(key=lambda x: x[0])
        dl_days, bname, bicon, sname, t = candidates[0]
        dl_str = t.get("deadline", "sem prazo")
        print(f"PRÓXIMA AÇÃO: {t['text']}")
        print(f"  Bloco: {bicon} {bname} > {sname}")
        if dl_days < 9999:
            print(f"  Prazo: {dl_str} ({dl_days}d)")
    else:
        print("Nenhuma tarefa pendente!")

    # Urgentes
    urgent = [(b, i, s, t) for b, i, s, t in all_tasks(state)
              if t.get("urgency") == "high" and not t.get("done")]
    if urgent:
        print(f"\nURGENTES ({len(urgent)}):")
        for bname, bicon, sname, t in urgent[:10]:
            print(f"  * {t['text']} [{bicon} {bname}]")

    # Atrasadas
    overdue = []
    for bname, bicon, sname, t in all_tasks(state):
        if t.get("done") or not t.get("deadline"):
            continue
        try:
            dl = date.fromisoformat(t["deadline"])
            if dl < today:
                overdue.append((t, (today - dl).days, bname))
        except (ValueError, TypeError):
            continue
    overdue.sort(key=lambda x: x[1], reverse=True)
    if overdue:
        print(f"\nATRASADAS ({len(overdue)}):")
        for t, days, bname in overdue[:10]:
            print(f"  * {t['text']} ({days}d atraso) [{bname}]")


def cmd_urgentes(state):
    urgent = [(b, i, s, t) for b, i, s, t in all_tasks(state)
              if t.get("urgency") == "high" and not t.get("done")]
    if not urgent:
        print("Nenhuma tarefa urgente!")
        return
    print(f"URGENTES ({len(urgent)}):")
    for bname, bicon, sname, t in urgent:
        dl = t.get("deadline", "")
        dl_str = f" [prazo: {dl}]" if dl else ""
        tid = t.get("id", "?")
        print(f"  * {t['text']}{dl_str} ({bicon} {bname}) ID:{tid}")


def cmd_atrasadas(state):
    today = date.today()
    overdue = []
    for bname, bicon, sname, t in all_tasks(state):
        if t.get("done") or not t.get("deadline"):
            continue
        try:
            dl = date.fromisoformat(t["deadline"])
            if dl < today:
                overdue.append((bname, bicon, t, (today - dl).days))
        except (ValueError, TypeError):
            continue
    overdue.sort(key=lambda x: x[3], reverse=True)
    if not overdue:
        print("Nenhuma tarefa atrasada!")
        return
    print(f"ATRASADAS ({len(overdue)}):")
    for bname, bicon, t, days in overdue:
        tid = t.get("id", "?")
        print(f"  * {t['text']} ({days}d atraso) [{bicon} {bname}] ID:{tid}")


def cmd_semana(state):
    today = date.today()
    week = []
    for bname, bicon, sname, t in all_tasks(state):
        if t.get("done") or not t.get("deadline"):
            continue
        try:
            dl = date.fromisoformat(t["deadline"])
            diff = (dl - today).days
            if 0 <= diff <= 7:
                week.append((bname, bicon, t, diff))
        except (ValueError, TypeError):
            continue
    week.sort(key=lambda x: x[3])
    if not week:
        print("Nenhum prazo nos próximos 7 dias!")
        return
    print(f"PRÓXIMOS 7 DIAS ({len(week)}):")
    for bname, bicon, t, diff in week:
        dia = "HOJE" if diff == 0 else f"AMANHÃ" if diff == 1 else f"{diff}d"
        print(f"  * {t['text']} [{dia}] ({bicon} {bname})")


def cmd_blocos(state):
    print("BLOCOS:")
    for block in state.get("blocks", []):
        btype = block.get("type", "")
        if btype in ("today", "inbox", "pericial"):
            continue
        total = done = urgent = 0
        for section in block.get("sections", []):
            for task in section.get("tasks", []):
                total += 1
                if task.get("done"):
                    done += 1
                elif task.get("urgency") == "high":
                    urgent += 1
        pct = int(done / total * 100) if total > 0 else 0
        icon = block.get("icon", "")
        urg_str = f" ({urgent} urgentes)" if urgent else ""
        print(f"  {icon} {block['name']}: {done}/{total} ({pct}%){urg_str}")


def cmd_bloco(state, query):
    query_lower = query.lower().strip()
    for block in state.get("blocks", []):
        if query_lower in block["name"].lower() or query_lower in block.get("id", "").lower():
            icon = block.get("icon", "")
            print(f"{icon} {block['name']}:")
            for section in block.get("sections", []):
                print(f"\n  {section['name']}:")
                for task in section.get("tasks", []):
                    check = "x" if task.get("done") else " "
                    urg = " *URGENTE*" if task.get("urgency") == "high" and not task.get("done") else ""
                    dl = f" [prazo: {task['deadline']}]" if task.get("deadline") else ""
                    tid = task.get("id", "")
                    print(f"    [{check}] {task['text']}{urg}{dl} ID:{tid}")
            return
    print(f"Bloco '{query}' não encontrado. Use 'blocos' para ver a lista.")


def cmd_inbox(state):
    items = state.get("inbox", [])
    if not items:
        print("Inbox vazia!")
        return
    print(f"INBOX ({len(items)}):")
    for item in items:
        dt = item.get("date", "")[:10]
        print(f"  * {item['text']} [{dt}]")


def cmd_meds(state):
    for block in state.get("blocks", []):
        if block.get("type") == "medications":
            meds = block.get("medications", {}).get("continuous", [])
            if not meds:
                print("Nenhum medicamento registrado.")
                return
            print("MEDICAMENTOS CONTÍNUOS:")
            for m in meds:
                nome = m.get("name", "?")
                pos = m.get("posologia", "")
                rec = m.get("receita", "")
                print(f"  * {nome}")
                if pos:
                    print(f"    Posologia: {pos}")
                if rec:
                    print(f"    Receita: {rec}")
            return
    print("Bloco de medicamentos não encontrado.")


def cmd_stats(state):
    today = date.today()
    total = done_count = urgent = overdue = 0
    for bname, bicon, sname, t in all_tasks(state):
        total += 1
        if t.get("done"):
            done_count += 1
        else:
            if t.get("urgency") == "high":
                urgent += 1
            if t.get("deadline"):
                try:
                    if date.fromisoformat(t["deadline"]) < today:
                        overdue += 1
                except (ValueError, TypeError):
                    pass
    pending = total - done_count
    pct = int(done_count / total * 100) if total > 0 else 0
    inbox_count = len(state.get("inbox", []))
    print(f"ESTATÍSTICAS DO PLANNER:")
    print(f"  Total: {total} tarefas")
    print(f"  Feitas: {done_count} ({pct}%)")
    print(f"  Pendentes: {pending}")
    print(f"  Urgentes: {urgent}")
    print(f"  Atrasadas: {overdue}")
    print(f"  Inbox: {inbox_count} itens")


def cmd_add(state, text):
    if "inbox" not in state:
        state["inbox"] = []
    state["inbox"].append({
        "text": text,
        "date": datetime.now().isoformat(),
    })
    save_state(state)
    save_patch({"action": "add_inbox", "text": text})
    print(f"Adicionado à inbox: {text}")


def cmd_feito(state, task_id):
    for block in state.get("blocks", []):
        for section in block.get("sections", []):
            for task in section.get("tasks", []):
                if task.get("id") == task_id:
                    task["done"] = not task.get("done", False)
                    save_state(state)
                    save_patch({"action": "toggle_done", "task_id": task_id, "done": task["done"]})
                    status = "FEITO" if task["done"] else "DESFEITO"
                    print(f"{status}: {task['text']}")
                    return
    print(f"Tarefa '{task_id}' não encontrada.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()
    state = load_state()

    if cmd == "hoje":
        cmd_hoje(state)
    elif cmd == "urgentes":
        cmd_urgentes(state)
    elif cmd == "atrasadas":
        cmd_atrasadas(state)
    elif cmd == "semana":
        cmd_semana(state)
    elif cmd == "blocos":
        cmd_blocos(state)
    elif cmd == "bloco":
        if len(sys.argv) < 3:
            print("Uso: planner_query.py bloco <nome>")
            sys.exit(1)
        cmd_bloco(state, " ".join(sys.argv[2:]))
    elif cmd == "inbox":
        cmd_inbox(state)
    elif cmd == "meds":
        cmd_meds(state)
    elif cmd == "stats":
        cmd_stats(state)
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("Uso: planner_query.py add <texto>")
            sys.exit(1)
        cmd_add(state, " ".join(sys.argv[2:]))
    elif cmd == "feito":
        if len(sys.argv) < 3:
            print("Uso: planner_query.py feito <id>")
            sys.exit(1)
        cmd_feito(state, sys.argv[2])
    else:
        print(f"Comando desconhecido: {cmd}")
        print("Use: hoje, urgentes, atrasadas, semana, blocos, bloco, inbox, meds, stats, add, feito")
        sys.exit(1)


if __name__ == "__main__":
    main()
