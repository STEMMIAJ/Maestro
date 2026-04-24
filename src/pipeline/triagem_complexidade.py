#!/usr/bin/env python3
"""
TRIAGEM AUTOMÁTICA DE COMPLEXIDADE PROCESSUAL
Autor: Dr. Jésus Eduardo Noleto da Penha — CRM/MG 92.148
Versão: 1.0 | Data: 18/03/2026

USO:
    python3 triagem_complexidade.py TEXTO-EXTRAIDO.txt
    python3 triagem_complexidade.py TEXTO-EXTRAIDO.txt --output TRIAGEM.md
    python3 triagem_complexidade.py TEXTO-EXTRAIDO.txt --json

O que faz:
    1. Lê o texto extraído de um processo (pdftotext)
    2. Busca CADA fator de complexidade usando regex + busca semântica
    3. Para cada fator encontrado, mostra:
       - O TRECHO EXATO do texto onde foi detectado (com número da linha)
       - O ID do documento PJe mais próximo (se detectável)
       - A classificação do fator
    4. Gera relatório em Markdown ou JSON
"""

import re
import sys
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple

# ══════════════════════════════════════════════════════════════
# CONFIGURAÇÃO: PADRÕES DE BUSCA POR FATOR
# ══════════════════════════════════════════════════════════════

# Cada fator tem:
# - nome: nome descritivo
# - grupo: A (carga), B (técnica), C (contexto)
# - patterns: lista de regex para buscar no texto
# - context_words: palavras-chave para busca semântica (co-ocorrência)
# - extract_fn: função especial de extração (opcional)

