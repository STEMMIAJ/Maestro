"""CNJ — regex unificado, validador, formatador, sanitizador para nome de arquivo.

Endereça:
- DUPLICATAS.md (regex CNJ replicado em 11 arquivos)
- PJE-019 (Windows: nome de arquivo com caracteres especiais quebra)
- ref: gerar_lista_prioridade.py (único que usa \\b corretamente)

NUNCA passar suggested_filename do download direto pro disco.
"""
from __future__ import annotations
import re

# CNJ: NNNNNNN-DD.AAAA.J.TR.OOOO
RE_CNJ = re.compile(r"\b(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})\b")
RE_CNJ_LIMPO = re.compile(r"^\d{20}$")


def validar_cnj(cnj: str) -> bool:
    if not cnj:
        return False
    return bool(RE_CNJ.match(cnj.strip()))


def limpar_cnj(cnj: str) -> str:
    """Retorna apenas os 20 dígitos."""
    return re.sub(r"\D", "", cnj or "")


def formatar_cnj(digitos: str) -> str | None:
    """20 dígitos → NNNNNNN-DD.AAAA.J.TR.OOOO. None se inválido."""
    d = limpar_cnj(digitos)
    if len(d) != 20:
        return None
    return f"{d[0:7]}-{d[7:9]}.{d[9:13]}.{d[13:14]}.{d[14:16]}.{d[16:20]}"


def safe_filename_cnj(cnj: str, sufixo: str = ".pdf") -> str:
    """Nome de arquivo seguro Windows + Mac. ref: PJE-019."""
    digitos = limpar_cnj(cnj)
    if len(digitos) == 20:
        return f"{digitos}{sufixo}"
    # fallback: strip de chars Windows-reservados
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", cnj or "sem-cnj")
    return f"{safe}{sufixo}"
