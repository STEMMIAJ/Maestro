"""Fase 1: Sintese Inicial — Decisao rapida de aceitar/rejeitar caso.

Recebe PDF do processo, extrai texto, envia ao Claude com structured output.
Retorna JSON com resumo executivo, quesitos, complexidade e recomendacao.
Tempo esperado: ~1 minuto.
"""

import json
from pathlib import Path

from src.claude_client import chamar_claude_estruturado, _carregar_prompt
from src.pdf_processor import extrair_texto_pdf, contar_tokens_aproximado

SYSTEM_PROMPT = """Voce e assistente de perito medico judicial.
Analise o processo e retorne APENAS JSON valido, sem texto adicional.
Extraia todas as informacoes relevantes para decisao rapida de aceitacao."""

PROMPT_TEMPLATE = """Analise este processo judicial e retorne APENAS JSON estruturado:

{{
  "resumo_executivo": "3-5 frases maximo",
  "numero_processo": "string",
  "tipo_acao": "civil|trabalhista|previdenciaria|criminal|familia",
  "partes": {{
    "autor": "nome",
    "reu": "nome",
    "interessados": ["lista"]
  }},
  "objeto_litigio": "O que esta em disputa (max 100 palavras)",
  "quesitos_extraidos": [
    {{
      "numero": 1,
      "pergunta": "texto exato da pergunta",
      "area_clinica": "especialidade relacionada"
    }}
  ],
  "historico_medico": {{
    "diagnosticos_alegados": ["lista"],
    "cids_mencionados": ["lista"],
    "datas_importantes": ["lista"],
    "relatorios_existentes": ["lista"]
  }},
  "valor_causa": "string ou null",
  "prazo_pericia": "string ou null",
  "complexidade": "baixa|media|alta|critica",
  "recomendacao_aceitacao": "aceitar|recusar|revisar_mais",
  "motivo_recomendacao": "string",
  "alertas": ["lista de pontos de atencao"]
}}

PROCESSO:
{texto_processo}"""


def executar(caminho_pdf: str | Path) -> dict:
    """Executa Fase 1: Sintese Inicial."""
    texto = extrair_texto_pdf(caminho_pdf)
    tokens = contar_tokens_aproximado(texto)

    # Se muito grande, trunca para primeiras 80 paginas (~160k chars)
    if len(texto) > 160000:
        texto = texto[:160000] + "\n\n[... DOCUMENTO TRUNCADO ...]"

    prompt = PROMPT_TEMPLATE.format(texto_processo=texto)

    resultado = chamar_claude_estruturado(
        prompt_usuario=prompt,
        system_prompt=SYSTEM_PROMPT,
    )

    resultado["_meta"] = {
        "arquivo": str(caminho_pdf),
        "tokens_estimados": tokens,
        "fase": "sintese_inicial",
    }

    return resultado


def formatar_decisao(resultado: dict) -> str:
    """Formata resultado para leitura rapida no terminal."""
    r = resultado
    linhas = [
        f"{'='*60}",
        f"SINTESE INICIAL — {r.get('numero_processo', 'N/A')}",
        f"{'='*60}",
        f"",
        f"Tipo: {r.get('tipo_acao', 'N/A')}",
        f"Complexidade: {r.get('complexidade', 'N/A')}",
        f"Recomendacao: {r.get('recomendacao_aceitacao', 'N/A')}",
        f"Motivo: {r.get('motivo_recomendacao', 'N/A')}",
        f"",
        f"RESUMO: {r.get('resumo_executivo', 'N/A')}",
        f"",
        f"PARTES:",
        f"  Autor: {r.get('partes', {}).get('autor', 'N/A')}",
        f"  Reu:   {r.get('partes', {}).get('reu', 'N/A')}",
        f"",
        f"QUESITOS ({len(r.get('quesitos_extraidos', []))} encontrados):",
    ]

    for q in r.get("quesitos_extraidos", []):
        linhas.append(f"  {q['numero']}. [{q.get('area_clinica', '?')}] {q['pergunta']}")

    if r.get("alertas"):
        linhas.append(f"\nALERTAS:")
        for a in r["alertas"]:
            linhas.append(f"  ! {a}")

    linhas.append(f"\n{'='*60}")
    return "\n".join(linhas)