FATORES = {
    # ─── GRUPO A: CARGA DE TRABALHO OBJETIVA ───
    "volume_documental": {
        "nome": "Volume Documental",
        "grupo": "A - Carga de Trabalho",
        "patterns": [],  # Calculado pelo pdfinfo, não por regex
        "descricao": "Total de páginas dos autos (via pdfinfo)",
        "como_extrair": "pdfinfo arquivo.pdf | grep Pages",
    },
    "quesitos": {
        "nome": "Quesitos Formulados",
        "grupo": "A - Carga de Trabalho",
        "patterns": [
            r'(?i)quesito[s]?',
            r'(?i)apresenta[r]?\s+(os\s+)?seguintes\s+quesitos',
            r'(?i)formula[r]?\s+(os\s+)?seguintes\s+quesitos',
            r'(?i)quesitos?\s+(do|da|das|dos)\s+(autor|réu|ré|juíz|juiz|MP)',
            r'(?i)quesitos?\s+suplementar',
            r'(?i)art\.\s*47[0-9]',
        ],
        "context_words": ["perito", "perícia", "responder", "laudo"],
        "descricao": "Quantidade e origem dos quesitos formulados pelas partes",
    },
    "assistente_tecnico": {
        "nome": "Assistente(s) Técnico(s) Indicado(s)",
        "grupo": "A - Carga de Trabalho",
        "patterns": [
            r'(?i)assistente[s]?\s+t[eé]cnic',
            r'(?i)indica[r]?\s+(como\s+)?assistente',
            r'(?i)nomeação\s+de\s+assistente',
            r'(?i)parecer\s+(do|da)\s+assistente',
            r'(?i)assistente.{0,30}CRM',
        ],
        "context_words": ["indicar", "nomear", "parecer", "CRM"],
        "descricao": "Presença de assistentes técnicos indicados pelas partes",
    },
    "especialidades": {
        "nome": "Especialidades Médicas Necessárias",
        "grupo": "A - Carga de Trabalho",
        "patterns_por_especialidade": {
            "Ortopedia": [
                r'(?i)ortoped', r'(?i)fratura', r'(?i)luxa[çc][ãa]o',
                r'(?i)articula[çc][ãa]o', r'(?i)coluna\s+(cervical|lombar|tor[áa]cica)',
                r'(?i)h[ée]rnia\s+disc', r'(?i)joelho', r'(?i)ombro',
                r'(?i)punho', r'(?i)tornozelo', r'(?i)membro\s+(superior|inferior)',
                r'(?i)goniometr', r'(?i)amplitude\s+de\s+movimento',
            ],
            "Cardiologia": [
                r'(?i)cardi[oó]', r'(?i)infarto', r'(?i)\bIAM\b',
                r'(?i)coron[áa]ri', r'(?i)\bECG\b', r'(?i)eletrocardiograma',
                r'(?i)troponina', r'(?i)angioplast', r'(?i)revascular',
                r'(?i)fra[çc][ãa]o\s+de\s+eje[çc][ãa]o', r'(?i)arritmia',
                r'(?i)insufici[êe]ncia\s+card',
            ],
            "Psiquiatria": [
                r'(?i)psiq', r'(?i)psicol[oó]g', r'(?i)\bTEPT\b',
                r'(?i)ansiedade', r'(?i)depress[ãa]o', r'(?i)transtorno\s+mental',
                r'(?i)transtorno\s+de\s+estresse', r'(?i)dano\s+psicol[oó]gico',
                r'(?i)sofrimento\s+ps[ií]quic', r'(?i)CID.{0,5}F\d',
            ],
            "Neurologia": [
                r'(?i)neuro', r'(?i)cerebr', r'(?i)\bAVC\b',
                r'(?i)encefal', r'(?i)medula', r'(?i)paralisi',
                r'(?i)convuls', r'(?i)epilep', r'(?i)cefaleia',
            ],
            "Obstetrícia": [
                r'(?i)obstet', r'(?i)ces[áa]r', r'(?i)parto',
                r'(?i)gesta[çc][ãa]o', r'(?i)gravid', r'(?i)pu[ée]rper',
                r'(?i)pré.natal', r'(?i)pre.natal', r'(?i)neonat',
            ],
            "Oftalmologia": [
                r'(?i)oftalmo', r'(?i)vis[ãa]o', r'(?i)cegueira',
                r'(?i)glaucom', r'(?i)catarat', r'(?i)retina',
                r'(?i)ocular', r'(?i)acuidade\s+visual',
            ],
            "Cirurgia Plástica / Dano Estético": [
                r'(?i)est[ée]tic', r'(?i)cicatriz', r'(?i)deformidade',
                r'(?i)cirurgia\s+pl[áa]st', r'(?i)cirurgia\s+reparador',
                r'(?i)dano\s+est[ée]tic', r'(?i)altera[çc][ãa]o\s+morfol[oó]g',
            ],
            "Medicina Legal / Perícia": [
                r'(?i)medicina\s+legal', r'(?i)med.{0,5}legal',
                r'(?i)nexo\s+(de\s+)?causal', r'(?i)incapacidade',
                r'(?i)invalidez', r'(?i)dano\s+corporal',
            ],
            "Clínica Médica Geral": [
                r'(?i)cl[ií]nic[ao]\s+m[ée]dic', r'(?i)cl[ií]nic[ao]\s+geral',
                r'(?i)exame\s+cl[ií]nico', r'(?i)anamnese',
            ],
        },
        "descricao": "Áreas da medicina exigidas pelos quesitos e objeto da perícia",
    },
    "docs_faltantes": {
        "nome": "Documentação a Requisitar",
        "grupo": "A - Carga de Trabalho",
        "patterns": [
            r'(?i)requisit[ae]r\s+(document|prontu[áa]rio|laudo|exame)',
            r'(?i)juntar\s+(document|prontu[áa]rio|laudo|exame)',
            r'(?i)oficiar\s+(ao|à|a)\s+(hospital|cl[ií]nica|UBS|UPA|INSS)',
            r'(?i)documenta[çc][ãa]o\s+complementar',
            r'(?i)n[ãa]o\s+consta[m]?\s+(nos|no)\s+auto',
            r'(?i)aus[êe]ncia\s+de\s+(prontu[áa]rio|laudo|exame|document)',
            r'(?i)art\.\s*473.*§\s*3',
        ],
        "context_words": ["prontuário", "hospital", "exame", "laudo", "complementar"],
        "descricao": "Documentos médicos necessários que não estão nos autos",
    },
    "deslocamento": {
        "nome": "Deslocamento Necessário",
        "grupo": "A - Carga de Trabalho",
        "patterns": [
            r'(?i)desloc[ae]mento',
            r'(?i)\d+\s*km', r'(?i)quil[ôo]metro',
            r'(?i)dist[âa]ncia', r'(?i)viagem',
            r'(?i)outra\s+comarca', r'(?i)comarca\s+distint',
        ],
        "context_words": ["km", "ida", "volta", "combustível", "diária"],
        "descricao": "Distância entre consultório do perito e local da perícia",
    },
    "esclarecimentos": {
        "nome": "Esclarecimentos Futuros Prováveis",
        "grupo": "A - Carga de Trabalho",
        "patterns": [
            r'(?i)protesta[r]?\s+(pela\s+)?juntada\s+de\s+quesitos\s+suplementar',
            r'(?i)quesitos?\s+suplementar',
            r'(?i)esclarecimento[s]?\s+(complementar|adiciona|posterior)',
            r'(?i)art\.\s*477',
            r'(?i)reserva.{0,20}esclarecimento',
        ],
        "context_words": ["suplementar", "esclarecimento", "art. 477"],
        "descricao": "Indicadores de que haverá pedidos de esclarecimento após o laudo",
    },

    # ─── GRUPO B: COMPLEXIDADE TÉCNICA ───
    "nexo_controvertido": {
        "nome": "Nexo Causal Controvertido",
        "grupo": "B - Complexidade Técnica",
        "patterns": [
            r'(?i)nexo\s+(de\s+)?causal',
            r'(?i)causalidade',
            r'(?i)culpa\s+exclusiv',
            r'(?i)concausa',
            r'(?i)nega[r]?\s+(o\s+)?nexo',
            r'(?i)aus[êe]ncia\s+de\s+nexo',
            r'(?i)rompimento\s+do\s+nexo',
            r'(?i)excludente\s+de\s+(responsabilidade|causalidade)',
            r'(?i)fato\s+(de\s+terceiro|da\s+v[ií]tima|exclusiv)',
        ],
        "context_words": ["contestação", "defesa", "culpa", "causa"],
        "descricao": "A defesa contesta a relação de causa e efeito entre o fato e o dano",
    },
    "dimensoes_dano": {
        "nome": "Múltiplas Dimensões de Dano",
        "grupo": "B - Complexidade Técnica",
        "patterns": [
            r'(?i)dano\s+moral', r'(?i)dano\s+material',
            r'(?i)dano\s+est[ée]tic', r'(?i)dano\s+corporal',
            r'(?i)dano\s+psicol[oó]g', r'(?i)dano\s+exist[êe]ncial',
            r'(?i)lucros?\s+cessante', r'(?i)pens[ãa]o\s+(vital[ií]cia|mensal)',
            r'(?i)incapacidade\s+(total|parcial|permanente|tempor[áa]ria)',
        ],
        "context_words": ["indenização", "reparação", "dano"],
        "descricao": "Tipos distintos de dano que o perito deve avaliar separadamente",
    },
    "vicios_quesitos": {
        "nome": "Quesitos com Vícios de Formulação",
        "grupo": "B - Complexidade Técnica",
        "patterns": [
            # Pressuposicional
            r'(?i)supost[ao]', r'(?i)alegad[ao]',
            # Causalidade exclusiva (extrapola competência)
            r'(?i)exclusivamente', r'(?i)exclusiv[ao]\s+do\s+evento',
            # Composto (múltiplas perguntas)
            r'(?i)quesito.{0,200}(Descreva|Especifique|Justifique|Explique).{0,200}(Descreva|Especifique|Justifique|Explique)',
            # Poderia (resposta literal)
            r'(?i)o\s+perito\s+poderia',
        ],
        "context_words": ["quesito", "perito", "responder"],
        "descricao": "Quesitos mal formulados que exigem análise crítica antes de responder",
    },
    "docs_contraditorios": {
        "nome": "Documentação Contraditória",
        "grupo": "B - Complexidade Técnica",
        "patterns": [
            r'(?i)contradi[çc][ãa]o', r'(?i)contradit[oó]ri',
            r'(?i)vers[ãõ]o?\s+conflitante',
            r'(?i)(autor|ré|réu).{0,100}(nega|contesta|refuta|impugna)',
            r'(?i)diverg[êe]n', r'(?i)incompat[ií]vel',
        ],
        "context_words": ["contestação", "réplica", "autor", "réu"],
        "descricao": "Versões conflitantes entre as partes sobre os fatos",
    },
    "periciando_vulneravel": {
        "nome": "Periciando Vulnerável",
        "grupo": "B - Complexidade Técnica",
        "patterns": [
            r'(?i)menor\s+(imp[úu]bere|de\s+idade)',
            r'(?i)crian[çc]a', r'(?i)adolescente',
            r'(?i)idoso', r'(?i)incapaz',
            r'(?i)interdit[ao]', r'(?i)curador',
            r'(?i)representad[ao]\s+(pel[oa]|por)',
            r'(?i)segredo\s+de\s+justi[çc]a',
        ],
        "context_words": ["representante", "genitor", "curador", "ECA", "Estatuto"],
        "descricao": "Periciando que demanda cuidados especiais (menor, idoso, incapaz)",
    },
    "componente_securitario": {
        "nome": "Componente Securitário",
        "grupo": "B - Complexidade Técnica",
        "patterns": [
            r'(?i)ap[óo]lice', r'(?i)seguradora',
            r'(?i)denuncia[çc][ãa]o\s+[àa]\s+lide',
            r'(?i)cobertura.{0,50}seguro',
            r'(?i)exclus[ãa]o.{0,50}(cobertura|ap[óo]lice|seguro)',
            r'(?i)sinistro', r'(?i)prêmio\s+de\s+seguro',
            r'(?i)condi[çc][õo]es\s+gerais',
            r'(?i)SUSEP', r'(?i)ramo\s+\d{2}',
            r'(?i)seguro\s+(de\s+)?(vida|invalidez|prestamista|RC|responsabilidade)',
        ],
        "context_words": ["apólice", "cobertura", "exclusão", "seguradora", "sinistro"],
        "descricao": "Existência de seguro que impacta a perícia (coberturas, exclusões)",
    },
    "instrumentos_obrigatorios": {
        "nome": "Instrumentos e Escalas Obrigatórios",
        "grupo": "B - Complexidade Técnica",
        "patterns": [
            r'(?i)goniometr', r'(?i)dinamometr',
            r'(?i)escala\s+de\s+(dor|funcionalidade|incapacidade)',
            r'(?i)CID.{0,5}(10|11)', r'(?i)\bCIF\b',
            r'(?i)classifica[çc][ãa]o.{0,30}(est[ée]tic|funcional|dano)',
            r'(?i)tabela.{0,30}(DPVAT|SUSEP|Baremo)',
            r'(?i)for[çc]a\s+de\s+preens[ãa]o',
        ],
        "context_words": ["avaliação", "escala", "instrumento", "classificação"],
        "descricao": "Instrumentos de avaliação exigidos pelos quesitos",
    },

    # ─── GRUPO C: CONTEXTO PROCESSUAL ───
    "multiplas_partes": {
        "nome": "Múltiplas Partes",
        "grupo": "C - Contexto Processual",
        "patterns": [
            r'(?i)denuncia[çc][ãa]o\s+[àa]\s+lide',
            r'(?i)litiscons[oó]rcio',
            r'(?i)chamamento\s+ao\s+processo',
            r'(?i)(terceiro|interveniente)',
            r'(?i)minist[ée]rio\s+p[úu]blico',
            r'(?i)fiscal\s+da\s+lei',
        ],
        "context_words": ["autor", "réu", "ré", "terceiro", "MP", "advogado"],
        "descricao": "Processo com 3+ polos de interesse distintos",
    },
    "pericia_anterior_falha": {
        "nome": "Perícia Anterior que Falhou",
        "grupo": "C - Contexto Processual",
        "patterns": [
            r'(?i)destitu[ií][çc][ãa]o\s+do\s+perit',
            r'(?i)recusa\s+d[ao]\s+perit',
            r'(?i)perit[ao]\s+anterior',
            r'(?i)nova\s+nomea[çc][ãa]o',
            r'(?i)substituir\s+o\s+perit',
            r'(?i)perit[ao]\s+(nomeado|anterior).{0,50}recus',
            r'(?i)escusa', r'(?i)recusou\s+a\s+nomea[çc][ãa]o',
        ],
        "context_words": ["nomeação", "perito", "anterior", "recusa", "destituição"],
        "descricao": "Houve nomeação anterior que não prosperou",
    },
    "longa_tramitacao": {
        "nome": "Longa Tramitação",
        "grupo": "C - Contexto Processual",
        "patterns": [
            # Detecta datas antigas de distribuição/ajuizamento
            r'(?i)distribu[ií]d[ao]\s+em\s+\d{2}/\d{2}/(201[0-9]|202[0-3])',
            r'(?i)ajuizad[ao]\s+em\s+\d{2}/\d{2}/(201[0-9]|202[0-3])',
            r'(?i)desde\s+(201[0-9]|202[0-3])',
        ],
        "context_words": ["distribuição", "ajuizamento", "tramita"],
        "descricao": "Processo tramita há 3+ anos",
    },
    "segredo_justica": {
        "nome": "Segredo de Justiça",
        "grupo": "C - Contexto Processual",
        "patterns": [
            r'(?i)segredo\s+de\s+justi[çc]a',
            r'(?i)tramita[çc][ãa]o\s+em\s+segredo',
            r'(?i)sigilo',
        ],
        "context_words": ["menor", "segredo", "sigilo"],
        "descricao": "Processo tramita em segredo de justiça",
    },
    "mp_fiscal": {
        "nome": "Ministério Público como Fiscal da Lei",
        "grupo": "C - Contexto Processual",
        "patterns": [
            r'(?i)minist[ée]rio\s+p[úu]blico',
            r'(?i)fiscal\s+da\s+lei',
            r'(?i)promot[oa]r\s+de\s+justi[çc]a',
            r'(?i)parecer\s+do\s+MP',
            r'(?i)vista\s+ao\s+MP',
            r'(?i)manifesta[çc][ãa]o\s+do\s+minist[ée]rio',
        ],
        "context_words": ["MP", "promotor", "fiscal", "menor", "incapaz"],
        "descricao": "MP atua como fiscal da lei (menor, incapaz, interesse público)",
    },
}


