"""Notificações macOS para oportunidades encontradas."""

import subprocess


def notificar(titulo: str, mensagem: str):
    try:
        subprocess.run([
            "osascript", "-e",
            f'display notification "{mensagem}" with title "{titulo}"'
        ], timeout=5)
    except Exception:
        pass


def tocar_som():
    try:
        subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], timeout=5)
    except Exception:
        pass


def notificar_resultados(novos: int, total: int):
    if novos > 0:
        notificar(
            "Buscador de Peritos",
            f"{novos} nova(s) oportunidade(s) encontrada(s)! Total: {total}"
        )
        tocar_som()
