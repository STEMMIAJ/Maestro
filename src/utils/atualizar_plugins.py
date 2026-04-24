#!/usr/bin/env python3
"""
Escaneia ~/.claude/plugins/ e atualiza os documentos em ~/Desktop/PLUGINS CLAUDE/
- PLUGINS-INSTALADOS.md: regenera com tudo que encontrar
- Detecta plugins novos comparando com o estado anterior
"""

import os
import json
from pathlib import Path
from datetime import datetime

PLUGINS_DIR = Path.home() / ".claude" / "plugins"
OUTPUT_DIR = Path.home() / "Desktop" / "PLUGINS CLAUDE"
INSTALADOS_FILE = OUTPUT_DIR / "PLUGINS-INSTALADOS.md"
NOVOS_FILE = OUTPUT_DIR / "PLUGINS-NOVOS.md"
STATE_FILE = OUTPUT_DIR / ".plugins-state.json"


def scan_plugin(plugin_path):
    """Escaneia um plugin e retorna seus componentes."""
    info = {
        "name": plugin_path.name,
        "path": str(plugin_path),
        "skills": [],
        "agents": [],
        "commands": [],
        "hooks": False,
    }

    skills_dir = plugin_path / "skills"
    if skills_dir.exists():
        info["skills"] = sorted([
            d.name for d in skills_dir.iterdir()
            if d.is_dir() or d.suffix == ".md"
        ])

    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        info["agents"] = sorted([
            f.stem for f in agents_dir.iterdir()
            if f.suffix == ".md"
        ])

    commands_dir = plugin_path / "commands"
    if commands_dir.exists():
        info["commands"] = sorted([
            f.stem for f in commands_dir.iterdir()
            if f.suffix == ".md"
        ])

    hooks_file = plugin_path / "hooks" / "hooks.json"
    if hooks_file.exists():
        info["hooks"] = True

    return info


def scan_marketplace(marketplace_path):
    """Escaneia plugins dentro de um marketplace."""
    plugins = []
    plugins_dir = marketplace_path / "plugins"
    external_dir = marketplace_path / "external_plugins"

    for search_dir, category in [(plugins_dir, "oficial"), (external_dir, "externo")]:
        if search_dir.exists():
            for item in sorted(search_dir.iterdir()):
                if item.is_dir() and not item.name.startswith("."):
                    plugins.append({
                        "name": item.name,
                        "path": str(item),
                        "category": category,
                    })

    # Se nao tem plugins/ nem external_plugins/, verificar plugins na raiz
    if not plugins:
        skip_files = {".git", ".github", "README.md", "LICENSE", "marketplace.json"}
        for item in sorted(marketplace_path.iterdir()):
            if item.is_dir() and item.name not in skip_files and not item.name.startswith("."):
                # Verificar se parece plugin (tem skills/, commands/, agents/ ou .claude-plugin/)
                has_plugin_structure = any(
                    (item / d).exists()
                    for d in ["skills", "commands", "agents", "hooks", ".claude-plugin"]
                )
                if has_plugin_structure:
                    plugins.append({
                        "name": item.name,
                        "path": str(item),
                        "category": marketplace_path.name,
                    })

    return plugins