# ══════════════════════════════════════════════════════════════
# EXTRATORES ESPECÍFICOS
# ══════════════════════════════════════════════════════════════

def extrair_ids_pje(texto: str) -> List[dict]:
    """Extrai IDs de documentos PJe (sequências de 10-13 dígitos em contexto)."""
    resultados = []
    for i, linha in enumerate(texto.split('\n'), 1):
        # Padrão: Id. XXXXXXXXXXX ou ID XXXXXXXXXXX ou Num. XXXXXXXXXXX
        matches = re.finditer(r'(?:Id\.?|ID|Num\.?|Documento)\s*[:.]?\s*(\d{10,13})', linha)
        for m in matches:
            resultados.append({
                "id": m.group(1),
                "linha": i,
                "contexto": linha.strip()[:200]
            })
    return resultados

def extrair_partes(texto: str) -> dict:
    """Extrai informações sobre as partes processuais."""
    partes = {"autores": [], "reus": [], "advogados": [], "crms": [], "oabs": []}

    for i, linha in enumerate(texto.split('\n'), 1):
        # OABs
        for m in re.finditer(r'OAB[/\s]*([A-Z]{2})[\s]*(\d[\d.]+)', linha):
            partes["oabs"].append({
                "estado": m.group(1), "numero": m.group(2),
                "linha": i, "contexto": linha.strip()[:200]
            })
        # CRMs
        for m in re.finditer(r'CRM[/\s]*([A-Z]{2})[\s]*([\d.]+)', linha):
            partes["crms"].append({
                "estado": m.group(1), "numero": m.group(2),
                "linha": i, "contexto": linha.strip()[:200]
            })

    return partes

