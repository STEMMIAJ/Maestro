import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.guardrails import (
    detect_unverified_claim,
    detect_user_frustration,
    detect_condescension,
)


def test_claim_with_no_verification_is_flagged():
    result = detect_unverified_claim("Pronto, está funcionando!", tools_used=["Write"])
    assert result is not None
    assert "funcionando" in result["claim"].lower() or "pronto" in result["claim"].lower()


def test_claim_with_bash_verification_passes():
    result = detect_unverified_claim("Pronto, está funcionando.", tools_used=["Write", "Bash"])
    assert result is None


def test_claim_with_read_verification_passes():
    result = detect_unverified_claim("Corrigido.", tools_used=["Edit", "Read"])
    assert result is None


def test_no_claim_passes_regardless_of_tools():
    result = detect_unverified_claim("Vou começar pela leitura do arquivo.", tools_used=[])
    assert result is None


def test_claim_in_english_is_flagged():
    result = detect_unverified_claim("Done. Working as expected.", tools_used=["Write"])
    assert result is not None


def test_claim_inside_quote_is_still_flagged():
    result = detect_unverified_claim('O usuário disse "está funcionando" mas não testei.',
                                     tools_used=["Write"])
    assert result is not None


def test_frustration_keywords_are_caught():
    for msg in [
        "você mentiu de novo",
        "isso não funciona",
        "está errado",
        "me trata como imbecil",
        "isso é insuportável",
        "você não fez nada",
        "tá quebrado",
    ]:
        assert detect_user_frustration(msg) is not None, f"falhou: {msg}"


def test_neutral_message_is_not_frustration():
    assert detect_user_frustration("ok, segue") is None
    assert detect_user_frustration("vamos para o próximo passo") is None


def test_frustration_returns_signals_list():
    result = detect_user_frustration("você mentiu, isso é insuportável")
    assert "signals" in result
    assert len(result["signals"]) >= 2


def test_condescension_patterns():
    for msg in [
        "Vamos juntos descobrir isso!",
        "Que tal tentarmos esse approach?",
        "Espero que isso ajude!",
        "Isso ficou claro?",
        "Faz sentido?",
    ]:
        assert detect_condescension(msg) is not None, f"falhou: {msg}"


def test_direct_message_is_not_condescension():
    assert detect_condescension("Arquivo criado em /tmp/foo.txt") is None
    assert detect_condescension("Falhou — permissão negada na linha 42.") is None
