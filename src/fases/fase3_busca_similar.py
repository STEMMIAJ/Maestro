"""Fase 3: Busca de Casos Similares — Encontra laudos anteriores parecidos.

Usa Supabase pgvector para busca por similaridade cosseno.
Se Supabase nao configurado, busca localmente na pasta laudos_base/.
Tempo esperado: ~1 minuto.
"""

from pathlib import Path

from src import config
from src.claude_client import chamar_claude
from src.vector_store import buscar_similares


def executar(texto_caso: str, sintese_inicial: dict | None = None) -> dict:
    """Busca laudos similares ao caso atual."""
    # Monta descricao para busca
    if sintese_inicial:
        descricao = (
            f"Tipo: {sintese_inicial.get('tipo_acao', '')}\n"
            f"Diagnosticos: {sintese_inicial.get('historico_medico', {}).get('diagnosticos_alegados', [])}\n"
            f"Objeto: {sintese_inicial.get('objeto_litigio', '')}"
        )
    else:
        descricao = texto_caso[:5000]

    # Tenta Supabase primeiro
    similares_db = buscar_similares(descricao, limite=3)

    # Busca local como fallback
    similares_locais = _buscar_local(descricao)

    return {
        "similares_banco": similares_db,
        "similares_locais": similares_locais,
        "total": len(similares_db) + len(similares_locais),
    }


def _buscar_local(descricao: str) -> list[dict]:
    """Busca laudos similares na pasta local laudos_base/."""
    pasta = config.LAUDOS_BASE_DIR
    if not pasta.exists():
        return []

    arquivos = list(pasta.glob("*.md")) + list(pasta.glob("*.txt"))
    if not arquivos:
        return []

    # Pede ao Claude para ranquear os arquivos por similaridade
    lista_arquivos = "\n".join(
        f"- {a.name}: {a.read_text(encoding='utf-8')[:500]}"
        for a in arquivos[:20]
    )

    prompt = f"""Compare esta descricao de caso com os laudos abaixo.
Retorne os 3 mais similares em ordem de relevancia.

CASO ATUAL:
{descricao}

LAUDOS DISPONIVEIS:
{lista_arquivos}

Retorne APENAS uma lista JSON:
[
  {{"arquivo": "nome.md", "similaridade": "alta|media|baixa", "motivo": "por que e similar"}}
]"""

    try:
        resultado = chamar_claude(prompt, json_output=True)
        import json
        return json.loads(resultado)
    except Exception:
        return []


def formatar_resultado(resultado: dict) -> str:
    """Formata busca para exibicao."""
    linhas = ["LAUDOS SIMILARES ENCONTRADOS:", ""]

    if resultado["similares_banco"]:
        linhas.append("Banco de dados (Supabase):")
        for s in resultado["similares_banco"]:
            linhas.append(f"  - Processo: {s.get('processo_numero', 'N/A')}")
            linhas.append(f"    Especialidade: {s.get('especialidade', 'N/A')}")
            linhas.append(f"    Similaridade: {s.get('similaridade', 'N/A')}")
            linhas.append("")

    if resultado["similares_locais"]:
        linhas.append("Laudos locais:")
        for s in resultado["similares_locais"]:
            linhas.append(f"  - {s.get('arquivo', 'N/A')}")
            linhas.append(f"    Similaridade: {s.get('similaridade', 'N/A')}")
            linhas.append(f"    Motivo: {s.get('motivo', 'N/A')}")
            linhas.append("")

    if resultado["total"] == 0:
        linhas.append("  Nenhum laudo similar encontrado.")
        linhas.append("  Salve laudos na pasta laudos_base/ para futuras buscas.")

    return "\n".join(linhas)
