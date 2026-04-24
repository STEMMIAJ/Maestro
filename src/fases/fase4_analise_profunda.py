"""Fase 4: Analise Profunda — Raciocinio estendido sobre o caso.

Usa Claude Opus com Extended Thinking para analise critica profunda.
Gera hipoteses, probabilidades e plano de investigacao.
Tempo esperado: ~10-15 minutos.
"""

from pathlib import Path

from src.claude_client import chamar_claude_profundo
from src.pdf_processor import extrair_texto_pdf

SYSTEM_PROMPT = """Voce e um analista medico-legal experiente.
Pense profundamente sobre cada caso. Nao aceite respostas superficiais.
Questione evidencias, identifique lacunas, proponha hipoteses alternativas.
Seu objetivo e preparar o perito para a pericia com clareza total."""

PROMPT_TEMPLATE = """Analise PROFUNDAMENTE este processo. Pense extensamente antes de responder.

CONTEXTO PREVIO (fases anteriores):
{contexto_previo}

Sua analise deve cobrir:

## ANALISE PROFUNDA
- Qual e REALMENTE a questao de fundo? (juridica vs medica)
- O que cada parte NAO esta dizendo mas esta implicito?
- Quais sao os pontos fracos de cada lado?

## HIPOTESES E PROBABILIDADES
Para cada hipotese:
1. **Hipotese**: [descricao]
   - **Probabilidade**: [%]
   - **Evidencia que suportaria**: [lista]
   - **Evidencia que refutaria**: [lista]

## CONTRADICOES CRITICAS
- Onde as narrativas nao batem?
- Que documentos contradizem outros?
- Que informacoes estao AUSENTES e deveriam estar presentes?

## PLANO DE INVESTIGACAO NA PERICIA
- Prioridade Alta: [o que deve investigar primeiro e por que]
- Prioridade Media: [investigar se tempo permitir]
- Prioridade Baixa: [nice to have]

## ARMADILHAS DO PERITO
- Onde voce pode ser induzido ao erro?
- Que perguntas armadilha o advogado pode fazer?
- Como blindar o laudo contra impugnacao?

## LITERATURA RELEVANTE
- Protocolos aplicaveis (ATLS, CFM, etc)
- Jurisprudencia STJ/STF relevante
- Guidelines medicas pertinentes

PROCESSO:
{texto_processo}"""


def executar(
    caminho_pdf: str | Path,
    sintese_inicial: dict | None = None,
    sintese_analitica: str | None = None,
) -> str:
    """Executa Fase 4: Analise Profunda com Extended Thinking."""
    texto = extrair_texto_pdf(caminho_pdf)

    if len(texto) > 120000:
        texto = texto[:120000] + "\n\n[... DOCUMENTO TRUNCADO ...]"

    # Monta contexto das fases anteriores
    contexto_partes = []
    if sintese_inicial:
        contexto_partes.append(
            f"Processo: {sintese_inicial.get('numero_processo', 'N/A')}\n"
            f"Tipo: {sintese_inicial.get('tipo_acao', 'N/A')}\n"
            f"Complexidade: {sintese_inicial.get('complexidade', 'N/A')}\n"
            f"Quesitos: {len(sintese_inicial.get('quesitos_extraidos', []))}\n"
            f"Diagnosticos: {sintese_inicial.get('historico_medico', {}).get('diagnosticos_alegados', [])}"
        )
    if sintese_analitica:
        # Inclui apenas resumo da sintese (nao repetir tudo)
        contexto_partes.append(
            f"Sintese analitica ja realizada (resumo):\n{sintese_analitica[:3000]}"
        )

    contexto = "\n---\n".join(contexto_partes) if contexto_partes else "Nenhum contexto previo."

    prompt = PROMPT_TEMPLATE.format(
        contexto_previo=contexto,
        texto_processo=texto,
    )

    return chamar_claude_profundo(
        prompt_usuario=prompt,
        system_prompt=SYSTEM_PROMPT,
    )
