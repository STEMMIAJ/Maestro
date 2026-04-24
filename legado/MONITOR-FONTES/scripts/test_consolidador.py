"""Testes do consolidador."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import consolidador  # noqa: E402


def _setup(tmp_path, monkeypatch):
    por_fonte = tmp_path / "por-fonte"
    por_fonte.mkdir()
    monkeypatch.setattr(consolidador, "POR_FONTE", por_fonte)
    monkeypatch.setattr(consolidador, "SAIDA_JSON", tmp_path / "out.json")
    monkeypatch.setattr(consolidador, "SAIDA_CSV", tmp_path / "out.csv")
    return por_fonte


def test_normalizar_cnj_formatado():
    r = consolidador._normalizar_cnj("5001234-56.2025.8.13.0105")
    assert r == "5001234-56.2025.8.13.0105"


def test_normalizar_cnj_sem_pontuacao():
    r = consolidador._normalizar_cnj("50012345620258130105")
    assert r == "5001234-56.2025.8.13.0105"


def test_normalizar_cnj_invalido():
    assert consolidador._normalizar_cnj("abc") is None
    assert consolidador._normalizar_cnj("") is None
    assert consolidador._normalizar_cnj(None) is None


def test_data_iso_formatos():
    assert consolidador._data_iso("2026-04-15") == "2026-04-15"
    assert consolidador._data_iso("15/04/2026") == "2026-04-15"
    assert consolidador._data_iso("2026-04-15T10:00:00") == "2026-04-15"
    assert consolidador._data_iso("bla") == ""
    assert consolidador._data_iso(None) == ""


def test_consolidar_dedup_por_cnj(tmp_path, monkeypatch):
    por_fonte = _setup(tmp_path, monkeypatch)
    (por_fonte / "aj.json").write_text(
        json.dumps([{"cnj": "5001234-56.2025.8.13.0105", "data": "2026-04-10"}])
    )
    (por_fonte / "djen.json").write_text(
        json.dumps(
            [
                {"cnj": "5001234-56.2025.8.13.0105", "data": "2026-04-15"},
                {"cnj": "5002000-00.2025.8.13.0105", "data": "2026-04-12"},
            ]
        )
    )
    lista = consolidador.consolidar()
    assert len(lista) == 2
    # Ordem desc
    assert lista[0]["cnj"] == "5001234-56.2025.8.13.0105"
    assert lista[0]["data_mais_recente"] == "2026-04-15"
    # Fontes juntas
    assert set(lista[0]["fontes"]) == {"aj", "djen"}
    assert len(lista[0]["detalhes"]) == 2


def test_consolidar_aceita_campos_alternativos(tmp_path, monkeypatch):
    por_fonte = _setup(tmp_path, monkeypatch)
    (por_fonte / "ajg.json").write_text(
        json.dumps(
            [
                {
                    "numeroProcesso": "5001234-56.2025.4.03.6109",
                    "dataNomeacao": "15/04/2026",
                    "classe": "CIVEL",
                }
            ]
        )
    )
    lista = consolidador.consolidar()
    assert len(lista) == 1
    assert lista[0]["data_mais_recente"] == "2026-04-15"
    assert lista[0]["resumo"]["classe"] == "CIVEL"


def test_consolidar_ignora_sem_cnj(tmp_path, monkeypatch):
    por_fonte = _setup(tmp_path, monkeypatch)
    (por_fonte / "aj.json").write_text(json.dumps([{"data": "2026-04-15"}, {"cnj": "lixo"}]))
    lista = consolidador.consolidar()
    assert lista == []


def test_consolidar_gera_csv(tmp_path, monkeypatch):
    por_fonte = _setup(tmp_path, monkeypatch)
    (por_fonte / "aj.json").write_text(
        json.dumps([{"cnj": "5001234-56.2025.8.13.0105", "data": "2026-04-10"}])
    )
    consolidador.consolidar()
    csv_path = tmp_path / "out.csv"
    assert csv_path.exists()
    conteudo = csv_path.read_text()
    assert "cnj,data_mais_recente" in conteudo
    assert "5001234-56.2025.8.13.0105" in conteudo
