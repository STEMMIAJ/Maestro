"""Testes do orquestrador."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import orquestrador  # noqa: E402


def test_fontes_configuradas_5():
    ids = {f["id"] for f in orquestrador.FONTES}
    assert ids == {"aj", "ajg", "djen", "domicilio", "datajud"}


def test_caminho_saida_por_fonte():
    for fid in ("aj", "ajg", "djen", "domicilio", "datajud"):
        p = orquestrador._caminho_saida(fid)
        assert p.name == f"{fid}.json"
        assert "por-fonte" in str(p)


def test_rodar_fonte_script_ausente():
    r = orquestrador.rodar_fonte(
        {
            "id": "inexistente",
            "nome": "Teste",
            "cmd": ["python3", "/tmp/nao_existe_fg9f8.py"],
            "timeout": 5,
        }
    )
    assert r["status"] == "erro"
    assert r["itens"] == 0


def test_rodar_fonte_comando_ok_retorna_lista(tmp_path):
    script = tmp_path / "fake.py"
    script.write_text('import json; print(json.dumps([{"cnj": "A"}, {"cnj": "B"}]))')
    r = orquestrador.rodar_fonte(
        {
            "id": "aj",  # usa aj pra nao quebrar _caminho_saida
            "nome": "Teste OK",
            "cmd": ["python3", str(script)],
            "timeout": 10,
        }
    )
    assert r["status"] == "ok"
    assert r["itens"] == 2
    saida = orquestrador._caminho_saida("aj")
    dados = json.loads(saida.read_text())
    assert len(dados) == 2
    assert dados[0]["cnj"] == "A"


def test_rodar_fonte_dict_com_matches(tmp_path):
    """dje_tjmg cospe dict {matches: [...]}: orquestrador extrai matches."""
    script = tmp_path / "dje.py"
    script.write_text(
        'import json; print(json.dumps({"total_matches": 1, "matches": [{"cnj": "X"}]}))'
    )
    r = orquestrador.rodar_fonte(
        {"id": "aj", "nome": "DJE", "cmd": ["python3", str(script)], "timeout": 10}
    )
    assert r["status"] == "ok"
    assert r["itens"] == 1
    saida = orquestrador._caminho_saida("aj")
    dados = json.loads(saida.read_text())
    assert dados == [{"cnj": "X"}]


def test_rodar_fonte_dict_vazio_vira_lista_vazia(tmp_path):
    """dict com matches=[] não deve virar [dict] — deve virar []."""
    script = tmp_path / "dje_vazio.py"
    script.write_text('import json; print(json.dumps({"total_matches": 0, "matches": []}))')
    r = orquestrador.rodar_fonte(
        {"id": "aj", "nome": "DJE vazio", "cmd": ["python3", str(script)], "timeout": 10}
    )
    assert r["status"] == "ok"
    assert r["itens"] == 0


def test_rodar_fonte_timeout(tmp_path):
    script = tmp_path / "slow.py"
    script.write_text("import time; time.sleep(10)")
    r = orquestrador.rodar_fonte(
        {
            "id": "aj",
            "nome": "Slow",
            "cmd": ["python3", str(script)],
            "timeout": 1,
        }
    )
    assert r["status"] == "timeout"
