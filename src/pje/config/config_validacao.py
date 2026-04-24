"""
config_validacao.py — Validação runtime do config_pje via pydantic.

Rodada no startup dos 3 fluxos (descobrir, baixar, incluir) via try/except
em modo fail-soft: se pydantic falhar ou validação acusar erro, apenas
registra no stderr e segue — não aborta o fluxo.

Uso:
    from config.config_validacao import validar_config
    try:
        validar_config()
    except Exception as e:
        print(f"[config-validacao] aviso: {e}")

Criado 2026-04-19 conforme adendo "Polimento de scripts STEMMIA Dexter"
do plano binary-gliding-pine.md.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List

try:
    from pydantic import BaseModel, Field, field_validator
    PYDANTIC_OK = True
except Exception:
    PYDANTIC_OK = False


# Garante que o config_pje é importável quando este módulo é executado
# stand-alone (adiciona a pasta config/ ao sys.path).
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))


if PYDANTIC_OK:

    class PJeConfigModel(BaseModel):
        """Modelo que valida os campos críticos de config_pje."""

        PERITO_CPF: str = Field(..., min_length=11, max_length=14)
        PERITO_CPF_FMT: str
        PERITO_NOME: str = Field(..., min_length=1)
        PERITO_NOME_COMPLETO: str = Field(..., min_length=3)
        DATAJUD_KEY: str = Field(..., min_length=20)
        DATAJUD_ENDPOINTS: Dict[str, str]
        PJE_TJMG_BASE: str
        PJE_CONSULTA_PUBLICA: str
        DJEN_API: str
        DEXTER_ROOT: Path
        PJE_ROOT: Path
        DESCOBERTA_DIR: Path
        DOWNLOAD_DIR: Path
        CADASTRO_DIR: Path
        WAIT_LOGIN: int = Field(..., ge=30, le=3600)
        WAIT_DOWNLOAD: int = Field(..., ge=10, le=3600)
        TIMEOUT_PROCESSO: int = Field(..., ge=30, le=3600)
        SLEEP_ENTRE_PROCESSOS: int = Field(..., ge=0, le=600)
        ORDEM_COMARCA_DEFAULT: List[str]

        model_config = {"arbitrary_types_allowed": True}

        @field_validator("PERITO_CPF")
        @classmethod
        def _cpf_digits(cls, v: str) -> str:
            digits = re.sub(r"\D", "", v)
            if len(digits) != 11:
                raise ValueError(f"CPF deve ter 11 dígitos, recebido: {v!r}")
            return digits

        @field_validator("DATAJUD_ENDPOINTS")
        @classmethod
        def _endpoints_https(cls, v: Dict[str, str]) -> Dict[str, str]:
            for k, url in v.items():
                if not url.startswith("https://"):
                    raise ValueError(f"endpoint {k} não é HTTPS: {url}")
            return v

        @field_validator(
            "PJE_TJMG_BASE",
            "PJE_CONSULTA_PUBLICA",
            "DJEN_API",
        )
        @classmethod
        def _https(cls, v: str) -> str:
            if not v.startswith("https://"):
                raise ValueError(f"URL não-HTTPS: {v}")
            return v


def validar_config() -> dict:
    """
    Importa config_pje e valida via pydantic. Retorna dict com:
        {"ok": bool, "problemas_paths": {...}, "erros_modelo": [...]}

    Fail-soft: nunca propaga exceção de validação — caller pode ignorar
    o retorno. Se pydantic não estiver disponível, retorna ok=True com
    aviso em "erros_modelo".
    """
    import config_pje  # type: ignore  # import tardio, depende de sys.path

    resultado = {
        "ok": True,
        "problemas_paths": {},
        "erros_modelo": [],
    }

    # Check de paths (reusa função existente no config_pje)
    try:
        resultado["problemas_paths"] = config_pje.validar() or {}
    except Exception as exc:
        resultado["erros_modelo"].append(f"config_pje.validar() falhou: {exc}")
        resultado["ok"] = False

    if not PYDANTIC_OK:
        resultado["erros_modelo"].append("pydantic indisponível — skip validação de modelo")
        return resultado

    # Monta kwargs a partir do módulo (somente campos declarados no modelo)
    campos = list(PJeConfigModel.model_fields.keys())
    kwargs = {}
    for nome in campos:
        if hasattr(config_pje, nome):
            kwargs[nome] = getattr(config_pje, nome)

    try:
        PJeConfigModel(**kwargs)
    except Exception as exc:
        resultado["erros_modelo"].append(str(exc))
        resultado["ok"] = False

    return resultado


if __name__ == "__main__":
    r = validar_config()
    print("ok:", r["ok"])
    if r["problemas_paths"]:
        print("problemas_paths:", r["problemas_paths"])
    if r["erros_modelo"]:
        print("erros_modelo:")
        for e in r["erros_modelo"]:
            print("  -", e)
