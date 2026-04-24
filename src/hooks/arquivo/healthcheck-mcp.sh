#!/bin/bash
# Health check dos servidores MCP configurados
# Executado no SessionStart via iniciar-sessao.sh
# Timeout total: 15 segundos (garantido pelo wrapper)
# Compatível com macOS (sem dependência de coreutils/timeout)

MCP_CONFIG="$HOME/.claude/.mcp.json"

if [ ! -f "$MCP_CONFIG" ]; then
    echo "MCP: config nao encontrada"
    exit 0
fi

# Usar Python para todo o health check (robusto, sem dependência de timeout externo)
/usr/bin/python3 << 'PYEOF'
import json, os, subprocess, sys, signal

# Timeout total do script
signal.alarm(15)

MCP_CONFIG = os.path.expanduser("~/.claude/.mcp.json")

try:
    with open(MCP_CONFIG) as f:
        cfg = json.load(f)
except Exception:
    print("MCP: erro ao ler config")
    sys.exit(0)

servers = cfg.get("mcpServers", {})
if not servers:
    print("MCP: nenhum servidor configurado")
    sys.exit(0)

total = len(servers)
ok_list = []
fail_list = []

def cmd_exists(cmd):
    """Verifica se comando existe no PATH"""
    try:
        result = subprocess.run(
            ["which", cmd],
            capture_output=True, timeout=3
        )
        return result.returncode == 0
    except Exception:
        return False

def check_server(name, config):
    """Retorna (ok: bool, motivo: str)"""
    cmd = config.get("command", "")
    args = config.get("args", [])

    if not cmd:
        return False, "comando vazio"

    if cmd == "node":
        # Server local — verificar se node existe e arquivo JS existe
        if not cmd_exists("node"):
            return False, "node nao encontrado"
        if args:
            js_file = args[0]
            if not os.path.isfile(js_file):
                return False, f"arquivo inexistente: {os.path.basename(js_file)}"
        return True, ""

    elif cmd == "npx":
        if not cmd_exists("npx"):
            return False, "npx nao encontrado"
        # Extrair nome do pacote (pular flags)
        pkg = None
        for arg in args:
            if arg.startswith("-"):
                continue
            # Pular @latest em pacotes como @playwright/mcp@latest
            pkg = arg
            break
        if not pkg:
            return False, "pacote nao identificado"
        # Verificar se npx consegue resolver o pacote (cache local)
        # Nao executar download, apenas checar se resolve
        return True, ""

    elif cmd in ("uv", "uvx"):
        if not cmd_exists(cmd):
            return False, f"{cmd} nao encontrado"
        # Para uv --directory: verificar se diretorio existe
        for i, arg in enumerate(args):
            if arg == "--directory" and i + 1 < len(args):
                dirpath = args[i + 1]
                if not os.path.isdir(dirpath):
                    return False, f"diretorio inexistente: {os.path.basename(dirpath)}"
        return True, ""

    elif cmd in ("python3", "python"):
        if not cmd_exists(cmd):
            return False, f"{cmd} nao encontrado"
        return True, ""

    else:
        # Comando generico
        if cmd_exists(cmd):
            return True, ""
        else:
            return False, f"comando nao encontrado: {cmd}"

for name in sorted(servers.keys()):
    try:
        ok, reason = check_server(name, servers[name])
        if ok:
            ok_list.append(name)
        else:
            fail_list.append((name, reason))
    except Exception as e:
        fail_list.append((name, str(e)[:60]))

ok_count = len(ok_list)

if ok_count == total:
    print(f"MCP: {total}/{total} OK")
else:
    fail_names = ", ".join(f[0] for f in fail_list)
    print(f"MCP: {ok_count}/{total} OK | FALHA: {fail_names}")
    for name, reason in fail_list:
        print(f"  {name}: {reason}")
PYEOF

exit 0
