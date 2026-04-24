"""Modelo de dados para oportunidades de perícia."""

from dataclasses import dataclass


@dataclass
class Oportunidade:
    url: str
    fonte: str  # "jusbrasil"
    termo_busca: str
    categoria: str  # escassez_direta, mutirao, etc.
    titulo: str = ""
    trecho: str = ""
    comarca: str = ""
    vara: str = ""
    tribunal: str = ""
    estado: str = ""
    data_publicacao: str = ""  # DD/MM/YYYY
    data_titulo: str = ""  # YYYY-MM-DD (para ordenação)
    processo_numero: str = ""