def extrair_valores_monetarios(texto: str) -> List[dict]:
    """Extrai valores monetários mencionados."""
    resultados = []
    for i, linha in enumerate(texto.split('\n'), 1):
        for m in re.finditer(r'R\$\s*([\d.,]+)', linha):
            valor_str = m.group(1).replace('.', '').replace(',', '.')
            try:
                valor = float(valor_str)
                resultados.append({
                    "valor": valor, "original": f"R$ {m.group(1)}",
                    "linha": i, "contexto": linha.strip()[:200]
                })
            except ValueError:
                pass
    return resultados

def extrair_datas(texto: str) -> List[dict]:
    """Extrai datas no formato DD/MM/AAAA."""
    resultados = []
    for i, linha in enumerate(texto.split('\n'), 1):
        for m in re.finditer(r'(\d{2}/\d{2}/\d{4})', linha):
            resultados.append({
                "data": m.group(1), "linha": i,
                "contexto": linha.strip()[:200]
            })
    return resultados

def contar_quesitos(texto: str) -> dict:
    """Tenta contar quesitos numerados."""
    # Padrão: "1." ou "1)" ou "Quesito 1" no início de linha ou após quebra
    quesitos_numerados = re.findall(
        r'(?:^|\n)\s*(?:Quesito\s+)?(\d{1,2})\s*[.):\-–]',
        texto, re.MULTILINE
    )

    # Buscar blocos de quesitos (petições específicas)
    blocos = []
    for m in re.finditer(
        r'(?i)(quesitos?|apresenta.{0,30}quesitos?)(.*?)(?=\n\n\n|\Z)',
        texto, re.DOTALL
    ):
        bloco = m.group(0)[:2000]
        nums = re.findall(r'(?:^|\n)\s*(\d{1,2})\s*[.):\-–]', bloco)
        if nums:
            blocos.append({
                "inicio": m.start(),
                "numeros": [int(n) for n in nums],
                "max_quesito": max(int(n) for n in nums),
                "trecho": bloco[:300]
            })

    return {
        "total_mencoes_quesito": len(re.findall(r'(?i)quesito', texto)),
        "blocos_detectados": blocos,
        "maior_numero_detectado": max([int(n) for n in quesitos_numerados], default=0),
    }


