"""Fase 6: Redacao do Laudo — Geracao semi-automatica do laudo pericial.

Usa template modelo + dados do caso + achados do exame para gerar
laudo completo em markdown (convertivel para Word/PDF).
Tempo esperado: ~10-15 minutos de geracao + revisao do perito.
"""

from pathlib import Path

from src import config
from src.claude_client import chamar_claude

SYSTEM_PROMPT = """Voce e redator especializado em laudos periciais medicos judiciais.

REGRAS OBRIGATORIAS:
- Tom formal, tecnico, impessoal
- Linguagem juridico-medica (CPC Art. 473 e ss.)
- Cite protocolos e literatura cientifica
- Para cada conclusao, indique: "Baseado em [evidencia X], [evidencia Y]"
- NAO faca diagnosticos — analise coerencia com padrao de cuidado
- Use estrutura padrao de laudo pericial (preambulo, historico, metodologia,
  exame, analise critica, conclusoes, referencias)
- Respostas aos quesitos devem ser diretas e fundamentadas"""

PROMPT_TEMPLATE = """Redija laudo pericial completo baseado nos dados abaixo.

{template_modelo}

DADOS DO CASO:
- Processo: {numero_processo}
- Tipo: {tipo_acao}
- Partes: Autor: {autor} | Reu: {reu}

SINTESE DO CASO:
{sintese}

ACHADOS DO EXAME PERICIAL:
{achados_exame}

QUESITOS E RESPOSTAS PRELIMINARES:
{quesitos}

ANALISE PROFUNDA (consideracoes):
{analise}

INSTRUCOES:
1. Siga a estrutura do template modelo se fornecido, senao use estrutura padrao
2. Preencha TODOS os campos com dados reais do caso
3. Secao ANALISE CRITICA: seja detalhado, cite literatura
4. Respostas aos quesitos: diretas, fundamentadas, com referencia aos achados
5. Inclua referencias bibliograficas ao final
6. Retorne em markdown formatado"""


def executar(
    sintese_inicial: dict,
    sintese_analitica: str | None = None,
    analise_profunda: str | None = None,
    achados_exame: str | None = None,
    template_path: str | Path | None = None,
) -> str:
    """Executa Fase 6: Gera laudo pericial."""
    # Carrega template se fornecido
    template = ""
    if template_path:
        p = Path(template_path)
        if p.exists():
            template = f"TEMPLATE MODELO (siga esta estrutura):\n{p.read_text(encoding='utf-8')}\n"
    if not template:
        template = _template_padrao()

    # Formata quesitos
    quesitos_fmt = ""
    for q in sintese_inicial.get("quesitos_extraidos", []):
        quesitos_fmt += (
            f"\nQuesito {q['numero']}: {q['pergunta']}\n"
            f"  Area: {q.get('area_clinica', 'N/A')}\n"
        )

    prompt = PROMPT_TEMPLATE.format(
        template_modelo=template,
        numero_processo=sintese_inicial.get("numero_processo", "N/A"),
        tipo_acao=sintese_inicial.get("tipo_acao", "N/A"),
        autor=sintese_inicial.get("partes", {}).get("autor", "N/A"),
        reu=sintese_inicial.get("partes", {}).get("reu", "N/A"),
        sintese=sintese_analitica[:5000] if sintese_analitica else "Nao disponivel.",
        achados_exame=achados_exame or "ACHADOS NAO FORNECIDOS — gere secao em branco para preenchimento manual.",
        quesitos=quesitos_fmt or "Nenhum quesito extraido.",
        analise=analise_profunda[:5000] if analise_profunda else "Nao disponivel.",
    )

    return chamar_claude(
        prompt_usuario=prompt,
        system_prompt=SYSTEM_PROMPT,
        max_tokens=32000,
    )


def _template_padrao() -> str:
    """Template padrao de laudo pericial quando nenhum modelo e fornecido."""
    return """TEMPLATE PADRAO (siga esta estrutura):

# LAUDO PERICIAL MEDICO

## PREAMBULO
[Perito, qualificacao, nomeacao, processo]

## 1. HISTORICO DO PROCESSO
[Resumo dos fatos conforme autos]

## 2. DOCUMENTOS ANALISADOS
[Lista de todos os documentos revisados]

## 3. METODOLOGIA
[Metodo utilizado, protocolos seguidos]

## 4. ANAMNESE PERICIAL
[Relato do periciando durante exame]

## 5. EXAME PERICIAL
### 5.1 Inspecao
### 5.2 Palpacao
### 5.3 Amplitude de Movimento
### 5.4 Testes Especiais
### 5.5 Exame Neurologico

## 6. EXAMES COMPLEMENTARES ANALISADOS
[Laudos de imagem, laboratoriais, etc]

## 7. DISCUSSAO E ANALISE CRITICA
[Analise fundamentada com literatura]

## 8. RESPOSTAS AOS QUESITOS
### Quesito 1:
[Resposta fundamentada]

## 9. CONCLUSAO
[Sintese final]

## 10. REFERENCIAS BIBLIOGRAFICAS
[Lista de referencias citadas]

## ENCERRAMENTO
[Fecho formal do laudo]
"""
