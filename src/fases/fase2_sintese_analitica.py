"""Fase 2: Sintese Analitica — Analise estruturada completa do processo.

Gera markdown com 6 secoes: identificacao, contexto juridico, contexto medico,
analise de quesitos, planejamento pericia, template modelo.
Tempo esperado: ~5 minutos.
"""

from pathlib import Path

from src.claude_client import chamar_claude
from src.pdf_processor import extrair_texto_pdf

SYSTEM_PROMPT = """Voce e assistente de sintese pericial. Quando recebe um processo,
SEMPRE retorna analise neste template estruturado. Nao desvie.

REGRAS:
- Tom formal, juridico-tecnico
- Cite CIDs quando identificar diagnosticos
- Para cada quesito, indique resposta preliminar + evidencias necessarias
- Identifique contradições entre partes
- Sugira armadilhas e pontos de atencao"""

PROMPT_TEMPLATE = """Analise este processo conforme template SINTESE ANALITICA.
Siga a estrutura exatamente. Retorne markdown completo.

# TEMPLATE OBRIGATORIO:

## 1. IDENTIFICACAO
- Numero: [extrair]
- Tipo: [civil/trabalhista/previdenciaria/criminal]
- Especialidade: [traumatologia/cardiologia/psiquiatria/etc]
- Complexidade: [baixa/media/alta]
- Prazo: [se mencionado]

## 2. CONTEXTO JURIDICO (max 5 paragrafos)
[Le: peticao inicial, contestacao, antecedentes processuais]
[Responde: Qual e a tese de cada parte? Qual precedente relevante?]

## 3. CONTEXTO MEDICO (max 5 paragrafos)
[Le: prontuarios, exames, relatorios medicos]
[Responde: Qual e o historico clinico? Diagnosticos? CIDs? Timeline medica?]

## 4. ANALISE DOS QUESITOS
Para CADA quesito encontrado:
### Quesito N: [texto]
- **Resposta preliminar**: [o que voce acha ATE AGORA]
- **Evidencias a favor**: [lista]
- **Evidencias contra**: [lista]
- **Investigar na pericia**: [o que precisa verificar]

## 5. CONTRADICOES E ALERTAS
- Pontos onde as partes se contradizem
- Documentos ausentes ou incompletos
- Riscos de contestacao do laudo

## 6. PLANEJAMENTO PRELIMINAR
- Objetivo da pericia: [1 frase]
- Achados esperados: [lista]
- Armadilhas: [pontos onde pode errar]
- Modelo similar sugerido: [tipo de laudo para usar como base]

---

PROCESSO COMPLETO:
{texto_processo}"""


def executar(caminho_pdf: str | Path) -> str:
    """Executa Fase 2: Sintese Analitica. Retorna markdown."""
    texto = extrair_texto_pdf(caminho_pdf)

    if len(texto) > 160000:
        texto = texto[:160000] + "\n\n[... DOCUMENTO TRUNCADO ...]"

    prompt = PROMPT_TEMPLATE.format(texto_processo=texto)

    resultado = chamar_claude(
        prompt_usuario=prompt,
        system_prompt=SYSTEM_PROMPT,
        max_tokens=16000,
    )

    return resultado


def executar_com_json(caminho_pdf: str | Path, sintese_inicial: dict) -> str:
    """Executa Fase 2 usando resultado da Fase 1 como contexto adicional."""
    texto = extrair_texto_pdf(caminho_pdf)

    if len(texto) > 140000:
        texto = texto[:140000] + "\n\n[... DOCUMENTO TRUNCADO ...]"

    contexto = (
        f"CONTEXTO DA FASE 1 (sintese inicial ja realizada):\n"
        f"- Processo: {sintese_inicial.get('numero_processo', 'N/A')}\n"
        f"- Tipo: {sintese_inicial.get('tipo_acao', 'N/A')}\n"
        f"- Complexidade: {sintese_inicial.get('complexidade', 'N/A')}\n"
        f"- Quesitos ja identificados: {len(sintese_inicial.get('quesitos_extraidos', []))}\n"
        f"- Diagnosticos alegados: {sintese_inicial.get('historico_medico', {}).get('diagnosticos_alegados', [])}\n"
        f"\nAgora faca a SINTESE ANALITICA completa.\n\n"
    )

    prompt = contexto + PROMPT_TEMPLATE.format(texto_processo=texto)

    resultado = chamar_claude(
        prompt_usuario=prompt,
        system_prompt=SYSTEM_PROMPT,
        max_tokens=16000,
    )

    return resultado