# ══════════════════════════════════════════════════════════════
# MOTOR DE BUSCA PRINCIPAL
# ══════════════════════════════════════════════════════════════

@dataclass
class Achado:
    """Um achado de fator de complexidade no texto."""
    fator: str
    nome: str
    grupo: str
    linha: int
    trecho: str
    pattern_usado: str
    id_pje_proximo: Optional[str] = None
    score_confianca: float = 0.0

def buscar_fator(texto: str, linhas: List[str], fator_key: str, fator_config: dict,
                 ids_pje: List[dict]) -> List[Achado]:
    """Busca um fator de complexidade no texto."""
    achados = []

    patterns = fator_config.get("patterns", [])
    context_words = fator_config.get("context_words", [])

    for pattern in patterns:
        try:
            for i, linha in enumerate(linhas, 1):
                if re.search(pattern, linha):
                    # Verificar co-ocorrência com palavras de contexto (janela de 10 linhas)
                    janela_start = max(0, i - 6)
                    janela_end = min(len(linhas), i + 5)
                    janela = ' '.join(linhas[janela_start:janela_end])

                    score = 0.5  # Base: encontrou o pattern
                    for cw in context_words:
                        if re.search(f'(?i){cw}', janela):
                            score += 0.1
                    score = min(score, 1.0)

                    # Encontrar ID PJe mais próximo
                    id_proximo = None
                    menor_dist = float('inf')
                    for id_info in ids_pje:
                        dist = abs(id_info["linha"] - i)
                        if dist < menor_dist and dist < 100:  # max 100 linhas de distância
                            menor_dist = dist
                            id_proximo = id_info["id"]

                    # Pegar contexto (3 linhas antes, a linha, 3 linhas depois)
                    ctx_start = max(0, i - 4)
                    ctx_end = min(len(linhas), i + 3)
                    trecho_ctx = '\n'.join(
                        f"  L{ctx_start + j + 1}: {linhas[ctx_start + j]}"
                        for j in range(ctx_end - ctx_start)
                    )

                    achados.append(Achado(
                        fator=fator_key,
                        nome=fator_config["nome"],
                        grupo=fator_config["grupo"],
                        linha=i,
                        trecho=trecho_ctx,
                        pattern_usado=pattern,
                        id_pje_proximo=id_proximo,
                        score_confianca=score,
                    ))
        except re.error:
            pass

    # Deduplicar: manter apenas 1 achado por janela de 5 linhas
    achados_dedup = []
    linhas_usadas = set()
    for a in sorted(achados, key=lambda x: -x.score_confianca):
        janela = range(a.linha - 3, a.linha + 4)
        if not any(l in linhas_usadas for l in janela):
            achados_dedup.append(a)
            linhas_usadas.update(janela)

    return achados_dedup[:5]  # Max 5 achados por fator

