"""Testes do alerta."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import alerta_telegram as alerta  # noqa: E402


def test_sem_cnjs_anteriores_tudo_e_novo():
    atual = [{"cnj": "A"}, {"cnj": "B"}]
    novos = alerta.detectar_novos([], atual)
    assert {n["cnj"] for n in novos} == {"A", "B"}


def test_cnj_ja_visto_nao_alerta():
    anterior = [{"cnj": "A"}]
    atual = [{"cnj": "A"}, {"cnj": "B"}]
    novos = alerta.detectar_novos(anterior, atual)
    assert [n["cnj"] for n in novos] == ["B"]


def test_sem_diferencas_retorna_vazio():
    lista = [{"cnj": "A"}, {"cnj": "B"}]
    assert alerta.detectar_novos(lista, lista) == []


def test_ignora_entradas_sem_cnj():
    atual = [{"cnj": "A"}, {"sem_cnj": True}]
    novos = alerta.detectar_novos([], atual)
    assert len(novos) == 1


def test_relogin_aj_com_erro_de_login():
    snap = {"aj": {"status": "erro", "erro": "Not logged in"}}
    assert alerta.precisa_relogin(snap) is True


def test_relogin_ajg_com_erro_sessao():
    snap = {"ajg": {"status": "erro", "erro": "Session expired"}}
    assert alerta.precisa_relogin(snap) is True


def test_erro_generico_nao_dispara_relogin():
    snap = {"aj": {"status": "erro", "erro": "timeout rede"}}
    assert alerta.precisa_relogin(snap) is False


def test_relogin_chrome_cdp_desconectado():
    """Erro real visto em produção: Chrome 9223 não rodando."""
    snap = {"aj": {"status": "erro", "erro": "BrowserType.connect_over_cdp: Protocol error"}}
    assert alerta.precisa_relogin(snap) is True


def test_relogin_connection_refused():
    snap = {"ajg": {"status": "erro", "erro": "ECONNREFUSED 127.0.0.1:9223"}}
    assert alerta.precisa_relogin(snap) is True


def test_sucesso_nao_dispara_relogin():
    snap = {"aj": {"status": "ok", "itens": 5}, "ajg": {"status": "ok", "itens": 3}}
    assert alerta.precisa_relogin(snap) is False


def test_enviar_sem_token_retorna_false(capsys):
    # Garante que nao ha token no env
    import os
    antigo = os.environ.pop("TELEGRAM_BOT_TOKEN", None)
    try:
        # Tambem nao pode carregar do env file
        import unittest.mock
        with unittest.mock.patch.object(alerta, "_carregar_token", return_value=""):
            r = alerta.enviar("teste")
        assert r is False
    finally:
        if antigo:
            os.environ["TELEGRAM_BOT_TOKEN"] = antigo