def load_previous_state():
    """Carrega estado anterior para detectar novos plugins."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"plugins": [], "timestamp": None}


def save_state(plugin_names):
    """Salva estado atual."""
    state = {
        "plugins": sorted(plugin_names),
        "timestamp": datetime.now().isoformat(),
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def generate_instalados(own_plugins, marketplace_plugins, superpowers_name):
    """Gera o conteudo do PLUGINS-INSTALADOS.md."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    lines = [
        "# Plugins Instalados — Claude Code",
        "",
        f"**Ultima atualizacao:** {now}",
        "**Localização base:** `~/.claude/plugins/`",
        "",
        "---",
        "",
        "## Plugins Próprios",
        "",
    ]

    for p in own_plugins:
        lines.append(f"### {p['name']}")
        lines.append(f"**Localização:** `{p['path']}`")
        if p["skills"]:
            lines.append(f"**Skills ({len(p['skills'])}):** {', '.join(p['skills'])}")
        if p["agents"]:
            lines.append(f"**Agentes ({len(p['agents'])}):** {', '.join(p['agents'])}")
        if p["commands"]:
            lines.append(f"**Commands ({len(p['commands'])}):** {', '.join(p['commands'])}")
        if p["hooks"]:
            lines.append("**Hooks:** sim")
        lines.append("")

    # Marketplace
    oficiais = [p for p in marketplace_plugins if p.get("category") == "oficial"]
    externos = [p for p in marketplace_plugins if p.get("category") == "externo"]

    if oficiais:
        lines.append("---")
        lines.append("")
        lines.append("## Marketplace Oficial")
        lines.append("")
        lines.append("| Plugin | Localização |")
        lines.append("|---|---|")
        for p in oficiais:
            lines.append(f"| {p['name']} | `{p['path']}` |")
        lines.append("")

    if externos:
        lines.append("---")
        lines.append("")
        lines.append("## Integrações Externas")
        lines.append("")
        lines.append("| Plugin | Localização |")
        lines.append("|---|---|")
        for p in externos:
            lines.append(f"| {p['name']} | `{p['path']}` |")
        lines.append("")

    if superpowers_name:
        lines.append("---")
        lines.append("")
        lines.append("## Superpowers Marketplace")
        lines.append(f"**Localização:** `{superpowers_name}`")
        lines.append("")

    # Totais
    total_own_skills = sum(len(p["skills"]) for p in own_plugins)
    total_own_agents = sum(len(p["agents"]) for p in own_plugins)
    total_own_commands = sum(len(p["commands"]) for p in own_plugins)
    total_marketplace = len(oficiais) + len(externos)

    lines.append("---")
    lines.append("")
    lines.append("## Totais")
    lines.append("")
    lines.append(f"- Plugins próprios: {len(own_plugins)}")
    lines.append(f"- Skills próprias: {total_own_skills}")
    lines.append(f"- Agentes próprios: {total_own_agents}")
    lines.append(f"- Commands próprios: {total_own_commands}")
    lines.append(f"- Plugins marketplace: {total_marketplace}")
    lines.append(f"- Total geral: {len(own_plugins) + total_marketplace} plugins")
    lines.append("")

    return "\n".join(lines)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    previous_state = load_previous_state()
    previous_plugins = set(previous_state.get("plugins", []))

    # Escanear plugins proprios (excluindo cache e marketplaces)
    own_plugins = []
    skip_dirs = {"cache", "marketplaces"}

    for item in sorted(PLUGINS_DIR.iterdir()):
        if item.is_dir() and item.name not in skip_dirs and not item.name.startswith("."):
            own_plugins.append(scan_plugin(item))

    # Escanear marketplaces
    marketplace_plugins = []
    superpowers_path = None
    marketplaces_dir = PLUGINS_DIR / "marketplaces"

    if marketplaces_dir.exists():
        for mkt in sorted(marketplaces_dir.iterdir()):
            if mkt.is_dir():
                if "superpowers" in mkt.name:
                    superpowers_path = str(mkt)
                else:
                    marketplace_plugins.extend(scan_marketplace(mkt))

    # Gerar PLUGINS-INSTALADOS.md
    content = generate_instalados(own_plugins, marketplace_plugins, superpowers_path)
    with open(INSTALADOS_FILE, "w") as f:
        f.write(content)

    # Detectar novos
    all_names = set()
    for p in own_plugins:
        all_names.add(p["name"])
    for p in marketplace_plugins:
        all_names.add(p["name"])

    new_plugins = all_names - previous_plugins

    # Salvar estado
    save_state(list(all_names))

    # Relatorio
    print(f"Plugins próprios: {len(own_plugins)}")
    print(f"Plugins marketplace: {len(marketplace_plugins)}")
    print(f"Total: {len(all_names)}")

    if new_plugins:
        print(f"\nNovos detectados ({len(new_plugins)}):")
        for name in sorted(new_plugins):
            print(f"  + {name}")
        print(f"\nAdicione as entradas em: {NOVOS_FILE}")
    else:
        print("\nNenhum plugin novo detectado.")

    print(f"\nAtualizado: {INSTALADOS_FILE}")


if __name__ == "__main__":
    main()
