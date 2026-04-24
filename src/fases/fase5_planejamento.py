"""Fase 5: Planejamento da Pericia — Roteiro estruturado de exame.

Gera checklist detalhado com anamnese, exame fisico, testes especiais,
e mapeamento de cada achado para os quesitos do processo.
Tempo esperado: ~5 minutos.
"""

from src.claude_client import chamar_claude

SYSTEM_PROMPT = """Voce e especialista em planejamento de pericias medicas judiciais.
Crie roteiros DETALHADOS e PRATICOS que o perito leva impresso para a pericia.
Cada item deve ter checkbox, ser especifico, e indicar QUAL QUESITO responde.
Use linguagem tecnica medica. Inclua escalas e criterios objetivos."""

PROMPT_TEMPLATE = """Crie roteiro DETALHADO para exame pericial.

DADOS DO CASO:
{dados_caso}

QUESITOS A RESPONDER:
{quesitos}

# ROTEIRO EXAME PERICIAL — Processo {numero_processo}

Gere o roteiro completo seguindo OBRIGATORIAMENTE esta estrutura:

## FASE PRE-EXAME (consultorio)
- Observacoes ao paciente entrar (postura, marcha, expressao facial)
- Confirmacao identidade e consentimento
- Revisao rapida de prontuarios trazidos pelo periciando

## FASE ANAMNESE (~15 min)
Para cada quesito, liste pergunta EXATA a fazer:
- Pergunta N: "[texto exato]" → resposta informara sobre [quesito N]
Inclua perguntas de validacao (contradiz o que disse antes?)

## FASE EXAME FISICO
### Inspecao
- Lista de itens com checkbox e escala de graduacao
### Palpacao
- Pontos especificos com localizacao anatomica
### Amplitude de Movimento
- Tabela goniometrica comparativa (lado afetado vs contralateral)
- Valores normais de referencia
### Testes Especiais
- Nome do teste → achado esperado → responde quesito N
### Exame Neurologico (se aplicavel)
- Sensibilidade, reflexos, forca muscular (escala 0-5)

## MAPEAMENTO QUESITO-ACHADO
Tabela: | Quesito | Achados necessarios | Testes | Conclusao esperada |

## ARMADILHAS / VALIDACAO
- Checklist de pontos criticos
- Testes de validade (simulacao, Waddell signs se aplicavel)
- Cruzamento de dados (anamnese vs exame vs documentos)

## MATERIAL NECESSARIO
- Instrumentos, formularios, escalas para levar
"""


def executar(
    sintese_inicial: dict,
    sintese_analitica: str | None = None,
    analise_profunda: str | None = None,
) -> str:
    """Executa Fase 5: Gera roteiro de pericia."""
    # Monta dados do caso
    dados = []
    if sintese_analitica:
        dados.append(f"SINTESE ANALITICA:\n{sintese_analitica[:4000]}")
    if analise_profunda:
        dados.append(f"ANALISE PROFUNDA:\n{analise_profunda[:4000]}")

    # Formata quesitos
    quesitos_fmt = ""
    for q in sintese_inicial.get("quesitos_extraidos", []):
        quesitos_fmt += f"\n{q['numero']}. [{q.get('area_clinica', '?')}] {q['pergunta']}"

    prompt = PROMPT_TEMPLATE.format(
        dados_caso="\n---\n".join(dados) if dados else "Dados limitados. Use quesitos.",
        quesitos=quesitos_fmt or "Nenhum quesito extraido.",
        numero_processo=sintese_inicial.get("numero_processo", "N/A"),
    )

    return chamar_claude(
        prompt_usuario=prompt,
        system_prompt=SYSTEM_PROMPT,
        max_tokens=16000,
    )