def buscar_especialidades(texto: str, linhas: List[str]) -> dict:
    """Busca especialidades médicas com contagem de evidências."""
    resultados = {}
    config = FATORES["especialidades"]["patterns_por_especialidade"]

    for especialidade, patterns in config.items():
        evidencias = []
        for pattern in patterns:
            try:
                for i, linha in enumerate(linhas, 1):
                    if re.search(pattern, linha):
                        evidencias.append({
                            "linha": i,
                            "trecho": linha.strip()[:200],
                            "pattern": pattern,
                        })
            except re.error:
                pass

        if evidencias:
            # Deduplicar por proximidade
            evidencias_dedup = []
            linhas_usadas = set()
            for e in evidencias:
                if e["linha"] not in linhas_usadas:
                    evidencias_dedup.append(e)
                    for l in range(e["linha"] - 2, e["linha"] + 3):
                        linhas_usadas.add(l)

            resultados[especialidade] = {
                "total_ocorrencias": len(evidencias),
                "evidencias_unicas": len(evidencias_dedup),
                "exemplos": evidencias_dedup[:3],
            }

    return resultados


# ══════════════════════════════════════════════════════════════
# GERAÇÃO DE RELATÓRIO
# ══════════════════════════════════════════════════════════════

def gerar_relatorio_md(
    arquivo: str,
    total_linhas: int,
    ids_pje: List[dict],
    partes: dict,
    valores: List[dict],
    datas: List[dict],
    quesitos: dict,
    especialidades: dict,
    achados_por_fator: dict,
) -> str:
    """Gera relatório em Markdown."""

    md = []
    md.append("# TRIAGEM AUTOMÁTICA DE COMPLEXIDADE PROCESSUAL")
    md.append(f"\n**Arquivo analisado:** `{arquivo}`")
    md.append(f"**Total de linhas:** {total_linhas}")
    md.append(f"**IDs PJe detectados:** {len(ids_pje)}")
    md.append(f"**Datas detectadas:** {len(datas)}")
    md.append(f"**Valores monetários detectados:** {len(valores)}")
    md.append(f"\n---\n")

    # ── DADOS BÁSICOS ──
    md.append("## 1. DADOS BÁSICOS EXTRAÍDOS\n")

    md.append("### OABs encontradas")
    if partes["oabs"]:
        for oab in partes["oabs"]:
            md.append(f"- OAB/{oab['estado']} {oab['numero']} — L{oab['linha']}: `{oab['contexto'][:100]}`")
    else:
        md.append("- Nenhuma OAB detectada")

    md.append("\n### CRMs encontrados")
    if partes["crms"]:
        for crm in partes["crms"]:
            md.append(f"- CRM/{crm['estado']} {crm['numero']} — L{crm['linha']}: `{crm['contexto'][:100]}`")
    else:
        md.append("- Nenhum CRM detectado")

    md.append("\n### Valores monetários relevantes")
    valores_sorted = sorted(valores, key=lambda x: -x["valor"])[:10]
    for v in valores_sorted:
        md.append(f"- **{v['original']}** — L{v['linha']}: `{v['contexto'][:100]}`")

    md.append("\n### Quesitos")
    md.append(f"- Menções a 'quesito': {quesitos['total_mencoes_quesito']}")
    md.append(f"- Maior número de quesito detectado: {quesitos['maior_numero_detectado']}")
    if quesitos["blocos_detectados"]:
        for bloco in quesitos["blocos_detectados"]:
            md.append(f"- Bloco detectado: quesitos até nº {bloco['max_quesito']}")
            md.append(f"  ```\n  {bloco['trecho'][:200]}\n  ```")

    # ── ESPECIALIDADES ──
    md.append("\n---\n")
    md.append("## 2. ESPECIALIDADES MÉDICAS DETECTADAS\n")

    if especialidades:
        md.append("| Especialidade | Ocorrências | Evidências únicas | Presente? |")
        md.append("|---------------|-------------|-------------------|-----------|")
        for esp, dados in sorted(especialidades.items(), key=lambda x: -x[1]["total_ocorrencias"]):
            presente = "✅ SIM" if dados["evidencias_unicas"] >= 2 else "⚠️ VERIFICAR" if dados["evidencias_unicas"] == 1 else "❌"
            md.append(f"| {esp} | {dados['total_ocorrencias']} | {dados['evidencias_unicas']} | {presente} |")

        md.append("\n### Exemplos de evidência por especialidade\n")
        for esp, dados in especialidades.items():
            if dados["exemplos"]:
                md.append(f"**{esp}:**")
                for ex in dados["exemplos"][:2]:
                    md.append(f"- L{ex['linha']}: `{ex['trecho'][:150]}`")
                md.append("")
    else:
        md.append("Nenhuma especialidade detectada automaticamente.")

    # ── FATORES DE COMPLEXIDADE ──
    md.append("\n---\n")
    md.append("## 3. FATORES DE COMPLEXIDADE\n")

    # Resumo
    presentes = {k: v for k, v in achados_por_fator.items() if v}
    ausentes = {k: v for k, v in achados_por_fator.items() if not v}

    md.append(f"**Fatores detectados:** {len(presentes)}/{len(achados_por_fator)}\n")

    md.append("### Resumo rápido\n")
    md.append("| Fator | Grupo | Detectado? | Linhas | ID PJe próximo |")
    md.append("|-------|-------|-----------|--------|----------------|")

    for fator_key, achados in sorted(achados_por_fator.items()):
        config = FATORES.get(fator_key, {})
        nome = config.get("nome", fator_key)
        grupo = config.get("grupo", "?")
        if achados:
            linhas_str = ", ".join(str(a.linha) for a in achados[:3])
            id_str = achados[0].id_pje_proximo or "—"
            md.append(f"| {nome} | {grupo} | ✅ SIM ({len(achados)} achados) | {linhas_str} | {id_str} |")
        else:
            md.append(f"| {nome} | {grupo} | ❌ NÃO | — | — |")

    # Detalhamento
    md.append("\n### Detalhamento dos fatores PRESENTES\n")

    for fator_key, achados in sorted(achados_por_fator.items()):
        if not achados:
            continue
        config = FATORES.get(fator_key, {})

        md.append(f"#### {config.get('nome', fator_key)}")
        md.append(f"**Grupo:** {config.get('grupo', '?')}")
        md.append(f"**Descrição:** {config.get('descricao', '')}")
        md.append(f"**Achados:** {len(achados)}\n")

        for j, achado in enumerate(achados, 1):
            md.append(f"**Achado {j}** (L{achado.linha}, confiança: {achado.score_confianca:.0%})")
            if achado.id_pje_proximo:
                md.append(f"ID PJe próximo: **{achado.id_pje_proximo}**")
            md.append(f"```")
            md.append(achado.trecho)
            md.append(f"```")
            md.append(f"Pattern: `{achado.pattern_usado}`\n")

        md.append("---\n")

    # Fatores NÃO detectados
    md.append("\n### Fatores NÃO detectados (verificar manualmente)\n")
    for fator_key in sorted(ausentes.keys()):
        config = FATORES.get(fator_key, {})
        md.append(f"- **{config.get('nome', fator_key)}** — {config.get('descricao', '')}")

    # ── IDS PJE ──
    md.append("\n---\n")
    md.append("## 4. ÍNDICE DE IDs PJe DETECTADOS\n")
    md.append("| ID | Linha | Contexto |")
    md.append("|-----|-------|----------|")
    for id_info in ids_pje[:30]:
        md.append(f"| {id_info['id']} | L{id_info['linha']} | `{id_info['contexto'][:80]}` |")

    # ── COMANDOS MANUAIS ──
    md.append("\n---\n")
    md.append("## 5. COMANDOS PARA BUSCA MANUAL\n")
    md.append("Use estes comandos no TEXTO-EXTRAIDO.txt para verificar manualmente:\n")
    md.append("```bash")
    md.append("# Assistente técnico")
    md.append('grep -in "assistente.t[eé]cnic" TEXTO-EXTRAIDO.txt')
    md.append("")
    md.append("# Quesitos (com contexto)")
    md.append('grep -in -B2 -A5 "quesito" TEXTO-EXTRAIDO.txt')
    md.append("")
    md.append("# IDs de documentos PJe")
    md.append('grep -n "Id\\.\\s*[0-9]\\{10,\\}" TEXTO-EXTRAIDO.txt')
    md.append("")
    md.append("# Nexo causal")
    md.append('grep -in "nexo.causal\\|causalidade\\|excludente" TEXTO-EXTRAIDO.txt')
    md.append("")
    md.append("# Danos (todos os tipos)")
    md.append('grep -in "dano.moral\\|dano.material\\|dano.est\\|dano.corporal\\|lucros.cessant\\|pensão" TEXTO-EXTRAIDO.txt')
    md.append("")
    md.append("# Seguro / Apólice")
    md.append('grep -in "apólice\\|seguradora\\|cobertura\\|exclusão.*segur\\|SUSEP\\|sinistro" TEXTO-EXTRAIDO.txt')
    md.append("")
    md.append("# Partes (OAB e CRM)")
    md.append('grep -oP "OAB[/\\s]*[A-Z]{2}[\\s]*[\\d.]+" TEXTO-EXTRAIDO.txt | sort -u')
    md.append('grep -oP "CRM[/\\s]*[A-Z]{2}[\\s]*[\\d.]+" TEXTO-EXTRAIDO.txt | sort -u')
    md.append("")
    md.append("# Valor da causa")
    md.append('grep -in "valor.da.causa" TEXTO-EXTRAIDO.txt')
    md.append("")
    md.append("# Justiça gratuita")
    md.append('grep -in "grat\\|AJG\\|assistência judiciária" TEXTO-EXTRAIDO.txt')
    md.append("")
    md.append("# Perícia anterior / escusa / recusa")
    md.append('grep -in "escusa\\|recus.*perit\\|destitu.*perit\\|nova.nomea" TEXTO-EXTRAIDO.txt')
    md.append("")
    md.append("# Segredo de justiça")
    md.append('grep -in "segredo.de.just\\|sigilo" TEXTO-EXTRAIDO.txt')
    md.append("")
    md.append("# Ministério Público")
    md.append('grep -in "ministério.público\\|fiscal.da.lei\\|promotor" TEXTO-EXTRAIDO.txt')
    md.append("```")

    return '\n'.join(md)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("USO: python3 triagem_complexidade.py TEXTO-EXTRAIDO.txt [--output SAIDA.md] [--json]")
        print("")
        print("EXEMPLO:")
        print("  python3 triagem_complexidade.py meu-processo/TEXTO-EXTRAIDO.txt")
        print("  python3 triagem_complexidade.py meu-processo/TEXTO-EXTRAIDO.txt --output TRIAGEM.md")
        sys.exit(1)

    arquivo = sys.argv[1]
    output_file = None
    output_json = False

    for i, arg in enumerate(sys.argv):
        if arg == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
        if arg == "--json":
            output_json = True

    # Ler arquivo
    with open(arquivo, 'r', encoding='utf-8', errors='replace') as f:
        texto = f.read()

    linhas = texto.split('\n')
    total_linhas = len(linhas)

    print(f"[1/6] Lendo {arquivo} ({total_linhas} linhas)...")

    # Extrações básicas
    print(f"[2/6] Extraindo IDs PJe, partes, valores, datas...")
    ids_pje = extrair_ids_pje(texto)
    partes = extrair_partes(texto)
    valores = extrair_valores_monetarios(texto)
    datas = extrair_datas(texto)
    quesitos = contar_quesitos(texto)

    # Especialidades
    print(f"[3/6] Detectando especialidades médicas...")
    especialidades = buscar_especialidades(texto, linhas)

    # Fatores de complexidade
    print(f"[4/6] Buscando fatores de complexidade...")
    achados_por_fator = {}
    for fator_key, fator_config in FATORES.items():
        if fator_key == "especialidades":
            continue  # Já tratado acima
        achados = buscar_fator(texto, linhas, fator_key, fator_config, ids_pje)
        achados_por_fator[fator_key] = achados
        if achados:
            print(f"  ✅ {fator_config['nome']}: {len(achados)} achado(s)")
        else:
            print(f"  ❌ {fator_config['nome']}: não detectado")

    # Gerar relatório
    print(f"[5/6] Gerando relatório...")

    if output_json:
        resultado = {
            "arquivo": arquivo,
            "total_linhas": total_linhas,
            "ids_pje": ids_pje[:20],
            "partes": partes,
            "valores": [v for v in valores if v["valor"] > 100],
            "quesitos": quesitos,
            "especialidades": {k: {"total": v["total_ocorrencias"], "unicas": v["evidencias_unicas"]}
                             for k, v in especialidades.items()},
            "fatores": {
                k: [{"linha": a.linha, "trecho": a.trecho[:200], "id_pje": a.id_pje_proximo, "confianca": a.score_confianca}
                    for a in v]
                for k, v in achados_por_fator.items()
            },
            "resumo": {
                "fatores_presentes": len([v for v in achados_por_fator.values() if v]),
                "fatores_total": len(achados_por_fator),
                "especialidades_detectadas": len(especialidades),
            }
        }
        saida = json.dumps(resultado, indent=2, ensure_ascii=False)
    else:
        saida = gerar_relatorio_md(
            arquivo, total_linhas, ids_pje, partes, valores, datas,
            quesitos, especialidades, achados_por_fator,
        )

    # Salvar ou imprimir
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(saida)
        print(f"[6/6] Relatório salvo em: {output_file}")
    else:
        if not output_file:
            # Auto-gerar nome
            base = os.path.dirname(arquivo)
            auto_name = os.path.join(base, "TRIAGEM-COMPLEXIDADE.md")
            with open(auto_name, 'w', encoding='utf-8') as f:
                f.write(saida)
            print(f"[6/6] Relatório salvo em: {auto_name}")

    # Resumo final
    presentes = len([v for v in achados_por_fator.values() if v])
    total = len(achados_por_fator)
    print(f"\n{'='*60}")
    print(f"RESULTADO: {presentes}/{total} fatores detectados")
    print(f"Especialidades: {', '.join(especialidades.keys()) if especialidades else 'nenhuma'}")
    print(f"IDs PJe: {len(ids_pje)} detectados")
    print(f"Quesitos: ~{quesitos['maior_numero_detectado']} detectados")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
