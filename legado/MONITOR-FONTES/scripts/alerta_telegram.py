#!/usr/bin/env python3
"""Detecta novidades entre consolidado de hoje e snapshot de ontem/anterior.
Envia alerta Telegram. Se Chrome deslogado em AJ/AJG, alerta de relogin.
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path.home() / "Desktop" / "MONITOR-FONTES"
CONSOLIDADO = RAIZ / "dados" / "processos-consolidados.json"
HISTORICO = RAIZ / "dados" / "historico"
DADOS = RAIZ / "dados"
CHAT_ID = "8397602236"


def _carregar_token() -> str:
    """Carrega TELEGRAM_BOT_TOKEN do env ou ~/.stemmia/credenciais.env."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        return token
    env_file = Path.home() / ".stemmia" / "credenciais.env"
    if env_file.exists():
        for linha in env_file.read_text().splitlines():
            if linha.startswith("TELEGRAM_BOT_TOKEN="):
                return linha.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def detectar_novos(anterior: list, atual: list) -> list:
    """Retorna itens de 'atual' cujo CNJ nao estava em 'anterior'."""
    cnjs_ant = {p["cnj"] for p in anterior if isinstance(p, dict) and p.get("cnj")}
    return [p for p in atual if isinstance(p, dict) and p.get("cnj") and p["cnj"] not in cnjs_ant]


def precisa_relogin(snapshot_fontes: dict) -> bool:
    """True se AJ ou AJG retornou erro de login/sessao."""
    for fid in ("aj", "ajg"):
        info = snapshot_fontes.get(fid, {})
        if info.get("status") in ("erro", "timeout"):
            erro = str(info.get("erro", "")).lower()
            # Erros tipicos de sessao expirada
            palavras_login = (
                "logi", "logg", "auth", "sess", "cookie", "redirect", "credential",
                "401", "403",
                "connect_over_cdp", "browser con", "cdp", "econnrefused", "refused",
            )
            if any(k in erro for k in palavras_login):
                return True
            # Tambem considera "0 itens" consistente (pode ser sessao expirada silenciosa)
            # — nao alertamos aqui pra nao dar falso positivo
    return False


def enviar(msg: str, token: str = "") -> bool:
    token = token or _carregar_token()
    if not token:
        print("[alerta] TELEGRAM_BOT_TOKEN ausente — pulando envio")
        return False
    try:
        import requests  # import lazy pra nao quebrar testes sem requests
    except ImportError:
        print("[alerta] requests nao instalado — pip3 install requests")
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=10,
        )
        if r.status_code != 200:
            print(f"[alerta] Telegram retornou {r.status_code}: {r.text[:200]}")
            return False
        return True
    except Exception as e:
        print(f"[alerta] erro ao enviar: {e}")
        return False


def _ultimo_consolidado_anterior() -> list:
    """Busca snapshot salvo ontem (ou mais antigo ate 7 dias). [] se nao achar."""
    hoje = datetime.now().date()
    for dias in range(1, 8):
        dia = (hoje - timedelta(days=dias)).strftime("%Y-%m-%d")
        p = DADOS / f"consolidado-{dia}.json"
        if p.exists():
            try:
                return json.loads(p.read_text())
            except json.JSONDecodeError:
                continue
    return []


def main():
    atual = []
    if CONSOLIDADO.exists():
        try:
            atual = json.loads(CONSOLIDADO.read_text())
        except json.JSONDecodeError:
            atual = []

    anterior = _ultimo_consolidado_anterior()

    # Salva snapshot de hoje para comparar amanha
    hoje = datetime.now().strftime("%Y-%m-%d")
    (DADOS / f"consolidado-{hoje}.json").write_text(
        json.dumps(atual, ensure_ascii=False, indent=2)
    )

    # Checa status das fontes
    snapshot_path = HISTORICO / f"{hoje}.json"
    if snapshot_path.exists():
        try:
            snapshot = json.loads(snapshot_path.read_text())
            if precisa_relogin(snapshot):
                msg = (
                    "⚠️ *MONITOR-FONTES: Chrome deslogado*\n\n"
                    "AJ ou AJG retornou erro de autenticacao.\n\n"
                    "Abrir:\n"
                    "`~/Desktop/MONITOR-FONTES/scripts/abrir_chrome_debug.command`\n\n"
                    "Logar em AJ TJMG e AJG novamente."
                )
                enviar(msg)
                print("[alerta] Enviado aviso de relogin")
                return
        except json.JSONDecodeError:
            pass

    novos = detectar_novos(anterior, atual)
    if not novos:
        print(f"[alerta] Sem novidades ({len(atual)} processos, {len(anterior)} anteriores)")
        return

    linhas = [f"🔔 *{len(novos)} processo(s) novo(s)* no MONITOR-FONTES:\n"]
    for n in novos[:15]:
        fontes = "+".join(n.get("fontes", []))
        data = n.get("data_mais_recente") or "?"
        linhas.append(f"• `{n['cnj']}` [{fontes}] — {data}")
    if len(novos) > 15:
        linhas.append(f"\n…e mais {len(novos) - 15}")
    linhas.append(f"\n📂 `~/Desktop/MONITOR-FONTES/dashboard/index.html`")
    enviar("\n".join(linhas))
    print(f"[alerta] Enviado: {len(novos)} novos")


if __name__ == "__main__":
    main()
