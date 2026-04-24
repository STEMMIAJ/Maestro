#!/usr/bin/env python3
"""
Notificação via Telegram — Stemmia Forense.

Envia mensagens para o bot @stemmiapericia_bot via API do Telegram.

Uso direto:
  python3 notificar_telegram.py "Mensagem de teste"
  python3 notificar_telegram.py --arquivo relatorio.txt

Como módulo:
  from notificar_telegram import enviar
  enviar("Texto aqui")

CONFIGURAÇÃO:
  Defina o token do bot em uma das opções:
    1. Variável de ambiente TELEGRAM_BOT_TOKEN
    2. Arquivo .telegram-token no diretório scripts/
    3. Arquivo ~/.telegram-token
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

CHAT_ID = "8397602236"
API_URL = "https://api.telegram.org/bot{token}/sendMessage"

# Onde procurar o token (em ordem de prioridade)
TOKEN_PATHS = [
    Path(__file__).parent / ".telegram-token",
    Path.home() / ".telegram-token",
]


def _carregar_token():
    """Carrega bot token de variável de ambiente ou arquivo."""
    # 1. Variável de ambiente
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if token:
        return token

    # 2. Arquivos
    for p in TOKEN_PATHS:
        if p.exists():
            token = p.read_text(encoding="utf-8").strip()
            if token:
                return token

    return None


def enviar(texto, chat_id=None, parse_mode="Markdown"):
    """
    Envia mensagem para o Telegram.

    Args:
        texto: Mensagem (suporta Markdown)
        chat_id: ID do chat (padrão: CHAT_ID do perito)
        parse_mode: "Markdown" ou "HTML"

    Returns:
        True se enviou, False se falhou
    """
    token = _carregar_token()
    if not token:
        print("ERRO: Token Telegram não configurado.", file=sys.stderr)
        print("Opções:", file=sys.stderr)
        print(f"  1. export TELEGRAM_BOT_TOKEN=seu_token", file=sys.stderr)
        print(f"  2. echo 'seu_token' > {TOKEN_PATHS[0]}", file=sys.stderr)
        return False

    url = API_URL.format(token=token)
    payload = {
        "chat_id": chat_id or CHAT_ID,
        "text": texto,
        "parse_mode": parse_mode,
    }

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("ok", False)
    except urllib.error.HTTPError as e:
        print(f"ERRO Telegram HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERRO Telegram: {e}", file=sys.stderr)
        return False


def enviar_descoberta(novos_cnjs, total):
    """Formata e envia notificação de descoberta de processos."""
    if not novos_cnjs:
        return

    linhas = [
        "*DESCOBERTA DE PROCESSOS*",
        f"_{__import__('datetime').datetime.now().strftime('%d/%m %H:%M')}_",
        "",
        f"*NOVOS:* {len(novos_cnjs)} processo(s)",
        f"*TOTAL:* {total} conhecidos",
        "",
    ]

    for cnj in novos_cnjs[:10]:
        linhas.append(f"• `{cnj}`")

    if len(novos_cnjs) > 10:
        linhas.append(f"  _...e mais {len(novos_cnjs) - 10}_")

    enviar("\n".join(linhas))


def enviar_relatorio_noturno(relatorio):
    """Formata e envia relatório do orquestrador noturno."""
    r = relatorio
    dl = r.get("downloads", {})

    linhas = [
        "*ORQUESTRADOR NOTURNO*",
        f"_{__import__('datetime').datetime.now().strftime('%d/%m %H:%M')}_",
        "",
        f"*NOMEAÇÕES:* AJ={r.get('nomeacoes_aj', 0)} | AJG={r.get('nomeacoes_ajg', 0)}",
        f"*DESATUALIZADOS:* {r.get('desatualizados', 0)}",
    ]

    if dl:
        linhas.append(
            f"*DOWNLOADS:* {dl.get('sucesso', 0)}/{dl.get('tentados', 0)}"
            + (f" ({dl.get('falha', 0)} falhas)" if dl.get('falha') else "")
        )

    novos = r.get("novos_descobertos", 0)
    if novos:
        linhas.append(f"*NOVOS PROCESSOS:* {novos}")

    if r.get("alertas_criticos"):
        linhas.append(f"\n*{r['alertas_criticos']} PRAZOS CRÍTICOS*")

    linhas.append(f"\n_Tempo: {r.get('tempo_total_seg', 0):.0f}s_")

    enviar("\n".join(linhas))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Enviar mensagem via Telegram")
    parser.add_argument("mensagem", nargs="?", help="Texto da mensagem")
    parser.add_argument("--arquivo", type=str, help="Ler mensagem de arquivo")
    parser.add_argument("--teste", action="store_true", help="Enviar mensagem de teste")
    args = parser.parse_args()

    if args.teste:
        ok = enviar("Teste Stemmia Forense - notificação OK")
        sys.exit(0 if ok else 1)

    if args.arquivo:
        texto = Path(args.arquivo).read_text(encoding="utf-8")
    elif args.mensagem:
        texto = args.mensagem
    else:
        texto = sys.stdin.read()

    if not texto.strip():
        print("Nada para enviar.", file=sys.stderr)
        sys.exit(1)

    ok = enviar(texto)
    sys.exit(0 if ok else 1)
