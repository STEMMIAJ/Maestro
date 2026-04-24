"""Detectores puros para enforcement anti-mentira / anti-condescendência."""
from __future__ import annotations

import re
from typing import Any

# Tools que contam como "verificação real" do que foi escrito/feito
VERIFICATION_TOOLS = {"Bash", "Read", "Grep", "Glob"}

CLAIM_PATTERNS = [
    r"\bfeito\b",
    r"\bpronto\b",
    r"\bcorrigid[oa]\b",
    r"\bfuncionand[oa]\b",
    r"\brodand[oa]\b",
    r"\bdeployad[oa]\b",
    r"\bfixad[oa]\b",
    r"\bresolvid[oa]\b",
    r"\bconcluíd[oa]\b",
    r"\bdone\b",
    r"\bfixed\b",
    r"\bworking\b",
    r"\bdeployed\b",
    r"\bcompleted\b",
]
_CLAIM_RE = re.compile("|".join(CLAIM_PATTERNS), re.IGNORECASE)

FRUSTRATION_MARKERS = [
    "mentiu", "mentindo", "mentira",
    "não funciona", "nao funciona", "não funcionou", "nao funcionou",
    "tá errado", "ta errado", "está errado",
    "me trata como", "imbecil", "burro",
    "insuportável", "insuportavel",
    "não fez", "nao fez", "não fizeste", "não fizeram",
    "tá quebrado", "ta quebrado", "está quebrado",
    "me atrasou", "me atrasando",
    "de novo", "outra vez",
    "perdi tempo", "perdendo tempo",
    "recusou", "recusando",
    "não obedece", "nao obedece",
]

CONDESCENSION_PATTERNS = [
    r"\bvamos juntos\b",
    r"\bque tal\b",
    r"\bposso te ajudar\b",
    r"\bespero que (isso|isto) ajude\b",
    r"\bficou claro\??$",
    r"\bfaz sentido\??$",
    r"\bcompreendido\??$",
    r"\bentendeu\??$",
    r"^vamos lá",
]
_CONDESCENSION_RE = re.compile("|".join(CONDESCENSION_PATTERNS), re.IGNORECASE | re.MULTILINE)


def detect_unverified_claim(
    assistant_text: str,
    tools_used: list,
) -> dict | None:
    if not assistant_text:
        return None
    match = _CLAIM_RE.search(assistant_text)
    if not match:
        return None
    if any(t in VERIFICATION_TOOLS for t in tools_used):
        return None
    return {
        "claim": match.group(0),
        "reason": f"Claim '{match.group(0)}' sem nenhuma tool de verificação ({', '.join(sorted(VERIFICATION_TOOLS))}) desde o último turno do usuário.",
    }


def detect_user_frustration(user_message: str) -> dict | None:
    if not user_message:
        return None
    lower = user_message.lower()
    signals = [m for m in FRUSTRATION_MARKERS if m in lower]
    if not signals:
        return None
    return {"signals": signals}


def detect_condescension(assistant_text: str) -> dict | None:
    if not assistant_text:
        return None
    match = _CONDESCENSION_RE.search(assistant_text)
    if not match:
        return None
    return {"pattern": match.group(0)}
