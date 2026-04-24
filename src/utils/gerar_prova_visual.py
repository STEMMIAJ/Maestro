#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_prova_visual.py — Prova Visual v2: petição vs. processo lado a lado

Mostra a petição completa na esquerda com cada frase verificável destacada.
Na direita, o processo INTEIRO, rolável, com scroll automático ao clicar.
Lista 100% das afirmações no topo (sumário clicável).

Uso:
    python3 gerar_prova_visual.py \
        --pdf saida/peticoes-cowork/PROPOSTA-HONORARIOS-INHAPIM.pdf \
        --json processos/[CNJ]/verificacao-proposta-honorarios.json \
        --texto processos/[CNJ]/TEXTO-EXTRAIDO.txt \
        --output processos/[CNJ]/PROVA-VISUAL.html
"""

import argparse
import json
import html
import os
import re
import subprocess
import sys


def extrair_texto_pdf(pdf_path: str) -> str:
    """Extrai texto do PDF usando pdftotext."""
    result = subprocess.run(
        ['pdftotext', '-layout', pdf_path, '-'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Erro ao extrair texto do PDF: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def limpar_texto_peticao(texto: str) -> str:
    """Remove headers/footers repetidos do pdftotext."""
    linhas = texto.split('\n')
    resultado = []
    pular = False
    for i, linha in enumerate(linhas):
        if linha.strip().startswith('Dr. Jésus E. Nolêto da Penha') and i > 5:
            pular = True
            continue
        if pular:
            if linha.strip() in ('', 'Médico - Perito Judicial',
                                  'CRM-MG 92.148',
                                  'Membro da ABMLPM – Associação Brasileira de Medicina Legal e Perícia Médica'):
                continue
            pular = False
        if 'Empresarial Maria Costa, Rua João Pinheiro' in linha:
            continue
        if '99900-1122' in linha and 'perito@drjesus' in linha:
            continue
        resultado.append(linha)
    return '\n'.join(resultado)


def extrair_linhas_ref(texto_fonte: str) -> list:
    """Extrai números de linha mencionados em fontes."""
    return [int(m) for m in re.findall(r'[Ll]inha\s+(\d+)', texto_fonte)]


def preparar_afirmacoes(data: dict) -> list:
    """Converte JSON de verificação em lista plana."""
    afirmacoes = []
    idx = 0
    for secao in data.get('secoes', []):
        for af in secao.get('afirmacoes', []):
            idx += 1
            linhas_ref = []
            fontes_texto = []
            for f in af.get('fontes', []):
                loc = f.get('localizacao', '') + ' ' + f.get('trecho_fonte', '')
                linhas_ref.extend(extrair_linhas_ref(loc))
                fontes_texto.append({
                    'trecho': f.get('trecho_fonte', ''),
                    'localizacao': f.get('localizacao', '')
                })
            afirmacoes.append({
                'idx': idx,
                'secao': secao.get('titulo', ''),
                'trecho': af.get('trecho_peticao', ''),
                'dados': af.get('dados_verificaveis', []),
                'status': af.get('status', ''),
                'linhas_ref': sorted(set(linhas_ref)),
                'fontes': fontes_texto,
                'alertas': af.get('alertas', [])
            })
    return afirmacoes


def encontrar_posicao(texto_peticao: str, trecho: str) -> tuple:
    """Encontra a posição do trecho no texto da petição.
    Retorna (inicio, fim) ou None."""
    pos = texto_peticao.find(trecho)
    if pos >= 0:
        return (pos, pos + len(trecho))

    texto_norm = re.sub(r'\s+', ' ', texto_peticao)
    trecho_norm = re.sub(r'\s+', ' ', trecho)
    pos = texto_norm.find(trecho_norm)
    if pos >= 0:
        return mapear_posicao_normalizada(texto_peticao, texto_norm, pos, len(trecho_norm))

    texto_lower = texto_norm.lower()
    trecho_lower = trecho_norm.lower()
    pos = texto_lower.find(trecho_lower)
    if pos >= 0:
        return mapear_posicao_normalizada(texto_peticao, texto_norm, pos, len(trecho_norm))

    for corte in [40, 30, 20, 15]:
        if len(trecho_lower) > corte:
            sub = trecho_lower[:corte]
            pos = texto_lower.find(sub)
            if pos >= 0:
                fim = min(pos + len(trecho_norm), len(texto_norm))
                return mapear_posicao_normalizada(texto_peticao, texto_norm, pos, fim - pos)

    numeros = re.findall(r'\d[\d./§º,\-]+', trecho)
    for num in numeros:
        if len(num) >= 4:
            pos = texto_peticao.find(num)
            if pos >= 0:
                inicio = max(0, pos - 5)
                fim = min(len(texto_peticao), pos + len(num) + 5)
                while inicio > 0 and texto_peticao[inicio] not in '\n.':
                    inicio -= 1
                while fim < len(texto_peticao) and texto_peticao[fim] not in '\n.':
                    fim += 1
                return (inicio, fim)

    nomes = re.findall(r'[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{3,}', trecho)
    for nome in nomes:
        if nome in ('CPC', 'CNJ', 'CRM', 'OAB', 'ART', 'BANCO'):
            continue
        pos = texto_peticao.find(nome)
        if pos < 0:
            pos = texto_peticao.lower().find(nome.lower())
        if pos >= 0:
            inicio = max(0, pos - 5)
            fim = min(len(texto_peticao), pos + len(nome) + 5)
            while inicio > 0 and texto_peticao[inicio] not in '\n.':
                inicio -= 1
            while fim < len(texto_peticao) and texto_peticao[fim] not in '\n.':
                fim += 1
            return (inicio, fim)

    palavras = [p for p in re.findall(r'\b\w{7,}\b', trecho) if p.lower() not in
                ('processo', 'conforme', 'pereira', 'perícia', 'pericia',
                 'honorários', 'honorarios', 'petição', 'peticao')]
    if len(palavras) >= 2:
        pattern = r'(?i)' + re.escape(palavras[0]) + r'.{0,100}' + re.escape(palavras[1])
        m = re.search(pattern, texto_peticao)
        if m:
            return (m.start(), m.end())
    elif len(palavras) == 1:
        m = re.search(r'(?i)' + re.escape(palavras[0]), texto_peticao)
        if m:
            return (m.start(), m.end())

    return None


def mapear_posicao_normalizada(original: str, normalizado: str, pos_norm: int, tam_norm: int) -> tuple:
    """Mapeia posição do texto normalizado de volta ao original."""
    chars_antes = 0
    pos_orig_inicio = 0
    j = 0
    for i, c in enumerate(original):
        if j >= pos_norm:
            pos_orig_inicio = i
            break
        if c == normalizado[j]:
            j += 1
        elif c in ' \n\r\t':
            continue
        else:
            j += 1

    chars_no_trecho = 0
    pos_orig_fim = pos_orig_inicio
    j = 0
    for i in range(pos_orig_inicio, len(original)):
        if j >= tam_norm:
            pos_orig_fim = i
            break
        c = original[i]
        norm_c = normalizado[pos_norm + j] if (pos_norm + j) < len(normalizado) else ''
        if c == norm_c:
            j += 1
        elif c in ' \n\r\t':
            continue
        else:
            j += 1
        pos_orig_fim = i + 1

    return (pos_orig_inicio, pos_orig_fim)


def escapar_js(s: str) -> str:
    """Escapa para uso em string JS."""
    return (s.replace('\\', '\\\\')
             .replace("'", "\\'")
             .replace('"', '\\"')
             .replace('\n', '\\n')
             .replace('\r', '')
             .replace('</', '<\\/'))


def gerar_html(texto_peticao: str, afirmacoes: list, linhas_processo: list,
               processo: str, resumo: dict) -> str:
    """Gera o HTML de prova visual v2."""

    # Marcar posições das afirmações no texto da petição
    marcacoes = []
    for af in afirmacoes:
        pos = encontrar_posicao(texto_peticao, af['trecho'])
        if pos is None:
            for dado in af.get('dados', []):
                pos = encontrar_posicao(texto_peticao, dado)
                if pos:
                    break
        marcacoes.append({
            'af': af,
            'pos': pos
        })

    # Construir HTML da petição com spans
    marcacoes_com_pos = [(m, m['pos']) for m in marcacoes if m['pos'] is not None]
    marcacoes_com_pos.sort(key=lambda x: x[1][0])

    peticao_html_parts = []
    ultimo_fim = 0
    for m, (inicio, fim) in marcacoes_com_pos:
        idx = m['af']['idx']
        status = m['af']['status']
        if inicio > ultimo_fim:
            peticao_html_parts.append(html.escape(texto_peticao[ultimo_fim:inicio]))
        classe = 'marca confirmado' if status == 'confirmado' else 'marca divergente' if status == 'divergente' else 'marca pendente'
        peticao_html_parts.append(
            f'<span class="{classe}" data-idx="{idx}" id="marca-{idx}" '
            f'onclick="selecionarAfirmacao({idx})" '
            f'title="#{idx}: {html.escape(m["af"]["secao"])}">'
        )
        peticao_html_parts.append(html.escape(texto_peticao[inicio:fim]))
        peticao_html_parts.append('</span>')
        ultimo_fim = fim

    if ultimo_fim < len(texto_peticao):
        peticao_html_parts.append(html.escape(texto_peticao[ultimo_fim:]))

    peticao_html = ''.join(peticao_html_parts)

    # Verificar quais afirmações têm posição no texto
    tem_posicao = set()
    for m in marcacoes:
        if m['pos'] is not None:
            tem_posicao.add(m['af']['idx'])

    # Preparar dados JS
    afirmacoes_js = json.dumps([{
        'idx': a['idx'],
        'secao': a['secao'],
        'trecho': a['trecho'],
        'status': a['status'],
        'linhas_ref': a['linhas_ref'],
        'fontes': a['fontes'],
        'alertas': a['alertas'],
        'tem_posicao': a['idx'] in tem_posicao
    } for a in afirmacoes], ensure_ascii=False)

    linhas_js_parts = []
    for linha in linhas_processo:
        linhas_js_parts.append("'" + escapar_js(linha) + "'")
    linhas_js = ',\n'.join(linhas_js_parts)

    total = resumo.get('total_afirmacoes', len(afirmacoes))
    confirmadas = resumo.get('confirmadas', 0)
    divergentes = resumo.get('divergentes', 0)
    sem_fonte = resumo.get('sem_fonte', 0)
    localizadas = len(tem_posicao)
    nao_localizadas = len(afirmacoes) - localizadas

    # Gerar lista de afirmações (sumário)
    sumario_html = '<div class="sumario">'
    sumario_html += f'<div class="sumario-titulo">TODAS AS AFIRMACOES VERIFICADAS ({len(afirmacoes)})</div>'
    for af in afirmacoes:
        status_icon = '&#10003;' if af['status'] == 'confirmado' else '&#10007;' if af['status'] == 'divergente' else '&#9679;'
        status_cls = 'sum-ok' if af['status'] == 'confirmado' else 'sum-div' if af['status'] == 'divergente' else 'sum-pend'
        pos_tag = '' if af['idx'] in tem_posicao else ' <span class="sem-pos-tag">sem posicao no texto</span>'
        trecho_curto = html.escape(af['trecho'][:120]) + ('...' if len(af['trecho']) > 120 else '')
        sumario_html += (
            f'<div class="sum-item {status_cls}" onclick="selecionarAfirmacao({af["idx"]})">'
            f'<span class="sum-num">#{af["idx"]}</span>'
            f'<span class="sum-icon">{status_icon}</span>'
            f'<span class="sum-texto">{trecho_curto}{pos_tag}</span>'
            f'</div>'
        )
    sumario_html += '</div>'

    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Prova Visual — {html.escape(processo)}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #ffffff; color: #1a1a1a; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}

/* BARRA TOPO */
.barra-topo {{ background: #f0f0f0; padding: 10px 20px; display: flex; align-items: center; gap: 16px; border-bottom: 2px solid #2563eb; flex-shrink: 0; }}
.barra-topo .titulo {{ font-size: 14px; font-weight: 700; color: #2563eb; }}
.barra-topo .info {{ font-size: 12px; color: #555; }}
.contagem {{ display: flex; gap: 12px; margin-left: auto; }}
.contagem span {{ font-size: 12px; padding: 3px 10px; border-radius: 10px; font-weight: 600; }}
.c-ok {{ background: #dcfce7; color: #166534; }}
.c-div {{ background: #fee2e2; color: #991b1b; }}
.c-sf {{ background: #fef9c3; color: #854d0e; }}

/* PAINEL PRINCIPAL */
.paineis {{ display: flex; flex: 1; overflow: hidden; }}

/* COLUNA ESQUERDA — PETICAO */
.col-peticao {{ width: 50%; overflow-y: auto; border-right: 2px solid #e5e7eb; background: #ffffff; display: flex; flex-direction: column; }}
.col-peticao-header {{ color: #2563eb; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; padding: 12px 24px 8px; background: #ffffff; border-bottom: 1px solid #e5e7eb; flex-shrink: 0; font-weight: 700; }}
.col-peticao-body {{ flex: 1; overflow-y: auto; padding: 0; }}

/* SUMARIO DE AFIRMACOES */
.sumario {{ background: #fafafa; border-bottom: 2px solid #e5e7eb; padding: 12px 20px; }}
.sumario-titulo {{ font-size: 11px; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }}
.sum-item {{ display: flex; align-items: flex-start; gap: 6px; padding: 5px 8px; border-radius: 4px; cursor: pointer; font-size: 12px; line-height: 1.4; transition: background 0.15s; }}
.sum-item:hover {{ background: #f0f0f0; }}
.sum-num {{ font-weight: 700; color: #6b7280; min-width: 28px; flex-shrink: 0; }}
.sum-icon {{ flex-shrink: 0; font-size: 14px; }}
.sum-texto {{ flex: 1; color: #374151; }}
.sum-ok .sum-icon {{ color: #16a34a; }}
.sum-div .sum-icon {{ color: #dc2626; }}
.sum-pend .sum-icon {{ color: #ca8a04; }}
.sem-pos-tag {{ font-size: 10px; background: #fef3c7; color: #92400e; padding: 1px 5px; border-radius: 3px; margin-left: 4px; }}

/* TEXTO DA PETICAO */
.texto-peticao {{ white-space: pre-wrap; font-size: 14px; line-height: 1.8; color: #1a1a1a; word-wrap: break-word; font-family: Georgia, 'Times New Roman', Times, serif; padding: 20px 24px; }}

/* MARCACOES */
.marca {{ cursor: pointer; border-radius: 3px; padding: 1px 3px; transition: all 0.2s; position: relative; }}
.marca.confirmado {{ background: #fff3cd; border-left: 3px solid #16a34a; }}
.marca.confirmado:hover {{ background: #fde68a; }}
.marca.divergente {{ background: #fee2e2; border-left: 3px solid #dc2626; }}
.marca.divergente:hover {{ background: #fecaca; }}
.marca.pendente {{ background: #fef9c3; border-left: 3px solid #ca8a04; }}
.marca.selecionada {{ background: #dbeafe !important; border-left: 4px solid #2563eb !important; box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.3); }}

/* COLUNA DIREITA — PROCESSO */
.col-processo {{ width: 50%; display: flex; flex-direction: column; overflow: hidden; background: #f8f9fa; }}
.col-processo-header {{ color: #2563eb; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; padding: 12px 20px 8px; flex-shrink: 0; font-weight: 700; border-bottom: 1px solid #e5e7eb; background: #f8f9fa; }}

.info-fonte {{ padding: 8px 20px; background: #f0f4ff; border-bottom: 1px solid #dbeafe; flex-shrink: 0; }}
.info-fonte .secao {{ font-size: 11px; color: #2563eb; text-transform: uppercase; font-weight: 600; }}
.info-fonte .trecho-af {{ font-size: 13px; color: #1a1a1a; margin: 4px 0; }}
.info-fonte .fonte-descr {{ font-size: 12px; color: #555; margin-top: 4px; padding: 4px 8px; background: #ffffff; border-radius: 4px; border-left: 3px solid #2563eb; }}
.info-fonte .alerta {{ font-size: 12px; color: #dc2626; margin-top: 4px; padding: 4px 8px; background: #fee2e2; border-radius: 4px; border-left: 3px solid #dc2626; }}

.texto-processo {{ flex: 1; overflow-y: auto; padding: 0; font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace; font-size: 12px; line-height: 1.5; }}
.linha {{ display: flex; padding: 1px 12px; }}
.linha:hover {{ background: #eef2ff; }}
.linha-num {{ color: #9ca3af; min-width: 50px; text-align: right; padding-right: 12px; user-select: none; border-right: 1px solid #e5e7eb; margin-right: 12px; font-size: 11px; }}
.linha-txt {{ color: #374151; white-space: pre-wrap; word-break: break-word; flex: 1; }}
.linha.destaque {{ background: #dcfce7 !important; border-left: 3px solid #16a34a; }}
.linha.destaque .linha-num {{ color: #166534; font-weight: 700; }}
.linha.destaque .linha-txt {{ color: #1a1a1a; font-weight: 500; }}

.placeholder {{ padding: 40px 20px; text-align: center; color: #9ca3af; font-size: 14px; }}

/* BARRA INFERIOR */
.barra-inferior {{ background: #f0f0f0; padding: 8px 20px; display: flex; align-items: center; gap: 8px; border-top: 1px solid #e5e7eb; flex-shrink: 0; }}
.btn {{ padding: 6px 16px; border: none; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; }}
.btn-ant {{ background: #e5e7eb; color: #555; }}
.btn-ant:hover {{ background: #d1d5db; }}
.btn-ok {{ background: #16a34a; color: #fff; }}
.btn-ok:hover {{ background: #15803d; }}
.btn-prob {{ background: #dc2626; color: #fff; }}
.btn-prob:hover {{ background: #b91c1c; }}
.btn-prox {{ background: #2563eb; color: #fff; }}
.btn-prox:hover {{ background: #1d4ed8; }}
.atalho {{ font-size: 10px; opacity: 0.6; margin-left: 3px; }}
.barra-info {{ margin-left: auto; font-size: 12px; color: #555; }}
.progresso {{ display: inline-block; background: #e5e7eb; border-radius: 8px; height: 6px; width: 120px; overflow: hidden; margin-left: 8px; vertical-align: middle; }}
.progresso-fill {{ height: 100%; background: #16a34a; transition: width 0.3s; }}

/* Decisao visual */
.marca.decisao-ok {{ background: rgba(22, 163, 74, 0.2) !important; }}
.marca.decisao-prob {{ background: rgba(220, 38, 38, 0.2) !important; text-decoration: wavy underline #dc2626; }}

/* Sumario item ativo */
.sum-item.ativo {{ background: #dbeafe; font-weight: 600; }}
</style>
</head>
<body>

<div class="barra-topo">
  <span class="titulo">PROVA VISUAL</span>
  <span class="info">{html.escape(processo)}</span>
  <div class="contagem">
    <span class="c-ok">{confirmadas} confirmadas</span>
    {f'<span class="c-div">{divergentes} divergentes</span>' if divergentes else ''}
    {f'<span class="c-sf">{sem_fonte} sem fonte</span>' if sem_fonte else ''}
  </div>
</div>

<div class="paineis">
  <!-- PETICAO -->
  <div class="col-peticao">
    <div class="col-peticao-header">Peticao Gerada ({localizadas} marcadas no texto / {nao_localizadas} so no sumario)</div>
    <div class="col-peticao-body">
      {sumario_html}
      <div class="texto-peticao">{peticao_html}</div>
    </div>
  </div>

  <!-- PROCESSO -->
  <div class="col-processo">
    <div class="col-processo-header">Processo na Integra ({len(linhas_processo)} linhas)</div>
    <div class="info-fonte" id="infoFonte">
      <div class="secao" id="fonteSecao"></div>
      <div class="trecho-af" id="fonteTrecho">Clique numa afirmacao ou frase destacada para ver a fonte.</div>
      <div id="fontesLista"></div>
    </div>
    <div class="texto-processo" id="textoProcesso"></div>
  </div>
</div>

<div class="barra-inferior">
  <button class="btn btn-ant" onclick="navegar(-1)">Anterior <span class="atalho">[&#8592;]</span></button>
  <button class="btn btn-ok" onclick="decidir('ok')">Conferido <span class="atalho">[Enter]</span></button>
  <button class="btn btn-prob" onclick="decidir('prob')">Problema <span class="atalho">[P]</span></button>
  <button class="btn btn-prox" onclick="navegar(1)">Proximo <span class="atalho">[&#8594;]</span></button>
  <span class="barra-info">
    <span id="indicador">0 / {total}</span>
    <span class="progresso"><span class="progresso-fill" id="barraProgresso" style="width:0%"></span></span>
  </span>
</div>

<script>
var AFIRMACOES = {afirmacoes_js};
var TEXTO_PROCESSO = [
{linhas_js}
];
var PROCESSO = '{escapar_js(processo)}';
var TOTAL = AFIRMACOES.length;
var STORAGE_KEY = 'prova_visual_' + PROCESSO;

var atual = -1;
var decisoes = carregarDecisoes();
var linhasDestaqueAtuais = [];

function carregarDecisoes() {{
  try {{
    var s = localStorage.getItem(STORAGE_KEY);
    if (s) return JSON.parse(s);
  }} catch(e) {{}}
  return {{}};
}}

function salvarDecisoes() {{
  try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(decisoes)); }} catch(e) {{}}
}}

function criarEl(tag, cls, txt) {{
  var el = document.createElement(tag);
  if (cls) el.className = cls;
  if (txt) el.textContent = txt;
  return el;
}}

// Renderizar processo INTEIRO ao carregar
function renderizarProcessoInteiro() {{
  var container = document.getElementById('textoProcesso');
  var fragment = document.createDocumentFragment();

  for (var n = 0; n < TEXTO_PROCESSO.length; n++) {{
    var numLinha = n + 1;
    var div = document.createElement('div');
    div.className = 'linha';
    div.id = 'proc-linha-' + numLinha;
    var numSpan = criarEl('span', 'linha-num', String(numLinha));
    var txtSpan = criarEl('span', 'linha-txt', TEXTO_PROCESSO[n] || '');
    div.appendChild(numSpan);
    div.appendChild(txtSpan);
    fragment.appendChild(div);
  }}

  container.appendChild(fragment);
}}

function destacarLinhas(linhasRef) {{
  // Remover destaques anteriores
  for (var i = 0; i < linhasDestaqueAtuais.length; i++) {{
    var el = document.getElementById('proc-linha-' + linhasDestaqueAtuais[i]);
    if (el) el.classList.remove('destaque');
  }}

  linhasDestaqueAtuais = linhasRef || [];

  // Aplicar novos destaques
  for (var i = 0; i < linhasDestaqueAtuais.length; i++) {{
    var el = document.getElementById('proc-linha-' + linhasDestaqueAtuais[i]);
    if (el) el.classList.add('destaque');
  }}

  // Scroll para primeira linha destacada
  if (linhasDestaqueAtuais.length > 0) {{
    setTimeout(function() {{
      var el = document.getElementById('proc-linha-' + linhasDestaqueAtuais[0]);
      if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    }}, 100);
  }}
}}

function selecionarAfirmacao(idx) {{
  atual = idx;

  // Remover selecao anterior da marca
  var prev = document.querySelector('.marca.selecionada');
  if (prev) prev.classList.remove('selecionada');

  // Remover selecao anterior do sumario
  var prevSum = document.querySelector('.sum-item.ativo');
  if (prevSum) prevSum.classList.remove('ativo');

  // Selecionar marca no texto (se existir)
  var el = document.getElementById('marca-' + idx);
  if (el) {{
    el.classList.add('selecionada');
    el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
  }}

  // Selecionar item no sumario
  var sumItems = document.querySelectorAll('.sum-item');
  if (idx >= 1 && idx <= sumItems.length) {{
    sumItems[idx - 1].classList.add('ativo');
    if (!el) {{
      // Se nao tem marca no texto, scroll o sumario para o item
      sumItems[idx - 1].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    }}
  }}

  // Encontrar afirmacao
  var af = null;
  for (var i = 0; i < AFIRMACOES.length; i++) {{
    if (AFIRMACOES[i].idx === idx) {{ af = AFIRMACOES[i]; break; }}
  }}
  if (!af) return;

  // Atualizar info fonte
  document.getElementById('fonteSecao').textContent = af.secao;
  document.getElementById('fonteTrecho').textContent = '#' + af.idx + ': ' + af.trecho;

  var lista = document.getElementById('fontesLista');
  while (lista.firstChild) lista.removeChild(lista.firstChild);

  af.fontes.forEach(function(f) {{
    var div = criarEl('div', 'fonte-descr');
    var loc = criarEl('strong', null, f.localizacao);
    div.appendChild(loc);
    div.appendChild(document.createTextNode(' — ' + f.trecho));
    lista.appendChild(div);
  }});

  if (af.alertas && af.alertas.length > 0) {{
    af.alertas.forEach(function(a) {{
      lista.appendChild(criarEl('div', 'alerta', 'ALERTA: ' + a));
    }});
  }}

  // Destacar linhas referenciadas no processo
  destacarLinhas(af.linhas_ref);

  atualizarIndicador();
}}

function navegar(dir) {{
  if (atual < 0 && dir === 1) {{
    selecionarAfirmacao(1);
    return;
  }}
  var novoIdx = atual + dir;
  if (novoIdx < 1) novoIdx = 1;
  if (novoIdx > TOTAL) novoIdx = TOTAL;
  selecionarAfirmacao(novoIdx);
}}

function decidir(tipo) {{
  if (atual < 1) return;
  decisoes[atual] = tipo;
  salvarDecisoes();

  var el = document.getElementById('marca-' + atual);
  if (el) {{
    el.classList.remove('decisao-ok', 'decisao-prob');
    el.classList.add(tipo === 'ok' ? 'decisao-ok' : 'decisao-prob');
  }}

  atualizarIndicador();

  if (atual < TOTAL) {{
    selecionarAfirmacao(atual + 1);
  }}
}}

function atualizarIndicador() {{
  var feitos = Object.keys(decisoes).length;
  document.getElementById('indicador').textContent = feitos + ' / ' + TOTAL;
  var pct = Math.round((feitos / TOTAL) * 100);
  document.getElementById('barraProgresso').style.width = pct + '%';
}}

function restaurarDecisoes() {{
  for (var k in decisoes) {{
    var el = document.getElementById('marca-' + k);
    if (el) {{
      el.classList.add(decisoes[k] === 'ok' ? 'decisao-ok' : 'decisao-prob');
    }}
  }}
  atualizarIndicador();
}}

// Atalhos de teclado
document.addEventListener('keydown', function(e) {{
  if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') return;
  switch(e.key) {{
    case 'Enter': e.preventDefault(); decidir('ok'); break;
    case 'p': case 'P': e.preventDefault(); decidir('prob'); break;
    case 'ArrowRight': e.preventDefault(); navegar(1); break;
    case 'ArrowLeft': e.preventDefault(); navegar(-1); break;
  }}
}});

// Inicializar: renderizar processo inteiro + restaurar decisoes
renderizarProcessoInteiro();
restaurarDecisoes();
</script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description='Gera HTML de prova visual v2')
    parser.add_argument('--pdf', required=True, help='PDF da peticao')
    parser.add_argument('--json', required=True, help='JSON de verificacao')
    parser.add_argument('--texto', required=True, help='TEXTO-EXTRAIDO.txt')
    parser.add_argument('--output', required=True, help='HTML de saida')
    args = parser.parse_args()

    texto_pdf = extrair_texto_pdf(args.pdf)
    texto_peticao = limpar_texto_peticao(texto_pdf)

    with open(args.json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(args.texto, 'r', encoding='utf-8') as f:
        linhas_processo = f.read().splitlines()

    processo = data.get('processo', '')
    resumo = data.get('resumo', {})
    afirmacoes = preparar_afirmacoes(data)

    html_content = gerar_html(texto_peticao, afirmacoes, linhas_processo, processo, resumo)

    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html_content)

    matches = 0
    for af in afirmacoes:
        if encontrar_posicao(texto_peticao, af['trecho']):
            matches += 1
        else:
            for dado in af.get('dados', []):
                if encontrar_posicao(texto_peticao, dado):
                    matches += 1
                    break

    print(f"Prova Visual v2 gerada: {args.output}")
    print(f"  {len(afirmacoes)} afirmacoes, {matches} localizadas no texto da peticao")
    print(f"  {len(afirmacoes) - matches} acessiveis apenas via sumario")
    print(f"  {len(linhas_processo)} linhas do processo (integra)")
    tamanho = os.path.getsize(args.output)
    print(f"  Tamanho: {tamanho / 1024:.0f} KB")


if __name__ == '__main__':
    main()
