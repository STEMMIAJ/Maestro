#!/usr/bin/env python3
"""
deploy_site.py — Upload de arquivos para stemmia.com.br + notificação Telegram
===============================================================================
Sobe arquivos para o site via FTP e notifica no Telegram.

Uso:
    python3 deploy_site.py arquivo1.pdf arquivo2.html
    python3 deploy_site.py ~/Desktop/GUIA-COMPLETO-STEMMIA.pdf --notify
    python3 deploy_site.py --all-from ~/Desktop/*.pdf

Flags:
    --notify    Envia notificação no Telegram após upload (padrão: sim)
    --no-notify Não envia notificação
    --dry-run   Mostra o que faria sem executar
"""

import ftplib
import os
import sys
import time
from pathlib import Path

# ── Configuração FTP ──
FTP_HOST = "alvorada.nuvemidc.com"
FTP_USER = "deploy@stemmia.com.br"
FTP_PASS = "@$xHQ[c*B&mqUj]R"
SITE_URL = "https://stemmia.com.br/webdev"

# ── Configuração Telegram ──
TELEGRAM_CHAT_ID = "8397602236"


def _carregar_token_telegram():
    """Carrega token do Telegram de arquivo ou variável de ambiente."""
    if os.environ.get("TELEGRAM_BOT_TOKEN"):
        return os.environ["TELEGRAM_BOT_TOKEN"]
    for path in [
        Path(__file__).parent / ".telegram-token",
        Path.home() / ".telegram-token",
    ]:
        if path.exists():
            return path.read_text().strip()
    return None


def upload_ftp(filepath, remote_name=None):
    """Sobe um arquivo via FTP. Retorna True se sucesso."""
    filepath = Path(filepath).expanduser().resolve()
    if not filepath.exists():
        print(f"  ERRO: {filepath} não existe")
        return False

    if remote_name is None:
        remote_name = filepath.name

    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, 21, timeout=120)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.set_pasv(True)

        size = filepath.stat().st_size
        print(f"  Subindo {remote_name} ({size:,} bytes)...", end=" ", flush=True)

        with open(filepath, "rb") as f:
            ftp.storbinary(f"STOR {remote_name}", f)

        ftp.quit()
        print("OK")
        return True

    except Exception as e:
        print(f"FALHOU: {e}")
        return False


def notificar_telegram(mensagem):
    """Envia notificação no Telegram."""
    token = _carregar_token_telegram()
    if not token:
        print("  [Telegram] Token não encontrado, pulando notificação")
        return False

    import urllib.request
    import urllib.error
    import json

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML",
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        print("  [Telegram] Notificação enviada")
        return True
    except Exception as e:
        print(f"  [Telegram] Falhou: {e}")
        return False


def main():
    args = sys.argv[1:]
    notify = True
    dry_run = False
    files = []

    for arg in args:
        if arg == "--no-notify":
            notify = False
        elif arg == "--notify":
            notify = True
        elif arg == "--dry-run":
            dry_run = True
        else:
            # Expandir globs
            p = Path(arg).expanduser()
            if p.exists():
                files.append(str(p))
            else:
                print(f"Arquivo não encontrado: {arg}")

    if not files:
        print("Uso: python3 deploy_site.py arquivo1 [arquivo2 ...]")
        print("Flags: --notify --no-notify --dry-run")
        sys.exit(1)

    print(f"\n=== Deploy para {SITE_URL} ===\n")

    uploaded = []
    for filepath in files:
        name = Path(filepath).name
        url = f"{SITE_URL}/{name}"

        if dry_run:
            print(f"  [DRY RUN] Subiria {name} → {url}")
            uploaded.append((name, url))
        else:
            if upload_ftp(filepath):
                uploaded.append((name, url))

    if uploaded and notify and not dry_run:
        linhas = [f"<b>Deploy concluído</b> ({len(uploaded)} arquivo{'s' if len(uploaded) > 1 else ''}):\n"]
        for name, url in uploaded:
            linhas.append(f"• {name}")
        linhas.append(f"\n{time.strftime('%d/%m/%Y %H:%M')}")
        notificar_telegram("\n".join(linhas))

    print(f"\n{'DRY RUN — ' if dry_run else ''}{len(uploaded)} arquivo(s) processado(s)")
    if uploaded:
        print("\nURLs:")
        for name, url in uploaded:
            print(f"  {url}")


if __name__ == "__main__":
    main()
